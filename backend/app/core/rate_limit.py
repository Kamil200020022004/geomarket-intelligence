"""Ograniczanie liczby zapytań (rate limiting) dla endpointów kont.

Limity liczone są per adres IP klienta, w pamięci procesu. Przy jednej instancji backendu
to wystarcza. Przy wielu instancjach licznik należałoby przenieść np. do Redisa.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings

# Limity (format biblioteki `limits`): ochrona przed zgadywaniem haseł i masową rejestracją.
LOGIN_LIMIT = "10/minute"
REGISTER_LIMIT = "5/minute"
FORGOT_PASSWORD_LIMIT = "5/minute"
RESET_PASSWORD_LIMIT = "10/minute"

limiter = Limiter(key_func=get_remote_address, enabled=get_settings().rate_limit_enabled)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    # Ten sam kształt błędu co w całym API: {"detail": ...}.
    return JSONResponse(
        status_code=429,
        content={"detail": "Zbyt wiele prób. Odczekaj chwilę i spróbuj ponownie."},
    )
