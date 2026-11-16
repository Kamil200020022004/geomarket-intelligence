# Konwencja Lakehouse — GeoMarket Intelligence

Autor: Sebastian Michulec. Wersja 1.0 (15.11.2026). Obowiązuje oba potoki: strumieniowy (notowania) i wsadowy (makro, newsy, GDELT, wyniki AI).

Słowa **MUSI** oznaczają wymóg, bez którego dane z obu potoków nie tworzą jednego Lakehouse. **ZALECANE** to dobra praktyka, której brak nie psuje integracji.

## 1. Idea

Lakehouse to jedno wspólne miejsce na dane analityczne. Tabele są w otwartym formacie Delta Lake (pliki Parquet + dziennik transakcji `_delta_log`), co daje:

- atomowe zapisy: odczyt nigdy nie widzi połowy zapisu,
- historię wersji (time travel): `DeltaTable(ścieżka, version=n)`,
- wymuszanie schematu: zapis z innymi kolumnami lub typami kończy się błędem, a nie cichym zepsuciem tabeli.

Każdy potok pisze **własnym kodem do własnych tabel**. Wspólne są tylko zasady z tego dokumentu oraz tabele, które jeden potok czyta od drugiego (sekcja 6).

## 2. Katalog główny (MUSI)

- Wszystkie tabele leżą pod jednym katalogiem `LAKEHOUSE_ROOT` (zmienna środowiskowa).
- Lokalnie domyślnie `<repozytorium>/data/lakehouse`. Katalog `data/` jest wykluczony z Gita w głównym `.gitignore`.
- W Docker Compose oba serwisy montują ten sam wolumen pod `/data/lakehouse` i ustawiają `LAKEHOUSE_ROOT=/data/lakehouse`.
- Ścieżki **nie mogą** zależeć od katalogu, z którego uruchomiono serwis. Ścieżka względna `data/` przy innym katalogu roboczym tworzy drugie, osobne „jezioro”.

## 3. Struktura i nazewnictwo

```
{LAKEHOUSE_ROOT}/{warstwa}/{domena}/{tabela}
```

- `warstwa`: `bronze` | `silver` | `gold` (MUSI).
- `domena`: obszar danych z jednym właścicielem (MUSI, tabela w sekcji 5).
- `tabela`: `snake_case`, małe litery, cyfry i `_` (MUSI). Bez symboli instrumentów w nazwie (np. `EURPLN=X`). Symbol jest kolumną, nie częścią ścieżki.
- Nazwy kolumn: `snake_case`, małe litery (MUSI).

| Warstwa | Zawartość | Typowy tryb zapisu |
| --- | --- | --- |
| `bronze` | Surowe dane ze źródła, bez poprawek, z metadanymi pobrania | `append` |
| `silver` | Dane oczyszczone, z poprawnymi typami, zdeduplikowane, z historią | `merge` (upsert po kluczu) lub `append` + deduplikacja |
| `gold` | Agregaty i wyniki gotowe dla API, frontendu i AI | `overwrite` (migawka) lub `merge` |

Wszystkie trzy warstwy są tabelami Delta (MUSI dla `silver` i `gold`, ZALECANE dla `bronze`). W Bronze surowa odpowiedź API może być jedną kolumną tekstową `payload` (JSON jako string).

## 4. Typy i czas

- Czas zawsze w **UTC**, typ `timestamp` ze strefą (`pa.timestamp("us", tz="UTC")`) (MUSI).
- `ts`: czas obserwacji, którego dotyczy wartość (np. czas notowania, data publikacji wskaźnika) (ZALECANE).
- `ingested_at`: czas zapisu do Lakehouse (MUSI w każdej tabeli).
- Liczby jako `double` lub `int64`, nie tekst (MUSI w `silver` i `gold`). Procenty jako liczba procentów (`2.5` = 2,5%).
- Brak wartości: `null`, nie `0` ani `""`.

