from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import html
import json
import logging
import os
import re
<<<<<<< HEAD
from urllib.parse import urlparse
import feedparser
=======
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import feedparser
import requests
from urllib.parse import urlparse
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a
from google import genai
import requests

from app.config.settings import settings
from app.data_sources.news import get_news
from app.models.news import NewsArticle, NewsResponse
from app.services.data_lake_service import (
    get_gdelt_from_silver,
    get_news_from_silver,
    get_news_gold_analysis,
    save_news_gold_analysis,
    save_news_to_silver,
    save_to_bronze,
)

logger = logging.getLogger("news_service")
client = genai.Client(api_key=settings.GEMINI_API_KEY)

<<<<<<< HEAD
IS_VERCEL = bool(os.getenv("VERCEL"))
=======
# Vercel uruchamia FastAPI jako funkcję serverless, której katalog aplikacji
# jest tylko do odczytu. Lokalne pliki Data Lake nie są trwałym magazynem.
IS_VERCEL = bool(os.environ.get("VERCEL"))


def _read_silver_safe(category: str, limit: int) -> list[dict]:
    if IS_VERCEL:
        return []
    try:
        return get_news_from_silver(category, limit=limit)
    except (OSError, ValueError) as exc:
        logger.warning("Nie można odczytać cache Silver (%s): %s", category, exc)
        return []


def _read_gold_safe(category: str) -> dict | None:
    if IS_VERCEL:
        return None
    try:
        return get_news_gold_analysis(category)
    except (OSError, ValueError) as exc:
        logger.warning("Nie można odczytać cache Gold (%s): %s", category, exc)
        return None


def _write_silver_safe(category: str, articles: list[dict]) -> None:
    if IS_VERCEL or not articles:
        return
    try:
        save_news_to_silver(category, articles)
    except OSError as exc:
        logger.warning("Nie można zapisać wiadomości Silver (%s): %s", category, exc)


def _write_gold_safe(category: str, payload: dict) -> None:
    if IS_VERCEL:
        return
    try:
        save_news_gold_analysis(category, payload)
    except OSError as exc:
        logger.warning("Nie można zapisać analizy Gold (%s): %s", category, exc)
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

