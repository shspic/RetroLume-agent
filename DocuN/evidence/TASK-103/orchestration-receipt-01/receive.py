"""Read/hash returned partial candidate and inspect only owned resource metadata."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-103"
OUT = BASE / "orchestration-receipt-01"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    path = OUT / name
    if path.exists():
        raise RuntimeError("Receipt exists; do not replace existing work")
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    declared = load(BASE / "final/pre-diff-post.json")
    rows = [*declared["changed"], *declared["unchanged_protected"], *declared["new"], *declared["additional_observed"]]
    checks = []
    current = {}
    for row in rows:
        rel = row["path"]
        expected = row["post_sha256"]
        path = ROOT / rel
        actual = sha(path.read_bytes()) if path.is_file() else None
        checks.append({"path": rel, "expected": expected, "actual": actual, "match": actual == expected,
                       "expected_absent": expected is None})
        if expected is not None:
            current[rel] = expected
    inputs = load(BASE / "final/inputs-after.json")
    for row in inputs:
        path = Path(row["path"])
        expected = row["expected_sha256"]
        actual = sha(path.read_bytes())
        checks.append({"path": str(path), "expected": expected, "actual": actual, "match": actual == expected})
    if any(not row["match"] for row in checks):
        save("blocked-checks.json", checks)
        raise RuntimeError("Candidate or protected input identity drift")
    save("identity-checks.json", checks)
    save("current-baseline.json", current)
    post_rows = load(BASE / "final/post/identities.json")
    for row in post_rows:
        if sha((ROOT / row["path"]).read_bytes()) != row["sha256"]:
            raise RuntimeError("Current bytes differ from reported post snapshot")
    accounting = load(BASE / "final/accounting-final.json")
    resources = load(BASE / "final/resources-after.json")
    owned = []
    for old in resources["containers"]:
        result = subprocess.run(["docker.exe", "inspect", "--type", "container", old["cid"]], capture_output=True, timeout=15, check=False)
        if result.returncode:
            owned.append({"cid": old["cid"], "verified": False, "exit_code": result.returncode})
            continue
        obj = json.loads(result.stdout)[0]
        value = {"cid": obj["Id"], "name": obj["Name"].lstrip("/"), "image": obj["Image"],
                 "state": {key: obj["State"].get(key) for key in ("Status", "Running", "Pid", "ExitCode")},
                 "labels": {key: obj["Config"].get("Labels", {}).get(key) for key in ("retrolume.task", "retrolume.permit", "retrolume.synthetic")},
                 "mounts": [{key: item.get(key) for key in ("Type", "Name", "Destination", "RW")} for item in obj.get("Mounts", [])],
                 "limits": {key: obj["HostConfig"].get(key) for key in ("NanoCpus", "Memory", "PidsLimit", "Privileged")}}
        value["verified"] = (value["cid"] == old["cid"] and value["image"] == old["image"] and value["name"] == old["name"]
            and value["labels"]["retrolume.task"] == "TASK-103" and not value["state"]["Running"] and value["state"]["Pid"] == 0)
        owned.append(value)
    save("resource-readonly.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "containers": owned,
         "operations": "read-only full JSON parsed, only nonsecret fields retained", "new_starts_or_SQL": 0})
    shared = ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/tasks/TASK-103.md"]
    before = []
    for rel in shared:
        data = (ROOT / rel).read_bytes()
        target = OUT / "before" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError("Shared pre-state already saved")
        target.write_bytes(data)
        before.append({"path": rel, "sha256": sha(data), "bytes": len(data), "backup": str(target)})
    save("before-manifest.json", before)
    report = (ROOT / "DocuN/results/TASK-103-result.md").read_bytes()
    (OUT / "TASK-103-as-returned.md").write_bytes(report)
    (OUT / "TASK-103-first-card-as-returned.md").write_bytes((ROOT / "DocuN/tasks/TASK-103.md").read_bytes())
    essential = []
    for rel in ["final/accounting-final.json", "final/pre-diff-post.json", "final/product.patch", "final/runs-ledger.json",
                "final/resources-after.json", "final/bundle-chain.json", "final/sql-snapshot-evidence.json",
                "browser-03/result.json", "browser-03/checkpoint.json", "failures/root24-integration-resume-result.json"]:
        path = BASE / rel
        data = path.read_bytes()
        essential.append({"path": str(path), "sha256": sha(data), "bytes": len(data)})
    save("returned-evidence-identities.json", essential)
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-103", "R": "R-097",
        "dispatch": "returned", "acceptance": "partial candidate and finite evidence received; complete G9 not accepted",
        "report_sha256": sha(report), "report_bytes": len(report), "manifest_rows_checked": len(rows), "current_unique_sources": len(current),
        "post_snapshot_objects": len(post_rows), "protected_rule_contract_checks": len(inputs), "changed": len(declared["changed"]),
        "new": len(declared["new"]), "removed_generated": len(declared["generated_removed_preserved_in_pre"]),
        "all_new_owned_containers_stopped_verified": all(row["verified"] for row in owned),
        "counts": accounting["counts"], "used_seconds": accounting["used_seconds"],
        "active_conservative_seconds": accounting["active_conservative_including_reply"], "original_run_permission_ended": True,
        "known_code_findings": ["real24 HTTP200 memory_profile_required business refusal; mapping candidate unverified", "memory schema damaged unconditionally rejects readable legacy derived paths; source-confirmed fallback gap"],
        "browser": "three original totalFAIL; editor has editSequence guard, not enough second-page DOM proof to classify original failure purely fixture",
        "session_type_reconciliation": "Actual SessionConfig lease=window20, manager50 with recorded positive parameters; prior suggestedlease60 not represented as satisfied and no worker change authorized",
        "root_product_writes": 0, "root_business_runs": 0,
        "next": "same TASK103/R097 continuation01; complete remaining code/SQL/tool/UI/coverage, new bounded permit, no preliminary full audit"})
    print(json.dumps({"candidate_sources": len(current), "manifest_checks": len(rows), "post_objects": len(post_rows),
        "protected_inputs": len(inputs), "report_sha256": sha(report), "report_bytes": len(report), "old_counts": accounting["counts"],
        "stopped_owned_resources": all(row["verified"] for row in owned), "root_business_runs": 0, "next": "same TASK103 continuation01"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
