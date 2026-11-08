from fastapi import APIRouter, HTTPException, Query
from app.services.news_service import (
    get_news_full_payload,
    get_category_ai_analysis,
    resolve_category,
)

router = APIRouter(prefix="/news", tags=["Market News & AI Analysis"])


@router.get(
    "",
    summary="Wiadomości internetowe dla wybranej kategorii",
    description=(
        "Zwraca rzeczywiste artykuły z RSS i NewsAPI dla jednej z 6 kategorii: "
        "stocks, macro, crypto, geopolitics, poland, global."
    ),
)
def get_category_news(
    category: str = Query(
        "stocks",
        description="Kategoria: stocks, macro, crypto, geopolitics, poland, global",
    ),
    limit: int = Query(25, ge=1, le=50),
    refresh: bool = Query(False, description="Wymuś odświeżenie z zewnętrznych źródeł"),
):
    try:
        resolve_category(category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Nieprawidłowa kategoria '{category}'. Dozwolone wartości: "
                "stocks, macro, crypto, geopolitics, poland, global."
            ),
        )

    return get_news_full_payload(category=category, limit=limit, refresh=refresh)


@router.get(
    "/analysis",
    summary="Analiza AI dla wybranej kategorii wiadomości",
    description=(
        "Generuje analizę AI (model gemini-3.5-flash-lite) na podstawie rzeczywistych "
        "pobranych artykułów dla kategorii: stocks, macro, crypto, geopolitics, poland, global."
    ),
)
def get_category_analysis(
    category: str = Query(
        "stocks",
        description="Kategoria: stocks, macro, crypto, geopolitics, poland, global",
    ),
    refresh: bool = Query(False, description="Wymuś ponowne wygenerowanie analizy przez Gemini"),
):
    try:
        resolve_category(category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Nieprawidłowa kategoria '{category}'. Dozwolone wartości: "
                "stocks, macro, crypto, geopolitics, poland, global."
            ),
        )

    return get_category_ai_analysis(category=category, refresh=refresh)