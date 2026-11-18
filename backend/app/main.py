"""Punkt wejścia aplikacji FastAPI (bramka API GeoMarket Intelligence, port 8000).

Uruchomienie lokalne (z katalogu backend/):
    uvicorn app.main:app --reload --port 8000
Dokumentacja Swagger: http://127.0.0.1:8000/docs
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.api import ai_proxy, auth, favorites, health, market
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging_setup import configure_logging
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.services import ai_gateway


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    # Zamknięcie puli połączeń HTTP do serwisu AI przy wyłączaniu serwera.
    ai_gateway.close_client()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="GeoMarket Intelligence — API",
        description=(
            "Bramka API platformy GeoMarket Intelligence: konta użytkowników, ulubione, "
            "dane rynkowe z potoku strumieniowego oraz pośredniczenie w zapytaniach do serwisu AI. "
            "Analizy mają charakter wyłącznie informacyjny i nie stanowią porady inwestycyjnej."
        ),
        version="0.2.0",
        lifespan=lifespan,
    )

    # CORS: przeglądarka pozwoli frontendowi wołać API tylko z adresów z listy.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    # Limity zapytań (SlowAPI wymaga limitera w app.state).
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(favorites.router)
    app.include_router(market.router)
    app.include_router(ai_proxy.router)
    return app


app = create_app()
