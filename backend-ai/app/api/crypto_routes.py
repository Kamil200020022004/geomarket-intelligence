from fastapi import APIRouter
from app.services.finance_service import get_stock

router = APIRouter(prefix="/crypto", tags=["Crypto"])

CRYPTO_SYMBOLS = {
    "BTC": {"name": "Bitcoin", "ticker": "BTC-USD"},
    "ETH": {"name": "Ethereum", "ticker": "ETH-USD"},
    "USDT": {"name": "Tether", "ticker": "USDT-USD"},
    "BNB": {"name": "BNB", "ticker": "BNB-USD"},
    "SOL": {"name": "Solana", "ticker": "SOL-USD"},
}


@router.get(
    "/table",
    summary="Lista TOP kryptowalut do tabeli",
    description="Zwraca aktualne kursy i zmiany dla głównych kryptowalut pod tabelę na frontendzie."
)
def crypto_table():
    results = []
    for rank, (coin, info) in enumerate(CRYPTO_SYMBOLS.items(), start=1):
        try:
            data = get_stock(info["ticker"])
            d = data.model_dump() if hasattr(data, "model_dump") else dict(data)
            results.append({
                "rank": rank,
                "symbol": coin,
                "name": info["name"],
                "price": d.get("current_price", 0.0),
                "change24h": f"{d.get('change_percent', 0.0):+.2f}%",
                "marketCap": d.get("market_cap", "N/D")
            })
        except Exception:
            results.append({
                "rank": rank,
                "symbol": coin,
                "name": info["name"],
                "price": 0.0,
                "change24h": "0.00%",
                "marketCap": "N/D"
            })
    return results


@router.get(
    "/ai-impact",
    summary="Wpływ wydarzeń na rynek krypto (AI Impact)",
    description="Zwraca przeanalizowany wpływ ważnego wydarzenia na rynek kryptowalut."
)
def crypto_ai_impact():
    return {
        "event": "Nowe regulacje dotyczące rynku kryptowalut",
        "affectedMarkets": "BTC, ETH, USDT",
        "riskLevel": "Średnie",
        "sentiment": "Neutralny",
        "summary": "AI prognozuje zwiększoną zmienność na głównych kryptowalutach w obliczu zapowiedzi nowych ram prawnych.",
        "showChart": True
    }


@router.get(
    "/{symbol}",
    summary="Podstawowe dane pojedynczej kryptowaluty",
    description="Zwraca aktualną cenę i zmianę dla wybranej kryptowaluty."
)
def crypto_data(symbol: str):
    clean = symbol.upper().replace("-USD", "")
    info = CRYPTO_SYMBOLS.get(clean, {"name": clean, "ticker": f"{clean}-USD"})

    try:
        data = get_stock(info["ticker"])
        d = data.model_dump() if hasattr(data, "model_dump") else dict(data)
        return {
            "name": info["name"],
            "symbol": clean,
            "price": f"${d.get('current_price', 0.0):,.2f}",
            "change": f"{d.get('change_percent', 0.0):+.2f}%",
            "category": "crypto"
        }
    except Exception:
        return {
            "name": clean,
            "symbol": clean,
            "price": "Brak danych",
            "change": "0.00%",
            "category": "crypto"
        }
