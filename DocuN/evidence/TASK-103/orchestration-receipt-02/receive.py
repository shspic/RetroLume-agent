"""编排普通回收，仅核哈希、原字节历史、原始元数据和自有资源只读状态。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess
import ast
import re

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-103"
FINAL = BASE / "continuation-01/final"
OUT = BASE / "orchestration-receipt-02"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    path = OUT / name
    if path.exists():
        assert load(path) == obj, "Existing receipt differs; preserve and investigate"
        return
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    old = load(BASE / "orchestration-receipt-01/current-baseline.json")
    change = load(FINAL / "pre-diff-post.json")
    current = dict(old)
    checks = []
    for row in change["changed"]:
        assert old[row["path"]] == row["pre_sha256"]
        current[row["path"]] = row["post_sha256"]
    for row in change["added"]:
        assert row["path"] not in current
        current[row["path"]] = row["sha256"]
    for row in change["deleted"]:
        rel = row["path"]
        assert rel in current and not (ROOT / rel).exists()
        current.pop(rel)
    assert len(old) == 266 and len(current) == 281
    for rel, expected in current.items():
        actual = digest((ROOT / rel).read_bytes())
        checks.append({"path": rel, "expected": expected, "actual": actual, "match": actual == expected})
    protected = load(FINAL / "protected-files.json")
    rules = load(FINAL / "rules-contracts-final.json")
    rule_lock = load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json")
    for row in [*protected, *rules]:
        path = Path(row["path"])
        if not path.is_absolute():
            path = ROOT / path
        actual = digest(path.read_bytes())
        checks.append({"path": str(path), "expected": row["sha256"], "actual": actual,
                       "match": actual == row["sha256"]})
    for row in rule_lock:
        path = Path(row["absolute_path"])
        actual = digest(path.read_bytes())
        checks.append({"path": str(path), "expected": row["sha256"], "actual": actual,
                       "match": actual == row["sha256"], "locked_rule": True})
    post = load(FINAL / "post/identities.json")
    assert len(post) == 281
    for row in post:
        assert current[row["path"]] == row["sha256"]
        assert digest((FINAL / "post" / row["path"]).read_bytes()) == row["sha256"]
    save("identity-checks.json", checks)
    if not all(row["match"] for row in checks):
        raise RuntimeError("Current object identity drift; related dispatch must stop")
    save("current-baseline.json", current)
    report = (ROOT / "DocuN/results/TASK-103-result.md").read_bytes()
    hp = load(FINAL / "result-history-proof.json")
    offset = hp["historical_suffix_offset"]
    assert digest(report[offset:]) == hp["original_sha256"]
    assert len(report[offset:]) == hp["original_bytes"]
    assert digest(report[:offset]) == hp["prefix_sha256"]
    assert len(report[:offset]) == hp["prefix_bytes"]
    assert report[offset:] == (BASE / "orchestration-receipt-01/TASK-103-as-returned.md").read_bytes()
    returned = OUT / "TASK-103-as-returned.md"
    if returned.exists():
        assert returned.read_bytes() == report
    else:
        returned.write_bytes(report)
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
                "DocuN/tasks/TASK-103.md", "DocuN/results/TASK-103-work-decision.md"]:
        data = (ROOT / rel).read_bytes()
        path = OUT / "before" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            assert path.read_bytes() == data
        else:
            path.write_bytes(data)
        before.append({"path": rel, "bytes": len(data), "sha256": digest(data)})
    save("before-manifest.json", before)
    bundle = load(FINAL / "bundle-chain.json")
    assert len(bundle["source_matches_build"]) == 24
    assert all(row["match"] and digest((ROOT / row["path"]).read_bytes()) == row["source_sha256"]
               for row in bundle["source_matches_build"])
    for row in bundle["dist"]:
        assert digest((ROOT / row["path"]).read_bytes()) == row["sha256"]
    for row in bundle["loaded"]:
        assert row["complete_bytes_match"]
        assert digest((ROOT / "frontend/dist" / row["path"].lstrip("/")).read_bytes()) == row["sha256"]
    runs = load(FINAL / "runs-ledger.json")
    for row in runs["runs"]:
        assert digest(Path(row["execution_path"]).read_bytes()) == row["execution_sha256"]
    sql = load(FINAL / "sql-chain.json")
    migration = (ROOT / "backend/migrations/010_learning_memory.sql").read_text(encoding="utf-8")
    assert sql["migration_sha256"] == digest(migration.encode("utf-8"))
    functions_from_sql = {m.group(1): digest(re.sub(r"\s+", "", m.group(2)).encode("utf-8"))
                          for m in re.finditer(r"CREATE FUNCTION public\.(\w+)\(.*?\bAS \$f\$(.*?)\$f\$;", migration, re.S)}
    repository_ast = ast.parse((ROOT / "backend/app/memory/repository.py").read_text(encoding="utf-8"))
    application_fingerprints = next(ast.literal_eval(n.value) for n in repository_ast.body
        if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "FUNCTION_FINGERPRINTS" for x in n.targets))
    assert len(functions_from_sql) == 12 and functions_from_sql == application_fingerprints == sql["source_fingerprints"]
    for row in sql["actual_catalogs"]:
        assert digest(Path(row["catalog"]).read_bytes()) == row["catalog_sha256"]
        assert row["all_12_match"] and row["fingerprints"] == sql["source_fingerprints"]
        raw_catalog = load(Path(row["catalog"]))
        catalog_fingerprints = {r[0]: digest(re.sub(r"\s+", "", r[2]).encode("utf-8"))
                                for r in raw_catalog["functions"] if r[0] in application_fingerprints}
        assert catalog_fingerprints == functions_from_sql
    forward = []
    for name in sql["forward_proofs"]:
        value = load(Path(name))
        assert value["rows_before_sha"] == value["rows_after_sha"]
        forward.append({"path": name, "sha256": digest(Path(name).read_bytes()), "keys": list(value),
                        "functions": value.get("functions"),
                        "row_hash_same": value.get("rows_before_sha") == value.get("rows_after_sha")})
    evidence = []
    for rel in ["final/pre-diff-post.json", "final/accounting-final.json", "final/runs-ledger.json",
                "final/sql-chain.json", "final/bundle-chain.json", "final/resources-after.json",
                "final/validation-matrix.json", "final/product.patch", "browser-01/result.json",
                "browser-02/result.json", "browser-03/result.json", "core-checkpoint.json",
                "gaps-result-real-12-resume-contract-status-and-absent.json", "final/runtime-configs.json"]:
        path = BASE / "continuation-01" / rel
        data = path.read_bytes()
        row = {"path": str(path), "sha256": digest(data), "bytes": len(data)}
        if rel.endswith("result.json") or rel.endswith("checkpoint.json") or "gaps-result" in rel:
            value = json.loads(data)
            row["status"] = value.get("status")
            row["case_statuses"] = [{"name": case.get("name"), "status": case.get("status"),
                                     "executed": case.get("executed")}
                                    for case in value.get("cases", [])]
        evidence.append(row)
    save("returned-evidence-identities.json", evidence)
    save("finite-binding-checks.json", {"history_exact": True, "post_current_exact": True,
         "post_objects": len(post), "frontend_source_count": 24, "dist": bundle["dist"],
         "loaded_assets": len(bundle["loaded"]), "browser_batch_status": bundle["browser_status"],
         "run_records_with_execution_hash_checked": len(runs["runs"]), "sql_catalogs": sql["actual_catalogs"],
         "migration_raw_bytes_sha256": current["backend/migrations/010_learning_memory.sql"],
         "migration_universal_newline_text_sha256": sql["migration_sha256"],
         "sql_source_application_raw_catalog_12_equal": True,
         "forward": forward, "pg2_reported_old_rows_same": sql["pg2_original_14_tables_32_rows_match"],
         "scope": "ordinary receipt and raw identity spot checks; not independent code audit or rerun",
         "receipt_metadata_correction": "Initial assertion mixed raw CRLF file SHA with package read_text universal-newline LF SHA; actual domains both verified; not product drift or SQL failure",
         "last_mapping": "teaching_api LearningRefusal/no_evidence ->409 only final ASGI stub proof; needs live HTTP zero-effect check"})
    accounting = load(FINAL / "accounting-final.json")
    resources = load(FINAL / "resources-after.json")
    owned = []
    for old_resource in resources["containers"]:
        result = subprocess.run(["docker.exe", "inspect", "--type", "container", old_resource["cid"]],
                                capture_output=True, timeout=15, check=False)
        if result.returncode:
            owned.append({"cid": old_resource["cid"], "verified": False, "exit_code": result.returncode})
            continue
        obj = json.loads(result.stdout)[0]
        labels = obj["Config"].get("Labels", {})
        value = {"cid": obj["Id"], "name": obj["Name"].lstrip("/"), "image": obj["Image"],
                 "state": {key: obj["State"].get(key) for key in ("Status", "Running", "Pid", "ExitCode")},
                 "labels": {key: labels.get(key) for key in ("retrolume.task", "retrolume.permit", "retrolume.synthetic")},
                 "mounts": [{key: item.get(key) for key in ("Type", "Name", "Destination", "RW")} for item in obj.get("Mounts", [])],
                 "limits": {key: obj["HostConfig"].get(key) for key in ("NanoCpus", "Memory", "PidsLimit", "Privileged")},
                 "restart": obj["HostConfig"]["RestartPolicy"].get("Name"),
                 "port_bindings": obj["HostConfig"].get("PortBindings")}
        value["verified"] = (value["cid"] == old_resource["cid"] and value["image"] == old_resource["image"]
            and value["name"] == old_resource["name"] and not value["state"]["Running"] and value["state"]["Pid"] == 0
            and value["labels"]["retrolume.task"] == "TASK-103"
            and value["labels"]["retrolume.permit"] == "TASK-103-G9-20261006"
            and value["limits"]["Memory"] == 536870912 and value["limits"]["NanoCpus"] == 1000000000
            and value["limits"]["PidsLimit"] == 128 and not value["limits"]["Privileged"]
            and len(value["mounts"]) == 1 and value["mounts"][0]["Type"] == "volume"
            and value["mounts"][0]["Name"] == old_resource["volume"] and value["restart"] == "no"
            and all(item["HostIp"] == "127.0.0.1" for items in value["port_bindings"].values() for item in items))
        owned.append(value)
    ports_cmd = "$p=@(18103,18104,55443,55444,55445); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $p} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    port_result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ports_cmd], capture_output=True, timeout=15, check=False)
    ports = json.loads(port_result.stdout) if port_result.stdout.strip() else []
    save("resource-readonly.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
         "containers": owned, "port_probe_exit_code": port_result.returncode, "listeners": ports,
         "operations": "inspect JSON only; no Env retained; read-only listen table", "starts_SQL_or_tests": 0})
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-103", "R": "R-097",
         "dispatch": "continuation01 returned", "acceptance": "partial candidate and finite evidence received; G9 not final accepted",
         "report_sha256": digest(report), "report_bytes": len(report), "history_exact": True,
         "current_sources": len(current), "post_snapshots": len(post), "protected_files": len(protected),
         "rules_and_contracts": len(rules), "locked_rules": len(rule_lock), "all_identity_checks": len(checks),
         "all_owned_stopped_verified": all(row["verified"] for row in owned), "no_target_listeners": not ports,
         "counts": accounting["counts"], "used_seconds": accounting["used_seconds"],
         "active_seconds": accounting["active_used_seconds"], "previous_permission_ended": True,
         "pending": ["V15 late real save receipt", "V15 late real citation response", "V15 actual stale browser POST", "last no_evidence mapping live HTTP zero-effect confirmation"],
         "root_product_writes": 0, "root_business_runs": 0,
         "next": "TASK103/R097 continuation02 focused combined proof; then one concentrated independent audit"})
    print(json.dumps({"current_sources": len(current), "post": len(post), "checks": len(checks),
                      "report_bytes": len(report), "report_sha256": digest(report),
                      "owned_stopped": all(row["verified"] for row in owned), "no_listeners": not ports,
                      "root_business_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
