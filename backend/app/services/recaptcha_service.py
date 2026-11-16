"""Weryfikacja tokenu Google reCAPTCHA po stronie serwera.

Przeglądarka (widget reCAPTCHA we frontendzie) dostaje od Google token. Backend wysyła go
wraz z sekretnym kluczem do endpointu `siteverify` i dopiero na tej podstawie przepuszcza
rejestrację. Sam widget bez tej weryfikacji niczego nie chroni — bot może go pominąć.
Dokumentacja: https://developers.google.com/recaptcha/docs/verify
"""

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


def is_enabled() -> bool:
    return bool(get_settings().recaptcha_secret_key)


def verify_token(token: str | None, remote_ip: str | None = None) -> bool:
    """True, gdy Google potwierdzi token. Brak klucza w konfiguracji = weryfikacja wyłączona."""
    settings = get_settings()
    if not settings.recaptcha_secret_key:
        return True
    if not token:
        return False

    data = {"secret": settings.recaptcha_secret_key, "response": token}
    if remote_ip:
        data["remoteip"] = remote_ip
    try:
        response = httpx.post(VERIFY_URL, data=data, timeout=10.0)
        result = response.json()
    except (httpx.RequestError, ValueError) as error:
        # Niedostępność Google = odmowa (fail closed): lepiej odrzucić rejestrację niż wpuścić boty.
        logger.error("Błąd weryfikacji reCAPTCHA: %s", type(error).__name__)
        return False

    if not result.get("success"):
        logger.info("reCAPTCHA odrzucona: %s", result.get("error-codes"))
        return False
    # reCAPTCHA v3 zwraca ocenę 0.0–1.0 (1.0 = prawie na pewno człowiek); v2 jej nie zwraca.
    score = result.get("score")
    if score is not None and score < settings.recaptcha_min_score:
        logger.info("reCAPTCHA: zbyt niska ocena %.2f", score)
        return False
    return True
