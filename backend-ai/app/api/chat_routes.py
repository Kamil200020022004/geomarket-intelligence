from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_message
from app.services.finance_service import get_history

# Łapiemy IP usera do pilnowania limitów
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit("15/minute")  # Limit ustawiony na sztywno: max 15 strzałów na minutę z jednego IP
def chat(request: Request, chat_data: ChatRequest):
    # 'request: Request' musi tu być, żeby limiter wiedział, kogo liczyć
    # 'chat_data' to treść wiadomości, którą wysyła frontend
    return process_message(chat_data)


@router.get("/history/{symbol}")
def history(symbol: str):
    # Zwykłe pobieranie historii – to nie żre tokenów z Gemini, więc bez limitu
    return get_history(symbol)