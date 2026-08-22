"""Alembic environment for the dashboard database."""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from api.models.db_models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

repo_root = Path(config.config_file_name or ".").resolve().parent.parent
backend_root = repo_root / "backend"
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(backend_root))

target_metadata = Base.metadata


def get_database_url() -> str:
    """Prefer the deployed database URL, with a local SQLite fallback."""
    database_url = os.environ.get("DATABASE_URL") or config.get_main_option(
        "sqlalchemy.url"
    )
    if database_url is None:
        raise RuntimeError("Alembic requires sqlalchemy.url or DATABASE_URL")
    return database_url.replace("%", "%%")


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
