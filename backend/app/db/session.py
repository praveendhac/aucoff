"""Database access with a per-service credential and a per-transaction tenant context.

Rules enforced here (constitution ZT-6, DB-3, DB-5):
* the service connects with its own login role over TLS, verifying the server certificate;
* every unit of work runs in a transaction that first sets `app.tenant_id` locally, so Row-Level
  Security sees the caller's tenant; without a tenant context queries return no rows.
"""

import ssl
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.core.config import Settings


def database_url(settings: Settings) -> URL:
    if not (settings.db_host and settings.db_user and settings.db_password):
        raise RuntimeError(
            "Database configuration is incomplete: set AUCOFF_DB_HOST, AUCOFF_DB_USER and "
            "AUCOFF_DB_PASSWORD. Each service uses its own credential (ZT-6)."
        )
    return URL.create(
        "postgresql+asyncpg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


def create_engine(settings: Settings) -> AsyncEngine:
    connect_args: dict[str, Any] = {}
    if settings.db_ssl:
        context = ssl.create_default_context(cafile=settings.db_ca_file)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        connect_args["ssl"] = context  # verifies the certificate chain and the host name
    return create_async_engine(
        database_url(settings), connect_args=connect_args, pool_pre_ping=True, pool_size=5
    )


@asynccontextmanager
async def tenant_connection(
    engine: AsyncEngine, tenant_id: uuid.UUID
) -> AsyncIterator[AsyncConnection]:
    """Open a transaction scoped to one tenant (RLS reads `app.tenant_id`)."""
    async with engine.begin() as conn:
        await conn.execute(
            text("select set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": str(tenant_id)},
        )
        yield conn


async def ping(engine: AsyncEngine) -> bool:
    async with engine.connect() as conn:
        return bool((await conn.execute(text("select 1"))).scalar_one() == 1)
