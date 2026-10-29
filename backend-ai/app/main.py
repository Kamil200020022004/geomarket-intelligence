<<<<<<< HEAD
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
=======

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

>>>>>>> 342c8bc2f5e88c4a64fc8af2597c3637556bb1a6
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.router import router
<<<<<<< HEAD
from app.config.settings import settings
from app.services.scheduler import start_scheduler

# Tworzymy limiter, który będzie łapał gości po ich IP
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Odpalamy schedulera w tle zaraz po starcie serwera, żeby dane same się zasysały
=======
from app.auth_excel import router as excel_auth_router
from app.password_reset import router as password_reset_router
from app.config.settings import settings
from app.services.scheduler import start_scheduler


# ============================================================
# RATE LIMITER
# ============================================================

limiter = Limiter(key_func=get_remote_address)


# ============================================================
# LIFESPAN – URUCHAMIANIE BACKENDU
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
>>>>>>> 342c8bc2f5e88c4a64fc8af2597c3637556bb1a6
    start_scheduler()
    yield


<<<<<<< HEAD
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Podpinamy limiter pod całą apkę i ustawiamy ładne łapanie błędów, jak ktoś przesadzi z zapytaniami
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Otwieramy bramy dla Reacta, żeby na frontendzie nie wywalało błędów CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Na razie wpuszczamy wszystkich, ale trzeba to będzie potem uciąć
    allow_credentials=True,
    allow_methods=["*"],  # Puszczamy wszystko jak leci (GET, POST itd.)
    allow_headers=["*"],  # Nagłówki też przepuszczamy bez marudzenia
)

app.include_router(router)
=======
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

# Istniejące endpointy Patryka
app.include_router(router)

# Logowanie i rejestracja przez Excel
app.include_router(excel_auth_router)

# Odzyskiwanie hasła przez e-mail
app.include_router(password_reset_router)
>>>>>>> 342c8bc2f5e88c4a64fc8af2597c3637556bb1a6
