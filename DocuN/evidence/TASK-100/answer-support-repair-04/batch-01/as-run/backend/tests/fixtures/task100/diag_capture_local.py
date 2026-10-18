"""TASK-100 诊断：捕获 apply_teaching_local 内被收敛的原始 psycopg 错误。

只读诊断：临时包裹 _transaction 的 psycopg.Error 捕获分支，把原始异常
类型/消息与 SQL 记到证据文件，然后原样重抛，产品代码零改动。
"""
import asyncio
import json
import os
import sys
import traceback
from pathlib import Path
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))

import psycopg  # noqa: E402

from app.capabilities.contracts import AdmissionDenied  # noqa: E402
from app.activities import ActivityLedgerConflict  # noqa: E402
from app.learning.teaching_contracts import GoalBody, TeachingCommandInput  # noqa: E402
from tests.fixtures.task100.support import DSN, Fixture  # noqa: E402
from app.runtime import psycopg_compatible_loop_factory  # noqa: E402

CAPTURED: list[dict] = []
_original_transaction = None


async def patched_transaction(self, operation):
    try:
        import psycopg as _p
        from psycopg.rows import dict_row as _dr
        connection = await _p.AsyncConnection.connect(
            self._dsn, connect_timeout=self._connect_timeout, row_factory=_dr)
        async with connection:
            async with connection.transaction():
                await connection.execute(
                    "SELECT set_config('statement_timeout', %s, true)",
                    (f"{self._statement_timeout_ms}ms",))
                await connection.execute(
                    "SELECT set_config('lock_timeout', %s, true)",
                    (f"{self._lock_timeout_ms}ms",))
                await connection.execute(
                    "SET LOCAL idle_in_transaction_session_timeout = '5s'")
                return await operation(connection)
    except (AdmissionDenied, ActivityLedgerConflict):
        raise
    except psycopg.Error as exc:
        CAPTURED.append({
            "type": type(exc).__name__,
            "message": str(exc)[:600],
            "sqlstate": getattr(exc, "sqlstate", None),
            "trace": traceback.format_exc()[-1200:],
        })
        raise


async def main() -> int:
    global _original_transaction
    from app.activities.repository import PostgresAdmissionLedger
    _original_transaction = PostgresAdmissionLedger._transaction
    PostgresAdmissionLedger._transaction = patched_transaction

    fixture = Fixture(DSN, Path(os.environ.get("TEMP", ".")) / "retrolume-task100-originals")
    source = fixture.text("平均速度 = 路程 ÷ 时间。2 分钟走 120 米，120 米 ÷ 120 秒 = 1 米/秒。\n")
    activity = await fixture.activity([source])
    body = GoalBody(goal="能正确换算平均速度并说明数量级", self_report=None, domain=None,
                    seed_operation_id=None, seed_payload_sha256=None)
    command = TeachingCommandInput(
        business_key=str(uuid4()), expected_revision=0, expected_goal_version=0,
        expected_scope_revision=1, action="goal", body=body.model_dump())
    failure = None
    try:
        receipt = await fixture.ledger.apply_teaching_local(activity, command)
        print("RECEIPT", receipt)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("LOCAL_FAILED", failure)

    # 第二步：同槽异文（第二版目标 goal_version=1），验证同槽竞争的真实错误码。
    slot_failure = None
    try:
        second_body = GoalBody(goal="同槽不同内容的目标表述", self_report=None, domain=None,
                                seed_operation_id=None, seed_payload_sha256=None)
        second = TeachingCommandInput(
            business_key=str(uuid4()), expected_revision=1, expected_goal_version=1,
            expected_scope_revision=1, action="goal", body=second_body.model_dump())
        receipt2 = await fixture.ledger.apply_teaching_local(activity, second)
        print("SECOND_RECEIPT", receipt2)
    except Exception as exc:
        slot_failure = f"{type(exc).__name__}: {exc}"
        print("SECOND_FAILED", slot_failure)

    out = BACKEND.parent / "DocuN/evidence/TASK-100/runtime/diag-local-error.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"failure": failure, "slot_failure": slot_failure,
                               "captured": CAPTURED},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", out)
    PostgresAdmissionLedger._transaction = _original_transaction
    return 0


if __name__ == "__main__":
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
        raise SystemExit(runner.run(main()))
