# r02 修正副本：仅移除 check_ignore() 内一次无input的 --stdin 无用调用（脚本缺陷，非核验对象漂移）；其余逻辑与 verify_revision01.py 逐行一致
# -*- coding: utf-8 -*-
"""TASK-080 续作01 一次静态清单/忽略边界核验（无 --staged：暂存前检查；
带 --staged：暂存后精确比对，供编排/提交时复用）。只读 git 与项目文件。"""
import hashlib
import json
import os
import subprocess
import sys
import datetime

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
OUT = os.path.join(ROOT, "Ndocu", "evidence", "task-080", "revision-01")
MANIFEST = os.path.join(OUT, "manifest.json")
EXCLUDED = os.path.join(OUT, "excluded.json")
GI_SHA_EXPECT = "7b56964c67ac"  # 续作01追加后前缀

STAGED_MODE = "--staged" in sys.argv

with open(MANIFEST, encoding="utf-8") as fh:
    man = json.load(fh)
with open(EXCLUDED, encoding="utf-8") as fh:
    exc = json.load(fh)
records = man["records"]
man_paths = set(r["path"] for r in records)
man_by_path = {r["path"]: r for r in records}

judged = set(x["path"] for x in exc["judged"])
dynamic_prefix = "Ndocu/evidence/task-080/revision-01/"
dynamic_exact = {"Ndocu/results/TASK-080-result.md"}

checks = []


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=50)
    return p.returncode, p.stdout.decode("utf-8", errors="replace"), p.stderr.decode("utf-8", errors="replace")[:300]


