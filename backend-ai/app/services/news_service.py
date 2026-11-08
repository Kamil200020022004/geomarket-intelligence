import hashlib
import html
import json
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import feedparser
import requests
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

# Mapowanie identyfikatorów z frontendu (angielskie) na wewnętrzne klucze Data Lake (polskie)
FRONTEND_TO_INTERNAL_CATEGORY = {
    "stocks": "gielda",
    "macro": "makroekonomia",
    "crypto": "kryptowaluty",
    "geopolitics": "geopolityka",
    "poland": "polska_gospodarka",
    "global": "swiatowe_rynki",
    # Obsługa bezpośrednich zapytań po polsku (np. ze schedulera)
    "gielda": "gielda",
    "makroekonomia": "makroekonomia",
    "kryptowaluty": "kryptowaluty",
    "geopolityka": "geopolityka",
    "polska_gospodarka": "polska_gospodarka",
    "swiatowe_rynki": "swiatowe_rynki",
}

INTERNAL_TO_FRONTEND_CATEGORY = {
    "gielda": "stocks",
    "makroekonomia": "macro",
    "kryptowaluty": "crypto",
    "geopolityka": "geopolitics",
    "polska_gospodarka": "poland",
    "swiatowe_rynki": "global",
}

# Zapytania do NewsAPI dopasowane ściśle do każdej kategorii (bez ogólnego fallbacku 'finance')
CATEGORY_MAPPING = {
    "gielda": "stock market OR NASDAQ OR S&P 500 OR equities",
    "makroekonomia": "inflation OR interest rates OR GDP OR central bank",
    "kryptowaluty": "bitcoin OR ethereum OR cryptocurrency",
    "geopolityka": "geopolitics OR sanctions OR trade tariff OR conflict economy",
    "polska_gospodarka": "Poland economy OR Warsaw Stock Exchange OR NBP",
    "swiatowe_rynki": "global markets OR Wall Street OR European markets OR commodities",
}

EXCLUDED_DOMAINS = [
    "pagesix.com",
    "thoughtcatalog.com",
    "tmz.com",
    "pypi.org",
    "github.com",
    "buzzfeed.com",
    "dailymail.co.uk",
]

# Zweryfikowane, działające źródła RSS dla każdej z 6 kategorii
RSS_SOURCES = {
    "gielda": [
        ("https://www.bankier.pl/rss/wiadomosci.xml", "Bankier.pl"),
        ("https://www.money.pl/rss/gielda.xml", "Money.pl Giełda"),
        ("https://news.google.com/rss/search?q=gie%C5%82da+GPW+WIG20+NASDAQ+akcje+when:7d&hl=pl&gl=PL&ceid=PL:pl", "Rynki Giełdowe"),
    ],
    "makroekonomia": [
        ("https://www.bankier.pl/rss/waluty.xml", "Bankier.pl Makro i Waluty"),
        ("https://news.google.com/rss/search?q=inflacja+stopy+procentowe+PKB+bank+centralny+FED+EBC+when:7d&hl=pl&gl=PL&ceid=PL:pl", "Makroekonomia"),
    ],
    "kryptowaluty": [
        ("https://bithub.pl/feed/", "BitHub.pl"),
        ("https://bitcoin.pl/feed", "Bitcoin.pl"),
        ("https://news.google.com/rss/search?q=bitcoin+ethereum+kryptowaluty+when:7d&hl=pl&gl=PL&ceid=PL:pl", "Rynek Krypto"),
    ],
    "geopolityka": [
        ("https://defence24.pl/rss", "Defence24"),
        ("https://news.google.com/rss/search?q=geopolityka+sankcje+konflikt+handel+gospodarka+when:7d&hl=pl&gl=PL&ceid=PL:pl", "Geopolityka i Świat"),
    ],
    "polska_gospodarka": [
        ("https://www.money.pl/rss/gospodarka.xml", "Money.pl Gospodarka"),
        ("https://news.google.com/rss/search?q=polska+gospodarka+NBP+GUS+inwestycje+GPW+when:7d&hl=pl&gl=PL&ceid=PL:pl", "Polska Gospodarka"),
    ],
    "swiatowe_rynki": [
        ("https://news.google.com/rss/search?q=rynki+finansowe+USA+Azja+Europa+surowce+ropa+z%C5%82oto+when:7d&hl=pl&gl=PL&ceid=PL:pl", "Światowe Rynki"),
        ("https://www.bankier.pl/rss/waluty.xml", "Bankier.pl Rynki"),
    ],
}

