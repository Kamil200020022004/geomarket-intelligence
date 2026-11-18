"""Pośredniczenie w zapytaniach do serwisu AI Patryka (`backend-ai`, port 8001).

Zasady:
1. Odpowiedzi GET z kodem 200 trafiają do cache (świeże przez TTL, potem zapas na awarię).
2. Serwis AI niedostępny (brak połączenia, przekroczony czas, błąd 5xx):
   - jest zapas w cache → zwracamy go (oznaczony nagłówkiem `X-Cache: STALE`),
   - brak zapasu → 503 z czytelnym komunikatem. Reszta platformy działa dalej.
3. Błędy 4xx serwisu AI (np. zła kategoria newsów) przekazujemy bez zmian — to błąd zapytania, nie awaria.
4. Prosty bezpiecznik (circuit breaker): po błędzie połączenia przez `AI_RETRY_AFTER_SECONDS` nie
   próbujemy łączyć się ponownie — odpowiadamy od razu z cache albo 503, zamiast za każdym razem
   czekać na przekroczenie czasu.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.cache import CacheEntry, TTLCache

logger = logging.getLogger(__name__)

AI_UNAVAILABLE_MESSAGE = "Serwis analiz AI jest chwilowo niedostępny. Spróbuj ponownie za chwilę."

cache = TTLCache()
_client: httpx.Client | None = None
# Do kiedy (time.monotonic) uznajemy serwis AI za niedostępny bez ponownej próby połączenia.
_unavailable_until: float = 0.0


class AIServiceUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: Any
    cache_status: str  # HIT | MISS | STALE | BYPASS


def get_client() -> httpx.Client:
    """Jeden klient HTTP z pulą połączeń na cały proces (szybciej niż nowe połączenie na każde żądanie)."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = httpx.Client(base_url=settings.ai_service_url, timeout=settings.ai_timeout_seconds)
    return _client


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


def _mark_unavailable() -> None:
    global _unavailable_until
    _unavailable_until = time.monotonic() + get_settings().ai_retry_after_seconds


def _mark_available() -> None:
    global _unavailable_until
    _unavailable_until = 0.0


def _breaker_open() -> bool:
    return time.monotonic() < _unavailable_until


def reset_breaker() -> None:
    _mark_available()


def _cache_key(path: str, params: dict[str, Any]) -> str:
    query = "&".join(f"{k}={params[k]}" for k in sorted(params) if params[k] is not None)
    return f"GET {path}?{query}"


def _forwarded_headers(client_ip: str | None) -> dict[str, str]:
    # Przekazujemy adres przeglądarki, żeby serwis AI mógł liczyć limity per użytkownik, a nie per bramka.
    return {"X-Forwarded-For": client_ip} if client_ip else {}


def _parse_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {"detail": response.text[:500]}


def get(
    path: str,
    params: dict[str, Any] | None = None,
    *,
    ttl_seconds: int | None = None,
    bypass_cache: bool = False,
    client_ip: str | None = None,
    timeout: float | None = None,
) -> GatewayResponse:
    settings = get_settings()
    params = {k: v for k, v in (params or {}).items() if v is not None}
    ttl = settings.ai_cache_ttl_seconds if ttl_seconds is None else ttl_seconds
    key = _cache_key(path, params)

    cached = cache.get(key)
    if cached is not None and not bypass_cache and cached.is_fresh(time.monotonic()):
        return GatewayResponse(200, cached.value, "HIT")

    if _breaker_open():
        return _stale_or_raise(cached)
    try:
        response = get_client().get(
            path,
            params=params,
            headers=_forwarded_headers(client_ip),
            timeout=timeout if timeout is not None else httpx.USE_CLIENT_DEFAULT,
        )
    except httpx.RequestError as error:
        logger.warning("Serwis AI niedostępny (GET %s): %s", path, type(error).__name__)
        _mark_unavailable()
        return _stale_or_raise(cached)
    _mark_available()

    if response.status_code >= 500:
        logger.warning("Serwis AI zwrócił %s dla GET %s", response.status_code, path)
        return _stale_or_raise(cached)

    body = _parse_body(response)
    if response.status_code == 200:
        cache.set(key, body, ttl_seconds=ttl, keep_seconds=settings.ai_stale_max_age_seconds)
    return GatewayResponse(response.status_code, body, "BYPASS" if bypass_cache else "MISS")


def post(path: str, json: Any, *, client_ip: str | None = None) -> GatewayResponse:
    """POST (np. czat) — bez cache: każda wiadomość jest inna."""
    if _breaker_open():
        raise AIServiceUnavailableError
    try:
        response = get_client().post(path, json=json, headers=_forwarded_headers(client_ip))
    except httpx.RequestError as error:
        logger.warning("Serwis AI niedostępny (POST %s): %s", path, type(error).__name__)
        _mark_unavailable()
        raise AIServiceUnavailableError from error
    _mark_available()
    if response.status_code >= 500:
        logger.warning("Serwis AI zwrócił %s dla POST %s", response.status_code, path)
        raise AIServiceUnavailableError
    return GatewayResponse(response.status_code, _parse_body(response), "BYPASS")


def _stale_or_raise(cached: CacheEntry | None) -> GatewayResponse:
    if cached is not None:
        return GatewayResponse(200, cached.value, "STALE")
    raise AIServiceUnavailableError
