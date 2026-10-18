"""Row-Level Security, privilege and audit-log tests (constitution DB-3, DB-4, DB-7, ZT-6)."""

import asyncio
import uuid
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.core.config import Settings
from app.db.session import create_engine, ping, tenant_connection
from tests.db.conftest import Db

pytestmark = pytest.mark.db

TENANT_A = uuid.UUID("11111111-1111-7111-8111-111111111111")
TENANT_B = uuid.UUID("22222222-2222-7222-8222-222222222222")


@pytest.fixture(scope="module")
def seeded(db: Db) -> Db:
    for tid, slug in ((TENANT_A, "tenant-a"), (TENANT_B, "tenant-b")):
        db.psql(
            f"insert into app.tenants (id, name, slug, region) values ('{tid}', '{slug}', '{slug}', 'us') "
            "on conflict do nothing"
        )
    for tid, who in ((TENANT_A, "alice"), (TENANT_B, "bob")):
        db.psql(
            f"insert into app.users (tenant_id, email, display_name) values ('{tid}', '{who}@example.test', '{who}') "
            "on conflict do nothing"
        )
    return db


@pytest.fixture
async def engine(seeded: Db) -> AsyncIterator[AsyncEngine]:
    settings = Settings(
        db_host="127.0.0.1",
        db_port=seeded.port,
        db_name="aucoff",
        db_user="aucoff_gateway",
        db_password=seeded.gateway_password,
        db_ssl=False,
    )
    eng = create_engine(settings)
    yield eng
    await eng.dispose()


async def test_service_connects_with_its_own_non_privileged_role(
    db: Db, engine: AsyncEngine
) -> None:
    assert await ping(engine)
    row = db.psql(
        "select rolsuper, rolbypassrls, rolcreaterole from pg_roles where rolname='aucoff_gateway'"
    )
    assert row == "f|f|f"


async def test_each_tenant_sees_only_its_own_rows(engine: AsyncEngine) -> None:
    async with tenant_connection(engine, TENANT_A) as conn:
        emails = (await conn.execute(text("select email from app.users"))).scalars().all()
        tenants = (await conn.execute(text("select slug from app.tenants"))).scalars().all()
    assert emails == ["alice@example.test"]
    assert tenants == ["tenant-a"]
    async with tenant_connection(engine, TENANT_B) as conn:
        assert (await conn.execute(text("select email from app.users"))).scalars().all() == [
            "bob@example.test"
        ]