DEFAULT_MARKETS_BY_CATEGORY = {
    "gielda": ["WIG20", "S&P 500", "NASDAQ"],
    "makroekonomia": ["USD/PLN", "EUR/PLN", "Obligacje skarbowe"],
    "kryptowaluty": ["BTC", "ETH", "SOL"],
    "geopolityka": ["Ropa Brent", "Złoto", "EUR/USD"],
    "polska_gospodarka": ["GPW", "PLN", "WIG20"],
    "swiatowe_rynki": ["S&P 500", "DAX", "Surowce"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GeoMarketIntelligence/1.0"
}


def resolve_category(category: str) -> tuple[str, str]:
    """Zwraca (internal_key, frontend_key) lub rzuca ValueError dla nieznanej kategorii."""
    clean = (category or "").strip().lower().replace(" ", "_")
    if clean not in FRONTEND_TO_INTERNAL_CATEGORY:
        raise ValueError(f"Nieobsługiwana kategoria: {category}")
    internal_key = FRONTEND_TO_INTERNAL_CATEGORY[clean]
    frontend_key = INTERNAL_TO_FRONTEND_CATEGORY.get(internal_key, clean)
    return internal_key, frontend_key


def _hash_id(prefix: str, url: str) -> str:
    short_hash = hashlib.md5(url.strip().encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{short_hash}"


def _clean_html(raw_text: str) -> str:
    if not raw_text:
        return ""
    text = html.unescape(raw_text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:400]


def _normalize_iso_date(raw_date: str | None, fallback_iso: str) -> str:
    if not raw_date:
        return fallback_iso
    raw_date = str(raw_date).strip()
    try:
        dt = parsedate_to_datetime(raw_date)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return fallback_iso


def _translate_titles_batch(titles: list[str]) -> list[str]:
    """Tłumaczy angielskie nagłówki z NewsAPI na język polski przez Gemini."""
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


def fetch_from_rss(internal_cat: str) -> list[dict]:
    """Pobiera, oczyszcza i normalizuje wiadomości z kanałów RSS dla danej kategorii."""
    feeds = RSS_SOURCES.get(internal_cat, [])
    frontend_cat = INTERNAL_TO_FRONTEND_CATEGORY.get(internal_cat, internal_cat)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    articles = []
    seen_urls = set()

    for feed_url, default_source_name in feeds:
        try:
            resp = requests.get(feed_url, headers=HEADERS, timeout=6)
            resp.raise_for_status()
            parsed = feedparser.parse(resp.content)

            for entry in parsed.entries[:15]:
                url = getattr(entry, "link", "").strip()
                title = _clean_html(getattr(entry, "title", ""))
                if not url or not title or url in seen_urls:
                    continue
                if "kanał rss został" in title.lower() or "komunikat" == title.lower():
                    continue

                source_name = default_source_name
                if hasattr(entry, "source") and isinstance(entry.source, dict):
                    source_name = entry.source.get("title") or default_source_name

                raw_pub = getattr(entry, "published", None) or getattr(entry, "updated", None)
                pub_iso = _normalize_iso_date(raw_pub, now_iso)
                desc = _clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
                if not desc or desc == title:
                    desc = f"Wiadomość rynkowa z serwisu {source_name} w kategorii {frontend_cat}."

                seen_urls.add(url)
                articles.append({
                    "id": _hash_id(frontend_cat, url),
                    "title": title,
                    "description": desc,
                    "source": source_name,
                    "url": url,
                    "image_url": None,
                    "category": internal_cat,
                    "published_at": pub_iso,
                    "fetched_at": now_iso,
                    "language": "pl",
                })
        except Exception as e:
            logger.warning(f"Błąd pobierania kanału RSS {feed_url}: {e}")

    if articles:
        try:
            save_to_bronze("news_rss", internal_cat, {"articles": articles})
        except Exception:
            pass

    return articles


def fetch_and_process_category(category_key: str) -> list[dict]:
    """
    Pobiera artykuły dla danej kategorii (RSS + uzupełnienie z NewsAPI)
    i zapisuje oczyszczony zbiór w warstwie Silver Data Lake.
    """
    try:
        internal_cat, frontend_cat = resolve_category(category_key)
    except ValueError:
        internal_cat = category_key.strip().lower().replace(" ", "_")
        frontend_cat = internal_cat

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_articles = fetch_from_rss(internal_cat)
    seen_urls = {a["url"] for a in all_articles}

    # Uzupełnienie z NewsAPI, jeśli z RSS pobrano mniej niż 10 artykułów
    if len(all_articles) < 10 and settings.NEWS_API_KEY:
        query = CATEGORY_MAPPING.get(internal_cat, internal_cat)
        raw_articles = []
        try:
            raw_articles = get_news(query, page_size=8)
        except Exception as e:
            logger.warning(f"NewsAPI niedostępne dla {internal_cat}: {e}")

        if raw_articles:
            try:
                save_to_bronze("newsapi", internal_cat, {"articles": raw_articles})
            except Exception:
                pass

        filtered_newsapi = []
        for art in raw_articles:
            source_name = (art.get("source", {}).get("name") or "").lower()
            url = (art.get("url") or "").strip()
            title = (art.get("title") or "").strip()

            if not url or not title or "[Removed]" in title or url in seen_urls:
                continue
            if any(domain in url.lower() or domain in source_name for domain in EXCLUDED_DOMAINS):
                continue

            filtered_newsapi.append(art)

        selected_newsapi = filtered_newsapi[:5]
        orig_titles = [a.get("title", "") for a in selected_newsapi]
        translated = _translate_titles_batch(orig_titles)

        for art, trans_title in zip(selected_newsapi, translated):
            url = art.get("url", "").strip()
            pub_iso = _normalize_iso_date(art.get("publishedAt"), now_iso)
            desc = _clean_html(art.get("description") or "") or trans_title
            seen_urls.add(url)
            all_articles.append({
                "id": _hash_id(frontend_cat, url),
                "title": trans_title,
                "description": desc,
                "source": art.get("source", {}).get("name", "NewsAPI"),
                "url": url,
                "image_url": art.get("urlToImage"),
                "category": internal_cat,
                "published_at": pub_iso,
                "fetched_at": now_iso,
                "language": "pl",
            })

    all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    if all_articles:
        save_news_to_silver(internal_cat, all_articles)

    return all_articles


def _format_article_for_api(article: dict, frontend_cat: str) -> dict:
    """Zapewnia spójny kontrakt JSON obsługujący zarówno camelCase (React), jak i snake_case."""
    url = article.get("url", "")
    art_id = article.get("id") or _hash_id(frontend_cat, url)
    pub = article.get("published_at") or article.get("publishedAt") or ""
    img = article.get("image_url") if "image_url" in article else article.get("imageUrl")
    desc = article.get("description") or article.get("title", "")

    return {
        "id": art_id,
        "title": article.get("title", "Brak tytułu"),
        "source": article.get("source", "Źródło rynkowe"),
        "publishedAt": pub,
        "published_at": pub,
        "url": url,
        "description": desc,
        "imageUrl": img,
        "image_url": img,
        "category": frontend_cat,
    }


def get_news_full_payload(category: str, limit: int = 25, refresh: bool = False) -> dict:
    """Zwraca wiadomości dla wybranej kategorii w formacie wymaganym przez frontend React."""
    internal_cat, frontend_cat = resolve_category(category)

    articles = [] if refresh else get_news_from_silver(internal_cat, limit=limit)
    if not articles or len(articles) < 3:
        articles = fetch_and_process_category(internal_cat)

    formatted_articles = [_format_article_for_api(a, frontend_cat) for a in articles[:limit]]
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    last_updated = articles[0].get("fetched_at", now_iso) if articles else now_iso

    return {
        "category": frontend_cat,
        "articles": formatted_articles,
        "count": len(formatted_articles),
        "total_results": len(formatted_articles),
        "lastUpdated": last_updated,
        "last_updated": last_updated,
    }


def latest_news(symbol: str) -> NewsResponse:
    """Obsługuje dotychczasowy endpoint GET /stock/news/{symbol}."""
    try:
        internal_cat, _ = resolve_category(symbol)
        articles = get_news_from_silver(internal_cat, limit=25)
        if not articles:
            articles = fetch_and_process_category(internal_cat)
    except ValueError:
        clean_sym = symbol.strip().upper()
        articles = get_news_from_silver(clean_sym.lower(), limit=15)
        if not articles:
            try:
                raw = get_news(clean_sym, page_size=8)
                now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                articles = [
                    {
                        "title": r.get("title", "Brak tytułu"),
                        "source": r.get("source", {}).get("name", "NewsAPI"),
                        "published_at": _normalize_iso_date(r.get("publishedAt"), now_iso),
                        "url": r.get("url", ""),
                    }
                    for r in raw
                    if r.get("title") and r.get("url")
                ]
            except Exception:
                articles = []

    articles_list = [
        NewsArticle(
            title=a.get("title", "Brak tytułu"),
            source=a.get("source", "Rynek"),
            published=a.get("published_at", ""),
            url=a.get("url", ""),
        )
        for a in articles[:25]
    ]
    return NewsResponse(articles=articles_list)


def get_category_ai_analysis(category: str, refresh: bool = False) -> dict:
    """
    Generuje analizę AI (Gemini) na podstawie rzeczywistych artykułów z warstwy Silver
    i zapisuje wynik w warstwie Gold Data Lake.
    """
    internal_cat, frontend_cat = resolve_category(category)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Pobieramy rzeczywiste artykuły z warstwy Silver (lub dociągamy, jeśli pusto)
    articles = get_news_from_silver(internal_cat, limit=10)
    if not articles:
        articles = fetch_and_process_category(internal_cat)[:10]

    if not articles:
        return {
            "category": frontend_cat,
            "generatedAt": now_iso,
            "updated_at": now_iso,
            "summary": "Brak bieżących artykułów źródłowych do przeprowadzenia analizy AI.",
            "sentiment": "neutral",
            "market_impact": "Brak danych źródłowych.",
            "uncertainty": "high",
            "analyses": [],
        }

    current_top_ids = [a.get("id") or _hash_id(frontend_cat, a.get("url", "")) for a in articles[:6]]

    # 2. Sprawdzamy cache w warstwie Gold (ważny, dopóki zestaw artykułów się nie zmienił i ma < 30 min)
    if not refresh:
        cached = get_news_gold_analysis(internal_cat)
        if cached and isinstance(cached, dict) and cached.get("analyses"):
            cached_ids = cached.get("source_signature", [])
            if cached_ids == current_top_ids:
                cached["category"] = frontend_cat
                return cached

    # 3. Budujemy kontekst z prawdziwych artykułów dla modelu Gemini
    articles_context = []
    for idx, art in enumerate(articles[:6], start=1):
        art_id = art.get("id") or _hash_id(frontend_cat, art.get("url", ""))
        articles_context.append({
            "id": art_id,
            "title": art.get("title", ""),
            "source": art.get("source", ""),
            "publishedAt": art.get("published_at", ""),
            "description": art.get("description", ""),
        })

    prompt = (
        f"Jesteś analitykiem rynkowym platformy GeoMarket Intelligence.\n"
        f"Kategoria: {frontend_cat} ({internal_cat}).\n"
        f"Przeanalizuj poniższe rzeczywiste artykuły prasowe:\n"
        f"{json.dumps(articles_context, ensure_ascii=False, indent=2)}\n\n"
        "ZASADY:\n"
        "1. Opieraj się WYŁĄCZNIE na przekazanych artykułach. Nie zmyślaj faktów ani nie dawaj rekomendacji inwestycyjnych.\n"
        "2. Przygotuj 2-3 konkretne analizy tematyczne grupujące powyższe wiadomości.\n"
        "3. W polu 'sourceArticleIds' podaj prawdziwe identyfikatory 'id' z przekazanej listy.\n"
        "4. Pole 'sentiment' musi mieć wartość: 'positive', 'neutral' lub 'negative'.\n"
        "5. Pole 'riskLevel' musi mieć wartość: 'low', 'medium' lub 'high'.\n\n"
        "Zwróć WYŁĄCZNIE poprawny obiekt JSON w formacie:\n"
        "{\n"
        '  "overallSummary": "2-3 zdania ogólnego podsumowania kategorii po polsku",\n'
        '  "overallSentiment": "positive | neutral | negative",\n'
        '  "overallImpact": "1-2 zdania o możliwych konsekwencjach rynkowych po polsku",\n'
        '  "overallRisk": "low | medium | high",\n'
        '  "analyses": [\n'
        "    {\n"
        '      "id": "analysis-001",\n'
        '      "title": "Zwięzły tytuł analizy po polsku",\n'
        '      "summary": "2-3 zdania merytorycznego podsumowania AI po polsku",\n'
        '      "affectedMarkets": ["Aktywo 1", "Aktywo 2"],\n'
        '      "sentiment": "positive | neutral | negative",\n'
        '      "riskLevel": "low | medium | high",\n'
        '      "potentialImpact": "Opis możliwych konsekwencji rynkowych (bez rekomendacji kup/sprzedaj)",\n'
        '      "sourceArticleIds": ["id-artykulu-1"]\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    try:
        res = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=900,
                temperature=0.2,
            ),
        )
        raw_ai = json.loads(res.text)
        raw_analyses = raw_ai.get("analyses", [])

        normalized_analyses = []
        valid_ids = {a["id"] for a in articles_context}
        default_markets = DEFAULT_MARKETS_BY_CATEGORY.get(internal_cat, ["Rynki finansowe"])

        for i, item in enumerate(raw_analyses, start=1):
            src_ids = [sid for sid in item.get("sourceArticleIds", []) if sid in valid_ids]
            if not src_ids and articles_context:
                src_ids = [articles_context[min(i - 1, len(articles_context) - 1)]["id"]]

            sentiment = str(item.get("sentiment", "neutral")).lower()
            if sentiment not in {"positive", "neutral", "negative"}:
                sentiment = "neutral"

            risk = str(item.get("riskLevel", "medium")).lower()
            if risk not in {"low", "medium", "high"}:
                risk = "medium"

            affected = item.get("affectedMarkets") or default_markets
            if isinstance(affected, str):
                affected = [m.strip() for m in affected.split(",") if m.strip()]

            impact_text = item.get("potentialImpact") or raw_ai.get("overallImpact") or "Możliwa podwyższona zmienność krótkoterminowa."

            normalized_analyses.append({
                "id": f"{frontend_cat}-analysis-{i:03d}",
                "title": item.get("title", f"Analiza rynkowa #{i}"),
                "summary": item.get("summary", ""),
                "affectedMarkets": affected,
                "sentiment": sentiment,
                "riskLevel": risk,
                "uncertainty": risk,
                "potentialImpact": impact_text,
                "market_impact": impact_text,
                "sourceArticleIds": src_ids,
            })

        result_payload = {
            "category": frontend_cat,
            "generatedAt": now_iso,
            "updated_at": now_iso,
            "summary": raw_ai.get("overallSummary") or (normalized_analyses[0]["summary"] if normalized_analyses else ""),
            "sentiment": raw_ai.get("overallSentiment", "neutral"),
            "market_impact": raw_ai.get("overallImpact", ""),
            "uncertainty": raw_ai.get("overallRisk", "medium"),
            "source_signature": current_top_ids,
            "analyses": normalized_analyses,
        }

        save_news_gold_analysis(internal_cat, result_payload)
        return result_payload

    except Exception as e:
        logger.error(f"Błąd analizy Gemini dla kategorii {frontend_cat}: {e}")
        # Jeśli mamy starszą analizę w Gold, zwracamy ją z flagą fallback
        cached = get_news_gold_analysis(internal_cat)
        if cached and isinstance(cached, dict) and cached.get("analyses"):
            cached["category"] = frontend_cat
            cached["stale"] = True
            return cached

        # Jawna informacja o niedostępności modelu AI oparta na prawdziwych pobranych artykułach
        default_markets = DEFAULT_MARKETS_BY_CATEGORY.get(internal_cat, ["Rynki finansowe"])
        fallback_analysis = {
            "id": f"{frontend_cat}-analysis-fallback",
            "title": f"Przegląd wiadomości: {articles_context[0]['title'][:70]}",
            "summary": (
                f"Usługa generowania analiz AI (Gemini) jest chwilowo przeciążona. "
                f"Pobrano {len(articles_context)} aktualnych artykułów źródłowych dla kategorii '{frontend_cat}' "
                f"(m.in. z: {', '.join( sorted({a['source'] for a in articles_context[:3]}) )})."
            ),
            "affectedMarkets": default_markets,
            "sentiment": "neutral",
            "riskLevel": "medium",
            "uncertainty": "medium",
            "potentialImpact": "Wymagana ponowna próba analizy po zwolnieniu limitów API modelu językowego.",
            "market_impact": "Wymagana ponowna próba analizy po zwolnieniu limitów API modelu językowego.",
            "sourceArticleIds": [a["id"] for a in articles_context[:3]],
        }
        return {
            "category": frontend_cat,
            "generatedAt": now_iso,
            "updated_at": now_iso,
            "summary": fallback_analysis["summary"],
            "sentiment": "neutral",
            "market_impact": fallback_analysis["potentialImpact"],
            "uncertainty": "medium",
            "aiUnavailable": True,
            "analyses": [fallback_analysis],
        }


def analyze_news_sentiment(category: str) -> dict:
    """Zachowanie kompatybilności wstecznej dla funkcji wewnętrznych."""
    return get_category_ai_analysis(category, refresh=False)