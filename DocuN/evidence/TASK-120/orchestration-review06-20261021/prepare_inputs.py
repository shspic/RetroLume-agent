"""Bounded orchestration metadata review and independent-audit input snapshot."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
AUDIT = ROOT / "DocuN/evidence/TASK-121/orchestration-20261021"
EXEC = ROOT / "DocuN/evidence/TASK-120/execution"
C06 = EXEC / "continuation-06"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="microseconds")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def put_json(path, value):
    path = path.resolve()
    assert path.is_relative_to(ROOT)
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes(data)
    assert path.read_bytes() == data


assert ROOT == Path("D:/shspic/project_NO3_RetroLume-agent").resolve()
assert not (ROOT / "DocuN/tasks/TASK-121.md").exists(), "TASK121 was already allocated; inspect current state."
rules = read_json(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
for item in rules:
    assert sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"], item["relative_path"]
assert len(rules) == 7
identities = read_json(C06 / "final-file-identities.json")
current = identities["current"]
assert len(current) == 209
for item in current:
    path = (ROOT / item["path"]).resolve()
    assert path.is_relative_to(ROOT)
    actual = sha(path.read_bytes()) if path.is_file() else None
    assert actual == item["sha256"], item["path"]
changed = identities["product_paths_changed"]
assert len(changed) == 8
assert sha((ROOT / "backend/migrations/015_activity_scope_delete_permission.sql").read_bytes()) == "59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e"
bundle = read_json(C06 / "formal-bundle-identities.json")
for item in bundle["assets"]:
    assert sha((ROOT / item["path"]).read_bytes()) == item["sha256"]

ledger = read_json(EXEC / "budget.json")
assert ledger["active_root"] is None and ledger.get("active_command") is None
assert ledger["engineering_status"] == "CONTINUATION06_COMPLETE_STOPPED_READY_FOR_INDEPENDENT_AUDIT"
assert ledger["counts"]["roots"] == 51 and ledger["counts"]["pg_starts"] == 52
assert ledger["counts"]["browser_starts"] == 14 and len(ledger["failures"]) == 125
assert all(ledger["counts"][key] == 0 for key in ("provider_calls", "actual_fee_microunits", "preview_creates", "preview_starts", "Git_writes"))
stop = read_json(C06 / "final-stop-proof-after-readonly.json")
assert stop["all_fresh_stop_dimensions_confirmed"] and stop["processes_jobs_ports_stopped"]
assert stop["metadata_read_problems"] == []
assert stop["docker_realtime"]["state"]["Running"] is False and stop["docker_realtime"]["state"]["Pid"] == 0
target = stop["restore_target_realtime"]
assert target["running"] is False and target["Pid"] == 0
assert target["cid"] == "4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332"
assert len(stop["registered_processes"]) == 622 and len(stop["registered_jobs"]) == 135
assert all(not row["same_identity_running"] for row in stop["registered_processes"])
assert all(row["absent"] or row.get("active_processes") == 0 for row in stop["registered_jobs"])
assert all(not row["listening"] for row in stop["ports"].values())
r70, r71 = (read_json(C06 / f"command-{number}.receipt.json") for number in ("070", "071"))
assert all(row["exit_code"] == 0 and row["tree_empty"] for row in (r70, r71))
assert math.isclose(ledger["command_wall_conservative_upper_seconds"], 50299.862003 - 60 + r71["wall_seconds"], abs_tol=0.000001)

old_input = read_json(ROOT / "DocuN/evidence/TASK-120/orchestration-continuation06-20261020/input-verification.json")
report = (ROOT / "DocuN/results/TASK-120-result.md").read_bytes()
old_start = report.index("# TASK-120 / R-114 — 完整收尾05结果：局部修复与证据收口完成，整体未通过".encode("utf-8"))
old_report_hashes = {key.replace("\\", "/"): value
                     for key, value in old_input["returned_report_budget_events_hashes"].items()}
assert sha(report[old_start:]) == old_report_hashes["DocuN/results/TASK-120-result.md"]
archive = read_json(C06 / "candidate-package-identity.json")
zip_path = ROOT / archive["path"]
zip_bytes = zip_path.read_bytes()
assert len(zip_bytes) == archive["bytes"] and sha(zip_bytes) == archive["sha256"]
with zipfile.ZipFile(zip_path) as stored:
    names = stored.namelist()
    assert len(names) == archive["files"]
    assert not any(name.lower().endswith(".zip") for name in names)

baseline = read_json(ROOT / "DocuN/evidence/TASK-120/orchestration-20261018/product-baseline.json")
baseline_map = {item["relative_path"].replace("\\", "/"): item for item in baseline["files"]}
diff_relpaths = ["source.diff", "continuation-01/source.diff", "repair-03/source.diff",
                 "validation-04/source.diff", "finalization-05/source.diff", "continuation-06/source.diff"]
paths = {item["path"].replace("\\", "/") for item in current}
diff_entries = []
for name in diff_relpaths:
    path = EXEC / name
    data = path.read_bytes()
    files = set()
    for line in data.decode("utf-8-sig").splitlines():
        if not line.startswith("+++ "):
            continue
        rel = line[4:].split("\t", 1)[0].replace("\\", "/")
        for prefix in ("after/", "b/"):
            if rel.startswith(prefix):
                rel = rel[len(prefix):]
                break
        if rel.startswith(("backend/", "frontend/", "config/", "deploy/")) or rel in ("README.md", ".gitignore"):
            files.add(rel)
    paths.update(files)
    diff_entries.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(data), "declared_paths": sorted(files)})

net_products, fixture_paths, generated_paths = [], [], []
for rel in sorted(paths):
    path = (ROOT / rel).resolve()
    assert path.is_relative_to(ROOT)
    if rel.startswith(("backend/tests/", "frontend/tests/")):
        fixture_paths.append(rel)
        continue
    if rel.startswith("frontend/dist/"):
        generated_paths.append(rel)
        continue
    if not (rel.startswith(("backend/app/", "backend/migrations/", "frontend/src/", "config/", "deploy/")) or rel in ("README.md", ".gitignore")):
        continue
    prior = baseline_map.get(rel)
    actual = sha(path.read_bytes()) if path.is_file() else None
    prior_sha = prior["sha256"] if prior else None
    if actual != prior_sha:
        net_products.append({"path": rel, "initial_sha256": prior_sha, "final_sha256": actual,
            "initial_manifest_entry_present": prior is not None, "initial_file_exists": prior.get("exists") if prior else None,
            "latest06_changed": rel in changed})

raw_names = ["final-review-index.json", "final-file-identities.json", "candidate-package-identity.json", "source.diff",
    "permission-risk-check.json", "real-profile-ACL-and-guard-PASS.json", "old-new-package-compatibility.json",
    "old-R02-and-final-readonly-reconciliation-PASS.json", "actual-scope-shrink-PASS.json", "scope-targeted-negatives-PASS.json",
    "K2-scope-shrink-PASS.json", "K2-scope-shrink-final-checkpoint.json", "UI-normal-GET-1-root-46.json",
    "UI-normal-GET-2-root-46.json", "UI-complete-DataContext-PASS-root-46.json", "UI-namespace-PASS-root-46.json",
    "normal-backup-checkpoint.json", "normal-restore-verified-checkpoint.json", "normal-selector-activation-COMMIT.json",
    "namespace-capabilities-authenticated-barrier.json", "readonly-listing-PASS.json", "readonly-listing-UI-PASS.json",
    "financial-summary.json", "final-fresh-financials-separated.json", "final-protocol-currentness-witness.json",
    "final-stop-proof-after-readonly.json", "command-070.receipt.json", "command-071.receipt.json"]
raw_hashes = [{"path": (C06 / name).relative_to(ROOT).as_posix(), "sha256": sha((C06 / name).read_bytes())} for name in raw_names]
for filename in ("UI-complete-DataContext-PASS-root-46.json", "UI-namespace-PASS-root-46.json"):
    observation = read_json(C06 / filename)
    assert observation["native_fetch_fulfilled"] is True and observation["business_body_consumed"] is False
    assert observation["zero_automatic_POST"] is True

put_json(AUDIT / "audit-inputs.json", {
    "timestamp": NOW, "root": str(ROOT), "task": "TASK-121", "R": "R-115", "parent": "TASK-120/R-114",
    "use": "Object identity only; no independent conclusions supplied by orchestration",
    "rules": rules, "current_frozen_files": current, "formal_dist": bundle["assets"],
    "opaque_engineering_report": {"path": "DocuN/results/TASK-120-result.md", "sha256": sha(report), "bytes": len(report), "do_not_decode": True},
    "candidate_archive": {"path": archive["path"], "sha256": archive["sha256"], "bytes": archive["bytes"], "files": len(names),
        "do_not_decode_implementation_result_or_self_evaluation_if_present": True},
    "raw_evidence_identity_entries": raw_hashes,
    "engineering_ledger": [{"path": (EXEC / name).relative_to(ROOT).as_posix(), "sha256": sha((EXEC / name).read_bytes())} for name in ("budget.json", "events.jsonl")],
    "original_120_baseline": "DocuN/evidence/TASK-120/orchestration-20261018/product-baseline.json",
    "latest06_current_and_as_run_navigation": "DocuN/evidence/TASK-120/execution/continuation-06/final-file-identities.json",
    "no_runtime_budget_in_this_audit": True})
put_json(AUDIT / "scope-index.json", {
    "scope": "Entire actual TASK120 change since its original baseline; not only the eight latest06 files; unchanged accepted S is inherited",
    "net_product_changes_relative_to_initial_manifest": net_products,
    "diff_chain": diff_entries, "fixture_paths_for_actual_evidence_review": fixture_paths,
    "generated_asset_paths": generated_paths, "latest06_product_changes": changed,
    "baseline_preimages": "DocuN/evidence/TASK-120/execution/preimage/",
    "later_preimages": ["continuation-01/preimage/", "repair-03/preimage/", "validation-04/preimage/", "finalization-05/preimage/", "continuation-06/preimage/"],
    "as_run_root46_to_final": identities["root46_to_final_product_delta"],
    "as_run_index": identities["as_run"],
    "raw_evidence_groups": {"original": "DocuN/evidence/TASK-120/execution/",
        "repair03": "DocuN/evidence/TASK-120/execution/repair-03/", "normal_UI": "DocuN/evidence/TASK-120/execution/validation-04/",
        "ACK_permission_K2": "DocuN/evidence/TASK-120/execution/finalization-05/", "latest": "DocuN/evidence/TASK-120/execution/continuation-06/"},
    "S_prior_independent_result": "DocuN/results/TASK-118-result.md",
    "design_adoption_contracts": ["DocuN/evidence/TASK-120/orchestration-20261018/task-contract.md",
        "DocuN/evidence/TASK-120/orchestration-continuation06-20261020/contract-06.md",
        "DocuN/evidence/TASK-120/orchestration-adoption06-20261020/adoption-proposal.md"]})
put_json(OUT / "bounded-review.json", {
    "timestamp": NOW, "role": "orchestration identity and evidence navigation review, not independent audit",
    "rules_match": 7, "current_identity_match": 209, "latest06_product_delta": changed,
    "net_product_change_count": len(net_products), "selected_raw_evidence_hashes": raw_hashes,
    "old_report_suffix_sha256": sha(report[old_start:]), "old_report_suffix_bytes": len(report[old_start:]),
    "candidate_archive_sha256": archive["sha256"], "candidate_archive_files": len(names),
    "last_stop_original_time": stop["utc"], "PID_birth_identities": 622, "named_jobs": 135,
    "both_exact_containers_stopped_at_that_time": True, "main_did_not_query_current_Docker": True,
    "last070_and_filesystem071_exit0_tree_empty": True,
    "counts": ledger["counts"], "caps": ledger["caps"], "failure_records": len(ledger["failures"]),
    "conservative_wall_after071_seconds": ledger["command_wall_conservative_upper_seconds"],
    "report_wall_including_60s_save_reserve": 50299.862003,
    "wall_reconciliation": "Replace only071 reserve60 with actual3.141; all earlier unknown reserves retained",
    "holding_seconds": ledger["runtime_holding_union_seconds"], "active_root": None, "active_command": None,
    "functional_test_run_by_main": False, "independent_audit_run_by_main": False,
    "technical_acceptance": "Candidate received for independent audit, not final TASK120 acceptance"})
print(json.dumps({"status": "INPUTS_FROZEN", "rules": 7, "current_identities": 209,
    "latest_delta_files": 8, "net_product_changes": len(net_products), "archive_entries": len(names),
    "root_count": 51, "wall_after071": ledger["command_wall_conservative_upper_seconds"]}, ensure_ascii=False))
