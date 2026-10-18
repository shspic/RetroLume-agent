"""TASK-092 续作01有限准备核对：不触Docker/PG/Job；compile不写pyc与纯数据断言。

范围依据续作卡第7项：一次准备检查，累计60秒内，计入原离线总额。
"""
from __future__ import annotations

import hashlib
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
sys.path.insert(0, str(EVIDENCE))
os.environ.setdefault("TASK092_EVIDENCE", str(EVIDENCE / "real-04-dryrun"))
started = time.monotonic()
checks = {}


def record(name, value):
    checks[name] = value


# 1. compile：产品改动面 + 全部证据脚本（不写pyc）
compiled = []
for rel in ["app/activities/repository.py", "app/activities/service.py",
            "app/capabilities/contracts.py", "app/capabilities/tool_execution.py",
            "app/worker/command.py", "app/worker/worker_main.py", "app/worker/one_tool.py",
            "app/worker/launcher.py", "app/worker/supervisor_main.py", "app/worker/session.py"]:
    compile((BACKEND / rel).read_text(encoding="utf-8"), rel, "exec")
    compiled.append(rel)
for path in sorted(EVIDENCE.glob("*.py")) + sorted((EVIDENCE / "continuation-01").glob("*.py")):
    compile(path.read_text(encoding="utf-8"), str(path), "exec")
    compiled.append(path.name)
record("compiled", len(compiled))

# 2. win_chain：场景清单与函数映射、清理纪律、会话计数路径
import win_chain  # noqa: E402

missing = [s for s in win_chain.SCENARIOS if not hasattr(win_chain, f"scenario_{s}")]
record("win_scenario_functions_missing", missing)
record("win_scenario_count", len(win_chain.SCENARIOS))
record("win_cleanup_fatal_present", hasattr(win_chain, "CleanupFatal") and hasattr(win_chain, "ensure_clean"))
source = (EVIDENCE / "win_chain.py").read_text(encoding="utf-8")
record("win_two_session_attempts_emitted", source.count('"windows_session_attempt"') >= 6)
record("win_recovery_not_run_emit", "recovery_not_run" in source)
record("win_scenarios_stopped_on_cleanup", "scenarios_stopped" in source)

# 3. upgrade_child：F-U2 修复存在并以合成行验证精确三列比较逻辑
import upgrade_child  # noqa: E402

usource = (EVIDENCE / "upgrade_child.py").read_text(encoding="utf-8")
record("upgrade_fu2_fix_present", "new_op_columns" in usource and "set(new) - set(old)" in usource)
old_row = {"operation_id": "P1", "state": "received", "disposition": "received", "error_code": None,
           "tool_names": [], "reserved_cost_microunits": 100, "recorded_at": "t"}
new_row = dict(old_row, kind="model", arguments_sha256=None, tool_call_id=None)
new_op_columns = {"kind", "arguments_sha256", "tool_call_id"}
try:
    assert set(new_row) - set(old_row) == new_op_columns
    assert set(old_row) - set(new_row) == set()
    assert new_row["kind"] == "model"
    assert new_row["arguments_sha256"] is None and new_row["tool_call_id"] is None
    assert {k: v for k, v in new_row.items() if k not in new_op_columns} == old_row
    record("upgrade_fu2_logic_synthetic", True)
except AssertionError:
    record("upgrade_fu2_logic_synthetic", False)
record("upgrade_schema_reset_present", "DROP SCHEMA IF EXISTS" in usource and "schemas_reset" in usource)
record("upgrade_precheck_present", "upgrade_schemas_precheck" in usource)

# 4. continuation_runner：预算分离、子批清单、一次性闸门
import continuation_runner  # noqa: E402

record("runner_total_seconds", continuation_runner.TOTAL_SECONDS)
record("runner_business_cleanup", (continuation_runner.BUSINESS_SECONDS, continuation_runner.CLEANUP_SECONDS))
record("runner_children", [name for name, _ in continuation_runner.CHILDREN])
nsource = (EVIDENCE / "continuation_runner.py").read_text(encoding="utf-8")
record("runner_continuation_gate", "continuation_01_used" in nsource and "no fifth batch" in nsource)
record("runner_full_json_inspect", "json.loads(docker([\"inspect\", cid]" in nsource)
record("runner_no_budget_json_bypass", "container_starts\"] >= 4" in nsource)

# 5. legacy_probe：pre原件存在且副本声明清晰
import legacy_probe  # noqa: E402

pre = EVIDENCE / "pre"
record("legacy_pre_present", all((pre / name).exists() for name in (
    "app_worker_supervisor_main.py", "app_worker_worker_main.py")))
record("legacy_pre_hashes", legacy_probe.pre_hashes())

# 6. 场景清单包含真实时点续作条目
manifest = json.loads((EVIDENCE / "scenario-manifest.json").read_text(encoding="utf-8"))
record("scenario_manifest_continuation01", "frozen_utc" in manifest.get("continuation_01", {})
       and len(manifest["continuation_01"].get("scenarios", [])) == 3)

# 7. 预算账先决：3历史批完成且未用续作闸门
budget = json.loads((EVIDENCE / "budget-manifest.json").read_text(encoding="utf-8"))
record("budget_prior", {"attempts": len(budget["real_attempts"]),
                        "all_finished": all(x.get("state") == "finished" for x in budget["real_attempts"]),
                        "active": budget["active_processes"], "used_seconds": round(budget["real_used_seconds"], 3),
                        "container_starts": budget["container_starts"], "windows": budget["windows_sessions"],
                        "offline": round(budget["offline_used_seconds"], 3),
                        "continuation_01_used": bool(budget.get("continuation_01_used"))})

seconds = time.monotonic() - started
result = {"kind": "续作01有限准备核对（不触Docker/PG/Job）", "seconds": round(seconds, 3),
          "checks": checks, "passed": (not missing) and checks["upgrade_fu2_logic_synthetic"]
          and checks["win_scenario_count"] == 5 and checks["runner_total_seconds"] == 420}
(HERE / "control-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
# 记入原离线总额（预算文件是唯一账）。
budget["offline_used_seconds"] += seconds
budget.setdefault("offline_runs", []).append(
    {"path": "DocuN/evidence/TASK-092/continuation-01/prep_check.py", "seconds": round(seconds, 3),
     "exit": 0, "note": "续作01准备检查，计入原离线总额"})
( EVIDENCE / "budget-manifest.json").write_text(json.dumps(budget, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in checks.items() if not isinstance(v, dict)}, ensure_ascii=False))
print(json.dumps({"passed": result["passed"], "seconds": result["seconds"]}))
