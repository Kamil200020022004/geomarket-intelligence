"""Połączenie z MySQL: silnik (pula połączeń) i sesje na czas jednego żądania HTTP."""

from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

engine = create_engine(
    get_settings().database_url,
    # Przed użyciem połączenia z puli sprawdza, czy nadal żyje (MySQL zamyka bezczynne połączenia).
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Zależność FastAPI: otwiera sesję na czas żądania i zawsze ją zamyka."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database() -> bool:
    """Zwraca True, jeśli baza odpowiada na proste zapytanie."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
