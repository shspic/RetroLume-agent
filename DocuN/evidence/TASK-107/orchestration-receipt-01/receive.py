"""普通核证107独立原件、当前文件及停止资源；不重跑产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-107"
OUT = BASE / "orchestration-receipt-01"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(name, value):
    target = OUT / name
    assert not target.exists(), "不重复核证或覆盖已保存结果"
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pointers(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("path"), str) and isinstance(obj.get("sha256"), str) and len(obj["sha256"]) == 64:
            path = Path(obj["path"])
            if path.is_absolute():
                yield path, obj["sha256"]
        for value in obj.values():
            yield from pointers(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from pointers(value)


def main():
    delivery = load(BASE / "audit/delivery-check.json")
    report_path = ROOT / "DocuN/results/TASK-107-result.md"
    report = report_path.read_bytes()
    assert len(report) == delivery["result"]["bytes"] == 17418
    assert sha(report) == delivery["result"]["sha256"]
    assert not delivery["missing_links"]
    source = load(BASE / "orchestration-setup-20261008/audit-input.json")["current_files"]
    assert len(source) == 363
    identity = load(BASE / "audit/final-identity-check.json")
    assert identity["current_objects"] == 363 and identity["all_match"]
    checks = []
    for row in identity["checks"]:
        path = Path(row["path"])
        actual = sha(path.read_bytes())
        assert actual == row["sha256"], row["path"]
        if row.get("expected") is not None:
            assert actual == row["expected"]
        checks.append({"path": str(path), "sha256": actual})
    for rel, expected in source.items():
        assert sha((ROOT / rel).read_bytes()) == expected, rel
    accounting = load(BASE / "audit/final-accounting.json")
    assert sha((BASE / "session.json").read_bytes()) == accounting["final_session_sha256"]
    assert accounting["prior_roots"] == 67 and accounting["total_roots"] == 70
    for row in accounting["methods"]:
        assert row["status"] == "PASS"
    assert accounting["counts"]["root"] == 3 and accounting["counts"]["SUP_attempt"] == 5
    raw_runs = []
    for name in ["R01-final-browser-one-session", "R02-final-browser-one-session", "R03-final-browser-one-session"]:
        path = BASE / "runs" / name / "result.json"
        obj = load(path)
        assert obj["status"] == "FAIL", "保留原根失败，不改写为成功"
        if name.startswith("R03"):
            assert obj["browser"]["status"] == "PASS"
            assert len(obj["browser"]["cases"]) == 5
            assert all(row["status"] == "PASS" for row in obj["browser"]["cases"])
        raw_runs.append({"path": str(path), "sha256": sha(path.read_bytes()), "root_status": "FAIL"})
    b1 = load(BASE / "audit/B1-history-and-native-v2-independent.json")
    assert b1["highest_answer_version"] == 2 and b1["supersedes_exact"]
    assert b1["original_answer_still_readable"] and b1["old_successor_commands_obsolete"]
    assert b1["only_new_v2_answer_in_frozen"] and b1["old_and_new_body_hash_valid"] and b1["final_feedback_body_hash_valid"]
    b2 = load(BASE / "audit/B2-original-key-commit-loss-independent.json")
    assert b2["accepted_unclaimed"] and b2["one_domain_effect"] and b2["one_native_and_transport_delta"] == [1, 1]
    assert b2["confirmed_original_key"] and b2["dropped_real_COMMIT_not_fake_receipt"]
    b3 = load(BASE / "audit/B3-three-window-independent.json")
    assert len(b3["windows"]) == 3 and b3["no_react_or_server_qualification_substitution"]
    for window in b3["windows"]:
        assert window["old_key_POST_after_held_capture"] == 0 and window["native_count_unchanged"]
        assert window["full_new_view_preserved"] and window["old_and_new_all_IDB_drafts_preserved"]
    native = load(BASE / "audit/five-native-and-raw-transport-chain.json")
    assert len(native["native_sessions"]) == 5 and native["all_request_hashes_match"] and native["all_native_trees_zero_at_end"]
    assert all(row["detail"]["active_processes_at_end"] == 0 and not row["detail"]["cleanup_incomplete"]
               for row in native["native_sessions"])
    matrix = load(BASE / "audit/V01-V24-independent-applicability.json")
    assert len(matrix["entries"]) == 24
    documents = list((BASE / "audit").glob("*.json")) + [BASE / "cleanup-supplement-01.json", BASE / "cleanup-supplement-03.json"]
    bound = {}
    for path in documents:
        obj = load(path)
        for target, expected in pointers(obj):
            actual = sha(target.read_bytes())
            assert actual == expected, str(target)
            assert str(target) not in bound or bound[str(target)] == expected
            bound[str(target)] = expected
    resource_old = load(BASE / "cleanup-supplement-03.json")
    assert resource_old["all_original_owned_births_stopped"]
    live = []
    for row in resource_old["containers"]:
        proc = subprocess.run(["docker.exe", "inspect", "--type", "container", row["cid"]], capture_output=True, timeout=15)
        assert proc.returncode == 0, "只读精确CID核证失败，原始Env不输出"
        data = json.loads(proc.stdout)[0]
        host = data["HostConfig"]
        mounts = [{key: m.get(key) for key in ["Type", "Name", "Destination", "RW"]} for m in data["Mounts"]]
        item = {"cid": data["Id"], "name": data["Name"].lstrip("/"), "image": data["Image"],
                "running": data["State"]["Running"], "pid": data["State"]["Pid"],
                "labels": {key: data["Config"].get("Labels", {}).get(key) for key in ["retrolume.task", "retrolume.permit", "retrolume.synthetic"]},
                "mounts": mounts, "limits": {key: host.get(key) for key in ["NanoCpus", "Memory", "PidsLimit", "Privileged"]},
                "restart": host["RestartPolicy"]["Name"], "ports": host["PortBindings"]}
        assert item["cid"] == row["cid"] and item["image"] == row["image"]
        assert item["name"] == row["name"].lstrip("/") and not item["running"] and item["pid"] == 0
        assert item["labels"] == row["labels"]
        assert len(mounts) == 1 and mounts[0]["Type"] == "volume" and mounts[0]["Name"] == item["name"] + "-data"
        assert host["NanoCpus"] == 1000000000 and host["Memory"] == 536870912 and host["PidsLimit"] == 128
        assert not host["Privileged"] and item["restart"] == "no"
        assert all(p["HostIp"] == "127.0.0.1" for values in item["ports"].values() for p in values)
        live.append(item)
    command = "$ports=@(18106,18107,55446,55447,55448); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $ports} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, timeout=15)
    assert proc.returncode == 0
    listeners = json.loads(proc.stdout) if proc.stdout.strip() else []
    assert not listeners, "有在途服务，不登记已完整停止"
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD",
                "DocuN/results/TASK-106-work-decision.md", "DocuN/results/TASK-107-work-decision.md"]:
        raw = (ROOT / rel).read_bytes()
        copy = OUT / "before" / rel
        assert not copy.exists()
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(raw)
        before.append({"path": rel, "bytes": len(raw), "sha256": sha(raw)})
    saved = OUT / "TASK-107-as-returned.md"
    assert not saved.exists()
    saved.write_bytes(report)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    write("identity-checks.json", checks)
    write("current-baseline.json", source)
    write("bound-originals.json", [{"path": p, "sha256": s} for p, s in sorted(bound.items())])
    write("before-manifest.json", before)
    write("resource-readonly.json", {"at": now, "containers": live, "listeners": listeners, "new_starts_SQL_tests": 0})
    write("observations-retained.json", [
        {"id": "O107-01", "grade": "P2/B级，非阻断观察", "condition": "公开bind_scope无序多源输入与权威来源排序不一致可能导致后续冻结比较拒绝；现UI已排序",
         "dynamic_permutation_test": "未运行", "decision": "保留待后续相关维护；不阻塞已批准UI有限切片，不冒全部API排列通过"},
        {"id": "O107-02", "grade": "P2/B级，非阻断观察", "condition": "submit/moreHistory错误catch只核panel，可能在同activity新view显示旧错误",
         "decision": "保留显示层观察；发送/notice/详情/草稿守卫按独立证据有限验收，不宣全部迟到错误投影通过"}])
    write("receipt.json", {"at": now, "TASK": "TASK-107", "R": "R-101", "report_bytes": len(report), "report_sha256": sha(report),
          "actual_return": True, "source_objects": len(source), "final_identity_objects": len(checks), "bound_raw_originals": len(bound),
          "three_axes": "独立代码、关键证据、控制均有限通过；编排按原件采用",
          "remaining_UI": "B1、B2、B3三个实际窗口共五方法成立", "root_statuses": raw_runs,
          "original_FAILs_not_rewritten": True, "native_trees_zero": True, "fresh_resources_stopped": True,
          "all_relevant_ports_free": True, "old70_roots_not_success_count": True,
          "accounting": accounting, "observations": ["O107-01", "O107-02"],
          "acceptance": "关闭TASK106/R100、TASK107/R101与批准G10有限切片，DEF024/025/026和E106-SEM有限关闭",
          "not_claimed": ["真实provider质量", "全部API排列", "完整Must/M-1", "项目或发布通过"],
          "permits_ended": True, "next": "STEP015/016交互HTML完整合同；B-01保持开放，不重跑旧实验",
          "main_product_writes_SQL_tests_build_starts": 0})
    print(json.dumps({"report_bytes": len(report), "source_objects": len(source), "identity_objects": len(checks),
          "bound_raw_originals": len(bound), "methods": 5, "root_statuses": "三个FAIL原样保留", "stopped": True,
          "next": "TASK108/R102只读完整HTML合同", "product_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
