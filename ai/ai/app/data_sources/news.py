import requests
from app.config.settings import settings

def get_news(query: str, page_size: int = 5):
    url = "https://newsapi.org/v2/everything"
    
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": settings.NEWS_API_KEY, 
    }
    
    # Dodajemy timeout=5 (maksymalnie 5 sekund oczekiwania)
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    
    return response.json().get("articles", [])