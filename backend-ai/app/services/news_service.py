import hashlib
import json
import logging
from datetime import datetime, timezone
import feedparser
from google import genai

from app.config.settings import settings
from app.data_sources.news import get_news
from app.models.news import NewsArticle, NewsResponse
from app.services.data_lake_service import (
    save_to_bronze,
    save_news_to_silver,
    get_news_from_silver,
    save_news_gold_analysis,
    get_news_gold_analysis,
)

logger = logging.getLogger("news_service")
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# 1. Mapowanie kategorii
CATEGORY_MAPPING = {
    "gielda": "stock market",
    "makroekonomia": "economy inflation",
    "kryptowaluty": "crypto",
    "geopolityka": "geopolitics diplomacy",
    "polska_gospodarka": "poland economy",
    "swiatowe_rynki": "global financial markets",
}

# 2. Czarna lista serwisów plotkarskich oraz repozytoriów kodu
EXCLUDED_DOMAINS = [
    "pagesix.com",
    "thoughtcatalog.com",
    "tmz.com",
    "pypi.org",
    "github.com",
    "buzzfeed.com",
    "dailymail.co.uk",
]

# 3. Zaufane polskie źródła RSS (Priorytet: 0 tokenów, język polski, brak limitu 100 req/dobę)
RSS_SOURCES = {
    "gielda": [
        ("https://www.bankier.pl/rss/wiadomosci.xml", "Bankier.pl Giełda"),
        ("https://stooq.pl/rss/", "Stooq"),
    ],
    "makroekonomia": [
        ("https://www.bankier.pl/rss/gospodarka.xml", "Bankier Gospodarka"),
    ],
    "kryptowaluty": [
        ("https://bithub.pl/feed/", "BitHub"),
        ("https://bitcoin.pl/feed", "Bitcoin.pl"),
    ],
    "geopolityka": [
        ("https://defence24.pl/rss", "Defence24"),
    ],
    "polska_gospodarka": [
        ("https://www.bankier.pl/rss/gospodarka.xml", "Bankier Polska"),
    ],
    "swiatowe_rynki": [
        ("https://www.bankier.pl/rss/rynki-zagraniczne.xml", "Bankier Świat"),
    ],
}


def _hash_id(url: str) -> str:
    return hashlib.md5(url.strip().encode("utf-8")).hexdigest()


def _translate_titles_batch(titles: list[str]) -> list[str]:
    """Tłumaczy nagłówki na język polski w jednym wsadowym zapytaniu do Gemini."""
    if not titles:
        return []

    prompt = (
        "Przetłumacz poniższe nagłówki wiadomości finansowych i geopolitycznych na naturalny, "
        "rzeczowy język polski. Zwróć wynik WYŁĄCZNIE jako poprawną tablicę JSON, "
        "dokładnie w tej samej kolejności: [\"tytuł 1\", \"tytuł 2\", ...].\n\n"
        f"Nagłówki:\n{json.dumps(titles, ensure_ascii=False)}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        translated = json.loads(response.text)
        if isinstance(translated, list) and len(translated) == len(titles):
            return translated
    except Exception as e:
        logger.warning(f"Błąd tłumaczenia tytułów przez Gemini: {e}")

    return titles


def fetch_from_rss(category_key: str) -> list[dict]:
    """Pobiera wiadomości z polskich kanałów RSS."""
    feeds = RSS_SOURCES.get(category_key, [])
    now_iso = datetime.now(timezone.utc).isoformat()
    articles = []

    for feed_url, source_name in feeds:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:25]:
                url = getattr(entry, "link", "").strip()
                title = getattr(entry, "title", "").strip()
                if not url or not title:
                    continue

                pub = getattr(entry, "published", now_iso)
                desc = getattr(entry, "summary", "")

                articles.append({
                    "id": _hash_id(url),
                    "title": title,
                    "description": desc,
                    "source": source_name,
                    "url": url,
                    "image_url": None,
                    "category": category_key,
                    "published_at": pub,
                    "fetched_at": now_iso,
                    "language": "pl",
                })
        except Exception as e:
            logger.error(f"Błąd pobierania RSS {feed_url}: {e}")

    return articles


