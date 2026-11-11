from app.data_sources.yahoo import get_stock_data, get_stock_history
from app.models.stock import StockResponse
from app.services.data_lake_service import get_stock_from_silver


def get_stock(symbol: str) -> StockResponse:
  symbol_clean = symbol.upper()

  # 1. Próba odczytu ze wspólnego Lakehouse'a (warstwa Silver Delta Lake)
  silver_data = get_stock_from_silver(symbol_clean)
  if silver_data and silver_data.get("current_price") is not None:
    return StockResponse(
        symbol=symbol_clean,
        company=silver_data.get("company")
        or silver_data.get("name")
        or symbol_clean,
        sector=silver_data.get("sector"),
        industry=silver_data.get("industry"),
        current_price=float(silver_data["current_price"]),
        previous_close=silver_data.get("previous_close"),
        day_high=silver_data.get("day_high"),
        day_low=silver_data.get("day_low"),
        market_cap=silver_data.get("market_cap"),
        pe_ratio=silver_data.get("pe_ratio"),
        currency=silver_data.get("currency", "USD"),
    )

  # 2. Bezpieczny fallback do konektora pomocniczego
  data = get_stock_data(symbol_clean)
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