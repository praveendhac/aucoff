"""Throwaway PostgreSQL 18 for database tests.

Starts the official `postgres:18` image with the Docker CLI (no extra Python dependency), creates the
same role layout as the cluster (database-spec 6.1), runs the real Alembic migrations as the migrator
role, and exposes engines that connect as the runtime role. Skips (loudly) if Docker is unavailable.
"""

import os
import secrets
import shutil
import subprocess
import sys
import time
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[2]
IMAGE = "postgres:18"


@dataclass(frozen=True)
class Db:
    port: int
    gateway_password: str
    migrator_password: str
    container: str

    def psql(self, sql: str, database: str = "aucoff") -> str:
        proc = subprocess.run(
            [
                "docker",
                "exec",
                "-i",
                self.container,
                "psql",
                "-U",
                "postgres",
                "-d",
                database,
                "-v",
                "ON_ERROR_STOP=1",
                "-tA",
                "-c",
                sql,
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip())
        return proc.stdout.strip()


def _docker_ok() -> bool:
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "info"], capture_output=True).returncode == 0


@pytest.fixture(scope="session")
def db() -> Iterator[Db]:
    if not _docker_ok():
        pytest.skip("Docker is not available: start Colima/Docker to run the database tests")
    name = f"aucoff-test-pg-{uuid.uuid4().hex[:8]}"
    su = secrets.token_urlsafe(16)
    gw, mg = secrets.token_urlsafe(16), secrets.token_urlsafe(16)
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "--name",
            name,
            "-e",
            f"POSTGRES_PASSWORD={su}",
            "-p",
            "127.0.0.1::5432",
            IMAGE,
        ],
        check=True,
        capture_output=True,
    )
    try:
        port = int(
            subprocess.run(
                ["docker", "port", name, "5432/tcp"], check=True, capture_output=True, text=True
            ).stdout.split(":")[-1]
        )
        probe = Db(port, gw, mg, name)
        for _ in range(60):
            ready = subprocess.run(
                ["docker", "exec", name, "pg_isready", "-U", "postgres"], capture_output=True
            )
            if ready.returncode == 0:
                try:
                    probe.psql("select 1", "postgres")
                    break
                except RuntimeError:
                    pass
            time.sleep(1)
        else:
            raise RuntimeError("PostgreSQL did not become ready")
        for role in ("aucoff_app", "aucoff_readonly", "aucoff_audit_reader"):
            probe.psql(f"create role {role} nologin", "postgres")
        probe.psql(f"create role aucoff_migrator login password '{mg}'", "postgres")
        probe.psql(
            f"create role aucoff_gateway login password '{gw}' in role aucoff_app", "postgres"
        )
        probe.psql("create database aucoff owner aucoff_migrator", "postgres")
        env = {
            **os.environ,
            "AUCOFF_MIGRATOR_HOST": "127.0.0.1",
            "AUCOFF_MIGRATOR_PORT": str(port),
            "AUCOFF_MIGRATOR_USER": "aucoff_migrator",
            "AUCOFF_MIGRATOR_PASSWORD": mg,
            "AUCOFF_MIGRATOR_DB": "aucoff",
            "AUCOFF_MIGRATOR_SSL": "false",
        }
        proc = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=BACKEND,
            env=env,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"migration failed:\n{proc.stderr}")
        yield probe
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)
