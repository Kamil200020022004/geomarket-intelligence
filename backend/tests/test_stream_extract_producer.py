"""Testy pobierania danych (Extract) i producenta — źródła i Kafka zastąpione atrapami."""

import json
import math

import httpx
import numpy as np
import pandas as pd
import pytest

from app.core.config import get_settings
from app.market import catalog
from app.stream import extract, topics
from app.stream.messages import Envelope, InvalidMessageError
from app.stream.producer import MarketProducer


def _frame(index_tz: str | None = "America/New_York") -> pd.DataFrame:
    index = pd.DatetimeIndex(["2026-11-17 09:30", "2026-11-17 09:31", "2026-11-17 09:32"], tz=index_tz)
    return pd.DataFrame(
        {"Open": [100.0, np.nan, 101.0], "High": [101.0, np.nan, 102.0], "Low": [99.5, np.nan, 100.5],
         "Close": [100.5, np.nan, 101.5], "Volume": [1000.0, np.nan, np.nan]},
        index=index,
    )


# --- Extract ---


def test_frame_to_bars_converts_to_utc_and_drops_empty_rows():
    bars = extract.frame_to_bars(_frame())
    assert [b["ts"] for b in bars] == ["2026-11-17T14:30:00Z", "2026-11-17T14:32:00Z"]  # 09:30 EST = 14:30 UTC
    assert bars[1]["volume"] is None  # NaN → null
    assert all(not isinstance(v, float) or not math.isnan(v) for b in bars for v in b.values())


def test_frame_without_timezone_is_rejected():
    with pytest.raises(ValueError):
        extract.frame_to_bars(_frame(index_tz=None))


def test_split_download_handles_multiindex_and_missing_symbols():
    frame = pd.concat({"AAPL": _frame(), "PKN.WA": _frame()}, axis=1)
    result = extract.split_download(frame, ["AAPL", "PKN.WA", "CCC.WA"])
    assert set(result) == {"AAPL", "PKN.WA"}  # brak danych dla symbolu → pomijany, bez błędu
    assert len(result["AAPL"]) == 2


def test_fetch_coingecko_sends_parameters_and_demo_key():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["params"] = dict(request.url.params)
        seen["key"] = request.headers.get("x-cg-demo-api-key")
        return httpx.Response(200, json=[{"id": "bitcoin"}])

    client = httpx.Client(transport=httpx.MockTransport(handler))
    assert extract.fetch_coingecko_top(100, "demo-key", client=client) == [{"id": "bitcoin"}]
    assert seen["params"]["per_page"] == "100"
    assert seen["params"]["sparkline"] == "true"
    assert seen["params"]["price_change_percentage"] == "1h,24h,7d"
    assert seen["key"] == "demo-key"


# --- Format wiadomości ---


def test_envelope_roundtrip_and_key():
    envelope = Envelope("bars", "yahoo", "PKN", "PKN.WA", "2026-11-17T14:30:00.000Z", {"interval": "1m", "bars": []})
    assert Envelope.from_bytes(envelope.to_bytes()) == envelope
    assert envelope.key == b"PKN"


@pytest.mark.parametrize("raw", [b"nie-json", b'{"schema_version": 99}', b'{"schema_version": 1, "kind": "bars"}'])
def test_invalid_envelope_is_rejected(raw):
    with pytest.raises(InvalidMessageError):
        Envelope.from_bytes(raw)


# --- Producent ---


class FakeKafka:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bytes, dict]] = []

    def produce(self, topic, key, value, on_delivery):
        self.messages.append((topic, key, json.loads(value)))
        on_delivery(None, None)

    def poll(self, timeout):
        return 0

    def flush(self, timeout=None):
        return 0


def _producer(**fetchers) -> tuple[MarketProducer, FakeKafka]:
    kafka = FakeKafka()
    return MarketProducer(get_settings(), kafka, **fetchers), kafka


def test_live_bars_one_message_per_instrument_keyed_by_symbol():
    bars = [{"ts": "2026-11-17T14:30:00Z", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]
    producer, kafka = _producer(fetch_bars=lambda symbols, interval, **kw: {"PKN.WA": bars, "AAPL": bars, "XYZ": bars})
    assert producer.poll_live_bars() == 2  # nieznany symbol XYZ pominięty
    topic, key, value = kafka.messages[0]
    assert topic == topics.YAHOO_BARS
    assert {k for _, k, _ in kafka.messages} == {b"PKN", b"AAPL"}  # klucz = symbol frontendu
    assert value["payload"]["interval"] == "1m"
    assert producer.sent == 2


def test_unavailable_symbols_are_not_requested_from_yahoo():
    requested = {}

    def fetch(symbols, interval, **kwargs):
        requested["symbols"] = symbols
        return {}

    producer, _ = _producer(fetch_bars=fetch)
    producer.poll_live_bars()
    assert "CCC.WA" not in requested["symbols"] and "SPL.WA" not in requested["symbols"]
    assert len(requested["symbols"]) == len(catalog.STREAMED)


def test_coins_snapshot_is_one_message():
    producer, kafka = _producer(fetch_coins=lambda limit, key: [{"id": "bitcoin"}] * limit)
    producer.poll_coins()
    topic, key, value = kafka.messages[0]
    assert (topic, key, value["kind"]) == (topics.COINGECKO_MARKETS, b"top100", "coins_markets")
    assert len(value["payload"]["coins"]) == 100


def test_instrument_info_only_for_stocks():
    producer, kafka = _producer(fetch_info=lambda symbol: {"shares": 1000.0, "currency": "PLN", "exchange": "WSE"})
    count = producer.refresh_instrument_info()
    assert count == sum(1 for i in catalog.STREAMED if i.asset_class == "stock")
    assert all(value["kind"] == "instrument_info" for _, _, value in kafka.messages)


def test_failing_source_does_not_stop_producer():
    def broken(*args, **kwargs):
        raise ConnectionError("Yahoo niedostępne")

    producer, _ = _producer(fetch_bars=broken)
    producer._run_job("yahoo-1m", producer.poll_live_bars)  # nie rzuca wyjątku dalej
