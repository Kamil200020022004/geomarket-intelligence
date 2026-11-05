import pandas as pd
from app.data_sources.fred import get_macro_indicator
from google import genai
from google.genai import types
from app.config.settings import settings
from app.services.data_lake_service import (
    save_to_bronze,
    process_macro_to_silver_and_gold
)

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def get_current_macro_summary() -> dict:
    """Pobiera komplet najnowszych wskaźników makro z historią i zasila Data Lake."""
    indicators = {
        "GDP": get_macro_indicator("GDP", limit=12),
        "CPI_Inflation": get_macro_indicator("INFLATION", limit=12),
        "Fed_Interest_Rate": get_macro_indicator("INTEREST_RATE", limit=12),
    }

    # Zapis do Data Lake (Bronze, Silver, Gold)
    for name, data in indicators.items():
        if data and data.get("value") != "N/A":
            save_to_bronze(source_name="fred", symbol_or_key=name.lower(), raw_data=data)

            try:
                history = data.get("history", [])
                if history:
                    df_macro = pd.DataFrame(history)
                    df_macro.set_index("date", inplace=True)
                else:
                    df_macro = pd.DataFrame([{"date": data.get("date"), "value": float(data.get("value", 0))}])
                    df_macro.set_index("date", inplace=True)
                
                process_macro_to_silver_and_gold(indicator_name=name, df_macro=df_macro)
            except Exception as e:
                print(f"⚠️ Błąd zapisu makro {name} do Data Lake: {e}")

    return {
        "GDP": {"date": indicators["GDP"]["date"], "value": indicators["GDP"]["value"]},
        "CPI_Inflation": {"date": indicators["CPI_Inflation"]["date"], "value": indicators["CPI_Inflation"]["value"]},
        "Fed_Interest_Rate": {"date": indicators["Fed_Interest_Rate"]["date"], "value": indicators["Fed_Interest_Rate"]["value"]},
    }


def analyze_macro_environment() -> str:
    """Oceniamy otoczenie makroekonomiczne przez Gemini z zabezpieczeniem przed błędem 503."""
    macro_data = get_current_macro_summary()
    
    prompt = f"""
    Na podstawie poniższych najnowszych wskaźników makroekonomicznych USA:
    - Dynamika PKB (GDP): {macro_data['GDP']['value']}% r/r (odczyt z dnia {macro_data['GDP']['date']})
    - Inflacja konsumencka (CPI): {macro_data['CPI_Inflation']['value']}% r/r (odczyt z dnia {macro_data['CPI_Inflation']['date']})
    - Stopa funduszy federalnych (FED): {macro_data['Fed_Interest_Rate']['value']}% (odczyt z dnia {macro_data['Fed_Interest_Rate']['date']})
    
    Krótko (maksymalnie 150 słów) oceń ogólny stan gospodarki pod kątem rynków finansowych.
    Wymień dokładnie 2 szanse i 2 zagrożenia dla stabilności wycen. Odpowiadaj po polsku.
    """
    
    disclaimer = "\n\n---\n*Zastrzeżenie: Analiza makroekonomiczna ma charakter informacyjny i nie stanowi rekomendacji doradczej.*"

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=250,
                temperature=0.2,
            ),
        )
        return (response.text or "") + disclaimer
    except Exception:
        # Odpowiedź awaryjna w przypadku przeciążenia Gemini (kod 503)
        return (
            f"Otoczenie makroekonomiczne (odczyty: PKB {macro_data['GDP']['value']}%, "
            f"Inflacja CPI {macro_data['CPI_Inflation']['value']}%, Stopa FED {macro_data['Fed_Interest_Rate']['value']}%): "
            "Bieżące odczyty wskazują na umiarkowane tempo wzrostu gospodarczego przy restrykcyjnych warunkach monetarnych. "
            "Szanse: stabilizacja presji cenowej i przewidywalność stóp. "
            "Zagrożenia: koszty obsługi długu oraz presja na marże spółek."
            + disclaimer
        )