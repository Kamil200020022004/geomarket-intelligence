from google import genai
from google.genai import types

from app.ai.system_prompt import SYSTEM_PROMPT
from app.config.settings import settings
from app.models.chat import ChatRequest, ChatResponse

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def process_message(request: ChatRequest) -> ChatResponse:
    # 1. Konstrukcja instrukcji systemowej
    custom_system_instruction = f"{SYSTEM_PROMPT}\nOdpowiedz maksymalnie w 300 słowach."
    if request.symbol:
        custom_system_instruction += f"\nAktualnie rozmawiasz z użytkownikiem w kontekście spółki/aktywa: {request.symbol}."

    # 2. Przygotowanie historii konwersacji
    contents = []
    if request.history:
        for msg in request.history:
            contents.append(
                types.Content(
                    role=msg.role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

    # 3. Dodanie aktualnej wiadomości użytkownika
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=request.message)]
        )
    )

    # 4. Wywołanie Gemini
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=custom_system_instruction,
            max_output_tokens=350,
            temperature=0.3,
        )
    )

    return ChatResponse(response=response.text)