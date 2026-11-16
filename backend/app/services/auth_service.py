"""Logika kont: rejestracja, logowanie, sesje, reset hasła.

Nowa implementacja na MySQL i standardowym JWT, zastępująca prototyp na pliku Excel
(`backend-ai/app/auth_excel.py`, `password_reset.py`, autor: Kamil). Kontrakt odpowiedzi zachowany.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import get_settings
from app.db.models import PasswordResetToken, User, UserSession


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidResetTokenError(Exception):
    pass


@dataclass(frozen=True)
class LoginResult:
    user: User
    access_token: str


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register_user(db: Session, name: str, email: str, password: str) -> LoginResult:
    user = User(name=name, email=normalize_email(email), password_hash=security.hash_password(password))
    db.add(user)
    try:
        db.flush()
    except IntegrityError as error:
        # Unikalny indeks na e-mailu chroni także przed dwiema równoległymi rejestracjami.
        db.rollback()
        raise EmailAlreadyRegisteredError from error
    result = _start_session(db, user)
    db.commit()
    return result


def login(db: Session, email: str, password: str) -> LoginResult:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    if user is None:
        # Weryfikacja na atrapie wyrównuje czas odpowiedzi — nie zdradza, czy konto istnieje.
        security.verify_password(password, security.DUMMY_PASSWORD_HASH)
        raise InvalidCredentialsError
    if not security.verify_password(password, user.password_hash):
        raise InvalidCredentialsError
    if security.password_needs_rehash(user.password_hash):
        user.password_hash = security.hash_password(password)
    result = _start_session(db, user)
    db.commit()
    return result


def _start_session(db: Session, user: User) -> LoginResult:
    expires_at = security.access_token_expiry()
    session = UserSession(user_id=user.id, expires_at=expires_at)
    db.add(session)
    db.flush()  # nadaje identyfikator sesji
    token = security.create_access_token(user.id, session.id, expires_at)
    return LoginResult(user=user, access_token=token)


def get_active_session(db: Session, token: str) -> UserSession | None:
    """Sesja dla tokenu, jeśli token jest poprawny, a sesja istnieje, nie wygasła i nie została unieważniona."""
    claims = security.decode_access_token(token)
    if claims is None:
        return None
    session = db.get(UserSession, claims.session_id)
    if (
        session is None
        or session.user_id != claims.user_id
        or session.revoked_at is not None
        or session.expires_at <= datetime.now(UTC)
    ):
        return None
    return session


def logout(db: Session, session: UserSession) -> None:
    session.revoked_at = datetime.now(UTC)
    db.commit()


def revoke_all_sessions(db: Session, user_id: str) -> None:
    db.execute(
        update(UserSession)
        .where(UserSession.user_id == user_id, UserSession.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )


def create_password_reset(db: Session, email: str) -> tuple[User, str] | None:
    """Tworzy jednorazowy token resetu. Zwraca (użytkownik, token) albo None, gdy konta nie ma."""
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    if user is None:
        return None
    now = datetime.now(UTC)
    # Nowy link unieważnia poprzednie, jeszcze niewykorzystane.
    db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))
        .values(used_at=now)
    )
    token = security.generate_reset_token()
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=security.hash_reset_token(token),
            expires_at=now + timedelta(minutes=get_settings().password_reset_ttl_minutes),
        )
    )
    db.commit()
    return user, token


def reset_password(db: Session, token: str, new_password: str) -> None:
    now = datetime.now(UTC)
    reset = db.scalar(
        select(PasswordResetToken)
        .where(PasswordResetToken.token_hash == security.hash_reset_token(token))
        # Blokada wiersza: dwa równoległe żądania z tym samym tokenem nie wykorzystają go dwukrotnie.
        .with_for_update()
    )
    if reset is None or reset.used_at is not None or reset.expires_at <= now:
        db.rollback()
        raise InvalidResetTokenError
    user = db.get(User, reset.user_id)
    if user is None:
        db.rollback()
        raise InvalidResetTokenError
    user.password_hash = security.hash_password(new_password)
    reset.used_at = now
    # Po zmianie hasła wylogowujemy wszystkie urządzenia (np. gdy ktoś przejął sesję).
    revoke_all_sessions(db, user.id)
    db.commit()
