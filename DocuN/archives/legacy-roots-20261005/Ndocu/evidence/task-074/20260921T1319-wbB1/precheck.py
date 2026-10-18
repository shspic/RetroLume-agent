# -*- coding: utf-8 -*-
"""TASK-074 只读预检：冻结 hash（旧值）核对、Docker/镜像/端口/venv 检查。"""
import hashlib
import json
import os
import socket
import subprocess
import time

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
BACKEND = os.path.join(ROOT, "backend")
VENV_PY = os.path.join(BACKEND, ".venv", "Scripts", "python.exe")
OUT = os.path.dirname(os.path.abspath(__file__))

FROZEN_OLD = {
    "backend/tests/test_activity_recovery.py": "ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246",
    "backend/app/activities/repository.py": "50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6",
    "backend/migrations/001_materials.sql": "767f47c331ba1e0322e48ffcedfb46619ba53b175b9c0aa69ae267a6d5f07a8d",
    "backend/migrations/002_activities.sql": "3a9c5855aa9ddc54a03666327267ff3b7cb81eafa931a9f260c5637922b2dda6",
}
IMPORTED = [
    "backend/app/activities/__init__.py",
    "backend/app/capabilities/__init__.py",
    "backend/app/runtime.py",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, timeout=60):
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    return {"rc": p.returncode, "stdout": p.stdout.decode("utf-8", "replace"), "stderr": p.stderr.decode("utf-8", "replace")}


R = {"started_wall": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "hashes": {}, "checks": {}}
all_ok = True
for rel, expect in FROZEN_OLD.items():
    actual = sha256(os.path.join(ROOT, rel))
    ok = actual == expect
    all_ok = all_ok and ok
    R["hashes"][rel] = {"expected_old": expect, "actual": actual, "match": ok}
for rel in IMPORTED:
    R["hashes"][rel] = {"actual": sha256(os.path.join(ROOT, rel))}

R["checks"]["venv_python_exists"] = os.path.isfile(VENV_PY)
if R["checks"]["venv_python_exists"]:
    r = run([VENV_PY, "-c", "import sys, psycopg; print(sys.version.split()[0]); print('psycopg', psycopg.__version__)"])
    R["checks"]["venv_versions"] = {"rc": r["rc"], "stdout": r["stdout"].strip()}

r = run(["docker", "version", "--format", "{{.Server.Version}}"])
R["checks"]["docker"] = r
if r["rc"] == 0:
    r2 = run(["docker", "image", "inspect", "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f",
              "--format", "{{.Id}} {{.RepoTags}}"])
    R["checks"]["image"] = r2
    all_ok = all_ok and r2["rc"] == 0

s = socket.socket()
s.settimeout(2)
try:
    s.connect(("127.0.0.1", 55435))
    R["checks"]["port_55435"] = "occupied"
    all_ok = False
except OSError:
    R["checks"]["port_55435"] = "free"
finally:
    s.close()

R["all_ok"] = bool(all_ok and R["checks"].get("docker", {}).get("rc") == 0)
R["finished_wall"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
with open(os.path.join(OUT, "precheck.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)
print("ALL_OK" if R["all_ok"] else "PRECHECK_FAIL")
