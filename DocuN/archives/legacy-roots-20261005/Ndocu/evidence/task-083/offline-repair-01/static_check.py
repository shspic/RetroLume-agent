"""TASK-083 补足轮01一次性只读 AST/hash/范围核对。"""

from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FILES = (
    "backend/app/worker/__init__.py",
    "backend/app/worker/command.py",
    "backend/app/worker/gate.py",
    "backend/app/worker/launcher.py",
    "backend/app/worker/session.py",
    "backend/app/worker/windows_job.py",
    "backend/app/worker/worker_main.py",
    "backend/tests/test_worker_session.py",
    "backend/tests/fixtures/task083/fixture.py",
    "backend/tests/fixtures/task083/job_control.py",
    "backend/tests/fixtures/task083/offline_unit.py",
    "backend/tests/fixtures/task083/run_offline.py",
    "backend/tests/fixtures/task083/pg_close.py",
    "backend/tests/fixtures/task083/pg_migration.py",
)
FROZEN = {
    "backend/app/activities/repository.py": "929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20",
    "backend/migrations/005_activities_dispatch_closed.sql": "26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb",
    "backend/migrations/004_activities_time_budget.sql": "8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc",
}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    for relative, expected in FROZEN.items():
        actual = digest(ROOT / relative)
        assert actual == expected, f"frozen drift {relative} {actual}"
        print(f"FROZEN OK {relative} {actual}")
    for relative in FILES:
        path = ROOT / relative
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=relative)
        print(f"AST OK {relative} {digest(path)}")
    # 纯单元运行清单显式只指向指定方法；绝不包含 WindowsJobTests。
    runner = (ROOT / "backend/tests/fixtures/task083/run_offline.py").read_text(encoding="utf-8")
    assert "WindowsJobTests." not in runner
    assert "discover(" not in runner
    for relative in ("backend/app/worker/command.py", "backend/app/worker/launcher.py", "backend/app/worker/session.py"):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "command_for_lease" not in source
    print("Pure unit manifest excludes Job/PG discovery; no arbitrary command callback")


if __name__ == "__main__":
    main()
