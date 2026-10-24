from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.router import router
from app.auth_excel import router as excel_auth_router
from app.config.settings import settings
from app.services.scheduler import start_scheduler


# ============================================================
# RATE LIMITER
# ============================================================

# Ograniczanie liczby zapytań na podstawie adresu IP użytkownika.
limiter = Limiter(key_func=get_remote_address)


# ============================================================
# LIFESPAN – URUCHAMIANIE BACKENDU
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uruchomienie schedulera odpowiedzialnego za pobieranie danych.
    start_scheduler()

    yield


# ============================================================
# FASTAPI – GŁÓWNA APLIKACJA
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ============================================================
# RATE LIMITING
# ============================================================

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# ============================================================
# CORS – POŁĄCZENIE Z REACT
# ============================================================

# Zezwalamy na połączenia z lokalnego frontendu React.
# W przyszłości należy dodać adres wdrożonej aplikacji.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERY API
# ============================================================

# Istniejące endpointy Patryka:
# /chat
# /stock/...
# /crypto/...
# /health
app.include_router(router)


# Tymczasowy system logowania z bazą Excel:
# /auth/register
# /auth/login
# /auth/me
# /auth/logout
app.include_router(excel_auth_router)