"""Test integracyjny z prawdziwą Kafką (kontener z docker-compose.yml).

Producent → temat → konsument → Delta Lake. Każdy test używa własnych, jednorazowych tematów
i grupy konsumentów, więc nie miesza się z działającym potokiem.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from confluent_kafka.admin import AdminClient

from app.core.config import get_settings
from app.stream import consumer as consumer_module, lakehouse as lh, topics
from app.stream.producer import MarketProducer, make_kafka_producer

pytestmark = pytest.mark.kafka

BOOTSTRAP = get_settings().kafka_bootstrap_servers
T0 = datetime(2026, 11, 17, 14, 0, tzinfo=UTC)


@pytest.fixture
def kafka_topics(monkeypatch):
    try:
        AdminClient({"bootstrap.servers": BOOTSTRAP, "socket.timeout.ms": 3000}).list_topics(timeout=5)
    except Exception:
        pytest.skip("Kafka nie działa — uruchom docker compose up -d")
    suffix = uuid.uuid4().hex[:8]
    names = {"yahoo": f"test.yahoo.{suffix}", "coins": f"test.coins.{suffix}"}
    topics.ensure_topics(BOOTSTRAP, {names["yahoo"]: 3, names["coins"]: 1})
    monkeypatch.setattr(topics, "YAHOO_BARS", names["yahoo"])
    monkeypatch.setattr(topics, "COINGECKO_MARKETS", names["coins"])
    yield names
    AdminClient({"bootstrap.servers": BOOTSTRAP}).delete_topics(list(names.values()))


def _bars(start: datetime, count: int) -> list[dict]:
    return [{"ts": (start + timedelta(minutes=i)).isoformat().replace("+00:00", "Z"), "open": 100.0 + i,
             "high": 101.0 + i, "low": 99.0 + i, "close": 100.5 + i, "volume": 10.0} for i in range(count)]


def _consume_all(root, topic_names: list[str], group: str, expected_batches: int = 1) -> None:
    kafka_consumer = consumer_module.make_kafka_consumer(BOOTSTRAP, group)
    rounds = {"n": 0}

    def stop() -> bool:
        rounds["n"] += 1
        # Pierwsze rundy zajmuje dołączenie do grupy i przydział partycji; potem odczyt tematu.
        return rounds["n"] > expected_batches + 8

    consumer_module.run(kafka_consumer, root, stop, topic_names, batch_timeout=1.0)


def test_message_flows_from_producer_through_kafka_to_silver_exactly_once(kafka_topics, tmp_path):
    bars = _bars(T0, 5)
    fetch = lambda symbols, interval, **kwargs: {"AAPL": bars, "PKN.WA": bars}  # noqa: E731
    producer = MarketProducer(get_settings(), make_kafka_producer(BOOTSTRAP), fetch_bars=fetch)

    producer.poll_live_bars()
    producer.poll_live_bars()  # ta sama paczka drugi raz (zakładka okien odpytywania)
    producer.flush()
    assert producer.sent == 4 and producer.failed == 0

    group = f"test-group-{uuid.uuid4().hex[:8]}"
    _consume_all(tmp_path, [kafka_topics["yahoo"]], group)
    silver = lh.read(tmp_path, lh.SILVER_BARS)
    assert len(silver) == 10  # 2 symbole × 5 świec, mimo że każda świeca przyszła dwa razy
    assert len(lh.read(tmp_path, lh.BRONZE_RAW)) == 4  # surowe wiadomości — wszystkie
    assert {r["symbol"] for r in lh.read(tmp_path, lh.GOLD_LATEST_PRICES)} == {"AAPL", "PKN"}

    # Odczyt całego tematu od początku przez nową grupę (np. odbudowa Lakehouse) — nadal bez duplikatów.
    _consume_all(tmp_path, [kafka_topics["yahoo"]], f"{group}-replay")
    assert len(lh.read(tmp_path, lh.SILVER_BARS)) == 10


def test_committed_offsets_prevent_reprocessing(kafka_topics, tmp_path):
    fetch = lambda symbols, interval, **kwargs: {"AAPL": _bars(T0, 2)}  # noqa: E731
    producer = MarketProducer(get_settings(), make_kafka_producer(BOOTSTRAP), fetch_bars=fetch)
    producer.poll_live_bars()
    producer.flush()

    group = f"test-group-{uuid.uuid4().hex[:8]}"
    _consume_all(tmp_path, [kafka_topics["yahoo"]], group)
    _consume_all(tmp_path, [kafka_topics["yahoo"]], group)  # ta sama grupa: offset zatwierdzony
    assert len(lh.read(tmp_path, lh.BRONZE_RAW)) == 1  # wiadomość przeczytana tylko raz
