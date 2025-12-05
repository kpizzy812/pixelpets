import os
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection

from alembic import context

# Import database Base for models (from base.py to avoid settings import)
from app.core.base import Base
from app.models import *  # noqa: F401, F403 - Import all models for autogenerate

# this is the Alembic Config object
config = context.config

# Get DATABASE_URL from environment directly (more reliable for migrations)
database_url = os.environ.get("DATABASE_URL", "")
# Convert async URL to sync for alembic
if database_url.startswith("postgresql+asyncpg://"):
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
elif database_url.startswith("postgresql://"):
    sync_url = database_url
else:
    sync_url = database_url

if sync_url:
    config.set_main_option("sqlalchemy.url", sync_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model's MetaData for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
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
