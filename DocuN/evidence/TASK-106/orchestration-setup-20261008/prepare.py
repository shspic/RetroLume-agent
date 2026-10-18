"""只读核实施起点与资源，不创建容器、运行产品或代做工程。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-106/orchestration-setup-20261008"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "不覆盖既有准备与授权登记"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    package = load(ROOT / "DocuN/evidence/TASK-105/orchestration-receipt-20261008/adoption-package.json")
    report = ROOT / "DocuN/results/TASK-105-result.md"
    decision = ROOT / "DocuN/results/TASK-105-work-decision.md"
    assert sha(report.read_bytes()) == package["source_contract_sha256"]
    assert sha(decision.read_bytes()) == package["work_decision_sha256"]
    current = load(ROOT / "DocuN/evidence/TASK-105/orchestration-receipt-20261008/current-baseline.json")
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    assert len(current) == 308
    assert not (ROOT / "DocuN/tasks/TASK-106.md").exists()
    assert not (ROOT / "backend/migrations/011_text_interview.sql").exists()
    rules = load(ROOT / "DocuN/evidence/TASK-105/orchestration-setup-20261007/design-input.json")["rules_contracts"]
    for row in rules:
        assert sha(Path(row["path"]).read_bytes()) == row["sha256"]
    save("baseline-input.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "current_objects": 308, "current_files": current, "rules_contracts": rules,
        "contract": {"path": str(report), "sha256": sha(report.read_bytes()), "bytes": report.stat().st_size},
        "work_decision_before_adoption": {"path": str(decision), "sha256": sha(decision.read_bytes()), "bytes": decision.stat().st_size},
        "G10_source_not_implemented": True, "runtime_starts": 0})
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/results/TASK-105-work-decision.md"]:
        data = (ROOT / rel).read_bytes()
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        p.write_bytes(data)
        before.append({"path": rel, "sha256": sha(data), "bytes": len(data)})
    save("before-manifest.json", before)
    result = subprocess.run(["docker.exe", "image", "inspect", IMAGE], capture_output=True, timeout=15, check=False)
    image = {"expected_id": IMAGE, "available": False, "exit_code": result.returncode}
    if result.returncode == 0:
        raw = json.loads(result.stdout)[0]
        image.update(id=raw["Id"], tags=raw.get("RepoTags"), os=raw.get("Os"), architecture=raw.get("Architecture"))
        image["available"] = raw["Id"] == IMAGE
    names_result = subprocess.run(["docker.exe", "container", "ls", "--all", "--filter", "name=retrolume-task-106-g10", "--format", "{{.Names}}"],
                                  capture_output=True, timeout=15, check=False)
    volume_result = subprocess.run(["docker.exe", "volume", "ls", "--filter", "name=retrolume-task-106-g10", "--format", "{{.Name}}"],
                                   capture_output=True, timeout=15, check=False)
    names = names_result.stdout.decode("utf-8", "replace").splitlines()
    volumes = volume_result.stdout.decode("utf-8", "replace").splitlines()
    port_cmd = "$p=@(18106,18107,55446,55447,55448); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $p} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    pr = subprocess.run(["powershell.exe", "-NoProfile", "-Command", port_cmd], capture_output=True, timeout=15, check=False)
    listeners = json.loads(pr.stdout) if pr.stdout.strip() else []
    save("resource-preflight.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "image": image,
        "matching_existing_container_names": names, "container_query_exit": names_result.returncode,
        "matching_existing_volume_names": volumes, "volume_query_exit": volume_result.returncode,
        "listeners": listeners, "ports_query_exit": pr.returncode, "ports": [18106, 18107, 55446, 55447, 55448],
        "python": (ROOT / "backend/.venv/Scripts/python.exe").is_file(),
        "vite": (ROOT / "frontend/node_modules/.bin/vite.cmd").is_file(),
        "playwright": (ROOT / "frontend/node_modules/playwright/package.json").is_file(),
        "read_only": True, "created_volumes_containers_or_started": 0,
        "runtime_gate": "执行前重核完整JSON/CID/标签/实际Mounts/loopback/配额；当前metadata不是未来运行通过"})
    assert image["available"] and names_result.returncode == volume_result.returncode == pr.returncode == 0
    assert not names and not volumes and not listeners
    save("adoption-received.json", {"registered_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "user_message": "批准", "user_local_date": "2026-10-08", "exact_user_message_time": "未提供，不回填",
        "object": "上条具体G10-P合成实现与定向验证采用请求", "status": "approved",
        "source_contract_sha256": package["source_contract_sha256"], "work_decision_before_sha256": package["work_decision_sha256"],
        "scope": "按105原A-D和已审普通读界限；新主要持久/公开/profile包采用，运行对象/预算由106卡明确",
        "excludes": package["excludes"], "actual_implementation_started": False})
    print(json.dumps({"G10_P": "user_approved", "baseline": 308, "image_available": image["available"],
        "new_names_clear": not names and not volumes, "ports_clear": not listeners, "runtime_starts": 0}))


if __name__ == "__main__":
    main()
