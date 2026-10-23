"""仅启动当前获准的一次定向批，白名单环境，不读取私有值。"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path.cwd()
evidence = Path(__file__).absolute().parent
scratch = evidence / "scratch"
scratch.mkdir(exist_ok=True)
environment = {name: os.environ[name] for name in ("SystemRoot", "WINDIR", "TEMP", "TMP", "ComSpec", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS") if name in os.environ}
environment.update(PATH=str(root / "backend/.venv/Scripts") + os.pathsep + str(Path(environment.get("SystemRoot", "C:/Windows")) / "System32"),
                   PYTHONDONTWRITEBYTECODE="1", RETROLUME_NORMAL_TEST_SCRATCH=str(scratch))
command = [str(root / "backend/.venv/Scripts/python.exe"), "-I", "-S", "-B", "-u", str(evidence / "offline-harness.py"), str(root)]
started_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
started = time.perf_counter()
try:
    result = subprocess.run(command, cwd=root, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
    code, output = result.returncode, result.stdout
except subprocess.TimeoutExpired as error:
    code, output = 124, error.stdout or b""
elapsed = time.perf_counter() - started
(evidence / "batch-01-output.txt").write_bytes(output)
record = {"batch": 1, "command": command, "started_utc": started_utc, "elapsed_seconds": elapsed, "exit_code": code,
          "timeout_seconds": 600, "environment_names": sorted(environment),
          "site_isolation": "-I -S；显式加入现有 backend 及其 venv site-packages；不装载 sitecustomize 或用户 site",
          "inherited": "仅列示系统变量；PATH 明确重建；不读取/继承 provider key、PG/DSN、私配路径或旧 PYTHONPATH"}
(evidence / "batch-01-command.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"batch": 1, "exit_code": code, "elapsed_seconds": elapsed}))
print(output.decode("utf-8", errors="replace"))
raise SystemExit(code)
