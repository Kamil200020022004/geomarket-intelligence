"""Gold: agregaty pod API, frontend i analizy AI.

1. `gold/market/ohlc_1h` — świece godzinowe. Łączy historię (świece 1h z Yahoo) ze strumieniem
   (świece 1m agregowane do godzin). Dla godziny, w której są oba źródła:
       open  = open świecy 1h (zaczyna się na początku godziny),
       high  = max, low = min z obu,
       close = close ostatniej świecy 1m (najświeższa cena),
       volume = większy z dwóch (oba liczą tę samą godzinę; suma liczyłaby obroty podwójnie).
   Dzięki temu historia i strumień tworzą jedną serię bez luk i bez nakładania.
2. `gold/market/latest_prices` — ostatnia cena, zmiany 1h/24h/7d, wolumen 24h, kapitalizacja.
   Kontrakt dla potoku wsadowego (AI Patryka): jedno źródło cen w systemie.
3. `gold/market/crypto_top` — ostatnia migawka TOP 100 kryptowalut.
4. `gold/market/dim_instrument` — wymiar instrumentów (katalog + liczba akcji).

Gold przeliczany jest przyrostowo: tylko godziny i symbole, których dotyczyła paczka wiadomości.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.market import catalog
from app.stream import lakehouse as lh
from app.stream.transform import hour_floor

LATEST_LOOKBACK = timedelta(days=8)  # wystarcza do zmiany 7-dniowej
CHANGE_WINDOWS = {"change_1h_pct": timedelta(hours=1), "change_24h_pct": timedelta(hours=24),
                  "change_7d_pct": timedelta(days=7)}


@dataclass(frozen=True)
class HourBar:
    symbol: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    last_ts: datetime


def _sum(values: list[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return sum(present) if present else None


def build_hour_bar(symbol: str, hour: datetime, bar_1h: dict | None, bars_1m: list[dict]) -> HourBar | None:
    """Świeca godzinowa z historii (1h) i/lub strumienia (1m) — reguły w opisie modułu."""
    minutes = sorted(bars_1m, key=lambda b: b["ts"])
    if not minutes and bar_1h is None:
        return None
    if not minutes:
        last_ts = min(hour + timedelta(minutes=59), bar_1h["fetched_at"]) if bar_1h.get("fetched_at") else hour
        return HourBar(symbol, hour, bar_1h["open"], bar_1h["high"], bar_1h["low"], bar_1h["close"],
                       bar_1h["volume"], max(last_ts, hour))
    agg_open, agg_close = minutes[0]["open"], minutes[-1]["close"]
    agg_high = max(b["high"] for b in minutes)
    agg_low = min(b["low"] for b in minutes)
    agg_volume = _sum([b["volume"] for b in minutes])
    if bar_1h is None:
        return HourBar(symbol, hour, agg_open, agg_high, agg_low, agg_close, agg_volume, minutes[-1]["ts"])
    volumes = [v for v in (bar_1h["volume"], agg_volume) if v is not None]
    return HourBar(
        symbol, hour,
        open=bar_1h["open"],
        high=max(bar_1h["high"], agg_high),
        low=min(bar_1h["low"], agg_low),
        close=agg_close,
        volume=max(volumes) if volumes else None,
        last_ts=minutes[-1]["ts"],
    )


def _read_silver_bars(root: Path, symbols: set[str], hours: set[datetime]) -> list[dict]:
    if not hours:
        return []
    dates = ", ".join(lh.sql_date(d) for d in sorted({h.date() for h in hours}))
    # Filtr po partycji `date` → czytane są tylko katalogi dni, których dotyczy paczka.
    return lh.read(root, lh.SILVER_BARS, f"date IN ({dates}) AND {lh.sql_in('symbol', sorted(symbols))}")


def update_ohlc(root: Path, touched: dict[str, set[datetime]], now: datetime) -> list[HourBar]:
    """Przelicza świece godzinowe dla (symbol, godzina) dotkniętych w paczce i zapisuje je MERGE."""
    if not touched:
        return []
    all_hours = set().union(*touched.values())
    rows = _read_silver_bars(root, set(touched), all_hours)
    grouped_1h: dict[tuple[str, datetime], dict] = {}
    grouped_1m: dict[tuple[str, datetime], list[dict]] = defaultdict(list)
    for row in rows:
        hour = hour_floor(row["ts"])
        if hour not in touched.get(row["symbol"], ()):
            continue
        if row["interval"] == "1h":
            grouped_1h[(row["symbol"], hour)] = row
        else:
            grouped_1m[(row["symbol"], hour)].append(row)
    bars = []
    for symbol, hours in touched.items():
        for hour in hours:
            bar = build_hour_bar(symbol, hour, grouped_1h.get((symbol, hour)), grouped_1m.get((symbol, hour), []))
            if bar is not None:
                bars.append(bar)
    lh.upsert(root, lh.GOLD_OHLC_1H, lh.to_table(lh.GOLD_OHLC_1H, [
        {**bar.__dict__, "ingested_at": now} for bar in bars
    ]))
    return bars


def _reference_price(rows: list[dict], at: datetime) -> float | None:
    """Cena zamknięcia ostatniej świecy, której ostatnie notowanie było nie później niż `at`."""
    candidates = [row for row in rows if row["last_ts"] <= at]
    return candidates[-1]["close"] if candidates else None


def _pct(price: float, reference: float | None) -> float | None:
    return round((price / reference - 1) * 100, 4) if reference else None


def compute_latest(symbol: str, rows: list[dict], shares: float | None, now: datetime) -> dict[str, Any] | None:
    rows = sorted(rows, key=lambda r: r["ts"])
    if not rows:
        return None
    instrument = catalog.BY_SYMBOL[symbol]
    last = rows[-1]
    price, ts = last["close"], last["last_ts"]
    result = {
        "symbol": symbol,
        "name": instrument.name,
        "asset_class": instrument.asset_class,
        "currency": instrument.currency,
        "price": price,
        "ts": ts,
        "ingested_at": now,
    }
    for column, window in CHANGE_WINDOWS.items():
        result[column] = _pct(price, _reference_price(rows, ts - window))
    volume = _sum([r["volume"] for r in rows if r["ts"] > ts - timedelta(hours=24)])
    is_stock = instrument.asset_class == "stock"
    result["volume_24h"] = volume if is_stock and volume else None
    result["market_cap"] = price * shares if is_stock and shares else None
    return result


def _shares_by_symbol(root: Path) -> dict[str, float]:
    rows = lh.read(root, lh.SILVER_INSTRUMENT_INFO, columns=["symbol", "shares"])
    return {r["symbol"]: r["shares"] for r in rows if r["shares"]}


def update_latest_prices(root: Path, symbols: set[str], now: datetime) -> int:
    if not symbols:
        return 0
    since = now - LATEST_LOOKBACK
    rows = lh.read(root, lh.GOLD_OHLC_1H, f"{lh.sql_in('symbol', sorted(symbols))} AND ts >= {lh.sql_ts(since)}")
    by_symbol: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_symbol[row["symbol"]].append(row)
    shares = _shares_by_symbol(root)
    latest = [r for s in symbols if (r := compute_latest(s, by_symbol.get(s, []), shares.get(s), now))]
    lh.upsert(root, lh.GOLD_LATEST_PRICES, lh.to_table(lh.GOLD_LATEST_PRICES, latest))
    return len(latest)


def update_crypto_top(root: Path, crypto_rows: list[dict]) -> int:
    """Ostatnia migawka z paczki (najpóźniejsze pobranie) → cała tabela Gold (TOP 100 to mała tabela)."""
    if not crypto_rows:
        return 0
    latest_fetch = max(r["fetched_at"] for r in crypto_rows)
    snapshot = [{k: v for k, v in r.items() if k != "date"} for r in crypto_rows if r["fetched_at"] == latest_fetch]
    snapshot.sort(key=lambda r: (r["market_cap_rank"] is None, r["market_cap_rank"] or 0))
    lh.overwrite(root, lh.GOLD_CRYPTO_TOP, lh.to_table(lh.GOLD_CRYPTO_TOP, snapshot))
    return len(snapshot)


def update_dim_instrument(root: Path, now: datetime) -> int:
    shares = _shares_by_symbol(root)
    rows = [
        {
            "symbol": i.symbol, "name": i.name, "asset_class": i.asset_class, "market": i.market,
            "currency": i.currency, "unit": i.unit, "source": i.source, "source_symbol": i.source_symbol,
            "streamed": i.source_symbol not in catalog.UNAVAILABLE_SOURCE_SYMBOLS,
            "shares": shares.get(i.symbol), "ingested_at": now,
        }
        for i in catalog.ALL_YAHOO
    ]
    lh.overwrite(root, lh.GOLD_DIM_INSTRUMENT, lh.to_table(lh.GOLD_DIM_INSTRUMENT, rows))
    return len(rows)


def touched_hours(bar_rows: list[dict]) -> dict[str, set[datetime]]:
    touched: dict[str, set[datetime]] = defaultdict(set)
    for row in bar_rows:
        touched[row["symbol"]].add(hour_floor(row["ts"]))
    return touched


def utc_now() -> datetime:
    return datetime.now(UTC)
