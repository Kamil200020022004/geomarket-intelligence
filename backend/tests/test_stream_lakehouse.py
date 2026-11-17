"""Testy transformacji i warstw Bronze/Silver/Gold na tymczasowym Lakehouse (bez Kafki)."""

from datetime import UTC, datetime, timedelta

import pytest

from app.market import catalog
from app.market.sources import LakehouseMarketData
from app.stream import gold, lakehouse as lh
from app.stream.consumer import process_batch
from app.stream.messages import Envelope
from app.stream.transform import RawMessage, transform

T0 = datetime(2026, 11, 17, 14, 0, tzinfo=UTC)


def iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def bar(ts: datetime, close: float, *, open_=None, high=None, low=None, volume=10.0) -> dict:
    return {"ts": iso(ts), "open": open_ or close, "high": high or close, "low": low or close, "close": close,
            "volume": volume}


def bars_message(offset: int, bars: list[dict], interval: str = "1m", symbol: str = "AAPL",
                 fetched_at: datetime = T0 + timedelta(hours=1)) -> RawMessage:
    envelope = Envelope("bars", "yahoo", symbol, catalog.BY_SYMBOL[symbol].source_symbol, iso(fetched_at),
                        {"interval": interval, "bars": bars})
    return RawMessage("market.yahoo.bars.v1", 0, offset, envelope.key, envelope.to_bytes())


# --- Transform ---


def test_transform_cleans_and_rejects_bad_bars():
    batch = transform([bars_message(0, [
        bar(T0, 92.6500015258789),  # artefakt float32 z Yahoo
        bar(T0 + timedelta(minutes=1), 0.0),  # cena ≤ 0
        {"ts": iso(T0 + timedelta(minutes=2)), "open": 1, "high": 1, "low": 5, "close": 2, "volume": 1},  # high < low
        {"ts": "zła data", "close": 1},
        bar(T0 + timedelta(minutes=3), 50.0, volume=-5),  # ujemny wolumen → null
    ])])
    assert batch.rejected_bars == 3
    assert [b["close"] for b in batch.bars] == [92.65, 50.0]
    assert batch.bars[1]["volume"] is None
    assert batch.bars[0]["ts"].tzinfo is not None and batch.bars[0]["date"] == T0.date()


def test_invalid_message_lands_in_bronze_with_error():
    batch = transform([RawMessage("t", 0, 7, b"x", b"{zepsuty json")])
    assert batch.invalid_messages == 1
    assert batch.bars == []
    assert batch.bronze[0]["parse_error"] and batch.bronze[0]["kafka_offset"] == 7


def test_bars_of_unknown_symbol_are_ignored():
    envelope = Envelope("bars", "yahoo", "NIEZNANY", "X", iso(T0), {"interval": "1m", "bars": [bar(T0, 1.0)]})
    batch = transform([RawMessage("t", 0, 0, envelope.key, envelope.to_bytes())])
    assert batch.bars == [] and batch.invalid_messages == 1


# --- Silver: idempotencja ---


def test_reprocessing_same_messages_creates_no_duplicates(tmp_path):
    messages = [bars_message(0, [bar(T0, 100.0), bar(T0 + timedelta(minutes=1), 101.0)])]
    process_batch(tmp_path, messages)
    process_batch(tmp_path, messages)  # np. po awarii przed zatwierdzeniem offsetu
    assert len(lh.read(tmp_path, lh.SILVER_BARS)) == 2
    assert len(lh.read(tmp_path, lh.BRONZE_RAW)) == 2  # Bronze to dziennik — kopia rozpoznawalna po offsecie


def test_open_bar_is_updated_not_duplicated(tmp_path):
    process_batch(tmp_path, [bars_message(0, [bar(T0, 100.0)])])
    process_batch(tmp_path, [bars_message(1, [bar(T0, 100.7)])])  # ta sama, jeszcze niezamknięta świeca
    rows = lh.read(tmp_path, lh.SILVER_BARS)
    assert [r["close"] for r in rows] == [100.7]


def test_duplicate_keys_within_one_batch_keep_last(tmp_path):
    process_batch(tmp_path, [bars_message(0, [bar(T0, 1.0)]), bars_message(1, [bar(T0, 2.0)])])
    assert [r["close"] for r in lh.read(tmp_path, lh.SILVER_BARS)] == [2.0]


