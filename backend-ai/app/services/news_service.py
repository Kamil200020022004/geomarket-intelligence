from app.data_sources.news import get_news
from app.models.news import NewsArticle, NewsResponse

def latest_news(symbol: str) -> NewsResponse:
    raw_articles = get_news(symbol)
    
    articles_list = []
    for article in raw_articles:
        news_item = NewsArticle(
            title=article.get("title", "Brak tytułu"),
            source=article.get("source", {}).get("name", "Nieznane źródło"),
            published=article.get("publishedAt", ""),
            url=article.get("url", "")
        )
        articles_list.append(news_item)
        
    return NewsResponse(articles=articles_list)