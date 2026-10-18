"""仅核既定输入、既有收尾状态和自有报告；不运行产品或业务。"""
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import time

from probe_support import HERE, ROOT, free, inspect_guard, load, publish


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


started = time.perf_counter()
before = load(HERE / "identity-check-before.json")
index = HERE / "input-snapshot.json"
assert digest(index) == before["index_sha256"]
rows = []
for entry in before["objects"]:
    actual = digest(ROOT / entry["path"])
    rows.append({"group": entry["group"], "path": entry["path"],
                 "expected": entry["expected"], "actual": actual,
                 "match": actual == entry["expected"]})
assert len(rows) == 691 and all(x["match"] for x in rows)
rules = []
for entry in load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json"):
    actual = digest(entry["absolute_path"])
    rules.append({"path": entry["relative_path"], "expected": entry["sha256"],
                  "actual": actual, "match": actual == entry["sha256"]})
assert len(rules) == 7 and all(x["match"] for x in rules)

resource_started = time.perf_counter()
container = inspect_guard()
assert container["running"] is False and container["pid"] == 0
for port in (18098, 55441):
    free(port)
resources = {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
             "action": "只读精确容器身份与两既定本机端口收尾复核",
             "container": container, "exclusive_bind_free": [18098, 55441],
             "new_entry": 0, "new_container_start": 0, "new_sup": 0,
             "seconds": time.perf_counter() - resource_started}
publish("resources-readonly-after.json", resources, HERE)

report_path = ROOT / "DocuN/results/TASK-098-result.md"
report_bytes = report_path.read_bytes()
report = report_bytes.decode("utf-8-sig")
assert "*" not in report
assert not re.search(r"(?m)^\s*\|", report)
assert all(re.search(r"(?m)^## " + part + r"\s", report) for part in "ABCD")
assert all("T" + str(i).zfill(2) in report for i in range(1, 19))
assert "winner解释器20824、loser解释器40532，唯一transport出自20824" in report
links = list(dict.fromkeys(re.findall(r"\]\((D:/[^)]+)\)", report)))
pending = {str((HERE / name).as_posix()) for name in
           ("identity-check-after.json", "audit-budget-final.json", "delivery-proof.json")}
for path in links:
    assert Path(path).exists() or path in pending, path

now = datetime.now(timezone(timedelta(hours=8)))
closure_seconds = time.perf_counter() - started
publish("identity-check-after.json", {
    "at": now.isoformat(), "index_sha256": digest(index), "objects": rows,
    "rules": rules, "object_counts": dict(Counter(x["group"] for x in rows)),
    "all_691_objects_match": True, "all_7_rules_match": True,
    "input_and_prior_evidence_unchanged": True,
    "offline_closure_seconds_through_report_readback": closure_seconds,
    "scope": "仅登记输入及公共规则字节身份；不读取评价正文，不替代动态覆盖"
}, HERE)

