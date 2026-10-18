"""Read/hash design receipt only; no product import or business execution."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-102"
OUT = BASE / "orchestration-receipt-01"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    path = OUT / name
    if path.exists():
        raise RuntimeError("Do not replace existing receipt")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    consistency = load(BASE / "consistency-check.json")
    final = consistency["final_document_binding"]
    report = (ROOT / "DocuN/results/TASK-102-result.md").read_bytes()
    if sha(report) != final["sha256"] or len(report) != final["bytes"]:
        raise RuntimeError("Actual report differs from final document binding")
    declared = load(BASE / "read-hashes.json")
    checks = []
    for row in declared["objects"]:
        path = Path(row["path"])
        actual = sha(path.read_bytes()) if path.is_file() else None
        checks.append({"path": str(path), "expected": row["sha256"], "actual": actual, "match": actual == row["sha256"]})
    if len(checks) != 59 or any(not row["match"] for row in checks):
        save("blocked-identities.json", checks)
        raise RuntimeError("Design input drift")
    functions = load(BASE / "function-facts.json")["functions"]
    signatures = []
    for row in functions:
        path = Path(row["path"])
        data = path.read_bytes()
        lines = data.decode("utf-8-sig").splitlines()
        for match in row["matches"]:
            exact = lines[match["line"] - 1].strip() == match["signature"].strip()
            signatures.append({"path": str(path), "function": row["function"], "line": match["line"], "exact": exact})
        if sha(data) != row["sha256"]:
            raise RuntimeError("Actual mapped function file changed")
    if any(not row["exact"] for row in signatures):
        save("blocked-signatures.json", signatures)
        raise RuntimeError("Function positioning does not match actual source")
    accounting = load(BASE / "session-accounting.json")
    if any(accounting["runtime_counts"].values()):
        raise RuntimeError("Unexpected product/business operation in read-only design")
    save("identity-checks.json", checks)
    save("function-signature-checks.json", signatures)
    (OUT / "TASK-102-as-returned.md").write_bytes(report)
    rels = ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/tasks/TASK-102.md"]
    backups = []
    for rel in rels:
        data = (ROOT / rel).read_bytes()
        path = OUT / "before" / rel
        if path.exists():
            raise RuntimeError("Prior shared state already preserved")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        backups.append({"path": rel, "sha256": sha(data), "bytes": len(data), "backup": str(path)})
    save("before-manifest.json", backups)
    save("source-verification.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "existing_source_FK": "001 has UNIQUE(source_id,id); M4 source composite target exists",
        "existing_event_FK": "009 PRIMARY KEY(activity_id,record_id); M4 event composite target exists",
        "current_locks": "_teaching_lock already takes sources then activity; proposed memory prefix must precede first activity lock",
        "v1_adapter": "Current validate_teaching_request recomputes messages from request data; proposed v2 must instead use persistent recipe and qualification, not request self-certification",
        "official_readonly_verified": [
            {"url": "https://www.postgresql.org/docs/16/sql-createfunction.html", "fact": "SECURITY DEFINER uses owner privileges; restrict search_path and remove default PUBLIC execute in the creation transaction"},
            {"url": "https://www.postgresql.org/docs/16/explicit-locking.html", "fact": "Consistent object order reduces deadlocks; same most restrictive lock must be obtained before later operations"},
            {"url": "https://www.postgresql.org/docs/16/transaction-iso.html", "fact": "Read Committed may show different committed versions to successive SELECT commands"},
            {"url": "https://www.postgresql.org/docs/16/functions-binarystring.html", "fact": "Core sha256(bytea) and convert_to(text,encoding) support UTF8 hash protocol"}
        ], "actual_database_version_or_role_validation": False,
        "ordinary_contract_clarification": "MemoryPage projects metadata and qualified short title only; full body and dependency closure are detail reads; keep wire response <=65536 bytes"})
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-102", "R": "R-096",
        "dispatch": "returned", "document_delivery": "accepted; full A-D implementation contract",
        "G9-P": "recommended; pending one explicit adoption decision, no implementation authorized",
        "report_sha256": sha(report), "report_bytes": len(report), "input_matches": len(checks),
        "mapped_function_entries": len(functions), "exact_signature_matches": len(signatures),
        "document_check_effective_passes": consistency["effective_text_checks_passed"], "initial_false_count_retained": True,
        "active_charge_seconds": accounting["active_upper_charge_seconds"], "active_basis": "continuous wall-time plus conservative first-read/reply charges; not exact whole monotonic timing",
        "metadata_conservative_seconds": accounting["metadata_conservative_charge_seconds"],
        "metadata_known_exec_seconds": accounting["metadata_known_exec_wall_seconds"], "unknowns_preserved": accounting["unknown"],
        "actual_window": "TASK102 actual Codex desktop/GPT6 context; original100 same-chat not proven, file-based handover accepted without brand re-audit",
        "root_product_writes": 0, "root_product_test_runs": 0, "official_public_readonly_pages": 4,
        "next": "Concrete G9-P adoption decision; TASK103/R097 stays planned only until authorization"})
    print(json.dumps({"report_sha256": sha(report), "bytes": len(report), "inputs": len(checks), "functions": len(functions),
        "signature_matches": len(signatures), "document_check": consistency["effective_text_checks_passed"],
        "active_upper": accounting["active_upper_charge_seconds"], "metadata_conservative": accounting["metadata_conservative_charge_seconds"],
        "business_runs": 0, "G9-P": "pending explicit adoption"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
