"""Trasy pośredniczące do serwisu AI Patryka.

Ścieżki i parametry są takie same jak w `backend-ai`, bo tak wołają je komponenty frontendu
(`ChatDrawer.jsx` → POST /chat, `News.jsx` → /news i /news/analysis, `AIImpactCard.jsx`
i `Dashboard.jsx` → /stock/ai-impact, `LatestNewsCard.jsx` → /stock/news/{symbol}).
Dzięki temu po zmianie adresu na bramkę (port 8000) frontend nie wymaga przeróbek.

Celowo NIE przekazujemy tras z notowaniami (`/stock/{symbol}`, `/stock/history/{symbol}`,
`/stock/overview/table`): jedynym źródłem cen w systemie jest potok strumieniowy (`/api/...`).
"""

from typing import Annotated, Any, Literal
from urllib.parse import quote

from fastapi import APIRouter, Path, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.services import ai_gateway

router = APIRouter(tags=["AI (pośrednictwo do serwisu AI)"])

NewsCategory = Literal["stocks", "macro", "crypto", "geopolitics", "poland", "global"]
# Symbol instrumentu: litery, cyfry, kropka, myślnik, znak równości (np. EURPLN=X), daszek (indeksy).
Symbol = Annotated[str, Path(pattern=r"^[A-Za-z0-9.=^\-]{1,20}$")]

ERRORS = {
    429: {"description": "Przekroczony limit zapytań"},
    503: {"description": "Serwis AI niedostępny i brak zapamiętanej odpowiedzi"},
}

# Czat: każda wiadomość to wywołanie Gemini (bez cache) — limit jak w serwisie AI.
CHAT_LIMIT = "15/minute"
# Trasy GET są obsługiwane głównie z cache (bez kosztu Gemini), więc limit chroni tylko przed
# nadużyciem. Limit 20/min był za niski: komponenty React wołają te same trasy z kilku miejsc,
# a tryb deweloperski (StrictMode) podwaja zapytania — frontend dostawał 429 po ok. 2 minutach.
NEWS_LIMIT = "120/minute"
ANALYSIS_LIMIT = "120/minute"


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _to_response(result: ai_gateway.GatewayResponse) -> JSONResponse:
    return JSONResponse(status_code=result.status_code, content=result.body, headers={"X-Cache": result.cache_status})


def _unavailable() -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": ai_gateway.AI_UNAVAILABLE_MESSAGE})


def _proxy_get(request: Request, path: str, params: dict[str, Any] | None = None, *, ttl: int | None = None,
               refresh: bool = False) -> JSONResponse:
    try:
        result = ai_gateway.get(path, params, ttl_seconds=ttl, bypass_cache=refresh, client_ip=_client_ip(request))
    except ai_gateway.AIServiceUnavailableError:
        return _unavailable()
    return _to_response(result)


# --- Czat ---


class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    symbol: str | None = Field(default=None, max_length=20)
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)


@router.post("/chat", summary="Czat z asystentem AI (bez cache)", responses=ERRORS)
@limiter.limit(CHAT_LIMIT)
def chat(request: Request, body: ChatRequest) -> JSONResponse:
    try:
        result = ai_gateway.post("/chat", body.model_dump(), client_ip=_client_ip(request))
    except ai_gateway.AIServiceUnavailableError:
        return _unavailable()
    return _to_response(result)


# --- Wiadomości ---


@router.get("/news", summary="Wiadomości dla kategorii (cache)", responses=ERRORS)
@limiter.limit(NEWS_LIMIT)
def news(
    request: Request,
    category: NewsCategory = "stocks",
    limit: Annotated[int, Query(ge=1, le=50)] = 25,
    refresh: bool = False,
) -> JSONResponse:
    params = {"category": category, "limit": limit, "refresh": "true" if refresh else None}
    return _proxy_get(request, "/news", params, ttl=get_settings().news_cache_ttl_seconds, refresh=refresh)


@router.get("/news/analysis", summary="Analiza AI wiadomości dla kategorii (cache)", responses=ERRORS)
@limiter.limit(ANALYSIS_LIMIT)
def news_analysis(request: Request, category: NewsCategory = "stocks", refresh: bool = False) -> JSONResponse:
    params = {"category": category, "refresh": "true" if refresh else None}
    return _proxy_get(request, "/news/analysis", params, refresh=refresh)


# --- Analizy AI ---


@router.get("/stock/ai-impact", summary="Karta AI Impact (cache)", responses=ERRORS)
@limiter.limit(ANALYSIS_LIMIT)
def ai_impact(request: Request) -> JSONResponse:
    return _proxy_get(request, "/stock/ai-impact")


@router.get("/stock/macro/analysis", summary="Analiza AI sytuacji makroekonomicznej (cache)", responses=ERRORS)
@limiter.limit(ANALYSIS_LIMIT)
def macro_analysis(request: Request) -> JSONResponse:
    return _proxy_get(request, "/stock/macro/analysis")


@router.get("/stock/macro/raw", summary="Wskaźniki makro z FRED (cache)", responses=ERRORS)
@limiter.limit(ANALYSIS_LIMIT)
def macro_raw(request: Request) -> JSONResponse:
    return _proxy_get(request, "/stock/macro/raw")


@router.get("/stock/analyze/{symbol}", summary="Analiza AI spółki (cache)", responses=ERRORS)
@limiter.limit(ANALYSIS_LIMIT)
def analyze(request: Request, symbol: Symbol) -> JSONResponse:
    return _proxy_get(request, f"/stock/analyze/{quote(symbol, safe='')}")


@router.get("/stock/news/{symbol}/sentiment", summary="Sentyment wiadomości o spółce (cache)", responses=ERRORS)
@limiter.limit(ANALYSIS_LIMIT)
def news_sentiment(request: Request, symbol: Symbol) -> JSONResponse:
    return _proxy_get(request, f"/stock/news/{quote(symbol, safe='')}/sentiment")


@router.get("/stock/report/{symbol}", summary="Raport AI o spółce (cache)", responses=ERRORS)
@limiter.limit(ANALYSIS_LIMIT)
def report(request: Request, symbol: Symbol) -> JSONResponse:
    return _proxy_get(request, f"/stock/report/{quote(symbol, safe='')}")


@router.get("/stock/news/{symbol}", summary="Wiadomości o spółce (cache)", responses=ERRORS)
@limiter.limit(NEWS_LIMIT)
def stock_news(request: Request, symbol: Symbol) -> JSONResponse:
    return _proxy_get(request, f"/stock/news/{quote(symbol, safe='')}", ttl=get_settings().news_cache_ttl_seconds)


@router.get("/stock/gdelt/events", summary="Wydarzenia geopolityczne GDELT (cache)", responses=ERRORS)
@limiter.limit(NEWS_LIMIT)
def gdelt_events(request: Request) -> JSONResponse:
    return _proxy_get(request, "/stock/gdelt/events", ttl=get_settings().news_cache_ttl_seconds)
