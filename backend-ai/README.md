# GeoMarket Intelligence - Backend AI

Backend w FastAPI spięty z Gemini. Obsługuje dane giełdowe, makro, krypto i chat AI.

---

## Jak to odpalić w VS Code (Windows)

Otwórz projekt w VS Code, odpal terminal (Ctrl + ~) w folderze backend-ai i lecisz po kolei:

### 1. Wirtualne środowisko i instalacja

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

(Jak PowerShell zablokuje aktywację venv, wpisz najpierw: Set-ExecutionPolicy -ExecutionPolicy Process -Scope Process)

### 2. Plik .env
Plik .env z kluczem masz już wrzucony w katalogu, więc nic nie musisz tworzyć ani zmieniać.

### 3. Start serwera

uvicorn main:app --reload

Aplikacja wstanie pod adresem: http://localhost:8000

---

## Swagger / Dokumentacja

Wszystkie trasy, struktury JSON i testowanie endpointów masz wyklikane pod:
http://localhost:8000/docs

---

## Trasy

* POST /chat - czat z AI (ustawiony limit 15 zapytań/minutę na IP)
* GET /stock/* - dane giełdowe, wykresy pod Plotly, newsy i analizy
* GET /crypto/* - dane i analiza rynku krypto
* GET /health - szybki test czy backend żyje (zwraca status OK)