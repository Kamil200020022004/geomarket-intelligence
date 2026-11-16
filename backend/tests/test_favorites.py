"""Testy integracyjne ulubionych: trwałość, brak duplikatów, separacja kont."""

import pytest

from tests.conftest import bearer, login, register

pytestmark = pytest.mark.integration

BITCOIN = {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 97000.5, "sparkline_in_7d": {"price": [1.0, 2.0]}}
AAPL = {"symbol": "AAPL", "name": "Apple", "market": "NASDAQ", "price": 230.1}


@pytest.fixture
def jan(api):
    register(api, email="jan@example.com")
    return bearer(login(api, email="jan@example.com"))


@pytest.fixture
def ola(api):
    register(api, email="ola@example.com", name="Ola")
    return bearer(login(api, email="ola@example.com"))


def test_favorites_require_login(api):
    assert api.get("/api/favorites/crypto").status_code == 401
    assert api.post("/api/favorites/crypto", json=BITCOIN).status_code == 401
    assert api.delete("/api/favorites/crypto/bitcoin").status_code == 401


def test_add_returns_full_snapshot_and_list_persists(api, jan):
    response = api.post("/api/favorites/crypto", json=BITCOIN, headers=jan)
    assert response.status_code == 200
    assert response.json() == [BITCOIN]
    assert api.get("/api/favorites/crypto", headers=jan).json() == [BITCOIN]


def test_favorites_survive_new_login(api, jan):
    api.post("/api/favorites/stock", json=AAPL, headers=jan)
    new_session = bearer(login(api, email="jan@example.com"))
    assert api.get("/api/favorites/stock", headers=new_session).json() == [AAPL]


def test_adding_same_item_twice_does_not_duplicate(api, jan):
    api.post("/api/favorites/crypto", json=BITCOIN, headers=jan)
    response = api.post("/api/favorites/crypto", json={**BITCOIN, "current_price": 1.0}, headers=jan)
    assert response.json() == [BITCOIN]  # pierwsza migawka zostaje, bez duplikatu


def test_stock_id_falls_back_to_symbol_and_delete_works(api, jan):
    api.post("/api/favorites/stock", json=AAPL, headers=jan)
    response = api.delete("/api/favorites/stock/AAPL", headers=jan)
    assert response.status_code == 200
    assert response.json() == []


def test_types_are_separate(api, jan):
    api.post("/api/favorites/crypto", json=BITCOIN, headers=jan)
    assert api.get("/api/favorites/stock", headers=jan).json() == []


def test_users_cannot_see_or_delete_each_others_favorites(api, jan, ola):
    api.post("/api/favorites/crypto", json=BITCOIN, headers=jan)
    assert api.get("/api/favorites/crypto", headers=ola).json() == []
    api.delete("/api/favorites/crypto/bitcoin", headers=ola)
    assert api.get("/api/favorites/crypto", headers=jan).json() == [BITCOIN]


def test_invalid_type_returns_422(api, jan):
    assert api.get("/api/favorites/forex", headers=jan).status_code == 422


def test_item_without_identifier_returns_422(api, jan):
    response = api.post("/api/favorites/stock", json={"name": "Bez symbolu"}, headers=jan)
    assert response.status_code == 422
    assert response.json() == {"detail": "Element nie ma identyfikatora."}


def test_too_large_item_returns_422(api, jan):
    huge = {"id": "x", "data": "a" * 40_000}
    assert api.post("/api/favorites/crypto", json=huge, headers=jan).status_code == 422
