# TASK-083 pg-run-08 一次只读预检（不创建容器、不连库、不修改任何文件）
# 检查：冻结四文件hash / 项目venv可用 / psycopg版本 / Docker可达 / 固定镜像在位 / 55437空闲
import hashlib
import socket
import subprocess
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")

FROZEN = {
    "backend/tests/fixtures/task083/pg_migration.py": "85d27efd9d73ed4c7736b0a0a0268c8dd852b19e29334173426a15c862a105ac",
    "backend/tests/fixtures/task083/pg_close.py": "00b58fe7d091a6ef40c1406c81faf211c83da50b79a432e205d8c2677f130970",
    "backend/app/activities/repository.py": "929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20",
    "backend/migrations/005_activities_dispatch_closed.sql": "26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb",
}
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"

out = []

def rec(k, v):
    out.append(f"{k} = {v}")

for rel, expect in FROZEN.items():
    p = ROOT / rel
    try:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        rec(f"hash:{rel}", "MATCH" if h == expect else f"DRIFT actual={h}")
    except OSError as e:
        rec(f"hash:{rel}", f"ERROR {e}")

venv_py = ROOT / "backend/.venv/Scripts/python.exe"
rec("venv:exists", venv_py.exists())
if venv_py.exists():
    try:
        r = subprocess.run([str(venv_py), "--version"], capture_output=True, text=True, timeout=25)
        rec("venv:python_version", (r.stdout + r.stderr).strip())
        r = subprocess.run([str(venv_py), "-c", "import psycopg;print('psycopg', psycopg.__version__)"],
                           capture_output=True, text=True, timeout=25)
        rec("venv:psycopg", (r.stdout + r.stderr).strip() or "no-output")
    except subprocess.TimeoutExpired:
        rec("venv:probe", "TIMEOUT")

try:
    r = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
                       capture_output=True, text=True, timeout=25)
    rec("docker:reachable", r.returncode == 0)
    rec("docker:server_version", r.stdout.strip() if r.returncode == 0 else r.stderr.strip()[:200])
except FileNotFoundError:
    rec("docker:reachable", "CLI_NOT_FOUND")
except subprocess.TimeoutExpired:
    rec("docker:reachable", "TIMEOUT")

if out and any(k.startswith("docker:reachable = True") for k in out):
    try:
        r = subprocess.run(["docker", "image", "inspect", IMAGE,
                            "--format", "{{.Id}}|{{json .RepoTags}}"],
                           capture_output=True, text=True, timeout=25)
        rec("image:present", r.returncode == 0)
        rec("image:info", r.stdout.strip() if r.returncode == 0 else r.stderr.strip()[:300])
    except subprocess.TimeoutExpired:
        rec("image:present", "TIMEOUT")
else:
    rec("image:present", "SKIPPED_docker_unreachable")

s = socket.socket()
try:
    s.bind(("127.0.0.1", 55437))
    rec("port:55437", "FREE")
except OSError as e:
    rec("port:55437", f"OCCUPIED {e}")
finally:
    s.close()

report = "\n".join(out)
print(report)
print("PRECHECK_VERDICT =",
      "PASS" if all([
          all(f"hash:{k} = MATCH" in report for k in FROZEN),
          "venv:exists = True" in report,
          "docker:reachable = True" in report,
          "image:present = True" in report,
          "port:55437 = FREE" in report,
      ]) else "FAIL")
