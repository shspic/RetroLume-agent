"""real-04后定向复检：upgrade生命线探针修正的静态与真实校验路径核对（零PG零网络）。

依据：real-04 upgrade子批在AdmissionDenied(invalid_input)中止——生命线工具拒绝
探针使用了model键M1的上下文配工具键T1的call，先命中admit_tool_operation的
operation绑定校验。修正为：租约存活期内、以T1自身上下文先探拒绝（零副作用），
再close/settle。本复检用真实校验路径（子类_transaction占位）证明修正后的
意图能通过绑定校验并到达事务边界，错误配对在事务前即被拒。
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
ROOT = EVIDENCE.parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
started = time.monotonic()
checks = {}


def record(name, value):
    checks[name] = value


source = (EVIDENCE / "upgrade_child.py").read_text(encoding="utf-8")
compile(source, "upgrade_child.py", "exec")
record("compiled", True)
record("deny_before_close", source.index("tool_limit_unconfigured") < source.index("begin_window_close(lifecycle_activity"))
record("tool_context_operation_t1", 'operation_id="T1"' in source and "tool_context" in source)
record("zero_side_effect_assert", "denied_ops == []" in source)

from app.activities import PostgresAdmissionLedger  # noqa: E402
from app.capabilities.contracts import (  # noqa: E402
    AdmissionDenied, AdmissionUnavailable, CallContext, ToolExecutionInput, ToolIntent,
    canonical_tool_arguments,
)


class Probe(PostgresAdmissionLedger):
    """真实校验路径 + 占位事务边界：不建连接、不发网络。"""

    def __init__(self):
        pass

    async def _transaction(self, operation):
        raise AdmissionUnavailable("synthetic no-pg boundary")


def intent(operation_id_context: str):
    raw, digest = canonical_tool_arguments({"operation": "add", "left": 1, "right": 2})
    call = ToolExecutionInput("T1", "calc.1", "finite_calculate", raw, digest)
    context = CallContext(activity_id="00000000-0000-0000-0000-000000000001",
                          operation_id=operation_id_context, executor_id="legacy092",
                          execution_generation=1, scope_revision=1)
    return ToolIntent(context=context, call=call)


async def main():
    ledger = Probe()
    wrong = intent("M1")
    try:
        await ledger.admit_tool_operation(wrong)
    except AdmissionDenied as exc:
        record("wrong_pairing_rejected_before_txn", str(exc) == "invalid_input")
    else:
        record("wrong_pairing_rejected_before_txn", False)
    right = intent("T1")
    try:
        await ledger.admit_tool_operation(right)
    except AdmissionUnavailable:
        record("right_pairing_reaches_txn_boundary", True)
    except AdmissionDenied as exc:
        record("right_pairing_reaches_txn_boundary", f"unexpected denial {exc}")
    else:
        record("right_pairing_reaches_txn_boundary", False)


asyncio.run(main())
seconds = time.monotonic() - started
result = {"kind": "real-04后upgrade生命线探针修正定向复检（零PG零网络）",
          "seconds": round(seconds, 3), "checks": checks,
          "passed": checks["deny_before_close"] and checks["right_pairing_reaches_txn_boundary"] is True
          and checks["wrong_pairing_rejected_before_txn"] is True}
(HERE / "control-check-02.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
budget = json.loads((EVIDENCE / "budget-manifest.json").read_text(encoding="utf-8"))
budget["offline_used_seconds"] += seconds
budget["offline_runs"].append({"path": "DocuN/evidence/TASK-092/continuation-01/control-check-02.py",
                               "seconds": round(seconds, 3), "exit": 0,
                               "note": "续作01运行后定向复检，计入原离线总额"})
(EVIDENCE / "budget-manifest.json").write_text(json.dumps(budget, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"passed": result["passed"], "seconds": result["seconds"], "checks": checks}, ensure_ascii=False))
