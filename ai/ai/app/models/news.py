from pydantic import BaseModel, Field
from typing import List

# --- PODSTAWOWE MODEL-E DLA NEWSÓW ---
class NewsArticle(BaseModel):
    title: str
    source: str
    published: str
    url: str

class NewsResponse(BaseModel):
    articles: List[NewsArticle]


# --- MODEL-E DLA ANALIZY SENTYMENTU GEMINI ---
class SentimentResult(BaseModel):
    title: str
    sentiment: str = Field(description="Ocena: Pozytywny, Neutralny lub Negatywny")
    justification: str = Field(description="Max 1 zdanie uzasadnienia")

class NewsSentimentResponse(BaseModel):
    symbol: str
    overall_sentiment: str = Field(description="Ogólny sentyment: Pozytywny, Neutralny lub Negatywny")
    analysis: List[SentimentResult]