FRONTEND_TO_INTERNAL_CATEGORY = {
    "stocks": "gielda",
    "macro": "makroekonomia",
    "crypto": "kryptowaluty",
    "geopolitics": "geopolityka",
    "poland": "polska_gospodarka",
    "global": "swiatowe_rynki",
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

CATEGORY_MAPPING = {
    "gielda": "stock market OR NASDAQ OR S&P 500 OR equities OR giełda",
<<<<<<< HEAD
    "makroekonomia": (
        "inflation OR interest rates OR GDP OR central bank OR inflacja stopy"
    ),
    "kryptowaluty": "bitcoin OR ethereum OR cryptocurrency OR krypto",
    "geopolityka": (
        "geopolitics OR sanctions OR trade tariff OR conflict economy"
    ),
    "polska_gospodarka": (
        "Poland economy OR Warsaw Stock Exchange OR NBP OR GUS"
    ),
    "swiatowe_rynki": (
        "global markets OR Wall Street OR European markets OR commodities"
    ),
=======
    "makroekonomia": "inflation OR interest rates OR GDP OR central bank OR inflacja stopy",
    "kryptowaluty": "bitcoin OR ethereum OR cryptocurrency OR krypto",
    "geopolityka": "geopolitics OR sanctions OR trade tariff OR conflict economy",
    "polska_gospodarka": "Poland economy OR Warsaw Stock Exchange OR NBP OR GUS",
    "swiatowe_rynki": "global markets OR Wall Street OR European markets OR commodities",
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a
}

# Uszczelniona czarna lista domen i repozytoriów deweloperskich
EXCLUDED_DOMAINS = [
    "pagesix.com",
    "thoughtcatalog.com",
    "tmz.com",
    "pypi.org",
    "pypi.python.org",
    "github.com",
    "github.io",
    "gitlab.com",
    "buzzfeed.com",
    "dailymail.co.uk",
    "npmjs.com",
    "packaging.python.org",
    "libraries.io",
    "readthedocs.io",
    "crates.io",
    "hackernews",
]

EXCLUDED_TITLE_KEYWORDS = [
    "added to pypi",
    "show hn",
    "release notes",
    "v0.",
    "v1.",
    "commit",
    "pull request",
    "merge branch",
    "pypi",
    "python package",
    "python library",
    "package released",
    "package published",
    "tickfeed",
    "npm package",
    "github release",
    "stackoverflow",
]

RSS_SOURCES = {
    "gielda": [
        ("https://www.bankier.pl/rss/wiadomosci.xml", "Bankier.pl"),
        ("https://www.money.pl/rss/gielda.xml", "Money.pl Giełda"),
        (
            "https://news.google.com/rss/search?q=gie%C5%82da+GPW+WIG20+NASDAQ+akcje+when:7d&hl=pl&gl=PL&ceid=PL:pl",
            "Rynki Giełdowe",
        ),
    ],
    "makroekonomia": [
        ("https://www.bankier.pl/rss/waluty.xml", "Bankier.pl Makro i Waluty"),
        (
            "https://news.google.com/rss/search?q=inflacja+stopy+procentowe+PKB+bank+centralny+FED+EBC+when:7d&hl=pl&gl=PL&ceid=PL:pl",
            "Makroekonomia",
        ),
    ],
    "kryptowaluty": [
        ("https://bithub.pl/feed/", "BitHub.pl"),
        ("https://bitcoin.pl/feed", "Bitcoin.pl"),
        (
            "https://news.google.com/rss/search?q=bitcoin+ethereum+kryptowaluty+when:7d&hl=pl&gl=PL&ceid=PL:pl",
            "Rynek Krypto",
        ),
    ],
    "geopolityka": [
        ("https://defence24.pl/rss", "Defence24"),
        (
            "https://news.google.com/rss/search?q=geopolityka+sankcje+konflikt+handel+gospodarka+when:7d&hl=pl&gl=PL&ceid=PL:pl",
            "Geopolityka i Świat",
        ),
    ],
    "polska_gospodarka": [
        ("https://www.money.pl/rss/gospodarka.xml", "Money.pl Gospodarka"),
        (
            "https://news.google.com/rss/search?q=polska+gospodarka+NBP+GUS+inwestycje+GPW+when:7d&hl=pl&gl=PL&ceid=PL:pl",
            "Polska Gospodarka",
        ),
    ],
    "swiatowe_rynki": [
        (
            "https://news.google.com/rss/search?q=rynki+finansowe+USA+Azja+Europa+surowce+ropa+z%C5%82oto+when:7d&hl=pl&gl=PL&ceid=PL:pl",
            "Światowe Rynki",
        ),
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

<<<<<<< HEAD
TOPIC_KEYWORDS = {
    "gielda": (
        "giełd",
        "gield",
        "akcj",
        "spółk",
        "spolk",
        "wig20",
        "gpw",
        "nasdaq",
        "s&p",
        "wall street",
        "stock",
        "equity",
        "earnings",
        "shares",
        "dow jones",
        "indeks",
        "nvidia",
        "apple",
        "tesla",
        "microsoft",
    ),
    "makroekonomia": (
        "inflac",
        "cpi",
        "pkb",
        "gdp",
        "stop",
        "oprocent",
        "bank central",
        "banku central",
        "fed",
        "ebc",
        "ecb",
        "nbp",
        "bezroboc",
        "gospodar",
        "reces",
        "monetarn",
        "interest rate",
        "inflation",
        "employment",
    ),
    "kryptowaluty": (
        "bitcoin",
        "btc",
        "ethereum",
        "ether",
        "eth",
        "krypto",
        "crypto",
        "blockchain",
        "stablecoin",
        "solana",
        "altcoin",
        "binance",
    ),
    "geopolityka": (
        "geopolit",
        "sankcj",
        "wojn",
        "konflikt",
        "nato",
        "rosj",
        "ukrain",
        "chiny",
        "chinach",
        "tajwan",
        "iran",
        "izrael",
        "cł",
        "celn",
        "taryf",
        "trade war",
        "sanction",
        "war ",
        "conflict",
        "diplomac",
    ),
    "polska_gospodarka": (
        "polsk",
        "poland",
        "nbp",
        "gus",
        "gpw",
        "wig20",
        "złot",
        "zlot",
        "pln",
        "warszaw",
        "polskie",
        "budżet",
        "budzet",
        "orlen",
        "pko bp",
        "kghm",
    ),
    "swiatowe_rynki": (
        "rynk",
        "market",
        "wall street",
        "s&p",
        "nasdaq",
        "dow jones",
        "dax",
        "nikkei",
        "surow",
        "ropa",
        "oil",
        "gold",
        "złot",
        "giełd",
        "stock",
        "indeks",
        "global",
        "walut",
        "currency",
        "dolar",
        "dollar",
        "euro",
        "azj",
        "europ",
    ),
=======
# Tematyczne sygnały: wymagamy zgodności także przy odczycie STAREGO cache.
# Weryfikacja z tytułu/opisu to heurystyka; szczegółową selekcję można później
# rozwinąć o klasyfikator, ale bez wymyślania informacji.
TOPIC_KEYWORDS = {
    "gielda": ("giełd", "gield", "akcj", "spółk", "spolk", "wig20", "gpw", "nasdaq", "s&p", "wall street", "stock", "equity", "earnings", "shares", "dow jones", "indeks", "nvidia", "apple", "tesla", "microsoft"),
    "makroekonomia": ("inflac", "cpi", "pkb", "gdp", "stop", "oprocent", "bank central", "banku central", "fed", "ebc", "ecb", "nbp", "bezroboc", "gospodar", "reces", "monetarn", "interest rate", "inflation", "employment"),
    "kryptowaluty": ("bitcoin", "btc", "ethereum", "ether", "eth", "krypto", "crypto", "blockchain", "stablecoin", "solana", "altcoin", "binance"),
    "geopolityka": ("geopolit", "sankcj", "wojn", "konflikt", "nato", "rosj", "ukrain", "chiny", "chinach", "tajwan", "iran", "izrael", "cł", "celn", "taryf", "trade war", "sanction", "war ", "conflict", "diplomac"),
    "polska_gospodarka": ("polsk", "poland", "nbp", "gus", "gpw", "wig20", "złot", "zlot", "pln", "warszaw", "polskie", "budżet", "budzet", "orlen", "pko bp", "kghm"),
    "swiatowe_rynki": ("rynk", "market", "wall street", "s&p", "nasdaq", "dow jones", "dax", "nikkei", "surow", "ropa", "oil", "gold", "złot", "giełd", "stock", "indeks", "global", "walut", "currency", "dolar", "dollar", "euro", "azj", "europ"),
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a
}


def _is_relevant(article: dict, internal_cat: str) -> bool:
<<<<<<< HEAD
  title = _clean_html(str(article.get("title") or ""))
  description = _clean_html(str(article.get("description") or ""))
  url = str(article.get("url") or "").strip()
  source = article.get("source") or ""
  if isinstance(source, dict):
    source = source.get("name") or ""
  if not title or not url.startswith(("https://", "http://")):
    return False
  domain = (urlparse(url).hostname or "").lower()
  low_title = title.casefold()
  if any(x in domain for x in EXCLUDED_DOMAINS):
    return False
  if any(x in low_title for x in EXCLUDED_TITLE_KEYWORDS):
    return False
  if "[removed]" in low_title or "[usunięto]" in low_title:
    return False
  combined = (title + " " + description).casefold()
  return any(word in combined for word in TOPIC_KEYWORDS[internal_cat])


def _valid_cached_articles(internal_cat: str, limit: int) -> list[dict]:
  articles = get_news_from_silver(internal_cat, limit=max(limit, 50))
  articles = [a for a in articles if _is_relevant(a, internal_cat)]
  articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)
  return articles[:limit]


def _looks_polish(text: str) -> bool:
  t = f" {text.lower()} "
  return bool(re.search(r"[ąćęłńóśźż]", t)) or any(
      f" {w} " in t
      for w in (
          "jest",
          "oraz",
          "przez",
          "polsce",
          "gospodarka",
          "rynku",
          "ceny",
          "wzrost",
          "spadek",
          "banku",
          "akcje",
          "inflacja",
          "nowe",
          "nowy",
          "spada",
          "rośnie",
          "rosnie",
          "wobec",
          "według",
          "wedlug",
          "dane",
          "kurs",
          "wyniki",
          "inwestorzy",
          "prognoza",
          "zmiany",
          "reaguje",
          "po",
          "na",
          "dla",
          "ze",
      )
  )
=======
    title = _clean_html(str(article.get("title") or ""))
    description = _clean_html(str(article.get("description") or ""))
    url = str(article.get("url") or "").strip()
    source = article.get("source") or ""
    if isinstance(source, dict):
        source = source.get("name") or ""
    if not title or not url.startswith(("https://", "http://")):
        return False
    domain = (urlparse(url).hostname or "").lower()
    low_title = title.casefold()
    if any(x in domain for x in EXCLUDED_DOMAINS):
        return False
    if any(x in low_title for x in EXCLUDED_TITLE_KEYWORDS):
        return False
    if "[removed]" in low_title or "[usunięto]" in low_title:
        return False
    combined = (title + " " + description).casefold()
    return any(word in combined for word in TOPIC_KEYWORDS[internal_cat])


def _valid_cached_articles(internal_cat: str, limit: int) -> list[dict]:
    articles = _read_silver_safe(internal_cat, limit=max(limit, 50))
    articles = [a for a in articles if _is_relevant(a, internal_cat)]
    articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)
    return articles[:limit]


def _looks_polish(text: str) -> bool:
    # Polskojęzyczne RSS bez polskich znaków także przechodzą przy ich znanym źródle;
    # dla NewsAPI ten test odróżnia część nieprzetłumaczonych nagłówków.
    t = f" {text.lower()} "
    return bool(re.search(r"[ąćęłńóśźż]", t)) or any(
        f" {w} " in t for w in ("jest", "oraz", "przez", "polsce", "gospodarka", "rynku", "ceny", "wzrost", "spadek", "banku", "akcje", "inflacja", "nowe", "nowy", "spada", "rośnie", "rosnie", "wobec", "według", "wedlug", "dane", "kurs", "wyniki", "inwestorzy", "prognoza", "zmiany", "reaguje", "po", "na", "dla", "ze")
    )
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GeoMarketIntelligence/1.0"
    )
}


