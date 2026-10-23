"""本轮唯一首批，累计03；精确白名单环境及600秒超时。"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
root = Path.cwd()
evidence = Path(__file__).absolute().parent
for name in ("batch-03-start.json", "batch-03-command.json", "batch-03-output.txt", "batch-03-summary.json"):
    if (evidence / name).exists():
        raise SystemExit("batch_already_started_or_has_output")
for row in json.loads((evidence / "tested-before-batch-03.json").read_text(encoding="utf-8")):
    assert hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"], "tested_input_drift"
scratch = root / "DocuN/evidence/TASK-125/execution/scratch"
link = scratch / "junction-fixture/link"
expected = json.loads((evidence / "junction-before.json").read_text(encoding="utf-8"))
info = link.lstat()
assert (info.st_dev, info.st_ino, info.st_mtime_ns, os.readlink(link)) == (
    expected["link_device"], expected["link_inode"], expected["link_mtime_ns"], expected["target_from_readlink"]), "junction_identity_drift"
environment = {name: os.environ[name] for name in ("SystemRoot", "WINDIR", "TEMP", "TMP", "ComSpec", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS") if name in os.environ}
environment.update(PATH=str(root / "backend/.venv/Scripts") + os.pathsep + str(Path(environment.get("SystemRoot", "C:/Windows")) / "System32"),
                   PYTHONDONTWRITEBYTECODE="1", RETROLUME_NORMAL_TEST_SCRATCH=str(scratch), RETROLUME_NORMAL_TEST_JUNCTION=str(link))
command = [str(root / "backend/.venv/Scripts/python.exe"), "-I", "-S", "-B", "-u", str(evidence / "offline-harness-03.py"), str(root)]
start = {"cumulative_batch": 3, "command": command, "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "timeout_seconds": 600, "environment_names": sorted(environment),
         "inherited": "仅必要系统变量；PATH重建；不读取/继承真实PGHOSTADDR/PGHOST/DSN/provider/私配/PYTHONPATH，PG合成占位仅在测试局部创建",
         "site_isolation": "-I -S -B；仅显式加入已有项目依赖；不装载sitecustomize"}
(evidence / "batch-03-start.json").write_text(json.dumps(start, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
started = time.perf_counter()
try:
    result = subprocess.run(command, cwd=root, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
    code, output = result.returncode, result.stdout
except subprocess.TimeoutExpired as error:
    code, output = 124, error.stdout or b""
elapsed = time.perf_counter() - started
(evidence / "batch-03-output.txt").write_bytes(output)
(evidence / "batch-03-command.json").write_text(json.dumps(dict(start, elapsed_seconds=elapsed, exit_code=code), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"cumulative_batch": 3, "exit_code": code, "elapsed_seconds": elapsed}))
print(output.decode("utf-8", errors="replace"))
raise SystemExit(code)
