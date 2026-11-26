# GeoMarket Intelligence — backend (bramka API, port 8000)

Autor: Sebastian Michulec. Serwis FastAPI, przez który frontend rozmawia z całym systemem: konta użytkowników, ulubione, dane rynkowe z potoku strumieniowego (Kafka → Delta Lake) oraz pośredniczenie w zapytaniach do serwisu AI (`backend-ai`, port 8001).

Stan: **etap 5**: cała platforma w Docker Compose, testy wydajnościowe; wcześniej: konta (`/auth/*`), ulubione (`/api/favorites/*`), potok strumieniowy notowań (Yahoo Finance i CoinGecko → Kafka → Delta Lake), dane dla zakładek z Lakehouse (`/api/stocks`, `/api/crypto/top`, `/api/macro`, `/api/dashboard/markets`), pośredniczenie do serwisu AI z cache (`/chat`, `/news`, `/stock/...`).

## Wymagania (Windows)

- Docker Desktop (WSL2) — wystarczy do uruchomienia całej platformy,
- Python 3.12 lub nowszy i Git — tylko do pracy nad kodem backendu i testów.

## Cała platforma jednym poleceniem (Docker)

Z katalogu głównego repozytorium:

1. `Copy-Item .env.example .env` i uzupełnij `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`, `JWT_SECRET_KEY`.
2. Klucze serwisu AI w `backend-ai/.env` (`GEMINI_API_KEY`, `FRED_API_KEY`, `NEWS_API_KEY` — ma je Patryk). Bez `GEMINI_API_KEY` serwis AI nie wystartuje (restartuje się); reszta platformy działa, a czat, newsy i wskaźniki makro są niedostępne.
3. Uruchomienie:

   ```powershell
   docker compose up -d --build
   ```

Uruchamiane usługi: `mysql`, `kafka`, `kafka-ui`, `migrate` (migracje, jednorazowo), `api` (port 8000), `consumer`, `producer`, `backfill` (historia, jednorazowo przy każdym starcie), `backend-ai` (port 8001, tylko z tego komputera), `frontend` (port 5173). Stan: `docker compose ps`, logi: `docker compose logs -f api consumer producer`.

| Adres | Co to jest |
| --- | --- |
| http://localhost:5173 | Frontend |
| http://localhost:8000/docs | API (Swagger) |
| http://localhost:8090 | Kafka UI |

Frontend w kontenerze łączy się z API pod adresem z `PUBLIC_API_URL` (domyślnie `http://localhost:8000`), wpisywanym w czasie budowania — po zmianie: `docker compose build frontend`. Na VPS za reverse proxy z SSL ustaw `PUBLIC_API_URL` na publiczny adres API, `CORS_ORIGINS` na adres frontendu, a `FORWARDED_ALLOW_IPS` na adres proxy (limity zapytań liczą wtedy prawdziwe IP klientów). Dockerfile serwisu AI i frontendu leżą w `docker/` — nie zmieniają kodu ich autorów.

## Praca nad backendem bez Dockera dla API (pierwsze uruchomienie)

Polecenia w PowerShell, z katalogu głównego repozytorium.

1. Konfiguracja: skopiuj wzór i uzupełnij co najmniej `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` i `JWT_SECRET_KEY` (opis każdej zmiennej jest w pliku).

   ```powershell
   Copy-Item .env.example .env
   ```

2. Same kontenery infrastruktury (MySQL, Kafka, Kafka UI):

   ```powershell
   docker compose up -d mysql kafka kafka-ui
   ```

3. Środowisko Pythona i zależności:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   ```

4. Migracje schematu:

   ```powershell
   alembic upgrade head
   ```

5. Serwer API:

   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```

## Potok strumieniowy (notowania)

Trzy procesy, każdy w osobnym terminalu PowerShell (w `backend/`, z aktywnym `.venv`):

| Krok | Polecenie | Co robi |
| --- | --- | --- |
| 1. Konsument (zostaw włączony) | `python -m app.stream.consumer` | Kafka → Bronze → Silver → Gold (Delta Lake w `LAKEHOUSE_ROOT`, domyślnie `data/lakehouse`) |
| 2. Historia (jednorazowo) | `python -m app.stream.backfill` | 60 dni świec godzinowych, liczba akcji spółek, TOP 100 krypto → Kafka |
| 3. Producent (zostaw włączony) | `python -m app.stream.producer` | co 60 s świece minutowe z Yahoo, co 5 min krypto z CoinGecko → Kafka |

