"""Kontrakty odpowiedzi endpointów rynkowych — dokładnie nazwy pól używane w komponentach React.

Źródła nazw pól (spisane z kodu frontendu 16.11.2026):
- `StockOut`  ← `pages/StockMarket.jsx` (tablica STOCKS + `history[].time/price`),
- `CryptoOut` ← `pages/Crypto.jsx` (format CoinGecko `/coins/markets`),
- `MacroOut`  ← `pages/Macro.jsx` (tablica MACRO_DATA + `history[].time/value`),
- `DashboardCardOut` ← `mock/markets.json` + `components/MarketCard.jsx`.

Pola dodatkowe (`currency`, `source`, `updated_at`, `unit_description`) są opcjonalne:
komponenty ich nie czytają, ale mówią, skąd i z kiedy jest wartość.
Liczby jako number (2.5 = 2,5%), brak wartości = null, serie od najstarszego do najnowszego.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PricePoint(BaseModel):
    time: datetime = Field(description="Czas punktu, ISO 8601 w UTC")
    price: float


class ValuePoint(BaseModel):
    time: datetime = Field(description="Czas punktu, ISO 8601 w UTC")
    value: float


class StockOut(BaseModel):
    symbol: str
    name: str
    market: str = Field(description='"Zagraniczny" albo "Polska" (etykiety z StockMarket.jsx)')
    price: float | None
    change: float | None = Field(description="Zmiana ceny w % względem poprzedniego zamknięcia")
    volume: float | None
    marketCap: float | None = Field(description="Kapitalizacja w walucie notowania")
    history: list[PricePoint]
    currency: str
    source: str
    updated_at: datetime | None


class Sparkline(BaseModel):
    price: list[float] = Field(description="Ceny godzinowe z 7 dni, od najstarszej")


class CryptoOut(BaseModel):
    id: str
    symbol: str
    name: str
    image: str | None
    market_cap_rank: int | None
    current_price: float | None
    price_change_percentage_1h_in_currency: float | None
    price_change_percentage_24h_in_currency: float | None
    price_change_percentage_7d_in_currency: float | None
    total_volume: float | None
    market_cap: float | None
    sparkline_in_7d: Sparkline
    source: str
    updated_at: datetime | None


class MacroOut(BaseModel):
    symbol: str
    name: str
    category: str = Field(description="Waluty | Inflacja | Stopy procentowe | PKB | Surowce")
    value: float | None
    change: float | None = Field(
        description="Kursy i surowce: % zmiany w 24 h. Inflacja, stopy, PKB: różnica w punktach "
        "procentowych względem poprzedniego odczytu."
    )
    unit: str = Field(description='"PLN", "USD" albo "%"')
    unit_description: str | None = Field(description='Dokładna jednostka, np. "USD za baryłkę", "% r/r"')
    description: str
    history: list[ValuePoint]
    source: str
    updated_at: datetime | None


class DashboardCardOut(BaseModel):
    id: int
    name: str
    value: str = Field(description='Wartość sformatowana do wyświetlenia, np. "267 540 PLN"')
    change: str = Field(description='Zmiana 24 h ze znakiem, np. "+2.45%" (MarketCard sprawdza startsWith("+"))')
    path: str
    value_number: float | None
    change_percent: float | None
    source: str
