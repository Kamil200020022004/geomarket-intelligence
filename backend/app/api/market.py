"""Endpointy danych rynkowych dla zakładek frontendu (potok strumieniowy Sebastiana).

Gotowe odpowiedzi JSON są trzymane w pamięci przez `MARKET_CACHE_SECONDS` (15 s) — tyle samo,
ile API trzyma odczyt tabel Gold. Bez tego każde zapytanie budowało od nowa JSON ze 100 spółkami
po ok. 150 punktów historii; test obciążeniowy (200 użytkowników) pokazał, że to było wąskie
gardło (proces API na 95% CPU, mediana /api/stocks 4,6 s).
"""

import threading
import time
from collections.abc import Callable

from fastapi import APIRouter, Depends, Response
from pydantic import TypeAdapter

from app.core.config import get_settings
from app.market import service
from app.market.schemas import CryptoOut, DashboardCardOut, MacroOut, StockOut
from app.market.sources import MarketDataSource, get_market_source

router = APIRouter(prefix="/api", tags=["dane rynkowe"])

_responses: dict[str, tuple[float, bytes]] = {}
_build_lock = threading.Lock()


def clear_response_cache() -> None:
    _responses.clear()


def _cached_json(key: str, model: type, build: Callable[[], list]) -> Response:
    """Zwraca zapamiętany JSON; po upływie czasu buduje go raz (blokada: równoległe zapytania nie liczą go wielokrotnie)."""
    ttl = get_settings().market_cache_seconds
    cached = _responses.get(key)
    if cached is None or time.monotonic() - cached[0] > ttl:
        with _build_lock:
            cached = _responses.get(key)
            if cached is None or time.monotonic() - cached[0] > ttl:
                body = TypeAdapter(list[model]).dump_json(build())
                cached = (time.monotonic(), body)
                _responses[key] = cached
    return Response(content=cached[1], media_type="application/json")


@router.get("/stocks", response_model=list[StockOut], summary="Spółki do zakładki Giełda (StockMarket.jsx)")
def stocks(source: MarketDataSource = Depends(get_market_source)) -> Response:
    return _cached_json(f"{source.name}:stocks", StockOut, lambda: service.list_stocks(source))


@router.get("/crypto/top", response_model=list[CryptoOut], summary="TOP kryptowaluty do zakładki Krypto (Crypto.jsx)")
def crypto_top(source: MarketDataSource = Depends(get_market_source)) -> Response:
    return _cached_json(f"{source.name}:crypto", CryptoOut, lambda: service.list_crypto(source))


@router.get(
    "/macro",
    response_model=list[MacroOut],
    summary="Kursy walut, surowce i wskaźniki makro do zakładki Makro (Macro.jsx)",
    description=(
        "Kursy i surowce pochodzą z potoku strumieniowego, inflacja, stopy i PKB z serwisu AI (FRED). "
        "Gdy serwis AI jest niedostępny, wskaźniki mają value=null, history=[] i source=\"unavailable\"."
    ),
)
def macro(source: MarketDataSource = Depends(get_market_source)) -> Response:
    return _cached_json(f"{source.name}:macro", MacroOut, lambda: service.list_macro(source))


@router.get(
    "/dashboard/markets",
    response_model=list[DashboardCardOut],
    summary="Kafelki rynkowe na stronę główną (zastępują mock/markets.json)",
)
def dashboard_markets(source: MarketDataSource = Depends(get_market_source)) -> Response:
    return _cached_json(f"{source.name}:dashboard", DashboardCardOut, lambda: service.dashboard_cards(source))
