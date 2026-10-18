"""TASK-083 job-run-07 pre-run check: frozen hashes + environment textual check.

Read-only. No import of project code, no probes, no pyc writes.
Drift on card-mandated run chain or direct dependencies => stop (exit 2).
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
EVID = ROOT / "Ndocu" / "evidence" / "task-083" / "job-run-07"

# Card-mandated run chain (job-run-07 frozen values; drift stops the batch)
RUN_CHAIN = {
    "backend/tests/fixtures/task083/job_batch.py": "648e419cea693aa10630326cb28176e010a82b9f2c3380c33b42169c19bdef5b",
    "backend/tests/fixtures/task083/job_control.py": "5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2",
    "backend/tests/fixtures/task083/scenario_child.py": "98f132f272b952c22ac887efbf8026c5b00ec618838b6d484a3deec3c73f3f36",
    "backend/tests/fixtures/task083/fixture.py": "c9970b8ddc718da1a4e83c6d206a67f6bd000d715578e028c0a0964d9f53dc7f",
}

# Direct dependencies of the run chain, frozen per
# Ndocu/evidence/task-083/stub-fix-05/final-hashes.txt (2026-09-24) and
# Ndocu/evidence/task-084/review-02/hashes.txt (test_worker_session.py).
# Drift => stop the batch.
DIRECT_DEPS = {
    "backend/app/worker/windows_job.py": "d05ca259d5c99e6cc8f67c7fcea01667068a2901066b865239e920bd0f5246f6",
    "backend/app/worker/session.py": "502a37436de83fa5e56636d54ae5a4f694639f18c5e474e02749162e4e15f16c",
    "backend/app/worker/command.py": "b0e91c3a2e65de19656b3c902df49a33bdd29dc135bc9c292e7732e300a5e273",
    "backend/app/worker/worker_main.py": "5d065b5e44b678c08dc34c9e611a5dcaaa2d0aa3ed2c6e588fe7a70ca25a1454",
    "backend/app/worker/launcher.py": "703ceb0344e21a174f3d70e81b05ede5635d700ed84f53e26e9ae70037d2acea",
    "backend/app/worker/supervisor_ipc.py": "57be00aead15114673b180b1abb436dde10ef426a618d56f30d0031e3201ac96",
    "backend/app/worker/supervisor_main.py": "98c420e75671b3ad1823ea5a72a3866221e7cb0fc1defe032feb0a5822afb145",
    "backend/app/worker/gate.py": "7e7588a58869038f53d850816c027aab00ecd1270d2c893d1fc4902978d32674",
    "backend/tests/test_worker_session.py": "720385a66045ce9f576bf7753024ee359fda2dfbae1defc081ba73516f18352c",
}

# Not in this batch's execution chain (batch has no PG/DB); drift is reported,
# does not gate the batch.
INFORMATIONAL = {
    "backend/app/activities/repository.py": "929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20",
    "backend/migrations/005_activities_dispatch_closed.sql": "26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb",
}

ENV_REQUIRED = [
    "backend/.venv/Scripts/python.exe",
    "backend/tests",
    "backend/tests/fixtures/task083",
    "backend/app/worker",
]
ENV_INFO = [
    "backend/tests/fixtures/__init__.py",
    "backend/tests/fixtures/task083/__init__.py",
    "backend/tests/__init__.py",
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


report = {"tool": "prep_run07.py", "hash": {}, "env": {}, "stop": False, "reasons": []}

for label, table in (("run_chain", RUN_CHAIN), ("direct_deps", DIRECT_DEPS), ("informational", INFORMATIONAL)):
    report["hash"][label] = {}
    for rel, expect in table.items():
        p = ROOT / rel
        if not p.exists():
            report["hash"][label][rel] = {"exists": False, "expected": expect, "match": False}
            continue
        actual = sha256(p)
        report["hash"][label][rel] = {"exists": True, "sha256": actual, "expected": expect, "match": actual == expect}

missing_env = [rel for rel in ENV_REQUIRED if not (ROOT / rel).exists()]
report["env"]["required_missing"] = missing_env
report["env"]["informational"] = {rel: (ROOT / rel).exists() for rel in ENV_INFO}

if not all(v["match"] for v in report["hash"]["run_chain"].values()):
    report["stop"] = True
    report["reasons"].append("run_chain hash mismatch vs card freeze")
if not all(v["match"] for v in report["hash"]["direct_deps"].values()):
    report["stop"] = True
    report["reasons"].append("direct dependency hash drift vs stub-fix-05/review-02 freeze")
if missing_env:
    report["stop"] = True
    report["reasons"].append("required env path missing: %s" % missing_env)

out = EVID / "pre-run-check.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"stop": report["stop"], "reasons": report["reasons"], "output": str(out)}, ensure_ascii=False))
sys.exit(2 if report["stop"] else 0)
