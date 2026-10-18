"""核证C01成功构建与误判退出，复用镜像；不启动或执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-109"
C01 = BASE / "execution/continuation-01"
OUT = BASE / "orchestration-receipt-02"
IMAGE = "sha256:aa824fa25eb0aae09cee50c10372fb218a7d86ffb10124b46074a5c1e977cc66"
CONFIG = "sha256:e881d12c9e682de7e535386b9db353bfc95838c3bcea04332bcdffd9cc30e6ea"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save(name, value):
    p = OUT / name
    assert not p.exists(), "不覆盖已有回收"
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def docker(args):
    p = subprocess.run(["docker.exe", *args], capture_output=True, timeout=15)
    assert p.returncode == 0, "只读核证失败，不输出完整Env"
    return p.stdout


def main():
    proof = load(C01 / "delivery-proof.json")
    report = (ROOT / "DocuN/results/TASK-109-result.md").read_bytes()
    old_report = (BASE / "orchestration-receipt-01/TASK-109-as-returned.md").read_bytes()
    assert len(report) == proof["result"]["bytes"] == 27219
    assert sha(report) == proof["result"]["sha256"] and report.endswith(old_report)
    old_session = BASE / "execution/session.json"
    assert sha(old_session.read_bytes()) == proof["old_session"]["expected_sha256"]
    baseline = load(BASE / "orchestration-receipt-01/current-baseline.json")
    changes = load(C01 / "source-diff.json")["changed"]
    current = dict(baseline)
    manifest = load(C01 / "as-run-source-manifest.json")
    assert len(manifest["files"]) == 130
    new_rows = {}
    for row in manifest["files"]:
        p = Path(row["path"])
        expected = row["sha256"]
        assert sha(p.read_bytes()) == expected
        new_rows[str(p.relative_to(ROOT)).replace("\\", "/")] = expected
    for rel in changes:
        assert rel in new_rows
    for rel, old in baseline.items():
        if rel not in changes:
            assert sha((ROOT / rel).read_bytes()) == old
    current.update(new_rows)
    metadata = load(C01 / "root-03/build-metadata.json")
    provenance = metadata["buildx.build.provenance"]
    material = provenance["materials"]
    assert len(material) == 1 and material[0]["uri"].startswith("pkg:oci/task109_cached_base?")
    base_digest = "c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac"
    assert material[0]["digest"]["sha256"] == base_digest
    context = provenance["invocation"]["parameters"]["args"]["context:task109_cached_base"]
    assert context.startswith("oci-layout://") and context.endswith("@sha256:" + base_digest)
    root = load(C01 / "root-03/root-result.json")
    assert root["state"] == "ERROR" and root["build_exit"] == 0 and root["terminal"] is None
    log = (C01 / "root-03/build-stderr.log").read_text(encoding="utf-8-sig")
    assert "OCI load from client" in log and "docker.io/library/task109_cached_base" in log
    assert "auth.docker.io" not in log
    oci = load(C01 / "root-03/OCI-identity.json")
    assert oci["cached_id_kind"] == "manifest" and oci["manifest_digest"] == "sha256:" + base_digest
    layout = Path(oci["layout"])
    config_file = layout / "blobs/sha256" / oci["config_digest"].split(":",1)[1]
    manifest_file = layout / "blobs/sha256" / base_digest
    assert sha(config_file.read_bytes()) == oci["config_digest"].split(":",1)[1]
    assert sha(manifest_file.read_bytes()) == base_digest
    descriptor = load(manifest_file)
    assert descriptor["config"]["digest"] == oci["config_digest"] and len(descriptor["layers"]) == 7
    assert load(config_file)["rootfs"]["diff_ids"] == oci["rootfs_diff_ids"]
    loaded = load(C01 / "root-03/loaded-image.json")
    assert loaded["loaded"]["id"] == IMAGE and loaded["loaded"]["descriptor"]["annotations"]["config.digest"] == CONFIG
    obj = json.loads(docker(["image", "inspect", IMAGE]))[0]
    actual = {"id": obj["Id"], "descriptor": obj.get("Descriptor"), "user": obj["Config"].get("User"),
              "entrypoint": obj["Config"].get("Entrypoint"), "os": obj["Os"], "architecture": obj["Architecture"],
              "labels": {k: obj["Config"].get("Labels", {}).get(k) for k in ["retrolume.task", "retrolume.permit", "retrolume.action-permit"]}}
    assert actual["id"] == IMAGE and actual["descriptor"]["annotations"]["config.digest"] == CONFIG
    assert actual["user"] == "10001:10001" and actual["entrypoint"] == ["node", "/opt/preview/h0-counter.cjs"]
    assert actual["labels"]["retrolume.task"] == "TASK-109" and actual["labels"]["retrolume.permit"] == "TASK-109-G11-20261009"
    assert not docker(["ps", "-a", "--filter", "name=retrolume-task-109-g11-", "--format", "{{.Names}}"]).strip()
    cmd = "$ports=@(18109,55449); @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in $ports} | Select-Object LocalAddress,LocalPort,OwningProcess) | ConvertTo-Json -Compress"
    p = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, timeout=15)
    assert p.returncode == 0
    listeners = json.loads(p.stdout) if p.stdout.strip() else []; assert not listeners
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/tasks/TASK-109.md", "DocuN/results/TASK-109-work-decision.md"]:
        data = (ROOT / rel).read_bytes()
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True); assert not p.exists(); p.write_bytes(data)
        before.append({"path": rel, "sha256": sha(data), "bytes": len(data)})
    copied = OUT / "TASK-109-C01-as-returned.md"; assert not copied.exists(); copied.write_bytes(report)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    raw = []
    for p in list(C01.glob("*.json")) + list((C01 / "root-03").glob("*.json")) + [C01 / "root-03/build-stderr.log"]:
        raw.append({"path": str(p), "sha256": sha(p.read_bytes()), "bytes": len(p.read_bytes())})
    save("before-manifest.json", before)
    save("current-baseline.json", current)
    save("evidence-identities.json", raw)
    save("image-resource-readonly.json", {"at": now, "image": actual, "task_containers": [], "listeners": listeners, "created_started_or_rebuilt": 0})
    save("receipt.json", {"at": now, "TASK": "TASK-109", "R": "R-103", "round": "C01",
         "report_bytes": len(report), "report_sha256": sha(report), "old_report_15176_exact_suffix": True,
         "old_session_unchanged": True, "old_baseline": len(baseline), "current_scope": len(current), "C01_sources": 130,
         "build_subfact_accepted": True, "registry_guard_false_positive": True, "root_ERROR_original_retained": True,
         "identity_kind_correction": "base/image ID本机实际为OCI manifest，严格manifest→config/layers链，不强求config==manifest",
         "image_manifest_id": IMAGE, "image_config_digest": CONFIG,
         "Root03_real": 53.922, "image_save_subsegment": 30.172, "image_build_subsegment": 2.438,
         "cumulative_real_roots": 73, "TASK109_roots": 3, "builds_used": 2,
         "old_27_219_plus_new_53_922": 81.141, "cumulative_build_subseconds": 27.017,
         "C01_active_upper": 1693.1, "C01_metadata_reserved_upper": 600, "offline": 0.297, "cleanup_upper": 30,
         "no_actual_preview_or_browser": True, "business_frozen": True,
         "next": "同卡只复用现有image直接一次create/start/诊断/收尾；新save/build0",
         "main_product_SQL_build_tests_starts": 0})
    print(json.dumps({"report": len(report), "source_scope": len(current), "immutable_image_verified": IMAGE,
        "OCI_build_true": True, "guard_false_positive": True, "task_containers": 0, "ports_free": True, "main_runtime": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