def check(name, ok, detail=""):
    checks.append({"check": name, "ok": bool(ok), "detail": str(detail)[:400]})


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_ignore(paths):
    if not paths:
        return {}
    # r02修正：删除原脚本中一次无input调用 check-ignore --stdin 的无用run()（stdin不关闭导致50s超时），其返回值从未被使用
    p = subprocess.run(["git", "-c", "core.quotepath=off", "check-ignore", "-v", "--stdin"],
                       cwd=ROOT, input=("\n".join(paths) + "\n").encode("utf-8"),
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


# 0) .gitignore 未再变动
gi_sha = sha_file(os.path.join(ROOT, ".gitignore"))
check(".gitignore sha256=续作01追加后", gi_sha.startswith(GI_SHA_EXPECT), gi_sha)

# 1) 仓库状态
code, out, err = run(["git", "rev-parse", "--show-toplevel"])
check("仓库根=项目根", code == 0 and out.strip().replace("\\", "/").rstrip("/")
      == ROOT.replace("\\", "/").rstrip("/"), out.strip() or err)
code, out, err = run(["git", "remote", "-v"])
check("无远端", code == 0 and out.strip() == "", "len=%d" % len(out.strip()))
code, out, err = run(["git", "rev-list", "--all", "--count"])
check("无提交(计数=0)", code == 0 and out.strip() == "0", out.strip() or err)
code, out, err = run(["git", "diff", "--cached", "--name-only"])
if STAGED_MODE:
    staged = set(x for x in out.splitlines() if x.strip())
    check("暂存区=manifest精确相等", staged == man_paths,
          "多=%s 少=%s" % (sorted(staged - man_paths)[:5], sorted(man_paths - staged)[:5]))
    check("暂存区无凭据/079/二进制/动态",
          not (staged & (judged | dynamic_exact)) and not any(s.startswith(dynamic_prefix) for s in staged),
          "交集=%s" % sorted(staged & (judged | dynamic_exact))[:5])
else:
    check("未暂存", code == 0 and out.strip() == "", "staged=%d" % len(out.strip().splitlines()))

# 2) 忽略正例（两份凭据证据 + 079真实文件 + 常规生成/私有路径）
old_cand = json.load(open(os.path.join(ROOT, "Ndocu", "evidence", "task-080", "candidates.json"), encoding="utf-8"))
dyn079 = [r["path"] for r in old_cand["records"] if r["status"] == "dynamic_079"]
must_ignore = [
    "Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json",
    "Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json",
    "Ndocu/evidence/task-079/20260923T1456-wbC1/precheck-blocked.log",
] + dyn079[:2] + [
    ".env", "config/local.env", "backend/.venv/pyvenv.cfg",
    "frontend/dist/index.html", ".workbuddy/memory/MEMORY.md",
]
got = check_ignore(must_ignore)
missing = [p for p in must_ignore if p not in got]
check("凭据证据与079证据均被忽略", not missing, "未覆盖=%s" % missing)

# 3) 忽略反例（必要源码/锁/迁移004/样例/079卡与结果/动态结果文档不得误排除）
must_keep = ["README.md", "backend/app/main.py",
             "backend/migrations/004_activities_time_budget.sql",
             "backend/requirements.lock", "frontend/package-lock.json",
             "config/local.env.example", "docu/PROJECT_EXECUTE_STATE.MD",
             "Ndocu/tasks/TASK-079.md", "Ndocu/results/TASK-079-result.md",
             "Ndocu/results/TASK-080-result.md"]
wrongly = check_ignore(must_keep)
check("必要源码/锁/004/样例未误排除", not wrongly,
      "误排除=%s" % [(k, v) for k, v in wrongly.items()][:5])

# 4) manifest 完整性：逐条 sha256 复算 + 004 在案
bad_hash = []
for r in records:
    fp = os.path.join(ROOT, r["path"])
    if not os.path.isfile(fp):
        bad_hash.append((r["path"], "文件缺失"))
        continue
    if sha_file(fp) != r["sha256"]:
        bad_hash.append((r["path"], "hash漂移"))
check("manifest逐条hash一致(%d条)" % len(records), not bad_hash, "异常=%s" % bad_hash[:5])
m004 = man_by_path.get("backend/migrations/004_activities_time_budget.sql")
check("迁移004在manifest且hash在案", bool(m004), "004=%s" % (m004 or {}).get("sha256", "缺失"))

# 5) status -uall 与 manifest/排除集精确一致（未暂存模式）
if not STAGED_MODE:
    ps = subprocess.run(["git", "-c", "core.quotepath=off", "status", "--porcelain", "-uall"],
                        cwd=ROOT, capture_output=True, timeout=50)
    lines = [x for x in ps.stdout.decode("utf-8", errors="replace").splitlines() if x.strip()]
    non_unt = [x for x in lines if not x.startswith("??")]
    status_paths = set(x[3:].replace("\\", "/") for x in lines)
    # 判定排除+动态中被忽略规则覆盖者不出现在status（如079目录下的.bin同时二项成立）
    excluded_universe = judged | dynamic_exact | set(
        p for p in status_paths if p.startswith(dynamic_prefix))
    ignored_of_excluded = set(check_ignore(sorted(excluded_universe - dynamic_exact)))
    expected_in_status = excluded_universe - ignored_of_excluded
    extra = status_paths - man_paths
    unexplained = [p for p in extra
                   if not (p in judged or p in dynamic_exact or p.startswith(dynamic_prefix))]
    check("status全部untracked", not non_unt, "非untracked=%d" % len(non_unt))
    check("status−manifest逐项均有排除原因(判定/动态)", not unexplained,
          "无原因项=%s" % unexplained[:5])
    check("排除集中未被忽略者均出现在status",
          expected_in_status <= status_paths,
          "应现未现=%s" % sorted(expected_in_status - status_paths)[:5])
    check("manifest⊆status", man_paths <= status_paths,
          "manifest有status无=%s" % sorted(man_paths - status_paths)[:5])

result = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
          "mode": "staged" if STAGED_MODE else "pre-stage",
          "all_passed": all(c["ok"] for c in checks), "checks": checks}
suffix = "-staged" if STAGED_MODE else ""
with open(os.path.join(OUT, "revision-check%s.json" % suffix), "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
for c in checks:
    print(("PASS" if c["ok"] else "FAIL"), "|", c["check"], "|", str(c["detail"])[:180])
print("ALL_PASSED:", result["all_passed"])
