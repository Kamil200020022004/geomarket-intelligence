"""Katalog instrumentów potoku strumieniowego (wymiar `dim_instrument` z konwencji Lakehouse).

Jedno miejsce, które mówi, CO pobieramy, skąd i pod jaką nazwą pokazujemy we frontendzie:
- `symbol` — identyfikator w API i we frontendzie (np. `AAPL`, `PKN`, `EUR/PLN`, `OIL`),
- `source_symbol` — symbol w źródle danych (Yahoo Finance: spółki GPW z sufiksem `.WA`, kursy `EURPLN=X`).

Lista spółek = lista ze `StockMarket.jsx` (50 z USA i 50 z GPW), uzgodnione 16.11.2026;
25.11.2026 usunięte CCC i Santander Bank Polska (brak notowań z GPW w Yahoo Finance) — 98 spółek.
Dostępność każdego symbolu w Yahoo Finance weryfikowana w etapie 3.
"""

from dataclasses import dataclass
from typing import Literal

AssetClass = Literal["stock", "index", "fx", "commodity", "crypto"]

# Etykiety rynku używane przez StockMarket.jsx (pole `market`).
MARKET_LABELS = {"US": "Zagraniczny", "PL": "Polska"}


@dataclass(frozen=True)
class Instrument:
    symbol: str
    name: str
    asset_class: AssetClass
    currency: str
    source: str
    source_symbol: str
    market: str | None = None  # US | PL dla spółek
    unit: str | None = None  # jednostka notowania, np. "USD za baryłkę"


_STOCKS: list[tuple[str, str, str]] = [
    ("AAPL", "Apple", "US"),
    ("MSFT", "Microsoft", "US"),
    ("NVDA", "Nvidia", "US"),
    ("GOOGL", "Alphabet", "US"),
    ("AMZN", "Amazon", "US"),
    ("META", "Meta Platforms", "US"),
    ("TSLA", "Tesla", "US"),
    ("AMD", "Advanced Micro Devices", "US"),
    ("NFLX", "Netflix", "US"),
    ("JPM", "JPMorgan Chase", "US"),
    ("V", "Visa", "US"),
    ("MA", "Mastercard", "US"),
    ("KO", "Coca-Cola", "US"),
    ("PEP", "PepsiCo", "US"),
    ("MCD", "McDonald's", "US"),
    ("DIS", "Walt Disney", "US"),
    ("INTC", "Intel", "US"),
    ("BA", "Boeing", "US"),
    ("WMT", "Walmart", "US"),
    ("NKE", "Nike", "US"),
    ("ORCL", "Oracle", "US"),
    ("CRM", "Salesforce", "US"),
    ("ADBE", "Adobe", "US"),
    ("PYPL", "PayPal", "US"),
    ("UBER", "Uber", "US"),
    ("ABNB", "Airbnb", "US"),
    ("SHOP", "Shopify", "US"),
    ("BABA", "Alibaba", "US"),
    ("PFE", "Pfizer", "US"),
    ("JNJ", "Johnson & Johnson", "US"),
    ("XOM", "Exxon Mobil", "US"),
    ("CVX", "Chevron", "US"),
    ("GS", "Goldman Sachs", "US"),
    ("BAC", "Bank of America", "US"),
    ("C", "Citigroup", "US"),
    ("T", "AT&T", "US"),
    ("VZ", "Verizon", "US"),
    ("QCOM", "Qualcomm", "US"),
    ("AVGO", "Broadcom", "US"),
    ("TXN", "Texas Instruments", "US"),
    ("IBM", "IBM", "US"),
    ("GE", "General Electric", "US"),
    ("GM", "General Motors", "US"),
    ("F", "Ford", "US"),
    ("SBUX", "Starbucks", "US"),
    ("COST", "Costco", "US"),
    ("HD", "Home Depot", "US"),
    ("LOW", "Lowe's", "US"),
    ("UPS", "UPS", "US"),
    ("FDX", "FedEx", "US"),
    ("PKN", "Orlen", "PL"),
    ("PKO", "PKO BP", "PL"),
    ("PEO", "Bank Pekao", "PL"),
    ("KGH", "KGHM", "PL"),
    ("PZU", "PZU", "PL"),
    ("CDR", "CD Projekt", "PL"),
    ("DNP", "Dino Polska", "PL"),
    ("ALE", "Allegro", "PL"),
    ("LPP", "LPP", "PL"),
    ("MBK", "mBank", "PL"),
    ("ING", "ING Bank Śląski", "PL"),
    ("ALR", "Alior Bank", "PL"),
    ("OPL", "Orange Polska", "PL"),
    ("TPE", "Tauron", "PL"),
    ("PGE", "PGE", "PL"),
    ("ENA", "Enea", "PL"),
    ("JSW", "JSW", "PL"),
    ("ACP", "Asseco Poland", "PL"),
    ("XTB", "XTB", "PL"),
    ("BFT", "Benefit Systems", "PL"),
    ("KTY", "Grupa Kęty", "PL"),
    ("KER", "Kernel", "PL"),
    ("ATT", "Grupa Azoty", "PL"),
    ("GPW", "GPW", "PL"),
    ("MIL", "Bank Millennium", "PL"),
    ("BHW", "Bank Handlowy", "PL"),
    ("CAR", "Inter Cars", "PL"),
    ("EUR", "Eurocash", "PL"),
    ("CPS", "Cyfrowy Polsat", "PL"),
    ("11B", "11 bit studios", "PL"),
    ("WPL", "Wirtualna Polska", "PL"),
    ("MAB", "Mabion", "PL"),
    ("DAT", "DataWalk", "PL"),
    ("TEN", "Ten Square Games", "PL"),
    ("PLW", "PlayWay", "PL"),
    ("RBW", "Rainbow Tours", "PL"),
    ("VRG", "VRG", "PL"),
    ("WLT", "Wielton", "PL"),
    ("NEU", "Neuca", "PL"),
    ("SNK", "Sanok Rubber", "PL"),
    ("DOM", "Dom Development", "PL"),
    ("ECH", "Echo Investment", "PL"),
    ("GTC", "GTC", "PL"),
    ("MRC", "Mercator Medical", "PL"),
    ("PCR", "PCC Rokita", "PL"),
    ("SNT", "Synektik", "PL"),
    ("VOT", "Votum", "PL"),
    ("MLS", "ML System", "PL"),
]

