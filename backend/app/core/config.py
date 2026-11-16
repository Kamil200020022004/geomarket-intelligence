"""Konfiguracja aplikacji czytana ze zmiennych środowiskowych i pliku .env.

Wartości poufne (hasła, klucze) nigdy nie są wpisane w kod. Lista wszystkich
zmiennych wraz z opisem znajduje się w pliku `.env.example` w katalogu głównym repozytorium.
"""

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
    return Settings()
