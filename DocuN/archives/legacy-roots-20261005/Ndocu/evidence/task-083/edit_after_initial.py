"""Single bounded correction after TASK-083 initial synthetic Job batch; no rerun here."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def replace_once(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    data = path.read_text(encoding="utf-8")
    assert data.count(old) == 1, (relative, data.count(old))
    path.write_text(data.replace(old, new), encoding="utf-8", newline="")


replace_once(
    "backend/tests/test_worker_session.py",
    "from datetime import datetime, timedelta, timezone\n",
    "from datetime import datetime, timedelta, timezone\nimport math\n",
)
replace_once(
    "backend/tests/test_worker_session.py",
    "        if not 1 <= elapsed_seconds <= window_seconds:\n",
    "        if not 1 <= math.ceil(elapsed_seconds) <= window_seconds:\n",
)
replace_once(
    "backend/tests/test_worker_session.py",
    "        return [sys.executable, \"-B\", str(FIXTURE), mode]\n",
    "        return [sys._base_executable, \"-B\", str(FIXTURE), mode]\n",
)
replace_once(
    "backend/tests/test_worker_session.py",
    "            sys.executable, \"-B\", str(FIXTURE), \"controller\", activity_id, \"7\",\n",
    "            sys._base_executable, \"-B\", str(FIXTURE), \"controller\", activity_id, \"7\",\n",
)
replace_once(
    "backend/tests/fixtures/task083/fixture.py",
    "worker = job.spawn_suspended([sys.executable, \"-B\", str(HERE), \"hang\"], cwd=str(HERE.parents[3]))",
    "worker = job.spawn_suspended([sys._base_executable, \"-B\", str(HERE), \"hang\"], cwd=str(HERE.parents[3]))",
)
