# -*- coding: utf-8 -*-
"""TASK-080 只读环境检查：Git可用性、仓库归属、重解析点、实际目录盘点。
不写任何项目文件（仅本证据JSON）；不修改任何配置。"""
import os
import json
import subprocess
import datetime

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
OUT = os.path.join(ROOT, "Ndocu", "evidence", "task-080")


def run(cmd, cwd=ROOT):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           errors="replace", timeout=50)
        return {"cmd": " ".join(cmd), "cwd": cwd or ROOT, "code": p.returncode,
                "stdout": (p.stdout or "").strip()[:3000],
                "stderr": (p.stderr or "").strip()[:3000]}
    except Exception as e:  # noqa: BLE001
        return {"cmd": " ".join(cmd), "cwd": cwd or ROOT, "code": "EXC",
                "stdout": "", "stderr": repr(e)[:500]}


def reparse(p):
    return {"islink": os.path.islink(p),
            "isjunction": bool(getattr(os.path, "isjunction", None) and os.path.isjunction(p))}


def count_files(d, cap=200000):
    n, total = 0, 0
    for dp, dn, fn in os.walk(d):
        dn[:] = [x for x in dn if x != ".git"]
        for f in fn:
            n += 1
            if n > cap:
                return n, total
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    return n, total


res = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "root": ROOT}

# 1) Git 可用性
res["git_version"] = run(["git", "--version"])
res["git_where"] = run(["where", "git"])

# 2) 仓库归属：当前目录向上是否已有仓库
res["rev_parse_toplevel"] = run(["git", "rev-parse", "--show-toplevel"])
res["rev_parse_gitdir"] = run(["git", "rev-parse", "--git-dir"])

chain = {}
for d in [ROOT, os.path.dirname(ROOT), os.path.dirname(os.path.dirname(ROOT))]:
    g = os.path.join(d, ".git")
    chain[d] = {"git_exists": os.path.exists(g), "is_dir": os.path.isdir(g),
                "is_file": os.path.isfile(g)}
res["git_chain"] = chain

# 3) 根与顶层条目 + 重解析点（深度1）
tops = sorted(os.listdir(ROOT))
res["top_level"] = []
for name in tops:
    p = os.path.join(ROOT, name)
    e = {"name": name, "dir": os.path.isdir(p), "file": os.path.isfile(p)}
    e.update(reparse(p))
    res["top_level"].append(e)

# 子目录一级 .git（防子仓库/嵌套仓库）
sub_git = []
for name in tops:
    p = os.path.join(ROOT, name)
    if os.path.isdir(p) and not os.path.islink(p):
        g = os.path.join(p, ".git")
        if os.path.exists(g):
            sub_git.append(os.path.relpath(g, ROOT).replace("\\", "/"))
res["subdir_git"] = sub_git

# 重解析点扫描：深度<=2，跳过 .git 与依赖/虚拟环境目录内容
SKIP = {".git", "node_modules", ".venv", "__pycache__"}
rp_hits = []
for dp, dn, fn in os.walk(ROOT):
    depth = os.path.relpath(dp, ROOT).count(os.sep)
    if depth >= 2:
        dn[:] = []
        continue
    dn[:] = [x for x in dn if x not in SKIP]
    for name in dn:
        p = os.path.join(dp, name)
        r = reparse(p)
        if r["islink"] or r["isjunction"]:
            rp_hits.append({"path": os.path.relpath(p, ROOT).replace("\\", "/"), **r})
res["reparse_hits_depth2"] = rp_hits
res["root_reparse"] = reparse(ROOT)

# 4) 实际目录盘点
spec = {}
for rel in ["backend/.venv", "backend/__pycache__", "backend/app", "backend/migrations",
            "backend/tests", "frontend/node_modules", "frontend/dist", "frontend/src",
            "frontend/public", "deploy", "config", "tests", "spikes", "docu",
            "Ndocu", "Ndocu/evidence/task-079", ".workbuddy", "evidence"]:
    p = os.path.join(ROOT, rel)
    if os.path.isdir(p):
        n, total = count_files(p)
        spec[rel] = {"exists": True, "type": "dir", "files": n, "bytes": total}
    elif os.path.exists(p):
        spec[rel] = {"exists": True, "type": "file", "bytes": os.path.getsize(p)}
    else:
        spec[rel] = {"exists": False}
res["special_dirs"] = spec

cfg = os.path.join(ROOT, "config")
res["config_files"] = sorted(os.listdir(cfg)) if os.path.isdir(cfg) else []
res["root_files"] = [x for x in tops if os.path.isfile(os.path.join(ROOT, x))]
res["frontend_top"] = sorted(os.listdir(os.path.join(ROOT, "frontend"))) \
    if os.path.isdir(os.path.join(ROOT, "frontend")) else []
res["backend_top"] = sorted(os.listdir(os.path.join(ROOT, "backend"))) \
    if os.path.isdir(os.path.join(ROOT, "backend")) else []

# Ndocu 日志按大小
logs = []
nd = os.path.join(ROOT, "Ndocu")
for dp, dn, fn in os.walk(nd):
    for f in fn:
        if f.lower().endswith(".log"):
            fp = os.path.join(dp, f)
            try:
                logs.append({"path": os.path.relpath(fp, ROOT).replace("\\", "/"),
                             "bytes": os.path.getsize(fp)})
            except OSError:
                pass
logs.sort(key=lambda x: -x["bytes"])
res["ndocu_logs"] = logs

# 5) 只读读取现有 git 配置（不改）
res["cfg_global_autocrlf"] = run(["git", "config", "--global", "--get", "core.autocrlf"])
res["cfg_system_autocrlf"] = run(["git", "config", "--system", "--get", "core.autocrlf"])
res["cfg_global_username"] = run(["git", "config", "--global", "--get", "user.name"])
res["cfg_global_initbranch"] = run(["git", "config", "--global", "--get", "init.defaultBranch"])

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "env-check.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=2)

print("collected_at:", res["collected_at"])
print("git_version:", res["git_version"]["code"], res["git_version"]["stdout"])
print("rev_parse_toplevel:", res["rev_parse_toplevel"]["code"], res["rev_parse_toplevel"]["stderr"][:120])
print("git_chain:", json.dumps(res["git_chain"], ensure_ascii=False))
print("root_reparse:", res["root_reparse"])
print("reparse_hits:", rp_hits)
print("subdir_git:", sub_git)
print("special:", json.dumps(res["special_dirs"], ensure_ascii=False))
print("config_files:", res["config_files"])
print("root_files:", res["root_files"])
print("frontend_top:", res["frontend_top"])
print("backend_top:", res["backend_top"])
print("autocrlf g/s:", res["cfg_global_autocrlf"]["stdout"] or "(unset)",
      "/", res["cfg_system_autocrlf"]["stdout"] or "(unset)")
print("logs_top10:", json.dumps(res["ndocu_logs"][:10], ensure_ascii=False))
