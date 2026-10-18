"""Alembic environment. Migrations run as the dedicated migrator role (never the runtime role).

Connection settings come from AUCOFF_MIGRATOR_HOST / _PORT / _DB / _USER / _PASSWORD / _CA_FILE
(and AUCOFF_MIGRATOR_SSL=false only for the throwaway test database).
"""

import asyncio
import os
import ssl
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import URL, Connection
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _url() -> URL:
    try:
        return URL.create(
            "postgresql+asyncpg",
            username=os.environ["AUCOFF_MIGRATOR_USER"],
            password=os.environ["AUCOFF_MIGRATOR_PASSWORD"],
            host=os.environ["AUCOFF_MIGRATOR_HOST"],
            port=int(os.environ.get("AUCOFF_MIGRATOR_PORT", "5432")),
            database=os.environ.get("AUCOFF_MIGRATOR_DB", "aucoff"),
        )
    except KeyError as exc:  # fail closed: no defaults for credentials
        raise RuntimeError(f"missing migrator setting {exc}") from exc


def _connect_args() -> dict[str, object]:
    if os.environ.get("AUCOFF_MIGRATOR_SSL", "true").lower() == "false":
        return {}
    ctx = ssl.create_default_context(cafile=os.environ.get("AUCOFF_MIGRATOR_CA_FILE"))
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    return {"ssl": ctx}


def _run(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=None, transaction_per_migration=True)
    with context.begin_transaction():
        context.run_migrations()


async def _run_async() -> None:
    engine = create_async_engine(_url(), connect_args=_connect_args())
    # A freshly started pod can reach DNS and the database a moment after it starts (network
    # policies are programmed asynchronously), so retry the connection a few times.
    last: Exception | None = None
    for attempt in range(1, 11):
        try:
            async with engine.connect() as connection:
                await connection.run_sync(_run)
            await engine.dispose()
            return
        except OSError as exc:  # DNS / connection refused / timeout
            last = exc
            print(f"database not reachable yet (attempt {attempt}/10): {exc}", file=sys.stderr)
            await asyncio.sleep(3)
    raise RuntimeError("database unreachable after 10 attempts") from last


asyncio.run(_run_async())