def resolve_category(category: str) -> tuple[str, str]:
<<<<<<< HEAD
  clean = (category or "").strip().lower().replace(" ", "_")
  if clean not in FRONTEND_TO_INTERNAL_CATEGORY:
    raise ValueError(f"Nieobsługiwana kategoria: {category}")
  internal_key = FRONTEND_TO_INTERNAL_CATEGORY[clean]
  frontend_key = INTERNAL_TO_FRONTEND_CATEGORY.get(internal_key, clean)
  return internal_key, frontend_key
=======
    clean = (category or "").strip().lower().replace(" ", "_")
    if clean not in FRONTEND_TO_INTERNAL_CATEGORY:
        raise ValueError(f"Nieobsługiwana kategoria: {category}")
    internal_key = FRONTEND_TO_INTERNAL_CATEGORY[clean]
    frontend_key = INTERNAL_TO_FRONTEND_CATEGORY.get(internal_key, clean)
    return internal_key, frontend_key
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a


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
<<<<<<< HEAD
  if not titles:
    return []

  prompt = (
      "Przetłumacz poniższe tytuły i opisy wiadomości finansowych i"
      " geopolitycznych na naturalny, rzeczowy język polski. Zachowaj fakty i"
      " nazwy własne, nie dopisuj informacji. Zwróć wynik WYŁĄCZNIE jako"
      ' poprawną tablicę JSON, dokładnie w tej samej kolejności: ["tytuł 1",'
      ' "tytuł 2", ...].\n\n'
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
=======
    if not titles:
        return []

    prompt = (
        "Przetłumacz poniższe tytuły i opisy wiadomości finansowych i geopolitycznych na naturalny, "
        "rzeczowy język polski. Zachowaj fakty i nazwy własne, nie dopisuj informacji. Zwróć wynik WYŁĄCZNIE jako poprawną tablicę JSON, "
        "dokładnie w tej samej kolejności: [\"tytuł 1\", \"tytuł 2\", ...].\n\n"
        f"Nagłówki:\n{json.dumps(titles, ensure_ascii=False)}"
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a
    )
    translated = json.loads(response.text)
    if isinstance(translated, list) and len(translated) == len(titles):
      return translated
  except Exception as e:
    logger.warning(f"Błąd tłumaczenia tytułów przez Gemini: {e}")

  return titles


def fetch_from_rss(internal_cat: str) -> list[dict]:
<<<<<<< HEAD
  feeds = RSS_SOURCES.get(internal_cat, [])
  frontend_cat = INTERNAL_TO_FRONTEND_CATEGORY.get(internal_cat, internal_cat)
  now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
  articles = []
  seen_urls = set()
=======
    feeds = RSS_SOURCES.get(internal_cat, [])
    frontend_cat = INTERNAL_TO_FRONTEND_CATEGORY.get(internal_cat, internal_cat)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    articles = []
    seen_urls = set()
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

  for feed_url, default_source_name in feeds:
    try:
      resp = requests.get(feed_url, headers=HEADERS, timeout=6)
      resp.raise_for_status()
      parsed = feedparser.parse(resp.content)

<<<<<<< HEAD
      for entry in parsed.entries[:15]:
        url = getattr(entry, "link", "").strip()
        title = _clean_html(getattr(entry, "title", ""))
        if not url or not title or url in seen_urls:
          continue
        if "kanał rss został" in title.lower() or "komunikat" == title.lower():
          continue
        if any(kw in title.lower() for kw in EXCLUDED_TITLE_KEYWORDS):
          continue
=======
            for entry in parsed.entries[:15]:
                url = getattr(entry, "link", "").strip()
                title = _clean_html(getattr(entry, "title", ""))
                if not url or not title or url in seen_urls:
                    continue
                if "kanał rss został" in title.lower() or "komunikat" == title.lower():
                    continue
                if any(kw in title.lower() for kw in EXCLUDED_TITLE_KEYWORDS):
                    continue
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

        source_name = default_source_name
        if hasattr(entry, "source") and isinstance(entry.source, dict):
          source_name = entry.source.get("title") or default_source_name

        raw_pub = getattr(entry, "published", None) or getattr(
            entry, "updated", None
        )
        pub_iso = _normalize_iso_date(raw_pub, now_iso)
        desc = _clean_html(
            getattr(entry, "summary", "") or getattr(entry, "description", "")
        )
        if not desc or desc == title:
          desc = (
              f"Wiadomość rynkowa z serwisu {source_name} w kategorii"
              f" {frontend_cat}."
          )

<<<<<<< HEAD
        candidate = {
            "title": title,
            "description": desc,
            "url": url,
            "source": source_name,
        }
        if not _is_relevant(candidate, internal_cat):
          continue
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

  return articles


def fetch_and_process_category(category_key: str) -> list[dict]:
  try:
    internal_cat, frontend_cat = resolve_category(category_key)
  except ValueError:
    internal_cat = category_key.strip().lower().replace(" ", "_")
    frontend_cat = internal_cat

  now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
  all_articles = fetch_from_rss(internal_cat)
  seen_urls = {a["url"] for a in all_articles}

  # Zasilenie kategorii "geopolityka" wydarzeniami z potoku wsadowego GDELT (Delta Lake)
  if internal_cat == "geopolityka":
    gdelt_events = get_gdelt_from_silver()
    gdelt_candidates = [
        ev
        for ev in gdelt_events[:5]
        if ev.get("url") and ev.get("title") and ev.get("url") not in seen_urls
    ]
    if gdelt_candidates:
      g_titles = [_clean_html(ev.get("title", "")) for ev in gdelt_candidates]
      trans_g_titles = _translate_titles_batch(g_titles)
      for ev, tr_title in zip(gdelt_candidates, trans_g_titles):
        if not _looks_polish(str(tr_title)):
          continue
        g_url = ev.get("url", "").strip()
        g_domain = ev.get("domain") or "GDELT 2.0"
        seen_urls.add(g_url)
        all_articles.append({
            "id": _hash_id(frontend_cat, g_url),
            "title": tr_title,
            "description": (
                f"Wydarzenie geopolityczne z bazy GDELT ({g_domain}):"
                f" {tr_title}"
            ),
            "source": f"GDELT / {g_domain}",
            "url": g_url,
            "image_url": None,
            "category": internal_cat,
            "published_at": ev.get("fetched_at", now_iso),
            "fetched_at": now_iso,
            "language": "pl",
        })

  if len(all_articles) < 10 and settings.NEWS_API_KEY:
    query = CATEGORY_MAPPING.get(internal_cat, internal_cat)
    raw_articles = []
=======
                candidate = {
                    "title": title, "description": desc, "url": url, "source": source_name
                }
                if not _is_relevant(candidate, internal_cat):
                    continue
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

    return articles


def fetch_and_process_category(category_key: str) -> list[dict]:
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a
    try:
      raw_articles = get_news(query, page_size=8)
    except Exception as e:
      logger.warning(f"NewsAPI niedostępne dla {internal_cat}: {e}")

    filtered_newsapi = []
    for art in raw_articles:
      source_name = (art.get("source", {}).get("name") or "").lower()
      url = (art.get("url") or "").strip().lower()
      title = (art.get("title") or "").strip().lower()

<<<<<<< HEAD
      if not url or not title or "[removed]" in title or url in seen_urls:
        continue
      if any(domain in url or domain in source_name for domain in EXCLUDED_DOMAINS):
        continue
      if any(kw in title for kw in EXCLUDED_TITLE_KEYWORDS):
        continue
      if not _is_relevant(
          {
              "title": art.get("title"),
              "description": art.get("description"),
              "url": art.get("url"),
              "source": source_name,
          },
          internal_cat,
      ):
        continue

      filtered_newsapi.append(art)

    selected_newsapi = filtered_newsapi[:5]
    orig_titles = [a.get("title", "") for a in selected_newsapi]
    descriptions = [
        _clean_html(a.get("description") or "") for a in selected_newsapi
    ]
    translated_items = _translate_titles_batch(orig_titles + descriptions)
    translated = translated_items[: len(orig_titles)]
    translated_descriptions = translated_items[len(orig_titles) :]

    for art, trans_title, trans_desc in zip(
        selected_newsapi, translated, translated_descriptions
    ):
      if not _looks_polish(str(trans_title)):
        logger.warning(
            "Pominięto anglojęzyczny nagłówek bez tłumaczenia: %s",
            str(trans_title)[:80],
        )
        continue
      url = art.get("url", "").strip()
      pub_iso = _normalize_iso_date(art.get("publishedAt"), now_iso)
      desc = (
          _clean_html(trans_desc)
          if _looks_polish(str(trans_desc))
          else trans_title
      )
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
=======
    if len(all_articles) < 10 and settings.NEWS_API_KEY:
        query = CATEGORY_MAPPING.get(internal_cat, internal_cat)
        raw_articles = []
        try:
            raw_articles = get_news(query, page_size=8)
        except Exception as e:
            logger.warning(f"NewsAPI niedostępne dla {internal_cat}: {e}")

        filtered_newsapi = []
        for art in raw_articles:
            source_name = (art.get("source", {}).get("name") or "").lower()
            url = (art.get("url") or "").strip().lower()
            title = (art.get("title") or "").strip().lower()

            if not url or not title or "[removed]" in title or url in seen_urls:
                continue
            if any(domain in url or domain in source_name for domain in EXCLUDED_DOMAINS):
                continue
            if any(kw in title for kw in EXCLUDED_TITLE_KEYWORDS):
                continue
            if not _is_relevant({"title": art.get("title"), "description": art.get("description"), "url": art.get("url"), "source": source_name}, internal_cat):
                continue
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

  all_articles = [a for a in all_articles if _is_relevant(a, internal_cat)]
  all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)