# --- Gold: świece godzinowe (historia + strumień) ---


def test_hour_bar_from_minutes_only():
    minutes = [{"ts": T0 + timedelta(minutes=m), "open": o, "high": h, "low": low, "close": c, "volume": 10.0}
               for m, o, h, low, c in [(0, 10, 12, 9, 11), (1, 11, 15, 10, 14), (2, 14, 14, 8, 13)]]
    result = gold.build_hour_bar("AAPL", T0, None, minutes)
    assert (result.open, result.high, result.low, result.close, result.volume) == (10, 15, 8, 13, 30.0)
    assert result.last_ts == T0 + timedelta(minutes=2)


def test_hour_bar_merges_history_and_stream_without_double_counting():
    history = {"open": 9.0, "high": 13.0, "low": 9.5, "close": 12.0, "volume": 100.0, "fetched_at": T0}
    minutes = [{"ts": T0 + timedelta(minutes=40), "open": 12, "high": 16, "low": 11, "close": 15, "volume": 30.0}]
    result = gold.build_hour_bar("AAPL", T0, history, minutes)
    assert result.open == 9.0  # początek godziny z historii
    assert result.high == 16 and result.low == 9.5
    assert result.close == 15  # najświeższa cena ze strumienia
    assert result.volume == 100.0  # nie 130 — obie liczą tę samą godzinę


def test_history_then_stream_gives_continuous_hourly_series(tmp_path):
    history = [bar(T0 + timedelta(hours=h), 100.0 + h) for h in range(5)]  # 14:00–18:00 z backfillu
    process_batch(tmp_path, [bars_message(0, history, interval="1h")])
    live = [bar(T0 + timedelta(hours=4, minutes=30 + m), 110.0 + m) for m in range(3)]  # 18:30–18:32: 110, 111, 112
    live += [bar(T0 + timedelta(hours=5, minutes=m), 120.0 + m) for m in range(0, 2)]  # 19:00–19:01
    process_batch(tmp_path, [bars_message(1, live)])
    rows = sorted(lh.read(tmp_path, lh.GOLD_OHLC_1H), key=lambda r: r["ts"])
    assert [r["ts"] for r in rows] == [T0 + timedelta(hours=h) for h in range(6)]  # bez luk i bez duplikatów
    assert rows[4]["open"] == 104.0 and rows[4]["close"] == 112.0  # 18:00: historia + strumień
    assert rows[5]["close"] == 121.0


def test_latest_price_changes_and_market_cap():
    rows = [{"ts": T0 + timedelta(hours=h), "close": c, "volume": 10.0, "last_ts": T0 + timedelta(hours=h, minutes=59)}
            for h, c in [(-24 * 7 - 1, 50.0), (-25, 80.0), (-1, 99.0), (0, 100.0)]]
    latest = gold.compute_latest("AAPL", rows, shares=1_000.0, now=T0)
    assert latest["price"] == 100.0
    assert latest["change_1h_pct"] == pytest.approx(1.0101, abs=1e-3)  # 99 → 100
    assert latest["change_24h_pct"] == pytest.approx(25.0)  # 80 → 100
    assert latest["change_7d_pct"] == pytest.approx(100.0)  # 50 → 100
    assert latest["market_cap"] == 100_000.0
    assert latest["volume_24h"] == 20.0  # świece z ostatnich 24 h


def test_latest_for_fx_has_no_volume_or_market_cap():
    rows = [{"ts": T0, "close": 4.4, "volume": 0.0, "last_ts": T0}]
    latest = gold.compute_latest("EUR/PLN", rows, shares=None, now=T0)
    assert latest["volume_24h"] is None and latest["market_cap"] is None
    assert latest["change_24h_pct"] is None  # brak danych sprzed 24 h → null, nie 0


# --- Krypto ---


def _coins_message(offset: int, prices: list[float]) -> RawMessage:
    coins = [{"id": f"coin{i}", "symbol": f"c{i}", "name": f"Coin {i}", "image": None, "market_cap_rank": i + 1,
              "current_price": p, "market_cap": 1e9, "total_volume": 1e6, "last_updated": iso(T0),
              "price_change_percentage_1h_in_currency": 0.1, "price_change_percentage_24h_in_currency": -1.0,
              "price_change_percentage_7d_in_currency": 5.0, "sparkline_in_7d": {"price": [1.0, 2.0, None]}}
             for i, p in enumerate(prices)]
    envelope = Envelope("coins_markets", "coingecko", "top100", "coins/markets", iso(T0), {"coins": coins})
    return RawMessage("market.coingecko.markets.v1", 0, offset, envelope.key, envelope.to_bytes())


