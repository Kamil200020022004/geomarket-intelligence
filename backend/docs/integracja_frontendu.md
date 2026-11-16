# Integracja frontendu z bramką API (dla Kamila)

Autor: Sebastian Michulec. Stan: etap 2 (16.11.2026). Bramka API: `http://127.0.0.1:8000`, Swagger: `/docs`.

Frontend łączy się **tylko z bramką na porcie 8000**. Bramka obsługuje konta i ulubione, dostarcza notowania z potoku strumieniowego i przekazuje zapytania AI do serwisu Patryka (port 8001). Ścieżki AI (`/chat`, `/news`, `/stock/...`) są takie same jak w serwisie Patryka, więc komponenty AI działają bez zmian.

> **Dane rynkowe są na razie testowe** (`"source": "test"`): kształt odpowiedzi jest docelowy, ale ceny są generowane. Prawdziwe notowania (Yahoo Finance, CoinGecko przez Kafkę) zastąpią je w etapie 3 bez zmiany formatu.

## 1. Konfiguracja

`frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
VITE_FAVORITES_PROVIDER=api
```

Po stronie backendu adres frontendu musi być na liście `CORS_ORIGINS` (domyślnie `http://localhost:5173` i `http://127.0.0.1:5173`). Dla Vercel/VPS dopisujemy jego domenę.

## 2. Pliki do podmiany (gotowe)

| Gotowy plik | Zastępuje | Co się zmienia |
| --- | --- | --- |
| [`frontend/aiApi.js`](frontend/aiApi.js) | `frontend/src/api/aiApi.js` | Krypto z backendu zamiast CoinGecko w przeglądarce; notowania z backendu zamiast Yahoo w przeglądarce; nowe funkcje `getStocks()`, `getMacroData()`, `getDashboardMarkets()`. Nazwy istniejących funkcji bez zmian. |
| [`frontend/favoritesService.js`](frontend/favoritesService.js) | `frontend/src/services/favoritesService.js` | Tryb `api`: ulubione w bazie (trwałe, osobne dla każdego konta). Tryb `local` działa jak dotąd. Sygnatury bez zmian. Token czytany z `localStorage["token"]` (tam zapisuje go `App.jsx`). |

## 3. Zmiany w komponentach

| Plik | Zmiana |
| --- | --- |
| `pages/StockMarket.jsx` | Zamiast `STOCKS` + `generateHistory()`: `const data = await getStocks()` w `useEffect`, potem `setStocks(data)` i `setSelectedStock(data[0])`. Dodać stan ładowania/błędu. `history[].time` to teraz czas ISO 8601 (np. `2026-11-16T14:00:00Z`) — do etykiety wykresu sformatować, np. `new Date(point.time).toLocaleString("pl-PL")`. |
| `pages/Macro.jsx` | Zamiast `MACRO_DATA` + `generateHistory()`: `await getMacroData()`. Wartość może być `null` (np. gdy serwis AI jest niedostępny) — wtedy `history` jest puste; `formatValue` już pokazuje „-”, wykres potrzebuje stanu „brak danych”. `history[].time` w ISO 8601. |
| `pages/Dashboard.jsx` | Zamiast `import markets from "../mock/markets.json"`: `await getDashboardMarkets()` w `useEffect`. `MarketCard` bez zmian (pola `name`, `value`, `change`, `path` jak w mocku). |
| `pages/Crypto.jsx` | Bez zmian — `getTopCryptocurrencies()` ma tę samą nazwę i format. |
| `components/ChatDrawer.jsx`, `pages/News.jsx`, `components/AIImpactCard.jsx`, `components/LatestNewsCard.jsx` | Bez zmian w logice. |
| `components/LoginDrawer.jsx`, `pages/ResetPassword.jsx`, `pages/News.jsx` | Domyślny adres (gdy brak `VITE_API_URL`) zmienić z `127.0.0.1:8001` na `127.0.0.1:8000`. |
| `components/LoginDrawer.jsx` (rejestracja) | Gdy będzie widget reCAPTCHA: wysyłać token w polu `recaptcha_token` obok `name`, `email`, `password`. Odrzucona captcha → 400 z `detail`. |
| obsługa błędów | Nowe kody: **429** (zbyt wiele prób, `detail` z komunikatem) i **503** (serwis AI niedostępny, `detail` z komunikatem). Wystarczy wyświetlić `detail`. |

Zakresy wykresów (1D/1W/1M w Giełdzie i Makro, 1H/24H/7D w Krypto): obecnie wycinają ostatnie N punktów. Seria testowa giełdy ma 48 punktów godzinowych, krypto 168 punktów godzinowych (7 dni). Docelowe zakresy uzgodnimy przy etapie 3, gdy będą prawdziwe serie.

## 4. Endpointy

