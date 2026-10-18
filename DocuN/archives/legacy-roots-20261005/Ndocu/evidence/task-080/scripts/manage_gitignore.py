# -*- coding: utf-8 -*-
"""TASK-080 .gitignore 维护：保留原规则字节不变，仅追加按实际发现的补充规则。
留改前副本、SHA-256、unified diff。"""
import difflib
import hashlib
import json
import os
import datetime

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
OUT = os.path.join(ROOT, "Ndocu", "evidence", "task-080")
GI = os.path.join(ROOT, ".gitignore")

ADD_LF = (
    "\n"
    "# --- TASK-080 / R-074 2026-09-23 补充（按实际发现，原规则未改动） ---\n"
    "# 本地私有运行配置（约定占位样例见 config/local.env.example）\n"
    "config/local.env\n"
    "# IDE/Agent 会话、本地记忆与凭据\n"
    ".workbuddy/\n"
    "# 浏览器/应用运行时合成快照（含 profile 二进制，可由脚本重建；原位置 Ndocu/evidence/）\n"
    "synthetic-runtime/\n"
)
ADD_CRLF = ADD_LF.replace("\n", "\r\n")


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


before = open(GI, "rb").read()
before_hash = sha_bytes(before)
with open(os.path.join(OUT, "gitignore-before.txt"), "wb") as fh:
    fh.write(before)

had_crlf = b"\r\n" in before
addition = (ADD_CRLF if had_crlf else ADD_LF).encode("utf-8")
after = before + addition
with open(GI, "wb") as fh:
    fh.write(after)
after_hash = sha_bytes(open(GI, "rb").read())

b_text = before.decode("utf-8")
a_text = after.decode("utf-8")
diff = "".join(difflib.unified_diff(
    b_text.splitlines(keepends=True), a_text.splitlines(keepends=True),
    fromfile=".gitignore (before, sha256=" + before_hash[:16] + ")",
    tofile=".gitignore (after, sha256=" + after_hash[:16] + ")"))
with open(os.path.join(OUT, "gitignore-diff.txt"), "w", encoding="utf-8", newline="") as fh:
    fh.write(diff)

rec = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "before_sha256": before_hash, "after_sha256": after_hash,
       "before_bytes": len(before), "after_bytes": len(after),
       "crlf_preserved": had_crlf,
       "diff_file": "Ndocu/evidence/task-080/gitignore-diff.txt"}
with open(os.path.join(OUT, "gitignore-change.json"), "w", encoding="utf-8") as fh:
    json.dump(rec, fh, ensure_ascii=False, indent=2)
print(json.dumps(rec, ensure_ascii=False, indent=1))
print("--- diff ---")
print(diff)
