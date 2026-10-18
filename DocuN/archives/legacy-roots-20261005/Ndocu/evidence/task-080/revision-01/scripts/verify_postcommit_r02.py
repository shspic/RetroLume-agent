# -*- coding: utf-8 -*-
"""TASK-080 续作02 提交后核验（有限脚本，仅本轮使用）：
HEAD 树路径恰 599 且与 manifest 精确相等；HEAD 树 blob 原字节 SHA256 逐项对照 manifest；
仅一个根提交、分支 main、无远端、暂存区空、已跟踪工作树无变化。只读 git 与项目文件。"""
import hashlib
import json
import os
import subprocess
import datetime

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
OUT = os.path.join(ROOT, "Ndocu", "evidence", "task-080", "revision-01")
MANIFEST = os.path.join(OUT, "manifest.json")

with open(MANIFEST, encoding="utf-8") as fh:
    man = json.load(fh)
man_by_path = {r["path"]: r["sha256"] for r in man["records"]}

checks = []
def check(name, ok, detail=""):
    checks.append({"check": name, "ok": bool(ok), "detail": str(detail)[:500]})

def g(args, binary=False):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    return p.returncode, (p.stdout if binary else p.stdout.decode("utf-8", "replace"))

# 1) HEAD / 分支 / 提交数 / 远端
rc, out = g(["rev-parse", "HEAD"]); head = out.strip()
rc2, out2 = g(["rev-parse", "HEAD^{tree}"]); tree = out2.strip()
rc3, out3 = g(["branch", "--show-current"]); branch = out3.strip()
rc4, out4 = g(["rev-list", "--all", "--count"])
rc5, out5 = g(["remote", "-v"])
rc6, out6 = g(["log", "--oneline", "--all"])
check("HEAD与tree已取得", rc == 0 and rc2 == 0, "HEAD=%s tree=%s" % (head[:12], tree[:12]))
check("分支=main", rc3 == 0 and branch == "main", branch)
check("全仓库提交数=1(仅根提交)", rc4 == 0 and out4.strip() == "1", "count=%s" % out4.strip())
check("无远端", rc5 == 0 and out5.strip() == "", "len=%d" % len(out5.strip()))
check("log恰一条(root-commit)", rc6 == 0 and len(out6.strip().splitlines()) == 1, out6.strip()[:80])

# 2) HEAD 树路径集合（-z 字节）
rc, out = g(["ls-tree", "-r", "-z", "--name-only", "HEAD"], binary=True)
tree_paths = [x for x in out.split(b"\0") if x]
tree_set = set(x.decode("utf-8") for x in tree_paths)
check("HEAD树路径数=599", len(tree_paths) == 599 and len(tree_set) == 599,
      "count=%d unique=%d" % (len(tree_paths), len(tree_set)))
multi = sorted(tree_set - set(man_by_path)); missing = sorted(set(man_by_path) - tree_set)
check("HEAD树集合与manifest精确相等", not multi and not missing,
      "多=%s 少=%s" % (multi[:5], missing[:5]))

# 3) HEAD 树 blob 原字节 SHA256 对照 manifest（cat-file --batch 批量读取）
rc, out = g(["ls-tree", "-r", "-z", "HEAD"], binary=True)
oid_by_path = {}
for e in out.split(b"\0"):
    if not e: continue
    meta, _, path = e.decode("utf-8", "surrogateescape").partition("\t")
    fields = meta.split()
    mode, otype, oid = fields[0], fields[1], fields[2]
    assert otype == "blob", "non-blob in tree: %s %s" % (otype, path)
    oid_by_path[path] = oid
check("ls-tree blob条目=599", len(oid_by_path) == 599, "count=%d" % len(oid_by_path))

batch = subprocess.Popen(["git", "-C", ROOT, "cat-file", "--batch"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
def read_exact(n):
    buf = b""
    while len(buf) < n:
        ch = batch.stdout.read(n - len(buf))
        if not ch: raise IOError("cat-file stream ended early")
        buf += ch
    return buf
blob_sha = {}
try:
    for path, oid in oid_by_path.items():
        batch.stdin.write(oid.encode() + b"\n"); batch.stdin.flush()
        header = b""
        while not header.endswith(b"\n"):
            header += batch.stdout.read(1)
        hf = header.decode().split()
        assert hf[1] == "blob", header
        data = read_exact(int(hf[2]))
        assert read_exact(1) == b"\n"
        blob_sha[path] = hashlib.sha256(data).hexdigest()
finally:
    batch.stdin.close(); batch.wait(timeout=30)
bad = [(p, "缺失" if blob_sha.get(p) is None else "漂移") for p in man_by_path
       if blob_sha.get(p) != man_by_path[p]]
check("HEAD树blob字节SHA256逐条=manifest(%d条)" % len(man_by_path), not bad, "异常=%s" % bad[:5])

# 4) 暂存区空 + 已跟踪工作树无变化
rc, out = g(["-c", "core.quotepath=off", "status", "--porcelain", "-uall"])
lines = [x for x in out.splitlines() if x.strip()]
tracked_dirty = [x for x in lines if not x.startswith("??")]
check("暂存区空且已跟踪工作树无变化", not tracked_dirty, "非untracked=%s" % tracked_dirty[:5])

# 5) 剩余 untracked 逐项归类计数（有理由即可，不删）
judged = set()
with open(os.path.join(OUT, "excluded.json"), encoding="utf-8") as fh:
    judged = set(x["path"] for x in json.load(fh)["judged"])
untracked = set(x[3:].replace("\\", "/") for x in lines if x.startswith("??"))
reason_judged = untracked & judged
reason_dynamic = set(p for p in untracked if p.startswith("Ndocu/evidence/task-080/revision-01/"))
reason_result = {"Ndocu/results/TASK-080-result.md"} & untracked
reason_r02new = set(p for p in untracked if p.startswith("Ndocu/results/TASK-080-"))
unexplained = untracked - reason_judged - reason_dynamic - reason_r02new
check("剩余untracked逐项有归类理由", not unexplained,
      "untracked=%d judged=%d dynamic_rev01=%d r02结果=%d 无理由=%s" % (
          len(untracked), len(reason_judged), len(reason_dynamic), len(reason_r02new), sorted(unexplained)[:5]))

result = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
          "head": head, "tree": tree, "branch": branch,
          "mode": "post-commit-r02", "all_passed": all(c["ok"] for c in checks), "checks": checks}
with open(os.path.join(OUT, "post-commit-check-r02.json"), "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
for c in checks:
    print(("PASS" if c["ok"] else "FAIL"), "|", c["check"], "|", str(c["detail"])[:200])
print("HEAD:", head)
print("TREE:", tree)
print("ALL_PASSED:", result["all_passed"])
