"""核证109准备失败、源码与无在途资源，普通回收不执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-109"
OUT = BASE / "orchestration-receipt-01"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    p = OUT / name
    assert not p.exists(), "不覆盖已有回收或重做已保存核证"
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def docker(args):
    p = subprocess.run(["docker.exe", *args], capture_output=True, timeout=15)
    assert p.returncode == 0, "只读Docker核证失败，不输出Env或启动daemon"
    return p.stdout.decode("utf-8", "replace")


def main():
    proof = load(BASE / "execution/delivery-proof.json")
    report = (ROOT / "DocuN/results/TASK-109-result.md").read_bytes()
    assert len(report) == proof["result"]["bytes"] == 15176
    assert sha(report) == proof["result"]["sha256"]
    protected = load(BASE / "orchestration-setup-20261009/input-baseline.json")["current_files"]
    assert len(protected) == 363
    for rel, expected in protected.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    final = load(BASE / "execution/final-source-manifest.json")
    assert len(final["files"]) == 128
    current = dict(protected)
    for row in final["files"]:
        p = Path(row["path"])
        assert sha(p.read_bytes()) == row["sha256"], str(p)
        current[str(p.relative_to(ROOT)).replace("\\", "/")] = row["sha256"]
    session = load(BASE / "execution/session.json")
    assert len(session["roots"]) == 2 and all(row["state"] == "FAIL" for row in session["roots"])
    assert len(session["image_builds"]) == 1 and not session["preview_creates"] and not session["preview_starts"]
    assert not session["controllers"] and session["pg_creates"] == session["sql"] == session["native_SUP"] == session["transport"] == 0
    assert session["global_real_root_count"] == 72 and not session["business_phase_entered"]
    raw = []
    for p in sorted((BASE / "execution").glob("*.json")):
        raw.append({"path": str(p), "bytes": len(p.read_bytes()), "sha256": sha(p.read_bytes())})
    for folder in ["root-01", "root-02"]:
        for p in sorted((BASE / "execution" / folder).glob("*.json")):
            raw.append({"path": str(p), "bytes": len(p.read_bytes()), "sha256": sha(p.read_bytes())})
        root = load(BASE / "execution" / folder / "root-result.json")
        assert root["state"] == "FAIL" and root["terminal"] is None
    stderr = BASE / "execution/root-02/build-stderr.log"
    log = stderr.read_text(encoding="utf-8-sig")
    assert "docker.io/library/sha256" in log and "auth.docker.io/token" in log
    raw.append({"path": str(stderr), "bytes": len(stderr.read_bytes()), "sha256": sha(stderr.read_bytes())})
    names = docker(["ps", "-a", "--filter", "name=retrolume-task-109-g11-", "--format", "{{.Names}} {{.ID}}"])
    assert not names.strip(), "发现本卡物理对象，先核真实在途，不另派运行"
    command = "$ports=@(18109,55449); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $ports} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    p = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, timeout=15)
    assert p.returncode == 0
    listeners = json.loads(p.stdout) if p.stdout.strip() else []
    assert not listeners
    status = json.loads(docker(["info", "--format", "{{json .DriverStatus}}"])); assert status == [["driver-type", "io.containerd.snapshotter.v1"]]
    builder = docker(["buildx", "inspect"])
    assert "Driver:        docker" in builder and "BuildKit version: v0.32.2" in builder
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/tasks/TASK-109.md", "DocuN/results/TASK-109-work-decision.md"]:
        data = (ROOT / rel).read_bytes()
        copy = OUT / "before" / rel
        copy.parent.mkdir(parents=True, exist_ok=True); assert not copy.exists(); copy.write_bytes(data)
        before.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
    saved = OUT / "TASK-109-as-returned.md"; assert not saved.exists(); saved.write_bytes(report)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    save("current-baseline.json", current)
    save("evidence-identities.json", raw)
    save("before-manifest.json", before)
    save("resource-readonly.json", {"at": now, "task_container_names": [], "listeners": listeners, "store": status,
         "builder_driver": "docker", "builder_version": "v0.32.2", "Docker_client_server": "29.7.2", "created_started_SQL": 0})
    save("technical-review.json", {"at": now,
         "observed": ["两根都发生在browser之前", "裸FROM被解析成registry仓库名", "正确repo digest源改好但未build", "host/counter没有生产NavigationGate，终态即使无反证也NOT_FULL_H0"],
         "next_method": "一次本地OCI layout命名上下文，精确缓存config与layer绑定，避免registry FROM解析；本机支持仍须实际一次验证",
         "primary_sources": [
             {"url": "https://docs.docker.com/reference/cli/docker/buildx/build/", "supports": "--build-context接受本地OCI layout，FROM名字使用指定上下文，可按manifest digest固定"},
             {"url": "https://docs.docker.com/reference/cli/docker/image/build/", "supports": "--network的范围是构建RUN；该页还描述legacy模式，但不将它当本机必然可用"},
             {"url": "https://docs.docker.com/engine/storage/containerd/", "supports": "实际driver-status识别containerd；不切换store，不重启daemon"}],
         "review_web_pages": 4, "actor_old_pages_used": 4, "not_reset_old_research_budget": True,
         "review_metadata_error": "buildx inspect没有--format，已用plain只读输出核；无build/create/启动效果",
         "not_proven": "新OCI构建Windows URI/上传支持、真实加载与浏览器安全仍not_run",
         "legacy_builder_or_store_switch_not_selected": True})
    save("receipt.json", {"at": now, "TASK": "TASK-109", "R": "R-103", "report_bytes": len(report), "report_sha256": sha(report),
         "protected": 363, "new_final_entries": 128, "current_scope": len(current), "session": session,
         "partial_acceptance": "接受准备源/明确失败与停止，不验收H0或完整G11",
         "builder_registry_attempt_not_zero_network_claim": True, "no_runtime_container_or_business_created": True,
         "old_global_roots": 72, "H0_old2_and_build1_remain_failed": True,
         "active_upper_bound": 2700.7, "metadata_upper_bound": 2700.7, "old_overlap_preserved": True,
         "next": "同109/R103续作01，只一离线构建与一真实最小证伪/精确收尾，全部业务继续冻结",
         "main_product_writes_build_test_SQL_starts": 0})
    print(json.dumps({"report": len(report), "protected": 363, "new": 128, "current": len(current), "roots_failed": 2,
        "task_containers": 0, "ports_free": True, "business_phase": False, "main_product_runs": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
