import logging
from typing import Any, Dict, List
import requests

logger = logging.getLogger("gdelt_source")
GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

def fetch_gdelt_events(query: str = "geopolitics", max_records: int = 15) -> List[Dict[str, Any]]:
    """
    Pobiera najnowsze globalne wydarzenia i artykuły z darmowego API GDELT 2.0.
    """
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": str(max_records),
        "format": "json",
        "sort": "date_desc"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GeoMarketPlatform/1.0"
    }
    try:
        # Zwiększamy timeout do 25 sekund na wypadek wolniejszej odpowiedzi serwerów GDELT
        response = requests.get(GDELT_API_URL, params=params, headers=headers, timeout=25)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        logger.info(f"Pobrano {len(articles)} rekordów z GDELT.")
        return articles
    except Exception as e:
        logger.error(f"Błąd podczas odpytywania GDELT API: {e}")
        return []