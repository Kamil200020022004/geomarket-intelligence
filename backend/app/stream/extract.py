"""Extract: pobieranie danych ze źródeł (Yahoo Finance przez yfinance, CoinGecko przez REST).

Oba źródła są odpytywane (polling) — nie wysyłają danych same. Strumień zdarzeń powstaje
w producencie: każda odpowiedź staje się wiadomością w Kafce.
"""

import logging
import math
from datetime import UTC, datetime
from typing import Any

import httpx
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
_OHLCV = ("Open", "High", "Low", "Close", "Volume")


def _clean_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(number) or math.isinf(number) else number


def frame_to_bars(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Ramka OHLCV jednego instrumentu → lista świec z czasem w UTC (od najstarszej), bez pustych wierszy."""
    if frame is None or frame.empty:
        return []
    index = frame.index
    if index.tz is None:
        # yfinance zwraca indeks ze strefą giełdy; bez strefy nie wiemy, który to moment — odrzucamy.
        raise ValueError("indeks bez strefy czasowej")
    bars = []
    for ts, row in zip(index.tz_convert(UTC), frame.itertuples(index=False), strict=True):
        values = dict(zip(frame.columns, row, strict=True))
        close = _clean_number(values.get("Close"))
        if close is None:
            continue  # brak notowania w tym przedziale (np. świeca bez transakcji w danych dziennych)
        bars.append(
            {
                "ts": ts.isoformat().replace("+00:00", "Z"),
                "open": _clean_number(values.get("Open")),
                "high": _clean_number(values.get("High")),
                "low": _clean_number(values.get("Low")),
                "close": close,
                "volume": _clean_number(values.get("Volume")),
            }
        )
    return bars


def split_download(frame: pd.DataFrame, source_symbols: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Wynik `yf.download(..., group_by="ticker")` → świece per symbol źródła."""
    result: dict[str, list[dict[str, Any]]] = {}
    if frame is None or frame.empty:
        return result
    multi = isinstance(frame.columns, pd.MultiIndex)
    for symbol in source_symbols:
        try:
            sub = frame[symbol] if multi else frame
        except KeyError:
            continue
        columns = [column for column in _OHLCV if column in sub.columns]
        bars = frame_to_bars(sub[columns])
        if bars:
            result[symbol] = bars
    return result


def fetch_yahoo_bars(
    source_symbols: list[str],
    interval: str,
    *,
    period: str | None = None,
    start: datetime | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Jedno zbiorcze zapytanie do Yahoo dla wszystkich symboli (mniej zapytań = mniejsze ryzyko blokady)."""
    frame = yf.download(
        source_symbols,
        interval=interval,
        period=period,
        start=start,
        group_by="ticker",
        auto_adjust=False,  # ceny faktyczne, nie korygowane o dywidendy
        progress=False,
        threads=True,
    )
    return split_download(frame, source_symbols)


def fetch_instrument_info(source_symbol: str) -> dict[str, Any] | None:
    """Dane referencyjne spółki: liczba akcji (do kapitalizacji), waluta, giełda."""
    try:
        info = yf.Ticker(source_symbol).fast_info
        return {
            "shares": _clean_number(info.get("shares")),
            "currency": info.get("currency"),
            "exchange": info.get("exchange"),
        }
    except Exception as error:  # yfinance zgłasza różne wyjątki zależnie od rodzaju błędu
        logger.warning("Brak danych referencyjnych dla %s: %s", source_symbol, type(error).__name__)
        return None


def fetch_coingecko_top(limit: int, api_key: str = "", client: httpx.Client | None = None) -> list[dict[str, Any]]:
    """TOP N kryptowalut wg kapitalizacji z 7-dniowym wykresem godzinowym (sparkline)."""
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "true",
        "price_change_percentage": "1h,24h,7d",
    }
    headers = {"x-cg-demo-api-key": api_key} if api_key else {}
    http = client or httpx.Client(timeout=20.0)
    try:
        response = http.get(COINGECKO_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    finally:
        if client is None:
            http.close()
    if not isinstance(data, list):
        raise ValueError("nieoczekiwana odpowiedź CoinGecko")
    return data


def utc_now() -> datetime:
    return datetime.now(UTC)
