"""Endpointy danych rynkowych dla zakładek frontendu (potok strumieniowy Sebastiana)."""

from fastapi import APIRouter, Depends

from app.market import service
from app.market.schemas import CryptoOut, DashboardCardOut, MacroOut, StockOut
from app.market.sources import MarketDataSource, get_market_source

router = APIRouter(prefix="/api", tags=["dane rynkowe"])


@router.get("/stocks", response_model=list[StockOut], summary="Spółki do zakładki Giełda (StockMarket.jsx)")
def stocks(source: MarketDataSource = Depends(get_market_source)) -> list[StockOut]:
    return service.list_stocks(source)


@router.get("/crypto/top", response_model=list[CryptoOut], summary="TOP kryptowaluty do zakładki Krypto (Crypto.jsx)")
def crypto_top(source: MarketDataSource = Depends(get_market_source)) -> list[CryptoOut]:
    return service.list_crypto(source)


@router.get(
    "/macro",
    response_model=list[MacroOut],
    summary="Kursy walut, surowce i wskaźniki makro do zakładki Makro (Macro.jsx)",
    description=(
        "Kursy i surowce pochodzą z potoku strumieniowego, inflacja, stopy i PKB z serwisu AI (FRED). "
        "Gdy serwis AI jest niedostępny, wskaźniki mają value=null, history=[] i source=\"unavailable\"."
    ),
)
def macro(source: MarketDataSource = Depends(get_market_source)) -> list[MacroOut]:
    return service.list_macro(source)


@router.get(
    "/dashboard/markets",
    response_model=list[DashboardCardOut],
    summary="Kafelki rynkowe na stronę główną (zastępują mock/markets.json)",
)
def dashboard_markets(source: MarketDataSource = Depends(get_market_source)) -> list[DashboardCardOut]:
    return service.dashboard_cards(source)
