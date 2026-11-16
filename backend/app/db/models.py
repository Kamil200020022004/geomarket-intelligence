"""Modele tabel MySQL (SQLAlchemy ORM).

Tabele:
- `users`: konta użytkowników,
- `user_sessions`: sesje logowania; każdy token JWT wskazuje swoją sesję (`jti`), co pozwala go unieważnić,
- `password_reset_tokens`: jednorazowe tokeny resetu hasła (w bazie tylko hash),
- `favorites`: ulubione instrumenty użytkownika.

Identyfikatory to UUID zapisane jako tekst (36 znaków), czytelne w narzędziach do bazy
i stabilne (nie zdradzają liczby użytkowników, w przeciwieństwie do kolejnych liczb).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(80))
    # Adres zapisywany małymi literami; unikalność wymusza baza (odporne na równoległe rejestracje).
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    # Hash Argon2id w formacie PHC (zawiera algorytm, parametry i sól).
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        default=utc_now, onupdate=utc_now
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserSession(Base):
    """Sesja logowania. Token JWT jest ważny tylko, gdy jego sesja istnieje i nie jest unieważniona."""

    __tablename__ = "user_sessions"

    # Identyfikator sesji = pole `jti` w tokenie JWT.
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    expires_at: Mapped[datetime] = mapped_column()
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)

    user: Mapped[User] = relationship(back_populates="sessions")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # SHA-256 tokenu (hex). Sam token trafia tylko do maila — wyciek bazy nie pozwala resetować haseł.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    expires_at: Mapped[datetime] = mapped_column()
    used_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        # Ten sam instrument nie może być dwa razy w ulubionych tego samego użytkownika.
        UniqueConstraint("user_id", "type", "item_id", name="uq_favorites_user_type_item"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # stock | crypto | macro
    type: Mapped[str] = mapped_column(String(16))
    # stock/macro → symbol, crypto → id (np. "bitcoin"); jak getFavoriteId() we frontendzie.
    item_id: Mapped[str] = mapped_column(String(64))
    # Migawka obiektu z chwili dodania (frontend wyświetla ją w zakładce Ulubione).
    item: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    user: Mapped[User] = relationship(back_populates="favorites")
