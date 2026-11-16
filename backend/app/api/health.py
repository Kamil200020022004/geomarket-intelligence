"""Endpointy stanu serwisu, używane przez Docker Compose i monitoring.

- `/health` (liveness): proces działa i odpowiada; nie sprawdza zależności.
- `/health/ready` (readiness): serwis jest gotowy do obsługi ruchu, czyli baza danych odpowiada.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.session import check_database

router = APIRouter(tags=["health"])


@router.get("/health", summary="Czy proces działa")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/health/ready",
    summary="Czy serwis jest gotowy (baza danych dostępna)",
    responses={503: {"description": "Baza danych niedostępna"}},
)
def ready() -> JSONResponse:
    database_ok = check_database()
    body = {
        "status": "ok" if database_ok else "unavailable",
        "database": "ok" if database_ok else "unavailable",
    }
    return JSONResponse(status_code=200 if database_ok else 503, content=body)
