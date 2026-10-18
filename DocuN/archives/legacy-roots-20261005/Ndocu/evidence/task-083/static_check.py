"""TASK-083 read-only, exact-scope static verification."""

from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PYTHON_FILES = [
    "backend/app/activities/repository.py",
    "backend/app/activities/__init__.py",
    "backend/app/worker/__init__.py",
    "backend/app/worker/gate.py",
    "backend/app/worker/session.py",
    "backend/app/worker/windows_job.py",
    "backend/app/worker/worker_main.py",
    "backend/tests/test_activity_time_budget.py",
    "backend/tests/test_activity_dispatch_close.py",
    "backend/tests/test_worker_session.py",
    "backend/tests/fixtures/task083/fixture.py",
]
ORIGINALS = {
    "backend/app/activities/repository.py": "045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534",
    "backend/app/activities/__init__.py": "6bdb960912ea3fc7ddd8730f37a44e580b73768e1067d23facc9983ca04a46dd",
    "backend/tests/test_activity_time_budget.py": "63a19d1f2a99236d56bd1cc1841953908fa8c1f955ff0c6d5d61b4ee84621a86",
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for relative in PYTHON_FILES:
        path = ROOT / relative
        ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        print(f"AST OK {relative} SHA256={digest(path)}")
    for relative, expected in ORIGINALS.items():
        old = ROOT / "Ndocu/evidence/task-083/pre" / Path(relative).name
        actual = digest(old)
        assert actual == expected, f"original drift: {relative} {actual}"
        print(f"PRE OK {relative} SHA256={actual}")
    migration = ROOT / "backend/migrations/004_activities_time_budget.sql"
    assert digest(migration) == "8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc"
    print("004 SHA256 OK")
    for relative in PYTHON_FILES:
        if "/worker/" not in relative and "fixtures/task083/" not in relative:
            continue
        source = (ROOT / relative).read_text(encoding="utf-8")
        forbidden = ("httpx.", "requests.", "urllib.request", "socket.", "psycopg.connect", "docker")
        assert not any(item in source for item in forbidden), f"external action token: {relative}"
    print("No direct real-network/DB/service token in internal worker or synthetic fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
