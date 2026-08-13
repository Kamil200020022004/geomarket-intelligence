from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str = Field(..., description="Rola: 'user' lub 'model'")
    content: str = Field(..., description="Treść wiadomości")


class ChatRequest(BaseModel):
    message: str = Field(..., description="Treść wiadomości / zapytania")
    symbol: Optional[str] = Field(None, description="Opcjonalny symbol spółki jako kontekst")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Historia konwersacji")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Odpowiedź wygenerowana przez model AI")