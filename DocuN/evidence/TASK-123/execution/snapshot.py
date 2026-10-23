"""TASK123 精确文件身份与前置副本，不读取私配或运行环境。"""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ALLOWED = ["backend/app/main.py", "backend/app/activities/api.py",
           "backend/app/q_readiness.py", "backend/tests/test_q_readiness.py",
           "README.md", "deploy/q-approval.md"]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    permit_path = ROOT / "DocuN/evidence/TASK-123/orchestration-20261022/permit.json"
    permit = json.loads(permit_path.read_bytes())
    assert now < datetime.datetime.fromisoformat(permit["calendar_deadline"])
    assert sha((ROOT / "DocuN/tasks/TASK-123.md").read_bytes()) == permit["contract_sha256"]
    manifest = ROOT / "DocuN/evidence/TASK-123/orchestration-20261022/input-manifest.json"
    assert sha(manifest.read_bytes()) == permit["input_manifest_sha256"]
    assert OUT.resolve().is_relative_to(ROOT)
    for folder in [ROOT, ROOT / "backend", ROOT / "backend/app", ROOT / "backend/app/activities",
                   ROOT / "backend/tests", ROOT / "deploy", OUT]:
        assert folder.resolve() == folder, str(folder)
    rows = []
    for row in json.loads(manifest.read_bytes())["rows"]:
        data = Path(row["path"]).read_bytes()
        rows.append({"path": row["path"], "bytes": len(data), "sha256": sha(data),
                     "expected_sha256": row["sha256"], "matched": sha(data) == row["sha256"]})
    assert all(row["matched"] for row in rows), "输入漂移，先停相关修改"
    before = OUT / "pre"
    before.mkdir(exist_ok=True)
    products = []
    for rel in ALLOWED:
        path = ROOT / rel
        assert path.resolve().is_relative_to(ROOT)
        exists = path.is_file()
        data = path.read_bytes() if exists else None
        backup = before / (rel.replace("/", "__") + ".bytes")
        if exists:
            assert not backup.exists(), "不得覆盖前置副本"
            backup.write_bytes(data)
        products.append({"path": rel, "exists": exists, "bytes": len(data) if exists else None,
                         "sha256": sha(data) if exists else None,
                         "pre_copy": str(backup) if exists else None})
    save("input-check.json", {"checked_at": now.isoformat(), "rows": rows, "all_matched": True})
    save("pre-snapshot.json", {"captured_at": now.isoformat(), "products": products})
    save("receipt.json", {"task": "TASK-123", "R": "R-117", "role": "A+增强工程执行者",
         "client": "Codex desktop", "specific_model_id": None,
         "window": "用户要求继续TASK122窗口；当前上下文无原执行聊天，以固定资料接续，不声称恢复缺失上下文",
         "receipt_observed_no_later_than_utc": "2026-10-21T16:29:41+00:00",
         "recorded_at": now.isoformat(), "permit_id": permit["permit_id"],
         "calendar_deadline": permit["calendar_deadline"], "tool_wall_cap_seconds": 7200,
         "closing_reserve_seconds": 600, "token_usage": None,
         "historical_failures_preserved": {"TASK120": 149, "TASK117_original": 81,
            "TASK122_metadata_failures_at_least": 2, "TASK122_unknown_subprocess_exits_and_timings": True},
         "no_resource_started": True, "normal_or_T0_or_grant_or_operator_approval_created": False})
    print(json.dumps({"inputs": len(rows), "all_matched": True, "pre_products": len(products),
                      "captured_at": now.isoformat()}, ensure_ascii=False))

if __name__ == "__main__":
    main()
