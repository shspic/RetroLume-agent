# -*- coding: utf-8 -*-
"""TASK-080 一致性核验（修正版）：仓库根/无远端/无提交/无暂存、忽略边界正反例、
候选与 git status -uall 一致性、局部配置白名单。只读 git 与项目文件。
check-ignore 以字节模式送 stdin（规避Windows text模式\n→\r\n翻译），
-v 输出按 <rule>\t<path> 解析。"""
import json
import os
import subprocess
import datetime

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
OUT = os.path.join(ROOT, "Ndocu", "evidence", "task-080")

with open(os.path.join(OUT, "candidates.json"), encoding="utf-8") as fh:
    cands = json.load(fh)
records = cands["records"]

checks = []


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       errors="replace", timeout=50)
    return {"cmd": " ".join(cmd), "code": p.returncode,
            "stdout": (p.stdout or "").strip()[:4000],
            "stderr": (p.stderr or "").strip()[:400]}


def check_ignore(paths):
    """返回 {path: rule}：被忽略的路径及其规则（字节模式输入，防\r污染）。"""
    if not paths:
        return {}
    p = subprocess.run(["git", "-c", "core.quotepath=off", "check-ignore", "-v", "--stdin"],
                       cwd=ROOT,
                       input=("\n".join(paths) + "\n").encode("utf-8"),
                       capture_output=True, timeout=50)
    got = {}
    for line in p.stdout.decode("utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        if "\t" in line:
            rule, _, pathpart = line.partition("\t")
            got[pathpart.strip().strip('"')] = rule
        else:
            got[line.strip()] = "?"
    return got


def check(name, ok, detail):
    checks.append({"check": name, "ok": bool(ok), "detail": str(detail)[:400]})


# 1) 仓库根与状态
r = run(["git", "rev-parse", "--show-toplevel"])
check("仓库根=项目根", r["code"] == 0 and r["stdout"].replace("\\", "/").lower().rstrip("/")
      == ROOT.replace("\\", "/").lower().rstrip("/"), r["stdout"] or r["stderr"])
r = run(["git", "rev-parse", "--is-inside-work-tree"])
check("工作树内", r["stdout"] == "true", r["stdout"])
r = run(["git", "remote", "-v"])
check("无远端", r["code"] == 0 and r["stdout"] == "", "stdout_len=%d" % len(r["stdout"]))
r = run(["git", "rev-list", "--all", "--count"])
check("无提交(计数=0)", r["code"] == 0 and r["stdout"] == "0", r["stdout"] or r["stderr"])
r = run(["git", "diff", "--cached", "--name-only"])
check("无暂存", r["code"] == 0 and r["stdout"] == "", "staged=%d" % len(r["stdout"].splitlines()))

# 2) status -uall 全为 untracked；与候选清单记录数一致
# 字节模式读取并关闭quotepath，避免中文路径被转成八进制引号串且输出被截断
ps = subprocess.run(["git", "-c", "core.quotepath=off", "status", "--porcelain", "-uall"],
                    cwd=ROOT, capture_output=True, timeout=50)
lines = [x for x in ps.stdout.decode("utf-8", errors="replace").splitlines() if x.strip()]
non_untracked = [x for x in lines if not x.startswith("??")]
status_paths = set(x[3:].replace("\\", "/") for x in lines)
by_top = {}
for x in lines:
    top = x[3:].replace("\\", "/").split("/")[0]
    by_top[top] = by_top.get(top, 0) + 1
check("status全部为untracked(??)", len(non_untracked) == 0,
      "非untracked行=%d" % len(non_untracked))
check("untracked总数=扫描记录总数",
      len(lines) == cands["summary"]["total_files_seen"],
      "status=%d, records=%d" % (len(lines), cands["summary"]["total_files_seen"]))
record_paths = set(rec["path"] for rec in records)
check("status路径与扫描记录路径一致",
      status_paths == record_paths,
      "仅status有=%s 仅记录有=%s" % (sorted(status_paths - record_paths)[:3],
                                    sorted(record_paths - status_paths)[:3]))

# 3) 必须被忽略的正例
must_ignore = [
    "backend/.venv/pyvenv.cfg",
    "frontend/node_modules/sample/index.js",
    "frontend/dist/index.html",
    "backend/app/__pycache__/sample.pyc",
    ".env", ".env.local",
    "config/database.local.json", "config/database.env", "config/local.env",
    ".workbuddy/memory/MEMORY.md",
    "Ndocu/evidence/task-065/task065-run1-20260921T0136Z/synthetic-runtime/edge-profile/CURRENT",
]
got = check_ignore(must_ignore)
missing = [p for p in must_ignore if p not in got]
check("敏感/生成路径均被忽略", not missing, "未覆盖=%s" % missing)

# 4) 不得被忽略的反例（固定关键文件 + 按类别抽样候选）
by_cat = {}
for rec in records:
    if rec["status"] == "candidate":
        by_cat.setdefault(rec["category"], rec["path"])
must_keep = ["README.md", "backend/app/main.py", "docu/PROJECT_ARCHITECTURE.MD",
             "config/local.env.example", "frontend/package.json",
             "Ndocu/tasks/TASK-079.md", "deploy/start_local.py",
             by_cat.get("工程级测试/看门狗", "tests/task057_watchdog.mjs"),
             by_cat.get("实验材料", ""), by_cat.get("数据库迁移", ""),
             by_cat.get("依赖清单/锁", "")]
must_keep = [x for x in must_keep if x]
wrongly = check_ignore(must_keep)
check("关键候选源文件无误排除", not wrongly,
      "误排除=%s" % [(k, v) for k, v in wrongly.items()][:5])

# 5) 候选无 check-ignore 冲突（与扫描结果交叉核对）
check("候选check-ignore冲突=0", cands["summary"]["check_ignore_conflicts"] == 0,
      "conflicts=%s" % cands["check_ignore_conflicts"][:3])

# 6) 局部配置白名单
r = run(["git", "config", "--local", "--list"])
local_cfg = r["stdout"]
check("局部config仅含预期键且autocrlf=false",
      "core.autocrlf=false" in local_cfg
      and "user.name" not in local_cfg and "user.email" not in local_cfg
      and "remote." not in local_cfg,
      local_cfg.replace("\n", " | "))
r = run(["git", "config", "--global", "--get", "user.name"])
check("global身份存在性登记(不改动)", r["code"] in (0, 1),
      "global user.name %s" % ("已配置" if r["code"] == 0 and r["stdout"] else "未配置"))

result = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
          "all_passed": all(c["ok"] for c in checks), "checks": checks,
          "untracked_by_top": by_top}
with open(os.path.join(OUT, "verify-log.json"), "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)

for c in checks:
    print(("PASS" if c["ok"] else "FAIL"), "|", c["check"], "|", str(c["detail"])[:200])
print("ALL_PASSED:", result["all_passed"])
print("untracked_by_top:", json.dumps(by_top, ensure_ascii=False))
