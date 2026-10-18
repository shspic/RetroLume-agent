"""普通回收106部分实现、失败与精确资源，只核元数据，不执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-106"
OUT = BASE / "orchestration-receipt-01"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "保留已保存回收，不覆盖或重复核证"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    delivery = load(BASE / "final/delivery-proof.json")
    report = (ROOT / "DocuN/results/TASK-106-result.md").read_bytes()
    assert len(report) == delivery["bytes"] and sha(report) == delivery["sha256"]
    baseline = load(BASE / "orchestration-setup-20261008/baseline-input.json")["current_files"]
    declared = load(BASE / "final/baseline-post-and-build-identity.json")
    post = load(BASE / "final/post-source.json")
    current = dict(baseline)
    checks = []
    for row in declared["authorized_changes"]:
        assert baseline[row["path"]] == row["before"]
        if row["after"] is None:
            assert not (ROOT / row["path"]).exists()
            current.pop(row["path"])
        else:
            current[row["path"]] = row["after"]
    for rel, expected in post.items():
        assert sha((ROOT / rel).read_bytes()) == expected
        assert sha((BASE / "final/post" / rel).read_bytes()) == expected
        current[rel] = expected
    for rel, expected in current.items():
        actual = sha((ROOT / rel).read_bytes())
        checks.append({"path": rel, "expected": expected, "actual": actual, "match": actual == expected})
    assert all(row["match"] for row in checks)
    for row in declared["protected"]:
        assert row["before"] == row["after"] == sha((ROOT / row["path"]).read_bytes())
    for row in declared["locked_rules"]:
        assert row["before"] == row["after"] == sha(Path(row["path"]).read_bytes())
    for row in declared["new_production"]:
        assert sha((ROOT / row["path"]).read_bytes()) == row["sha256"]
    for rel, expected in declared["final_build"]["dist"].items():
        assert sha((ROOT / rel).read_bytes()) == expected
    save("identity-checks.json", checks)
    save("current-baseline.json", current)
    (OUT / "TASK-106-as-returned.md").write_bytes(report)
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
                "DocuN/tasks/TASK-106.md", "DocuN/results/TASK-106-work-decision.md"]:
        data = (ROOT / rel).read_bytes()
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        p.write_bytes(data)
        before.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
    save("before-manifest.json", before)
    runs = load(BASE / "final/run-index.json")
    for row in runs["runs"]:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    semantic = load(BASE / "final/semantic-oracle.json")
    assert semantic["T"]["supports"] is False and semantic["H"]["supports_both_dates"] is False
    evidence = []
    for rel in ["final/run-index.json", "final/matrix.json", "final/remainder-work.json", "final/semantic-oracle.json",
                "final/session-close.json", "final/resource-stop-proof.json", "final/baseline-post-and-build-identity.json",
                "final/delivery-proof.json", "implementation-map.json", "session.json"]:
        p = BASE / rel
        data = p.read_bytes()
        evidence.append({"path": str(p), "bytes": len(data), "sha256": sha(data)})
    save("returned-evidence-identities.json", evidence)
    stopped = load(BASE / "final/resource-stop-proof.json")
    live_resources = []
    for old in stopped["containers"]:
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
               "restart": hc["RestartPolicy"]["Name"], "ports": hc["PortBindings"],
               "database": old["database"], "port": old["port"]}
        assert row["cid"] == old["cid"] and row["image"] == old["image"] and row["name"] == old["name"]
        assert not row["running"] and row["pid"] == 0
        assert row["labels"] == old["labels"] and row["labels"]["retrolume.task"] == "TASK-106"
        assert hc["Memory"] == 536870912 and hc["NanoCpus"] == 1000000000 and hc["PidsLimit"] == 128 and not hc["Privileged"]
        assert len(row["mounts"]) == 1 and row["mounts"][0]["Type"] == "volume" and row["mounts"][0]["Name"] == old["volume"]
        assert row["restart"] == "no" and all(v["HostIp"] == "127.0.0.1" for vs in row["ports"].values() for v in vs)
        live_resources.append(row)
    cmd = "$p=@(18106,18107,55446,55447,55448); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $p} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    p = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, timeout=15, check=False)
    assert p.returncode == 0
    listeners = json.loads(p.stdout) if p.stdout.strip() else []
    save("resource-readonly.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "containers": live_resources,
         "listeners": listeners, "new_starts_SQL_or_tests": 0})
    close = load(BASE / "final/session-close.json")
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-106", "R": "R-100",
         "dispatch": "实际部分返回", "report_bytes": len(report), "report_sha256": sha(report),
         "acceptance": "接受已保存实现候选、有限有效子证据与停止；完整G10未通过，未派107",
         "current_objects": len(current), "post_source_fixture_dist_subset": len(post),
         "protected_count": len(declared["protected"]), "new_production": len(declared["new_production"]),
         "run_records_checked": len(runs["runs"]), "semantic_T_H": "两个正向FAIL保留，位置通过不等语义支持",
         "remaining_core": ["正确支持片段正向oracle", "历史答案修订UI/递归后继", "同活动view/key/hash恢复守卫", "caller取消后诊断收尾准确组合"],
         "counts": close["counts"], "seconds": close["seconds"], "active_checkpoint": close["active_elapsed"],
         "accounting_limit": "active为05:19:52封装检查点，05:22:10更晚交付的新增用时未逐项精准；旧未知不返额",
         "old_permit_ended": True, "all_owned_stopped": True, "no_listeners": not listeners,
         "root_business_runs": 0, "root_product_writes": 0,
         "next": "同106/R100续作01完整剩余及定向验证，新独立许可，原窗口/原CID/有效证据保留"})
    print(json.dumps({"current_objects": len(current), "post_subset": len(post), "protected": len(declared["protected"]),
        "report_bytes": len(report), "report_sha256": sha(report), "records": len(runs["runs"]),
        "stopped": True, "no_listeners": not listeners, "product_runs": 0}))


if __name__ == "__main__":
    main()
