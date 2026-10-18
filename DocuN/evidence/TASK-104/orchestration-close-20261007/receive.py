"""核证独立增量的原件身份与历史，供编排有限验收，不执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-104/review-02"
OUT = ROOT / "DocuN/evidence/TASK-104/orchestration-close-20261007"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "保留已有关闭核证，不重复覆盖"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    delivery = load(BASE / "delivery-check.json")
    report = (ROOT / "DocuN/results/TASK-104-result.md").read_bytes()
    assert len(report) == delivery["report"]["bytes"] and sha(report) == delivery["report"]["sha256"]
    offset = delivery["prefix_bytes"]
    assert sha(report[:offset]) == delivery["prefix_sha256"]
    assert len(report[offset:]) == delivery["historical_suffix_bytes"] == 21896
    assert sha(report[offset:]) == delivery["historical_suffix_sha256"]
    assert report[offset:] == (ROOT / "DocuN/evidence/TASK-104/orchestration-receipt-01/TASK-104-as-returned.md").read_bytes()
    current = load(ROOT / "DocuN/evidence/TASK-103/orchestration-repair-03-receipt/current-baseline.json")
    assert len(current) == 308
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    identity = load(BASE / "final-identity-check.json")
    for row in identity["checks"]:
        assert sha(Path(row["path"]).read_bytes()) == row["expected_sha256"]
    pointers = identity["raw_pointer_checks"]
    for row in pointers:
        assert sha(Path(row["path"]).read_bytes()) == row.get("expected_sha256", row.get("sha256"))
    save("current-baseline.json", current)
    save("identity-checks.json", {"current": 308, "checks": identity["checks"], "raw_pointers": pointers, "all_match": True})
    (OUT / "TASK-104-as-returned.md").write_bytes(report)
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
                "DocuN/results/TASK-103-work-decision.md", "DocuN/results/TASK-104-work-decision.md"]:
        data = (ROOT / rel).read_bytes()
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        p.write_bytes(data)
        before.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
    save("before-manifest.json", before)
    p1 = load(BASE / "F01-exact-window-binding.json")
    assert p1["strict_order"] and p1["full_B_identity_and_body_same"] and p1["clean_B_has_no_draft"]
    assert p1["old_A_detail_GET_increment"] == 0
    for key in ["post_controller", "list_controller"]:
        row = p1[key]
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    e1 = load(BASE / "E01-late-citation-layered-binding.json")
    assert e1["status"] == 200 and e1["new_panel_loaded_before_delivery_attempt"]
    assert e1["route_fulfill_returned"] and e1["citation_phase_POST_count"] == 0
    assert not e1["old_full_quote_present_in_new_DOM"] and e1["citation_text_sha_matches_original"]
    assert not e1["dedicated_PG_snapshots_during_citation_phase"]
    accounting = load(BASE / "session-accounting.json")
    assert accounting["new_real_tests_product_fixture_compile_build_PG_SQL_HTTP_browser_resources_model_POST_password_DDL"] == 0
    evidence = []
    for rel in ["delivery-check.json", "final-identity-check.json", "source-prelog.md", "pre-current-source-chain.json",
                "F01-exact-window-binding.json", "E01-late-citation-layered-binding.json",
                "actual-and-inherited-case-binding.json", "all-nine-run-and-loaded-bundle-binding.json",
                "eight-POST-and-persistent-effect-binding.json", "execution-control-independent-binding.json",
                "session-accounting.json", "audit-mistakes.json"]:
        p = BASE / rel
        data = p.read_bytes()
        evidence.append({"path": str(p), "sha256": sha(data), "bytes": len(data)})
    save("accepted-evidence-identities.json", evidence)
    resources = load(ROOT / "DocuN/evidence/TASK-103/orchestration-repair-03-receipt/resource-readonly.json")
    verified = []
    for old in resources["containers"]:
        r = subprocess.run(["docker.exe", "inspect", "--type", "container", old["cid"]], capture_output=True, timeout=15, check=False)
        assert r.returncode == 0
        o = json.loads(r.stdout)[0]
        hc = o["HostConfig"]
        labels = o["Config"].get("Labels", {})
        v = {"cid": o["Id"], "name": o["Name"].lstrip("/"), "image": o["Image"],
             "running": o["State"]["Running"], "pid": o["State"]["Pid"], "exit_code": o["State"]["ExitCode"],
             "labels": {k: labels.get(k) for k in ("retrolume.task", "retrolume.permit", "retrolume.synthetic")},
             "mounts": [{k: m.get(k) for k in ("Type", "Name", "Destination", "RW")} for m in o["Mounts"]],
             "limits": {k: hc.get(k) for k in ("NanoCpus", "Memory", "PidsLimit", "Privileged")},
             "restart": hc["RestartPolicy"]["Name"], "ports": hc["PortBindings"]}
        assert all(v[k] == old[k] for k in ["cid", "name", "image", "labels", "mounts", "limits", "restart", "ports"])
        assert not v["running"] and v["pid"] == 0
        verified.append(v)
    cmd = "$p=@(18103,18104,55443,55444,55445); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $p} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, timeout=15, check=False)
    assert r.returncode == 0
    listeners = json.loads(r.stdout) if r.stdout.strip() else []
    save("resource-readonly.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "containers": verified,
         "listeners": listeners, "starts_SQL_or_tests": 0})
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-104", "R": "R-098",
         "round": "review-02", "report_bytes": len(report), "report_sha256": sha(report), "old_history_21896_exact": True,
         "current_objects": 308, "rule_contracts": identity["rules_contracts"], "raw_pointer_count": len(pointers),
         "independent_three_axes": "本次有限增量通过，原首轮未变范围有效继承，F01/E01证据闭合",
         "F01": "准确回执已确认后列表GET等待期间载入干净B，旧返回不抢回；当前源码/实际新bundle/真实effect链对应",
         "E01": "真实服务GET200、卸载Abort、新活动加载后尝试晚交付不复活；不声称客户端曾解析旧正文或有专属PG快照",
         "accepted_boundaries": "单机有限G9；原批FAIL/no-op/未知/非阻断O01—03保留；不签全STEP/M-1/真实provider/发布/项目",
         "audit_active_seconds": accounting["active_used_seconds_at_delivery_check"],
         "audit_metadata_seconds": accounting["metadata_charged_seconds"], "official_pages": accounting["official_primary_pages_read"],
         "new_audit_execution": 0, "root_product_writes": 0, "root_business_runs": 0,
         "all_owned_stopped": True, "no_listeners": not listeners,
         "next": "编排有限验收关闭103/104/G9与DEF023/E01，按既有STEP014组织只读文字面试完整合同"})
    print(json.dumps({"current": 308, "raw_pointers": len(pointers), "report_bytes": len(report), "report_sha256": sha(report),
                      "all_owned_stopped": True, "no_listeners": not listeners, "product_runs": 0}))


if __name__ == "__main__":
    main()
