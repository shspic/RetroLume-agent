# TASK-083 launcher-complete-09 一次只读预检：Docker / 镜像 / 端口 / venv。
# 缺失即阻塞（exit 2）：不启动 Desktop、不循环等待、不换端口、不杀占用者。
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
VENV_PY = ROOT / "backend/.venv/Scripts/python.exe"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
PORT = 55438
lines = []
ok = True

def check(label, cond, detail=""):
    global ok
    lines.append(f"{label}: {'OK' if cond else 'FAIL'} {detail}".rstrip())
    if not cond:
        ok = False

t0 = time.monotonic()
try:
    r = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
                       capture_output=True, text=True, timeout=20)
    check("docker", r.returncode == 0, (r.stdout or r.stderr).strip()[:80])
except Exception as e:
    check("docker", False, f"{type(e).__name__}: {e}")

try:
    r = subprocess.run(["docker", "image", "inspect", IMAGE, "--format", "{{json .RepoTags}}"],
                       capture_output=True, text=True, timeout=20)
    check("image", r.returncode == 0, (r.stdout or r.stderr).strip()[:120])
except Exception as e:
    check("image", False, f"{type(e).__name__}: {e}")

s = socket.socket()
s.settimeout(2)
try:
    s.connect(("127.0.0.1", PORT))
    check("port", False, f"127.0.0.1:{PORT} 已被占用")
except OSError:
    check("port", True, f"127.0.0.1:{PORT} 空闲")
finally:
    s.close()

check("venv_python", VENV_PY.is_file(), str(VENV_PY))
try:
    r = subprocess.run([str(VENV_PY), "-c", "import psycopg,sys;print(sys.version.split()[0], psycopg.__version__)"],
                       capture_output=True, text=True, timeout=30)
    check("venv_psycopg", r.returncode == 0, r.stdout.strip()[:60] or r.stderr.strip()[:80])
except Exception as e:
    check("venv_psycopg", False, f"{type(e).__name__}: {e}")

lines.append(f"elapsed: {time.monotonic() - t0:.2f}s")
lines.append("PRECHECK_OK" if ok else "PRECHECK_BLOCKED")
out = "\n".join(lines)
Path(__file__).with_name("precheck-output.txt").write_text(out + "\n", encoding="utf-8")
print(out)
sys.exit(0 if ok else 2)
