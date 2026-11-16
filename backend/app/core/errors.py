"""Wspólna obsługa błędów.

Wszystkie błędy API mają ten sam kształt co domyślne błędy FastAPI: `{"detail": ...}`.
Dzięki temu frontend obsługuje błędy w jeden sposób, niezależnie od ich źródła.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Szczegóły błędu trafiają tylko do logów serwera, nigdy do odpowiedzi (nie ujawniamy wnętrza systemu).
    logger.exception("Nieobsłużony wyjątek podczas %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Wewnętrzny błąd serwera."})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unhandled_exception_handler)