<<<<<<< HEAD
  if all_articles and not IS_VERCEL:
    save_news_to_silver(internal_cat, all_articles)

  return all_articles


def _format_article_for_api(article: dict, frontend_cat: str) -> dict:
  url = article.get("url", "")
  art_id = article.get("id") or _hash_id(frontend_cat, url)
  pub = article.get("published_at") or article.get("publishedAt") or ""
  img = (
      article.get("image_url")
      if "image_url" in article
      else article.get("imageUrl")
  )
  desc = article.get("description") or article.get("title", "")
=======
        selected_newsapi = filtered_newsapi[:5]
        orig_titles = [a.get("title", "") for a in selected_newsapi]
        # Tłumaczymy zarówno tytuły, jak i opisy jednym wywołaniem Gemini.
        descriptions = [_clean_html(a.get("description") or "") for a in selected_newsapi]
        translated_items = _translate_titles_batch(orig_titles + descriptions)
        translated = translated_items[:len(orig_titles)]
        translated_descriptions = translated_items[len(orig_titles):]

        for art, trans_title, trans_desc in zip(selected_newsapi, translated, translated_descriptions):
            # Nie pokazuj nagłówka po angielsku jako polski, jeśli tłumaczenie zawiodło.
            if not _looks_polish(str(trans_title)):
                logger.warning("Pominięto anglojęzyczny nagłówek bez tłumaczenia: %s", str(trans_title)[:80])
                continue
            url = art.get("url", "").strip()
            pub_iso = _normalize_iso_date(art.get("publishedAt"), now_iso)
            desc = _clean_html(trans_desc) if _looks_polish(str(trans_desc)) else trans_title
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

    all_articles = [a for a in all_articles if _is_relevant(a, internal_cat)]
    all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    _write_silver_safe(internal_cat, all_articles)

    return all_articles


