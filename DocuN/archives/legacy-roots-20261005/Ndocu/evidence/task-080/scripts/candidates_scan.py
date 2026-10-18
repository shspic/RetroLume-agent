# -*- coding: utf-8 -*-
"""TASK-080 首批纳管候选清单扫描：全树分类、排除边界、git check-ignore 权威核验、
有限敏感信息检查与人工裁定。只读项目文件；输出仅写 Ndocu/evidence/task-080/。
敏感检查结果只含路径与模式名，不含匹配值。"""
import json
import os
import re
import subprocess
import datetime

ROOT = r"D:\shspic\project_NO3_RetroLume-agent"
OUT = os.path.join(ROOT, "Ndocu", "evidence", "task-080")
MAX_SENSITIVE_SCAN_BYTES = 1_000_000
MAX_FILE_BYTES = 1_000_000

# 疑似秘密待裁定：文件含运行期生成的口令值与DSN（合成容器、仅回环、已销毁，但属凭据值材料）。
# 按卡不纳管、不改动原文件，交回编排裁定。
WITHHELD = {
    "Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json":
        "含运行期生成的 db_password 与 DSN 值（task-073 合成容器证据），按卡不纳管交回判断",
    "Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json":
        "含运行期生成的 db_password 与 DSN 值（task-074 合成容器证据），按卡不纳管交回判断",
}

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
    ".pytest_cache": "测试缓存",
    ".ruff_cache": "lint缓存",
    ".cache": "缓存（忽略规则 .cache/）",
    ".vscode": "IDE配置目录",
    ".idea": "IDE配置目录",
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
# 人工裁定表（执行者已逐文件查看命中上下文；此处不记录匹配值）
ADJUDICATION = [
    {"files": ["tests/task054_pdf_materials_integration.mjs",
               "Ndocu/evidence/task-057/task054-original-script-copy.mjs",
               "Ndocu/evidence/task-059/task054-pre-059-script-copy.mjs",
               "Ndocu/evidence/task-061/task054-pre-061-script-copy.mjs",
               "Ndocu/evidence/task-064/pre-task054_pdf_materials_integration.mjs",
               "Ndocu/evidence/task-066/pre-task054_pdf_materials_integration.mjs"],
     "patterns": ["cred_url"],
     "verdict": "良性，保留候选",
     "rationale": "指向 127.0.0.1 本地合成测试库的固定测试标识符（与任务同名的占位用户/口令），非真实凭据；历史副本与 tests 源文件内容一致"},
    {"files": ["Ndocu/evidence/task-073/20260921T1254-wbA1/run_task073.py",
               "Ndocu/evidence/task-074/20260921T1319-wbB1/run_task074.py"],
     "patterns": ["cred_url"],
     "verdict": "良性，保留候选",
     "rationale": "DSN 为运行期由 secrets 模块生成拼接的模板字符串，脚本内无硬编码口令；口令仅存在于对应 run-result.json"},
    {"files": ["Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json",
               "Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json"],
     "patterns": ["cred_url"],
     "verdict": "疑似凭据值，不纳管交回判断",
     "rationale": "文件含运行期生成的 db_password 与 DSN 实际值（合成容器一次性口令，仅回环、容器已销毁）；按卡不纳管、不改动原文件，交编排裁定"},
    {"files": ["backend/app/capabilities/contracts.py",
               "backend/app/capabilities/gateway.py"],
     "patterns": ["assign_secret"],
     "verdict": "良性，保留候选",
     "rationale": "分别为 Pydantic SecretStr 字段声明与 get_secret_value() 取值调用，无任何硬编码密钥值"},
]


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


records = []
dir_exclusions = []
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
        ext = os.path.splitext(f)[1].lower()
        rec = {"path": rel, "bytes": size, "category": category_of(rel)}
        if rel in WITHHELD:
            rec["status"] = "withheld_secret_judgment"
            rec["reason"] = WITHHELD[rel]
            rec["secret_pattern_names"] = ["cred_url"]
        elif ext in BINARY_EXT:
            rec["status"] = "excluded"
            rec["reason"] = "二进制/生成物(%s)" % ext
        elif size > MAX_FILE_BYTES:
            rec["status"] = "excluded"
            rec["reason"] = "超大文件(>1MB)"
        elif rel.startswith("Ndocu/evidence/task-079/"):
            rec["status"] = "dynamic_079"
            rec["reason"] = "079窗口可能继续写入，本轮快照动态排除（不冻结）"
        else:
            rec["status"] = "candidate"
        records.append(rec)

# 有限敏感信息检查（仅候选文本，只记路径与模式名）
secret_hits = []
for rec in records:
    if rec["status"] != "candidate":
        continue
    ext = os.path.splitext(rec["path"])[1].lower()
    if ext not in TEXT_EXT or rec["bytes"] > MAX_SENSITIVE_SCAN_BYTES or rec["bytes"] < 0:
        continue
    full = os.path.join(ROOT, rec["path"])
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
    except OSError:
        continue
    hits = [name for name, pat in SECRET_PATTERNS if pat.search(text)]
    if hits:
        rec["secret_pattern_names"] = hits
        secret_hits.append({"path": rec["path"], "category": rec["category"],
                            "patterns": hits})

