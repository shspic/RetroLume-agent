"""One-time exact-anchor edits before TASK-083 initial verification batch."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def replace_once(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    data = path.read_text(encoding="utf-8")
    assert data.count(old) == 1, (relative, data.count(old))
    path.write_text(data.replace(old, new), encoding="utf-8", newline="")


replace_once(
    "backend/app/worker/windows_job.py",
    "        handle = api.CreateJobObjectW(None, name)  # 当前用户默认DACL；返回句柄不可继承。\n",
    "        ctypes.set_last_error(0)\n        handle = api.CreateJobObjectW(None, name)  # 当前用户默认DACL；返回句柄不可继承。\n",
)
replace_once(
    "backend/tests/test_worker_session.py",
    "from uuid import uuid4\n\nfrom app.activities",
    "from uuid import uuid4\n\nBACKEND = Path(__file__).resolve().parents[1]\nsys.path.insert(0, str(BACKEND))\n\nfrom app.activities",
)
replace_once(
    "backend/tests/test_worker_session.py",
    "\nBACKEND = Path(__file__).resolve().parents[1]\nFIXTURE =",
    "\nFIXTURE =",
)
replace_once(
    "backend/tests/test_activity_dispatch_close.py",
    "from uuid import uuid4\n\nfrom app.activities",
    "from uuid import uuid4\nfrom pathlib import Path\nimport sys\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n\nfrom app.activities",
)