def test_crypto_snapshot_goes_to_gold(tmp_path):
    process_batch(tmp_path, [_coins_message(0, [100.0, 2.0])])
    top = sorted(lh.read(tmp_path, lh.GOLD_CRYPTO_TOP), key=lambda r: r["market_cap_rank"])
    assert [c["id"] for c in top] == ["coin0", "coin1"]
    assert list(top[0]["sparkline_7d"]) == [1.0, 2.0]  # null w serii odrzucony


# --- API na danych z Lakehouse ---


def test_lakehouse_source_maps_gold_to_snapshots(tmp_path):
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    history = [bar(now - timedelta(hours=h), 100.0 + h) for h in range(30, -1, -1)]
    process_batch(tmp_path, [bars_message(0, history, interval="1h", fetched_at=now), _coins_message(1, [5.0])])
    source = LakehouseMarketData(tmp_path, history_days=30, cache_seconds=60)
    snap = source.snapshot(catalog.BY_SYMBOL["AAPL"])
    assert snap.price == 100.0
    # Cena sprzed 24 h = zamknięcie świecy zakończonej 24 h temu (start 25 h temu, cena 125) → 125 → 100.
    assert snap.change_24h_pct == pytest.approx(-20.0)
    assert [t for t, _ in snap.history] == sorted(t for t, _ in snap.history)
    assert len(snap.history) == 31
    assert source.top_coins(10)[0].id == "coin0"


def test_lakehouse_source_without_data_returns_nulls(tmp_path):
    source = LakehouseMarketData(tmp_path, history_days=30, cache_seconds=60)
    snap = source.snapshot(catalog.BY_SYMBOL["PKN"])
    assert snap.price is None and snap.history == []
    assert source.top_coins(10) == []


def test_stocks_endpoint_reads_lakehouse(client, tmp_path):
    from app.market.sources import get_market_source

    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    process_batch(tmp_path, [bars_message(0, [bar(now, 100.0)], interval="1h", fetched_at=now)])
    client.app.dependency_overrides[get_market_source] = lambda: LakehouseMarketData(tmp_path, 30, 0)
    stocks = {s["symbol"]: s for s in client.get("/api/stocks").json()}
    assert stocks["AAPL"]["price"] == 100.0 and stocks["AAPL"]["source"] == "lakehouse"
    assert stocks["CCC"]["price"] is None and stocks["CCC"]["history"] == []  # niedostępny w Yahoo


def test_filtered_read_works_after_merge_rewrote_file(tmp_path):
    """Regresja (D-034): MERGE aktualizujący istniejący wiersz przepisuje plik z kolumnami `string_view`.

    Filtry PyArrow Dataset nie porównują wtedy `string` ze `string_view` (ArrowNotImplementedError),
    przez co konsument padał na drugiej paczce. Odczyt przez `lakehouse.read()` (SQL) musi działać.
    """
    def row(symbol: str, close: float) -> dict:
        return {"symbol": symbol, "ts": T0, "open": close, "high": close, "low": close, "close": close,
                "volume": 1.0, "last_ts": T0, "ingested_at": T0}

    lh.upsert(tmp_path, lh.GOLD_OHLC_1H, lh.to_table(lh.GOLD_OHLC_1H, [row("AAPL", 1.0), row("PKN", 1.0)]))
    lh.upsert(tmp_path, lh.GOLD_OHLC_1H, lh.to_table(lh.GOLD_OHLC_1H, [row("AAPL", 2.0)]))  # aktualizacja wiersza
    result = lh.read(tmp_path, lh.GOLD_OHLC_1H, f"symbol IN ('AAPL') AND ts >= {lh.sql_ts(T0)}", ["symbol", "close"])
    assert result == [{"symbol": "AAPL", "close": 2.0}]
    assert gold.update_latest_prices(tmp_path, {"AAPL", "PKN"}, T0) == 2  # ścieżka, na której padał konsument
