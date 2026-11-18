"""Testy kontraktu endpointów rynkowych: dokładnie pola i typy czytane przez komponenty React."""

from datetime import datetime

import pytest

from app.market import catalog, service

STOCK_FIELDS = {"symbol", "name", "market", "price", "change", "volume", "marketCap", "history",
                "currency", "source", "updated_at"}
CRYPTO_FIELDS = {"id", "symbol", "name", "image", "market_cap_rank", "current_price",
                 "price_change_percentage_1h_in_currency", "price_change_percentage_24h_in_currency",
                 "price_change_percentage_7d_in_currency", "total_volume", "market_cap", "sparkline_in_7d",
                 "source", "updated_at"}
MACRO_FIELDS = {"symbol", "name", "category", "value", "change", "unit", "unit_description", "description",
                "history", "source", "updated_at"}
# Kolejność i symbole jak w MACRO_DATA w Macro.jsx.
MACRO_SYMBOLS = ["EUR/PLN", "USD/PLN", "CHF/PLN", "GBP/PLN", "EUR/USD", "CPI PL", "CPI USA", "CPI EU",
                 "NBP RATE", "FED RATE", "ECB RATE", "GDP PL", "GDP USA", "GDP EU", "OIL", "GOLD", "GAS"]

MACRO_RAW = {
    # Kolejność historii celowo pomieszana — backend musi ją posortować.
    "CPI_PL": {"date": "2026-09-01", "value": "3.1",
               "history": [{"date": "2026-09-01", "value": 3.1}, {"date": "2026-07-01", "value": 3.6},
                           {"date": "2026-08-01", "value": 3.4}]},
    "GDP": {"date": "N/A", "value": "N/A", "history": []},
}


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None, f"czas bez strefy: {value}"
    return parsed


def _assert_chronological(times: list[str]) -> None:
    parsed = [_parse_time(t) for t in times]
    assert parsed == sorted(parsed), "historia musi być od najstarszego do najnowszego"


# --- Giełda ---


def test_stocks_contract(client):
    response = client.get("/api/stocks")
    assert response.status_code == 200
    stocks = response.json()
    assert isinstance(stocks, list)
    assert len(stocks) == 100
    for stock in stocks:
        assert set(stock) == STOCK_FIELDS
        assert stock["market"] in {"Zagraniczny", "Polska"}
        assert isinstance(stock["price"], float)
        assert isinstance(stock["change"], float)
        assert stock["history"], "wykres potrzebuje punktów"
        assert all(set(point) == {"time", "price"} for point in stock["history"])
        _assert_chronological([point["time"] for point in stock["history"]])
        assert stock["source"] == "test"


def test_stocks_keep_frontend_symbols_and_currencies(client):
    stocks = {s["symbol"]: s for s in client.get("/api/stocks").json()}
    assert stocks["AAPL"]["market"] == "Zagraniczny" and stocks["AAPL"]["currency"] == "USD"
    assert stocks["PKN"]["market"] == "Polska" and stocks["PKN"]["currency"] == "PLN"
    assert list(stocks)[:3] == ["AAPL", "MSFT", "NVDA"]  # kolejność jak w StockMarket.jsx


def test_catalog_maps_gpw_symbols_to_yahoo():
    assert catalog.BY_SYMBOL["PKN"].source_symbol == "PKN.WA"
    assert catalog.BY_SYMBOL["AAPL"].source_symbol == "AAPL"
    assert catalog.BY_SYMBOL["EUR/PLN"].source_symbol == "EURPLN=X"
    assert len({i.symbol for i in catalog.STOCKS}) == 100  # brak duplikatów


# --- Kryptowaluty ---


def test_crypto_contract(client):
    coins = client.get("/api/crypto/top").json()
    assert isinstance(coins, list) and coins  # Crypto.jsx: setCoins(result), setSelectedCoin(result[0])
    assert coins[0]["id"] == "bitcoin"
    for coin in coins:
        assert set(coin) == CRYPTO_FIELDS
        assert set(coin["sparkline_in_7d"]) == {"price"}
        assert len(coin["sparkline_in_7d"]["price"]) == 168  # 7 dni × 24 punkty godzinowe
        assert all(isinstance(p, float) for p in coin["sparkline_in_7d"]["price"])
    assert [c["market_cap_rank"] for c in coins] == sorted(c["market_cap_rank"] for c in coins)


