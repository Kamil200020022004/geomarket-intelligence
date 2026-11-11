from functools import lru_cache
import json
from google import genai
from google.genai import types

from app.ai.system_prompt import SYSTEM_PROMPT
from app.config.settings import settings
from app.models.news import NewsSentimentResponse
from app.models.stock import AIImpactResponse
from app.services.data_lake_service import get_gdelt_from_silver
from app.services.finance_service import get_stock
from app.services.macro_service import get_current_macro_summary
from app.services.news_service import latest_news

client = genai.Client(api_key=settings.GEMINI_API_KEY)

DISCLAIMER = (
    "\n\n---\n*Zastrzeżenie: Prezentowane analizy mają charakter wyłącznie"
    " informacyjno-edukacyjny i nie stanowią rekomendacji inwestycyjnych w"
    " rozumieniu przepisów prawa.*"
)


def analyze_stock(symbol: str) -> str:
  stock_obj = get_stock(symbol)
  data = (
      stock_obj.model_dump()
      if hasattr(stock_obj, "model_dump")
      else dict(stock_obj)
  )

  prompt = f"""
{SYSTEM_PROMPT}

Odpowiedz maksymalnie w 250-300 słowach.

Na podstawie poniższych danych przygotuj profesjonalną analizę spółki.

Dane spółki:
Nazwa: {data.get('company')}
Symbol: {data.get('symbol')}
Sektor: {data.get('sector')}
Branża: {data.get('industry')}
Aktualna cena: {data.get('current_price')} {data.get('currency')}
Poprzednie zamknięcie: {data.get('previous_close')}
Dzienne maksimum: {data.get('day_high')}
Dzienne minimum: {data.get('day_low')}
Kapitalizacja rynkowa: {data.get('market_cap')}
Wskaźnik P/E: {data.get('pe_ratio')}

Przygotuj analizę zawierającą:
1. Krótkie podsumowanie profilu działalności spółki.
2. Kluczowe mocne strony i fundamenty.
3. Główne czynniki ryzyka rynkowego i sektorowego.
4. Ocenę bieżącej wyceny na tle wskaźników.
5. Czynniki do dalszej obserwacji (BEZ formułowania rekomendacji kupna/sprzedaży).

Odpowiadaj po polsku.
"""

  response = client.models.generate_content(
      model="gemini-3.5-flash-lite",
      contents=prompt,
      config=types.GenerateContentConfig(
          max_output_tokens=500,
          temperature=0.3,
      ),
  )

  return (response.text or "") + DISCLAIMER


def analyze_news_sentiment(symbol: str) -> NewsSentimentResponse:
  news_data = latest_news(symbol)

  top_articles = news_data.articles[:3]
  news_text = "\n".join([f"- {article.title}" for article in top_articles])

  prompt = f"""
    Oceń sentyment nagłówków finansowych dla symbolu {symbol}.
    Dla każdego podaj sentyment (Pozytywny, Neutralny, Negatywny) i max 1 zdanie uzasadnienia.
    Zwróć ogólny sentyment.
    
    Nagłówki:
    {news_text if news_text else "Brak bieżących nagłówków."}
    """

  response = client.models.generate_content(
      model="gemini-3.5-flash-lite",
      contents=prompt,
      config=types.GenerateContentConfig(
          response_mime_type="application/json",
          response_schema=NewsSentimentResponse,
          max_output_tokens=300,
          temperature=0.2,
      ),
  )

  return NewsSentimentResponse.model_validate_json(response.text)


@lru_cache(maxsize=100)
def generate_full_investment_report(symbol: str) -> str:
  stock_obj = get_stock(symbol)
  stock_data = (
      stock_obj.model_dump()
      if hasattr(stock_obj, "model_dump")
      else dict(stock_obj)
  )
  news_data = latest_news(symbol)
  macro_data = get_current_macro_summary()

  short_news = [f"- {art.title[:60]}..." for art in news_data.articles[:2]]
  news_str = "\n".join(short_news) if short_news else "Brak newsów."

  prompt = f"""
    Zrób krótki raport analityczny dla spółki {symbol}.
    
    Dane:
    - Spółka: {stock_data.get('company')} | Cena: {stock_data.get('current_price')} {stock_data.get('currency')} | P/E: {stock_data.get('pe_ratio')}
    - Sektor: {stock_data.get('sector')}
    - Makro USA: PKB dynamika {macro_data.get('GDP', {}).get('value')}%, Inflacja r/r {macro_data.get('CPI_Inflation', {}).get('value')}%, Stopa FED {macro_data.get('Fed_Interest_Rate', {}).get('value')}%
    - Newsy: {news_str}
    
    Napisz w Markdown po polsku (max 200 słów):
    1. Sytuacja fundamentalna spółki
    2. Wpływ otoczenia makroekonomicznego
    3. Podsumowanie analityczne (BEZ rekomendacji doradczych)
    """

  response = client.models.generate_content(
      model="gemini-3.5-flash-lite",
      contents=prompt,
      config=types.GenerateContentConfig(
          max_output_tokens=350,
          temperature=0.2,
      ),
  )

  return (response.text or "") + DISCLAIMER


def generate_dynamic_ai_impact(
    category_or_topic: str = "geopolityka",
) -> AIImpactResponse:
  """Dynamiczna karta AI Impact generowana przez Gemini na podstawie bieżących newsów i GDELT."""
  news_data = latest_news(category_or_topic)
  headlines = [art.title for art in news_data.articles[:3]]

  gdelt_events = get_gdelt_from_silver()
  for ev in gdelt_events[:3]:
    title = ev.get("title")
    if title and title not in headlines:
      headlines.append(f"[GDELT Event] {title}")

  headlines_str = (
      "\n".join([f"- {h}" for h in headlines])
      if headlines
      else "Brak bieżących nagłówków."
  )

  prompt = f"""
Jesteś analitykiem ryzyka rynkowego i geopolitycznego platformy GeoMarket Intelligence.
Na podstawie poniższych ostatnich doniesień medialnych oraz globalnych zdarzeń GDELT:
{headlines_str}

Zidentyfikuj najważniejsze bieżące wydarzenie lub trend geopolityczno-gospodarczy i oceń jego rynkowy wpływ.
Zwróć wynik jako JSON o polach:
{{
  "event": "Krótka nazwa kluczowego wydarzenia geopolitycznego lub makro",
  "affectedMarkets": "Główne rynki i aktywa (np. ropa, EUR/PLN, złoto, indeksy giełdowe)",
  "riskLevel": "Niskie / Średnie / Wysokie",
  "sentiment": "Pozytywny / Neutralny / Negatywny",
  "summary": "2-3 zdaniowa zwięzła synteza wpływu wydarzenia na rynki finansowe.",
  "showChart": true
}}
"""

  try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=300,
            temperature=0.2,
        ),
    )
    data = json.loads(response.text)
    return AIImpactResponse(**data)
  except Exception:
    return AIImpactResponse(
        event="Napięcia geopolityczne i zmiany polityki monetarnej",
        affectedMarkets="Rynki surowców energetycznych, waluty, obligacje",
        riskLevel="Średnie",
        sentiment="Neutralny",
        summary=(
            "AI wskazuje na umiarkowaną zmienność na rynkach w obliczu"
            " napływających danych makro i wydarzeń międzynarodowych."
        ),
        showChart=True,
    )