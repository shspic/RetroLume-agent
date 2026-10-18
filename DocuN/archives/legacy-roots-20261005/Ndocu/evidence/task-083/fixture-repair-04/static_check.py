"""fixture-repair-04 静态检查：AST解析（不import）、新旧hash、有限diff、未改文件防漂移。

只覆盖任务卡三文件的新旧对照；未改文件与review-03/hashes.txt冻结值核对，
windows_job.py无review-03冻结值，仅登记现值供复核。不运行代码、不写pyc。
"""
import ast
import difflib
import hashlib
import time
from pathlib import Path

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
EV = ROOT / "Ndocu/evidence/task-083/fixture-repair-04"
PRE = EV / "pre"
CHANGED = [
    "backend/tests/fixtures/task083/job_control.py",
    "backend/tests/fixtures/task083/focused_unit.py",
    "backend/tests/fixtures/task083/offline_unit.py",
]
FROZEN = {
    "backend/app/worker/launcher.py": "703ceb0344e21a174f3d70e81b05ede5635d700ed84f53e26e9ae70037d2acea",
    "backend/app/worker/supervisor_ipc.py": "57be00aead15114673b180b1abb436dde10ef426a618d56f30d0031e3201ac96",
    "backend/app/worker/supervisor_main.py": "98c420e75671b3ad1823ea5a72a3866221e7cb0fc1defe032feb0a5822afb145",
    "backend/app/worker/session.py": "502a37436de83fa5e56636d54ae5a4f694639f18c5e474e02749162e4e15f16c",
    "backend/app/worker/command.py": "b0e91c3a2e65de19656b3c902df49a33bdd29dc135bc9c292e7732e300a5e273",
    "backend/app/worker/worker_main.py": "5d065b5e44b678c08dc34c9e611a5dcaaa2d0aa3ed2c6e588fe7a70ca25a1454",
    "backend/app/worker/gate.py": "7e7588a58869038f53d850816c027aab00ecd1270d2c893d1fc4902978d32674",
    "backend/app/worker/windows_job.py": None,
    "backend/app/activities/repository.py": "929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20",
    "backend/migrations/005_activities_dispatch_closed.sql": "26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb",
    "backend/tests/fixtures/task083/fixture.py": "c9970b8ddc718da1a4e83c6d206a67f6bd000d715578e028c0a0964d9f53dc7f",
    "backend/tests/fixtures/task083/scenario_child.py": "98f132f272b952c22ac887efbf8026c5b00ec618838b6d484a3deec3c73f3f36",
    "backend/tests/fixtures/task083/job_batch.py": "648e419cea693aa10630326cb28176e010a82b9f2c3380c33b42169c19bdef5b",
}

start = time.monotonic()
lines = ["TASK-083 fixture-repair-04 static check: AST parse only (no import), changed-file diff, frozen drift guard"]
diff = []
for rel in CHANGED:
    path = ROOT / rel
    data = path.read_bytes()
    ast.parse(data.decode("utf-8"), filename=str(path))
    sha = hashlib.sha256(data).hexdigest()
    old = (PRE / rel.replace("/", "__")).read_bytes()
    lines.append(f"{rel}")
    lines.append(f"  pre_sha256={hashlib.sha256(old).hexdigest()}")
    lines.append(f"  new_sha256={sha}")
    diff.extend(difflib.unified_diff(
        old.decode("utf-8").splitlines(keepends=True),
        data.decode("utf-8").splitlines(keepends=True),
        fromfile="a/" + rel, tofile="b/" + rel))
for rel, expected in FROZEN.items():
    actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    if expected is None:
        lines.append(f"RECORDED {rel} {actual}")
    elif actual != expected:
        raise SystemExit(f"FROZEN_DRIFT {rel} actual={actual} expected={expected}")
    else:
        lines.append(f"FROZEN_OK {rel} {actual}")
(EV / "incremental.diff").write_text("".join(diff), encoding="utf-8")
(EV / "final-hashes.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"AST_OK {len(CHANGED)} changed paths; FROZEN_OK {sum(1 for v in FROZEN.values() if v)} frozen paths")
print("\n".join(lines))
print(f"elapsed_seconds={time.monotonic() - start:.6f}")
