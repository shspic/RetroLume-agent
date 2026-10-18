"""核证续作01的文件身份、历史、账目和停止资源；不运行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-106"
C01 = BASE / "continuation-01"
OUT = BASE / "orchestration-receipt-02"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(name, value):
    path = OUT / name
    assert not path.exists(), "不覆盖已保存的回收证据"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    report_path = ROOT / "DocuN/results/TASK-106-result.md"
    report = report_path.read_bytes()
    delivery = load(C01 / "final/delivery-proof.json")
    old_report = (BASE / "orchestration-receipt-01/TASK-106-as-returned.md").read_bytes()
    assert len(report) == delivery["bytes"] == 33407
    assert sha(report) == delivery["sha256"]
    assert report.endswith(old_report) and len(old_report) == 21949
    assert sha(old_report) == delivery["old_suffix_sha256"]
    baseline = load(BASE / "orchestration-receipt-01/current-baseline.json")
    declaration = load(C01 / "final/baseline-diff-build.json")
    post = load(C01 / "final/post-source.json")
    assert len(baseline) == declaration["baseline"] == 346
    assert len(post) == 363
    changes = declaration["changed"]
    unchanged = declaration["unchanged"]
    assert len(changes) == 7 and len(unchanged) == 339
    for row in changes:
        rel = row["path"]
        assert baseline[rel] == row["before"]
        assert sha((C01 / "pre" / rel).read_bytes()) == row["before"]
        if row["after"] is None:
            assert not (ROOT / rel).exists() and rel not in post
        else:
            assert post[rel] == row["after"]
    for row in unchanged:
        assert baseline[row["path"]] == row["before"] == row["after"] == post[row["path"]]
    checks = []
    for rel, expected in post.items():
        actual = sha((ROOT / rel).read_bytes())
        archived = sha((C01 / "final/post" / rel).read_bytes())
        assert actual == archived == expected, rel
        checks.append({"path": rel, "sha256": actual, "snapshot_match": True})
    for row in declaration["rules"]:
        assert row["before"] == row["after"] == sha(Path(row["path"]).read_bytes())
    assert not declaration["protected_drift"]
    for rel, expected in declaration["build"]["dist"].items():
        assert sha((ROOT / rel).read_bytes()) == expected
    identities = []
    files = [C01 / "final" / n for n in [
        "delivery-proof.json", "old-result-byte-preservation.json", "baseline-diff-build.json",
        "post-source.json", "matrix.json", "remainder-work.json", "run-index.json",
        "session-close.json", "resource-stop-proof.json"]]
    run_index = load(C01 / "final/run-index.json")
    for row in run_index["runs"]:
        raw = Path(row["path"])
        fact = load(raw)
        assert fact["name"] == row["name"] and fact["status"] == row["status"]
        files.append(raw)
        files.extend(p for p in raw.parent.glob("*.json") if p != raw)
    for path in sorted(set(files)):
        data = path.read_bytes()
        identities.append({"path": str(path), "bytes": len(data), "sha256": sha(data)})
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
                "DocuN/results/TASK-106-work-decision.md", "DocuN/tasks/TASK-106.md"]:
        data = (ROOT / rel).read_bytes()
        dest = OUT / "before" / rel
        assert not dest.exists()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        before.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
    stopped = load(C01 / "final/resource-stop-proof.json")
    resources = []
    for old in stopped["containers"]:
        process = subprocess.run(["docker.exe", "inspect", "--type", "container", old["cid"]],
                                 capture_output=True, timeout=15, check=False)
        assert process.returncode == 0, "精确CID只读核失败；不输出原始Env"
        raw = json.loads(process.stdout)[0]
        hc = raw["HostConfig"]
        labels = raw["Config"].get("Labels", {})
        mounts = [{k: m.get(k) for k in ("Type", "Name", "Destination", "RW")} for m in raw["Mounts"]]
        row = {"cid": raw["Id"], "name": raw["Name"].lstrip("/"), "image": raw["Image"],
               "running": raw["State"]["Running"], "pid": raw["State"]["Pid"],
               "labels": {k: labels.get(k) for k in ("retrolume.task", "retrolume.permit", "retrolume.synthetic")},
               "mounts": mounts, "limits": {k: hc.get(k) for k in ("NanoCpus", "Memory", "PidsLimit", "Privileged")},
               "restart": hc["RestartPolicy"]["Name"], "ports": hc["PortBindings"]}
        assert row["cid"] == old["cid"] and row["name"] == old["name"].lstrip("/") and row["image"] == old["image"]
        assert not row["running"] and row["pid"] == 0
        assert row["labels"] == old["labels"] and row["labels"]["retrolume.task"] == "TASK-106"
        assert hc["Memory"] == 536870912 and hc["NanoCpus"] == 1000000000 and hc["PidsLimit"] == 128
        assert not hc["Privileged"] and row["restart"] == "no"
        assert len(mounts) == 1 and mounts[0]["Type"] == "volume"
        assert mounts[0]["Name"] == row["name"] + "-data"
        assert all(v["HostIp"] == "127.0.0.1" for vs in row["ports"].values() for v in vs)
        resources.append(row)
    cmd = "$ports=@(18106,18107,55446,55447,55448); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $ports} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    process = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, timeout=15, check=False)
    assert process.returncode == 0
    listeners = json.loads(process.stdout) if process.stdout.strip() else []
    assert not listeners, "有在途监听；停止派新验证"
    close = load(C01 / "final/session-close.json")
    remainder = load(C01 / "final/remainder-work.json")
    assert close["counts"]["listener_start"] == close["count_limits"]["listener_start"] == 6
    assert len(remainder["not_run"]) == 3
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    write("identity-checks.json", checks)
    write("current-baseline.json", post)
    write("evidence-identities.json", identities)
    write("before-manifest.json", before)
    write("resource-readonly.json", {"at": now, "containers": resources, "listeners": listeners,
          "starts_SQL_product_tests": 0, "raw_Env_saved": False})
    saved_report = OUT / "TASK-106-C01-as-returned.md"
    assert not saved_report.exists()
    saved_report.write_bytes(report)
    write("receipt.json", {"at": now, "TASK": "TASK-106", "R": "R-100", "round": "续作01",
          "report_bytes": len(report), "report_sha256": sha(report), "old_history_bytes": len(old_report),
          "old_history_exact": True, "current_objects": len(post), "changed_original_objects": len(changes),
          "unchanged_original_objects": len(unchanged), "new_effective_entries": len(post) - len(unchanged) - 6,
          "source_changed": [r["path"] for r in changes if r["path"].startswith(("backend/app/", "frontend/src/"))],
          "raw_run_records": len(run_index["runs"]), "evidence_objects_hashed": len(identities),
          "counts": close["counts"], "limits": close["count_limits"], "seconds": close["seconds"],
          "active_checkpoint": close["active_elapsed"], "delivery_active_elapsed": close.get("delivery_active_elapsed"),
          "delivery_utc": close.get("delivery_utc"), "old_real_roots_45_plus_16_plus_6": 67,
          "acceptance": "普通接受保存的源码修复候选、可核原件和停止；不关闭DEF、不签完整G10",
          "remaining_browser_methods": remainder["not_run"], "permit_ended": True,
          "remaining_nominal_counters_do_not_authorize_execution": True,
          "all_owned_containers_stopped": True, "relevant_ports_free": True,
          "next": "TASK-107/R-101集中独立终审与剩余浏览器取证；原106停止，不再分派相同C02",
          "main_product_writes_tests_build_SQL_starts": 0})
    print(json.dumps({"report_bytes": len(report), "current_objects": len(post), "unchanged": len(unchanged),
          "source_delta": 5, "records": len(run_index["runs"]), "raw_evidence_hashed": len(identities),
          "old_suffix_exact": True, "stopped": True, "ports_free": True,
          "delivery_active_elapsed": close.get("delivery_active_elapsed"), "product_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
