"""TASK-083 fixture-completion-06 final targeted batch (one quota, two commands).

Wrapper runs under managed Python; the two commands themselves use the project
venv interpreter exactly as the card specifies. Command 2 only starts if
command 1 exits 0 (card rule). Single timing source: time.perf_counter here.
No retry, no recheck, no pyc (both test commands use -B).
"""
import subprocess
import time
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
EV = ROOT / "Ndocu/evidence/task-083/fixture-completion-06"
VENV_PY = ROOT / "backend/.venv/Scripts/python.exe"

COMMANDS = [
    ("unit-lifecycle-06",
     [str(VENV_PY), "-B", "backend/tests/fixtures/task083/focused_unit.py", "--failfast",
      "StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt",
      "StartLifecycleTests.test_04_start_handle_release_exactly_once_on_failure"]),
    ("offline-05-06",
     [str(VENV_PY), "-B", "backend/tests/fixtures/task083/offline_unit.py",
      "OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry"]),
]

for idx, (name, cmd) in enumerate(COMMANDS):
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, timeout=60)
    elapsed = time.perf_counter() - t0
    out = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")
    (EV / f"{name}.log").write_text(out + ("\n[stderr]\n" + err if err.strip() else ""), encoding="utf-8")
    (EV / f"{name}-meta.txt").write_text(
        f"command: {' '.join(cmd)}\n"
        f"cwd: {ROOT}\n"
        f"exit_code: {proc.returncode}\n"
        f"elapsed_seconds: {elapsed:.6f}\n"
        f"timing_source: time.perf_counter in run_batch_06.py (single)\n"
        f"limit: <=60s per command, <=120s total\n",
        encoding="utf-8")
    print(f"=== {name}: exit={proc.returncode} elapsed={elapsed:.3f}s")
    if out:
        print(out[-1500:])
    if err.strip():
        print("[stderr]", err[-800:])
    if proc.returncode != 0:
        remaining = [n for n, _ in COMMANDS[idx + 1:]]
        print(f"STOP: {name} failed; not started per card: {remaining or 'none'}")
        break
else:
    print("BATCH COMPLETE: all commands exit 0")
