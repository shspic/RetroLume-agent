"""Pure standard-library receipt and identity check; no product import or test."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import difflib

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-100/answer-support-repair-04"
OUT = ROOT / "DocuN/evidence/TASK-100/orchestration-receipt-07"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    target = OUT / name
    if target.exists():
        raise RuntimeError(f"Refuse overwriting receipt: {target}")
    target.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checked(path, expected, group):
    path = Path(path)
    data = path.read_bytes() if path.is_file() else None
    actual = sha(data) if data is not None else None
    return {"group": group, "path": str(path), "expected": expected, "actual": actual,
            "bytes": len(data) if data is not None else None, "match": actual == expected}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    delivery = load(BASE / "delivery-check.json")
    report_path = ROOT / "DocuN/results/TASK-100-result.md"
    report = report_path.read_bytes()
    history_length = delivery["original_history_bytes"]
    report_bound = sha(report) == delivery["result_sha256"]
    history_bound = sha(report[-history_length:]) == delivery["original_history_sha256"]
    final = load(BASE / "final-identities.json")
    current_checks = [checked(row["path"], row["expected_final_sha256"], row["group"])
                      for row in final["records"]]
    rules = load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
    rule_checks = [checked(item["absolute_path"], item["sha256"], "rules") for item in rules]
    asrun = load(BASE / "batch-01/as-run-identities.json")
    after = load(BASE / "batch-01/after-identities.json")
    asrun_hashes = {row["path"]: row["sha256"] for row in asrun}
    after_hashes = {row["path"]: row["after_sha256"] for row in after}
    after_asrun_hashes = {row["path"]: row["as_run_sha256"] for row in after}
    if len(asrun) != len(after) or asrun_hashes != after_hashes or asrun_hashes != after_asrun_hashes:
        raise RuntimeError("as-run and after identities differ")
    batch_checks = []
    for row in asrun:
        batch_checks.append(checked(row["path"], row["sha256"], "current_as_run"))
        batch_checks.append(checked(BASE / "batch-01/as-run" / row["relative_path"], row["sha256"], "as_run_snapshot"))
    raw_index = load(BASE / "evidence-index.json")
    raw_checks = [checked(BASE / row["path"], row["sha256"], "raw") for row in raw_index["entries"]]
    changes = load(BASE / "changes.json")
    source_changes = []
    change_checks = []
    diff_results = []
    for row in changes:
        rel = row["path"]
        data = (ROOT / rel).read_bytes()
        change_checks.append(checked(ROOT / rel, row["after_sha256"], "declared_final"))
        change_checks.append(checked(BASE / row["post"], row["after_sha256"], "post_copy"))
        if row.get("absent_before"):
            old = b""
        else:
            before_path = BASE / "pre" / rel
            change_checks.append(checked(before_path, row["before_sha256"], "pre_copy"))
            old = before_path.read_bytes()
        if rel.startswith("backend/") and row["changed"]:
            source_changes.append(rel)
        if rel.startswith("backend/"):
            actual_diff = (BASE / row["diff"]).read_text(encoding="utf-8")
            generated = "".join(difflib.unified_diff(old.decode("utf-8").splitlines(keepends=True),
                data.decode("utf-8").splitlines(keepends=True),
                fromfile="/dev/null" if row.get("absent_before") else "a/" + rel, tofile="b/" + rel))
            diff_results.append({"path": rel, "file": str(BASE / row["diff"]),
                "normalized_exact": actual_diff.replace("\r\n", "\n") == generated.replace("\r\n", "\n")})
    expected_changes = {"backend/app/learning/teaching_policy.py", "backend/tests/test_task100_repair.py", "backend/tests/test_task100_answer_support.py"}
    old_baseline = load(ROOT / "DocuN/evidence/TASK-100/orchestration-receipt-06/scope-baseline.json")
    changed_from_baseline = [rel for rel, expected in old_baseline["post_baseline"].items()
                             if sha((ROOT / rel).read_bytes()) != expected]
    expected_existing_changes = expected_changes - {"backend/tests/test_task100_answer_support.py"}
    if set(source_changes) != expected_changes or set(changed_from_baseline) != expected_existing_changes:
        raise RuntimeError("Unexpected source drift outside bounded repair04")
    checks = current_checks + rule_checks + batch_checks + raw_checks + change_checks
    if (not report_bound or not history_bound or any(not row["match"] for row in checks)
            or any(not row["normalized_exact"] for row in diff_results)):
        save("blocked-checks.json", {"checks": checks, "diffs": diff_results,
             "report_bound": report_bound, "history_bound": history_bound})
        raise RuntimeError("Returned identities, history, or actual diffs do not match")
    save("identity-checks.json", checks)
    save("diff-checks.json", diff_results)
    unit = load(BASE / "batch-01/unittest-result.json")
    execution = load(BASE / "batch-01/execution.json")
    accounting = load(BASE / "session-accounting.json")
    stderr = (BASE / "batch-01/stderr.txt").read_text(encoding="utf-8-sig")
    stdout = (BASE / "batch-01/stdout.txt").read_text(encoding="utf-8-sig")
    ok_names = re.findall(r"(?m)^\S+ \(([^)]+)\) \.\.\. ok\s*$", stderr)
    raw_cases = [json.loads(line.split(" ", 1)[1]) for line in stdout.splitlines()
                 if line.startswith("ANSWER_SUPPORT_CASE ")]
    exported = load(BASE / "case-results.json")
    bound_cases = raw_cases == exported["cases"]
    method_bind = len(ok_names) == 18 and set(ok_names) == set(unit["methods"])
    callbacks_ok = len(unit["subtests"]) == unit["subtest_count"] == 81 and all(row["success"] for row in unit["subtests"])
    success = (execution["exit_code"] == 0 and unit["successful"] and method_bind and callbacks_ok
               and bound_cases and len(raw_cases) == exported["count"] == 64
               and all(unit[name] == 0 for name in ["failure_count", "error_count", "skip_count", "expected_failure_count", "unexpected_success_count"])
               and "Ran 18 tests" in stderr and stderr.rstrip().endswith("OK"))
    if not success:
        save("raw-log-checks-blocked.json", {"ok_names": ok_names, "method_bind": method_bind,
            "callbacks_ok": callbacks_ok, "bound_cases": bound_cases, "raw_cases": len(raw_cases)})
        raise RuntimeError("Actual final-byte offline log does not support the supplied counts")
    save("raw-log-receipt.json", {"methods": ok_names, "methods_count": len(ok_names), "subtests": len(unit["subtests"]),
        "all_subtests_success": callbacks_ok, "sample_count": len(raw_cases), "case_export_exact_stdout": bound_cases,
        "exit_code": execution["exit_code"], "unittest_ok": True, "offline_seconds": accounting["offline_charged_seconds"],
        "active_final_upper_seconds": accounting["active_charged_upper_seconds"],
        "active_report_checkpoint_seconds": accounting["report_upper_checkpoint_seconds"],
        "report_to_final_package_seconds": accounting["report_to_final_package_seconds"],
        "resources": accounting["resource_counts"], "scope": "ordinary receipt only; assertions and F01 closure require independent review"})
    rels = ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
            "DocuN/tasks/TASK-100.md", "DocuN/tasks/TASK-101.md",
            "DocuN/results/TASK-100-work-decision.md", "DocuN/results/TASK-101-work-decision.md"]
    backups = []
    for rel in rels:
        data = (ROOT / rel).read_bytes()
        target = OUT / "before" / rel
        if target.exists():
            raise RuntimeError("Refuse overwriting original shared history")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        backups.append({"path": rel, "sha256": sha(data), "bytes": len(data), "backup": str(target)})
    save("before-manifest.json", backups)
    snapshot_names = {"TASK-100-repair-04-card-as-returned.md": "DocuN/tasks/TASK-100.md",
                      "TASK-101-review-02-report-as-frozen.md": "DocuN/results/TASK-101-result.md"}
    contracts = [{"path": str(ROOT / "DocuN/results/TASK-099-result.md"),
                  "sha256": sha((ROOT / "DocuN/results/TASK-099-result.md").read_bytes())}]
    for name, rel in snapshot_names.items():
        target = OUT / name
        if target.exists():
            raise RuntimeError("Refuse replacing contract snapshot")
        data = (ROOT / rel).read_bytes()
        target.write_bytes(data)
        contracts.append({"path": str(target), "sha256": sha(data)})
    excluded = {"result-prefix.md", "result-prefix-template.md", "pre/DocuN/results/TASK-100-result.md",
                "post/DocuN/results/TASK-100-result.md", "diff/DocuN__results__TASK-100-result.md.diff"}
    neutral_raw = [{"path": str(BASE / row["path"]), "sha256": row["sha256"], "bytes": row["bytes"]}
                   for row in raw_index["entries"] if row["path"].replace("\\", "/") not in excluded]
    source_current = [{"path": str(ROOT / row["relative_path"]), "sha256": row["sha256"]} for row in asrun]
    neutral = {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "task": "TASK-101", "R": "R-095", "round": "review-03",
        "purpose": "F01 bounded delta only; no implementation self-report or prior whole-stage re-audit",
        "contracts": contracts, "rules": rule_checks, "current_objects": source_current,
        "changes": [row for row in changes if row["path"].startswith("backend/")],
        "raw_files": neutral_raw, "excluded_implementation_self_reports": sorted(excluded) + [str(report_path)],
        "notes_after_source_prelog_only": ["grammar-and-applicability.md", "propagation-source.md", "method-applicability.json"],
        "author_index_navigation_only": str(BASE / "evidence-index.json"),
        "report_history_before_new_round": {"bytes": (ROOT / "DocuN/results/TASK-101-result.md").stat().st_size,
            "sha256": sha((ROOT / "DocuN/results/TASK-101-result.md").read_bytes())},
        "business_or_resource_execution_permitted": False}
    save("review-03-input-prepared.json", neutral)
    input_path = ROOT / "DocuN/evidence/TASK-101/review-03-input.json"
    if input_path.exists():
        raise RuntimeError("Independent review03 input already registered; do not overwrite")
    input_path.write_text(json.dumps(neutral, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    save("receipt.json", {"at": neutral["at"], "task": "TASK-100", "R": "R-094", "round": "repair-04",
        "status": "returned; candidate and finite local evidence received; F01/DEF-008 still pending independent review",
        "report_sha256": sha(report), "report_bytes": len(report), "original_history_bytes": history_length, "original_history_preserved": True,
        "current_manifest_rows": len(current_checks), "as_run_unique_current": len(asrun), "as_run_copies_bound": True,
        "raw_evidence_index_items": len(raw_checks), "source_changed_files": source_changes, "diffs_exact": True,
        "offline_methods": 18, "offline_subtests": 81, "actual_sample_records": 64,
        "test_batches": f'{accounting["offline_batches_used"]}/3', "offline_seconds": accounting["offline_charged_seconds"],
        "active_final_upper_seconds": accounting["active_charged_upper_seconds"], "report_checkpoint_delta_seconds": accounting["report_to_final_package_seconds"],
        "root_product_writes": 0, "root_product_test_runs": 0, "runtime_observation": "prior stop timestamp only; no new resource actions",
        "remaining_defect": "DEF-008/P1; do not adopt implementer closure statement as independent conclusion",
        "root_metadata_correction": "Initial helper compared different as-run and after JSON schemas as whole objects; exit1 before any backups/shared mutation. Corrected by comparing actual path and hash fields; original helper preserved. No product evidence or business run changed.",
        "next": "original TASK-101/R-095 A+ independent window; pure read/hash evidence increment review03",
        "neutral_input_path": str(input_path), "neutral_input_sha256": sha(input_path.read_bytes())})
    print(json.dumps({"report_bytes": len(report), "report_sha256": sha(report), "source_changes": source_changes,
        "as_run": len(asrun), "raw_index": len(raw_checks), "methods": 18, "subtests": 81, "raw_cases": len(raw_cases),
        "history_unchanged": True, "neutral_files": len(neutral_raw), "neutral_sha256": sha(input_path.read_bytes()),
        "active_final_upper": accounting["active_charged_upper_seconds"], "business_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
