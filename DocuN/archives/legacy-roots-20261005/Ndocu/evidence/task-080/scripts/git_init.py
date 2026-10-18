# -*- coding: utf-8 -*-
"""TASK-080 本地仓库初始化：git init -b main + 仅局部配置 core.autocrlf=false。
不执行 git add / commit / remote；不改 global/system 配置。"""
import json
import os
import subprocess
import datetime

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
OUT = os.path.join(ROOT, "Ndocu", "evidence", "task-080")


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       errors="replace", timeout=50)
    return {"cmd": " ".join(cmd), "code": p.returncode,
            "stdout": (p.stdout or "").strip()[:3000],
            "stderr": (p.stderr or "").strip()[:500]}


log = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "steps": []}
log["steps"].append(run(["git", "init", "-b", "main"]))
log["steps"].append(run(["git", "config", "--local", "core.autocrlf", "false"]))
log["steps"].append(run(["git", "config", "--local", "--list"]))
log["steps"].append(run(["git", "rev-parse", "--show-toplevel"]))
log["steps"].append(run(["git", "rev-parse", "--is-inside-work-tree"]))
r = run(["git", "status", "--porcelain"])
r["stdout_line_count"] = len([x for x in r["stdout"].splitlines() if x.strip()])
r["stdout"] = "(明细不输出到本日志，仅计数)"
log["steps"].append(r)
log["steps"].append(run(["git", "remote", "-v"]))
log["steps"].append(run(["git", "log", "--oneline", "-1"]))  # 预期失败：尚无提交

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "init-log.json"), "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=2)
for s in log["steps"]:
    print(s["cmd"], "->", s["code"], "|", s["stdout"][:100].replace("\n", " / "),
          "|", s["stderr"][:100].replace("\n", " / "))
