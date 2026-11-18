"""Producent: odpytuje Yahoo Finance i CoinGecko i publikuje wyniki do Kafki.

Uruchomienie (z katalogu backend/, Kafka musi działać):
    python -m app.stream.producer

Harmonogram (konfigurowalny w .env):
- przy starcie: świece godzinowe z ostatnich CATCH_UP_DAYS dni (zasypanie luki po przerwie),
- co YAHOO_POLL_SECONDS (60 s): świece minutowe z ostatnich 15 minut dla wszystkich instrumentów,
- co COINGECKO_POLL_SECONDS (300 s): TOP 100 kryptowalut,
- co INSTRUMENT_INFO_REFRESH_SECONDS (24 h): liczba akcji spółek (do kapitalizacji).

Okno 15 minut przy odpytywaniu co minutę daje zakładkę: każda świeca przychodzi kilka razy
(ostatnia — jeszcze niezamknięta — z aktualizowaną ceną). Duplikaty usuwa konsument
(zapis idempotentny po kluczu symbol + interwał + czas), a zakładka chroni przed lukami,
gdy pojedyncze zapytanie się nie uda.
"""

import logging
import signal
import time
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from confluent_kafka import Producer

from app.core.config import Settings, get_settings
from app.core.logging_setup import configure_logging
from app.market import catalog
from app.stream import extract, topics
from app.stream.messages import Envelope, utc_now_iso

logger = logging.getLogger(__name__)

LIVE_WINDOW = timedelta(minutes=15)


def make_kafka_producer(bootstrap_servers: str) -> Producer:
    return Producer(
        {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "geomarket-producer",
            # Potwierdzenie od wszystkich replik + idempotencja: ponowienie po błędzie sieci nie tworzy duplikatu w temacie.
            "acks": "all",
            "enable.idempotence": True,
            "compression.type": "zstd",
            "linger.ms": 50,  # krótkie grupowanie wiadomości w paczki → większa przepustowość
        }
    )


