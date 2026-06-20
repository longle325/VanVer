from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from core.config import settings
from core.database import Base, _prepare_url
from migrations.baseline import should_stamp_legacy_schema
from migrations.url_config import escape_configparser_value
import models.db_models  # noqa: F401

# Same normalization the app uses (strips sslmode, maps it to asyncpg ssl args).
_clean_url, _connect_args = _prepare_url(settings.DATABASE_URL)

config = context.config
config.set_main_option("sqlalchemy.url", escape_configparser_value(_clean_url))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def stamp_existing_schema_if_needed(connection: Connection) -> None:
    inspector = inspect(connection)
    if should_stamp_legacy_schema(
        inspector.get_table_names(),
        target_metadata.tables.keys(),
    ):
        context.get_context().stamp(ScriptDirectory.from_config(config), "head")


def run_migrations_offline() -> None:
    context.configure(
        url=_clean_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    stamp_existing_schema_if_needed(connection)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=_connect_args,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
