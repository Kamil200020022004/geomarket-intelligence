from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

# Wyznaczenie katalogu głównego repozytorium (niezależnie od miejsca uruchomienia Uvicorna)
_CURRENT_FILE = Path(__file__).resolve()
_REPO_ROOT = (
    _CURRENT_FILE.parents[3]
    if (_CURRENT_FILE.parents[3] / ".git").exists()
    else _CURRENT_FILE.parents[2]
)
_DEFAULT_LAKEHOUSE = str(_REPO_ROOT / "data" / "lakehouse")


class Settings:
    APP_NAME = os.getenv("APP_NAME", "GeoMarket Intelligence AI")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    FRED_API_KEY = os.getenv("FRED_API_KEY")
    LAKEHOUSE_ROOT = os.getenv("LAKEHOUSE_ROOT", _DEFAULT_LAKEHOUSE)


settings = Settings()