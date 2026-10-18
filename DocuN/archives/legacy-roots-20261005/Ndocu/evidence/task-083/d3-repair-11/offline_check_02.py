"""Repair11 second offline batch: only post-batch-01 fixture/runner corrections."""
import hashlib
from pathlib import Path
import sys
import unittest
ROOT=Path(r"D:/shspic/project_NO3_RetroLume-agent")
FILES=(
 "backend/tests/fixtures/task083/d3_pg_windows.py",
 "backend/tests/test_d3_runner_control.py",
 "Ndocu/evidence/task-083/d3-repair-11/runner.py",
 "Ndocu/evidence/task-083/d3-repair-11/controlled_child.py",
 "Ndocu/evidence/task-083/d3-repair-11/contracts.py",
)
for rel in FILES:
    path=ROOT/rel; raw=path.read_bytes(); compile(raw,str(path),"exec")
    print(f"COMPILE_OK {rel} {hashlib.sha256(raw).hexdigest()}",flush=True)
sys.path[:0]=[str(ROOT/"backend/tests"),str(ROOT/"backend")]
ids=(
 "test_d3_runner_control.ControllerTests.test_runner_import_does_not_touch_resources",
 "test_d3_runner_control.ControllerTests.test_unknown_cleanup_and_windows_start_block_retry",
 "test_d3_runner_control.ControllerTests.test_close_failure_marks_cleanup_unknown",
 "test_d3_runner_control.ControllerTests.test_optimization_guard",
 "test_d3_runner_control.ControllerTests.test_exact_results_and_deadlines",
)
suite=unittest.defaultTestLoader.loadTestsFromNames(ids)
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(f"OFFLINE_RESULT ran={result.testsRun} failures={len(result.failures)} errors={len(result.errors)}",flush=True)
sys.exit(0 if result.wasSuccessful() else 1)