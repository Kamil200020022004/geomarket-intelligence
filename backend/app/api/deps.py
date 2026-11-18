"""Wspólne zależności tras: uwierzytelnienie użytkownika na podstawie nagłówka `Authorization: Bearer`."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.models import User, UserSession
from app.db.session import get_db
from app.services import auth_service

# auto_error=False: brak nagłówka obsługujemy sami, żeby zwrócić 401 w formacie {"detail": ...}.
bearer_scheme = HTTPBearer(auto_error=False, description="Token JWT z /auth/login")


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserSession:
    if credentials is None:
        raise _unauthorized("Wymagane logowanie.")
    session = auth_service.get_active_session(db, credentials.credentials)
    if session is None:
        raise _unauthorized("Sesja wygasła. Zaloguj się ponownie.")
    return session


def get_current_user(session: UserSession = Depends(get_current_session)) -> User:
    """Właściciel danych zawsze z tokenu — nigdy z identyfikatora przysłanego przez przeglądarkę."""
    return session.user
