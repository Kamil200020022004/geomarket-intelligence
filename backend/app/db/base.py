"""Klasa bazowa modeli SQLAlchemy i wspólne typy kolumn.

Wszystkie tabele MySQL dziedziczą po `Base`. Alembic porównuje `Base.metadata`
z aktualnym schematem bazy, żeby generować migracje.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """Czas zawsze w UTC.

    MySQL `DATETIME` nie przechowuje strefy czasowej. Ten typ przy zapisie zamienia czas
    na UTC i usuwa strefę, a przy odczycie dokleja strefę UTC. Dzięki temu w kodzie
    zawsze porównujemy czasy „świadome strefy” i nie mieszamy czasu lokalnego z UTC.
    """

    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "mysql":
            return dialect.type_descriptor(mysql.DATETIME(fsp=6))  # mikrosekundy
        return dialect.type_descriptor(DateTime())

    def process_bind_param(self, value: datetime | None, dialect: Dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Czas zapisywany do bazy musi mieć strefę czasową (UTC).")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: Dialect):
        if value is None:
            return None
        return value.replace(tzinfo=UTC)


class Base(DeclarativeBase):
    type_annotation_map = {datetime: UTCDateTime}
