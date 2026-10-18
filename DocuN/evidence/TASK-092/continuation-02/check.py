"""续作02有限准备核对：不触Docker/PG/Job；compile不写pyc与纯数据断言（≤60秒）。"""
from __future__ import annotations

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
os.environ.setdefault("TASK092_EVIDENCE", str(EVIDENCE / "real-05-dryrun"))
started = time.monotonic()
checks = {}


def record(name, value):
    checks[name] = value


# 1. compile：产品冻结面 + 本轮夹具与专用runner + 未触碰脚本
for rel in ["app/activities/repository.py", "app/activities/service.py",
            "app/capabilities/contracts.py", "app/capabilities/tool_execution.py",
            "app/worker/command.py", "app/worker/worker_main.py", "app/worker/one_tool.py",
            "app/worker/launcher.py", "app/worker/supervisor_main.py", "app/worker/session.py"]:
    compile((BACKEND / rel).read_text(encoding="utf-8"), rel, "exec")
for name in ("upgrade_child.py", "upgrade_runner.py", "child_control.py"):
    compile((EVIDENCE / name).read_text(encoding="utf-8"), name, "exec")
record("compiled", True)

# 2. 冻结未触碰脚本（与continuation-02/pre逐hash一致）
import hashlib  # noqa: E402
pre = {}
for line in (HERE / "pre/pre-hashes.txt").read_text().splitlines():
    h, p = line.split(" *")
    pre[p] = h
untouched = {name: hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() for name in
             ("child_control.py", "win_chain.py", "bootstrap.py", "legacy_probe.py")}
record("untouched_scripts_unchanged", all(pre[name] == value for name, value in untouched.items()))

# 3. upgrade_child：独立结果结构、阴性识别、定向重跑支持
import upgrade_child  # noqa: E402

record("scenario_funcs", sorted(upgrade_child.SCENARIO_FUNCS))
usource = (EVIDENCE / "upgrade_child.py").read_text(encoding="utf-8")
record("independent_results", "'not_run'" in usource and "excluded_by_retry_scope" in usource)
record("retry_only_support", "TASK092_UPGRADE_ONLY" in usource and "DROP SCHEMA IF EXISTS" in usource)
record("per_scenario_conn_finally", "conn.close()" in usource and "cleanup_error" in usource)

# 阴性识别逻辑：错误SQLSTATE或错误文本必须拒绝，预期组合必须接受。
import psycopg.errors  # noqa: E402

class FakeErr(Exception):
    sqlstate = "08006"


try:
    upgrade_child.expect_migration_rejection(FakeErr("connection failure"), "已有痕迹")
    record("rejects_wrong_sqlstate", False)
except AssertionError:
    record("rejects_wrong_sqlstate", True)
try:
    upgrade_child.expect_migration_rejection(psycopg.errors.RaiseException("synthetic other raise"), "唯一识别")
    record("rejects_wrong_marker", False)
except AssertionError:
    record("rejects_wrong_marker", True)
info = upgrade_child.expect_migration_rejection(
    psycopg.errors.RaiseException("原成本正值约束未能唯一识别（匹配 0 条），迁移整体回滚"), "唯一识别")
record("accepts_expected_p0001_marker", info["sqlstate"] == "P0001" and info["type"] == "RaiseException")

# 4. runner：三段截止、真实闸门、retry门
import upgrade_runner  # noqa: E402

record("runner_seconds", (upgrade_runner.BUSINESS_SECONDS, upgrade_runner.CLEANUP_SECONDS,
                          upgrade_runner.TOTAL_SECONDS))
rsource = (EVIDENCE / "upgrade_runner.py").read_text(encoding="utf-8")
record("runner_gates", "expected_prior = 5 if retry_targets else 4" in rsource
       and "continuation_02_retry_used" in rsource and "real-05 passed; retry is prohibited" in rsource)
record("runner_windows_zero_guard", "windows_sessions_violation" in rsource)
record("runner_full_json_inspect", "json.loads(docker([\"inspect\", cid]" in rsource)
record("runner_exit_none_init", '"exit": None' in rsource and 'state["exit"] = 0' not in rsource)

# 5. 场景清单与预算先决
manifest = json.loads((EVIDENCE / "scenario-manifest.json").read_text(encoding="utf-8"))
record("scenario_manifest_continuation02", len(manifest.get("continuation_02", {}).get("scenarios", [])) == 5)
budget = json.loads((EVIDENCE / "budget-manifest.json").read_text(encoding="utf-8"))
record("budget_prior", {"attempts": len(budget["real_attempts"]),
                        "all_finished": all(x.get("state") == "finished" for x in budget["real_attempts"]),
                        "active": budget["active_processes"],
                        "used_seconds": round(budget["real_used_seconds"], 3),
                        "container_starts": budget["container_starts"],
                        "windows": budget["windows_sessions"],
                        "offline": round(budget["offline_used_seconds"], 3),
                        "c02_used": bool(budget.get("continuation_02_used"))})

seconds = time.monotonic() - started
passed = (checks["untouched_scripts_unchanged"] and checks["rejects_wrong_sqlstate"]
          and checks["rejects_wrong_marker"] and checks["accepts_expected_p0001_marker"]
          and checks["runner_seconds"] == (180, 120, 300)
          and checks["scenario_funcs"] == ["s1", "s2", "s3"])
result = {"kind": "续作02有限准备核对（不触Docker/PG/Job）", "seconds": round(seconds, 3),
          "checks": checks, "passed": passed}
(HERE / "control-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
budget["offline_used_seconds"] += seconds
budget["offline_runs"].append({"path": "DocuN/evidence/TASK-092/continuation-02/check.py",
                               "seconds": round(seconds, 3), "exit": 0,
                               "note": "续作02准备核对，计入原离线总额"})
(EVIDENCE / "budget-manifest.json").write_text(json.dumps(budget, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"passed": passed, "seconds": result["seconds"]}, ensure_ascii=False))
print(json.dumps({k: v for k, v in checks.items() if not isinstance(v, dict)}, ensure_ascii=False))
