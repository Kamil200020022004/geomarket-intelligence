# Moja część projektu — Sebastian Michulec

Rejestr wszystkiego, co w repozytorium jest autorstwa Sebastiana. Pełną historię pokazują `git log --author="Sebastian"` i `git blame <plik>`.

## 1. Pliki w całości autorstwa Sebastiana

| Ścieżka | Co to jest | Etap |
| --- | --- | --- |
| `backend/` (cały katalog) | Bramka API, konta, ulubione, potok strumieniowy, testy, dokumentacja | od 0 |
| `docker-compose.yml` (katalog główny) | Uruchamianie usług całej platformy | 0 |
| `.env.example` (katalog główny) | Wzór konfiguracji backendu i Docker Compose | 0 |

### Zawartość `backend/` (aktualizowane na bieżąco)

| Ścieżka | Odpowiedzialność |
| --- | --- |
| `app/main.py` | Tworzenie aplikacji FastAPI, CORS, rejestracja tras i obsługi błędów |
| `app/core/config.py` | Konfiguracja ze zmiennych środowiskowych (`.env`) |
| `app/core/errors.py` | Jednolity format błędów |
| `app/db/base.py`, `app/db/session.py`, `app/db/models.py` | Połączenie z MySQL, sesje, rejestr modeli |
| `app/api/health.py` | `/health` i `/health/ready` |
| `alembic/`, `alembic.ini` | Migracje schematu MySQL |
| `docker/mysql-init/01-test-database.sh` | Tworzenie bazy testowej przy pierwszym starcie MySQL |
| `tests/` | Testy automatyczne |
| `docs/konwencja_lakehouse.md` | Konwencja Lakehouse obowiązująca oba potoki |
| `docs/decyzje.md`, `docs/zrodla.md`, `docs/moja_czesc.md`, `docs/opis_dzialania.md` | Dokumentacja do pracy inżynierskiej |

## 2. Zmiany w plikach innych autorów

Brak. Zasada: cudzego kodu nie edytujemy; uwagi przekazujemy właścicielowi. Każdy wyjątek (np. adaptery JS, jeśli zostaną uzgodnione) zostanie tu wpisany z opisem zmiany.

## 3. Elementy przejęte od innych członków zespołu

| Element | Pierwotny autor | Co zrobiono |
| --- | --- | --- |
| Logowanie, rejestracja i reset hasła | Kamil (prototyp na Excelu w `backend-ai`) | Etap 1: nowa implementacja na MySQL i JWT, kontrakt odpowiedzi zachowany |
| Pobieranie notowań z Yahoo Finance | Patryk (`backend-ai/app/data_sources/yahoo.py`) | Etap 3: przeniesione do potoku strumieniowego |

## 4. Uzgodnienia przekazane zespołowi

| Data | Do kogo | Czego dotyczy |
| --- | --- | --- |
| 15.11.2026 | Patryk | Konwencja Lakehouse (`docs/konwencja_lakehouse.md`): wspólny `LAKEHOUSE_ROOT`, Delta w Silver i Gold, odczyt cen z `gold/market/latest_prices` |
