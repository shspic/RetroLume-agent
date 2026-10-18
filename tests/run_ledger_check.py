"""在 TASK-048 专用合成数据库中应用 001/002 并运行八类真实 PG 检查。"""

from __future__ import annotations

import os
from pathlib import Path
import platform
import sys
import unittest

import psycopg
import uvicorn


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DSN = os.environ.get("RETROLUME_TASK_048_DATABASE_URL", "")
REMAINING_TESTS = (
    "test_activity_ledger.ActivityLedgerPostgresTests.test_02_concurrent_duplicate_operation_gets_one_permit",
    "test_activity_ledger.ActivityLedgerPostgresTests.test_03_nonpositive_creation_and_exhausted_limit_are_denied",
    "test_activity_ledger.ActivityLedgerPostgresTests.test_04_source_version_replacement_revokes_admission",
    "test_activity_ledger.ActivityLedgerPostgresTests.test_05_cancel_increments_generation_and_consumes_pending_permit",
    "test_activity_ledger.ActivityLedgerPostgresTests.test_06_unknown_survives_new_connection_and_keeps_budget",
    "test_activity_ledger.ActivityLedgerPostgresTests.test_07_same_outcome_is_idempotent_and_conflict_cannot_overwrite",
    "test_activity_ledger.ActivityLedgerPostgresTests.test_08_transaction_failure_leaves_no_partial_reservation",
)


def apply_migration_if_needed(connection: psycopg.Connection, table: str, path: Path) -> None:
    exists = connection.execute("SELECT to_regclass(%s)", (f"public.{table}",)).fetchone()[0]
    if exists is None:
        connection.execute(path.read_text(encoding="utf-8"))


def main() -> int:
    if not DSN:
        print("RETROLUME_TASK_048_DATABASE_URL is required", file=sys.stderr)
        return 2
    sys.path.insert(0, str(BACKEND))
    loop_factory = uvicorn.Config(
        "app.main:create_app",
        factory=True,
        loop="app.runtime:psycopg_compatible_loop_factory",
    ).get_loop_factory()
    if loop_factory is None:
        print("Uvicorn did not resolve the configured loop factory", file=sys.stderr)
        return 2
    loop = loop_factory()
    try:
        loop_type = f"{type(loop).__module__}.{type(loop).__name__}"
        print(
            "uvicorn_loop_factory="
            f"{loop_factory.__module__}:{loop_factory.__name__} loop={loop_type}"
        )
        if sys.platform == "win32" and "Selector" not in type(loop).__name__:
            print("Windows loop is not Selector-compatible", file=sys.stderr)
            return 2
    finally:
        loop.close()
    with psycopg.connect(DSN, autocommit=True) as connection:
        info = connection.info
        server = connection.execute("SHOW server_version").fetchone()[0]
        print(f"python={platform.python_version()} psycopg={psycopg.__version__} postgres={server}")
        print(f"target host={info.host} port={info.port} dbname={info.dbname} user={info.user}")
        apply_migration_if_needed(connection, "material_sources", BACKEND / "migrations" / "001_materials.sql")
        apply_migration_if_needed(connection, "activities", BACKEND / "migrations" / "002_activities.sql")
    sys.path.insert(0, str(BACKEND / "tests"))
    suite = unittest.defaultTestLoader.loadTestsFromNames(REMAINING_TESTS)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
