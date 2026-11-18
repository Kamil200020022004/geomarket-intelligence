"""Budowanie odpowiedzi dla zakładek Giełda, Krypto, Makro i Dashboard.

Warstwa mapowania: dane z potoku (źródło `MarketDataSource`) i dane makro z serwisu AI
zamieniane są na dokładnie te pola, które czytają komponenty React (`schemas.py`).
"""

import logging
from datetime import UTC, date, datetime
from typing import Any

from app.market import catalog
from app.market.schemas import CryptoOut, DashboardCardOut, MacroOut, PricePoint, Sparkline, StockOut, ValuePoint
from app.market.sources import MarketDataSource
from app.services import ai_gateway

logger = logging.getLogger(__name__)

MACRO_RAW_TTL_SECONDS = 3600  # dane FRED są miesięczne/kwartalne — odświeżanie co godzinę wystarcza
# Zakładka Makro nie może czekać na serwis AI tak długo jak czat (kursy z naszego potoku są gotowe od razu).
MACRO_RAW_TIMEOUT_SECONDS = 10.0


# --------------------------------------------------------------------------------------
# Giełda
# --------------------------------------------------------------------------------------


def list_stocks(source: MarketDataSource) -> list[StockOut]:
    result = []
    for instrument in catalog.STOCKS:
        snap = source.snapshot(instrument)
        result.append(
            StockOut(
                symbol=instrument.symbol,
                name=instrument.name,
                market=catalog.MARKET_LABELS[instrument.market or "US"],
                price=snap.price,
                change=snap.change_24h_pct,
                volume=snap.volume,
                marketCap=snap.market_cap,
                history=[PricePoint(time=t, price=p) for t, p in snap.history],
                currency=instrument.currency,
                source=source.name,
                updated_at=snap.updated_at,
            )
        )
    return result


# --------------------------------------------------------------------------------------
# Kryptowaluty
# --------------------------------------------------------------------------------------


def list_crypto(source: MarketDataSource, limit: int = catalog.CRYPTO_TOP_N) -> list[CryptoOut]:
    return [
        CryptoOut(
            id=coin.id,
            symbol=coin.symbol,
            name=coin.name,
            image=coin.image,
            market_cap_rank=coin.market_cap_rank,
            current_price=coin.price,
            price_change_percentage_1h_in_currency=coin.change_1h_pct,
            price_change_percentage_24h_in_currency=coin.change_24h_pct,
            price_change_percentage_7d_in_currency=coin.change_7d_pct,
            total_volume=coin.total_volume,
            market_cap=coin.market_cap,
            sparkline_in_7d=Sparkline(price=coin.sparkline_7d),
            source=source.name,
            updated_at=coin.updated_at,
        )
        for coin in source.top_coins(limit)
    ]


# --------------------------------------------------------------------------------------
# Makro: kursy i surowce (potok strumieniowy) + wskaźniki (serwis AI Patryka, FRED)
# --------------------------------------------------------------------------------------

_MARKET_MACRO_DESCRIPTIONS = {
    "EUR/PLN": "Kurs euro względem polskiego złotego.",
    "USD/PLN": "Kurs dolara amerykańskiego względem polskiego złotego.",
    "CHF/PLN": "Kurs franka szwajcarskiego względem polskiego złotego.",
    "GBP/PLN": "Kurs funta brytyjskiego względem polskiego złotego.",
    "EUR/USD": "Kurs euro względem dolara amerykańskiego.",
    "OIL": "Cena ropy Brent (kontrakt terminowy z najbliższym terminem).",
    "GOLD": "Cena złota (kontrakt terminowy z najbliższym terminem).",
    "GAS": "Cena gazu ziemnego Henry Hub (kontrakt terminowy z najbliższym terminem).",
}

# (symbol frontendu, nazwa, kategoria, klucz w odpowiedzi /stock/macro/raw serwisu AI, jednostka, opis)
# Serie FRED zdefiniowane w backend-ai/app/data_sources/fred.py (stan 11.11.2026).
MACRO_INDICATORS: list[tuple[str, str, str, str, str, str]] = [
    ("CPI PL", "Inflacja CPI Polska", "Inflacja", "CPI_PL", "% r/r",
     "Inflacja konsumencka w Polsce, zmiana cen r/r (FRED: POLCPIALLMINMEI)."),
    ("CPI USA", "Inflacja CPI USA", "Inflacja", "CPI_Inflation", "% r/r",
     "Inflacja konsumencka w USA, zmiana cen r/r (FRED: CPIAUCSL)."),
    ("CPI EU", "Inflacja HICP strefa euro", "Inflacja", "CPI_EU", "% r/r",
     "Zharmonizowana inflacja konsumencka w strefie euro, r/r (FRED: CP0000EZ19M086NEST)."),
    ("NBP RATE", "Stopa procentowa Polska", "Stopy procentowe", "RATES_PL", "%",
     "Krótkoterminowa stopa procentowa rynku międzybankowego w Polsce (FRED: IRSTCI01PLM156N)."),
    ("FED RATE", "Stopa procentowa FED", "Stopy procentowe", "Fed_Interest_Rate", "%",
     "Efektywna stopa funduszy federalnych w USA (FRED: FEDFUNDS)."),
    ("ECB RATE", "Stopa depozytowa EBC", "Stopy procentowe", "RATES_EU", "%",
     "Stopa depozytowa Europejskiego Banku Centralnego (FRED: ECBDFR)."),
    ("GDP PL", "PKB Polska", "PKB", "GDP_PL", "% r/r",
     "Dynamika realnego PKB Polski, r/r (FRED: CLVMNACSCAB1GQPL)."),
    ("GDP USA", "PKB USA", "PKB", "GDP", "% r/r",
     "Dynamika PKB USA, r/r (FRED: GDP)."),
    ("GDP EU", "PKB strefa euro", "PKB", "GDP_EU", "% r/r",
     "Dynamika realnego PKB strefy euro, r/r (FRED: CLVMEURSCAB1GQEA19)."),
]

