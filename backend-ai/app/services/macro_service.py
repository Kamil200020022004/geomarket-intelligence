from google import genai
from google.genai import types
import pandas as pd
from app.config.settings import settings
from app.data_sources.fred import get_macro_indicator
from app.services.data_lake_service import (
    process_macro_to_silver_and_gold,
    save_to_bronze,
)

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def get_current_macro_summary() -> dict:
  """Pobiera komplet najnowszych wskaźników makro (USA, Polska, Strefa Euro) z historią i zasila Data Lake."""
  indicators = {
      "GDP": get_macro_indicator("GDP", limit=12),
      "CPI_Inflation": get_macro_indicator("INFLATION", limit=12),
      "Fed_Interest_Rate": get_macro_indicator("INTEREST_RATE", limit=12),
      "CPI_PL": get_macro_indicator("CPI_PL", limit=12),
      "RATES_PL": get_macro_indicator("RATES_PL", limit=12),
      "GDP_PL": get_macro_indicator("GDP_PL", limit=12),
      "CPI_EU": get_macro_indicator("CPI_EU", limit=12),
      "RATES_EU": get_macro_indicator("RATES_EU", limit=12),
      "GDP_EU": get_macro_indicator("GDP_EU", limit=12),
  }

  for name, data in indicators.items():
    if data and data.get("value") != "N/A":
      save_to_bronze(
          source_name="fred", symbol_or_key=name.lower(), raw_data=data
      )

      try:
        history = data.get("history", [])
        if history:
          df_macro = pd.DataFrame(history)
          df_macro.set_index("date", inplace=True)
        else:
          df_macro = pd.DataFrame([{
              "date": data.get("date"),
              "value": float(data.get("value", 0)),
          }])
          df_macro.set_index("date", inplace=True)

        process_macro_to_silver_and_gold(indicator_name=name, df_macro=df_macro)
      except Exception as e:
        print(f"[Data Lake Warning] Błąd zapisu makro {name}: {e}")

  return {
      key: {
          "date": val["date"],
          "value": val["value"],
          "history": val.get("history", []),
      }
      for key, val in indicators.items()
  }


def analyze_macro_environment() -> str:
  """Ocenia otoczenie makroekonomiczne (USA, Polska, Strefa Euro) przez model Gemini."""
  macro_data = get_current_macro_summary()

  prompt = f"""
    Na podstawie poniższych najnowszych wskaźników makroekonomicznych z bazy FRED:
    - USA: Dynamika PKB {macro_data['GDP']['value']}% r/r, Inflacja CPI {macro_data['CPI_Inflation']['value']}% r/r, Stopa FED {macro_data['Fed_Interest_Rate']['value']}%
    - Polska: Dynamika PKB {macro_data['GDP_PL']['value']}% r/r, Inflacja CPI {macro_data['CPI_PL']['value']}% r/r, Stopa proc. {macro_data['RATES_PL']['value']}%
    - Strefa Euro: Dynamika PKB {macro_data['GDP_EU']['value']}% r/r, Inflacja HICP {macro_data['CPI_EU']['value']}% r/r, Stopa EBC {macro_data['RATES_EU']['value']}%
    
    Krótko (maksymalnie 150 słów) oceń ogólny stan gospodarki pod kątem rynków finansowych.
    Wymień dokładnie 2 szanse i 2 zagrożenia dla stabilności wycen. Odpowiadaj po polsku.
    """

  disclaimer = (
      "\n\n---\n*Zastrzeżenie: Analiza makroekonomiczna ma charakter"
      " informacyjny i nie stanowi rekomendacji doradczej.*"
  )

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
    return (
        f"Otoczenie makroekonomiczne (USA: PKB {macro_data['GDP']['value']}%,"
        f" CPI {macro_data['CPI_Inflation']['value']}%, FED"
        f" {macro_data['Fed_Interest_Rate']['value']}% | PL: CPI"
        f" {macro_data['CPI_PL']['value']}% | UE: CPI"
        f" {macro_data['CPI_EU']['value']}%): Bieżące odczyty wskazują na"
        " umiarkowane tempo wzrostu gospodarczego przy podwyższonych stopach"
        " procentowych. Szanse: stabilizacja presji cenowej i przewidywalność"
        " polityki banków centralnych. Zagrożenia: koszty obsługi długu oraz"
        " presja na marże spółek."
        + disclaimer
    )