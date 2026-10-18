"""stub-fix-05 定向命令运行器：单一计时来源 time.perf_counter。

用法：python run_cmd.py <log> <meta> <workdir> <cmd...>
子进程stdout+stderr原样写入log；meta记录命令、工作目录、退出码、时长。
"""
import subprocess
import sys
import time
from pathlib import Path

log_path, meta_path, workdir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
cmd = sys.argv[4:]
t0 = time.perf_counter()
proc = subprocess.run(cmd, cwd=str(workdir), capture_output=True)
duration = time.perf_counter() - t0
log_path.write_bytes((proc.stdout or b"") + (proc.stderr or b""))
meta_path.write_text(
    "TASK-083 stub-fix-05 run (single timing source: perf_counter)\n"
    f"command: {' '.join(cmd)}\n"
    f"cwd: {workdir}\n"
    f"exit_code: {proc.returncode}\n"
    f"duration_perf_counter_seconds: {duration:.7f}\n",
    encoding="utf-8")
print(f"exit={proc.returncode} seconds={duration:.7f}")
