from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.router import router
from app.config.settings import settings
from app.services.scheduler import start_scheduler

# Tworzymy limiter, który będzie łapał gości po ich IP
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Odpalamy schedulera w tle zaraz po starcie serwera, żeby dane same się zasysały
    start_scheduler()
    yield


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