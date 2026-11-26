from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
from deltalake import DeltaTable, write_deltalake
import pandas as pd
from app.config.settings import settings

# Katalog główny z LAKEHOUSE_ROOT (domyślnie <repo>/data/lakehouse, w Dockerze /data/lakehouse)
DATA_DIR = str(Path(settings.LAKEHOUSE_ROOT).resolve())
IS_VERCEL = bool(os.getenv("VERCEL"))


def _utc_now() -> pd.Timestamp:
    """Zwraca aktualny znacznik czasu UTC zgodny z pa.timestamp('us', tz='UTC')."""
    return pd.Timestamp.now(tz="UTC").floor("us")


def _json_serializer(obj):
    if isinstance(obj, (datetime, date, pd.Timestamp)):
        return obj.isoformat()
    return str(obj)


# =========================================================
# WARSTWA BRONZE (Surowe odpowiedzi API w formacie JSON)
# =========================================================


def save_to_bronze(source_name: str, symbol_or_key: str, raw_data: dict | list) -> str:
    if IS_VERCEL:
        return ""
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y%m%d_%H%M%S")
    clean_source = source_name.strip().lower()
    clean_key = (
        symbol_or_key.replace("=", "_")
        .replace("^", "")
        .replace("/", "_")
        .replace(" ", "_")
        .lower()
    )

    folder_path = os.path.join(DATA_DIR, "bronze", clean_source)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{clean_key}_{timestamp}.json")
    envelope = {
        "source": clean_source,
        "key": clean_key,
        "ingested_at": now_utc.isoformat(),
        "payload": raw_data,
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2, default=_json_serializer)

    return file_path


# =========================================================
# POTOK MAKRO: FRED -> SILVER (DELTA LAKE) & GOLD (DELTA LAKE)
# =========================================================


def process_macro_to_silver_and_gold(
    indicator_name: str, df_macro: pd.DataFrame
) -> dict:
    if df_macro is None or df_macro.empty:
        return {}

    clean_ind = indicator_name.strip().lower()
    ingested_at = _utc_now()

    df_clean = df_macro.dropna().copy()
    if "date" not in df_clean.columns:
        df_clean = df_clean.reset_index()

    # Wyznaczenie kolumny z wartościami liczbowymi
    excluded_cols = {"date", "index", "updated_at", "ts", "ingested_at", "indicator"}
    val_candidates = [c for c in df_clean.columns if c not in excluded_cols]
    if not val_candidates:
        return {}
    val_col = val_candidates[0]

    # Konwersja typów zgodnie z Konwencją Lakehouse:
    # nazwy kolumn snake_case, ts i ingested_at w UTC, liczby jako float64 (double)
    df_clean["indicator"] = clean_ind
    df_clean["ts"] = pd.to_datetime(df_clean["date"], utc=True, errors="coerce").dt.floor("us")
    df_clean["value"] = pd.to_numeric(df_clean[val_col], errors="coerce").astype("float64")
    df_clean = df_clean.dropna(subset=["ts", "value"]).sort_values(by="ts", ascending=True)
    df_clean["ingested_at"] = ingested_at

    silver_df = df_clean[["indicator", "ts", "value", "ingested_at"]].reset_index(drop=True)

    if not IS_VERCEL and not silver_df.empty:
        silver_table_path = os.path.join(DATA_DIR, "silver", "macro", clean_ind)
        os.makedirs(silver_table_path, exist_ok=True)
        write_deltalake(
            silver_table_path, silver_df, mode="overwrite", schema_mode="overwrite"
        )

    latest_val = float(silver_df["value"].iloc[-1]) if len(silver_df) > 0 else None
    prev_val = float(silver_df["value"].iloc[-2]) if len(silver_df) > 1 else None
    latest_ts = silver_df["ts"].iloc[-1] if len(silver_df) > 0 else ingested_at
    change_val = (
        round(latest_val - prev_val, 4)
        if (latest_val is not None and prev_val is not None)
        else 0.0
    )

    gold_summary = {
        "indicator": indicator_name.upper(),
        "latest_value": latest_val,
        "previous_value": prev_val,
        "change": change_val,
        "last_updated": ingested_at.isoformat(),
    }

    if not IS_VERCEL and latest_val is not None:
        gold_table_path = os.path.join(DATA_DIR, "gold", "macro", clean_ind)
        os.makedirs(gold_table_path, exist_ok=True)
        df_gold = pd.DataFrame([{
            "indicator": clean_ind,
            "latest_value": float(latest_val),
            "previous_value": float(prev_val) if prev_val is not None else float("nan"),
            "change": float(change_val),
            "ts": latest_ts,
            "ingested_at": ingested_at,
        }])
        write_deltalake(
            gold_table_path, df_gold, mode="overwrite", schema_mode="overwrite"
        )

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
    os.makedirs(folder_path, exist_ok=True)

    df_events = pd.DataFrame(events)
    ingested_at = _utc_now()

    # Normalizacja nazw kolumn do snake_case
    df_events.columns = [str(c).strip().lower() for c in df_events.columns]

    if "seendate" in df_events.columns:
        df_events["ts"] = pd.to_datetime(
            df_events["seendate"], utc=True, errors="coerce"
        ).dt.floor("us")
        df_events["ts"] = df_events["ts"].fillna(ingested_at)
    else:
        df_events["ts"] = ingested_at

    # Zachowanie typów liczbowych jako float64, a tekstowych jako string/null
    for col in df_events.columns:
        if col == "ts":
            continue
        if pd.api.types.is_numeric_dtype(df_events[col]):
            df_events[col] = pd.to_numeric(df_events[col], errors="coerce").astype("float64")
        else:
            df_events[col] = df_events[col].where(df_events[col].notna(), None)
            df_events[col] = df_events[col].apply(
                lambda x: str(x) if x is not None else None
            )

    df_events["ingested_at"] = ingested_at

    write_deltalake(folder_path, df_events, mode="overwrite", schema_mode="overwrite")
    return folder_path


