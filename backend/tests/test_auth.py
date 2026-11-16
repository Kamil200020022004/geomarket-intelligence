"""Testy integracyjne kont `/auth/*` (MySQL w kontenerze, zewnętrzne usługi jako atrapy)."""

from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from sqlalchemy import select, update

from app.core import security
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.models import PasswordResetToken, User, UserSession
from app.db.session import SessionLocal
from app.services import recaptcha_service
from tests.conftest import bearer, login, register

pytestmark = pytest.mark.integration


# --- Rejestracja ---


def test_register_returns_contract_shape(api):
    response = register(api, email="Jan@Example.com", name="  Jan  ")
    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"user", "access_token", "token_type"}
    assert body["token_type"] == "bearer"
    assert set(body["user"]) == {"id", "name", "email"}
    assert body["user"]["email"] == "jan@example.com"  # e-mail zapisany małymi literami
    assert body["user"]["name"] == "Jan"
    assert len(body["user"]["id"]) == 36  # UUID


def test_password_is_stored_as_argon2_hash(api):
    register(api)
    with SessionLocal() as db:
        user = db.scalar(select(User))
    assert user.password_hash.startswith("$argon2id$")
    assert "tajnehaslo1" not in user.password_hash


def test_register_duplicate_email_returns_409(api):
    register(api)
    response = register(api, email="JAN@example.com")
    assert response.status_code == 409
    assert response.json() == {"detail": "Konto z tym adresem już istnieje."}


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "J", "email": "jan@example.com", "password": "tajnehaslo1"},
        {"name": "Jan", "email": "to-nie-email", "password": "tajnehaslo1"},
        {"name": "Jan", "email": "jan@example.com", "password": "krotkie"},
        {"name": "   ", "email": "jan@example.com", "password": "tajnehaslo1"},
    ],
)
def test_register_invalid_data_returns_422(api, payload):
    assert api.post("/auth/register", json=payload).status_code == 422


# --- Logowanie, /me, wylogowanie ---


def test_register_login_me_flow(api):
    user_id = register(api).json()["user"]["id"]
    token = login(api, email="JAN@example.com")
    response = api.get("/auth/me", headers=bearer(token))
    assert response.status_code == 200
    assert response.json() == {"user": {"id": user_id, "name": "Jan", "email": "jan@example.com"}}


def test_login_wrong_password_and_unknown_email_give_same_401(api):
    register(api)
    wrong_password = api.post("/auth/login", json={"email": "jan@example.com", "password": "zlehaslo1"})
    unknown_email = api.post("/auth/login", json={"email": "nikt@example.com", "password": "tajnehaslo1"})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()  # nie zdradzamy, które konto istnieje