def _format_article_for_api(article: dict, frontend_cat: str) -> dict:
    url = article.get("url", "")
    art_id = article.get("id") or _hash_id(frontend_cat, url)
    pub = article.get("published_at") or article.get("publishedAt") or ""
    img = article.get("image_url") if "image_url" in article else article.get("imageUrl")
    desc = article.get("description") or article.get("title", "")
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

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


<<<<<<< HEAD
def get_news_full_payload(
    category: str, limit: int = 25, refresh: bool = False
) -> dict:
  internal_cat, frontend_cat = resolve_category(category)

  articles = [] if refresh else _valid_cached_articles(internal_cat, limit)
  if not articles or len(articles) < 3:
    fetched = fetch_and_process_category(internal_cat)
    articles = [a for a in fetched if _is_relevant(a, internal_cat)]
    if not articles:
      articles = _valid_cached_articles(internal_cat, limit)
=======
def get_news_full_payload(category: str, limit: int = 25, refresh: bool = False) -> dict:
    internal_cat, frontend_cat = resolve_category(category)

    articles = [] if refresh else _valid_cached_articles(internal_cat, limit)
    if not articles or len(articles) < 3:
        fetched = fetch_and_process_category(internal_cat)
        # Filtruj ponownie nawet gdy w cache wciąż pozostają stare niepoprawne rekordy.
        articles = [a for a in fetched if _is_relevant(a, internal_cat)]
        if not articles:
            articles = _valid_cached_articles(internal_cat, limit)
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

  formatted_articles = [
      _format_article_for_api(a, frontend_cat) for a in articles[:limit]
  ]
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
<<<<<<< HEAD
  try:
    internal_cat, _ = resolve_category(symbol)
    articles = _valid_cached_articles(internal_cat, 25)
    if not articles:
      articles = [
          a
          for a in fetch_and_process_category(internal_cat)
          if _is_relevant(a, internal_cat)
      ]
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
                "published_at": _normalize_iso_date(
                    r.get("publishedAt"), now_iso
                ),
                "url": r.get("url", ""),
            }
            for r in raw
            if r.get("title") and r.get("url")
        ]
      except Exception:
        articles = []
