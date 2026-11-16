"""Prosty cache w pamięci procesu z czasem świeżości (TTL) i przechowywaniem „przeterminowanych” wpisów.

Wpis ma dwa progi:
- `fresh_until` — do tego momentu zwracamy go bez pytania źródła,
- `keep_until` — do tego momentu trzymamy go jako zapas na wypadek awarii źródła (stale-if-error).

Wystarcza dla jednej instancji backendu. Przy wielu instancjach cache należałoby
przenieść do wspólnego magazynu (np. Redis).
"""

import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    fresh_until: float
    keep_until: float

    def is_fresh(self, now: float) -> bool:
        return now < self.fresh_until


class TTLCache:
    def __init__(self, max_entries: int = 1000) -> None:
        self._entries: dict[str, CacheEntry] = {}
        self._lock = threading.Lock()  # trasy synchroniczne działają w wielu wątkach
        self._max_entries = max_entries

    def get(self, key: str) -> CacheEntry | None:
        now = time.monotonic()
        with self._lock:
            entry = self._entries.get(key)
            if entry is not None and now >= entry.keep_until:
                del self._entries[key]
                return None
            return entry

    def set(self, key: str, value: Any, ttl_seconds: float, keep_seconds: float) -> None:
        now = time.monotonic()
        with self._lock:
            if len(self._entries) >= self._max_entries and key not in self._entries:
                self._evict_oldest()
            self._entries[key] = CacheEntry(
                value=value,
                fresh_until=now + ttl_seconds,
                keep_until=now + max(ttl_seconds, keep_seconds),
            )

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def _evict_oldest(self) -> None:
        oldest_key = min(self._entries, key=lambda k: self._entries[k].fresh_until)
        del self._entries[oldest_key]
