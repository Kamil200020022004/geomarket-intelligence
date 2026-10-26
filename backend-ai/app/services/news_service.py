import json
from google import genai
from google.genai import types
from app.config.settings import settings
from app.data_sources.news import get_news
from app.models.news import NewsArticle, NewsResponse

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Mapowanie kategorii z przycisków na frontendzie na precyzyjne zapytania
CATEGORY_MAPPING = {
    "gielda": "gielda OR akcje OR 'stock market' OR gpw",
    "makroekonomia": "inflacja OR stopy procentowe OR pkb OR 'interest rates' OR inflation",
    "kryptowaluty": "bitcoin OR krypto OR kryptowaluty OR ethereum",
    "geopolityka": "geopolityka OR sankcje OR konflikt OR wojna OR 'geopolitics'",
    "polska gospodarka": "polska gospodarka OR wig20 OR nbp OR rpp OR gpw",
    "polska_gospodarka": "polska gospodarka OR wig20 OR nbp OR rpp OR gpw",
    "swiatowe rynki": "fed OR wall street OR 'global economy' OR surowce",
    "swiatowe_rynki": "fed OR wall street OR 'global economy' OR surowce",
}


def _translate_titles_batch(titles: list[str]) -> list[str]:
    """Tłumaczy listę nagłówków na język polski w jednym zapytaniu do Gemini."""
    if not titles:
        return []

    prompt = (
        "Przetłumacz poniższe nagłówki wiadomości finansowych na naturalny, profesjonalny język polski biznesowy. "
        "Zwróć wynik WYŁĄCZNIE jako tablicę JSON z przetłumaczonymi tytułami w tej samej kolejności, np. ['tytuł 1', 'tytuł 2'].\n\n"
        f"Nagłówki do przetłumaczenia:\n{json.dumps(titles, ensure_ascii=False)}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        translated = json.loads(response.text)
        if isinstance(translated, list) and len(translated) == len(titles):
            return translated
    except Exception:
        pass

    return titles  # Fallback: zwraca oryginał w razie błędu


def latest_news(symbol: str) -> NewsResponse:
    # 1. Sprawdzamy czy przekazano kategorię z przycisku, czy ticker spółki
    clean_key = symbol.strip().lower()
    query = CATEGORY_MAPPING.get(clean_key, symbol)

    raw_articles = get_news(query)

    # 2. Filtrujemy niechciane źródła (np. pypi.org) i usuwamy puste wpisy
    filtered_articles = []
    for art in raw_articles:
        source_name = art.get("source", {}).get("name", "") or ""
        url = art.get("url", "") or ""
        title = art.get("title", "") or ""

        # Odrzucamy puste tytuły i paczki biblioteczne
        if not title or "[Removed]" in title:
            continue
        if "pypi.org" in url or "pypi" in source_name.lower():
            continue

        filtered_articles.append(art)

    # Ograniczamy do 6 najświeższych wpisów pod widok kafelków
    selected_articles = filtered_articles[:6]

    # 3. Hurtowe tłumaczenie nagłówków przez Gemini (jedno szybkie wywołanie)
    original_titles = [a.get("title", "Brak tytułu") for a in selected_articles]
    translated_titles = _translate_titles_batch(original_titles)

    articles_list = []
    for art, trans_title in zip(selected_articles, translated_titles):
        news_item = NewsArticle(
            title=trans_title,
            source=art.get("source", {}).get("name", "Rynek"),
            published=art.get("publishedAt", ""),
            url=art.get("url", ""),
        )
        articles_list.append(news_item)

    return NewsResponse(articles=articles_list)