"""Konfiguracja Alembic (migracje schematu MySQL).

Adres bazy pochodzi z ustawień aplikacji (`app.core.config`), a nie z alembic.ini,
więc hasło jest tylko w pliku .env. Modele są importowane przez `app.db.models`,
dzięki czemu `alembic revision --autogenerate` widzi wszystkie tabele.

Najczęstsze polecenia (z katalogu backend/):
    alembic upgrade head                                  # zastosuj wszystkie migracje
    alembic revision --autogenerate -m "opis zmiany"      # wygeneruj nową migrację z modeli
    alembic downgrade -1                                  # cofnij ostatnią migrację
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.db.models  # noqa: F401  (rejestruje modele w Base.metadata)
from app.core.config import get_settings
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Pozwala nadpisać adres (np. bazą testową) przez `config.set_main_option("sqlalchemy.url", ...)`.
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generuje SQL bez łączenia się z bazą (alembic upgrade head --sql)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Łączy się z bazą i wykonuje migracje."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
