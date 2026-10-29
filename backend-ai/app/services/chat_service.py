import re
from google import genai
from google.genai import types
from app.ai.system_prompt import SYSTEM_PROMPT
from app.config.settings import settings
from app.models.chat import ChatRequest, ChatResponse
from app.services.finance_service import get_stock

client = genai.Client(api_key=settings.GEMINI_API_KEY)

TICKER_MAP = {
    "apple": "AAPL",
    "aapl": "AAPL",
    "samsung": "SSNLF",  # Samsung Electronics Co., Ltd. (OTC)
    "microsoft": "MSFT",
    "msft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "googl": "GOOGL",
    "tesla": "TSLA",
    "tsla": "TSLA",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "amazon": "AMZN",
    "amzn": "AMZN",
    "meta": "META",
    "orlen": "PKN.WA",
}


def _detect_symbols(message: str, fallback_symbol: str | None) -> list[str]:
    symbols = []
    if fallback_symbol and fallback_symbol.lower() not in ["string", "none", ""]:
        symbols.append(fallback_symbol.upper())

    words = re.findall(r"\b[a-zA-Z0-9.-]+\b", message.lower())
    for word in words:
        if word in TICKER_MAP and TICKER_MAP[word] not in symbols:
            symbols.append(TICKER_MAP[word])

    return symbols[:2]


def process_message(request: ChatRequest) -> ChatResponse:
    target_symbols = _detect_symbols(request.message, request.symbol)

    market_context = ""
    for sym in target_symbols:
        try:
            stock_data = get_stock(sym)
            data_dict = stock_data.model_dump() if hasattr(stock_data, "model_dump") else dict(stock_data)
            market_context += f"- Dane dla {sym}: {data_dict}\n"
        except Exception:
            pass

    custom_system_instruction = (
        f"{SYSTEM_PROMPT}\n\n"
        "ŚCISŁE ZASADY ODPOWIEDZI:\n"
        "1. ZWIĘZŁOŚĆ: Odpowiedź ma mieć maksymalnie 3-4 zdania lub zwartą listę punktową.\n"
        "2. ZAKAZ ODSYŁANIA: Nigdy nie pisz 'wejdź w zakładkę Giełda/Newsy' ani nie tłumacz struktury menu.\n"
        "3. INTEGRALNOŚĆ DANYCH: Jeśli poniżej podano aktualne dane z systemu, koniecznie na nich oprzyj liczby i wyceny. "
        "Jeśli liczb nie ma w kontekście, nie zmyślaj kursów, lecz przedstaw zwięzłe podsumowanie profilu biznesowego spółek.\n"
    )

    if market_context:
        custom_system_instruction += f"\nAKTUALNE DANE Z SYSTEMU DLA SPÓŁEK:\n{market_context}\n"

    contents = []
    if request.history:
        for msg in request.history:
            contents.append(
                types.Content(
                    role=msg.role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=request.message)]
        )
    )

    # Bezpieczne wywołanie z obsługą błędu 503 / przeciążenia Gemini
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=custom_system_instruction,
                max_output_tokens=300,
                temperature=0.2,
            )
        )
        answer = response.text
    except Exception:
        if market_context:
            answer = (
                "Moduł analityczny AI jest chwilowo przeciążony, lecz oto najświeższe dane rynkowe z systemu:\n"
                f"{market_context}\nSpróbuj zadać pytanie ponownie za chwilę."
            )
        else:
            answer = "Serwery analityczne AI są w tej chwili mocno obciążone. Spróbuj zadać pytanie za chwilę."

    return ChatResponse(response=answer)