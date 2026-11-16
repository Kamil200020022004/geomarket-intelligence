# Dziennik decyzji — część Sebastiana

Format wpisu: kontekst (problem) → decyzja → uzasadnienie → konsekwencje. Materiał do pracy inżynierskiej.

---

## D-001. Osobny serwis w `backend/` jako bramka API (15.11.2026)

- **Kontekst:** frontend łączył się bezpośrednio z serwisem AI (`backend-ai`). Logowanie było tam oparte na pliku Excel.
- **Decyzja:** nowy serwis FastAPI na porcie 8000. Frontend rozmawia tylko z nim, a serwis AI działa na porcie 8001 jako usługa wewnętrzna.
- **Uzasadnienie:** izolacja kosztów i limitów Gemini, niezależne skalowanie, awaria AI nie wyłącza logowania ani danych rynkowych. Frontend ma już `VITE_API_URL=http://127.0.0.1:8000`, więc adres się nie zmienia.
- **Konsekwencje:** bramka pośredniczy w zapytaniach do AI (etap 2) i musi zachować ścieżki używane przez frontend.

## D-002. Konfiguracja przez zmienne środowiskowe i jeden plik `.env` (15.11.2026)

- **Kontekst:** hasła i klucze nie mogą trafić do repozytorium; ta sama konfiguracja jest potrzebna backendowi i Docker Compose.
- **Decyzja:** `pydantic-settings` czyta zmienne z pliku `.env` w katalogu głównym repozytorium. Do Gita trafia tylko `.env.example` bez wartości.
- **Uzasadnienie:** zasada „konfiguracja w środowisku” (Twelve-Factor App). Typy i wartości domyślne sprawdzane przy starcie.
- **Konsekwencje:** wdrożenie na VPS wymaga jedynie uzupełnienia `.env`.

## D-003. Synchroniczny SQLAlchemy 2 + PyMySQL (15.11.2026)

- **Kontekst:** wybór sterownika MySQL i stylu dostępu do bazy.
- **Decyzja:** synchroniczny SQLAlchemy 2 (ORM) ze sterownikiem PyMySQL. Endpointy bazodanowe jako zwykłe funkcje `def`.
- **Uzasadnienie:** FastAPI wykonuje funkcje `def` w puli wątków, więc zapytania nie blokują serwera. Przy skali projektu wersja asynchroniczna nie daje zysku, a komplikuje kod i testy. PyMySQL jest napisany w czystym Pythonie (brak kompilacji na Windows). Pakiet `cryptography` jest wymagany przez domyślne uwierzytelnianie MySQL 8 (`caching_sha2_password`).
- **Konsekwencje:** pula połączeń z `pool_pre_ping` i `pool_recycle`, bo MySQL zamyka bezczynne połączenia.

## D-004. Migracje schematu w Alembic (15.11.2026)

- **Decyzja:** każda zmiana tabel MySQL jako migracja Alembic. Adres bazy pobierany z ustawień aplikacji, a nie z `alembic.ini`. Nazwy plików migracji z datą.
- **Uzasadnienie:** schemat odtwarzalny na każdym komputerze i na VPS jednym poleceniem (`alembic upgrade head`); historia zmian schematu w Gicie.

## D-005. MySQL 8.4 w Dockerze z osobną bazą testową (15.11.2026)

- **Decyzja:** obraz `mysql:8.4` (wydanie LTS), dane w nazwanym wolumenie, healthcheck `mysqladmin ping`. Przy pierwszym starcie skrypt tworzy bazę `<nazwa>_test` dla testów integracyjnych.
- **Uzasadnienie:** testy nigdy nie dotykają danych roboczych. Healthcheck pozwala innym usługom czekać, aż baza będzie gotowa.
- **Problem i rozwiązanie:** skrypt `.sh` z końcami linii CRLF (Windows) nie uruchomi się w kontenerze Linux. Rozwiązanie: `.gitattributes` wymusza LF dla `*.sh`.

## D-006. Dwa endpointy stanu: liveness i readiness (15.11.2026)

- **Decyzja:** `/health` odpowiada, gdy proces żyje. `/health/ready` sprawdza bazę i zwraca 503, gdy jest niedostępna.
- **Uzasadnienie:** wzorzec znany z Kubernetes. Orkiestrator rozróżnia „proces zawieszony” od „zależność chwilowo niedostępna”.

## D-007. Jednolity format błędów `{"detail": ...}` (15.11.2026)

- **Decyzja:** nieobsłużone wyjątki zwracają 500 z ogólnym komunikatem, a szczegóły trafiają tylko do logów.
- **Uzasadnienie:** ten sam kształt co błędy walidacji FastAPI, więc frontend obsługuje błędy jednym kodem. Brak wycieku informacji o wnętrzu systemu.

## D-008. CORS z listą dozwolonych adresów (15.11.2026)

- **Decyzja:** dozwolone pochodzenia (origins) z `CORS_ORIGINS`, domyślnie serwer deweloperski Vite (port 5173).
- **Uzasadnienie:** `*` pozwalałby dowolnej stronie wołać API z przeglądarki zalogowanego użytkownika.

## D-009. Konwencja Lakehouse ustalona przed implementacją potoków (15.11.2026)

- **Kontekst:** potok wsadowy zaczął już zapisywać tabele Delta. Bez wspólnych zasad oba potoki utworzyłyby osobne, niespójne zbiory danych.
- **Decyzja:** dokument `konwencja_lakehouse.md`: wspólny `LAKEHOUSE_ROOT`, ścieżki `warstwa/domena/tabela`, czas w UTC, jedna tabela = jeden właściciel zapisu, schemat gwiazdy dla notowań. Istniejące ścieżki potoku wsadowego zostały przyjęte jako zgodne.
- **Uzasadnienie:** minimum uzgodnień przy maksymalnej niezależności zespołu. Jedynym punktem odczytu między potokami jest tabela cen (jedno źródło cen w systemie).
