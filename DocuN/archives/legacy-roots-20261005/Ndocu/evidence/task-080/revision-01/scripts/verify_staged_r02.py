# -*- coding: utf-8 -*-
"""TASK-080 续作02 暂存后核验（有限脚本，仅本轮使用）：
1) git diff --cached --name-only -z 字节路径：暂存集合与 manifest 599 条精确相等；
2) git ls-files -s -z 取索引 blob OID，git cat-file --batch 读取全部 blob 原字节，
   逐条 SHA256 对照 manifest（覆盖过滤器/换行变换差异，不只核工作树）。
只读 git 与项目文件，不写入索引。"""
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
records = man["records"]
man_by_path = {r["path"]: r["sha256"] for r in records}

checks = []

def check(name, ok, detail=""):
    checks.append({"check": name, "ok": bool(ok), "detail": str(detail)[:500]})

# 1) 暂存路径集合（-z 字节，NUL 分隔）
p = subprocess.run(["git", "-C", ROOT, "-c", "core.quotepath=off", "diff", "--cached", "--name-only", "-z"],
                   capture_output=True)
staged_paths = [x for x in p.stdout.split(b"\0") if x]
staged_set = set(x.decode("utf-8") for x in staged_paths)  # bytes→str 后与 manifest 比较
man_set = set(man_by_path)
check("暂存路径数=599", len(staged_paths) == 599 and len(staged_set) == 599,
      "count=%d unique=%d" % (len(staged_paths), len(staged_set)))
multi = sorted(staged_set - man_set)
missing = sorted(man_set - staged_set)
check("暂存集合与manifest精确相等", not multi and not missing,
      "多=%s 少=%s" % ([x.decode('utf-8', 'replace') for x in multi[:5]], missing[:5]))

# 2) 索引 blob 原字节 SHA256 对照 manifest
p2 = subprocess.run(["git", "-C", ROOT, "ls-files", "-s", "-z"], capture_output=True)
entries = [x for x in p2.stdout.split(b"\0") if x]
oid_by_path = {}
for e in entries:
    parts = e.decode("utf-8", "surrogateescape").split("\t", 1)
    meta = parts[0].split()
    oid_by_path[parts[1]] = meta[1]
check("ls-files条目数=599", len(oid_by_path) == 599, "count=%d" % len(oid_by_path))

batch = subprocess.Popen(["git", "-C", ROOT, "cat-file", "--batch"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
blob_sha = {}
def read_exact(n):
    buf = b""
    while len(buf) < n:
        ch = batch.stdout.read(n - len(buf))
        if not ch:
            raise IOError("cat-file stream ended early")
        buf += ch
    return buf
try:
    for path, oid in oid_by_path.items():
        batch.stdin.write(oid.encode() + b"\n")
        batch.stdin.flush()
        header = b""
        while not header.endswith(b"\n"):
            header += batch.stdout.read(1)
        hfields = header.decode().split()
        assert hfields[1] == "blob", "unexpected type: %s" % header
        size = int(hfields[2])
        data = read_exact(size)
        tail = read_exact(1)
        assert tail == b"\n", "missing trailing LF"
        blob_sha[path] = hashlib.sha256(data).hexdigest()
finally:
    batch.stdin.close()
    batch.wait(timeout=30)

bad = []
for path, exp in man_by_path.items():
    got = blob_sha.get(path)
    if got is None:
        bad.append((path, "blob缺失"))
    elif got != exp:
        bad.append((path, "hash漂移 got=%s" % got))
check("索引blob字节SHA256逐条=manifest(%d条)" % len(man_by_path), not bad, "异常=%s" % bad[:5])

result = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
          "mode": "staged-r02", "all_passed": all(c["ok"] for c in checks), "checks": checks}
with open(os.path.join(OUT, "staged-check-r02.json"), "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
for c in checks:
    print(("PASS" if c["ok"] else "FAIL"), "|", c["check"], "|", str(c["detail"])[:200])
print("ALL_PASSED:", result["all_passed"])
