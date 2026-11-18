"""Kryptografia kont: hashowanie haseł (Argon2id), tokeny JWT i tokeny resetu hasła."""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import get_settings

# Argon2id z parametrami domyślnymi biblioteki argon2-cffi (zgodnymi z zaleceniami RFC 9106).
# Hash w formacie PHC zawiera algorytm, parametry i sól, np. "$argon2id$v=19$m=65536,t=3,p=4$...".
_password_hasher = PasswordHasher()

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Porównanie w stałym czasie realizuje biblioteka; błędny lub uszkodzony hash = False."""
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    """True, gdy hash powstał ze słabszymi parametrami niż obecne (np. po ich podniesieniu)."""
    return _password_hasher.check_needs_rehash(password_hash)


# Hash używany przy logowaniu na nieistniejące konto, żeby czas odpowiedzi nie zdradzał,
# czy adres e-mail jest zarejestrowany.
DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(16))


@dataclass(frozen=True)
class TokenClaims:
    user_id: str
    session_id: str


def create_access_token(user_id: str, session_id: str, expires_at: datetime) -> str:
    """JWT podpisany HS256. `sub` = użytkownik, `jti` = sesja (do unieważnienia przy wylogowaniu)."""
    payload = {
        "sub": user_id,
        "jti": session_id,
        "iat": datetime.now(UTC),
        "exp": expires_at,
    }
    return jwt.encode(payload, get_settings().jwt_secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> TokenClaims | None:
    """Zwraca dane tokenu albo None, gdy podpis jest zły, token wygasł lub brakuje pól."""
    try:
        payload = jwt.decode(
            token,
            get_settings().jwt_secret_key,
            # Jawna lista algorytmów chroni przed atakiem podmiany algorytmu (np. "none").
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "jti", "exp", "iat"]},
        )
    except jwt.PyJWTError:
        return None
    return TokenClaims(user_id=str(payload["sub"]), session_id=str(payload["jti"]))


def access_token_expiry() -> datetime:
    return datetime.now(UTC) + timedelta(minutes=get_settings().access_token_ttl_minutes)


def generate_reset_token() -> str:
    """Losowy token resetu (256 bitów entropii), bezpieczny w adresie URL."""
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    """SHA-256 wystarcza: token jest losowy i długi, więc nie da się go odgadnąć słownikiem."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