def get_gdelt_from_silver() -> list[dict]:
    """Odczyt oczyszczonych wydarzeń GDELT z tabeli Delta Lake."""
    folder_path = os.path.join(DATA_DIR, "silver", "gdelt", "events_delta")
    if not os.path.exists(os.path.join(folder_path, "_delta_log")):
        return []
    try:
        dt = DeltaTable(folder_path)
        df = dt.to_pandas()
        for col in ["ts", "ingested_at"]:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return df.to_dict(orient="records")
    except Exception:
        return []


# =========================================================
# ODCZYT NOTOWAŃ Z TABELI KONTRAKTOWEJ (gold/market/latest_prices)
# =========================================================


def get_stock_from_silver(symbol: str) -> dict | None:
    """
    Odczytuje najnowsze notowanie instrumentu z tabeli kontraktowej
    potoku strumieniowego: {LAKEHOUSE_ROOT}/gold/market/latest_prices
    """
    candidate_paths = [
        os.path.join(DATA_DIR, "gold", "market", "latest_prices"),
        os.path.join(DATA_DIR, "silver", "market", "prices"),
    ]
    clean_sym = symbol.strip().upper()

    for path in candidate_paths:
        if os.path.exists(os.path.join(path, "_delta_log")):
            try:
                dt = DeltaTable(path)
                df = dt.to_pandas()
                if "symbol" in df.columns:
                    df = df[df["symbol"].astype(str).str.upper() == clean_sym]
                if not df.empty:
                    row = df.iloc[-1]
                    price_val = float(row["price"]) if pd.notna(row.get("price")) else 0.0
                    change_pct = (
                        float(row["change_24h_pct"])
                        if "change_24h_pct" in row and pd.notna(row.get("change_24h_pct"))
                        else float(row.get("change", 0.0) or 0.0)
                    )
                    return {
                        "symbol": str(row.get("symbol", clean_sym)),
                        "name": str(row.get("name", clean_sym)),
                        "asset_class": str(row.get("asset_class", "stock")),
                        "price": round(price_val, 2),
                        "change": round(change_pct, 2),
                        "change_percent": f"{change_pct:.2f}%",
                        "currency": str(row.get("currency", "USD")),
                        "ts": str(row.get("ts", "")),
                    }
            except Exception:
                continue
    return None


