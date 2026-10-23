"""仅本机同一Docker客户端的有界只读版本门；不启动或修复宿主服务。"""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
root = Path.cwd()
evidence = Path(__file__).absolute().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
options = parser.parse_args()
assert options.output.is_absolute() and options.output.parent == evidence and not options.output.exists()
docker = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/DockerDesktop/resources/bin/docker.exe"
assert docker.is_file()
names = ("SystemRoot", "WINDIR", "TEMP", "TMP", "ComSpec", "USERPROFILE", "APPDATA", "LOCALAPPDATA")
environment = {name: os.environ[name] for name in names if name in os.environ}
environment["PATH"] = str(docker.parent) + os.pathsep + str(Path(environment["SystemRoot"]) / "System32")
command = [str(docker), "version", "--format", "{{json .}}"]
started = time.perf_counter()
record = {"command": command, "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "environment_names": sorted(environment), "timeout_seconds": 25, "read_only": True}
try:
    result = subprocess.run(command, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25)
    record.update(exit_code=result.returncode, stderr=result.stderr.decode("utf-8", errors="replace")[:3000])
    try:
        value = json.loads(result.stdout)
    except ValueError:
        value = {}
    client, server = value.get("Client") or {}, value.get("Server") or {}
    record["client"] = {key: client.get(key) for key in ("Version", "ApiVersion", "Os", "Arch", "Context")}
    record["server"] = {key: server.get(key) for key in ("Version", "ApiVersion", "MinAPIVersion", "Os", "Arch")}
    record["server_responded"] = bool(server)
except subprocess.TimeoutExpired:
    record.update(exit_code=124, server_responded=False, reason="docker_version_read_timeout")
record["elapsed_seconds"] = time.perf_counter() - started
with options.output.open("x", encoding="utf-8") as stream:
    stream.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(record, ensure_ascii=False, indent=2))
raise SystemExit(0 if record.get("server_responded") and record.get("exit_code") == 0 else 1)
