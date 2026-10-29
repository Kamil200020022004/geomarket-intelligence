import pandas as pd
from app.data_sources.fred import get_macro_indicator, SERIES_IDS
from google import genai
from google.genai import types
from app.config.settings import settings
from app.services.data_lake_service import (
    save_to_bronze,
    process_macro_to_silver_and_gold
)

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def get_current_macro_summary() -> dict:
    """Pobiera komplet najnowszych wskaźników makro i zapisuje je do Data Lake."""
    macro_indicators = {
        "GDP": get_macro_indicator(SERIES_IDS["GDP"]),
        "CPI_Inflation": get_macro_indicator(SERIES_IDS["INFLATION"]),
        "Fed_Interest_Rate": get_macro_indicator(SERIES_IDS["INTEREST_RATE"]),
    }

    # Zapis do Data Lake (Bronze, Silver, Gold)
    for name, data in macro_indicators.items():
        if data:
            # 1. Bronze (Raw JSON)
            save_to_bronze(source_name="fred", symbol_or_key=name.lower(), raw_data=data)

            # 2. Silver (.parquet) & Gold (summary JSON)
            try:
                df_macro = pd.DataFrame([{"date": data.get("date"), "value": data.get("value")}])
                if "date" in df_macro.columns:
                    df_macro.set_index("date", inplace=True)
                
                process_macro_to_silver_and_gold(indicator_name=name, df_macro=df_macro)
            except Exception as e:
                print(f"⚠️ Błąd zapisu makro {name} do Data Lake: {e}")

    return macro_indicators


def analyze_macro_environment() -> str:
    """Oceniamy otoczenie makroekonomiczne przez Gemini z twardym limitem tokenów."""
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
            max_output_tokens=250,
            temperature=0.2,
        ),
    )
    
    return response.text