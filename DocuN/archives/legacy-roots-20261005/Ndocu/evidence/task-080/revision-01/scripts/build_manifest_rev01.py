# -*- coding: utf-8 -*-
"""TASK-080 续作01：追加精确忽略规则 + 重建全量首提交 manifest + literal pathspec。
- 先核对当前 .gitignore sha256 与上轮一致（63cd46bb…01fe）再纯追加三条根相对规则；
- 全树重扫（不复用旧记录），check-ignore 权威判定（字节模式 stdin，防 \\r 污染）；
- 候选全量 SHA256；本轮动态产物（revision-01/ 与 TASK-080-result.md 当前版）放独立排除列表；
- 与旧候选清单（Ndocu/evidence/task-080/candidates.json）做集合对比，记录漂移；
- 敏感复检只记路径/模式/裁定，不回显秘密值。
只读项目文件；输出仅写 Ndocu/evidence/task-080/revision-01/ 与根 .gitignore。"""
import difflib
import hashlib
import json
import os
import re
import subprocess
import datetime

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
OUT = os.path.join(ROOT, "Ndocu", "evidence", "task-080", "revision-01")
OLD_CAND = os.path.join(ROOT, "Ndocu", "evidence", "task-080", "candidates.json")
GI = os.path.join(ROOT, ".gitignore")
EXPECTED_BEFORE_SHA = "63cd46bb84701d3db560ca9513be13d857546a5616517d898482c9ce932701fe"

MAX_FILE_BYTES = 1_000_000
MAX_SENSITIVE_SCAN_BYTES = 1_000_000

DYNAMIC_PREFIXES = ("Ndocu/evidence/task-080/revision-01/",)
DYNAMIC_EXACT = ("Ndocu/results/TASK-080-result.md",)

PRUNE_DIRS = {".git", ".workbuddy", "node_modules", ".venv", "__pycache__", "dist",
              "synthetic-runtime", ".pytest_cache", ".ruff_cache", ".cache",
              ".vscode", ".idea"}
DIR_EXCLUDE_REASON = {
    ".git": "git内部目录（不纳管）",
    ".workbuddy": "IDE/Agent会话与本地记忆（忽略规则 .workbuddy/）",
    "node_modules": "依赖目录（忽略规则 node_modules/）",
    ".venv": "虚拟环境（忽略规则 .venv/）",
    "__pycache__": "Python字节码缓存（忽略规则 __pycache__/）",
    "dist": "前端构建输出（忽略规则 dist/）",
    "synthetic-runtime": "运行时合成快照含浏览器profile二进制（忽略规则 synthetic-runtime/，原位置保留不删）",
}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
              ".7z", ".gz", ".pyc", ".pyo", ".pyd", ".map", ".bcmap", ".woff",
              ".woff2", ".ttf", ".eot", ".otf", ".exe", ".dll", ".bin", ".wasm",
              ".db", ".sqlite", ".sqlite3", ".mp4", ".mp3", ".wav"}
TEXT_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".md",
            ".sql", ".txt", ".cmd", ".ps1", ".example", ".yml", ".yaml", ".toml",
            ".lock", ".html", ".css", ".env", ".cfg", ".ini", ".svg"}
