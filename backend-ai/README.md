# GeoMarket Intelligence - Backend AI (`:8001`)

Mikroserwis wsadowy i analityczny (Batch ETL & AI) w FastAPI spięty z modelem Google Gemini (`gemini-3.5-flash-lite`) oraz trójwarstwowym jeziorem danych Medallion (Delta Lake). Obsługuje potoki makroekonomiczne (FRED), wiadomości rynkowe (RSS / NewsAPI), wydarzenia geopolityczne (GDELT 2.0) oraz moduły analityczne AI i czat.

---

## Jak to odpalić w VS Code (Windows)

Otwórz projekt w VS Code, odpal terminal (`Ctrl + ~`), przejdź do folderu `backend-ai` i wykonaj po kolei:

### 1. Wirtualne środowisko i instalacja

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt