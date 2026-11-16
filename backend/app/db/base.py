"""Klasa bazowa modeli SQLAlchemy.

Wszystkie tabele MySQL dziedziczą po `Base`. Alembic porównuje `Base.metadata`
z aktualnym schematem bazy, żeby generować migracje.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