=======
    try:
        internal_cat, _ = resolve_category(symbol)
        articles = _valid_cached_articles(internal_cat, 25)
        if not articles:
            articles = [a for a in fetch_and_process_category(internal_cat) if _is_relevant(a, internal_cat)]
    except ValueError:
        clean_sym = symbol.strip().upper()
        articles = _read_silver_safe(clean_sym.lower(), limit=15)
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
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

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
<<<<<<< HEAD
  internal_cat, frontend_cat = resolve_category(category)
  now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

  articles = _valid_cached_articles(internal_cat, 10)
  if not articles:
    articles = [
        a
        for a in fetch_and_process_category(internal_cat)
        if _is_relevant(a, internal_cat)
    ][:10]
=======
    internal_cat, frontend_cat = resolve_category(category)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    articles = [] if refresh else _valid_cached_articles(internal_cat, 10)
    if not articles:
        articles = [a for a in fetch_and_process_category(internal_cat) if _is_relevant(a, internal_cat)][:10]
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

  if not articles:
    return {
        "category": frontend_cat,
        "generatedAt": now_iso,
        "updated_at": now_iso,
        "summary": (
            "Brak bieżących artykułów źródłowych do przeprowadzenia analizy AI."
        ),
        "sentiment": "neutral",
        "market_impact": "Brak danych źródłowych.",
        "uncertainty": "high",
        "analyses": [],
    }

  current_top_ids = [
      a.get("id") or _hash_id(frontend_cat, a.get("url", ""))
      for a in articles[:6]
  ]

