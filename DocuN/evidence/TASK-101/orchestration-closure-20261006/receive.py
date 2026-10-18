"""Accept audit through read/hash evidence; no product imports or test execution."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
AUDIT = ROOT / "DocuN/evidence/TASK-101/review-03"
OUT = ROOT / "DocuN/evidence/TASK-101/orchestration-closure-20261006"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    path = OUT / name
    if path.exists():
        raise RuntimeError("Receipt already exists; preserve prior work")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (ROOT / "DocuN/tasks/TASK-102.md").exists() or (ROOT / "DocuN/results/TASK-102-result.md").exists():
        raise RuntimeError("TASK102 already has work; read it instead of replacing it")
    proof = load(AUDIT / "delivery-check.json")
    report = (ROOT / "DocuN/results/TASK-101-result.md").read_bytes()
    original = report[-proof["preserved_history_bytes"]:]
    if sha(report) != proof["result_sha256"] or sha(original) != proof["preserved_history_sha256"]:
        raise RuntimeError("Audit result or original history drifted")
    checks = []
    final = load(AUDIT / "final-input-identity-check.json")
    for row in final["objects"]:
        path = Path(row["path"])
        actual = sha(path.read_bytes()) if path.is_file() else None
        checks.append({"path": str(path), "group": row["group"], "expected": row["expected"], "actual": actual,
                       "match": actual == row["expected"]})
    if len(checks) != 306 or any(not row["match"] for row in checks):
        save("blocked-checks.json", checks)
        raise RuntimeError("Audited input identity changed")
    save("identity-checks.json", checks)
    previous = load(ROOT / "DocuN/evidence/TASK-100/answer-support-repair-04/delivery-check.json")
    if sha((ROOT / "DocuN/results/TASK-100-result.md").read_bytes()) != previous["result_sha256"]:
        raise RuntimeError("Implementation report changed after audit")
    accounting = load(AUDIT / "session-accounting.json")
    if accounting["business_runs"] != 0 or any(accounting["resource_counts"].values()):
        raise RuntimeError("Unexpected new audit business/resource execution")
    rels = ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
        "DocuN/tasks/TASK-100.md", "DocuN/tasks/TASK-101.md", "DocuN/results/TASK-100-work-decision.md", "DocuN/results/TASK-101-work-decision.md"]
    backups = []
    for rel in rels:
        data = (ROOT / rel).read_bytes()
        target = OUT / "before" / rel
        if target.exists():
            raise RuntimeError("Cannot overwrite shared pre-state")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        backups.append({"path": rel, "sha256": sha(data), "bytes": len(data), "backup": str(target)})
    save("before-manifest.json", backups)
    (OUT / "TASK-101-review-03-as-returned.md").write_bytes(report)
    (OUT / "TASK-100-result-as-accepted.md").write_bytes((ROOT / "DocuN/results/TASK-100-result.md").read_bytes())
    essential = ["DocuN/evidence/TASK-101/review-03/delivery-check.json", "DocuN/evidence/TASK-101/review-03/audit-findings.json",
        "DocuN/evidence/TASK-101/review-03/source-structure-check.json", "DocuN/evidence/TASK-101/review-03/runtime-evidence-pairing.json",
        "DocuN/evidence/TASK-101/review-03/execution-control-check.json", "DocuN/evidence/TASK-101/review-03/R03-O01-precision-observation.md"]
    extra = []
    for rel in essential:
        data = (ROOT / rel).read_bytes()
        extra.append({"path": rel, "sha256": sha(data), "bytes": len(data)})
    save("audit-evidence-identities.json", extra)
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "audit_TASK": "TASK-101", "audit_R": "R-095", "round": "review-03", "audit_delivery": "accepted",
        "implementation_TASK": "TASK-100", "implementation_R": "R-094",
        "decision": "approved G8 finite slice accepted and closed; no full STEP/provider/M-1/project signoff",
        "DEF_008": "closed", "R03_O01": "existing nonblocking P2; root to register DEF-019 without reopening G8",
        "audit_report_sha256": sha(report), "audit_report_bytes": len(report), "audit_old_history_bytes": len(original), "audit_old_history_sha256": sha(original),
        "implementation_report_sha256": previous["result_sha256"], "current_identity_matches": len(checks),
        "audit_new_business_runs": 0, "audit_active_charged_upper_seconds": accounting["active_charged_final_upper_with_reply_seconds"],
        "audit_metadata_conservative_seconds": accounting["metadata_conservative_charge_seconds"],
        "timing_unknowns_preserved": True, "previous_failed_helpers_and_history_preserved": True,
        "root_business_runs": 0, "root_product_writes": 0,
        "next": "TASK-102/R-096; STEP013 memory lifecycle and deletion-consistency complete implementation contract; read-only design to original A+ TASK100 window"})
    print(json.dumps({"audit_sha256": sha(report), "audit_bytes": len(report), "old_history_bytes": len(original),
        "matched": len(checks), "G8": "finite approved slice accepted", "DEF008": "closed",
        "P2": "R03-O01/DEF019 nonblocking", "audit_active_upper_seconds": accounting["active_charged_final_upper_with_reply_seconds"],
        "business_runs": 0, "next_TASK": "102/R096 read-only design"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
