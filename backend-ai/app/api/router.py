from fastapi import APIRouter

from app.api.chat_routes import router as chat_router
from app.api.news_routes import router as news_router
from app.api.stock_routes import router as stock_router
from app.auth_excel import router as auth_router
from app.password_reset import router as password_reset_router

router = APIRouter()


@router.get("/")
def root():
  return {"message": "GeoMarket Intelligence AI działa!"}


@router.get("/health")
def health():
  return {"status": "OK"}


router.include_router(news_router)
router.include_router(chat_router)
router.include_router(stock_router)
router.include_router(auth_router)
router.include_router(password_reset_router)