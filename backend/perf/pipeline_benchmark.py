"""Pomiar przepustowości i opóźnienia potoku strumieniowego.

Dwa pomiary:
1. `lakehouse` — sam zapis paczek (Bronze → Silver → Gold) na tymczasowym Lakehouse, bez Kafki:
   ile świec na sekundę przetwarza konsument przy różnych rozmiarach paczek.
2. `kafka` — pełna ścieżka producent → Kafka → konsument → Delta na jednorazowym temacie:
   przepustowość (wiadomości/s) i opóźnienie od wysłania do zapisu w Lakehouse.

Dane syntetyczne (świece minutowe dla instrumentów z katalogu), żeby wynik nie zależał od Yahoo.

Uruchomienie (z katalogu backend/; dla pomiaru `kafka` Kafka musi działać):
    python -m perf.pipeline_benchmark lakehouse
    python -m perf.pipeline_benchmark kafka --messages 2000
"""

import argparse
import statistics
import tempfile
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from confluent_kafka.admin import AdminClient

from app.core.config import get_settings
from app.market import catalog
from app.stream import consumer as consumer_module, lakehouse as lh, topics
from app.stream.messages import Envelope
from app.stream.producer import make_kafka_producer
from app.stream.transform import RawMessage

START = datetime(2026, 11, 16, 14, 30, tzinfo=UTC)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def make_envelope(symbol: str, start: datetime, bars: int, fetched_at: datetime | None = None) -> Envelope:
    instrument = catalog.BY_SYMBOL[symbol]
    rows = [
        {"ts": _iso(start + timedelta(minutes=i)), "open": 100.0 + i, "high": 101.0 + i, "low": 99.0 + i,
         "close": 100.5 + i, "volume": 1000.0}
        for i in range(bars)
    ]
    return Envelope("bars", "yahoo", symbol, instrument.source_symbol, _iso(fetched_at or datetime.now(UTC)),
                    {"interval": "1m", "bars": rows})


def _num(value: float) -> str:
    """Liczba z separatorem tysięcy (spacja), np. 12 144."""
    return f"{value:,.0f}".replace(",", " ")


def bench_lakehouse(rounds: int) -> None:
    symbols = [i.symbol for i in catalog.STREAMED]
    print(f"Zapis paczek do Lakehouse (bez Kafki), {len(symbols)} instrumentów, {rounds} kolejnych paczek:")
    print("| świec na instrument | świec w paczce | czas paczki (mediana) | świec/s |")
    print("| --- | --- | --- | --- |")
    for bars in (15, 60, 240):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            times = []
            for r in range(rounds):
                start = START + timedelta(minutes=r * bars)
                messages = [
                    RawMessage("bench", 0, r * len(symbols) + i, s.encode(), make_envelope(s, start, bars).to_bytes())
                    for i, s in enumerate(symbols)
                ]
                t0 = time.perf_counter()
                consumer_module.process_batch(root, messages)
                times.append(time.perf_counter() - t0)
            median = statistics.median(times[1:] or times)  # pierwsza paczka tworzy tabele — pomijamy
            total = bars * len(symbols)
            print(f"| {bars} | {total} | {median:.2f} s | {_num(total / median)} |")


def bench_kafka(message_count: int, bars_per_message: int) -> None:
    settings = get_settings()
    bootstrap = settings.kafka_bootstrap_servers
    topic = f"bench.bars.{uuid.uuid4().hex[:8]}"
    topics.ensure_topics(bootstrap, {topic: 3})
    symbols = [i.symbol for i in catalog.STREAMED]
    producer = make_kafka_producer(bootstrap)

    t_produce = time.perf_counter()
    for n in range(message_count):
        symbol = symbols[n % len(symbols)]
        start = START + timedelta(minutes=(n // len(symbols)) * bars_per_message)
        envelope = make_envelope(symbol, start, bars_per_message)
        producer.produce(topic, key=envelope.key, value=envelope.to_bytes())
        producer.poll(0)
    producer.flush(60)
    produce_seconds = time.perf_counter() - t_produce

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        kafka_consumer = consumer_module.make_kafka_consumer(bootstrap, f"bench-{uuid.uuid4().hex[:8]}")
        state = {"idle": 0, "processed": 0}
        t_consume = time.perf_counter()

        def stop() -> bool:
            rows = lh.read(root, lh.BRONZE_RAW, columns=["count(*) AS n"])
            state["processed"] = rows[0]["n"] if rows else 0
            if state["processed"] >= message_count:
                return True
            state["idle"] += 1
            return state["idle"] > 200

        consumer_module.run(kafka_consumer, root, stop, [topic], batch_timeout=1.0)
        consume_seconds = time.perf_counter() - t_consume
        latencies = [
            (r["ingested_at"] - r["fetched_at"]).total_seconds()
            for r in lh.read(root, lh.BRONZE_RAW, columns=["fetched_at", "ingested_at"])
        ]
    AdminClient({"bootstrap.servers": bootstrap}).delete_topics([topic])

    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95) - 1] if latencies else float("nan")
    print(f"Kafka: {message_count} wiadomości × {bars_per_message} świec, temat 3 partycje")
    print("| Etap | Wynik |\n| --- | --- |")
    print(f"| Wysłanie przez producenta (acks=all, zstd) | {produce_seconds:.2f} s, {_num(message_count / produce_seconds)} wiad./s |")
    print(f"| Odczyt + zapis do Lakehouse (z dołączeniem do grupy) | {consume_seconds:.2f} s, {_num(state['processed'] / consume_seconds)} wiad./s |")
    print(f"| Opóźnienie wysłanie → zapis: mediana / p95 / max | {statistics.median(latencies):.2f} s / {p95:.2f} s / {latencies[-1]:.2f} s |")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pomiar wydajności potoku strumieniowego")
    parser.add_argument("mode", choices=["lakehouse", "kafka"])
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--messages", type=int, default=2000)
    parser.add_argument("--bars", type=int, default=15, help="świec w wiadomości (jak okno producenta: 15)")
    args = parser.parse_args()
    if args.mode == "lakehouse":
        bench_lakehouse(args.rounds)
    else:
        bench_kafka(args.messages, args.bars)


if __name__ == "__main__":
    main()