def test_me_without_token_returns_401(api):
    response = api.get("/auth/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {"detail": "Wymagane logowanie."}


def test_me_with_garbage_token_returns_401(api):
    assert api.get("/auth/me", headers=bearer("abc.def.ghi")).status_code == 401


def test_logout_revokes_token_on_server(api):
    register(api)
    token = login(api)
    assert api.post("/auth/logout", headers=bearer(token)).status_code == 200
    # Ten sam (wciąż nieprzeterminowany) token jest już bezużyteczny.
    assert api.get("/auth/me", headers=bearer(token)).status_code == 401


def test_logout_affects_only_one_session(api):
    register(api)
    phone, laptop = login(api), login(api)
    api.post("/auth/logout", headers=bearer(phone))
    assert api.get("/auth/me", headers=bearer(laptop)).status_code == 200


def test_expired_session_is_rejected(api):
    register(api)
    token = login(api)
    with SessionLocal() as db:
        db.execute(update(UserSession).values(expires_at=datetime.now(UTC) - timedelta(seconds=1)))
        db.commit()
    assert api.get("/auth/me", headers=bearer(token)).status_code == 401


def test_token_of_deleted_user_is_rejected(api):
    register(api)
    token = login(api)
    with SessionLocal() as db:
        db.delete(db.scalar(select(User)))
        db.commit()
    assert api.get("/auth/me", headers=bearer(token)).status_code == 401


# --- Reset hasła ---


def _token_from_link(link: str) -> str:
    return parse_qs(urlparse(link).query)["token"][0]


def test_forgot_password_unknown_email_gives_same_neutral_message(api, sent_emails):
    register(api)
    known = api.post("/auth/forgot-password", json={"email": "jan@example.com"})
    unknown = api.post("/auth/forgot-password", json={"email": "nikt@example.com"})
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()
    assert len(sent_emails) == 1  # wiadomość tylko do istniejącego konta


def test_reset_link_points_to_frontend_and_db_stores_only_hash(api, sent_emails):
    register(api)
    api.post("/auth/forgot-password", json={"email": "jan@example.com"})
    link = sent_emails[0]["link"]
    assert link.startswith("http://localhost:5173/reset-password?token=")
    token = _token_from_link(link)
    with SessionLocal() as db:
        stored = db.scalar(select(PasswordResetToken))
    assert stored.token_hash == security.hash_reset_token(token)
    assert stored.token_hash != token


def test_full_password_reset_flow(api, sent_emails):
    register(api)
    old_session = login(api)
    api.post("/auth/forgot-password", json={"email": "jan@example.com"})
    token = _token_from_link(sent_emails[0]["link"])

    response = api.post("/auth/reset-password", json={"token": token, "password": "nowehaslo123"})
    assert response.status_code == 200

    assert api.post("/auth/login", json={"email": "jan@example.com", "password": "tajnehaslo1"}).status_code == 401
    assert login(api, password="nowehaslo123")
    # Zmiana hasła wylogowuje wszystkie wcześniejsze sesje.
    assert api.get("/auth/me", headers=bearer(old_session)).status_code == 401


def test_reset_token_is_single_use(api, sent_emails):
    register(api)
    api.post("/auth/forgot-password", json={"email": "jan@example.com"})
    token = _token_from_link(sent_emails[0]["link"])
    assert api.post("/auth/reset-password", json={"token": token, "password": "nowehaslo123"}).status_code == 200
    second = api.post("/auth/reset-password", json={"token": token, "password": "innehaslo123"})
    assert second.status_code == 400
    assert second.json() == {"detail": "Link jest nieprawidłowy lub wygasł. Poproś o nowy."}


def test_expired_reset_token_is_rejected(api, sent_emails):
    register(api)
    api.post("/auth/forgot-password", json={"email": "jan@example.com"})
    token = _token_from_link(sent_emails[0]["link"])
    with SessionLocal() as db:
        db.execute(update(PasswordResetToken).values(expires_at=datetime.now(UTC) - timedelta(seconds=1)))
        db.commit()
    assert api.post("/auth/reset-password", json={"token": token, "password": "nowehaslo123"}).status_code == 400


def test_new_reset_request_invalidates_previous_link(api, sent_emails):
    register(api)
    api.post("/auth/forgot-password", json={"email": "jan@example.com"})
    api.post("/auth/forgot-password", json={"email": "jan@example.com"})
    first, second = (_token_from_link(mail["link"]) for mail in sent_emails)
    assert api.post("/auth/reset-password", json={"token": first, "password": "nowehaslo123"}).status_code == 400
    assert api.post("/auth/reset-password", json={"token": second, "password": "nowehaslo123"}).status_code == 200


def test_unknown_reset_token_is_rejected(api):
    response = api.post("/auth/reset-password", json={"token": "x" * 43, "password": "nowehaslo123"})
    assert response.status_code == 400


# --- reCAPTCHA (atrapa Google) ---


@pytest.fixture
def recaptcha_on(monkeypatch):
    monkeypatch.setattr(get_settings(), "recaptcha_secret_key", "test-recaptcha-secret")
    calls: list[dict] = []

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return self._payload

    def fake_post(url, data, timeout):
        calls.append(data)
        if data["response"] == "dobry-token":
            return FakeResponse({"success": True})
        if data["response"] == "bot-v3":
            return FakeResponse({"success": True, "score": 0.1})
        return FakeResponse({"success": False, "error-codes": ["invalid-input-response"]})

    monkeypatch.setattr(recaptcha_service.httpx, "post", fake_post)
    return calls


def _register_with_captcha(api, captcha):
    payload = {"name": "Jan", "email": "jan@example.com", "password": "tajnehaslo1", "recaptcha_token": captcha}
    return api.post("/auth/register", json=payload)


def test_register_requires_recaptcha_when_enabled(api, recaptcha_on):
    assert _register_with_captcha(api, None).status_code == 400
    assert recaptcha_on == []  # brak tokenu — nawet nie pytamy Google


def test_register_rejects_invalid_recaptcha(api, recaptcha_on):
    response = _register_with_captcha(api, "zly-token")
    assert response.status_code == 400
    assert recaptcha_on[0]["secret"] == "test-recaptcha-secret"


def test_register_rejects_low_recaptcha_v3_score(api, recaptcha_on):
    assert _register_with_captcha(api, "bot-v3").status_code == 400


def test_register_accepts_valid_recaptcha(api, recaptcha_on):
    assert _register_with_captcha(api, "dobry-token").status_code == 201


# --- Rate limiting ---


def test_login_is_rate_limited(api, monkeypatch):
    monkeypatch.setattr(limiter, "enabled", True)
    payload = {"email": "nikt@example.com", "password": "zlehaslo1"}
    statuses = [api.post("/auth/login", json=payload).status_code for _ in range(11)]
    assert statuses[:10] == [401] * 10
    assert statuses[10] == 429
    assert api.post("/auth/login", json=payload).json() == {
        "detail": "Zbyt wiele prób. Odczekaj chwilę i spróbuj ponownie."
    }
