"""批次pg子进程：新建工具库001—008基线与定向测试；hash捕获在父runner已完成。"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

TOOLS_DB = "retrolume_task092_tools"
ROLE = "retrolume_task092_synth"

TARGETS = [
    "tests.test_activity_tools.ToolPostgresTests",
    "tests.test_activity_results.ActivityResultsPostgresTests.test_03_atomic_commit_idempotent_retry_and_conflict",
    "tests.test_activity_results.ActivityResultsPostgresTests.test_05_close_door_rejects_payload_write_but_allows_unknown",
    "tests.test_activity_results.ActivityResultsPostgresTests.test_16_historical_binding_and_write_free_confirmation",
    "tests.test_activity_time_budget.ActivityTimeBudgetPostgresTests.test_01_settle_normal_path_and_idempotent_retry",
]


def emit(**item):
    print(json.dumps(item, default=str), flush=True)


def apply_baseline(folder: Path) -> list[dict]:
    import psycopg
    dsn = os.environ["RETROLUME_TOOL_TEST_DATABASE_URL"]
    applied = []
    with psycopg.connect(dsn, autocommit=True) as conn:
        identity = conn.execute("SELECT current_database(), current_user").fetchone()
        assert identity == (TOOLS_DB, ROLE), identity
        if os.environ.get("TASK092_NEW_DB") == "1":
            for path in sorted((BACKEND / "migrations").glob("00[1-8]_*.sql")):
                began = datetime.now(timezone.utc)
                conn.execute(path.read_text(encoding="utf-8"))
                applied.append({"file": path.name,
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                "applied_utc": began.isoformat()})
                emit(event="synthetic_baseline_applied", file=path.name)
        # 008 标记：列与具名约束齐备，否则本批不得继续。
        columns = conn.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_name='activities' "
            "AND column_name IN ('max_tool_calls','tools_reserved')").fetchone()[0]
        kind = conn.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_name='activity_operations' "
            "AND column_name='kind'").fetchone()[0]
        constraints = conn.execute(
            "SELECT count(*) FROM pg_constraint WHERE conname IN "
            "('activities_tool_budget_limit','activities_tool_budget_reserved','activities_tool_budget_balance',"
            "'activity_operations_kind_domain','activity_operations_kind_shape')").fetchone()[0]
        assert columns == 2 and kind == 1 and constraints == 5, (columns, kind, constraints)
        emit(event="schema_markers", columns=columns, kind=kind, constraints=constraints)
    return applied


def run_targets(folder: Path, targets: list[str]) -> int:
    before = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((BACKEND / "app").rglob("*.py"))}
    suite = unittest.defaultTestLoader.loadTestsFromNames(targets)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    after = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted((BACKEND / "app").rglob("*.py"))}
    summary = {
        "discovered": suite.countTestCases(),
        "run_including_skips": result.testsRun,
        "executed": result.testsRun - len(result.skipped),
        "skipped": len(result.skipped),
        "passed": result.testsRun - len(result.skipped) - len(result.errors) - len(result.failures),
        "failures": len(result.failures), "errors": len(result.errors),
        "source_unchanged": before == after,
        "targets": targets,
    }
    (folder / "case-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    emit(event="case_summary", **summary)
    return 0 if result.wasSuccessful() and before == after else 1


def main(folder: Path) -> int:
    applied = apply_baseline(folder)
    (folder / "migration-applied.json").write_text(json.dumps(applied, indent=2), encoding="utf-8")
    override = os.environ.get("TASK092_PG_TARGETS")
    targets = json.loads(override) if override else TARGETS + sys.argv[3:]
    return run_targets(folder, targets)


if __name__ == "__main__":
    assert sys.argv[1] == "--child"
    try:
        code = main(Path(sys.argv[2]))
    except BaseException as exc:
        emit(event="child_error", type=type(exc).__name__,
             label=str(exc) if type(exc) is AssertionError else None)
        code = 1
    raise SystemExit(code)
