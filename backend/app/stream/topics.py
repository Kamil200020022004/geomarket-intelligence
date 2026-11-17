"""Tematy Kafki potoku strumieniowego.

| Temat                        | Klucz   | Partycje | Zawartość |
| ---------------------------- | ------- | -------- | --------- |
| market.yahoo.bars.v1         | symbol  | 3        | świece (1m bieżące, 1h historia) i dane referencyjne spółek |
| market.coingecko.markets.v1  | "top100"| 1        | migawka TOP 100 kryptowalut |

- Klucz = symbol → kolejność wiadomości jednego instrumentu zachowana (jedna partycja).
- 3 partycje → do 3 konsumentów w grupie może czytać równolegle (skalowanie).
- Retencja 7 dni: po awarii konsument może nadrobić tydzień zaległości.
- Sufiks `.v1` = wersja formatu; zmiana niekompatybilna → nowy temat, stary wygasa.
"""

import logging

from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

logger = logging.getLogger(__name__)

YAHOO_BARS = "market.yahoo.bars.v1"
COINGECKO_MARKETS = "market.coingecko.markets.v1"

RETENTION_MS = str(7 * 24 * 3600 * 1000)

TOPICS: dict[str, int] = {YAHOO_BARS: 3, COINGECKO_MARKETS: 1}


def ensure_topics(bootstrap_servers: str, topics: dict[str, int] | None = None) -> None:
    """Tworzy brakujące tematy (istniejące zostawia bez zmian)."""
    topics = topics or TOPICS
    admin = AdminClient({"bootstrap.servers": bootstrap_servers})
    existing = set(admin.list_topics(timeout=10).topics)
    new = [
        NewTopic(
            name,
            num_partitions=partitions,
            replication_factor=1,
            config={"retention.ms": RETENTION_MS, "cleanup.policy": "delete", "compression.type": "producer"},
        )
        for name, partitions in topics.items()
        if name not in existing
    ]
    if not new:
        return
    for name, future in admin.create_topics(new).items():
        try:
            future.result()
            logger.info("Utworzono temat %s", name)
        except KafkaException as error:
            # Wyścig: temat mógł powstać w międzyczasie (np. równolegle uruchomiony konsument).
            if "TOPIC_ALREADY_EXISTS" not in str(error):
                raise
