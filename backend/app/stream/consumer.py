"""Konsument: Kafka → Delta Lake (Bronze → Silver → Gold).

Uruchomienie (z katalogu backend/, Kafka musi działać):
    python -m app.stream.consumer

Przetwarzanie paczkami (micro-batch): do 500 wiadomości albo 5 s oczekiwania, potem:
  1. Bronze  — surowe wiadomości (z tematem, partycją i offsetem) dopisywane bez zmian,
  2. Silver  — oczyszczone świece, dane referencyjne i notowania krypto zapisywane MERGE po kluczu,
  3. Gold    — przeliczenie świec godzinowych i ostatnich cen dla dotkniętych symboli,
  4. dopiero po udanym zapisie zatwierdzenie offsetów w Kafce.

Semantyka „co najmniej raz” (at-least-once) + idempotentny MERGE w Silver i Gold = efekt
„dokładnie raz” (effectively-once): po awarii między zapisem a zatwierdzeniem paczka zostanie
przetworzona ponownie, ale nie powstaną duplikaty. W Bronze ponowienie może dopisać kopię
surowej wiadomości — Bronze jest dziennikiem (kopie da się rozpoznać po temacie, partycji i offsecie).
"""

import logging
import signal
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

from confluent_kafka import Consumer, KafkaError, Message

from app.core.config import get_settings
from app.core.logging_setup import configure_logging
from app.stream import gold, lakehouse as lh, topics
from app.stream.transform import RawMessage, TransformedBatch, transform

logger = logging.getLogger(__name__)

BATCH_SIZE = 500
BATCH_TIMEOUT_SECONDS = 5.0
MAINTENANCE_INTERVAL_SECONDS = 3600


@dataclass
class BatchResult:
    messages: int
    bars: int
    rejected_bars: int
    invalid: int
    hours_updated: int
    latest_updated: int
    crypto: int
    seconds: float
    latency_median: float | None


def process_batch(root: Path, messages: list[RawMessage]) -> BatchResult:
    """Cała logika zapisu jednej paczki — niezależna od Kafki (testowalna bez brokera)."""
    started = time.perf_counter()
    batch: TransformedBatch = transform(messages)
    now = gold.utc_now()

    lh.append(root, lh.BRONZE_RAW, lh.to_table(lh.BRONZE_RAW, batch.bronze))
    lh.upsert(root, lh.SILVER_BARS, lh.to_table(lh.SILVER_BARS, batch.bars))
    lh.upsert(root, lh.SILVER_INSTRUMENT_INFO, lh.to_table(lh.SILVER_INSTRUMENT_INFO, batch.instrument_info))
    lh.upsert(root, lh.SILVER_CRYPTO, lh.to_table(lh.SILVER_CRYPTO, batch.crypto))

    touched = gold.touched_hours(batch.bars)
    hour_bars = gold.update_ohlc(root, touched, now)
    # Nowa liczba akcji zmienia kapitalizację — przeliczamy też ceny spółek z danymi referencyjnymi.
    info_symbols = {row["symbol"] for row in batch.instrument_info}
    latest = gold.update_latest_prices(root, set(touched) | info_symbols, now)
    crypto = gold.update_crypto_top(root, batch.crypto)
    if batch.instrument_info:
        gold.update_dim_instrument(root, now)

    return BatchResult(
        messages=len(messages),
        bars=len(batch.bars),
        rejected_bars=batch.rejected_bars,
        invalid=batch.invalid_messages,
        hours_updated=len(hour_bars),
        latest_updated=latest,
        crypto=crypto,
        seconds=time.perf_counter() - started,
        latency_median=statistics.median(batch.latencies) if batch.latencies else None,
    )


def maintain(root: Path) -> None:
    """Kompaktowanie małych plików (każda paczka tworzy nowe) i usuwanie nieużywanych plików starszych niż 7 dni."""
    for spec in (lh.BRONZE_RAW, lh.SILVER_BARS, lh.SILVER_CRYPTO, lh.GOLD_OHLC_1H, lh.GOLD_LATEST_PRICES):
        table = lh.open_table(root, spec)
        if table is None:
            continue
        try:
            table.optimize.compact()
            table.vacuum(retention_hours=168, dry_run=False, enforce_retention_duration=True)
        except Exception:
            logger.exception("Konserwacja tabeli %s nie powiodła się", spec.name)


def make_kafka_consumer(bootstrap_servers: str, group_id: str) -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "client.id": "geomarket-consumer",
            # Nowa grupa zaczyna od najstarszych wiadomości w temacie (nic nie pomija).
            "auto.offset.reset": "earliest",
            # Offsety zatwierdzamy ręcznie, dopiero po zapisie do Lakehouse.
            "enable.auto.commit": False,
        }
    )


def to_raw(message: Message) -> RawMessage:
    return RawMessage(message.topic(), message.partition(), message.offset(), message.key(), message.value() or b"")


def run(consumer: Consumer, root: Path, stop, topic_names: list[str] | None = None,
        batch_timeout: float = BATCH_TIMEOUT_SECONDS) -> None:
    consumer.subscribe(topic_names or list(topics.TOPICS))
    next_maintenance = time.monotonic() + MAINTENANCE_INTERVAL_SECONDS
    while not stop():
        polled = consumer.consume(num_messages=BATCH_SIZE, timeout=batch_timeout)
        messages = []
        for message in polled:
            if message.error():
                if message.error().code() != KafkaError._PARTITION_EOF:
                    logger.error("Błąd Kafki: %s", message.error())
                continue
            messages.append(to_raw(message))
        if messages:
            result = process_batch(root, messages)
            # Zatwierdzenie offsetów DOPIERO po zapisie — awaria wcześniej = ponowne przetworzenie paczki.
            consumer.commit(asynchronous=False)
            logger.info(
                "Paczka: %d wiad., %d świec (%d odrzuconych), %d niepoprawnych, %d godzin Gold, %d cen, %d krypto, "
                "%.2f s, opóźnienie (mediana) %s s",
                result.messages, result.bars, result.rejected_bars, result.invalid, result.hours_updated,
                result.latest_updated, result.crypto, result.seconds,
                f"{result.latency_median:.1f}" if result.latency_median is not None else "-",
            )
        if time.monotonic() >= next_maintenance:
            maintain(root)
            next_maintenance = time.monotonic() + MAINTENANCE_INTERVAL_SECONDS
    consumer.close()


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    root = Path(settings.lakehouse_root)
    root.mkdir(parents=True, exist_ok=True)
    topics.ensure_topics(settings.kafka_bootstrap_servers)
    gold.update_dim_instrument(root, gold.utc_now())
    # Kompaktowanie także przy starcie: przy częstych restartach konsumenta (praca lokalna)
    # cykl godzinowy mógłby nigdy nie nadejść, a małe pliki spowalniają odczyty.
    maintain(root)

    stopping = False

    def request_stop(*_: object) -> None:
        nonlocal stopping
        stopping = True
        logger.info("Zatrzymywanie konsumenta (dokończenie bieżącej paczki)…")

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    logger.info("Konsument uruchomiony: Kafka %s, Lakehouse %s", settings.kafka_bootstrap_servers, root)
    run(make_kafka_consumer(settings.kafka_bootstrap_servers, settings.kafka_consumer_group), root, lambda: stopping)


if __name__ == "__main__":
    main()
