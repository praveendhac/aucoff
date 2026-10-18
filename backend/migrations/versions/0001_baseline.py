"""Baseline schema: tenancy, identity, reference roles and the hash-chained audit log.

Revision ID: 0001
Revises:
Implements database-spec.md sections 3.1, 3.5, 6.1 and 6.2 and constitution DB-3, DB-4, DB-7:
* every tenant table has `tenant_id` and FORCED Row-Level Security that fails closed;
* the runtime group role `aucoff_app` has DML only on tenant tables and INSERT only on the audit log;
* the audit log is append-only and hash-chained per tenant (tamper evident).
Statements run one at a time because the asyncpg driver prepares each statement.
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

UPGRADE = [
    # ---- schemas and default lock-down -------------------------------------------------------
    "create schema if not exists app",
    "create schema if not exists ref",
    "create schema if not exists audit",
    "revoke all on schema public from public",
    "grant usage on schema app, ref to aucoff_app, aucoff_readonly",
    "grant usage on schema audit to aucoff_app, aucoff_audit_reader",
    # ---- tenant context helper (fails closed: no setting -> NULL -> no rows) ------------------
    """
    create function app.current_tenant_id() returns uuid
    language sql stable
    as $$ select nullif(current_setting('app.tenant_id', true), '')::uuid $$
    """,
    "revoke all on function app.current_tenant_id() from public",
    "grant execute on function app.current_tenant_id() to aucoff_app, aucoff_readonly, aucoff_audit_reader",
    # ---- reference data (shared, read-only for the runtime) -----------------------------------
    """
    create table ref.roles (
        id uuid primary key default uuidv7(),
        name text not null unique,
        description text not null,
        permissions jsonb not null default '{}'::jsonb
    )
    """,
    """
    insert into ref.roles (name, description) values
        ('compliance_officer', 'Owns mappings, assessments and approvals'),
        ('auditor', 'Read-only review of evidence, results and the audit trail'),
        ('engineer', 'Provides technical evidence and remediates findings'),
        ('executive', 'Dashboards and posture summaries'),
        ('ciso', 'Owns posture; approves risk acceptance and exports'),
        ('admin', 'Tenant administration: users, roles, SSO, integrations'),
        ('external_auditor', 'Scoped, time-boxed read-only access')
    """,
    "grant select on ref.roles to aucoff_app, aucoff_readonly",
    # ---- tenants -------------------------------------------------------------------------------
    """
    create table app.tenants (
        id uuid primary key default uuidv7(),
        name text not null,
        slug text not null unique check (slug ~ '^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$'),
        region text not null,
        status text not null default 'active' check (status in ('active', 'suspended', 'offboarding')),
        created_at timestamptz not null default now()
    )
    """,
    "alter table app.tenants enable row level security",
    "alter table app.tenants force row level security",
    "create policy tenant_isolation on app.tenants using (id = app.current_tenant_id())",
    # The runtime can read its own tenant; creating or deleting tenants is a platform-operator path.
    "grant select on app.tenants to aucoff_app, aucoff_readonly",
    # ---- users ---------------------------------------------------------------------------------
    """
    create table app.users (
        id uuid primary key default uuidv7(),
        tenant_id uuid not null references app.tenants (id),
        email text not null,
        display_name text not null,
        idp_subject text,
        status text not null default 'active' check (status in ('active', 'disabled')),
        last_login_at timestamptz,
        created_at timestamptz not null default now(),
        unique (tenant_id, id)
    )
    """,
    "create unique index users_tenant_email_key on app.users (tenant_id, lower(email))",
    "alter table app.users enable row level security",
    "alter table app.users force row level security",
    """
    create policy tenant_isolation on app.users
        using (tenant_id = app.current_tenant_id())
        with check (tenant_id = app.current_tenant_id())
    """,
    "grant select, insert, update, delete on app.users to aucoff_app",
    "grant select on app.users to aucoff_readonly",
    # ---- user_roles (composite FK makes cross-tenant links impossible) -------------------------
    """
    create table app.user_roles (
        tenant_id uuid not null,
        user_id uuid not null,
        role_id uuid not null references ref.roles (id),
        granted_at timestamptz not null default now(),
        primary key (tenant_id, user_id, role_id),
        foreign key (tenant_id, user_id) references app.users (tenant_id, id) on delete cascade
    )
    """,
    "alter table app.user_roles enable row level security",
    "alter table app.user_roles force row level security",
    """
    create policy tenant_isolation on app.user_roles
        using (tenant_id = app.current_tenant_id())
        with check (tenant_id = app.current_tenant_id())
    """,
    "grant select, insert, update, delete on app.user_roles to aucoff_app",
    "grant select on app.user_roles to aucoff_readonly",
    # ---- audit log: append-only, hash-chained per tenant ---------------------------------------
    """
    create table audit.audit_log (
        seq bigint generated always as identity primary key,
        id uuid not null default uuidv7() unique,
        tenant_id uuid not null,
        chain_pos bigint not null default 0,
        occurred_at timestamptz not null default now(),
        actor_type text not null,
        actor_id text not null,
        action text not null,
        target_type text,
        target_id text,
        outcome text not null check (outcome in ('success', 'failure', 'denied')),
        request_id text,
        details jsonb not null default '{}'::jsonb,
        prev_hash bytea not null,
        row_hash bytea not null
    )
    """,
    # chain_pos is assigned inside the per-tenant lock, so chain order is gap-free and race-free
    # (seq is assigned before the trigger runs and could interleave between concurrent writers).
    "create unique index audit_log_tenant_chain on audit.audit_log (tenant_id, chain_pos)",
    "alter table audit.audit_log enable row level security",
    # Not FORCEd: the SECURITY DEFINER chain function runs as the owner and must see prior rows.
    """
    create policy audit_insert on audit.audit_log for insert to aucoff_app
        with check (tenant_id = app.current_tenant_id())
    """,
    """
    create policy audit_read on audit.audit_log for select to aucoff_audit_reader
        using (tenant_id = app.current_tenant_id())
    """,
    """
    create function audit.canonical(r audit.audit_log) returns bytea
    language sql immutable
    as $$
        select convert_to(concat_ws('|', r.tenant_id, r.chain_pos, r.id,
            to_char(r.occurred_at at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US'),
            r.actor_type, r.actor_id, r.action, coalesce(r.target_type, ''),
            coalesce(r.target_id, ''), r.outcome, coalesce(r.request_id, ''), r.details::text), 'UTF8')
    $$
    """,
    """
    create function audit.chain_row() returns trigger
    language plpgsql security definer set search_path = pg_catalog, audit
    as $$
    declare
        prev bytea;
        pos bigint;
    begin
        perform pg_advisory_xact_lock(hashtextextended(new.tenant_id::text, 0));
        select row_hash, chain_pos into prev, pos from audit.audit_log
            where tenant_id = new.tenant_id order by chain_pos desc limit 1;
        new.chain_pos := coalesce(pos, 0) + 1;
        new.occurred_at := clock_timestamp();
        new.prev_hash := coalesce(prev, decode(repeat('00', 32), 'hex'));
        new.row_hash := sha256(new.prev_hash || audit.canonical(new));
        return new;
    end
    $$
    """,
    "revoke all on function audit.chain_row() from public",
    """
    create trigger audit_chain before insert on audit.audit_log
        for each row execute function audit.chain_row()
    """,
    """
    create function audit.forbid_change() returns trigger
    language plpgsql
    as $$ begin raise exception 'audit_log is append-only'; end $$
    """,
    """
    create trigger audit_no_update before update or delete on audit.audit_log
        for each row execute function audit.forbid_change()
    """,
    """
    create trigger audit_no_truncate before truncate on audit.audit_log
        for each statement execute function audit.forbid_change()
    """,
    """
    create function audit.verify_chain(p_tenant uuid) returns boolean
    language plpgsql security definer set search_path = pg_catalog, audit
    as $$
    declare
        r audit.audit_log;
        expected_prev bytea := decode(repeat('00', 32), 'hex');
        expected_pos bigint := 1;
    begin
        for r in select * from audit.audit_log where tenant_id = p_tenant order by chain_pos loop
            if r.chain_pos <> expected_pos
               or r.prev_hash <> expected_prev
               or r.row_hash <> sha256(r.prev_hash || audit.canonical(r)) then
                return false;
            end if;
            expected_prev := r.row_hash;
            expected_pos := expected_pos + 1;
        end loop;
        return true;
    end
    $$
    """,
    "revoke all on function audit.verify_chain(uuid) from public",
    "grant execute on function audit.verify_chain(uuid) to aucoff_audit_reader",
    # The runtime may only INSERT; it cannot read, update or delete audit rows.
    "revoke all on audit.audit_log from public",
    "grant insert on audit.audit_log to aucoff_app",
    "grant select on audit.audit_log to aucoff_audit_reader",
]

DOWNGRADE = [
    "drop schema audit cascade",
    "drop schema app cascade",
    "drop schema ref cascade",
]


def upgrade() -> None:
    for statement in UPGRADE:
        op.execute(statement)


def downgrade() -> None:
    for statement in DOWNGRADE:
        op.execute(statement)