# =========================================================
# POTOK WIADOMOŚCI: RSS / NEWSAPI -> SILVER & GOLD (DELTA LAKE)
# =========================================================


def save_news_to_silver(category: str, articles: list[dict]) -> str:
    if IS_VERCEL or not articles:
        return ""
    clean_cat = category.strip().lower()
    table_path = os.path.join(DATA_DIR, "silver", "news", clean_cat)
    os.makedirs(table_path, exist_ok=True)
    ingested_at = _utc_now()

    existing_articles = get_news_from_silver(clean_cat, limit=50)

    seen_urls = {a.get("url") for a in articles if a.get("url")}
    combined = list(articles)
    for old_art in existing_articles:
        if old_art.get("url") and old_art.get("url") not in seen_urls:
            combined.append(old_art)
            seen_urls.add(old_art.get("url"))

    combined.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    combined = combined[:50]

    df_news = pd.DataFrame(combined)
    df_news.columns = [str(c).strip().lower() for c in df_news.columns]

    if "published_at" in df_news.columns:
        df_news["ts"] = pd.to_datetime(
            df_news["published_at"], utc=True, errors="coerce"
        ).dt.floor("us")
        df_news["ts"] = df_news["ts"].fillna(ingested_at)
    else:
        df_news["ts"] = ingested_at

    df_news["category"] = clean_cat
    df_news["ingested_at"] = ingested_at

    for col in df_news.columns:
        if col not in ["ts", "ingested_at"]:
            df_news[col] = df_news[col].where(df_news[col].notna(), None)
            df_news[col] = df_news[col].apply(
                lambda x: str(x) if x is not None else None
            )

    write_deltalake(table_path, df_news, mode="overwrite", schema_mode="overwrite")
    return table_path


def get_news_from_silver(category: str, limit: int = 30) -> list[dict]:
    clean_cat = category.strip().lower()
    table_path = os.path.join(DATA_DIR, "silver", "news", clean_cat)
    if not os.path.exists(os.path.join(table_path, "_delta_log")):
        return []
    try:
        dt = DeltaTable(table_path)
        df = dt.to_pandas()
        if "published_at" in df.columns:
            df = df.sort_values(by="published_at", ascending=False)
        records = []
        for row in df.head(limit).to_dict(orient="records"):
            records.append({
                "id": str(row.get("id") or ""),
                "title": str(row.get("title") or ""),
                "description": str(row.get("description") or ""),
                "source": str(row.get("source") or "News"),
                "url": str(row.get("url") or ""),
                "published_at": str(row.get("published_at") or ""),
                "category": str(row.get("category") or clean_cat),
            })
        return records
    except Exception:
        return []


def save_news_gold_analysis(category: str, analysis_data: dict) -> str:
    if IS_VERCEL or not analysis_data:
        return ""
    clean_cat = category.strip().lower()
    table_path = os.path.join(DATA_DIR, "gold", "ai", f"news_{clean_cat}")
    os.makedirs(table_path, exist_ok=True)
    ingested_at = _utc_now()

    df_gold = pd.DataFrame([{
        "category": clean_cat,
        "overall_sentiment": str(analysis_data.get("overallSentiment") or "Neutralny"),
        "risk_level": str(analysis_data.get("riskLevel") or "Średnie"),
        "summary": str(analysis_data.get("summary") or ""),
        "source_signature_json": json.dumps(
            analysis_data.get("source_signature", []), ensure_ascii=False
        ),
        "payload_json": json.dumps(
            analysis_data, ensure_ascii=False, default=_json_serializer
        ),
        "ts": ingested_at,
        "ingested_at": ingested_at,
    }])

    write_deltalake(table_path, df_gold, mode="overwrite", schema_mode="overwrite")
    return table_path


def get_news_gold_analysis(category: str) -> dict | None:
    clean_cat = category.strip().lower()
    table_path = os.path.join(DATA_DIR, "gold", "ai", f"news_{clean_cat}")
    if not os.path.exists(os.path.join(table_path, "_delta_log")):
        return None
    try:
        dt = DeltaTable(table_path)
        df = dt.to_pandas()
        if df.empty:
            return None
        payload_str = df.iloc[-1].get("payload_json")
        return json.loads(payload_str) if payload_str else None
    except Exception:
        return None