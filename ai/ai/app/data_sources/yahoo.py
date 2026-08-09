import yfinance as yf


def get_stock_data(symbol: str):
    ticker = yf.Ticker(symbol)

    info = ticker.info
    history = ticker.history(period="1mo")

    return {
        "symbol": symbol.upper(),
        "company": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "current_price": info.get("currentPrice"),
        "previous_close": info.get("previousClose"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "currency": info.get("currency"),
        "history": history.reset_index().to_dict(orient="records"),
        
    }
def get_stock_history(symbol: str, period: str = "1mo"):
    ticker = yf.Ticker(symbol)

    history = ticker.history(period=period)

    history.reset_index(inplace=True)

    return history