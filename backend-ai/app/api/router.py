from fastapi import APIRouter

from app.api.chat_routes import router as chat_router
from app.api.stock_routes import router as stock_router
from app.api.crypto_routes import router as crypto_router  # Dołączamy moduł krypto

router = APIRouter()


@router.get("/")
def root():
    # Szybki strzał na główny adres – potwierdzenie, że serwer żyje
    return {
        "message": "GeoMarket Intelligence AI działa!"
    }


@router.get("/health")
def health():
    # Sprawdzenie statusu serwera (wymagane przez Kamila do testów)
    return {
        "status": "OK"
    }


# Wpinamy wszystkie routery w jedno miejsce
router.include_router(chat_router)
router.include_router(stock_router)
router.include_router(crypto_router)  # Trasa dla kryptowalut podpięta