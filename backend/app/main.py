"""Punkt wejścia aplikacji FastAPI (bramka API GeoMarket Intelligence, port 8000).

Uruchomienie lokalne (z katalogu backend/):
    uvicorn app.main:app --reload --port 8000
Dokumentacja Swagger: http://127.0.0.1:8000/docs
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health
from app.core.config import get_settings
from app.core.errors import register_exception_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    app = FastAPI(
        title="GeoMarket Intelligence — API",
        description=(
            "Bramka API platformy GeoMarket Intelligence: konta użytkowników, ulubione, "
            "dane rynkowe z potoku strumieniowego oraz pośredniczenie w zapytaniach do serwisu AI. "
            "Analizy mają charakter wyłącznie informacyjny i nie stanowią porady inwestycyjnej."
        ),
        version="0.1.0",
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
    app.include_router(health.router)
    return app


app = create_app()
