"""Źródła danych rynkowych.

Warstwa usług (`service.py`) nie wie, skąd pochodzą notowania — dostaje je przez interfejs
`MarketDataSource`. W etapie 2 jest to `TestMarketData` (dane testowe), w etapie 3 dojdzie
implementacja czytająca tabele Gold z Lakehouse. Zmiana źródła = zmiana `MARKET_DATA_SOURCE`,
bez zmian w endpointach i formatach odpowiedzi.
"""

import hashlib
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Protocol

from app.core.config import get_settings
from app.market.catalog import Instrument


@dataclass(frozen=True)
class InstrumentSnapshot:
    """Stan instrumentu: ostatnia cena, zmiana i seria historyczna (od najstarszego punktu)."""

    price: float | None
    change_24h_pct: float | None
    volume: float | None
    market_cap: float | None
    history: list[tuple[datetime, float]]
    updated_at: datetime | None


@dataclass(frozen=True)
class CoinSnapshot:
    id: str
    symbol: str
    name: str
    image: str | None
    market_cap_rank: int | None
    price: float | None
    change_1h_pct: float | None
    change_24h_pct: float | None
    change_7d_pct: float | None
    total_volume: float | None
    market_cap: float | None
    sparkline_7d: list[float] = field(default_factory=list)
    updated_at: datetime | None = None


class MarketDataSource(Protocol):
    name: str

    def snapshot(self, instrument: Instrument) -> InstrumentSnapshot: ...

    def top_coins(self, limit: int) -> list[CoinSnapshot]: ...


# --------------------------------------------------------------------------------------
# Dane testowe (etap 2)
# --------------------------------------------------------------------------------------

# Przybliżone poziomy startowe, żeby dane testowe wyglądały wiarygodnie w interfejsie.
_TEST_BASE_PRICES = {
    "EUR/PLN": 4.27, "USD/PLN": 3.92, "CHF/PLN": 4.55, "GBP/PLN": 5.02, "EUR/USD": 1.09,
    "OIL": 74.0, "GOLD": 2650.0, "GAS": 3.1, "WIG20": 2350.0,
}
_TEST_COINS = [
    ("bitcoin", "btc", "Bitcoin", 97000.0), ("ethereum", "eth", "Ethereum", 3400.0),
    ("tether", "usdt", "Tether", 1.0), ("ripple", "xrp", "XRP", 1.1), ("binancecoin", "bnb", "BNB", 640.0),
    ("solana", "sol", "Solana", 190.0), ("usd-coin", "usdc", "USDC", 1.0), ("dogecoin", "doge", "Dogecoin", 0.32),
    ("cardano", "ada", "Cardano", 0.78), ("tron", "trx", "TRON", 0.2),
]


def _rng(key: str) -> random.Random:
    """Generator deterministyczny dla danego klucza — te same dane przy każdym wywołaniu (stabilne testy)."""
    return random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:16], 16))


def _random_walk(rng: random.Random, start: float, points: int, volatility: float) -> list[float]:
    values = [start]
    for _ in range(points - 1):
        values.append(max(values[-1] * (1 + rng.gauss(0, volatility)), start * 0.01))
    return values


def _hourly_grid(points: int, now: datetime) -> list[datetime]:
    last = now.replace(minute=0, second=0, microsecond=0)
    return [last - timedelta(hours=points - 1 - i) for i in range(points)]


def _pct(new: float, old: float) -> float:
    return round((new / old - 1) * 100, 2)


class TestMarketData:
    """Dane TESTOWE: deterministyczne błądzenie losowe na siatce godzinowej. Oznaczane source="test"."""

    __test__ = False  # nazwa zaczyna się od "Test" — informacja dla pytest, że to nie jest klasa testów
    name = "test"
    history_points = 48

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now

    def _current_time(self) -> datetime:
        return self._now or datetime.now(UTC)

    def snapshot(self, instrument: Instrument) -> InstrumentSnapshot:
        rng = _rng(instrument.symbol)
        base = _TEST_BASE_PRICES.get(instrument.symbol, round(rng.uniform(5, 500), 2))
        volatility = 0.002 if instrument.asset_class == "fx" else 0.006
        now = self._current_time()
        values = _random_walk(rng, base, self.history_points, volatility)
        history = [(t, round(v, 4)) for t, v in zip(_hourly_grid(self.history_points, now), values, strict=True)]
        is_stock = instrument.asset_class == "stock"
        return InstrumentSnapshot(
            price=history[-1][1],
            change_24h_pct=_pct(values[-1], values[-25]),
            volume=float(rng.randint(10_000, 50_000_000)) if is_stock else None,
            market_cap=float(rng.randint(1, 3000)) * 1e9 if is_stock else None,
            history=history,
            updated_at=history[-1][0],
        )

    def top_coins(self, limit: int) -> list[CoinSnapshot]:
        now = self._current_time()
        coins = []
        for rank, (coin_id, symbol, name, base) in enumerate(_TEST_COINS[:limit], start=1):
            rng = _rng(coin_id)
            values = _random_walk(rng, base, 168, 0.0001 if base == 1.0 else 0.008)
            coins.append(
                CoinSnapshot(
                    id=coin_id, symbol=symbol, name=name, image=None, market_cap_rank=rank,
                    price=round(values[-1], 6),
                    change_1h_pct=_pct(values[-1], values[-2]),
                    change_24h_pct=_pct(values[-1], values[-25]),
                    change_7d_pct=_pct(values[-1], values[0]),
                    total_volume=float(rng.randint(10**8, 5 * 10**10)),
                    market_cap=float(rng.randint(10**9, 2 * 10**12)),
                    sparkline_7d=[round(v, 6) for v in values],
                    updated_at=_hourly_grid(1, now)[0],
                )
            )
        return coins