<<<<<<< HEAD
  if not refresh:
    cached = get_news_gold_analysis(internal_cat)
    if cached and isinstance(cached, dict) and cached.get("analyses"):
      cached_ids = cached.get("source_signature", [])
      if cached_ids == current_top_ids:
        cached["category"] = frontend_cat
        return cached

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
=======
    if not refresh:
        cached = _read_gold_safe(internal_cat)
        if cached and isinstance(cached, dict) and cached.get("analyses"):
            cached_ids = cached.get("source_signature", [])
            if cached_ids == current_top_ids:
                cached["category"] = frontend_cat
                return cached

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
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a

  prompt = (
      "Jesteś analitykiem rynkowym platformy GeoMarket Intelligence.\n"
      f"Kategoria: {frontend_cat} ({internal_cat}).\n"
      "Przeanalizuj poniższe rzeczywiste artykuły prasowe:\n"
      f"{json.dumps(articles_context, ensure_ascii=False, indent=2)}\n\n"
      "ZASADY:\n"
      "1. Opieraj się WYŁĄCZNIE na przekazanych artykułach. Nie zmyślaj faktów"
      " ani nie dawaj rekomendacji inwestycyjnych.\n"
      "2. Przygotuj 2-3 konkretne analizy tematyczne grupujące powyższe"
      " wiadomości.\n"
      "3. W polu 'sourceArticleIds' podaj prawdziwe identyfikatory 'id' z"
      " przekazanej listy.\n"
      "4. Pole 'sentiment' musi mieć wartość: 'positive', 'neutral' lub"
      " 'negative'.\n"
      "5. Pole 'riskLevel' musi mieć wartość: 'low', 'medium' lub 'high'.\n\n"
      "Zwróć WYŁĄCZNIE poprawny obiekt JSON w formacie:\n"
      "{\n"
      '  "overallSummary": "2-3 zdania ogólnego podsumowania kategorii po'
      ' polsku",\n'
      '  "overallSentiment": "positive | neutral | negative",\n'
      '  "overallImpact": "1-2 zdania o możliwych konsekwencjach rynkowych po'
      ' polsku",\n'
      '  "overallRisk": "low | medium | high",\n'
      '  "analyses": [\n'
      "    {\n"
      '      "id": "analysis-001",\n'
      '      "title": "Zwięzły tytuł analizy po polsku",\n'
      '      "summary": "2-3 zdania merytorycznego podsumowania AI po'
      ' polsku",\n'
      '      "affectedMarkets": ["Aktywo 1", "Aktywo 2"],\n'
      '      "sentiment": "positive | neutral | negative",\n'
      '      "riskLevel": "low | medium | high",\n'
      '      "potentialImpact": "Opis możliwych konsekwencji rynkowych (bez'
      ' rekomendacji kup/sprzedaj)",\n'
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
    default_markets = DEFAULT_MARKETS_BY_CATEGORY.get(
        internal_cat, ["Rynki finansowe"]
    )

    for i, item in enumerate(raw_analyses, start=1):
      src_ids = [
          sid for sid in item.get("sourceArticleIds", []) if sid in valid_ids
      ]
      if not src_ids and articles_context:
        src_ids = [
            articles_context[min(i - 1, len(articles_context) - 1)]["id"]
        ]

      sentiment = str(item.get("sentiment", "neutral")).lower()
      if sentiment not in {"positive", "neutral", "negative"}:
        sentiment = "neutral"

      risk = str(item.get("riskLevel", "medium")).lower()
      if risk not in {"low", "medium", "high"}:
        risk = "medium"

      affected = item.get("affectedMarkets") or default_markets
      if isinstance(affected, str):
        affected = [m.strip() for m in affected.split(",") if m.strip()]

      impact_text = (
          item.get("potentialImpact")
          or raw_ai.get("overallImpact")
          or "Możliwa podwyższona zmienność krótkoterminowa."
      )

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
        "summary": raw_ai.get("overallSummary")
        or (normalized_analyses[0]["summary"] if normalized_analyses else ""),
        "sentiment": raw_ai.get("overallSentiment", "neutral"),
        "market_impact": raw_ai.get("overallImpact", ""),
        "uncertainty": raw_ai.get("overallRisk", "medium"),
        "source_signature": current_top_ids,
        "analyses": normalized_analyses,
    }

    if not IS_VERCEL:
      save_news_gold_analysis(internal_cat, result_payload)
    return result_payload

  except Exception as e:
    logger.error(f"Błąd analizy Gemini dla kategorii {frontend_cat}: {e}")
    cached = get_news_gold_analysis(internal_cat)
    if cached and isinstance(cached, dict) and cached.get("analyses"):
      cached["category"] = frontend_cat
      cached["stale"] = True
      return cached

