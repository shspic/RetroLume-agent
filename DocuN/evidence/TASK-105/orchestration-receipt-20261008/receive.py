"""核105设计结果及源码事实，不执行任何产品或未来模型。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import ast

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-105/design"
OUT = ROOT / "DocuN/evidence/TASK-105/orchestration-receipt-20261008"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), "保留现有回收登记"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    report_path = ROOT / "DocuN/results/TASK-105-result.md"
    report = report_path.read_bytes()
    consistency = load(BASE / "document-consistency.json")
    session = load(BASE / "session.json")
    assert sha(report) == consistency["result_sha256"] == session["result_sha256"]
    text = report.decode("utf-8")
    for h in ["## A ", "## B ", "## C ", "## D "]:
        assert h in text
    assert "*" not in text
    assert len(consistency["checks"]) == 22 and all(r["passed"] for r in consistency["checks"])
    assert all(value == 0 for value in session["runtime_counts"].values()) and session["actual_new_runtime"] == 0
    identities = load(BASE / "input-identity.json")
    checks = []
    for row in identities["records"]:
        actual = sha(Path(row["path"]).read_bytes())
        checks.append({"path": row["path"], "expected": row["expected"], "actual": actual, "match": actual == row["expected"]})
    assert len(checks) == 46 and all(r["match"] for r in checks)
    current = load(ROOT / "DocuN/evidence/TASK-104/orchestration-close-20261007/current-baseline.json")
    for rel, expected in current.items():
        assert sha((ROOT / rel).read_bytes()) == expected
    facts = load(BASE / "source-function-facts.json")
    positions = []
    for row in facts["files"]:
        p = Path(row["path"])
        assert sha(p.read_bytes()) == row["sha256"]
        tree = ast.parse(p.read_text(encoding="utf-8-sig"))
        nodes = {(n.name, n.lineno, n.end_lineno) for n in ast.walk(tree)
                 if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))}
        for location in row["locations"]:
            assert (location["name"], location["line"], location["end_line"]) in nodes
        positions.append({"path": str(p), "sha256": row["sha256"], "locations_verified": len(row["locations"])})
    new_paths = ["backend/migrations/011_text_interview.sql", "backend/app/activities/interview_repository.py",
        "backend/app/interview/__init__.py", "backend/app/interview/contracts.py", "backend/app/interview/prompt.py",
        "backend/app/interview/evidence.py", "backend/app/interview/policy.py", "backend/app/interview/views.py",
        "backend/app/interview/service.py", "backend/app/interview/api.py", "frontend/src/activities/InterviewWorkspace.tsx",
        "frontend/src/activities/InterviewCitations.tsx", "frontend/src/activities/interviewApi.ts",
        "frontend/src/activities/interviewIntents.ts", "frontend/src/activities/interviewDrafts.ts",
        "frontend/src/activities/interview-workspace.css"]
    assert len(new_paths) == 16 and all(not (ROOT / p).exists() for p in new_paths)
    save("identity-checks.json", checks)
    save("function-position-checks.json", positions)
    save("current-baseline.json", current)
    (OUT / "TASK-105-as-returned.md").write_bytes(report)
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/tasks/TASK-105.md"]:
        data = (ROOT / rel).read_bytes()
        p = OUT / "before" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        p.write_bytes(data)
        before.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
    save("before-manifest.json", before)
    save("receipt.json", {"at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "TASK": "TASK-105", "R": "R-099",
        "dispatch": "已实际返回", "report_bytes": len(report), "report_sha256": sha(report), "input_checks": len(checks),
        "current_product_objects_unchanged": len(current), "function_files": len(positions),
        "function_locations_verified": sum(r["locations_verified"] for r in positions),
        "consistency_checks": 22, "proposed_new16_not_created": True,
        "source_spot_checks": "真实_scope SourceSnapshot映射、operation→head锁序、终态确认/同事务正文及OneCall载荷位置一致",
        "design_receipt": "完整A—D建议合同可审阅；文档交付不等于实施或运行通过",
        "ordinary_fixed_details": "公开history仅元数据不传模型/回答全文，workspace有界当前投影，单record详情受明确wire上限；在work-decision列明作为实施细化，不追加用户选择",
        "proposed_G10_P": "三表/011/五函数/两领域角色/公开九动作六路由/受信interview.v1/工作区意图恢复/独立能力门；待用户采用",
        "active_seconds": session["active_elapsed_seconds"], "metadata_seconds": session["metadata_used_seconds"],
        "metadata_failures": session["metadata_failures"], "official_pages": session["official_pages"],
        "design_permission_ended": True, "product_runs": 0, "root_product_writes": 0,
        "necessary_next": "编排设计验收关闭105，保存具体G10-P采用包；106实现仍仅计划不占号/出卡"})
    print(json.dumps({"report_bytes": len(report), "report_sha256": sha(report), "input_checks": len(checks),
        "function_locations": sum(r["locations_verified"] for r in positions), "unchanged": len(current),
        "new_model_implemented": False, "product_runs": 0}))


if __name__ == "__main__":
    main()
