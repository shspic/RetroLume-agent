"""核对审计回传身份和原有理由承载的文件定位，不执行产品。"""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
HERE = Path(__file__).resolve().parent
AUDIT = ROOT / "DocuN/evidence/TASK-124/audit"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def norm(value):
    p = Path(str(value).replace("\\\\", "/").replace("\\", "/"))
    return p if p.is_absolute() else ROOT / p


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


rows = []


def check(path, expected, scope):
    p = norm(path)
    actual = digest(p) if p.is_file() else None
    rows.append({"path": p.as_posix(), "expected": expected, "actual": actual,
                 "scope": scope, "match": expected == actual})


for row in load(AUDIT / "input-verification.json")["rows"]:
    check(row["path"], row["expected_sha256"], "79_audit_inputs")
seal = load(AUDIT / "save-proof.json")
for row in seal["artifact_and_report_rows"]:
    check(row["path"], row["sha256"], "eight_sealed_outputs")
for row in load(ROOT / "DocuN/evidence/TASK-123/execution/post-snapshot.json")["products"]:
    check(row["path"], row["post_sha256"], "six_unchanged_final_files")
for row in load(ROOT / "DocuN/evidence/TASK-123/execution/delivery-manifest.json")["rows"]:
    check(row["path"], row["sha256"], "48_frozen_engineering_artifacts")

sources = [
    ("DocuS/最终需求文档.MD", "FR010/DR002原批准要求为保存带依据的理由和进度，未要求独立任意手写中性备注接口"),
    ("DocuN/evidence/TASK-116/design/acceptance-contract.md", "L01/L05保留理由与真实进度证据，不改Must"),
    ("DocuN/evidence/TASK-116/design/integration-contract.md", "M06及主链明确evaluate同事务保存progress及保留/推进理由"),
    ("backend/app/activities/teaching_repository.py", "_progress_reason、evaluate分支进度写入、correct争议效果及原workspace/record读取"),
    ("backend/app/learning/teaching_progress.py", "correction按父反馈入争议集合，即使disputed_dimensions空仍排除独立依据"),
    ("frontend/src/activities/TeachingWorkspace.tsx", "已有更新或保留理由面板读取reasonBody.reason，不需要新增中性备注动作"),
]
source_facts = [{"path": (ROOT / path).as_posix(), "sha256": digest(ROOT / path), "scope": purpose,
                 "evidence_grade": "B 源码/原合同静态事实，不是本轮行为验证"} for path, purpose in sources]

protected_rel = ["DocuN/results/TASK-123-result.md", "DocuN/results/TASK-124-result.md",
    "DocuN/results/TASK-120-result.md", "DocuN/results/TASK-121-result.md", "DocuN/results/TASK-122-result.md",
    "DocuN/evidence/TASK-120/execution/budget.json", "DocuN/evidence/TASK-120/execution/events.jsonl",
    "DocuS/原始需求文档.MD", "DocuS/最终需求文档.MD"]
protected = {rel: digest(ROOT / rel) for rel in protected_rel}
findings = load(AUDIT / "findings.json")
assert len(findings["blocking"]) == 1 and findings["blocking"][0]["id"] == "F124-01"
result = {"schema": "retrolume.task124.orchestration-return.v1", "at": datetime.now(timezone.utc).isoformat(),
    "identity_count": len(rows), "rows": rows, "mismatches": [row for row in rows if not row["match"]],
    "report_bytes": seal["report"]["bytes"], "report_sha256": seal["report"]["sha256"],
    "source_facts": source_facts, "protected_before_publication": protected,
    "finding_accepted": "F124-01_P1_OPEN_PENDING_DOCUMENT_CORRECTION",
    "cause": "中性手写参考文字误用correct；原批准的实际进度理由已有progress.reason承载，原源接口无须改变",
    "code_and_13_offline_evidence_adopted_in_audit_scope": True,
    "original_product_or_test_or_network_execution": 0,
    "metadata_lookup_limitations": "主控一次组合rg含归档前087旧路径、一次猜测teaching_progress测试路径不存在；所需实际合同/仓储/前端均已定位，不冒称缺件已读，不影响本范围。",
    "passed": all(row["match"] for row in rows)}
(HERE / "return-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": result["passed"], "identity_rows": len(rows), "mismatches": result["mismatches"],
    "F124-01": "OPEN_PENDING_DOCUMENT_CORRECTION", "runtime": 0}, ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