API czyta tabele Gold, gdy `MARKET_DATA_SOURCE=lakehouse` (domyślnie w `.env.example`). Do pracy bez potoku: `MARKET_DATA_SOURCE=test` (dane testowe).

Odbudowa Lakehouse z Kafki (tematy przechowują wiadomości 7 dni): zatrzymaj konsumenta, odczekaj ok. minutę, usuń katalog `data/lakehouse` i grupę konsumentów `geomarket-lakehouse` (Kafka UI → Consumers), uruchom konsumenta ponownie — przetworzy wszystkie wiadomości od początku.

## Adresy

| Adres | Co to jest |
| --- | --- |
| http://127.0.0.1:8000/docs | Dokumentacja Swagger (OpenAPI) |
| http://127.0.0.1:8000/health | Czy proces działa |
| http://127.0.0.1:8000/health/ready | Czy baza danych jest dostępna (503, jeśli nie) |
| `/auth/register`, `/auth/login`, `/auth/me`, `/auth/logout`, `/auth/forgot-password`, `/auth/reset-password` | Konta (szczegóły i przykłady w Swaggerze) |
| `/api/favorites/{stock\|crypto\|macro}` | Ulubione zalogowanego użytkownika |
| `/api/stocks`, `/api/crypto/top`, `/api/macro`, `/api/dashboard/markets` | Dane dla zakładek Giełda, Krypto, Makro i strony głównej |
| `/chat`, `/news`, `/news/analysis`, `/stock/...` | Zapytania AI przekazywane do serwisu AI (`AI_SERVICE_URL`, domyślnie port 8001) |
| `127.0.0.1:3306` | MySQL (DBeaver / MySQL Workbench; użytkownik i hasło z `.env`) |
| `localhost:9092` | Kafka (tematy `market.yahoo.bars.v1`, `market.coingecko.markets.v1`) |
| http://localhost:8090 | Kafka UI: tematy, partycje, wiadomości, opóźnienie konsumentów |

## Testy

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

Testy oznaczone `integration` wymagają działającego MySQL, a `kafka` — działającej Kafki (`docker compose up -d`). Bez kontenerów są pomijane. Testy używają osobnej bazy `geomarket_test` i nigdy nie łączą się z Resend ani Google (atrapy).

## Testy wydajnościowe

Narzędzia w `perf/` (zależności z `requirements-dev.txt`):

| Polecenie (z `backend/`) | Co mierzy |
| --- | --- |
| `locust -f perf/locustfile.py --host http://localhost:8000 --headless -u 200 -r 20 -t 2m --csv perf/wyniki/api_200` | obciążenie API: przeglądanie zakładek + zalogowani użytkownicy z ulubionymi |
| `python -m perf.pipeline_benchmark lakehouse` | zapis paczek do Delta Lake (świece/s) |
| `python -m perf.pipeline_benchmark kafka --messages 2000` | producent → Kafka → konsument → Delta: przepustowość i opóźnienie |

Podczas testu obciążeniowego wszyscy wirtualni użytkownicy mają jedno IP — limity zapytań trzeba wyłączyć (`RATE_LIMIT_ENABLED=false` dla usługi `api`). Na Windows przy kilkuset równoczesnych połączeniach przekierowanie portów Docker Desktop zrywa część połączeń — dokładniejszy wynik daje Locust uruchomiony w sieci Compose:
`docker run --rm --network geomarket_default -v ${PWD}/perf:/mnt/perf locustio/locust:2.47.0 -f /mnt/perf/locustfile.py --host http://api:8000 --headless -u 500 -r 50 -t 90s`.

## Reset hasła lokalnie

Bez `RESEND_API_KEY` w trybie `APP_ENV=development` backend nie wysyła maila, tylko wypisuje link resetu w konsoli. Wystarczy go skopiować do przeglądarki.

## Serwis AI

Czat, newsy i analizy wymagają działającego serwisu AI (`backend-ai`, port 8001, instrukcja w jego README). Bez niego bramka działa dalej: zapytania AI zwracają 503 albo ostatnią zapamiętaną odpowiedź, a wskaźniki makro mają wartość `null`.

## Dokumentacja

- [docs/integracja_frontendu.md](docs/integracja_frontendu.md): podłączenie frontendu, mapa pól, gotowe adaptery JS
- [docs/konwencja_lakehouse.md](docs/konwencja_lakehouse.md): wspólne zasady Lakehouse dla obu potoków
