"""TASK-083 job-run-07 batch runner wrapper.

Runs the single audited command exactly once:
  interpreter: D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe
  args:        -B -m fixtures.task083.job_batch
  cwd:         D:/shspic/project_NO3_RetroLume-agent/backend/tests

Recording guarantees (independent of tool yield):
- child stdout/stderr redirected at OS level straight into evidence files
- real exit code from Popen.wait()
- wall clock: 60 s hard cap enforced here (time.perf_counter is the single
  timing source for duration; epoch timestamps recorded alongside)
- on timeout: precise tree stop of the one process we spawned
  (taskkill /PID <pid> /T /F), never name/port batch kills
No rerun, no retry, no extra scenarios.
"""
import json
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
EVID = ROOT / "Ndocu" / "evidence" / "task-083" / "job-run-07"
CWD = ROOT / "backend" / "tests"
PY = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"
CMD_BUDGET_S = 60.0

stdout_path = EVID / "run-batch-stdout.log"
stderr_path = EVID / "run-batch-stderr.log"
meta = {
    "tool": "run_batch_07.py",
    "command": [str(PY), "-B", "-m", "fixtures.task083.job_batch"],
    "cwd": str(CWD),
    "wall_clock_budget_seconds": CMD_BUDGET_S,
    "timing_source": "run_batch_07.py time.perf_counter (single timing source for duration)",
}

t0_perf = time.perf_counter()
t0_epoch = time.time()
timed_out = False
exit_code = None
kill_output = None
pid = None
with open(stdout_path, "wb") as out_f, open(stderr_path, "wb") as err_f:
    proc = subprocess.Popen([str(PY), "-B", "-m", "fixtures.task083.job_batch"], cwd=str(CWD), stdout=out_f, stderr=err_f)
    pid = proc.pid
    try:
        exit_code = proc.wait(timeout=CMD_BUDGET_S)
    except subprocess.TimeoutExpired:
        timed_out = True
        kr = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True)
        kill_output = {"taskkill_returncode": kr.returncode, "taskkill_stdout": kr.stdout, "taskkill_stderr": kr.stderr}
        try:
            exit_code = proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            exit_code = None
t1_perf = time.perf_counter()
t1_epoch = time.time()
tz = timezone(timedelta(hours=8))
meta.update({
    "batch_pid": pid,
    "exit_code": exit_code,
    "timed_out_at_60s": timed_out,
    "kill_output": kill_output,
    "duration_seconds": round(t1_perf - t0_perf, 6),
    "start_epoch": t0_epoch,
    "start_iso_utc8": datetime.fromtimestamp(t0_epoch, tz=tz).isoformat(),
    "end_epoch": t1_epoch,
    "end_iso_utc8": datetime.fromtimestamp(t1_epoch, tz=tz).isoformat(),
    "stdout_path": str(stdout_path),
    "stderr_path": str(stderr_path),
})
(EVID / "run-batch-meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False))
