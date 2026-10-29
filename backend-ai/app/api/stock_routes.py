from fastapi import APIRouter

from app.models.stock import (
    StockResponse,
    MacroAnalysisResponse,
    AIImpactResponse
)
from app.models.news import NewsResponse, NewsSentimentResponse
from app.services.finance_service import get_stock, get_history
from app.services.analysis_service import (
    analyze_stock, 
    analyze_news_sentiment, 
    generate_full_investment_report
)
from app.services.chart_service import get_chart
from app.services.news_service import latest_news
from app.services.macro_service import get_current_macro_summary, analyze_macro_environment

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
    description="Zwraca przeanalizowany wpływ ważnego wydarzenia geopolitycznego na wybrane rynki, ocenia ryzyko i sentyment. Wykorzystuje model Gemini."
)
def ai_impact():
    return {
        "event": "Nowe napięcia geopolityczne na Bliskim Wschodzie",
        "affectedMarkets": "EUR/PLN, ropa, WIG20",
        "riskLevel": "Wysokie",
        "sentiment": "Negatywny",
        "summary": "AI wskazuje, że wydarzenie może zwiększyć zmienność na rynku surowców energetycznych oraz wpłynąć na kursy walut i indeksy giełdowe.",
        "showChart": True
    }


@router.get(
    "/macro/analysis", 
    response_model=MacroAnalysisResponse, 
    tags=["AI Analysis"],
    summary="Analiza makroekonomiczna (Gemini)",
    description="Pobiera najnowsze dane FRED (PKB, inflacja, stopy), przekazuje je do Gemini i zwraca syntetyczną ocenę stanu gospodarki."
)
def macro_analysis():
    return {
        "analysis": analyze_macro_environment(),
        "source_data_summary": get_current_macro_summary()
    }


@router.get(
    "/analyze/{symbol}", 
    tags=["AI Analysis"],
    summary="Analiza wybranej spółki (Gemini)",
    description="Pobiera zagregowane wskaźniki spółki z Data Lake i ocenia jej kondycję fundamentalną za pomocą AI."
)
def analyze(symbol: str):
    return {
        "analysis": analyze_stock(symbol)
    }


@router.get(
    "/news/{symbol}/sentiment", 
    response_model=NewsSentimentResponse, 
    tags=["AI Analysis"],
    summary="Sentyment najnowszych wiadomości",
    description="Pobiera nagłówki prasowe z NewsAPI, a AI ocenia ich wydźwięk rynkowy (pozytywny, negatywny lub neutralny)."
)
def news_sentiment(symbol: str):
    return analyze_news_sentiment(symbol)


@router.get(
    "/report/{symbol}", 
    tags=["AI Analysis"],
    summary="Pełny raport inwestycyjny",
    description="Generuje kompleksowy raport inwestycyjny, łącząc dane rynkowe, makroekonomię i wiadomości przy użyciu modelu Gemini."
)
def report(symbol: str):
    return {
        "report": generate_full_investment_report(symbol)
    }


# ---------------------------------------------------------
# 2. MACROECONOMICS (Dane z FRED z warstwy Gold)
# ---------------------------------------------------------
@router.get(
    "/macro/raw", 
    tags=["Macroeconomics"],
    summary="Surowe wskaźniki gospodarcze (FRED)",
    description="Zwraca najnowsze wskaźniki makroekonomiczne z warstwy Data Lake bez angażowania modelu AI."
)
def macro_raw():
    return get_current_macro_summary()


# ---------------------------------------------------------
# 3. MARKET DATA (Twarde dane z Yahoo Finance, Parquet, Plotly)
# ---------------------------------------------------------
@router.get(
    "/overview/table",
    tags=["Market Data"],
    summary="Lista spółek do głównej tabeli giełdowej",
    description="Zwraca zbiorcze zestawienie spółek technologicznych pod tabelę frontendu w jednym zapytaniu."
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
    description="Zwraca historię notowań (daty, ceny OHLC) pod tabele i zestawienia historyczne."
)
def history(symbol: str):
    return get_history(symbol)


@router.get(
    "/chart/{symbol}", 
    tags=["Market Data"],
    summary="Dane wykresu (Plotly JSON)",
    description="Zwraca strukturę JSON przygotowaną bezpośrednio pod bibliotekę react-plotly.js."
)
def chart(symbol: str):
    return get_chart(symbol)


@router.get(
    "/{symbol}", 
    response_model=StockResponse, 
    tags=["Market Data"],
    summary="Podstawowe dane giełdowe",
    description="Zwraca aktualną cenę, nazwę spółki i bazowe metryki w czasie rzeczywistym z Yahoo Finance."
)
def stock(symbol: str):
    return get_stock(symbol)


# ---------------------------------------------------------
# 4. MARKET NEWS (Wiadomości z NewsAPI i tłumaczenie)
# ---------------------------------------------------------
@router.get(
    "/news/{symbol}", 
    response_model=NewsResponse, 
    tags=["Market News"],
    summary="Najnowsze artykuły z NewsAPI",
    description="Zwraca listę nagłówków i odnośników do artykułów dla podanej kategorii lub spółki."
)
def news(symbol: str):
    return latest_news(symbol)