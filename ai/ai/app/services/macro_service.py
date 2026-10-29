from app.data_sources.fred import get_macro_indicator, SERIES_IDS
from google import genai
from google.genai import types
from app.config.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_current_macro_summary() -> dict:
    """Pobiera komplet najnowszych wskaźników makro."""
    return {
        "GDP": get_macro_indicator(SERIES_IDS["GDP"]),
        "CPI_Inflation": get_macro_indicator(SERIES_IDS["INFLATION"]),
        "Fed_Interest_Rate": get_macro_indicator(SERIES_IDS["INTEREST_RATE"]),
    }

def analyze_macro_environment() -> str:
    """Oceniamy otoczenie makroekonomiczne przez Gemini z twardym limitom tokenów."""
    macro_data = get_current_macro_summary()
    
    prompt = f"""
    Na podstawie poniższych najnowszych danych makroekonomicznych USA:
    - PKB (GDP): {macro_data['GDP']['value']} (z dnia {macro_data['GDP']['date']})
    - Inflacja (CPI): {macro_data['CPI_Inflation']['value']} (z dnia {macro_data['CPI_Inflation']['date']})
    - Stopa FED: {macro_data['Fed_Interest_Rate']['value']}% (z dnia {macro_data['Fed_Interest_Rate']['date']})
    
    Krótko (max 150 słów) oceń ogólny stan gospodarki dla inwestorów giełdowych. 
    Wymień 2 szanse i 2 zagrożenia. Odpowiadaj po polsku.
    """
    
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=250,  # Bardzo niski limit = oszczędność tokenów
            temperature=0.2,
        ),
    )
    
    return response.text