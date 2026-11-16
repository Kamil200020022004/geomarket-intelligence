# GeoMarket Intelligence — backend (bramka API, port 8000)

Autor: Sebastian Michulec. Serwis FastAPI, przez który frontend rozmawia z całym systemem: konta użytkowników, ulubione, dane rynkowe z potoku strumieniowego (Kafka → Delta Lake) oraz pośredniczenie w zapytaniach do serwisu AI (`backend-ai`, port 8001).

Stan: **etap 0**, szkielet aplikacji, MySQL, migracje, konwencja Lakehouse.

## Wymagania (Windows)

- Docker Desktop (WSL2)
- Python 3.12 lub nowszy
- Git

## Pierwsze uruchomienie

Polecenia w PowerShell, z katalogu głównego repozytorium.

1. Konfiguracja: skopiuj wzór i uzupełnij hasła `MYSQL_PASSWORD` i `MYSQL_ROOT_PASSWORD`.

   ```powershell
   Copy-Item .env.example .env
   ```

2. Baza danych (MySQL w kontenerze):

   ```powershell
   docker compose up -d
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

5. Serwer:

   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```

## Adresy

| Adres | Co to jest |
| --- | --- |
| http://127.0.0.1:8000/docs | Dokumentacja Swagger (OpenAPI) |
| http://127.0.0.1:8000/health | Czy proces działa |
| http://127.0.0.1:8000/health/ready | Czy baza danych jest dostępna (503, jeśli nie) |
| `127.0.0.1:3306` | MySQL (DBeaver / MySQL Workbench; użytkownik i hasło z `.env`) |

## Testy

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

Testy oznaczone `integration` wymagają działającego MySQL (`docker compose up -d`). Bez niego są pomijane.

## Dokumentacja

- [docs/konwencja_lakehouse.md](docs/konwencja_lakehouse.md): wspólne zasady Lakehouse dla obu potoków
- [docs/opis_dzialania.md](docs/opis_dzialania.md): jak działa backend (komponenty, przepływy)
- [docs/decyzje.md](docs/decyzje.md): dziennik decyzji projektowych
- [docs/moja_czesc.md](docs/moja_czesc.md): zakres autorstwa
- [docs/zrodla.md](docs/zrodla.md): źródła