# --------------------------------------------------------------------------------------
# Lakehouse (etap 3) — odczyt tabel Gold zapisywanych przez konsumenta Kafki
# --------------------------------------------------------------------------------------


@dataclass
class _GoldView:
    latest: dict[str, dict]
    history: dict[str, list[tuple[datetime, float]]]
    coins: list[dict]
    loaded_at: float


class LakehouseMarketData:
    """Czyta Gold (`latest_prices`, `ohlc_1h`, `crypto_top`) i trzyma je w pamięci przez kilka sekund.

    Tabele są małe (ok. 100 instrumentów × 30 dni × 24 h), więc jeden odczyt na kilkanaście sekund
    obsługuje dowolną liczbę zapytań HTTP. Delta Lake gwarantuje spójny odczyt (izolacja migawek),
    nawet gdy konsument w tym samym momencie zapisuje nową wersję tabeli.
    """

    name = "lakehouse"

    def __init__(self, root: Path, history_days: int, cache_seconds: float) -> None:
        self.root = root
        self.history_days = history_days
        self.cache_seconds = cache_seconds
        self._view: _GoldView | None = None
        self._lock = threading.Lock()

    def _load(self) -> _GoldView:
        from app.stream import lakehouse as lh  # import leniwy: tryb "test" nie ładuje biblioteki deltalake

        latest = {r["symbol"]: r for r in lh.read(self.root, lh.GOLD_LATEST_PRICES)}

        history: dict[str, list[tuple[datetime, float]]] = {}
        since = datetime.now(UTC) - timedelta(days=self.history_days)
        rows = lh.read(self.root, lh.GOLD_OHLC_1H, f"ts >= {lh.sql_ts(since)}", columns=["symbol", "ts", "close"])
        for row in sorted(rows, key=lambda r: r["ts"]):
            history.setdefault(row["symbol"], []).append((row["ts"], row["close"]))

        coins = lh.read(self.root, lh.GOLD_CRYPTO_TOP)
        coins.sort(key=lambda r: (r["market_cap_rank"] is None, r["market_cap_rank"] or 0))
        return _GoldView(latest, history, coins, time.monotonic())

    def _view_now(self) -> _GoldView:
        with self._lock:
            if self._view is None or time.monotonic() - self._view.loaded_at > self.cache_seconds:
                self._view = self._load()
            return self._view

    def snapshot(self, instrument: Instrument) -> InstrumentSnapshot:
        view = self._view_now()
        latest = view.latest.get(instrument.symbol)
        history = view.history.get(instrument.symbol, [])
        if latest is None:
            return InstrumentSnapshot(None, None, None, None, history, None)
        return InstrumentSnapshot(
            price=latest["price"],
            change_24h_pct=_round(latest["change_24h_pct"]),
            volume=latest["volume_24h"],
            market_cap=latest["market_cap"],
            history=history,
            updated_at=latest["ts"],
        )

    def top_coins(self, limit: int) -> list[CoinSnapshot]:
        return [
            CoinSnapshot(
                id=c["id"], symbol=c["symbol"], name=c["name"], image=c["image"],
                market_cap_rank=c["market_cap_rank"], price=c["price"],
                change_1h_pct=_round(c["change_1h_pct"]), change_24h_pct=_round(c["change_24h_pct"]),
                change_7d_pct=_round(c["change_7d_pct"]), total_volume=c["total_volume"],
                market_cap=c["market_cap"], sparkline_7d=list(c["sparkline_7d"] or []), updated_at=c["ts"],
            )
            for c in self._view_now().coins[:limit]
        ]


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 2)


_lakehouse_source: LakehouseMarketData | None = None


def get_market_source() -> MarketDataSource:
    global _lakehouse_source
    settings = get_settings()
    if settings.market_data_source == "test":
        return TestMarketData()
    if settings.market_data_source == "lakehouse":
        if _lakehouse_source is None:
            _lakehouse_source = LakehouseMarketData(
                Path(settings.lakehouse_root), settings.chart_history_days, settings.market_cache_seconds
            )
        return _lakehouse_source
    raise RuntimeError(f"Nieznane źródło danych rynkowych: {settings.market_data_source!r} (test | lakehouse)")