SECRET_PATTERNS = [
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("openai_like_key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("cred_url", re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|redis|mongodb|amqp)://[^\s'\"<>]+:[^\s'\"<>@]+@")),
    ("assign_secret", re.compile(r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|auth[_-]?token|password|passwd)\b[\"']?\s*[:=][\"']?\s*[^\"'\s]{8,}")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-_.]{20,}")),
]
# 沿用首轮人工裁定（本轮对仍为候选者逐条复核命中模式是否一致）
ADJUDICATION = [
    {"files": ["tests/task054_pdf_materials_integration.mjs",
               "Ndocu/evidence/task-057/task054-original-script-copy.mjs",
               "Ndocu/evidence/task-059/task054-pre-059-script-copy.mjs",
               "Ndocu/evidence/task-061/task054-pre-061-script-copy.mjs",
               "Ndocu/evidence/task-064/pre-task054_pdf_materials_integration.mjs",
               "Ndocu/evidence/task-066/pre-task054_pdf_materials_integration.mjs"],
     "patterns": ["cred_url"],
     "verdict": "良性，保留候选",
     "rationale": "指向 127.0.0.1 本地合成测试库的固定测试标识符（与任务同名的占位用户/口令），非真实凭据"},
    {"files": ["Ndocu/evidence/task-073/20260921T1254-wbA1/run_task073.py",
               "Ndocu/evidence/task-074/20260921T1319-wbB1/run_task074.py"],
     "patterns": ["cred_url"],
     "verdict": "良性，保留候选",
     "rationale": "DSN 为运行期生成拼接的模板字符串，脚本内无硬编码口令"},
    {"files": ["Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json",
               "Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json"],
     "patterns": ["cred_url"],
     "verdict": "凭据值文件，续作01起按根相对忽略规则永久排除原件纳管（编排裁定），本地原件保留不改",
     "rationale": "含运行期生成的 db_password 与 DSN 实际值；不以容器据称销毁作为公开依据"},
    {"files": ["backend/app/capabilities/contracts.py",
               "backend/app/capabilities/gateway.py"],
     "patterns": ["assign_secret"],
     "verdict": "良性，保留候选",
     "rationale": "Pydantic SecretStr 字段声明与 get_secret_value() 取值调用，无硬编码密钥值"},
]
ADJ_BY_PATH = {}
for a in ADJUDICATION:
    for f in a["files"]:
        ADJ_BY_PATH[f] = a


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def category_of(rel):
    p = rel.replace("\\", "/")
    if p == ".gitignore":
        return "工程配置（忽略规则）"
    if p == "AGENTS.md":
        return "根入口规则"
    if p == "README.md":
        return "根入口说明"
    if p == "start-local.cmd":
        return "根启动入口"
    if p.startswith("backend/app/"):
        return "后端源代码"
    if p.startswith("backend/migrations/"):
        return "数据库迁移"
    if p in ("backend/requirements.txt", "backend/requirements.lock"):
        return "依赖清单/锁"
    if p.startswith("backend/tests/"):
        return "后端测试"
    if p == "frontend/package-lock.json":
        return "前端依赖锁"
    if p == "frontend/package.json":
        return "前端依赖清单"
    if p.startswith("frontend/src/"):
        return "前端源代码"
    if p in ("frontend/index.html", "frontend/tsconfig.json", "frontend/vite.config.js"):
        return "前端配置/入口"
    if p.startswith("deploy/"):
        return "部署脚本"
    if p.startswith("tests/"):
        return "工程级测试/看门狗"
    if p.startswith("docu/"):
        return "正式文档"
    if p == "config/local.env.example":
        return "样例配置（脱敏占位）"
    if p.startswith("config/"):
        return "配置"
    if p.startswith("Ndocu/tasks/"):
        return "任务卡（合同）"
    if p.startswith("Ndocu/results/"):
        return "任务结果"
    if p.startswith("Ndocu/evidence/"):
        return "任务证据"
    if p.startswith("Ndocu/handoffs/"):
        return "交接"
    if p.startswith("Ndocu/archives/"):
        return "归档快照（规则历史副本）"
    if p.startswith("Ndocu/prompts/"):
        return "阶段提示词副本"
    if p.startswith("Ndocu/"):
        return "Ndocu其他"
    if p.startswith("evidence/"):
        return "顶层历史证据"
    if p.startswith("spikes/"):
        return "实验材料"
    return "其他"


# ---------- 1) .gitignore 纯追加（根相对精确规则） ----------
before = open(GI, "rb").read()
before_sha = sha_file(GI)
if before_sha != EXPECTED_BEFORE_SHA:
    raise SystemExit("FATAL: .gitignore 当前 sha256=%s 与预期 %s 不符，停止交回" % (before_sha, EXPECTED_BEFORE_SHA))

