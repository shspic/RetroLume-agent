"""普通回收修复03，仅核真实字节、原件、历史与资源metadata。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-103/audit-repair-03"
OUT = ROOT / "DocuN/evidence/TASK-103/orchestration-repair-03-receipt"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "不覆盖已保存回收记录"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    previous = load(ROOT / "DocuN/evidence/TASK-104/orchestration-receipt-01/current-baseline.json")
    delta = load(BASE / "final/pre-diff-post.json")
    assert len(previous) == delta["base_files"] == 297
    current = dict(previous)
    for row in delta["changed"]:
        assert previous[row["path"]] == row["pre_sha256"]
        current[row["path"]] = row["post_sha256"]
    for rel in delta["deleted"]:
        assert rel in current and not (ROOT / rel).exists()
        current.pop(rel)
    for row in delta["added"]:
        assert row["path"] not in current
        current[row["path"]] = row["sha256"]
    assert len(current) == delta["final_files"] == 308
    checks = []
    for rel, expected in current.items():
        actual = sha((ROOT / rel).read_bytes())
        checks.append({"path": rel, "expected": expected, "actual": actual, "match": actual == expected})
    rules = load(BASE / "rules-verified.json")
    for row in rules:
        p = Path(row["path"])
        actual = sha(p.read_bytes())
        checks.append({"path": str(p), "expected": row["sha256"], "actual": actual, "match": actual == row["sha256"]})
    assert all(r["match"] for r in checks)
    post = load(BASE / "final/post/identities.json")
    assert len(post) == 308
    for row in post:
        assert current[row["path"]] == row["sha256"]
        assert sha((BASE / "final/post" / row["path"]).read_bytes()) == row["sha256"]
    for row in delta["changed"]:
        assert sha((BASE / "pre" / row["path"]).read_bytes()) == row["pre_sha256"]
    for rel in delta["deleted"]:
        assert sha((BASE / "pre" / rel).read_bytes()) == previous[rel]
    save("identity-checks.json", checks)
    save("current-baseline.json", current)
    history = load(BASE / "final/history-proof.json")
    report = (ROOT / "DocuN/results/TASK-103-result.md").read_bytes()
    offset = history["prefix_bytes"]
    assert sha(report[:offset]) == history["prefix_sha256"]
    assert len(report[offset:]) == history["history_bytes"] == 52856
    assert sha(report[offset:]) == history["history_sha256"]
    old_report = ROOT / "DocuN/evidence/TASK-103/audit-repair-03/original-result.md"
    assert report[offset:] == old_report.read_bytes()
    (OUT / "TASK-103-as-returned.md").write_bytes(report)
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
                "DocuN/results/TASK-103-work-decision.md", "DocuN/results/TASK-104-work-decision.md", "DocuN/tasks/TASK-104.md"]:
        data = (ROOT / rel).read_bytes()
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        p.write_bytes(data)
        before.append({"path": rel, "sha256": sha(data), "bytes": len(data)})
    save("before-manifest.json", before)
    bundle = load(BASE / "final/bundle-chain.json")
    assert len(bundle["source"]) == 24
    for row in [*bundle["source"], *bundle["final_dist"]]:
        assert sha((ROOT / row["path"]).read_bytes()) == row["sha256"]
    for row in bundle["loaded"]:
        p = ROOT / "frontend/dist" / row["path"].lstrip("/")
        assert sha(p.read_bytes()) == row["sha256"] and row["bytes_match_final"]
    runs = load(BASE / "final/runs-ledger.json")
    for row in runs:
        assert sha(Path(row["execution_path"]).read_bytes()) == row["execution_sha256"]
    evidence = []
    rels = ["final/pre-diff-post.json", "final/product.patch", "final/bundle-chain.json", "final/runs-ledger.json",
            "final/accounting-final.json", "final/resources-after.json", "final/old-facts-preserved.json",
            "final/sql-backend-frozen.json", "captured-pg-verification.json",
            "groups/real-03-r03-p1-unique-effect/result.json", "groups/real-03-r03-p1-unique-effect/persistent-command-proof.json",
            "groups/real-03-r03-p1-unique-effect/browser/result.json",
            "groups/real-03-r03-p1-unique-effect/browser/p1-post-controller.json",
            "groups/real-03-r03-p1-unique-effect/browser/p1-confirmed-refresh-controller.json",
            "groups/real-02-r03-preloaded-targets/result.json", "groups/real-02-r03-preloaded-targets/browser/result.json",
            "groups/real-02-r03-preloaded-targets/browser/late-citation-controller.json"]
    for rel in rels:
        p = BASE / rel
        data = p.read_bytes()
        row = {"path": str(p), "sha256": sha(data), "bytes": len(data)}
        if rel.endswith("result.json"):
            value = json.loads(data)
            row["status"] = value.get("status")
            row["cases"] = [{"name": c.get("name"), "status": c.get("status"), "executed": c.get("executed")}
                            for c in value.get("cases", [])]
        evidence.append(row)
    save("returned-evidence-identities.json", evidence)
    old_resource = load(ROOT / "DocuN/evidence/TASK-104/orchestration-receipt-01/resource-readonly.json")
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
        assert all(row[k] == old[k] for k in ["cid", "name", "image", "labels", "mounts", "limits", "restart", "ports"])
        assert not row["running"] and row["pid"] == 0
        containers.append(row)
    cmd = "$p=@(18103,18104,55443,55444,55445); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $p} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    ports = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, timeout=15, check=False)
    assert ports.returncode == 0
    listeners = json.loads(ports.stdout) if ports.stdout.strip() else []
    save("resource-readonly.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
         "containers": containers, "listeners": listeners, "new_starts_SQL_or_tests": 0})
    accounting = load(BASE / "final/accounting-final.json")
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-103", "R": "R-097",
         "round": "审计修复03", "dispatch": "已实际返回", "acceptance": "普通接收修复候选与新增原件；DEF023及G9最终等待104增量",
         "report_sha256": sha(report), "report_bytes": len(report), "history_52856_bytes_exact": True,
         "current_objects": 308, "complete_post_objects": 308, "identity_checks": len(checks),
         "changed_product_sources": 2, "changed_dist_entry": 1, "old_js_preserved_pre": True,
         "loaded_asset_hash_checks": len(bundle["loaded"]), "frontend_source_build_bound": 24,
         "run_execution_records_checked": len(runs), "run_record_correction": "真实结构化run记录9份；报告八份为数量误写，核证以实际9份及5离线/1build/3真实账为准",
         "scope": "源码差异／原件身份普通核对，不替代独立审计；real02 rootFAIL与browserPASS并存，real03其余五项继承",
         "all_owned_stopped": True, "no_listeners": not listeners, "counts": accounting["counts"], "seconds": accounting["used_seconds"],
         "active_seconds": accounting["active_used_seconds"], "old_permission_ended": True,
         "root_product_writes": 0, "root_business_runs": 0, "next": "原TASK104/R098 review02只读增量，零测试启动"})
    print(json.dumps({"objects": 308, "post": 308, "checks": len(checks), "report_bytes": len(report), "report_sha256": sha(report),
                      "records": len(runs), "all_owned_stopped": True, "no_listeners": not listeners, "root_product_runs": 0}))


if __name__ == "__main__":
    main()