| Metoda i ścieżka | Komponent | Odpowiedź |
| --- | --- | --- |
| `GET /api/stocks` | StockMarket | tablica 100 spółek |
| `GET /api/crypto/top` | Crypto | tablica (format CoinGecko) |
| `GET /api/macro` | Macro | tablica 17 pozycji |
| `GET /api/dashboard/markets` | Dashboard | tablica 3 kafelków |
| `GET/POST /api/favorites/{stock\|crypto\|macro}`, `DELETE /api/favorites/{type}/{id}` | Ulubione (przez `favoritesService.js`) | tablica elementów |
| `/auth/*` | LoginDrawer, App, ResetPassword | bez zmian względem prototypu |
| `POST /chat`, `GET /news`, `GET /news/analysis`, `GET /stock/ai-impact`, `GET /stock/news/{symbol}` i inne `/stock/...` z analizami | czat, newsy, AI Impact | jak w serwisie AI (przekazywane, z cache) |

## 5. Mapa pól

Źródło: **strumień** = potok strumieniowy Sebastiana (etap 2: dane testowe), **FRED** = serwis AI Patryka.

### Giełda — `GET /api/stocks`

| Pole JSX | Typ | Jednostka | Źródło |
| --- | --- | --- | --- |
| `symbol` | string | — | katalog (lista ze StockMarket.jsx) |
| `name` | string | — | katalog |
| `market` | string | `"Zagraniczny"` / `"Polska"` | katalog |
| `price` | number / null | waluta notowania (`currency`) | strumień |
| `change` | number / null | % zmiany 24 h | strumień |
| `volume` | number / null | liczba akcji | strumień |
| `marketCap` | number / null | waluta notowania | strumień |
| `history[]` | `{time: ISO 8601, price: number}` | od najstarszego | strumień |
| `currency` (opcjonalne) | string | `USD` / `PLN` | katalog |
| `source`, `updated_at` (opcjonalne) | string, ISO 8601 | — | — |

### Krypto — `GET /api/crypto/top`

Pola jak w CoinGecko `/coins/markets`: `id`, `symbol`, `name`, `image`, `market_cap_rank`, `current_price` (USD), `price_change_percentage_1h_in_currency`, `price_change_percentage_24h_in_currency`, `price_change_percentage_7d_in_currency` (%), `total_volume` (USD), `market_cap` (USD), `sparkline_in_7d.price` (ceny godzinowe z 7 dni, od najstarszej). Opcjonalne: `source`, `updated_at`. Docelowo TOP 100 z CoinGecko; dane testowe: 10 monet, `image = null`.

### Makro — `GET /api/macro`

| Pole JSX | Typ | Opis |
| --- | --- | --- |
| `symbol`, `name`, `category`, `description` | string | Symbole i kolejność jak w `MACRO_DATA` |
| `value` | number / null | Ostatnia wartość |
| `change` | number / null | Kursy i surowce: % zmiany 24 h. Inflacja, stopy, PKB: różnica w **punktach procentowych** do poprzedniego odczytu |
| `unit` | `"PLN"` / `"USD"` / `"%"` | Jak w `MACRO_DATA` |
| `unit_description` (opcjonalne) | string | Dokładna jednostka: `"USD za baryłkę"`, `"% r/r"` itd. |
| `history[]` | `{time: ISO 8601, value: number}` | Od najstarszego. Wskaźniki FRED: 12 ostatnich odczytów (miesięcznych/kwartalnych) — bez sztucznych punktów dziennych |

| Symbole | Źródło | Uwagi |
| --- | --- | --- |
| EUR/PLN, USD/PLN, CHF/PLN, GBP/PLN, EUR/USD | strumień (Yahoo) | |
| OIL, GOLD, GAS | strumień (Yahoo, kontrakty terminowe) | Ropa Brent (USD/baryłka), złoto (USD/uncja), gaz Henry Hub (USD/MMBtu) |
| CPI PL, CPI USA, CPI EU | FRED (serwis AI) | % r/r |
| NBP RATE, FED RATE, ECB RATE | FRED (serwis AI) | NBP RATE to obecnie krótkoterminowa stopa międzybankowa (seria OECD), nie stopa referencyjna NBP |
| GDP PL, GDP USA, GDP EU | FRED (serwis AI) | % r/r |

### Dashboard — `GET /api/dashboard/markets`

`id` (number), `name`, `value` (napis sformatowany po polsku, np. `"267 540 PLN"`), `change` (napis ze znakiem, np. `"+2.45%"`; brak danych: `"—"`), `path`. Opcjonalnie liczby: `value_number`, `change_percent`. Kafelki: Bitcoin (PLN = cena USD × USD/PLN), WIG20, EUR/PLN.

## 6. Przykładowe odpowiedzi (DANE TESTOWE)

```json
// GET /api/stocks (fragment jednego elementu)
{"symbol": "PKN", "name": "Orlen", "market": "Polska", "price": 191.74, "change": 0.24,
 "volume": 1250000.0, "marketCap": 74000000000.0, "currency": "PLN", "source": "test",
 "updated_at": "2026-11-16T19:00:00Z",
 "history": [{"time": "2026-11-14T20:00:00Z", "price": 190.12}, "..."]}

// GET /api/dashboard/markets
[{"id": 1, "name": "Bitcoin", "value": "364 053 PLN", "change": "-6.04%", "path": "/kryptowaluty",
  "value_number": 364053.2, "change_percent": -6.04, "source": "test"}, "..."]
```

Pełne schematy z typami i kodami błędów: Swagger `http://127.0.0.1:8000/docs`.
