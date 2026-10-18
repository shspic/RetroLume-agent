"""Repair11 offline batch: compile in memory and run only affected pure tests."""
import hashlib
from pathlib import Path
import sys
import unittest
ROOT=Path(r"D:/shspic/project_NO3_RetroLume-agent")
FILES=(
    "backend/app/activities/repository.py",
    "backend/app/worker/session.py",
    "backend/tests/fixtures/task083/d3_pg_windows.py",
    "backend/tests/test_d3_recovery.py",
    "backend/tests/test_d3_runner_control.py",
    "Ndocu/evidence/task-083/d3-repair-11/controlled_child.py",
    "Ndocu/evidence/task-083/d3-repair-11/contracts.py",
    "Ndocu/evidence/task-083/d3-repair-11/runner.py",
)
for rel in FILES:
    path=ROOT/rel
    raw=path.read_bytes()
    compile(raw,str(path),"exec")
    print(f"COMPILE_OK {rel} {hashlib.sha256(raw).hexdigest()}",flush=True)
sys.path[:0]=[str(ROOT/"backend/tests"),str(ROOT/"backend")]
ids=(
    "test_d3_recovery.D3RecoveryGuards",
    "test_d3_recovery.D3ClockOrder",
    "test_worker_session.ProtocolUnitTests",
    "test_d3_runner_control.ControllerTests",
)
suite=unittest.defaultTestLoader.loadTestsFromNames(ids)
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(f"OFFLINE_RESULT ran={result.testsRun} failures={len(result.failures)} errors={len(result.errors)}",flush=True)
sys.exit(0 if result.wasSuccessful() else 1)