ADD_LF = (
    "\n"
    "# --- TASK-080 续作01 2026-09-23 追加（根相对精确规则；原规则未改动） ---\n"
    "# 073/074 合成容器证据含运行期生成口令值：编排裁定永久排除原件纳管，本地原件保留不改，\n"
    "# 不以容器据称销毁作为公开依据\n"
    "/Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json\n"
    "/Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json\n"
    "# 079 证据：仅首提交整体暂缓追踪（原始文件保留）；未来选择性纳管须另查敏感信息并调整本规则\n"
    "/Ndocu/evidence/task-079/\n"
)
ADD = (ADD_LF.replace("\n", "\r\n") if b"\r\n" in before else ADD_LF).encode("utf-8")
after = before + ADD
with open(GI, "wb") as fh:
    fh.write(after)
after_sha = sha_file(GI)
b_text, a_text = before.decode("utf-8"), after.decode("utf-8")
diff_text = "".join(difflib.unified_diff(
    b_text.splitlines(keepends=True), a_text.splitlines(keepends=True),
    fromfile=".gitignore (before, sha256=" + before_sha[:16] + ")",
    tofile=".gitignore (after, sha256=" + after_sha[:16] + ")"))
gi_rec = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
          "before_sha256": before_sha, "after_sha256": after_sha,
          "before_bytes": len(before), "after_bytes": len(after),
          "added_rules": ["/Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json",
                          "/Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json",
                          "/Ndocu/evidence/task-079/"]}
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "gitignore-change-rev01.json"), "w", encoding="utf-8") as fh:
    json.dump(gi_rec, fh, ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "gitignore-diff-rev01.txt"), "w", encoding="utf-8", newline="") as fh:
    fh.write(diff_text)
print("gitignore:", before_sha[:12], "->", after_sha[:12], "(纯追加3条根相对规则)")

# ---------- 2) 全树重扫 ----------
records = []          # candidate
excl_rule = []        # ignored by .gitignore
excl_judged = []      # binary/oversized
dynamic = []          # 本轮动态产物
dir_exclusions = []
all_paths = []
for dp, dn, fn in os.walk(ROOT):
    rel_dir = os.path.relpath(dp, ROOT)
    if rel_dir == ".":
        rel_dir = ""
    keep = []
    for d in sorted(dn):
        if d in PRUNE_DIRS:
            dir_exclusions.append({"dir": (rel_dir + "/" + d).lstrip("/") if rel_dir else d,
                                   "reason": DIR_EXCLUDE_REASON.get(d, "目录排除")})
        else:
            keep.append(d)
    dn[:] = keep
    for f in sorted(fn):
        full = os.path.join(dp, f)
        rel = os.path.relpath(full, ROOT).replace("\\", "/")
        try:
            size = os.path.getsize(full)
        except OSError:
            size = -1
        all_paths.append(rel)
        ext = os.path.splitext(f)[1].lower()
        if ext in BINARY_EXT:
            excl_judged.append({"path": rel, "bytes": size, "category": category_of(rel),
                                "reason": "二进制/生成物(%s)，非候选维持不纳管，不整目录忽略" % ext})
        elif size > MAX_FILE_BYTES:
            excl_judged.append({"path": rel, "bytes": size, "category": category_of(rel),
                                "reason": "超大文件(>1MB)"})
        elif any(rel.startswith(x) for x in DYNAMIC_PREFIXES) or rel in DYNAMIC_EXACT:
            dynamic.append(rel)
        else:
            records.append({"path": rel, "bytes": size, "category": category_of(rel)})

# check-ignore 权威判定（一次批量，字节输入）
p = subprocess.run(["git", "-c", "core.quotepath=off", "check-ignore", "-v", "--stdin"],
                   cwd=ROOT, input=("\n".join(all_paths) + "\n").encode("utf-8"),
                   capture_output=True, timeout=50)
ignored_map = {}
for line in p.stdout.decode("utf-8", errors="replace").splitlines():
    if not line.strip():
        continue
    if "\t" in line:
        rule, _, pathpart = line.partition("\t")
        ignored_map[pathpart.strip().strip('"')] = rule
    else:
        ignored_map[line.strip()] = "?"

for rec in list(records):
    rule = ignored_map.get(rec["path"])
    if rule:
        records.remove(rec)
        if "task-079/" in rule:
            group = "079证据（首提交整体暂缓追踪，原始文件保留）"
        elif "task-073" in rule or "task-074" in rule:
            group = "073/074凭据证据（编排裁定永久排除原件纳管，原件保留不改）"
        else:
            group = "常规忽略规则命中"
        excl_rule.append({"path": rec["path"], "bytes": rec["bytes"],
                          "category": rec["category"], "group": group, "rule": rule})
        continue
    rec["sha256"] = sha_file(os.path.join(ROOT, rec["path"]))

