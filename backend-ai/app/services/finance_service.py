from app.data_sources.yahoo import get_stock_data, get_stock_history
from app.models.stock import StockResponse
from app.services.data_lake_service import (
    save_to_bronze,
    process_bronze_to_silver_stock,
    generate_gold_stock_summary
)


def get_stock(symbol: str) -> StockResponse:
    symbol_clean = symbol.upper()
    data = get_stock_data(symbol_clean)

    # 1. Warstwa Bronze: Zapis surowej odpowiedzi ze słownika do JSON
    if data:
        save_to_bronze(source_name="yfinance", symbol_or_key=symbol_clean, raw_data=data)

    # 2. Pobranie historii, zapis do Silver (.parquet) oraz wyliczenie Gold
    try:
        history_df = get_stock_history(symbol_clean)
        if not history_df.empty:
            process_bronze_to_silver_stock(symbol=symbol_clean, df_stock=history_df)
            generate_gold_stock_summary(symbol=symbol_clean)
    except Exception as e:
        print(f"⚠️ Nie udało się zapisać historii dla {symbol_clean} w Data Lake: {e}")

    # Zwrócenie poprawnej struktury Pydantic
    return StockResponse(
        symbol=data["symbol"],
        company=data["company"],
        sector=data["sector"],
        industry=data["industry"],
        current_price=data["current_price"],
        previous_close=data["previous_close"],
        day_high=data["day_high"],
        day_low=data["day_low"],
        market_cap=data["market_cap"],
        pe_ratio=data["pe_ratio"],
        currency=data["currency"],
    )


def get_history(symbol: str):
    history = get_stock_history(symbol)
    return history.to_dict(orient="records")