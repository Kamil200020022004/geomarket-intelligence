"""Wspólne przygotowanie testów.

Testy pracują na osobnej bazie `<MYSQL_DATABASE>_test` (tworzonej przez skrypt w
docker/mysql-init), nigdy na bazie roboczej. Zmienne środowiskowe ustawiamy PRZED
importem aplikacji, bo mają pierwszeństwo przed plikiem .env.
"""

import os

from dotenv import dotenv_values

from app.core.config import REPO_ROOT

_base_db = os.environ.get("MYSQL_DATABASE") or dotenv_values(REPO_ROOT / ".env").get("MYSQL_DATABASE") or "geomarket"
os.environ["MYSQL_DATABASE"] = os.environ.get("TEST_MYSQL_DATABASE", f"{_base_db}_test")
os.environ["APP_ENV"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-test-secret-key-0123456789"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["RESEND_API_KEY"] = ""
os.environ["RESEND_FROM_EMAIL"] = ""
os.environ["RECAPTCHA_SECRET_KEY"] = ""
os.environ["FRONTEND_URL"] = "http://localhost:5173"

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.rate_limit import limiter  # noqa: E402
from app.db.session import check_database, engine  # noqa: E402
from app.main import create_app  # noqa: E402

BACKEND_DIR = REPO_ROOT / "backend"
TABLES = ("favorites", "password_reset_tokens", "user_sessions", "users")

assert get_settings().mysql_database.endswith("_test"), "Testy muszą działać na bazie testowej!"


@pytest.fixture(scope="session")
def migrated_db():
    """Raz na sesję testów: migracje Alembic na bazie testowej (przy okazji testuje same migracje)."""
    if not check_database():
        pytest.skip("MySQL nie działa — uruchom docker compose up -d")
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(config, "head")
    return engine


@pytest.fixture
def db_clean(migrated_db):
    """Pusta baza przed każdym testem integracyjnym."""
    with migrated_db.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in TABLES:
            connection.execute(text(f"TRUNCATE TABLE {table}"))
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


@pytest.fixture
def client() -> TestClient:
    # raise_server_exceptions=False: testujemy odpowiedź HTTP z handlera błędów, a nie sam wyjątek.
    limiter.reset()
    return TestClient(create_app(), raise_server_exceptions=False)


@pytest.fixture
def api(db_clean, client) -> TestClient:
    """Klient HTTP z czystą bazą — dla testów kont i ulubionych."""
    return client


@pytest.fixture
def sent_emails(monkeypatch) -> list[dict]:
    """Atrapa wysyłki e-maili: zamiast Resend zapisuje wiadomości na liście."""
    from app.services import email_service

    outbox: list[dict] = []

    def fake_send(email: str, link: str, ttl_minutes: int) -> None:
        outbox.append({"email": email, "link": link, "ttl_minutes": ttl_minutes})

    monkeypatch.setattr(email_service, "send_password_reset_email", fake_send)
    return outbox


def register(client: TestClient, email: str = "jan@example.com", password: str = "tajnehaslo1", name: str = "Jan"):
    return client.post("/auth/register", json={"name": name, "email": email, "password": password})


def login(client: TestClient, email: str = "jan@example.com", password: str = "tajnehaslo1") -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
