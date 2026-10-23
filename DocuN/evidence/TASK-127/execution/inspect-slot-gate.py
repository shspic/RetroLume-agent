"""只读复核精确source槽位预建存在门，不输出Docker Env。"""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
here = Path(__file__).absolute().parent
docker = Path(os.environ["LOCALAPPDATA"]) / "Programs/DockerDesktop/resources/bin/docker.exe"
env = {key: os.environ[key] for key in ("SystemRoot", "WINDIR", "TEMP", "TMP", "ComSpec", "USERPROFILE", "APPDATA", "LOCALAPPDATA") if key in os.environ}
env["PATH"] = str(docker.parent) + os.pathsep + str(Path(env["SystemRoot"]) / "System32")
rows = []
for kind, name in (("container", "retrolume-q-first-normal"), ("volume", "retrolume-q-first-normal-data"), ("network", "retrolume-first-install-source_default")):
    args = [str(docker), kind, "inspect", name]
    start = time.perf_counter()
    result = subprocess.run(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    row = {"argv": args, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "exit_code": result.returncode, "stderr": result.stderr.decode("utf-8", errors="replace"), "wall_seconds": time.perf_counter() - start}
    if result.returncode == 0:
        objects = json.loads(result.stdout)
        row["existing_projection"] = [{key: obj.get(key) for key in ("Id", "ID", "Name", "Created", "CreatedAt", "State", "Labels")} for obj in objects]
    rows.append(row)
with (here / "slot-gate-diagnosis.json").open("x", encoding="utf-8") as out:
    json.dump(rows, out, ensure_ascii=False, indent=2)
print(json.dumps(rows, ensure_ascii=False))
