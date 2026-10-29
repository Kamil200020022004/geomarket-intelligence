from fastapi import APIRouter
<<<<<<< HEAD
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

=======

router = APIRouter(prefix="/crypto", tags=["Crypto"])

>>>>>>> 342c8bc2f5e88c4a64fc8af2597c3637556bb1a6

@router.get(
    "/ai-impact",
    summary="Wpływ wydarzeń na rynek krypto (AI Impact)",
    description="Zwraca przeanalizowany wpływ ważnego wydarzenia na rynek kryptowalut."
)
def crypto_ai_impact():
    return {
<<<<<<< HEAD
        "event": "Nowe regulacje dotyczące rynku kryptowalut",
=======
        "event": "Nowe regulacje SEC dotyczące rynku kryptowalut",
>>>>>>> 342c8bc2f5e88c4a64fc8af2597c3637556bb1a6
        "affectedMarkets": "BTC, ETH, USDT",
        "riskLevel": "Średnie",
        "sentiment": "Neutralny",
        "summary": "AI prognozuje zwiększoną zmienność na głównych kryptowalutach w obliczu zapowiedzi nowych ram prawnych.",
        "showChart": True
    }


@router.get(
    "/{symbol}",
<<<<<<< HEAD
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
=======
    summary="Podstawowe dane kryptowaluty",
    description="Zwraca aktualną cenę i bazowe metryki dla wybranej kryptowaluty."
)
def crypto_data(symbol: str):
    return {
        "name": symbol.upper(),
        "value": "267 540 PLN",
        "change": "+2.45%",
        "category": "crypto"
    }
>>>>>>> 342c8bc2f5e88c4a64fc8af2597c3637556bb1a6