# git check-ignore 权威核验（候选不应被忽略）
candidates = [r["path"] for r in records if r["status"] == "candidate"]
ignored_map = {}
conflicts = []
if candidates:
    # 以字节输入避免Windows text模式把\n翻译成\r\n（否则git收到带幻影\r的路径，
    # 核验空转）；-c core.quotepath=off 仅本次调用生效，保证非ASCII路径原样输出。
    # -v 输出格式：<source>:<line>:<pattern>\t<pathname>
    p = subprocess.run(["git", "-c", "core.quotepath=off", "check-ignore", "-v", "--stdin"],
                       cwd=ROOT,
                       input=("\n".join(candidates) + "\n").encode("utf-8"),
                       capture_output=True, timeout=50)
    for line in p.stdout.decode("utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        if "\t" in line:
            rule, _, pathpart = line.partition("\t")
            ignored_map[pathpart.strip().strip('"')] = rule
        else:
            ignored_map[line.strip()] = "?"
    for c in candidates:
        if c in ignored_map:
            for r in records:
                if r["path"] == c:
                    r["check_ignore_conflict"] = ignored_map[c]
            conflicts.append({"path": c, "ignored_by": ignored_map[c]})

summary = {"total_files_seen": len(records),
           "candidate": sum(1 for r in records if r["status"] == "candidate"),
           "excluded": sum(1 for r in records if r["status"] == "excluded"),
           "dynamic_079": sum(1 for r in records if r["status"] == "dynamic_079"),
           "withheld_secret_judgment": sum(1 for r in records if r["status"] == "withheld_secret_judgment"),
           "check_ignore_conflicts": len(conflicts),
           "dir_exclusions": len(dir_exclusions),
           "files_with_secret_patterns": len(secret_hits)}
by_cat = {}
for r in records:
    if r["status"] == "candidate":
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
summary["candidate_by_category"] = by_cat

excluded_dirs_unique = {}
for d in dir_exclusions:
    excluded_dirs_unique.setdefault(d["reason"], []).append(d["dir"])

out = {"collected_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "root": ROOT, "summary": summary, "records": records,
       "dir_exclusions": dir_exclusions, "secret_hits": secret_hits,
       "secret_adjudication": ADJUDICATION,
       "check_ignore_conflicts": conflicts}
with open(os.path.join(OUT, "candidates.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

# 人类可审阅版
md = []
md.append("# TASK-080 首批纳管候选清单（快照）")
md.append("")
md.append("采集时刻：%s（Asia/Shanghai；079窗口证据为动态排除，不冻结）" % out["collected_at"])
md.append("")
md.append("## 汇总")
md.append("")
md.append("- 扫描文件总数：%d；候选：%d；单文件排除（二进制/生成物/超大）：%d；动态排除（079证据）：%d；疑似秘密待裁定（不纳管）：%d" %
          (summary["total_files_seen"], summary["candidate"], summary["excluded"],
           summary["dynamic_079"], summary["withheld_secret_judgment"]))
md.append("- check-ignore 冲突（候选被忽略规则命中）：%d" % summary["check_ignore_conflicts"])
md.append("- 候选文本敏感模式命中文件数：%d（仅路径与模式名，匹配值不记录；逐条裁定见下）" % len(secret_hits))
md.append("")
md.append("## 候选按类别")
md.append("")
for cat in sorted(by_cat):
    md.append("- %s：%d 个" % (cat, by_cat[cat]))
md.append("")
for cat in sorted(by_cat):
    md.append("## 候选清单：%s" % cat)
    md.append("")
    for r in records:
        if r["status"] == "candidate" and r["category"] == cat:
            flags = ""
            if r.get("secret_pattern_names"):
                flags = " 【敏感模式命中:%s，已裁定良性，见裁定表】" % ",".join(r["secret_pattern_names"])
            md.append("- `%s`（%d 字节）%s" % (r["path"], r["bytes"], flags))
    md.append("")
md.append("## 疑似秘密人工裁定表（执行者逐文件查证，本表不含匹配值）")
md.append("")
for a in ADJUDICATION:
    md.append("- 模式：%s；裁定：%s" % (",".join(a["patterns"]), a["verdict"]))
    for f in a["files"]:
        md.append("  - `%s`" % f)
    md.append("  - 依据：%s" % a["rationale"])
md.append("")
md.append("## 目录级排除（原位置保留不删）")
md.append("")
for reason, dirs in excluded_dirs_unique.items():
    md.append("- %s：%d 处（如 %s%s）" % (reason, len(dirs), dirs[0], " 等" if len(dirs) > 1 else ""))
md.append("")
md.append("## 单文件排除（二进制/生成物/超大文件；原位置保留不删）")
md.append("")
for r in records:
    if r["status"] == "excluded":
        md.append("- `%s`（%d 字节，%s）" % (r["path"], r["bytes"], r["reason"]))
md.append("")
md.append("## 疑似秘密待裁定（不纳管，原文件未改动）")
md.append("")
for r in records:
    if r["status"] == "withheld_secret_judgment":
        md.append("- `%s`（%d 字节）：%s" % (r["path"], r["bytes"], r["reason"]))
md.append("")
md.append("## 动态排除：079 证据（本轮快照不冻结；正式提交前需停写或逐文件快照）")
md.append("")
for r in records:
    if r["status"] == "dynamic_079":
        md.append("- `%s`（%d 字节）" % (r["path"], r["bytes"]))
md.append("")
with open(os.path.join(OUT, "candidates.md"), "w", encoding="utf-8", newline="") as fh:
    fh.write("\n".join(md))

print(json.dumps(summary, ensure_ascii=False, indent=1))
print("withheld:", list(WITHHELD))
print("conflicts:", conflicts[:5])