class MarketProducer:
    def __init__(
        self,
        settings: Settings,
        kafka: Producer,
        *,
        fetch_bars: Callable[..., dict[str, list[dict[str, Any]]]] = extract.fetch_yahoo_bars,
        fetch_coins: Callable[..., list[dict[str, Any]]] = extract.fetch_coingecko_top,
        fetch_info: Callable[[str], dict[str, Any] | None] = extract.fetch_instrument_info,
        instruments: list[catalog.Instrument] | None = None,
    ) -> None:
        self.settings = settings
        self.kafka = kafka
        self.fetch_bars = fetch_bars
        self.fetch_coins = fetch_coins
        self.fetch_info = fetch_info
        self.instruments = instruments if instruments is not None else catalog.STREAMED
        self._by_source = {i.source_symbol: i for i in self.instruments}
        self.sent = 0
        self.failed = 0

    # --- wysyłka ---

    def _on_delivery(self, error, message) -> None:
        if error is not None:
            self.failed += 1
            logger.error("Nie dostarczono wiadomości do %s: %s", message.topic(), error)
        else:
            self.sent += 1

    def publish(self, topic: str, envelope: Envelope) -> None:
        while True:
            try:
                self.kafka.produce(topic, key=envelope.key, value=envelope.to_bytes(), on_delivery=self._on_delivery)
                break
            except BufferError:
                # Lokalna kolejka producenta pełna — czekamy, aż wiadomości zostaną wysłane.
                self.kafka.poll(1.0)
        self.kafka.poll(0)  # obsługa potwierdzeń (wywołuje _on_delivery)

    def flush(self, timeout: float = 30.0) -> None:
        remaining = self.kafka.flush(timeout)
        if remaining:
            logger.error("Po %.0f s nie wysłano %d wiadomości", timeout, remaining)

    # --- zadania ---

    def publish_bars(self, bars_by_symbol: dict[str, list[dict[str, Any]]], interval: str) -> int:
        fetched_at = utc_now_iso()
        count = 0
        for source_symbol, bars in bars_by_symbol.items():
            instrument = self._by_source.get(source_symbol)
            if instrument is None or not bars:
                continue
            self.publish(
                topics.YAHOO_BARS,
                Envelope(
                    kind="bars",
                    source="yahoo",
                    symbol=instrument.symbol,
                    source_symbol=source_symbol,
                    fetched_at=fetched_at,
                    payload={"interval": interval, "bars": bars},
                ),
            )
            count += 1
        return count

    def poll_live_bars(self) -> int:
        symbols = list(self._by_source)
        bars = self.fetch_bars(symbols, "1m", start=extract.utc_now() - LIVE_WINDOW)
        return self.publish_bars(bars, "1m")

    def publish_hourly_history(self, days: int) -> int:
        symbols = list(self._by_source)
        bars = self.fetch_bars(symbols, "1h", period=f"{days}d")
        return self.publish_bars(bars, "1h")

    def poll_coins(self) -> int:
        coins = self.fetch_coins(catalog.CRYPTO_TOP_N, self.settings.coingecko_api_key)
        self.publish(
            topics.COINGECKO_MARKETS,
            Envelope(
                kind="coins_markets",
                source="coingecko",
                symbol="top100",
                source_symbol="coins/markets",
                fetched_at=utc_now_iso(),
                payload={"vs_currency": "usd", "coins": coins},
            ),
        )
        return 1

    def refresh_instrument_info(self) -> int:
        count = 0
        for instrument in self.instruments:
            if instrument.asset_class != "stock":
                continue
            info = self.fetch_info(instrument.source_symbol)
            if not info:
                continue
            self.publish(
                topics.YAHOO_BARS,
                Envelope(
                    kind="instrument_info",
                    source="yahoo",
                    symbol=instrument.symbol,
                    source_symbol=instrument.source_symbol,
                    fetched_at=utc_now_iso(),
                    payload=info,
                ),
            )
            count += 1
        return count

    # --- pętla główna ---

    def run_forever(self, stop: Callable[[], bool]) -> None:
        settings = self.settings
        jobs: list[tuple[str, float, Callable[[], int]]] = [
            ("yahoo-1m", settings.yahoo_poll_seconds, self.poll_live_bars),
            ("coingecko", settings.coingecko_poll_seconds, self.poll_coins),
            ("instrument-info", settings.instrument_info_refresh_seconds, self.refresh_instrument_info),
        ]
        self._run_job("catch-up-1h", lambda: self.publish_hourly_history(settings.catch_up_days))
        next_run = {name: 0.0 for name, _, _ in jobs}
        while not stop():
            now = time.monotonic()
            for name, interval, job in jobs:
                if now >= next_run[name]:
                    next_run[name] = now + interval
                    self._run_job(name, job)
            self.kafka.poll(1.0)
        self.flush()

    def _run_job(self, name: str, job: Callable[[], int]) -> None:
        started = time.perf_counter()
        try:
            published = job()
        except Exception:
            # Błąd jednego źródła (np. chwilowa niedostępność Yahoo) nie zatrzymuje producenta.
            logger.exception("Zadanie %s nie powiodło się", name)
            return
        self.kafka.flush(10)
        logger.info(
            "%s: %d wiadomości w %.1f s (łącznie wysłano %d, błędów %d)",
            name, published, time.perf_counter() - started, self.sent, self.failed,
        )


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    topics.ensure_topics(settings.kafka_bootstrap_servers)
    producer = MarketProducer(settings, make_kafka_producer(settings.kafka_bootstrap_servers))

    stopping = False

    def request_stop(*_: object) -> None:
        nonlocal stopping
        stopping = True
        logger.info("Zatrzymywanie producenta…")

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    logger.info("Producent uruchomiony: %d instrumentów Yahoo, Kafka %s", len(producer.instruments),
                settings.kafka_bootstrap_servers)
    producer.run_forever(lambda: stopping)


if __name__ == "__main__":
    main()
