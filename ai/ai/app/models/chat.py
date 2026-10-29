from pydantic import BaseModel

# Definicja danych wejściowych (to, co aplikacja odbiera z zewnątrz)
class ChatRequest(BaseModel):
    message: str

# Definicja danych wyjściowych (to, co aplikacja odsyła jako wynik)
class ChatResponse(BaseModel):
    response: str