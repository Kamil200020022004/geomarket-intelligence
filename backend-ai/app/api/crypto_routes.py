from fastapi import APIRouter

router = APIRouter(prefix="/crypto", tags=["Crypto"])


@router.get(
    "/ai-impact",
    summary="Wpływ wydarzeń na rynek krypto (AI Impact)",
    description="Zwraca przeanalizowany wpływ ważnego wydarzenia na rynek kryptowalut."
)
def crypto_ai_impact():
    return {
        "event": "Nowe regulacje SEC dotyczące rynku kryptowalut",
        "affectedMarkets": "BTC, ETH, USDT",
        "riskLevel": "Średnie",
        "sentiment": "Neutralny",
        "summary": "AI prognozuje zwiększoną zmienność na głównych kryptowalutach w obliczu zapowiedzi nowych ram prawnych.",
        "showChart": True
    }


@router.get(
    "/{symbol}",
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