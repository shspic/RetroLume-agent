"""续作03 E2子进程：对最终版冻结的11个缺证工具PG方法定向运行（工具库，只读迁移面）。"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

TOOLS_DB = "retrolume_task092_tools"
ROLE = "retrolume_task092_synth"

# 冻结的缺证方法清单（real-01以旧版夹具执行；c7/c9已由real-03对最终版真实通过，排除）。
TARGETS = [
    "tests.test_activity_tools.ToolPostgresTests.test_c1_tool_operation_conditional_constraints",
    "tests.test_activity_tools.ToolPostgresTests.test_c1_budget_check_rejections_and_repeat_008_rollback",
    "tests.test_activity_tools.ToolPostgresTests.test_c2_mark_and_record_reject_wrong_identity",
    "tests.test_activity_tools.ToolPostgresTests.test_c3_rejected_admit_leaves_no_trace_and_no_refund_of_unknown",
    "tests.test_activity_tools.ToolPostgresTests.test_c3_whitelist_null_zero_and_exhaustion",
    "tests.test_activity_tools.ToolPostgresTests.test_c4_model_key_occupied_and_winner_crash_zero_execution",
    "tests.test_activity_tools.ToolPostgresTests.test_c4_same_key_two_connections_single_permit_and_execution",
    "tests.test_activity_tools.ToolPostgresTests.test_c5_read_list_typed_and_parent_isolation",
    "tests.test_activity_tools.ToolPostgresTests.test_c6_admit_and_mark_commit_boundaries",
    "tests.test_activity_tools.ToolPostgresTests.test_c8_committed_record_response_loss_and_write_free_confirmation",
    "tests.test_activity_tools.ToolPostgresTests.test_c12_settle_and_close_facts_with_tool_budget",
]


def emit(**item):
    print(json.dumps(item, default=str), flush=True)


def main(folder: Path) -> int:
    import psycopg
    dsn = os.environ["RETROLUME_TOOL_TEST_DATABASE_URL"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        identity = conn.execute("SELECT current_database(), current_user").fetchone()
        assert identity == (TOOLS_DB, ROLE), identity
        columns = conn.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_name='activities' "
            "AND column_name IN ('max_tool_calls','tools_reserved')").fetchone()[0]
        kind = conn.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_name='activity_operations' "
            "AND column_name='kind'").fetchone()[0]
        assert columns == 2 and kind == 1, (columns, kind)
        emit(event="database_identity", db=identity[0], role=identity[1], markers=(columns, kind))
    before = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((BACKEND / "app").rglob("*.py"))}
    suite = unittest.defaultTestLoader.loadTestsFromNames(TARGETS)
    began = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    elapsed = time.monotonic() - began
    after = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted((BACKEND / "app").rglob("*.py"))}
    summary = {"discovered": suite.countTestCases(), "run_including_skips": result.testsRun,
               "executed": result.testsRun - len(result.skipped), "skipped": len(result.skipped),
               "passed": result.testsRun - len(result.skipped) - len(result.errors) - len(result.failures),
               "failures": len(result.failures), "errors": len(result.errors),
               "source_unchanged": before == after, "seconds": round(elapsed, 3), "targets": TARGETS}
    (folder / "case-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    emit(event="case_summary", **summary)
    return 0 if result.wasSuccessful() and before == after else 1


if __name__ == "__main__":
    assert sys.argv[1] == "--child"
    try:
        code = main(Path(sys.argv[2]))
    except BaseException as exc:
        emit(event="child_error", type=type(exc).__name__,
             label=str(exc) if type(exc) is AssertionError else None)
        code = 1
    raise SystemExit(code)
