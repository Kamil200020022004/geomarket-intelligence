from app.data_sources.yahoo import get_stock_data
from app.models.stock import StockResponse
from app.data_sources.yahoo import get_stock_history

def get_stock(symbol: str) -> StockResponse:
    data = get_stock_data(symbol)

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