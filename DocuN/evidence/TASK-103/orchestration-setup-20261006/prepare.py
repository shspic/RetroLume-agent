"""Authorize through file/hash and read-only Docker metadata; no product execution."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import subprocess

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-103/orchestration-setup-20261006"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
OLD = "80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    target = OUT / name
    if target.exists():
        raise RuntimeError("Do not overwrite prepared authorization")
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inspect(kind, target):
    args = ["docker.exe", "image", "inspect", target] if kind == "image" else ["docker.exe", "inspect", "--type", "container", target]
    result = subprocess.run(args, capture_output=True, timeout=15, check=False)
    if result.returncode:
        return {"kind": kind, "verified": False, "exit_code": result.returncode}
    obj = json.loads(result.stdout)[0]
    if kind == "image":
        return {"kind": kind, "verified": obj["Id"] == target, "Id": obj["Id"], "OS": obj["Os"],
            "Architecture": obj["Architecture"], "RepoTags": obj.get("RepoTags"), "RepoDigests": obj.get("RepoDigests")}
    return {"kind": kind, "verified": obj["Id"] == target, "Id": obj["Id"], "Name": obj["Name"], "Image": obj["Image"],
        "State": {key: obj["State"].get(key) for key in ("Status", "Running", "Pid", "ExitCode")},
        "Mounts": [{key: mount.get(key) for key in ("Type", "Name", "Destination", "RW")} for mount in obj.get("Mounts", [])]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (ROOT / "DocuN/tasks/TASK-103.md").exists() or (ROOT / "DocuN/results/TASK-103-result.md").exists():
        raise RuntimeError("TASK103 already has work; inspect instead of replacing")
    newly_expected = ["backend/migrations/010_learning_memory.sql", "backend/app/memory", "frontend/src/activities/MemoryWorkspace.tsx"]
    if any((ROOT / rel).exists() for rel in newly_expected):
        raise RuntimeError("New memory product objects already exist; inspect actual in-flight changes")
    prior = load(ROOT / "DocuN/evidence/TASK-102/orchestration-receipt-01/identity-checks.json")
    context = {str((ROOT / rel).resolve()).casefold() for rel in ("DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuN/tasks/TASK-102.md")}
    checks = []
    for row in prior:
        path = Path(row["path"])
        if str(path.resolve()).casefold() in context:
            continue
        actual = sha(path.read_bytes())
        checks.append({"path": str(path), "expected": row["expected"], "actual": actual, "match": actual == row["expected"]})
    if len(checks) != 56 or any(not row["match"] for row in checks):
        raise RuntimeError("Current code/rule/parent identity changed")
    save("identity-checks.json", checks)
    save("approval.json", {"registered_at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "user_approval": "批准",
        "user_message_exact_timestamp": "not provided; client date2026-10-06 Asia/Shanghai", "adopted_package": "G9-P",
        "scope_source": "TASK102 result A-D and TASK102-work-decision recommended concrete packet from immediately preceding user-facing approval request",
        "adoption_effect": "bounded synthetic implementation/verification; no user DB/data deletion/provider paid/deployment permission",
        "old_permissions_revived": False, "recipient": "A+ actual TASK102 execution window", "next_task": "TASK103/R097"})
    resources = {"checked_at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "cached_image": inspect("image", IMAGE),
        "old_preserved_container": inspect("container", OLD), "new_resources_not_started": True,
        "ports_checked_free_in_readonly_preflight": [55443,55444,55445,18103,18104],
        "new_names_and_volumes_checked_no_collision": True,
        "node_dependencies_present": (ROOT / "frontend/node_modules").is_dir(),
        "playwright_present": (ROOT / "frontend/node_modules/playwright/package.json").is_file(),
        "python_present": (ROOT / "backend/.venv/Scripts/python.exe").is_file(),
        "metadata_read_errors": ["rg requested nonexistent task100/bootstrap.py; actual bootstrap/sitecustomize.py located", "rg requested nonexistent worker/config.py; no product execution or modification"],
        "command_output_policy": "only safe selected Docker fields; no raw Env, no credential/read private config", "root_business_runs": 0}
    save("resource-preflight.json", resources)
    product = []
    extensions = {".py", ".sql", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".css", ".html", ".svg"}
    for rel_root in ("backend/app", "backend/migrations", "backend/tests", "frontend/src", "frontend/tests", "frontend/dist"):
        base = ROOT / rel_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix in extensions and "__pycache__" not in path.parts:
                product.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(path.read_bytes()), "bytes": path.stat().st_size})
    for rel in ("README.md", ".gitignore", "frontend/package.json", "frontend/package-lock.json", "config/activity.example.json"):
        path = ROOT / rel
        if path.is_file():
            product.append({"path": rel, "sha256": sha(path.read_bytes()), "bytes": path.stat().st_size})
    save("product-baseline.json", product)
    rels = ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/results/TASK-102-work-decision.md"]
    before = []
    for rel in rels:
        data = (ROOT / rel).read_bytes()
        target = OUT / "before" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError("Prior state already preserved")
        target.write_bytes(data)
        before.append({"path": rel, "sha256": sha(data), "bytes": len(data), "backup": str(target)})
    save("before-manifest.json", before)
    report = ROOT / "DocuN/results/TASK-102-result.md"
    if sha(report.read_bytes()) != "f3bf109c1398b5cf1a8d112f4ebcc55db6d3c0a1f42dc2f92d7aff67377f22b3":
        raise RuntimeError("Approved design report changed")
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "G9-P": "approved by user", "TASK103_R097": "preparing authorized full card",
        "identity_matches": len(checks), "product_source_baseline_count": len(product), "cached_image_verified": resources["cached_image"]["verified"],
        "old_container_current_state": resources["old_preserved_container"].get("State"), "root_product_writes": 0, "root_business_runs": 0,
        "read_only_infrastructure_inspection": True, "new_resource_creates_starts": 0, "result102_untouched": True})
    print(json.dumps({"adopted": "G9-P", "matches": len(checks), "product_baseline": len(product), "cached_image": resources["cached_image"].get("RepoTags"),
        "old_container": resources["old_preserved_container"].get("State"), "new_resources_started": 0, "TASK103": "authorized card preparing"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
