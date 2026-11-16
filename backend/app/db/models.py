"""Rejestr modeli SQLAlchemy.

Każdy nowy moduł z modelami importujemy tutaj, żeby Alembic widział jego tabele.
Modele kont, tokenów i ulubionych dochodzą w etapie 1.
"""

from app.db.base import Base  # noqa: F401
