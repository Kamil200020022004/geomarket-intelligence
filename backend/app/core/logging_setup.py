"""Wspólna konfiguracja logów dla API, producenta, konsumenta i ładowania historii."""

import logging
import sys


def configure_logging(level: str) -> None:
    # Konsola Windows domyślnie nie używa UTF-8 — bez tego polskie znaki w logach są zniekształcone.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    logging.basicConfig(level=level.upper(), format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    # Biblioteki zewnętrzne: tylko ostrzeżenia (httpx loguje każde zapytanie; yfinance zgłasza
    # zamknięte giełdy jako błędy „possibly delisted”).
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
