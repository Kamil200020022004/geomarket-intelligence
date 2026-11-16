# Jak działa część Sebastiana — opis techniczny

Dokument opisuje, **jak** działa backend i potok strumieniowy: komponenty, przepływy danych, kluczowe mechanizmy. Jest aktualizowany po każdym etapie i ma wystarczyć do napisania rozdziałów „Projekt” i „Implementacja” pracy inżynierskiej bez zaglądania do kodu.

Dokumenty uzupełniające:
- [decyzje.md](decyzje.md) — **dlaczego** wybrano dane rozwiązanie (alternatywy, uzasadnienie),
- [moja_czesc.md](moja_czesc.md) — **kto** jest autorem czego,
- [konwencja_lakehouse.md](konwencja_lakehouse.md) — zasady wspólnego Lakehouse,
- [zrodla.md](zrodla.md) — bibliografia.

Stan: **etap 0** (szkielet).

---

## 1. Miejsce w architekturze

```
Przeglądarka (React, Kamil)
        │ HTTP/JSON
        ▼
Backend Sebastiana :8000 (FastAPI) ──▶ MySQL (konta, tokeny, ulubione)
        │                         └──▶ Serwis AI Patryka :8001 (etap 2)
        ▼
Lakehouse (Delta Lake) ◀── Konsument Kafki ◀── Kafka ◀── Producent (Yahoo, CoinGecko)   (etap 3)
```

Backend jest **bramką API** (API gateway): jedynym punktem, z którym rozmawia frontend. Ukrywa przed przeglądarką wewnętrzne usługi (bazę, serwis AI, Lakehouse) i przemapowuje dane na formaty oczekiwane przez komponenty React.

## 2. Struktura kodu (`backend/`)

| Katalog / plik | Warstwa | Rola |
| --- | --- | --- |
| `app/main.py` | wejście | Tworzy aplikację (`create_app`), rejestruje middleware CORS, obsługę błędów i routery |
| `app/core/` | konfiguracja | Ustawienia z `.env` (`config.py`), format błędów (`errors.py`) |
| `app/api/` | prezentacja (HTTP) | Routery FastAPI — jeden plik na obszar (np. `health.py`) |
| `app/db/` | dostęp do danych | Silnik i sesje SQLAlchemy, klasa bazowa modeli, rejestr modeli |
| `alembic/` | schemat bazy | Migracje MySQL |
| `tests/` | testy | pytest + `TestClient` |
| `docker/mysql-init/` | infrastruktura | Skrypty wykonywane przy pierwszym starcie MySQL |

Zasada podziału: trasy HTTP nie zawierają logiki biznesowej ani zapytań SQL — wołają warstwę usług (`app/services/`, od etapu 1), a ta korzysta z modeli i sesji z `app/db/`.

## 3. Cykl życia żądania HTTP

1. Uvicorn (serwer ASGI) przyjmuje połączenie i przekazuje żądanie aplikacji FastAPI.
2. **Middleware CORS** sprawdza nagłówek `Origin`. Jeśli adres frontendu jest na liście `CORS_ORIGINS`, dodaje nagłówek `Access-Control-Allow-Origin` — bez niego przeglądarka nie odda odpowiedzi skryptowi strony.
3. FastAPI dopasowuje trasę, waliduje parametry i ciało żądania (Pydantic). Błędne dane → automatycznie 422 z opisem w `detail`.
4. **Zależności** (`Depends`) przygotowują zasoby, np. `get_db()` otwiera sesję bazy na czas żądania i zamyka ją po odpowiedzi.
5. Funkcja trasy zwraca wynik, FastAPI serializuje go do JSON.
6. Nieobsłużony wyjątek przechwytuje `unhandled_exception_handler`: zapis pełnego śladu do logów, klientowi tylko `500 {"detail": "Wewnętrzny błąd serwera."}`.

## 4. Konfiguracja

- Klasa `Settings` (`pydantic-settings`) czyta zmienne środowiskowe, a brakujące — z pliku `.env` w katalogu głównym repozytorium. Typy są sprawdzane przy starcie (np. `MYSQL_PORT` musi być liczbą).
- Ten sam `.env` czyta Docker Compose (hasła MySQL), więc konfiguracja jest w jednym miejscu.
- `get_settings()` jest opakowane w `lru_cache` — plik czytany raz na proces.
- Adres bazy (`database_url`) składany z części: `mysql+pymysql://użytkownik:hasło@host:port/baza?charset=utf8mb4`.

## 5. Baza danych

- **MySQL 8.4** w kontenerze; dane w nazwanym wolumenie `mysql_data` (przetrwają usunięcie kontenera).
- Przy pierwszym starcie skrypt `01-test-database.sh` tworzy bazę `geomarket_test` i nadaje do niej uprawnienia — testy integracyjne pracują na niej, nie na bazie roboczej.
- **SQLAlchemy 2** (ORM, tryb synchroniczny) z pulą połączeń; `pool_pre_ping` wykrywa połączenia zerwane przez MySQL, `pool_recycle=3600` odnawia je co godzinę.
- **Alembic**: schemat zmieniany wyłącznie migracjami w `alembic/versions/`. `env.py` bierze adres bazy z `Settings` i metadane z `Base.metadata`, więc `alembic revision --autogenerate` porównuje modele z bazą i generuje różnicę.

## 6. Stan serwisu (healthcheck)

| Endpoint | Co sprawdza | Kody |
| --- | --- | --- |
| `GET /health` | proces żyje (liveness) | 200 |
| `GET /health/ready` | baza odpowiada na `SELECT 1` (readiness) | 200 / 503 |

Kontener MySQL ma własny healthcheck (`mysqladmin ping`), dzięki któremu Docker Compose może uruchamiać zależne usługi dopiero po starcie bazy.

## 7. Testy

| Plik | Rodzaj | Co sprawdza |
| --- | --- | --- |
| `tests/test_health.py` | jednostkowe + 1 integracyjny | liveness; readiness przy działającej i niedziałającej bazie (atrapa przez `monkeypatch`); CORS przepuszcza frontend i odrzuca obcy adres; błąd 500 nie ujawnia szczegółów |

Testy oznaczone `@pytest.mark.integration` wymagają kontenerów; bez nich są pomijane (nie fałszywie zaliczane).

## 8. Materiał do pracy: zrzuty ekranu i pomiary

Lista rzeczy do uchwycenia w trakcie (✔ = zrobione):

- [ ] Swagger `/docs` po etapie 1 (endpointy kont i ulubionych)
- [ ] Tabele MySQL w DBeaver/Workbench (ERD)
- [ ] Wynik `pytest` z pokryciem
- [ ] Kafka UI: tematy, partycje, wiadomości, consumer lag (etap 3)
- [ ] Struktura katalogów Lakehouse i historia wersji tabeli Delta (etap 3)
- [ ] Pomiary wydajności (etap 5)
