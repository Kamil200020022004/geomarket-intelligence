"""Transform: wiadomości z Kafki → wiersze tabel Bronze i Silver.

Czyszczenie i ujednolicenie:
- czas zawsze w UTC (`timestamp[us, UTC]`), świece wyrównane do początku przedziału,
- liczby jako float, brak wartości = null (NaN/inf odrzucane już w producencie i tutaj),
- ceny z Yahoo zaokrąglone do 7 cyfr znaczących (źródło przechowuje je jako float32),
- odrzucane świece bez ceny zamknięcia, z ceną ≤ 0 albo z high < low (błędne dane źródła),
- wartości ujemne wolumenu → null.
"""

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.market import catalog
from app.stream.messages import Envelope, InvalidMessageError, parse_utc

logger = logging.getLogger(__name__)

VALID_INTERVALS = {"1m", "1h"}


@dataclass
class RawMessage:
    """Wiadomość odczytana z Kafki (niezależna od biblioteki klienta — ułatwia testy)."""

    topic: str
    partition: int
    offset: int
    key: bytes | None
    value: bytes


@dataclass
class TransformedBatch:
    bronze: list[dict[str, Any]] = field(default_factory=list)
    bars: list[dict[str, Any]] = field(default_factory=list)
    instrument_info: list[dict[str, Any]] = field(default_factory=list)
    crypto: list[dict[str, Any]] = field(default_factory=list)
    rejected_bars: int = 0
    invalid_messages: int = 0
    # Opóźnienie od pobrania ze źródła do zapisu (sekundy) — do pomiarów wydajności.
    latencies: list[float] = field(default_factory=list)


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(number) or math.isinf(number) else number


def _price(value: Any) -> float | None:
    """Cena z Yahoo: 7 cyfr znaczących.

    Yahoo przechowuje ceny jako liczby pojedynczej precyzji (float32, ok. 7 cyfr znaczących),
    więc po zamianie na float64 pojawiają się artefakty, np. 92.6500015258789 zamiast 92.65.
    Zaokrąglenie do 7 cyfr znaczących przywraca wartość z giełdy i niczego nie traci.
    """
    number = _number(value)
    return None if number is None else float(f"{number:.7g}")


def _bar_row(envelope: Envelope, interval: str, bar: dict[str, Any], ingested_at: datetime) -> dict[str, Any] | None:
    try:
        ts = parse_utc(bar["ts"])
    except (KeyError, TypeError, ValueError):
        return None
    close = _price(bar.get("close"))
    if close is None or close <= 0:
        return None
    open_, high, low = _price(bar.get("open")), _price(bar.get("high")), _price(bar.get("low"))
    open_ = open_ if open_ and open_ > 0 else close
    high = high if high and high > 0 else max(open_, close)
    low = low if low and low > 0 else min(open_, close)
    if high < low:
        return None
    volume = _number(bar.get("volume"))
    return {
        "symbol": envelope.symbol,
        "interval": interval,
        "ts": ts,
        "open": open_,
        "high": max(high, open_, close),
        "low": min(low, open_, close),
        "close": close,
        "volume": volume if volume is not None and volume >= 0 else None,
        "source": envelope.source,
        "fetched_at": parse_utc(envelope.fetched_at),
        "ingested_at": ingested_at,
        "date": ts.date(),
    }


def _coin_row(coin: dict[str, Any], fetched_at: datetime, ingested_at: datetime) -> dict[str, Any] | None:
    coin_id = coin.get("id")
    price = _number(coin.get("current_price"))
    if not coin_id or price is None:
        return None
    try:
        ts = parse_utc(coin["last_updated"]) if coin.get("last_updated") else fetched_at
    except ValueError:
        ts = fetched_at
    sparkline = (coin.get("sparkline_in_7d") or {}).get("price") or []
    rank = coin.get("market_cap_rank")
    return {
        "id": str(coin_id),
        "ts": ts,
        "symbol": str(coin.get("symbol") or ""),
        "name": str(coin.get("name") or coin_id),
        "image": coin.get("image"),
        "market_cap_rank": int(rank) if isinstance(rank, int) else None,
        "price": price,
        "market_cap": _number(coin.get("market_cap")),
        "total_volume": _number(coin.get("total_volume")),
        "change_1h_pct": _number(coin.get("price_change_percentage_1h_in_currency")),
        "change_24h_pct": _number(coin.get("price_change_percentage_24h_in_currency")),
        "change_7d_pct": _number(coin.get("price_change_percentage_7d_in_currency")),
        "sparkline_7d": [p for p in (_number(v) for v in sparkline) if p is not None],
        "fetched_at": fetched_at,
        "ingested_at": ingested_at,
        "date": ts.date(),
    }


def transform(messages: list[RawMessage], ingested_at: datetime | None = None) -> TransformedBatch:
    ingested_at = ingested_at or datetime.now(UTC)
    batch = TransformedBatch()
    for message in messages:
        bronze = {
            "topic": message.topic,
            "kafka_partition": message.partition,
            "kafka_offset": message.offset,
            "message_key": message.key.decode("utf-8", "replace") if message.key else None,
            "kind": None,
            "source": None,
            "fetched_at": None,
            "payload": message.value.decode("utf-8", "replace"),
            "parse_error": None,
            "ingested_at": ingested_at,
            "ingest_date": ingested_at.date(),
        }
        batch.bronze.append(bronze)
        try:
            envelope = Envelope.from_bytes(message.value)
            fetched_at = parse_utc(envelope.fetched_at)
        except (InvalidMessageError, ValueError) as error:
            # Wiadomość, której nie umiemy odczytać, zostaje w Bronze z opisem błędu (do analizy), nie zatrzymuje potoku.
            bronze["parse_error"] = str(error)[:500]
            batch.invalid_messages += 1
            logger.warning("Niepoprawna wiadomość %s[%s]@%s: %s", message.topic, message.partition, message.offset, error)
            continue

        bronze.update(kind=envelope.kind, source=envelope.source, fetched_at=fetched_at)
        batch.latencies.append((ingested_at - fetched_at).total_seconds())

        if envelope.kind == "bars":
            interval = envelope.payload.get("interval")
            if interval not in VALID_INTERVALS or envelope.symbol not in catalog.BY_SYMBOL:
                batch.invalid_messages += 1
                continue
            for bar in envelope.payload.get("bars") or []:
                row = _bar_row(envelope, interval, bar, ingested_at)
                if row is None:
                    batch.rejected_bars += 1
                else:
                    batch.bars.append(row)
        elif envelope.kind == "instrument_info":
            batch.instrument_info.append(
                {
                    "symbol": envelope.symbol,
                    "shares": _number(envelope.payload.get("shares")),
                    "currency": envelope.payload.get("currency"),
                    "exchange": envelope.payload.get("exchange"),
                    "fetched_at": fetched_at,
                    "ingested_at": ingested_at,
                }
            )
        elif envelope.kind == "coins_markets":
            for coin in envelope.payload.get("coins") or []:
                row = _coin_row(coin, fetched_at, ingested_at)
                if row is not None:
                    batch.crypto.append(row)
        else:
            batch.invalid_messages += 1
    return batch


def hour_floor(ts: datetime) -> datetime:
    return ts.replace(minute=0, second=0, microsecond=0)
