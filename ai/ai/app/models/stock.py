from pydantic import BaseModel


class StockResponse(BaseModel):
    symbol: str
    company: str | None = None
    sector: str | None = None
    industry: str | None = None
    current_price: float | None = None
    previous_close: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    market_cap: int | None = None
    pe_ratio: float | None = None
    currency: str | None = None