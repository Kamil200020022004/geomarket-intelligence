from fastapi import APIRouter

from app.models.stock import StockResponse
from app.models.news import NewsResponse, NewsSentimentResponse
from app.services.finance_service import get_stock, get_history
from app.services.analysis_service import analyze_stock, analyze_news_sentiment
from app.services.chart_service import get_chart
from app.services.news_service import latest_news
from app.services.macro_service import get_current_macro_summary, analyze_macro_environment
from app.services.analysis_service import generate_full_investment_report

router = APIRouter(prefix="/stock", tags=["Stocks"])


@router.get("/{symbol}", response_model=StockResponse)
def stock(symbol: str):
    return get_stock(symbol)


@router.get("/analyze/{symbol}")
def analyze(symbol: str):
    return {
        "analysis": analyze_stock(symbol)
    }


@router.get("/history/{symbol}")
def history(symbol: str):
    return get_history(symbol)


@router.get("/chart/{symbol}")
def chart(symbol: str):
    return get_chart(symbol)


# --- NEWSY I SENTYMENT (zmienione z async def na def) ---
@router.get("/news/{symbol}", response_model=NewsResponse)
def news(symbol: str):
    return latest_news(symbol)


@router.get("/news/{symbol}/sentiment", response_model=NewsSentimentResponse)
def news_sentiment(symbol: str):
    return analyze_news_sentiment(symbol)


# --- MAKROEKONOMIA FRED (zmienione z async def na def) ---
@router.get("/macro/raw")
def macro_raw():
    return get_current_macro_summary()


@router.get("/macro/analysis")
def macro_analysis():
    return {"analysis": analyze_macro_environment()}

@router.get("/report/{symbol}")
def report(symbol: str):
    return {
        "report": generate_full_investment_report(symbol)
    }