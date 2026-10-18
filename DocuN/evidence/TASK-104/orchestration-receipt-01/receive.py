"""回收104独立终审原件和资源状态，编排不执行产品验证。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-104"
OUT = BASE / "orchestration-receipt-01"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "已有回收记录必须保留"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    delivery = load(BASE / "audit/delivery-check.json")
    report = (ROOT / "DocuN/results/TASK-104-result.md").read_bytes()
    assert sha(report) == delivery["result_sha256"] and len(report) == delivery["result_bytes"]
    previous = load(ROOT / "DocuN/evidence/TASK-103/orchestration-receipt-03/current-baseline.json")
    identity = load(BASE / "audit/final-identity-check.json")
    checks = []
    for row in identity["checks"]:
        p = Path(row["path"])
        if not p.is_absolute():
            p = ROOT / p
        expected = row["expected"]
        actual = sha(p.read_bytes())
        checks.append({"path": str(p), "expected": expected, "actual": actual, "match": actual == expected})
    assert len(checks) == 325 and all(r["match"] for r in checks)
    current = dict(previous)
    for rel, expected in previous.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    new_harness = sorted((ROOT / "backend/tests/fixtures/task104").glob("*.py"))
    new_harness.append(ROOT / "frontend/tests/task104-citation-audit.cjs")
    for p in new_harness:
        current[p.relative_to(ROOT).as_posix()] = sha(p.read_bytes())
    save("identity-checks.json", checks)
    save("current-baseline.json", current)
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
                "DocuN/results/TASK-103-work-decision.md", "DocuN/tasks/TASK-103.md"]:
        data = (ROOT / rel).read_bytes()
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        p.write_bytes(data)
        before.append({"path": rel, "sha256": sha(data), "bytes": len(data)})
    save("before-manifest.json", before)
    (OUT / "TASK-104-as-returned.md").write_bytes(report)
    source = (ROOT / "frontend/src/activities/MemoryWorkspace.tsx").read_text(encoding="utf-8")
    assert "await refresh();await select(identity);return;" in source
    excerpt = load(BASE / "audit/R104-F01-final-bundle-excerpt.json")
    bundle_path = Path(excerpt["path"])
    if not bundle_path.is_absolute():
        bundle_path = ROOT / bundle_path
    assert sha(bundle_path.read_bytes()) == excerpt["sha256"]
    assert excerpt["excerpt"] in bundle_path.read_text(encoding="utf-8")
    conclusions = load(BASE / "audit/audit-conclusions.json")
    assert conclusions["blocking"][0]["id"] == "R104-F01" and conclusions["blocking"][0]["priority"] == "P1"
    ledger = load(BASE / "runtime-ledger.json")
    evidence = []
    for rel in ["audit/delivery-check.json", "audit/audit-conclusions.json", "audit/initial-identity-check.json",
                "audit/final-identity-check.json", "audit/R104-F01-static-finding.md", "audit/R104-F01-final-bundle-excerpt.json",
                "audit/product-diff-current.patch", "audit/all-run-version-applicability.json",
                "audit/sql-current-source-app-live-catalog-binding.json", "audit/final-bundle-source-and-old-native-load-binding.json",
                "audit/verified-old-behavior-and-c02-pairing.json", "audit/execution-control-conclusion.json",
                "audit/final-readonly-resource-state.json", "audit/session-accounting.json", "runtime-ledger.json",
                "read-only-01/root-result.json", "read-only-02/root-result.json", "read-only-03/root-result.json"]:
        p = BASE / rel
        data = p.read_bytes()
        evidence.append({"path": str(p), "sha256": sha(data), "bytes": len(data)})
    save("returned-evidence-identities.json", evidence)
    old_resource = load(ROOT / "DocuN/evidence/TASK-103/orchestration-receipt-03/resource-readonly.json")
    containers = []
    for old in old_resource["containers"]:
        result = subprocess.run(["docker.exe", "inspect", "--type", "container", old["cid"]], capture_output=True, timeout=15, check=False)
        assert result.returncode == 0
        raw = json.loads(result.stdout)[0]
        hc = raw["HostConfig"]
        labels = raw["Config"].get("Labels", {})
        row = {"cid": raw["Id"], "name": raw["Name"].lstrip("/"), "image": raw["Image"],
               "running": raw["State"]["Running"], "pid": raw["State"]["Pid"], "exit_code": raw["State"]["ExitCode"],
               "labels": {k: labels.get(k) for k in ("retrolume.task", "retrolume.permit", "retrolume.synthetic")},
               "mounts": [{k: m.get(k) for k in ("Type", "Name", "Destination", "RW")} for m in raw["Mounts"]],
               "limits": {k: hc.get(k) for k in ("NanoCpus", "Memory", "PidsLimit", "Privileged")},
               "restart": hc["RestartPolicy"]["Name"], "ports": hc["PortBindings"]}
        assert row["cid"] == old["cid"] and row["name"] == old["name"] and row["image"] == old["image"]
        assert not row["running"] and row["pid"] == 0
        assert row["labels"] == old["labels"] and row["mounts"] == old["mounts"] and row["limits"] == old["limits"]
        assert row["restart"] == old["restart"] and row["ports"] == old["ports"]
        containers.append(row)
    pc = "$p=@(18103,18104,55443,55444,55445); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $p} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    pr = subprocess.run(["powershell.exe", "-NoProfile", "-Command", pc], capture_output=True, timeout=15, check=False)
    assert pr.returncode == 0
    listeners = json.loads(pr.stdout) if pr.stdout.strip() else []
    save("resource-readonly.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
         "containers": containers, "listeners": listeners, "new_starts_SQL_or_tests": 0})
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-104", "R": "R-098",
         "dispatch": "已实际返回", "report_sha256": sha(report), "report_bytes": len(report), "identity_checks": len(checks),
         "unchanged_prior_objects": len(previous), "new_harness_files": len(new_harness), "current_objects": len(current),
         "audit_receipt": "接受独立审查交付和原件；G9终审不通过，最后引用未验，任务待修后增量",
         "P1": "R104-F01，真实可达旧保存后列表GET返回未经重新确认身份select(A)，源码及现有bundle绑定；B级确定推导，不冒实测误写",
         "independence": "实际沿101独立审计会话的隔离职责，非完全空白窗口；未参与102/103，例外已披露，非重审理由",
         "nonblocking": conclusions["nonblocking"], "DEF_recommendations": conclusions["DEF_recommendations"],
         "counts": ledger["counts"], "used_seconds": ledger["used"],
         "active_checkpoint_seconds": delivery["active_checkpoint_seconds"], "active_upper_with_reply": delivery["active_upper_with_reply"],
         "previous_permission_ended": True, "all_owned_stopped": True, "no_listeners": not listeners,
         "root_product_writes": 0, "root_business_runs": 0,
         "next": "原TASK103/R097审计修复03，一次交付P1身份修复／准确窗口及最后引用补证，原104后续仅增量"})
    print(json.dumps({"checks": len(checks), "current": len(current), "report_bytes": len(report), "report_sha256": sha(report),
                      "owned_stopped": True, "no_listeners": not listeners, "root_product_runs": 0}))


if __name__ == "__main__":
    main()
