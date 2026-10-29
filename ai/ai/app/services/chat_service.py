from google import genai

from app.ai.system_prompt import SYSTEM_PROMPT
from app.config.settings import settings
from app.models.chat import ChatResponse

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def process_message(message: str) -> ChatResponse:
    full_prompt = f"""
{SYSTEM_PROMPT}

Odpowiedz maksymalnie w 300 słowach.

Wiadomość użytkownika:
{message}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=full_prompt,
    )

    return ChatResponse(
        response=response.text
    )