# Kolejność kategorii jak w Macro.jsx.
_CATEGORY_ORDER = ["Waluty", "Inflacja", "Stopy procentowe", "PKB", "Surowce"]


def _market_macro_items(source: MarketDataSource) -> list[MacroOut]:
    items = []
    for instrument in catalog.FX + catalog.COMMODITIES:
        snap = source.snapshot(instrument)
        items.append(
            MacroOut(
                symbol=instrument.symbol,
                name=instrument.name,
                category="Waluty" if instrument.asset_class == "fx" else "Surowce",
                value=snap.price,
                change=snap.change_24h_pct,
                unit=instrument.currency,
                unit_description=instrument.unit or f"{instrument.currency} za 1 {instrument.symbol.split('/')[0]}",
                description=_MARKET_MACRO_DESCRIPTIONS[instrument.symbol],
                history=[ValuePoint(time=t, value=v) for t, v in snap.history],
                source=source.name,
                updated_at=snap.updated_at,
            )
        )
    return items


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None  # np. "N/A" z serwisu AI


def _date_to_utc(value: str) -> datetime | None:
    try:
        return datetime.combine(date.fromisoformat(value), datetime.min.time(), tzinfo=UTC)
    except (TypeError, ValueError):
        return None


def _fetch_macro_raw() -> dict[str, Any] | None:
    try:
        result = ai_gateway.get(
            "/stock/macro/raw", ttl_seconds=MACRO_RAW_TTL_SECONDS, timeout=MACRO_RAW_TIMEOUT_SECONDS
        )
    except ai_gateway.AIServiceUnavailableError:
        logger.warning("Wskaźniki makro niedostępne — serwis AI nie odpowiada.")
        return None
    if result.status_code != 200 or not isinstance(result.body, dict):
        return None
    return result.body


def _indicator_items(raw: dict[str, Any] | None) -> list[MacroOut]:
    items = []
    for symbol, name, category, key, unit_description, description in MACRO_INDICATORS:
        entry = (raw or {}).get(key) or {}
        history = []
        for point in entry.get("history") or []:
            time, value = _date_to_utc(point.get("date")), _to_float(point.get("value"))
            if time is not None and value is not None:
                history.append(ValuePoint(time=time, value=value))
        history.sort(key=lambda p: p.time)
        value = _to_float(entry.get("value"))
        change = round(history[-1].value - history[-2].value, 2) if len(history) >= 2 else None
        items.append(
            MacroOut(
                symbol=symbol,
                name=name,
                category=category,
                value=value,
                change=change,
                unit="%",
                unit_description=unit_description,
                description=description,
                history=history,
                source="fred" if value is not None else "unavailable",
                updated_at=_date_to_utc(entry.get("date")),
            )
        )
    return items


def list_macro(source: MarketDataSource) -> list[MacroOut]:
    items = _market_macro_items(source) + _indicator_items(_fetch_macro_raw())
    return sorted(items, key=lambda item: _CATEGORY_ORDER.index(item.category))


# --------------------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------------------


def _format_pl(value: float, decimals: int) -> str:
    """Format polski jak w mock/markets.json: spacja jako separator tysięcy, przecinek dziesiętny."""
    return f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")


def _format_change(change: float | None) -> str:
    return "—" if change is None else f"{change:+.2f}%"


def dashboard_cards(source: MarketDataSource) -> list[DashboardCardOut]:
    usd_pln = source.snapshot(catalog.BY_SYMBOL["USD/PLN"]).price
    bitcoin = next((coin for coin in source.top_coins(catalog.CRYPTO_TOP_N) if coin.id == "bitcoin"), None)
    btc_pln = bitcoin.price * usd_pln if bitcoin and bitcoin.price is not None and usd_pln is not None else None
    wig20 = source.snapshot(catalog.BY_SYMBOL["WIG20"])
    eur_pln = source.snapshot(catalog.BY_SYMBOL["EUR/PLN"])

    cards = [
        (1, "Bitcoin", btc_pln, 0, " PLN", bitcoin.change_24h_pct if bitcoin else None, "/kryptowaluty"),
        (2, "WIG20", wig20.price, 2, "", wig20.change_24h_pct, "/gielda"),
        (3, "EUR/PLN", eur_pln.price, 4, "", eur_pln.change_24h_pct, "/makro"),
    ]
    return [
        DashboardCardOut(
            id=card_id,
            name=name,
            value="—" if value is None else _format_pl(value, decimals) + suffix,
            change=_format_change(change),
            path=path,
            value_number=value,
            change_percent=change,
            source=source.name,
        )
        for card_id, name, value, decimals, suffix, change, path in cards
    ]