STOCKS: list[Instrument] = [
    Instrument(
        symbol=symbol,
        name=name,
        asset_class="stock",
        currency="USD" if market == "US" else "PLN",
        source="yahoo",
        source_symbol=symbol if market == "US" else f"{symbol}.WA",
        market=market,
    )
    for symbol, name, market in _STOCKS
]

FX: list[Instrument] = [
    Instrument("EUR/PLN", "Euro / Polski złoty", "fx", "PLN", "yahoo", "EURPLN=X"),
    Instrument("USD/PLN", "Dolar amerykański / Polski złoty", "fx", "PLN", "yahoo", "USDPLN=X"),
    Instrument("CHF/PLN", "Frank szwajcarski / Polski złoty", "fx", "PLN", "yahoo", "CHFPLN=X"),
    Instrument("GBP/PLN", "Funt brytyjski / Polski złoty", "fx", "PLN", "yahoo", "GBPPLN=X"),
    Instrument("EUR/USD", "Euro / Dolar amerykański", "fx", "USD", "yahoo", "EURUSD=X"),
]

# Kontrakty terminowe (front month) z Yahoo Finance — najbliższy dostępny odpowiednik ceny rynkowej.
COMMODITIES: list[Instrument] = [
    Instrument("OIL", "Ropa Brent", "commodity", "USD", "yahoo", "BZ=F", unit="USD za baryłkę"),
    Instrument("GOLD", "Złoto", "commodity", "USD", "yahoo", "GC=F", unit="USD za uncję trojańską"),
    Instrument("GAS", "Gaz ziemny (Henry Hub)", "commodity", "USD", "yahoo", "NG=F", unit="USD za MMBtu"),
]

INDICES: list[Instrument] = [
    Instrument("WIG20", "WIG20", "index", "PLN", "yahoo", "WIG20.WA", market="PL"),
]

ALL_YAHOO: list[Instrument] = STOCKS + FX + COMMODITIES + INDICES
BY_SYMBOL: dict[str, Instrument] = {instrument.symbol: instrument for instrument in ALL_YAHOO}

# Kryptowaluty: TOP 100 według kapitalizacji z CoinGecko — lista dynamiczna (zmienia się z rynkiem),
# więc nie jest wpisana na sztywno; identyfikatorem jest `id` CoinGecko (np. "bitcoin").
CRYPTO_TOP_N = 100

# Symbole z katalogu, których źródło nie notuje — producent ich nie pobiera, API zwraca je z ceną null.
# 17.11.2026 były tu CCC.WA (CCC — w Yahoo tylko giełda w Stuttgarcie) i SPL.WA (Santander Bank Polska,
# obecnie Erste Bank Polska — brak notowań z GPW); 25.11.2026 zespół zdecydował usunąć je z katalogu.
UNAVAILABLE_SOURCE_SYMBOLS: frozenset[str] = frozenset()

STREAMED: list[Instrument] = [i for i in ALL_YAHOO if i.source_symbol not in UNAVAILABLE_SOURCE_SYMBOLS]
BY_SOURCE_SYMBOL: dict[str, Instrument] = {i.source_symbol: i for i in ALL_YAHOO}