<<<<<<< HEAD
    default_markets = DEFAULT_MARKETS_BY_CATEGORY.get(
        internal_cat, ["Rynki finansowe"]
    )
    fallback_analysis = {
        "id": f"{frontend_cat}-analysis-fallback",
        "title": f"Przegląd wiadomości: {articles_context[0]['title'][:70]}",
        "summary": (
            "Usługa generowania analiz AI (Gemini) jest chwilowo"
            f" przeciążona. Pobrano {len(articles_context)} aktualnych"
            f" artykułów źródłowych dla kategorii '{frontend_cat}' (m.in. z:"
            f" {', '.join( sorted({a['source'] for a in articles_context[:3]}) )})."
        ),
        "affectedMarkets": default_markets,
        "sentiment": "neutral",
        "riskLevel": "medium",
        "uncertainty": "medium",
        "potentialImpact": (
            "Wymagana ponowna próba analizy po zwolnieniu limitów API."
        ),
        "market_impact": (
            "Wymagana ponowna próba analizy po zwolnieniu limitów API."
        ),
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
  return get_category_ai_analysis(category, refresh=False)
=======
        _write_gold_safe(internal_cat, result_payload)
        return result_payload

    except Exception as e:
        logger.error(f"Błąd analizy Gemini dla kategorii {frontend_cat}: {e}")
        cached = _read_gold_safe(internal_cat)
        if cached and isinstance(cached, dict) and cached.get("analyses"):
            cached["category"] = frontend_cat
            cached["stale"] = True
            return cached

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
            "potentialImpact": "Wymagana ponowna próba analizy po zwolnieniu limitów API.",
            "market_impact": "Wymagana ponowna próba analizy po zwolnieniu limitów API.",
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
    return get_category_ai_analysis(category, refresh=False)
>>>>>>> c6357038517f74371f6fa94bd869928bf5e64b8a
