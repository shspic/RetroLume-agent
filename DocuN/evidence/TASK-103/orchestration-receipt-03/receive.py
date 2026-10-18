"""普通回收续作02，验证原件身份和自有资源只读状态，不执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-103"
C02 = BASE / "continuation-02"
OUT = BASE / "orchestration-receipt-03"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    p = OUT / name
    assert not p.exists(), "保留现有编排记录，不覆盖"
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    baseline = load(BASE / "orchestration-receipt-02/current-baseline.json")
    manifest = load(C02 / "final/pre-diff-post.json")
    current = dict(baseline)
    assert manifest["baseline_files"] == 281 and manifest["product_changed"] is False
    for row in manifest["added"]:
        assert row["path"] not in current
        current[row["path"]] = row["sha256"]
    assert len(current) == 291
    checks = []
    for rel, expected in current.items():
        actual = sha((ROOT / rel).read_bytes())
        checks.append({"path": rel, "expected": expected, "actual": actual, "match": expected == actual})
    rules = load(C02 / "rules-verified.json")
    protected = load(BASE / "continuation-01/final/protected-files.json")
    for row in [*rules, *protected]:
        p = Path(row["path"])
        if not p.is_absolute():
            p = ROOT / p
        actual = sha(p.read_bytes())
        checks.append({"path": str(p), "expected": row["sha256"], "actual": actual, "match": row["sha256"] == actual})
    assert all(row["match"] for row in checks)
    post = load(C02 / "final/post/identities.json")
    assert len(post) == 291
    for row in post:
        assert current[row["path"]] == row["sha256"]
        assert sha((C02 / "final/post" / row["path"]).read_bytes()) == row["sha256"]
    save("identity-checks.json", checks)
    save("current-baseline.json", current)
    report = (ROOT / "DocuN/results/TASK-103-result.md").read_bytes()
    hist = load(C02 / "final/history-proof.json")
    prefix = hist["prefix_bytes"]
    assert sha(report[:prefix]) == hist["prefix_sha256"]
    assert len(report[prefix:]) == hist["history_bytes"] == 41022
    assert sha(report[prefix:]) == hist["history_sha256"]
    assert report[prefix:] == (BASE / "orchestration-receipt-02/TASK-103-as-returned.md").read_bytes()
    (OUT / "TASK-103-as-returned.md").write_bytes(report)
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/results/TASK-103-work-decision.md"]:
        data = (ROOT / rel).read_bytes()
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        p.write_bytes(data)
        before.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
    save("before-manifest.json", before)
    noev = load(C02 / "no-evidence-http.json")
    assert noev["response_status"] == 409 and noev["response"]["detail"]["code"] == "no_evidence"
    assert noev["before"] == noev["after"] and noev["budgets_before"] == noev["budgets_after"]
    assert all(noev[key] == 0 for key in ["new_accepted_commands", "new_operations", "provider_sends", "sup"])
    pg_before = load(C02 / "tail/pg-before.json")
    browser = load(C02 / "browser/result.json")
    assert browser["status"] == "FAIL" and len(browser["cases"]) == 2
    finite = []
    for case in browser["cases"]:
        assert case["status"] == "PASS" and case["executed"]
        mid = case["memory_id"]
        head = next(r for r in pg_before["learning_memories"] if r["memory_id"] == mid)
        receipts = [r for r in pg_before["learning_memory_commands"] if r["memory_id"] == mid]
        expected = 2 if "陈旧" in case["name"] else 1
        assert head["revision"] == head["current_version"] == expected
        assert sum(r["effect_applied"] for r in receipts) == expected
        if case.get("stale_key"):
            assert not any(r["business_key"] == case["stale_key"] for r in receipts)
        if case.get("business_key"):
            assert sum(r["business_key"] == case["business_key"] for r in receipts) == 1
        finite.append({"name": case["name"], "memory_id": mid, "revision": expected, "persistent_effects": expected,
                       "scope": "真实POST／控制器／DOM原件加后批PG快照，非总批PASS"})
    loaded = load(C02 / "final/bundle-chain.json")
    for row in loaded["loaded"]:
        p = ROOT / "frontend/dist" / row["path"].lstrip("/")
        assert sha(p.read_bytes()) == row["sha256"] and row["complete_bytes_match"]
    runs = load(C02 / "final/runs-ledger.json")
    for row in runs:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    evidence = []
    for rel in ["final/pre-diff-post.json", "final/history-proof.json", "final/runs-ledger.json", "final/accounting-final.json",
                "final/resources-after.json", "final/four-proof-matrix.json", "final/bundle-chain.json",
                "final/persistent-proof.json", "final/unknown-preserved.json", "no-evidence-http.json", "target-selection.json",
                "browser-target.json", "browser/result.json", "browser/late-edit-controller.json", "browser-02/result.json",
                "browser-02/late-switch-controller.json", "tail/result.json", "tail/pg-before.json", "citation-selector-final-not-run.json"]:
        p = C02 / rel
        data = p.read_bytes()
        evidence.append({"path": str(p), "bytes": len(data), "sha256": sha(data)})
    save("returned-evidence-identities.json", evidence)
    save("finite-receipt-checks.json", {"current_281_unchanged": True, "added_fixture_files": 10, "complete_post_objects": 291,
         "history_41022_bytes_exact": True, "no_evidence_real409_six_tables_budgets_equal": True,
         "verified_finite_browser_properties": finite, "all_root_and_browser_totalFAIL_preserved": True,
         "late_save_identity_switch": "另有真实COMMIT回执和浏览器断言；最后独立后批PG快照未取得，不扩签",
         "loaded_asset_hash_checks": len(loaded["loaded"]), "run_execution_hash_checks": len(runs),
         "citation": "NOT_RUN，引用浏览器挂起请求未开始，真实目标GET200不替代迟到验证",
         "scope": "普通回收与原件抽查，不是独立终审"})
    owned = []
    resources = load(C02 / "final/resources-after.json")
    for previous in resources["containers"]:
        result = subprocess.run(["docker.exe", "inspect", "--type", "container", previous["cid"]], capture_output=True, timeout=15, check=False)
        assert result.returncode == 0, "精确owned容器metadata不可读，不能启动依赖任务"
        obj = json.loads(result.stdout)[0]
        hc = obj["HostConfig"]
        labels = obj["Config"].get("Labels", {})
        value = {"cid": obj["Id"], "name": obj["Name"].lstrip("/"), "image": obj["Image"],
                 "running": obj["State"]["Running"], "pid": obj["State"]["Pid"], "exit_code": obj["State"]["ExitCode"],
                 "labels": {k: labels.get(k) for k in ("retrolume.task", "retrolume.permit", "retrolume.synthetic")},
                 "mounts": [{k: m.get(k) for k in ("Type", "Name", "Destination", "RW")} for m in obj["Mounts"]],
                 "limits": {k: hc.get(k) for k in ("NanoCpus", "Memory", "PidsLimit", "Privileged")},
                 "restart": hc["RestartPolicy"]["Name"], "ports": hc["PortBindings"]}
        assert value["cid"] == previous["cid"] and value["image"] == previous["image"] and value["name"] == previous["name"]
        assert not value["running"] and value["pid"] == 0
        assert value["labels"]["retrolume.task"] == "TASK-103" and value["labels"]["retrolume.permit"] == "TASK-103-G9-20261006"
        assert hc["NanoCpus"] == 1000000000 and hc["Memory"] == 536870912 and hc["PidsLimit"] == 128 and not hc["Privileged"]
        assert len(value["mounts"]) == 1 and value["mounts"][0]["Type"] == "volume" and value["mounts"][0]["Name"] == previous["volume"]
        assert value["restart"] == "no" and all(x["HostIp"] == "127.0.0.1" for vs in value["ports"].values() for x in vs)
        owned.append(value)
    ports_cmd = "$p=@(18103,18104,55443,55444,55445); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $p} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    p = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ports_cmd], capture_output=True, timeout=15, check=False)
    assert p.returncode == 0
    listeners = json.loads(p.stdout) if p.stdout.strip() else []
    save("resource-readonly.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "containers": owned,
         "listeners": listeners, "target_ports": [18103, 18104, 55443, 55444, 55445], "starts_SQL_or_tests": 0})
    accounting = load(C02 / "final/accounting-final.json")
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-103", "R": "R-097",
         "dispatch": "续作02已返回", "acceptance": "保存稳定实现候选与三项有限补证；最后引用迟到未验，G9未最终通过",
         "report_bytes": len(report), "report_sha256": sha(report), "history_exact": True,
         "current_files": 291, "baseline_281_unchanged": True, "post_snapshots": 291,
         "rules_contracts": len(rules), "protected": len(protected), "all_checks": len(checks),
         "all_owned_stopped": True, "no_target_listeners": not listeners,
         "counts": accounting["counts"], "seconds": accounting["used_seconds"], "active_seconds": accounting["active_used_seconds"],
         "previous_permission_ended": True, "root_business_runs": 0, "root_product_writes": 0,
         "next": "稳定产品无新差异，最后只读引用补证并入TASK104/R098集中隔离独立审计，不新增纯实施补卡"})
    print(json.dumps({"current": 291, "checks": len(checks), "report_bytes": len(report), "report_sha256": sha(report),
                      "stopped": True, "no_listeners": not listeners, "product_runs": 0, "next": "TASK-104 / R-098"}))


if __name__ == "__main__":
    main()
