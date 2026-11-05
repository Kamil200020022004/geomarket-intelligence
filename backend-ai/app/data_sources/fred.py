import requests
from app.config.settings import settings

SERIES_CONFIG = {
    "GDP": {
        "id": "GDP",
        "units": "pc1",  # Percent Change from Year Ago (% r/r)
        "description": "Dynamika PKB USA (% r/r)"
    },
    "INFLATION": {
        "id": "CPIAUCSL",
        "units": "pc1",  # Inflacja konsumencka CPI (% r/r)
        "description": "Inflacja CPI USA (% r/r)"
    },
    "INTEREST_RATE": {
        "id": "FEDFUNDS",
        "units": "lin",  # Poziom stóp procentowych FED (%)
        "description": "Stopa funduszy federalnych FED (%)"
    }
}


def get_macro_indicator(series_key: str, limit: int = 12) -> dict:
    """
    Pobiera najświeższe odczyty z FRED API (sort_order=desc)
    oraz historię obserwacji dla warstw Data Lake.
    """
    cfg = SERIES_CONFIG.get(series_key.upper(), {"id": series_key, "units": "lin"})
    series_id = cfg["id"]
    units = cfg.get("units", "lin")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": settings.FRED_API_KEY.strip() if settings.FRED_API_KEY else "",
        "file_type": "json",
        "sort_order": "desc",  # Pobieramy od najnowszych
        "units": units,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json().get("observations", [])
        
        valid_obs = [obs for obs in data if obs.get("value") and obs.get("value") != "."]
        
        if valid_obs:
            latest = valid_obs[0]  # Przy sort_order=desc indeks 0 to najświeższy odczyt
            val_float = round(float(latest["value"]), 2)
            
            history_list = [
                {"date": o["date"], "value": round(float(o["value"]), 2)}
                for o in reversed(valid_obs)
            ]
            
            return {
                "date": latest["date"],
                "value": str(val_float),
                "history": history_list
            }
    except Exception as e:
        print(f"[FRED API WARNING] Nie udało się pobrać {series_key} ({series_id}): {e}")
        
    return {"date": "N/A", "value": "N/A", "history": []}