async def test_no_tenant_context_returns_no_rows(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        assert (await conn.execute(text("select count(*) from app.users"))).scalar_one() == 0
        assert (await conn.execute(text("select count(*) from app.tenants"))).scalar_one() == 0


async def test_invalid_tenant_context_fails_closed(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text("select set_config('app.tenant_id', 'not-a-uuid', true)"))
        with pytest.raises(DBAPIError):
            await conn.execute(text("select count(*) from app.users"))


async def test_cannot_write_rows_for_another_tenant(engine: AsyncEngine) -> None:
    with pytest.raises(DBAPIError, match="row-level security"):
        async with tenant_connection(engine, TENANT_A) as conn:
            await conn.execute(
                text(
                    "insert into app.users (tenant_id, email, display_name) values (:t, 'x@example.test', 'x')"
                ),
                {"t": TENANT_B},
            )


async def test_cannot_update_or_delete_other_tenants_rows(db: Db, engine: AsyncEngine) -> None:
    async with tenant_connection(engine, TENANT_A) as conn:
        updated = await conn.execute(
            text("update app.users set display_name='hacked' where email='bob@example.test'")
        )
        deleted = await conn.execute(text("delete from app.users where email='bob@example.test'"))
    assert updated.rowcount == 0 and deleted.rowcount == 0
    assert db.psql("select display_name from app.users where email='bob@example.test'") == "bob"


async def test_user_roles_cannot_link_across_tenants(db: Db, engine: AsyncEngine) -> None:
    bob = db.psql("select id from app.users where email='bob@example.test'")
    role = db.psql("select id from ref.roles where name='auditor'")
    with pytest.raises(DBAPIError, match="foreign key"):
        async with tenant_connection(engine, TENANT_A) as conn:
            await conn.execute(
                text(
                    "insert into app.user_roles (tenant_id, user_id, role_id) values (:t, :u, :r)"
                ),
                {"t": TENANT_A, "u": uuid.UUID(bob), "r": uuid.UUID(role)},
            )


async def test_runtime_cannot_manage_tenants_or_reference_data(engine: AsyncEngine) -> None:
    for sql in (
        "insert into app.tenants (name, slug, region) values ('n', 'new-tenant', 'us')",
        "delete from app.tenants",
        "insert into ref.roles (name, description) values ('evil', 'x')",
        "update ref.roles set name = 'x'",
        "create table app.evil (id int)",
    ):
        with pytest.raises(ProgrammingError, match="permission denied"):
            async with tenant_connection(engine, TENANT_A) as conn:
                await conn.execute(text(sql))


async def _audit(conn: AsyncConnection, tenant: uuid.UUID, action: str) -> None:
    await conn.execute(
        text(
            "insert into audit.audit_log (tenant_id, actor_type, actor_id, action, outcome, details) "
            "values (:t, 'user', 'u1', :a, 'success', '{\"k\": 1}'::jsonb)"
        ),
        {"t": tenant, "a": action},
    )


async def test_audit_log_is_insert_only_for_the_runtime(engine: AsyncEngine) -> None:
    async with tenant_connection(engine, TENANT_A) as conn:
        await _audit(conn, TENANT_A, "login")
    for sql in (
        "select * from audit.audit_log",
        "update audit.audit_log set action='x'",
        "delete from audit.audit_log",
        "truncate audit.audit_log",
    ):
        with pytest.raises(ProgrammingError, match="permission denied"):
            async with tenant_connection(engine, TENANT_A) as conn:
                await conn.execute(text(sql))


async def test_audit_insert_for_other_tenant_is_rejected(engine: AsyncEngine) -> None:
    with pytest.raises(DBAPIError, match="row-level security"):
        async with tenant_connection(engine, TENANT_A) as conn:
            await _audit(conn, TENANT_B, "forged")


async def test_audit_chain_is_valid_under_concurrent_inserts(db: Db, engine: AsyncEngine) -> None:
    async def one(i: int) -> None:
        async with tenant_connection(engine, TENANT_A) as conn:
            await _audit(conn, TENANT_A, f"concurrent-{i}")

    await asyncio.gather(*(one(i) for i in range(20)))
    assert db.psql(f"select audit.verify_chain('{TENANT_A}')") == "t"
    rows = int(db.psql(f"select count(*) from audit.audit_log where tenant_id='{TENANT_A}'"))
    assert rows >= 21


async def test_tampering_with_the_audit_log_is_detected(db: Db) -> None:
    with pytest.raises(RuntimeError, match="append-only"):
        db.psql("update audit.audit_log set action='tampered'")  # blocked even for superusers
    # Bypass the guard trigger as a superuser would in an attack, then verify detection.
    db.psql(
        "set session_replication_role = replica; "
        f"update audit.audit_log set action='tampered' where tenant_id='{TENANT_A}' and seq = "
        f"(select min(seq) from audit.audit_log where tenant_id='{TENANT_A}')"
    )
    assert db.psql(f"select audit.verify_chain('{TENANT_A}')") == "f"


async def test_deleting_audit_rows_breaks_the_chain(db: Db) -> None:
    other = "33333333-3333-7333-8333-333333333333"
    db.psql(
        f"insert into app.tenants (id, name, slug, region) values ('{other}', 'c', 'tenant-c', 'us')"
    )
    for i in range(3):
        db.psql(
            "set app.tenant_id = '" + other + "'; "
            f"insert into audit.audit_log (tenant_id, actor_type, actor_id, action, outcome) "
            f"values ('{other}', 'user', 'u', 'a{i}', 'success')"
        )
    assert db.psql(f"select audit.verify_chain('{other}')") == "t"
    db.psql(
        "set session_replication_role = replica; "
        f"delete from audit.audit_log where tenant_id='{other}' and chain_pos = 2"
    )
    assert db.psql(f"select audit.verify_chain('{other}')") == "f"