def fetch_and_process_category(category_key: str) -> list[dict]:
    """
    Pobiera artykuły. Polskie RSS są priorytetem (0 tokenów),
    a NewsAPI stanowi uzupełnienie tylko, jeśli brakuje artykułów.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    clean_cat = category_key.strip().lower().replace(" ", "_")
    all_articles = []

    # 1. Priorytet: Zaufane polskie źródła RSS
    rss_articles = fetch_from_rss(clean_cat)
    all_articles.extend(rss_articles)

    # 2. Uzupełnienie z NewsAPI tylko wtedy, gdy z RSS jest mniej niż 15 artykułów
    if len(all_articles) < 15:
        query = CATEGORY_MAPPING.get(clean_cat, clean_cat)
        raw_articles = []
        try:
            raw_articles = get_news(query)
            if not raw_articles and clean_cat in CATEGORY_MAPPING:
                raw_articles = get_news("finance")
        except Exception as e:
            logger.warning(f"NewsAPI niedostępne dla {clean_cat}: {e}")

        if raw_articles:
            try:
                save_to_bronze("newsapi", clean_cat, {"articles": raw_articles})
            except Exception:
                pass

        filtered_newsapi = []
        for art in raw_articles:
            source_name = (art.get("source", {}).get("name") or "").lower()
            url = (art.get("url") or "").lower()
            title = art.get("title") or ""

            if not title or "[Removed]" in title:
                continue
            if any(domain in url or domain in source_name for domain in EXCLUDED_DOMAINS):
                continue

            filtered_newsapi.append(art)

        selected_newsapi = filtered_newsapi[:5]
        orig_titles = [a.get("title", "") for a in selected_newsapi]
        translated = _translate_titles_batch(orig_titles)

        for art, trans_title in zip(selected_newsapi, translated):
            url = art.get("url", "")
            all_articles.append({
                "id": _hash_id(url),
                "title": trans_title,
                "description": art.get("description", ""),
                "source": art.get("source", {}).get("name", "NewsAPI"),
                "url": url,
                "image_url": art.get("urlToImage"),
                "category": clean_cat,
                "published_at": art.get("publishedAt", now_iso),
                "fetched_at": now_iso,
                "language": "pl",
            })

    # 3. Zapis do warstwy Silver Data Lake (deduplikacja i sortowanie)
    if all_articles:
        save_news_to_silver(clean_cat, all_articles)

    return all_articles


def latest_news(symbol: str) -> NewsResponse:
    """
    Główny endpoint GET /stock/news/{symbol}.
    Czyta artykuły z Data Lake (Silver). Pobiera w locie, jeśli kategoria jest pusta.
    """
    clean_cat = symbol.strip().lower().replace(" ", "_")

    articles = get_news_from_silver(clean_cat, limit=30)
    if not articles or len(articles) < 5:
        articles = fetch_and_process_category(clean_cat)

    articles_list = [
        NewsArticle(
            title=a.get("title", "Brak tytułu"),
            source=a.get("source", "Rynek"),
            published=a.get("published_at", ""),
            url=a.get("url", ""),
        )
        for a in articles[:30]
    ]

    return NewsResponse(articles=articles_list)


def get_news_full_payload(category: str, limit: int = 30) -> dict:
    """Format rozszerzony (zgodny ze specyfikacją Kamila)."""
    clean_cat = category.strip().lower().replace(" ", "_")
    articles = get_news_from_silver(clean_cat, limit=limit)
    if not articles:
        articles = fetch_and_process_category(clean_cat)

    last_updated = articles[0].get("fetched_at") if articles else None

    return {
        "category": clean_cat,
        "total_results": len(articles),
        "last_updated": last_updated,
        "articles": articles[:limit],
    }


def analyze_news_sentiment(category: str) -> dict:
    """Zwięzła analiza AI dla danej kategorii z pamięcią podręczną w warstwie Gold (<150 tokenów)."""
    clean_cat = category.strip().lower().replace(" ", "_")

    cached = get_news_gold_analysis(clean_cat)
    if cached:
        return cached

    articles = get_news_from_silver(clean_cat, limit=5)
    if not articles:
        return {
            "category": clean_cat,
            "summary": "Brak artykułów w Data Lake do przeprowadzenia analizy.",
            "sentiment": "Neutralny",
            "market_impact": "Brak danych.",
            "uncertainty": "Umiarkowana",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    digest = "\n".join([f"- [{a.get('id', '')[:8]}] {a.get('title', '')} ({a.get('source', '')})" for a in articles])

    prompt = (
        f"Kategoria wiadomości: {clean_cat}\n"
        f"Nagłówki rynkowe:\n{digest}\n\n"
        "Jako analityk sporządź zwięzłą analizę. Zwróć WYŁĄCZNIE obiekt JSON z polami:\n"
        "- summary: 1-2 zdania streszczenia sytuacji.\n"
        "- market_impact: 1 zdanie o wpływie na rynek i wyceny.\n"
        "- sentiment: jedno słowo (Pozytywny, Negatywny, Neutralny).\n"
        "- uncertainty: jedno słowo (Niska, Umiarkowana, Wysoka)."
    )

    try:
        res = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=180,
                temperature=0.1,
            ),
        )
        data = json.loads(res.text)
        data["category"] = clean_cat
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_news_gold_analysis(clean_cat, data)
        return data
    except Exception as e:
        logger.error(f"Błąd analizy Gemini: {e}")
        return {
            "category": clean_cat,
            "summary": "Analiza AI chwilowo niedostępna.",
            "sentiment": "Neutralny",
            "market_impact": "Brak możliwości oszacowania.",
            "uncertainty": "Wysoka",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }