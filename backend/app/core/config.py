"""Konfiguracja aplikacji czytana ze zmiennych środowiskowych i pliku .env.

Wartości poufne (hasła, klucze) nigdy nie są wpisane w kod. Lista wszystkich
zmiennych wraz z opisem znajduje się w pliku `.env.example` w katalogu głównym repozytorium.
"""

import logging
import secrets
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Katalog główny repozytorium (backend/app/core/config.py -> trzy poziomy wyżej).
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Jeden wspólny plik .env w katalogu głównym repozytorium (używa go też Docker Compose).
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Aplikacja ---
    app_env: str = Field(default="development", description="development | test | production")
    log_level: str = "INFO"
    # Adresy frontendu, z których przeglądarka może wołać API (CORS), rozdzielone przecinkami.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- MySQL ---
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "geomarket"
    mysql_user: str = "geomarket"
    mysql_password: str = ""

    # --- Konta i tokeny ---
    # Sekret podpisu JWT (HS256), min. 32 znaki. Pusty: w development/test generowany przy starcie
    # (sesje nie przetrwają restartu), w production — błąd startu.
    jwt_secret_key: str = ""
    # Ważność sesji jak w prototypie logowania: 8 godzin.
    access_token_ttl_minutes: int = 8 * 60
    password_reset_ttl_minutes: int = 15
    # Adres frontendu używany w linku resetu hasła: {FRONTEND_URL}/reset-password?token=...
    frontend_url: str = "http://localhost:5173"
    # Limity zapytań do endpointów kont (ochrona przed zgadywaniem haseł i spamem).
    rate_limit_enabled: bool = True

    # --- Resend (e-maile z linkiem resetu) ---
    resend_api_key: str = ""
    resend_from_email: str = ""

    # --- Google reCAPTCHA (weryfikacja rejestracji) ---
    # Pusty klucz = weryfikacja wyłączona (praca lokalna). Ustawiony = token wymagany.
    recaptcha_secret_key: str = ""
    # Dla reCAPTCHA v3: minimalna ocena (0.0–1.0). Dla v2 odpowiedź nie zawiera oceny i próg jest pomijany.
    recaptcha_min_score: float = 0.5

    # --- Serwis AI Patryka (backend-ai) ---
    # Adres wewnętrzny; przeglądarka nigdy nie łączy się z nim bezpośrednio.
    ai_service_url: str = "http://127.0.0.1:8001"
    # Odpowiedzi Gemini potrafią trwać kilkadziesiąt sekund.
    ai_timeout_seconds: float = 60.0
    # Czas świeżości odpowiedzi w cache (sekundy); po nim odpowiedź jest pobierana ponownie.
    ai_cache_ttl_seconds: int = 600
    news_cache_ttl_seconds: int = 300
    # Jak długo trzymać ostatnią udaną odpowiedź na wypadek awarii serwisu AI (sekundy).
    ai_stale_max_age_seconds: int = 24 * 3600
    # Po błędzie połączenia: przez tyle sekund nie próbujemy ponownie (odpowiedź od razu z cache albo 503).
    ai_retry_after_seconds: float = 15.0

    # --- Dane rynkowe ---
    # test = dane testowe generowane w kodzie (etap 2); lakehouse = tabele Gold (etap 3).
    market_data_source: str = "test"

    # --- Lakehouse (Delta Lake) ---
    # Wspólny katalog główny Lakehouse dla obu potoków (patrz docs/konwencja_lakehouse.md).
    lakehouse_root: Path = REPO_ROOT / "data" / "lakehouse"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        return self._mysql_url(self.mysql_database)

    def _mysql_url(self, database: str) -> str:
        # Sterownik PyMySQL; utf8mb4 obsługuje pełny Unicode (także emoji i polskie znaki).
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{database}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    """Zwraca jedną, współdzieloną instancję ustawień (wczytaną raz przy starcie)."""
    settings = Settings()
    if len(settings.jwt_secret_key) < 32:
        if settings.app_env == "production":
            raise RuntimeError("JWT_SECRET_KEY musi mieć co najmniej 32 znaki w środowisku production.")
        logging.getLogger(__name__).warning(
            "Brak JWT_SECRET_KEY — wygenerowano tymczasowy sekret (sesje nie przetrwają restartu)."
        )
        settings.jwt_secret_key = secrets.token_urlsafe(48)
    return settings