## 5. Domeny i właściciele

Jedna tabela ma jednego właściciela, który do niej pisze (MUSI). Pozostali tylko czytają. Unikamy w ten sposób równoczesnych zapisów do tej samej tabeli z dwóch serwisów.

| Domena | Właściciel | Zawartość |
| --- | --- | --- |
| `market` | Sebastian (potok strumieniowy) | Notowania akcji, indeksów, walut, surowców, kryptowalut |
| `macro` | Patryk (potok wsadowy) | Wskaźniki makroekonomiczne (FRED, dane PL i UE) |
| `news` | Patryk | Artykuły (RSS, NewsAPI) |
| `gdelt` | Patryk | Wydarzenia geopolityczne GDELT |
| `ai` | Patryk | Wyniki analiz LLM (sentyment, analizy, AI Impact) |

Obecne ścieżki potoku wsadowego (`silver/macro/<wskaźnik>`, `silver/gdelt/events_delta`) są zgodne ze schematem `warstwa/domena/tabela`.

## 6. Tabele domeny `market` (Sebastian)

Wstępne schematy; szczegóły ustalane w etapie 3 i dopisywane tutaj. Kolumny oznaczone ★ to **kontrakt** dla innych potoków. Nie zmieniają się bez uzgodnienia, nowe kolumny mogą dochodzić.

**Wymiar** `gold/market/dim_instrument`: jeden wiersz na instrument.
`symbol`★ (string, klucz, np. `AAPL`, `EUR/PLN`, `bitcoin`), `name`★, `asset_class`★ (`stock` | `index` | `fx` | `commodity` | `crypto`), `market` (np. `NASDAQ`, `GPW`), `currency`★, `source` (`yahoo` | `coingecko`), `source_symbol` (np. `EURPLN=X`), `ingested_at`.

**Fakty** `silver/market/prices`: oczyszczone notowania z historią (jedno źródło cen w systemie).
`symbol`★, `ts`★, `price`★ (double), `volume` (double / null), `currency`★, `asset_class`, `source`, `ingested_at`. Klucz unikalności: (`symbol`, `ts`). Partycjonowanie: `asset_class`.

**Fakty** `gold/market/ohlc`: świece dla wykresów.
`symbol`, `interval` (`1h` | `1d`), `ts` (początek świecy), `open`, `high`, `low`, `close`, `volume`, `ingested_at`.

**Migawka** `gold/market/latest_prices`: ostatnia cena każdego instrumentu, przeznaczona m.in. dla AI.
`symbol`★, `name`★, `asset_class`★, `currency`★, `price`★, `change_24h_pct`★ (double / null), `ts`★, `ingested_at`.

**Bronze** `bronze/market/quotes_raw`: surowe wiadomości przekazane przez Kafkę.
`source`, `source_symbol`, `payload` (JSON jako string), `kafka_topic`, `kafka_partition`, `kafka_offset`, `ingest_date` (partycja), `ingested_at`.

### Odczyt cen przez potok wsadowy / AI

```python
from deltalake import DeltaTable
import os

root = os.environ["LAKEHOUSE_ROOT"]
df = DeltaTable(f"{root}/gold/market/latest_prices").to_pandas()
row = df[df["symbol"] == "AAPL"]
```

## 7. Model danych analitycznych

Schemat gwiazdy: wymiar `dim_instrument` połączony po `symbol` z tabelami faktów `prices` i `ohlc`. Analogicznie zalecany dla domeny `macro`: wymiar wskaźników (`indicator`, `name`, `country`, `unit`, `frequency`) i fakty obserwacji (`indicator`, `ts`, `value`). Diagram powstaje razem z tabelami w etapie 3.

## 8. Czego nie robimy

- Nie zapisujemy danych z Lakehouse do Gita.
- Nie piszemy do cudzych tabel.
- Nie zmieniamy kolumn ★ bez uzgodnienia.
