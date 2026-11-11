from fastapi import APIRouter

from app.models.news import NewsResponse, NewsSentimentResponse
from app.models.stock import (
    AIImpactResponse,
    MacroAnalysisResponse,
    StockResponse,
)
from app.services.analysis_service import (
    analyze_news_sentiment,
    analyze_stock,
    generate_dynamic_ai_impact,
    generate_full_investment_report,
)
from app.services.data_lake_service import get_gdelt_from_silver
from app.services.finance_service import get_history, get_stock
from app.services.macro_service import analyze_macro_environment, get_current_macro_summary
from app.services.news_service import latest_news

router = APIRouter(prefix="/stock")

TOP_STOCKS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"]


# ---------------------------------------------------------
# 1. AI ANALYSIS (Wykorzystanie modelu Gemini)
# ---------------------------------------------------------
@router.get(
    "/ai-impact",
    response_model=AIImpactResponse,
    tags=["AI Analysis"],
    summary="Wpływ wydarzeń na rynki (AI Impact)",
    description=(
        "Dynamicznie analizuje wpływ bieżących wydarzeń rynkowo-geopolitycznych"
        " za pomocą modelu Gemini."
    ),
)
def ai_impact():
  return generate_dynamic_ai_impact("geopolityka")


@router.get(
    "/macro/analysis",
    response_model=MacroAnalysisResponse,
    tags=["AI Analysis"],
    summary="Analiza makroekonomiczna (Gemini)",
    description=(
        "Pobiera najnowsze dane FRED (USA, Polska, Strefa Euro), przekazuje je"
        " do Gemini i zwraca syntetyczną ocenę stanu gospodarki."
    ),
)
def macro_analysis():
  return {
      "analysis": analyze_macro_environment(),
      "source_data_summary": get_current_macro_summary(),
  }


@router.get(
    "/analyze/{symbol}",
    tags=["AI Analysis"],
    summary="Analiza wybranej spółki (Gemini)",
    description=(
        "Pobiera wskaźniki spółki i ocenia jej kondycję fundamentalną za pomocą"
        " AI (zgodnie z zasadą bez porad inwestycyjnych)."
    ),
)
def analyze(symbol: str):
  return {"analysis": analyze_stock(symbol)}


@router.get(
    "/news/{symbol}/sentiment",
    response_model=NewsSentimentResponse,
    tags=["AI Analysis"],
    summary="Sentyment najnowszych wiadomości",
    description=(
        "Pobiera nagłówki prasowe z NewsAPI/RSS, a AI ocenia ich wydźwięk"
        " rynkowy (pozytywny, negatywny lub neutralny)."
    ),
)
def news_sentiment(symbol: str):
  return analyze_news_sentiment(symbol)


@router.get(
    "/report/{symbol}",
    tags=["AI Analysis"],
    summary="Pełny raport inwestycyjny",
    description=(
        "Generuje zwięzły raport analityczny łącząc dane giełdowe,"
        " makroekonomię i newsy przy użyciu modelu Gemini z pamięcią podręczną"
        " cache."
    ),
)
def report(symbol: str):
  return {"report": generate_full_investment_report(symbol)}


# ---------------------------------------------------------
# 2. MACROECONOMICS (Dane z FRED z warstwy Gold)
# ---------------------------------------------------------
@router.get(
    "/macro/raw",
    tags=["Macroeconomics"],
    summary="Surowe wskaźniki gospodarcze (FRED)",
    description=(
        "Zwraca najnowsze wskaźniki makroekonomiczne (USA, Polska, Strefa Euro)"
        " z warstwy Data Lake wraz z 12-punktową historią obserwacji."
    ),
)
def macro_raw():
  return get_current_macro_summary()


# ---------------------------------------------------------
# 3. MARKET DATA
# ---------------------------------------------------------
@router.get(
    "/overview/table",
    tags=["Market Data"],
    summary="Lista spółek do głównej tabeli giełdowej",
    description=(
        "Zwraca zbiorcze zestawienie spółek technologicznych pod tabelę"
        " frontendu w jednym zapytaniu HTTP."
    ),
)
def stock_table():
  overview = []
  for sym in TOP_STOCKS:
    try:
      data = get_stock(sym)
      d = data.model_dump() if hasattr(data, "model_dump") else dict(data)
      overview.append(d)
    except Exception:
      pass
  return overview


@router.get(
    "/history/{symbol}",
    tags=["Market Data"],
    summary="Historia notowań (Tabela)",
    description=(
        "Zwraca historię notowań (daty, ceny OHLC) pod tabele i zestawienia"
        " historyczne."
    ),
)
def history(symbol: str):
  return get_history(symbol)


@router.get(
    "/{symbol}",
    response_model=StockResponse,
    tags=["Market Data"],
    summary="Podstawowe dane giełdowe",
    description=(
        "Zwraca aktualną cenę, nazwę spółki i bazowe metryki na potrzeby analiz"
        " AI."
    ),
)
def stock(symbol: str):
  return get_stock(symbol)


# ---------------------------------------------------------
# 4. MARKET NEWS (Wiadomości z NewsAPI / RSS)
# ---------------------------------------------------------
@router.get(
    "/news/{symbol}",
    response_model=NewsResponse,
    tags=["Market News"],
    summary="Najnowsze artykuły z NewsAPI / RSS",
    description=(
        "Zwraca listę nagłówków i odnośników do artykułów dla podanej kategorii"
        " lub spółki."
    ),
)
def news(symbol: str):
  return latest_news(symbol)


# ---------------------------------------------------------
# 5. GEOPOLITICS & GDELT (Potok wsadowy)
# ---------------------------------------------------------
@router.get(
    "/gdelt/events",
    tags=["Geopolitics & GDELT"],
    summary="Najnowsze zdarzenia geopolityczne z potoku wsadowego GDELT",
    description=(
        "Zwraca ustrukturyzowane wydarzenia geopolityczne pobrane wsadowo i"
        " zapisane w warstwie Silver Lakehouse'a."
    ),
)
def get_gdelt_events():
  return {
      "source": "GDELT Project 2.0 Doc API",
      "events": get_gdelt_from_silver(),
  }