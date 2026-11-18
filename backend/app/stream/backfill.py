"""Jednorazowe załadowanie historii notowań (inicjalizacja potoku, wzorzec Kappa).

Historia NIE idzie osobną ścieżką do Lakehouse: jest publikowana do tych samych tematów
Kafki co dane bieżące i przechodzi przez tego samego konsumenta (Bronze → Silver → Gold).
Jeden potok najpierw odtwarza przeszłość, potem przetwarza bieżące zdarzenia.

Uruchomienie (z katalogu backend/, Kafka musi działać):
    python -m app.stream.backfill            # domyślnie HISTORY_DAYS (60) dni świec godzinowych
    python -m app.stream.backfill --days 30

Ponowne uruchomienie jest bezpieczne: zapis w Silver jest idempotentny (te same świece
nadpisują się, nie dublują).
"""

import argparse
import logging

from app.core.config import get_settings
from app.core.logging_setup import configure_logging
from app.stream import topics
from app.stream.producer import MarketProducer, make_kafka_producer

logger = logging.getLogger(__name__)

# Yahoo udostępnia świece godzinowe z maksymalnie ~730 dni.
MAX_HOURLY_DAYS = 729


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Załadowanie historii notowań do Kafki")
    parser.add_argument("--days", type=int, default=settings.history_days, help="liczba dni świec godzinowych")
    args = parser.parse_args()
    days = max(1, min(args.days, MAX_HOURLY_DAYS))

    configure_logging(settings.log_level)
    topics.ensure_topics(settings.kafka_bootstrap_servers)
    producer = MarketProducer(settings, make_kafka_producer(settings.kafka_bootstrap_servers))

    logger.info("Historia: świece godzinowe z %d dni dla %d instrumentów", days, len(producer.instruments))
    bars = producer.publish_hourly_history(days)
    info = producer.refresh_instrument_info()
    coins = producer.poll_coins()
    producer.flush()
    logger.info("Opublikowano: %d serii historii, %d rekordów referencyjnych, %d migawkę krypto (błędów: %d)",
                bars, info, coins, producer.failed)


if __name__ == "__main__":
    main()