# ---------- 3) 敏感复检（候选文本） ----------
sensitive = []
uncertain = []
for rec in records:
    ext = os.path.splitext(rec["path"])[1].lower()
    if ext not in TEXT_EXT or rec["bytes"] > MAX_SENSITIVE_SCAN_BYTES or rec["bytes"] < 0:
        continue
    try:
        text = open(os.path.join(ROOT, rec["path"]), "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        continue
    hits = [n for n, pat in SECRET_PATTERNS if pat.search(text)]
    if not hits:
        continue
    rec["secret_pattern_names"] = hits
    adj = ADJ_BY_PATH.get(rec["path"])
    if adj and sorted(adj["patterns"]) == sorted(hits):
        entry = {"path": rec["path"], "patterns": hits, "status": "candidate",
                 "verdict": adj["verdict"], "rationale": adj["rationale"], "prior": True}
    elif adj:
        entry = {"path": rec["path"], "patterns": hits, "status": "excluded_uncertain",
                 "verdict": "命中模式与首轮裁定不一致，排除并回报", "rationale": "", "prior": True}
        rec["status"] = "excluded_uncertain"
        uncertain.append(entry)
    else:
        entry = {"path": rec["path"], "patterns": hits, "status": "excluded_uncertain",
                 "verdict": "首轮未裁定的新命中，排除并回报", "rationale": "", "prior": False}
        rec["status"] = "excluded_uncertain"
        uncertain.append(entry)
    sensitive.append(entry)
for u in uncertain:
    records = [r for r in records if r["path"] != u["path"]]

# ---------- 4) 与旧清单对比 ----------
old = json.load(open(OLD_CAND, encoding="utf-8"))
old_paths = set(r["path"] for r in old["records"] if r["status"] == "candidate")
new_paths = set(r["path"] for r in records)
added = sorted(new_paths - old_paths)
removed = sorted(old_paths - new_paths)

# ---------- 5) 汇总输出 ----------
cats = {}
for r in records:
    cats[r["category"]] = cats.get(r["category"], 0) + 1
summary = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "manifest_candidates": len(records),
           "excluded_by_rule": len(excl_rule),
           "excluded_judged": len(excl_judged),
           "dynamic_rev01": len(dynamic),
           "dir_level_exclusions": len(dir_exclusions),
           "sensitive_hits_total": len(sensitive),
           "uncertain_excluded": len(uncertain),
           "added_vs_old": len(added), "removed_vs_old": len(removed),
           "candidate_by_category": cats}

with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
    json.dump({"summary": summary, "records": records}, fh, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "excluded.json"), "w", encoding="utf-8") as fh:
    json.dump({"by_rule": excl_rule, "judged": excl_judged, "dynamic_rev01": dynamic,
               "dir_level": dir_exclusions,
               "dynamic_note": "revision-01/ 内全部文件与 Ndocu/results/TASK-080-result.md 当前版为本轮动态产物，不进首提交manifest（自引用），提交时定稿后按当时hash纳入或次轮提交"},
              fh, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "sensitive-review.json"), "w", encoding="utf-8") as fh:
    json.dump({"hits": sensitive, "uncertain_excluded": uncertain,
               "adjudication": ADJUDICATION}, fh, ensure_ascii=False, indent=1)

# pathspec：UTF-8、NUL 分隔、每条 :(literal) 前缀，防 pathspec 魔法扩围
spec = "\0".join(":(literal)" + r["path"] for r in records)
with open(os.path.join(OUT, "pathspec-first-commit.txt"), "wb") as fh:
    fh.write(spec.encode("utf-8"))

print(json.dumps(summary, ensure_ascii=False, indent=1))
print("added_vs_old:", added)
print("removed_vs_old:", removed[:20], "..." if len(removed) > 20 else "")
print("uncertain_excluded:", [u["path"] for u in uncertain])