entry = load(HERE / "runtime/run-01/entry-final.json")
assert entry["entry"] == 1 and entry["container_starts"] == 1
assert entry["sup_attempts"] == 2 and entry["actual_sup_created"] == 2
assert entry["actual_sup_resumed"] == 2
assert entry["child_exit_code"] == 0 and entry["case"]["exit_code"] == 0
assert entry["cleanup_ok"] and entry["case"]["cleanup_ok"]
assert not entry["cleanup_errors"] and not entry["case"]["cleanup_errors"]
cleanup = entry["outer_cleanup_seconds"] + entry["case"]["cleanup_seconds"]
business = entry["total_seconds"] - cleanup
assert business <= 300 and cleanup <= 120
assert all(entry[key] == 0 for key in ("browser", "driver", "build", "provider", "paid"))
measured = [
    {"action": "初始hash", "seconds": 0.5381673, "exit_code": 0},
    {"action": "static_reconstruction.py只读重建", "seconds": 12.292219, "exit_code": 0},
    {"action": "offline_preparation.py一次自身夹具准备", "seconds": 0.578, "exit_code": 0},
    {"action": "final_reconstruction.py只读重建", "seconds": 3.985, "exit_code": 0},
    {"action": "build_qualification.py只读解释", "seconds": 0.015, "exit_code": 0},
    {"action": "delivery_closure.py最终hash/收尾只读/报告读回", "seconds": closure_seconds, "exit_code": None,
     "completion_confirmed_by": "同批工具真实退出0及delivery-proof.json"},
]
offline_measured = sum(x["seconds"] for x in measured)
offline_upper = offline_measured + 60
recorded_start = datetime.fromisoformat(before["recorded_clock_start"])
active_upper = (now - recorded_start).total_seconds() + 600 + 5
assert max(x["seconds"] for x in measured) < 60 and offline_upper < 240 and active_upper < 10800
publish("audit-budget-final.json", {
    "at": now.isoformat(), "task": "TASK-098", "result": "R-092",
    "counts": {key: entry[key] for key in
               ("entry", "container_starts", "sup_attempts", "actual_sup_created",
                "actual_sup_resumed", "browser", "driver", "build", "provider", "paid")},
    "business_seconds": business, "cleanup_seconds": cleanup,
    "business_prepare_remainder_conservatively_included": business - entry["case"]["business_seconds"],
    "dynamic_limits": {"entry": 1, "container_starts": 1, "sup_attempts": 2,
                       "business_seconds": 300, "cleanup_seconds": 120},
    "offline_measured_items": measured,
    "offline_measured_seconds": offline_measured,
    "offline_unmetered_readonly_navigation_and_publication_allowance_seconds": 60,
    "offline_conservative_upper_seconds": offline_upper,
    "offline_limit_seconds": 240, "offline_batch_limit_seconds": 60,
    "fixture_preparation_runs": 1, "fixture_repair_rechecks": 0,
    "active_recorded_clock_start": before["recorded_clock_start"],
    "active_earlier_read_allowance_seconds": 600,
    "active_final_publication_allowance_seconds": 5,
    "active_wallclock_upper_seconds_at_closure": active_upper,
    "active_limit_seconds": 10800,
    "old_097_unchanged": {"entry": 11, "container_starts": 11, "sup_official": 23,
                          "browser": 6, "driver": 7, "business_seconds": 541.468,
                          "cleanup_seconds": 6.781, "offline_seconds": 149.7236913,
                          "active_wallclock_upper_seconds": 19091.1341925},
    "cross_task_official": {"entry": 12, "container_starts": 12, "sup": 25,
                            "actual_sup_created": 25, "resumed_lower_bound": 24,
                            "claim_job_observations": 23, "browser": 6, "driver": 7,
                            "business_seconds": 541.468 + business,
                            "cleanup_seconds": 6.781 + cleanup,
                            "offline_conservative_upper_seconds": 149.7236913 + offline_upper,
                            "active_wallclock_upper_seconds": 19091.1341925 + active_upper},
    "cross_task_enter_create_function_conservative_count": 26,
    "count_scope_note": "26含09创建前观察失败，不能当26个CreateProcess；官方25保持。旧FAIL、缺回执、095超限/漏时不清零。",
    "resource_closure": "resources-readonly-after.json及原run-01收尾原件",
    "limits_met": True
}, HERE)

self_path = HERE / "delivery-proof.json"
link_readback = [{"path": path, "exists": Path(path).exists()}
                 for path in links if Path(path) != self_path]
assert all(x["exists"] for x in link_readback)
proof = {
    "at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "result_path": report_path.as_posix(), "result_bytes": len(report_bytes),
    "result_sha256": hashlib.sha256(report_bytes).hexdigest(),
    "saved_and_utf8_readback": True,
    "format_checks": {"asterisks_absent": True, "markdown_tables_absent": True,
                      "sections_A_D_present": True, "T01_T18_present": True,
                      "all_report_navigation_targets_except_this_self_reference_exist": True},
    "link_targets": link_readback,
    "self_reference": {"path": self_path.as_posix(),
                       "excluded_from_prepublication_exists_claim": True},
    "inputs_and_prior_evidence_all_match": True,
    "new_dynamic_entry_total": 1, "real_entry_exit_code": 0,
    "new_business_or_browser_or_build_from_this_closure": False,
    "closure_script": str(Path(__file__).resolve()),
    "closure_command": [str(ROOT / "backend/.venv/Scripts/python.exe"), "-B", str(Path(__file__).resolve())],
    "closure_exit_code": "同批工具真实退出状态；不预写未来退出0"
}
publish("delivery-proof.json", proof, HERE)
assert self_path.exists() and all(Path(path).exists() for path in links)
assert digest(report_path) == proof["result_sha256"]
print(json.dumps({"result_path": report_path.as_posix(), "result_bytes": len(report_bytes),
                  "result_sha256": proof["result_sha256"], "input_objects_match": len(rows),
                  "rules_match": len(rules), "report_links_exist": len(links),
                  "offline_upper_seconds": offline_upper,
                  "active_upper_seconds_at_closure": active_upper,
                  "saved_and_readable": True}, ensure_ascii=False))
