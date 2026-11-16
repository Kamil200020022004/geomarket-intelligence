"""Testy pośredniczenia do serwisu AI: przekazywanie, cache, awaria serwisu AI, walidacja."""

import pytest

from app.core.config import get_settings

IMPACT = {"title": "AI Impact", "risk": "średnie", "summary": "Informacyjnie, nie porada inwestycyjna."}


def test_get_is_forwarded_with_same_path_and_body(client, ai_service):
    ai_service.respond("GET", "/stock/ai-impact", body=IMPACT)
    response = client.get("/stock/ai-impact")
    assert response.status_code == 200
    assert response.json() == IMPACT
    assert response.headers["x-cache"] == "MISS"


def test_second_request_is_served_from_cache(client, ai_service):
    ai_service.respond("GET", "/stock/ai-impact", body=IMPACT)
    client.get("/stock/ai-impact")
    second = client.get("/stock/ai-impact")
    assert second.json() == IMPACT
    assert second.headers["x-cache"] == "HIT"
    assert len(ai_service.calls_to("/stock/ai-impact")) == 1  # Gemini wywołany tylko raz


def test_cache_key_includes_query_parameters(client, ai_service):
    ai_service.respond("GET", "/news", body={"articles": []})
    client.get("/news?category=crypto")
    client.get("/news?category=macro")
    assert [call.url.params["category"] for call in ai_service.calls_to("/news")] == ["crypto", "macro"]


def test_refresh_bypasses_cache_and_is_forwarded(client, ai_service):
    ai_service.respond("GET", "/news/analysis", body={"analysis": "x"})
    client.get("/news/analysis?category=stocks")
    response = client.get("/news/analysis?category=stocks&refresh=true")
    assert response.headers["x-cache"] == "BYPASS"
    calls = ai_service.calls_to("/news/analysis")
    assert len(calls) == 2
    assert calls[1].url.params["refresh"] == "true"


def test_client_ip_is_forwarded(client, ai_service):
    ai_service.respond("GET", "/stock/ai-impact", body=IMPACT)
    client.get("/stock/ai-impact")
    assert ai_service.calls[0].headers["x-forwarded-for"] == "testclient"


def test_ai_service_down_without_cache_returns_503(client, ai_service):
    ai_service.down = True
    response = client.get("/stock/ai-impact")
    assert response.status_code == 503
    assert response.json() == {"detail": "Serwis analiz AI jest chwilowo niedostępny. Spróbuj ponownie za chwilę."}


def test_ai_service_down_returns_last_known_answer(client, ai_service, monkeypatch):
    monkeypatch.setattr(get_settings(), "ai_cache_ttl_seconds", 0)  # wpis od razu nieświeży
    ai_service.respond("GET", "/stock/ai-impact", body=IMPACT)
    client.get("/stock/ai-impact")
    ai_service.down = True
    response = client.get("/stock/ai-impact")
    assert response.status_code == 200
    assert response.json() == IMPACT
    assert response.headers["x-cache"] == "STALE"


def test_ai_service_5xx_is_treated_as_unavailable(client, ai_service):
    ai_service.respond("GET", "/stock/macro/analysis", status=500, body={"detail": "Gemini error"})
    response = client.get("/stock/macro/analysis")
    assert response.status_code == 503
    assert "Gemini" not in response.text  # nie ujawniamy szczegółów błędu serwisu wewnętrznego


def test_ai_service_4xx_is_passed_through_and_not_cached(client, ai_service):
    ai_service.respond("GET", "/stock/analyze/XYZ", status=404, body={"detail": "Brak danych"})
    first = client.get("/stock/analyze/XYZ")
    client.get("/stock/analyze/XYZ")
    assert first.status_code == 404
    assert first.json() == {"detail": "Brak danych"}
    assert len(ai_service.calls_to("/stock/analyze/XYZ")) == 2


@pytest.mark.parametrize("url", ["/news?category=sport", "/news?limit=500", "/stock/analyze/AA%20BB"])
def test_invalid_parameters_are_rejected_before_reaching_ai(client, ai_service, url):
    assert client.get(url).status_code == 422
    assert ai_service.calls == []


def test_path_traversal_in_symbol_never_reaches_ai(client, ai_service):
    # Zakodowany ukośnik zmienia ścieżkę — router jej nie dopasuje (404), a zapytanie nie wychodzi dalej.
    assert client.get("/stock/analyze/AA%2F..%2Fadmin").status_code == 404
    assert ai_service.calls == []


def test_market_data_routes_of_ai_service_are_not_exposed(client, ai_service):
    # Notowania mają jedno źródło: potok strumieniowy (/api/...), nie Yahoo w serwisie AI.
    assert client.get("/stock/AAPL").status_code == 404
    assert client.get("/stock/history/AAPL").status_code == 404
    assert ai_service.calls == []


# --- Czat ---


def test_chat_is_forwarded(client, ai_service):
    ai_service.respond("POST", "/chat", body={"response": "Odpowiedź modelu"})
    payload = {"message": "Co z inflacją?", "symbol": "AAPL", "history": [{"role": "user", "content": "Cześć"}]}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    assert response.json() == {"response": "Odpowiedź modelu"}
    sent = ai_service.calls_to("/chat")[0]
    assert sent.method == "POST"
    import json

    assert json.loads(sent.content) == payload


def test_chat_is_never_cached(client, ai_service):
    ai_service.respond("POST", "/chat", body={"response": "x"})
    client.post("/chat", json={"message": "a"})
    client.post("/chat", json={"message": "a"})
    assert len(ai_service.calls_to("/chat")) == 2


def test_chat_validation(client, ai_service):
    assert client.post("/chat", json={"message": ""}).status_code == 422
    assert client.post("/chat", json={"message": "x", "history": [{"role": "admin", "content": "x"}]}).status_code == 422
    assert ai_service.calls == []


def test_chat_when_ai_down_returns_503(client, ai_service):
    ai_service.down = True
    assert client.post("/chat", json={"message": "Cześć"}).status_code == 503


def test_after_connection_failure_ai_is_not_retried_immediately(client, ai_service):
    ai_service.down = True
    client.get("/stock/ai-impact")
    ai_service.down = False
    ai_service.respond("GET", "/stock/ai-impact", body=IMPACT)
    response = client.get("/stock/ai-impact")
    assert response.status_code == 503  # bezpiecznik: przez chwilę nie czekamy na serwis, który nie odpowiadał
    assert len(ai_service.calls_to("/stock/ai-impact")) == 1


def test_ai_is_retried_after_breaker_pause(client, ai_service, monkeypatch):
    monkeypatch.setattr(get_settings(), "ai_retry_after_seconds", 0)
    ai_service.down = True
    client.get("/stock/ai-impact")
    ai_service.down = False
    ai_service.respond("GET", "/stock/ai-impact", body=IMPACT)
    assert client.get("/stock/ai-impact").status_code == 200
