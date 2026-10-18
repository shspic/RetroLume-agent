"""采用后的只读资源与基线预检，不创建或启动产品资源。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-108/orchestration-adoption-20261009"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    p = OUT / name
    assert not p.exists(), "不覆盖已有预检"
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def docker(args):
    process = subprocess.run(["docker.exe", *args], capture_output=True, timeout=15)
    assert process.returncode == 0, "只读Docker预检失败；不输出完整stderr/Env，不启动daemon"
    return process.stdout


def main():
    baseline = load(ROOT / "DocuN/evidence/TASK-108/orchestration-receipt-01/current-baseline.json")
    for rel, expected in baseline.items():
        assert sha((ROOT / rel).read_bytes()) == expected, rel
    proposal = ROOT / "DocuN/evidence/TASK-108/orchestration-receipt-01/adoption-proposal.json"
    work = ROOT / "DocuN/results/TASK-108-work-decision.md"
    report = ROOT / "DocuN/results/TASK-108-result.md"
    assert sha(work.read_bytes()) == "0903a5ffd6fb36a8dc66137c3c6442b4302adef64dc184d8838ee877b769b207"
    assert sha(report.read_bytes()) == "91d004bfde204c83b8f8387d8df2489e72889ef4d53935a63b80ad46693e4710"
    images = []
    for image_id in ["sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac",
                     "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"]:
        obj = json.loads(docker(["image", "inspect", image_id]))[0]
        assert obj["Id"] == image_id and obj["Os"] == "linux" and obj["Architecture"] == "amd64"
        images.append({"id": obj["Id"], "os": obj["Os"], "architecture": obj["Architecture"],
                       "created": obj["Created"], "default_user": obj.get("Config", {}).get("User"),
                       "cached": True, "executed": False})
    preview_names = [f"retrolume-task-109-g11-preview-{n:02d}" for n in range(1, 17)]
    owned_names = ["retrolume-task-109-g11-pg1", *preview_names]
    names = docker(["container", "ls", "-a", "--format", "{{.Names}}", "--filter", "name=retrolume-task-109-g11-"]).decode("utf-8").splitlines()
    assert not any(name in owned_names for name in names), "新资源名称已有对象，须查明，不覆盖或接管"
    volume_names = docker(["volume", "ls", "--format", "{{.Name}}", "--filter", "name=retrolume-task-109-g11-pg1-data"]).decode("utf-8").splitlines()
    assert "retrolume-task-109-g11-pg1-data" not in volume_names
    cmd = "$ports=@(18109,55449); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $ports} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, timeout=15)
    assert proc.returncode == 0
    listeners = json.loads(proc.stdout) if proc.stdout.strip() else []
    assert not listeners, "新端口被占用，不重启或杀别的服务"
    package_root = ROOT / "frontend/node_modules/playwright-core"
    package = load(package_root / "package.json")
    assert package["version"] == "1.62.1"
    package_files = {str(p.relative_to(package_root)).replace("\\", "/"): sha(p.read_bytes())
                     for p in sorted(package_root.rglob("*")) if p.is_file()}
    assert package_files and (ROOT / "backend/.venv/Scripts/python.exe").exists()
    assert (ROOT / "frontend/node_modules/vite/bin/vite.js").exists()
    assert (Path(r"C:\Users\28432\AppData\Local\ms-playwright") / "chromium-1234").exists()
    for rel in ["backend/app/preview", "frontend/src/explanations", "backend/migrations/012_html_explanations.sql", "DocuN/tasks/TASK-109.md"]:
        assert not (ROOT / rel).exists(), rel
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    save("baseline-input.json", {"at": now, "current_files": baseline, "objects": len(baseline),
          "approved_proposal_before": {"path": str(proposal), "sha256": sha(proposal.read_bytes())},
          "work_decision_before": {"path": str(work), "sha256": sha(work.read_bytes())},
          "source_contract": {"path": str(report), "sha256": sha(report.read_bytes()), "bytes": len(report.read_bytes())},
          "new_paths_absent": True, "source_or_runtime_changes": 0})
    save("resource-preflight.json", {"at": now, "images": images, "container_names_reserved": owned_names,
          "volume": "retrolume-task-109-g11-pg1-data", "existing_target_collisions": [], "listeners": listeners,
          "API": "127.0.0.1:18109", "PG": "127.0.0.1:55449", "no_env_saved": True,
          "created_started_SQL_or_product_tests": 0, "runtime_privacy_checks_still_required": True})
    save("playwright-local-files.json", {"path": str(package_root), "version": "1.62.1", "files": package_files,
          "count": len(package_files), "dependency_copied_installed_or_executed": False})
    print(json.dumps({"current_objects": len(baseline), "cached_images": len(images), "new_names_clear": True,
          "new_ports_clear": True, "local_package_files": len(package_files), "product_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
