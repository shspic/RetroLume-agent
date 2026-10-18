"""TASK-083 本机合成Job夹具：仅sleep、可控子进程与管道回执。"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4


HERE = Path(__file__).resolve()


def main() -> int:
    mode = sys.argv[1]
    if mode == "fast":
        time.sleep(0.15)
        return 0
    if mode in ("hang", "child"):
        time.sleep(20 if mode == "hang" else 1.5)
        return 0
    if mode == "parent":
        subprocess.Popen([sys.executable, "-B", str(HERE), "child"], close_fds=True)
        return 0
    if mode == "controller":
        # 父测试进程先取得精确worker进程句柄，再让此SUP按约定退出。
        sys.path.insert(0, str(HERE.parents[3]))
        from app.worker.windows_job import NamedJob

        activity_id = sys.argv[2]
        generation = int(sys.argv[3])
        job = NamedJob.create(activity_id, generation)
        worker = job.spawn_suspended([sys._base_executable, "-B", str(HERE), "hang"], cwd=str(HERE.parents[3]))
        job.resume()
        print(worker, flush=True)
        sys.stdin.buffer.read(1)
        os._exit(0)  # 仅退出本夹具SUP；OS关闭其Job最后句柄。
    raise ValueError(f"unknown fixture mode: {mode}")


if __name__ == "__main__":
    raise SystemExit(main())
