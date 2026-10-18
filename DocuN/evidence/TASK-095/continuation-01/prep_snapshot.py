"""TASK-095 续作01 准备阶段：冻结修改前副本与 SHA-256，登记旧账继承。

仅写 continuation-01 证据目录；不覆盖 095/096 旧件。真实身份如实登记：
本窗口为 WorkBuddy（GLM-5.3-Flash），与 092/094/095 的 Claude 桌面 Code
窗口不同，非 096 独立审计窗口。
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
EVIDENCE = ROOT / "DocuN" / "evidence" / "TASK-095" / "continuation-01"
ORIGINALS = EVIDENCE / "pre-originals"

FILES = [
    "backend/app/materials/api.py",
    "frontend/src/activities/ActivityWorkspace.tsx",
    "backend/app/activities/repository.py",
    "backend/tests/test_activity_workspace_reads.py",
    "backend/tests/test_activity_workspace_api.py",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for relative in FILES:
        source = ROOT / relative
        digest = sha256_file(source)
        hashes[relative] = digest
        target = ORIGINALS / relative.replace("/", "__")
        shutil.copy2(source, target)
        if sha256_file(target) != digest:
            raise SystemExit(f"copy verification failed: {relative}")
    (EVIDENCE / "pre-hashes.json").write_text(
        json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "purpose": "TASK-095 continuation-01 修改前冻结副本与哈希（改前存证）",
            "note": "副本在 pre-originals/，SHA-256 见本表；不覆盖 095 final-snapshot 旧件",
            "files": hashes,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(hashes, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
