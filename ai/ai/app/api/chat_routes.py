from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_message
from app.services.finance_service import get_history

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    return process_message(request.message)

@router.get("/history/{symbol}")
def history(symbol: str):
    return get_history(symbol)