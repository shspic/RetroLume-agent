# TASK-081 读取范围哈希清单生成脚本（只读输入，仅写同目录 read-hashes.txt）
import hashlib
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
FILES = [
    ("AGENTS 入口", ROOT / "AGENTS.md"),
    ("公共 AGENTS", Path(r"D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD")),
    ("076 裁定", ROOT / "Ndocu/results/TASK-076-work-decision.md"),
    ("076 结果", ROOT / "Ndocu/results/TASK-076-result.md"),
    ("需求 v1.1", ROOT / "docu/LATER_REQUIREMENTS.MD"),
    ("架构 v0.34", ROOT / "docu/PROJECT_ARCHITECTURE.MD"),
    ("执行状态 v1.36", ROOT / "docu/PROJECT_EXECUTE_STATE.MD"),
    ("活动仓储", ROOT / "backend/app/activities/repository.py"),
    ("Windows Job", ROOT / "backend/app/pdf_import/_windows_job.py"),
    ("PDF 监督器", ROOT / "backend/app/pdf_import/supervisor.py"),
    ("受控网关", ROOT / "backend/app/capabilities/gateway.py"),
    ("传输", ROOT / "backend/app/capabilities/transport.py"),
    ("004 迁移", ROOT / "backend/migrations/004_activities_time_budget.sql"),
    ("079 结果", ROOT / "Ndocu/results/TASK-079-result.md"),
]

lines = []
for label, path in FILES:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    lines.append(f"{digest}  {label}  {path}")

out = Path(__file__).with_name("read-hashes.txt")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"WROTE {out} ({len(FILES)} files)")
