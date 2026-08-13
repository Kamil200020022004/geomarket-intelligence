from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


# Twój oryginalny model danych dla spółki giełdowej
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


# Raport analityczny generowany przez AI dla spółki
class StockReportResponse(BaseModel):
    symbol: str = Field(..., example="AAPL")
    company_name: str = Field(..., example="Apple Inc.")
    current_price: float = Field(..., example=224.23)
    currency: str = Field(..., example="USD")
    summary: str = Field(..., example="Krótkie podsumowanie kondycji spółki...")
    key_metrics: Dict[str, Any]


# Analiza makroekonomiczna
class MacroAnalysisResponse(BaseModel):
    analysis: str = Field(..., example="Podsumowanie sytuacji makroekonomicznej...")
    source_data_summary: Dict[str, Any]


# 1. Kafelki rynkowe (np. Bitcoin, EUR/PLN)
class MarketAssetItem(BaseModel):
    name: str = Field(..., example="Bitcoin")
    value: str = Field(..., example="267 540 PLN")
    change: str = Field(..., example="+2.45%")
    category: str = Field(..., example="crypto")


# 2. Sekcja AI Impact (Analiza geopolityczna/rynkowa od Kamila)
class AIImpactResponse(BaseModel):
    event: str = Field(..., example="Nowe napięcia geopolityczne na Bliskim Wschodzie")
    affectedMarkets: str = Field(..., example="EUR/PLN, ropa, WIG20")
    riskLevel: str = Field(..., example="Wysokie")
    sentiment: str = Field(..., example="Negatywny")
    summary: str = Field(..., example="AI wskazuje, że wydarzenie może zwiększyć zmienność na rynku...")
    showChart: bool = Field(True, example=True)


# 3. Punkty scenariusza dla wykresów AI
class ChartPoint(BaseModel):
    date: str = Field(..., example="Pon")
    current: float = Field(..., example=4.31)
    aiScenario: float = Field(..., example=4.35)