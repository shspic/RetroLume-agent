"""TASK-083 same-process owner guard: Win32 mutex is recursive for one thread."""
from pathlib import Path

path = Path("backend/app/worker/session.py")
source = path.read_text(encoding="utf-8")
edits = [
    ("import os\nimport time\n", "import os\nimport threading\nimport time\n"),
    ("from .windows_job import ActivityMutex, JobUnknown, NamedJob, job_name\n\n\nclass WindowLedger",
     '''from .windows_job import ActivityMutex, JobUnknown, NamedJob, job_name


_LOCAL_LOCKS_GUARD = threading.Lock()
_LOCAL_LOCKS: dict[str, threading.Lock] = {}


def _local_lock(activity_id: str) -> threading.Lock:
    with _LOCAL_LOCKS_GUARD:
        return _LOCAL_LOCKS.setdefault(activity_id, threading.Lock())


class WindowLedger'''),
    ("        owner: ActivityMutex | None = None\n        try:\n",
     '''        owner: ActivityMutex | None = None
        local_owner = _local_lock(activity_id)
        if not local_owner.acquire(blocking=False):
            return SessionOutcome(run_tag, "local_owner_busy", activity_id)
        try:
'''),
    ("            if owner is not None:\n                owner.close()\n        return SessionOutcome(\n",
     "            if owner is not None:\n                owner.close()\n            local_owner.release()\n        return SessionOutcome(\n"),
]
for before, after in edits:
    if source.count(before) != 1:
        raise RuntimeError(f"anchor mismatch {before[:60]!r}")
    source = source.replace(before, after, 1)
path.write_text(source, encoding="utf-8", newline="")