# --- Makro ---


def test_macro_contract_with_ai_service(client, ai_service):
    ai_service.respond("GET", "/stock/macro/raw", body=MACRO_RAW)
    items = client.get("/api/macro").json()
    assert [item["symbol"] for item in items] == MACRO_SYMBOLS
    for item in items:
        assert set(item) == MACRO_FIELDS
        assert item["unit"] in {"PLN", "USD", "%"}
        assert all(set(point) == {"time", "value"} for point in item["history"])
        _assert_chronological([point["time"] for point in item["history"]])


def test_macro_indicator_mapping(client, ai_service):
    ai_service.respond("GET", "/stock/macro/raw", body=MACRO_RAW)
    items = {item["symbol"]: item for item in client.get("/api/macro").json()}
    cpi = items["CPI PL"]
    assert cpi["value"] == 3.1  # napis "3.1" z serwisu AI zamieniony na liczbę
    assert cpi["change"] == -0.3  # różnica w punktach procentowych do poprzedniego odczytu
    assert [p["value"] for p in cpi["history"]] == [3.6, 3.4, 3.1]
    assert cpi["unit_description"] == "% r/r"
    assert cpi["source"] == "fred"
    gdp = items["GDP USA"]  # "N/A" w serwisie AI → null, bez zmyślonych wartości
    assert gdp["value"] is None and gdp["history"] == [] and gdp["source"] == "unavailable"


def test_macro_survives_ai_service_outage(client, ai_service):
    ai_service.down = True
    response = client.get("/api/macro")
    assert response.status_code == 200
    items = {item["symbol"]: item for item in response.json()}
    assert items["EUR/PLN"]["value"] is not None  # kursy z naszego potoku działają dalej
    assert items["CPI PL"]["value"] is None and items["CPI PL"]["source"] == "unavailable"


def test_macro_raw_from_ai_is_cached(client, ai_service):
    ai_service.respond("GET", "/stock/macro/raw", body=MACRO_RAW)
    client.get("/api/macro")
    client.get("/api/macro")
    assert len(ai_service.calls_to("/stock/macro/raw")) == 1


# --- Dashboard ---


def test_dashboard_cards_match_marketcard_props(client):
    cards = client.get("/api/dashboard/markets").json()
    assert [(c["id"], c["name"], c["path"]) for c in cards] == [
        (1, "Bitcoin", "/kryptowaluty"), (2, "WIG20", "/gielda"), (3, "EUR/PLN", "/makro"),
    ]
    for card in cards:
        assert isinstance(card["value"], str) and isinstance(card["change"], str)
        assert card["change"][0] in "+-"  # MarketCard: change.startsWith("+")
        assert card["change"].endswith("%")
    assert cards[0]["value"].endswith(" PLN")


@pytest.mark.parametrize(
    ("value", "decimals", "expected"),
    [(267540.4, 0, "267 540"), (2320.405, 2, "2 320,41"), (4.312, 4, "4,3120"), (-1234.5, 1, "-1 234,5")],
)
def test_polish_number_format(value, decimals, expected):
    assert service._format_pl(value, decimals) == expected


def test_market_response_is_reused_within_cache_window(client, monkeypatch):
    """Wydajność: w oknie MARKET_CACHE_SECONDS odpowiedź jest budowana raz (regresja testu obciążeniowego)."""
    calls = {"n": 0}
    original = service.list_stocks

    def counting(source):
        calls["n"] += 1
        return original(source)

    monkeypatch.setattr(service, "list_stocks", counting)
    first = client.get("/api/stocks")
    second = client.get("/api/stocks")
    assert first.status_code == second.status_code == 200
    assert first.content == second.content
    assert first.headers["content-type"] == "application/json"
    assert calls["n"] == 1
