from datetime import date, datetime
import json
import os
from deltalake import DeltaTable, write_deltalake
import pandas as pd

DATA_DIR = "data"
IS_VERCEL = bool(os.getenv("VERCEL"))


def _json_serializer(obj):
  if isinstance(obj, (datetime, date, pd.Timestamp)):
    return obj.isoformat()
  return str(obj)


# =========================================================
# WARSTWA BRONZE (Surowe odpowiedzi API w formacie JSON)
# =========================================================


def save_to_bronze(source_name: str, symbol_or_key: str, raw_data: dict) -> str:
  if IS_VERCEL:
    return ""
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  folder_path = os.path.join(DATA_DIR, "bronze", source_name)
  os.makedirs(folder_path, exist_ok=True)

  file_path = os.path.join(folder_path, f"{symbol_or_key}_{timestamp}.json")
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(raw_data, f, ensure_ascii=False, indent=2, default=_json_serializer)

  return file_path


# =========================================================
# POTOK MAKRO: FRED -> SILVER (DELTA LAKE TABLE) & GOLD
# =========================================================


def process_macro_to_silver_and_gold(
    indicator_name: str, df_macro: pd.DataFrame
) -> dict:
  if df_macro.empty:
    return {}

  df_clean = df_macro.dropna().copy()
  if "date" not in df_clean.columns:
    df_clean = df_clean.reset_index()
  df_clean["updated_at"] = datetime.now().isoformat()

  if not IS_VERCEL:
    silver_table_path = os.path.join(
        DATA_DIR, "silver", "macro", indicator_name.lower()
    )
    os.makedirs(os.path.dirname(silver_table_path), exist_ok=True)
    write_deltalake(silver_table_path, df_clean, mode="overwrite")

  val_col = [
      c for c in df_clean.columns if c not in ["date", "index", "updated_at"]
  ][0]
  latest_val = float(df_clean[val_col].iloc[-1]) if len(df_clean) > 0 else None
  prev_val = float(df_clean[val_col].iloc[-2]) if len(df_clean) > 1 else None

  gold_summary = {
      "indicator": indicator_name.upper(),
      "latest_value": latest_val,
      "previous_value": prev_val,
      "change": (
          round(latest_val - prev_val, 4)
          if (latest_val is not None and prev_val is not None)
          else 0.0
      ),
      "last_updated": datetime.now().isoformat(),
  }

  if not IS_VERCEL:
    gold_folder = os.path.join(DATA_DIR, "gold", "macro")
    os.makedirs(gold_folder, exist_ok=True)
    with open(
        os.path.join(gold_folder, f"{indicator_name.lower()}_summary.json"),
        "w",
        encoding="utf-8",
    ) as f:
      json.dump(gold_summary, f, indent=2, default=_json_serializer)

  return gold_summary


# =========================================================
# POTOK GEOPOLITYCZNY: GDELT -> BRONZE & SILVER (DELTA LAKE)
# =========================================================


def save_gdelt_to_lakehouse(events: list[dict]) -> str:
  if not events or IS_VERCEL:
    return ""

  save_to_bronze(
      source_name="gdelt",
      symbol_or_key="geopolitics_events",
      raw_data={"articles": events},
  )

  folder_path = os.path.join(DATA_DIR, "silver", "gdelt", "events_delta")
  os.makedirs(os.path.dirname(folder_path), exist_ok=True)

  df_events = pd.DataFrame(events)
  df_events = df_events.astype(str)
  df_events["fetched_at"] = datetime.now().isoformat()

  write_deltalake(folder_path, df_events, mode="overwrite")
  return folder_path


def get_gdelt_from_silver() -> list[dict]:
  """Odczyt oczyszczonych wydarzeń GDELT z tabeli Delta Lake."""
  folder_path = os.path.join(DATA_DIR, "silver", "gdelt", "events_delta")
  if not os.path.exists(folder_path):
    return []
  try:
    dt = DeltaTable(folder_path)
    return dt.to_pandas().to_dict(orient="records")
  except Exception:
    return []


# =========================================================
# ODCZYT NOTOWAŃ Z WARSTWY SILVER (WSPÓLNY LAKEHOUSE)
# =========================================================


def get_stock_from_silver(symbol: str) -> dict | None:
  """Odczytuje najnowsze notowanie spółki z tabeli Delta Lake w warstwie Silver."""
  candidate_paths = [
      os.path.join(DATA_DIR, "silver", "stocks", symbol.lower()),
      os.path.join(DATA_DIR, "silver", "market", "stocks"),
      os.path.join(DATA_DIR, "silver", "stocks"),
  ]
  for path in candidate_paths:
    if os.path.exists(path):
      try:
        dt = DeltaTable(path)
        df = dt.to_pandas()
        if "symbol" in df.columns:
          df = df[df["symbol"].astype(str).str.upper() == symbol.upper()]
        if not df.empty:
          latest = df.iloc[-1].to_dict()
          return latest
      except Exception:
        continue
  return None


# =========================================================
# POTOK WIADOMOŚCI: RSS / NEWSAPI -> SILVER & GOLD (AI)
# =========================================================


def save_news_to_silver(category: str, articles: list[dict]) -> str:
  if IS_VERCEL:
    return ""
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

  seen_urls = {a.get("url") for a in articles if a.get("url")}
  combined = list(articles)
  for old_art in existing_articles:
    if old_art.get("url") not in seen_urls:
      combined.append(old_art)
      seen_urls.add(old_art.get("url"))

  combined.sort(key=lambda x: x.get("published_at", ""), reverse=True)
  combined = combined[:50]

  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(
        combined, f, ensure_ascii=False, indent=2, default=_json_serializer
    )

  return file_path


def get_news_from_silver(category: str, limit: int = 30) -> list[dict]:
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
  if IS_VERCEL:
    return ""
  folder_path = os.path.join(DATA_DIR, "gold", "news")
  os.makedirs(folder_path, exist_ok=True)
  file_path = os.path.join(folder_path, f"{category.lower()}_analysis.json")

  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(
        analysis_data, f, ensure_ascii=False, indent=2, default=_json_serializer
    )

  return file_path


def get_news_gold_analysis(category: str) -> dict | None:
  file_path = os.path.join(
      DATA_DIR, "gold", "news", f"{category.lower()}_analysis.json"
  )
  if not os.path.exists(file_path):
    return None
  try:
    with open(file_path, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    return None