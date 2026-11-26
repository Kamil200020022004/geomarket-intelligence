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
    # FastAPI wykonuje trasy synchroniczne w puli do 40 wątków (AnyIO). Domyślna pula SQLAlchemy
    # (5 + 10 zapasowych) przy 500 użytkownikach w teście obciążeniowym kończyła się błędem
    # „QueuePool limit … reached” — wątki czekały na połączenie dłużej niż 30 s. 20 + 20 = 40
    # połączeń odpowiada liczbie wątków (MySQL domyślnie przyjmuje 151 połączeń).
    pool_size=20,
    max_overflow=20,
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
