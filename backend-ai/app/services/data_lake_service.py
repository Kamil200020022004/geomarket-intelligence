import json
import os
from datetime import datetime, date
import pandas as pd

DATA_DIR = "data"


def _json_serializer(obj):
    """Pomocniczy konwerter typów nieobsługiwanych standardowo przez bibliotekę json."""
    if isinstance(obj, (datetime, date, pd.Timestamp)):
        return obj.isoformat()
    return str(obj)


def save_to_bronze(source_name: str, symbol_or_key: str, raw_data: dict) -> str:
    """Warstwa Bronze: Zapis surowej odpowiedzi z API w formacie JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join(DATA_DIR, "bronze", source_name)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{symbol_or_key}_{timestamp}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2, default=_json_serializer)

    return file_path


def process_bronze_to_silver_stock(symbol: str, df_stock: pd.DataFrame) -> str:
    """Warstwa Silver: Oczyszczanie notowań giełdowych i zapis do Parquet."""
    folder_path = os.path.join(DATA_DIR, "silver", "stocks")
    os.makedirs(folder_path, exist_ok=True)

    df_clean = df_stock.dropna().copy()
    df_clean["symbol"] = symbol.upper()
    df_clean["updated_at"] = datetime.now()

    file_path = os.path.join(folder_path, f"{symbol.upper()}.parquet")
    df_clean.to_parquet(file_path, index=True)

    return file_path


def generate_gold_stock_summary(symbol: str) -> dict:
    """Warstwa Gold: Tworzenie gotowych agregatów giełdowych dla modeli AI."""
    silver_path = os.path.join(DATA_DIR, "silver", "stocks", f"{symbol.upper()}.parquet")

    if not os.path.exists(silver_path):
        return {}

    df = pd.read_parquet(silver_path)

    gold_summary = {
        "symbol": symbol.upper(),
        "latest_close": float(df["Close"].iloc[-1]) if "Close" in df else None,
        "avg_close_30d": float(df["Close"].tail(30).mean()) if "Close" in df else None,
        "max_high_30d": float(df["High"].tail(30).max()) if "High" in df else None,
        "min_low_30d": float(df["Low"].tail(30).min()) if "Low" in df else None,
        "last_updated": datetime.now().isoformat()
    }

    gold_folder = os.path.join(DATA_DIR, "gold", "stocks")
    os.makedirs(gold_folder, exist_ok=True)

    with open(os.path.join(gold_folder, f"{symbol.upper()}_summary.json"), "w", encoding="utf-8") as f:
        json.dump(gold_summary, f, indent=2, default=_json_serializer)

    return gold_summary


def process_macro_to_silver_and_gold(indicator_name: str, df_macro: pd.DataFrame) -> dict:
    """Warstwa Silver & Gold dla danych makroekonomicznych (FRED)."""
    if df_macro.empty:
        return {}

    # 1. Warstwa Silver: Zapis do Parquet
    silver_folder = os.path.join(DATA_DIR, "silver", "macro")
    os.makedirs(silver_folder, exist_ok=True)

    df_clean = df_macro.dropna().copy()
    df_clean["updated_at"] = datetime.now()

    silver_path = os.path.join(silver_folder, f"{indicator_name.lower()}.parquet")
    df_clean.to_parquet(silver_path, index=True)

    # 2. Warstwa Gold: Zapis zagregowanego podsumowania JSON
    latest_val = float(df_clean.iloc[-1, 0]) if len(df_clean) > 0 else None
    prev_val = float(df_clean.iloc[-2, 0]) if len(df_clean) > 1 else None

    gold_summary = {
        "indicator": indicator_name.upper(),
        "latest_value": latest_val,
        "previous_value": prev_val,
        "change": round(latest_val - prev_val, 4) if (latest_val is not None and prev_val is not None) else 0.0,
        "last_updated": datetime.now().isoformat()
    }

    gold_folder = os.path.join(DATA_DIR, "gold", "macro")
    os.makedirs(gold_folder, exist_ok=True)

    with open(os.path.join(gold_folder, f"{indicator_name.lower()}_summary.json"), "w", encoding="utf-8") as f:
        json.dump(gold_summary, f, indent=2, default=_json_serializer)

    return gold_summary
def save_news_to_silver(category: str, articles: list[dict]) -> str:
    """Warstwa Silver: Przechowywanie zdeduplikowanych i ustrukturyzowanych newsów."""
    folder_path = os.path.join(DATA_DIR, "silver", "news")
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{category.lower()}.json")

    existing_articles = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_articles = json.load(f)
        except Exception:
            existing_articles = []

    # Deduplikacja po unikalnym URL
    seen_urls = {a.get("url") for a in articles if a.get("url")}
    combined = list(articles)
    for old_art in existing_articles:
        if old_art.get("url") not in seen_urls:
            combined.append(old_art)
            seen_urls.add(old_art.get("url"))

    # Sortowanie od najnowszych i zachowanie max 50 artykułów
    combined.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    combined = combined[:50]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2, default=_json_serializer)

    return file_path

def get_news_from_silver(category: str, limit: int = 30) -> list[dict]:
    """Odczyt oczyszczonych wiadomości z warstwy Silver."""
    file_path = os.path.join(DATA_DIR, "silver", "news", f"{category.lower()}.json")
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[:limit]
    except Exception:
        return []


def save_news_gold_analysis(category: str, analysis_data: dict) -> str:
    """Warstwa Gold: Przechowywanie analizy AI dla wiadomości z danej kategorii."""
    folder_path = os.path.join(DATA_DIR, "gold", "news")
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{category.lower()}_analysis.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=_json_serializer)

    return file_path


def get_news_gold_analysis(category: str) -> dict | None:
    """Odczyt gotowej analizy AI z warstwy Gold."""
    file_path = os.path.join(DATA_DIR, "gold", "news", f"{category.lower()}_analysis.json")
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None