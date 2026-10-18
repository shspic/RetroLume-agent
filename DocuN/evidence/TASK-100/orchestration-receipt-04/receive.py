"""Read-only file identity receipt and orchestration backups; no product imports."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
AUDIT = ROOT / "DocuN/evidence/TASK-101"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


audit_freeze = json.loads((AUDIT / "final-freeze-and-usage.json").read_text(encoding="utf-8"))
checks = []
for obj in audit_freeze["objects"]:
    if obj["group"] == "raw_files":
        continue
    p = Path(obj["path"])
    if not p.is_absolute():
        p = ROOT / p
    actual = digest(p) if p.is_file() else None
    checks.append({"group": obj["group"], "path": str(p), "expected": obj["actual"],
                   "actual": actual, "match": actual == obj["actual"]})

report = ROOT / "DocuN/results/TASK-101-result.md"
checks.append({"group": "audit_report", "path": str(report),
               "expected": audit_freeze["report_sha256"], "actual": digest(report),
               "match": digest(report) == audit_freeze["report_sha256"]})
mismatches = [c for c in checks if not c["match"]]
if mismatches:
    save("identity-blocked.json", mismatches)
    raise SystemExit("Identity drift; no shared-state edits authorized by this script.")

backups = []
for rel in (
    "DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
    "DocuN/tasks/TASK-100.md", "DocuN/tasks/TASK-101.md",
    "DocuN/results/TASK-100-work-decision.md",
):
    src = ROOT / rel
    dst = OUT / "before" / rel
    if dst.exists():
        raise SystemExit(f"Existing backup must not be overwritten: {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    backups.append({"path": rel, "backup": str(dst), "sha256": digest(dst)})

identities = []
for p in sorted(AUDIT.iterdir()):
    if p.is_file():
        identities.append({"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size})
save("audit-delivery-identity.json", identities)
save("baseline-checks.json", checks)
save("before-manifest.json", backups)

save("continuation-input.json", {
    "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "project_root": str(ROOT), "task": "TASK-100", "R": "R-094",
    "continuation": "audit-repair-03", "rules": "task_model V4.0 CHG-0003",
    "audit_report": {"path": str(report), "sha256": digest(report)},
    "audited_input_sha256": audit_freeze["snapshot_sha256"],
    "source_contract": "DocuN/results/TASK-099-result.md",
    "objects": checks,
    "note": "File identity only. Raw 657-file audit conclusions are referenced, not rerun. New permit is in the task card, never inferred from this index.",
})
save("receipt.json", {
    "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "audit_delivery": "accepted", "g8_disposition": "not_accepted_pending_consolidated_repair",
    "object_checks": len(checks), "mismatches": 0,
    "prior_pg_classification": {"intermediate_version_ok_methods": 25, "later_final_version_ok_methods": 4,
                                "not_a_claim": "29 final-version PG passes"},
    "prior_content": "Concept/program citation support fails; structural and transaction observations remain scoped evidence.",
    "current_findings": [{"DEF": f"DEF-{8+i:03d}", "audit": k, "severity": s}
                         for i, (k, s) in enumerate([
        ("F01", "P1"), ("F02", "P1"), ("F03", "P2"), ("F04", "P2"),
        ("F05", "P2"), ("F06", "P2"), ("F07", "P2"), ("F08", "P2"),
        ("F09", "P2"), ("E02", "P1"), ("E01", "P2")])],
    "resource_read_only_observation": {
        "at": "2026-10-05T16:32:48.4030400+08:00",
        "container_id": "80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d",
        "state": "exited", "running": False, "pid": 0, "exit_code": 0,
        "listeners_18100_55442": [], "task100_runtime_processes": [],
        "method": "docker inspect State + Get-NetTCPConnection + filtered Win32_Process; no credentials/output command lines",
    },
    "orchestrator_executions": {"product_imports": 0, "tests": 0, "build": 0, "PG_connections": 0,
                                "resource_mutations": 0, "browser": 0, "Job": 0},
    "auxiliary_search_error": "An initial rg Windows wildcard path was invalid (exit 1); rg --files then supplied the exact enumeration. No business execution.",
})
print(json.dumps({"checks": len(checks), "mismatches": 0, "audit_files": len(identities),
                  "report_sha256": digest(report), "out": str(OUT)}, ensure_ascii=False))
