from google import genai
from google.genai import types

from app.ai.system_prompt import SYSTEM_PROMPT
from app.config.settings import settings
from app.data_sources.yahoo import get_stock_data
from app.services.news_service import latest_news
from app.models.news import NewsSentimentResponse

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_stock(symbol: str):
    data = get_stock_data(symbol)

    prompt = f"""
{SYSTEM_PROMPT}

Odpowiedz maksymalnie w 300 słowach.

Na podstawie poniższych danych przygotuj profesjonalną analizę inwestycyjną.

Dane spółki:

Nazwa: {data['company']}
Symbol: {data['symbol']}
Sektor: {data['sector']}
Branża: {data['industry']}
Aktualna cena: {data['current_price']} {data['currency']}
Poprzednie zamknięcie: {data['previous_close']}
Dzienne maksimum: {data['day_high']}
Dzienne minimum: {data['day_low']}
Kapitalizacja rynkowa: {data['market_cap']}
Wskaźnik P/E: {data['pe_ratio']}

Przygotuj analizę zawierającą:

1. Krótkie podsumowanie spółki.
2. Mocne strony.
3. Ryzyka.
4. Ocenę obecnej sytuacji.
5. Wniosek dla inwestora.

Odpowiadaj po polsku.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=500,  # Ograniczenie tokenów wyjściowych
            temperature=0.3,
        ),
    )

    return response.text


# --- NOWA FUNKCJA ANALIZY SENTYMENTU NEWSÓW ---
def analyze_news_sentiment(symbol: str) -> NewsSentimentResponse:
    news_data = latest_news(symbol)
    
    # Bierzemy max 3 artykuły (oszczędność tokenów wejściowych)
    top_articles = news_data.articles[:3]
    news_text = "\n".join([f"- {article.title}" for article in top_articles])
    
    prompt = f"""
    Oceń sentyment nagłówków finansowych dla spółki {symbol}.
    Dla każdego podaj sentyment (Pozytywny, Neutralny, Negatywny) i max 1 zdanie uzasadnienia.
    Zwróć ogólny sentyment.
    
    Nagłówki:
    {news_text}
    """
    
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NewsSentimentResponse,
            max_output_tokens=300,  # Limit tokenów wyjściowych dla JSON
            temperature=0.2,
        ),
    )
    
    return NewsSentimentResponse.model_validate_json(response.text)

from functools import lru_cache
from google import genai
from google.genai import types

from app.config.settings import settings
from app.data_sources.yahoo import get_stock_data
from app.services.news_service import latest_news
from app.services.macro_service import get_current_macro_summary

client = genai.Client(api_key=settings.GEMINI_API_KEY)


# DEKORATOR CACHE: Zapamiętuje wynik funkcji na 100 ostatnich zapytań.
# Dzięki temu powtórne zapytanie o ten sam symbol NIE ZUŻYWA ŻADNYCH TOKENÓW Gemini!
@lru_cache(maxsize=100)
def generate_full_investment_report(symbol: str) -> str:
    # 1. Pobieramy dane
    stock_data = get_stock_data(symbol)
    news_data = latest_news(symbol)
    macro_data = get_current_macro_summary()
    
    # 2. OPTYMALIZACJA WEJŚCIA: Obcinamy nagłówki do max 60 znaków i bierzemy tylko 2 artykuły
    short_news = [f"- {art.title[:60]}..." for art in news_data.articles[:2]]
    news_str = "\n".join(short_news) if short_news else "Brak newsów."
    
    # 3. Ultrazwięzły prompt
    prompt = f"""
    Zrób krótki Raport dla {symbol}.
    
    Dane:
    - Spółka: {stock_data.get('company')} | Cena: {stock_data.get('current_price')} {stock_data.get('currency')} | P/E: {stock_data.get('pe_ratio')}
    - Sektor: {stock_data.get('sector')}
    - Makro USA: PKB {macro_data['GDP']['value']}, Inflacja {macro_data['CPI_Inflation']['value']}, Stopa FED {macro_data['Fed_Interest_Rate']['value']}%
    - Newsy: {news_str}
    
    Napisz w Markdown po polsku (max 200 słów):
    1. Sytuacja spółki
    2. Otoczenie makro
    3. Werdykt
    """
    
    # 4. TWARDY LIMIT WYJŚCIA (350 tokenów ≈ 200 słów)
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=350,  # Drastyczne cięcie kosztów
            temperature=0.2,        # Bardzo zwięzła i konkretna odpowiedź
        ),
    )
    
    return response.text