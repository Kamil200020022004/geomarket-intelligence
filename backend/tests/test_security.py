"""Testy jednostkowe kryptografii kont (bez bazy danych)."""

from datetime import UTC, datetime, timedelta

import jwt

from app.core import security
from app.core.config import get_settings


def test_password_hash_is_argon2id_with_random_salt():
    first = security.hash_password("tajnehaslo1")
    second = security.hash_password("tajnehaslo1")
    assert first.startswith("$argon2id$")
    assert first != second  # inna sól = inny hash tego samego hasła
    assert "tajnehaslo1" not in first


def test_verify_password_accepts_correct_and_rejects_wrong():
    password_hash = security.hash_password("tajnehaslo1")
    assert security.verify_password("tajnehaslo1", password_hash)
    assert not security.verify_password("zlehaslo", password_hash)
    assert not security.verify_password("tajnehaslo1", "to-nie-jest-hash")


def test_access_token_roundtrip():
    expires = datetime.now(UTC) + timedelta(minutes=5)
    token = security.create_access_token("user-1", "session-1", expires)
    claims = security.decode_access_token(token)
    assert claims == security.TokenClaims(user_id="user-1", session_id="session-1")


def test_expired_token_is_rejected():
    token = security.create_access_token("user-1", "session-1", datetime.now(UTC) - timedelta(seconds=1))
    assert security.decode_access_token(token) is None


def test_token_with_wrong_signature_is_rejected():
    payload = {"sub": "u", "jti": "s", "iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(minutes=5)}
    forged = jwt.encode(payload, "inny-sekret-inny-sekret-inny-sekret-12", algorithm="HS256")
    assert security.decode_access_token(forged) is None


def test_unsigned_token_alg_none_is_rejected():
    payload = {"sub": "u", "jti": "s", "iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(minutes=5)}
    unsigned = jwt.encode(payload, None, algorithm="none")
    assert security.decode_access_token(unsigned) is None


def test_token_without_session_id_is_rejected():
    payload = {"sub": "u", "iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(minutes=5)}
    token = jwt.encode(payload, get_settings().jwt_secret_key, algorithm="HS256")
    assert security.decode_access_token(token) is None


def test_reset_token_is_random_and_hash_is_deterministic():
    token = security.generate_reset_token()
    assert len(token) >= 40
    assert token != security.generate_reset_token()
    assert security.hash_reset_token(token) == security.hash_reset_token(token)
    assert len(security.hash_reset_token(token)) == 64
