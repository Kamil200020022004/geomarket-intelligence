import requests
from app.config.settings import settings

SERIES_IDS = {
    "GDP": "GDP",
    "INFLATION": "CPIAUCSL",
    "INTEREST_RATE": "FEDFUNDS"
}

def get_macro_indicator(series_id: str) -> dict:
    url = "https://api.stlouisfed.org/fred/series/observations"
    
    params = {
        "series_id": series_id,
        "api_key": settings.FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json().get("observations", [])
        if data:
            return {
                "date": data[0]["date"],
                "value": data[0]["value"]
            }
    except Exception as e:
        # Jeśli FRED zwróci błąd 400 (np. nieaktywny klucz), przechwytujemy go!
        print(f"[FRED API WARNING] Nie udało się pobrać {series_id}: {e}")
        
    return {"date": "N/A", "value": "N/A"}