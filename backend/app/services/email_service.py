"""Wysyłka e-maili przez API Resend (https://resend.com/docs/api-reference/emails/send-email).

Treść wiadomości resetującej przejęta z prototypu logowania (Kamil), z tymi samymi
zmiennymi konfiguracyjnymi: RESEND_API_KEY, RESEND_FROM_EMAIL.
"""

import html
import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


class EmailNotConfiguredError(RuntimeError):
    pass


def send_password_reset_email(email: str, link: str, ttl_minutes: int) -> None:
    """Wysyła link resetu. Wywoływane w tle (po wysłaniu odpowiedzi HTTP), więc błędy tylko loguje."""
    settings = get_settings()
    if not settings.resend_api_key or not settings.resend_from_email:
        if settings.app_env == "development":
            # Wygoda pracy lokalnej bez konta Resend. Nigdy w production.
            logger.warning("Resend nie jest skonfigurowany. Link resetu (tylko development): %s", link)
            return
        logger.error("Resend nie jest skonfigurowany — wiadomość resetująca nie została wysłana.")
        return

    safe_link = html.escape(link, quote=True)
    payload = {
        "from": settings.resend_from_email,
        "to": [email],
        "subject": "GeoMarket - resetowanie hasła",
        "html": (
            "<p>Otrzymaliśmy prośbę o zmianę hasła do konta GeoMarket Intelligence.</p>"
            f'<p><a href="{safe_link}">Ustaw nowe hasło</a></p>'
            f"<p>Link jest ważny przez {ttl_minutes} minut i może zostać wykorzystany tylko raz.</p>"
            "<p>Jeżeli nie prosiłeś o zmianę hasła, zignoruj tę wiadomość.</p>"
        ),
        "text": (
            "Otrzymaliśmy prośbę o zmianę hasła.\n"
            f"Ustaw nowe hasło: {link}\n"
            f"Link jest ważny przez {ttl_minutes} minut i może zostać wykorzystany tylko raz."
        ),
    }
    try:
        response = httpx.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json=payload,
            timeout=15.0,
        )
    except httpx.RequestError as error:
        logger.error("Błąd połączenia z Resend: %s", type(error).__name__)
        return
    if response.is_success:
        logger.info("Resend przyjął wiadomość resetującą.")
    else:
        # Bez adresu e-mail w logach (dane osobowe).
        logger.error("Resend odrzucił wiadomość: HTTP %s %s", response.status_code, response.text[:500])
