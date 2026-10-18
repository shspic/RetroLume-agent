"""普通回收108设计与读入身份，仅核文件，不执行未来产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import ast
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-108"
OUT = BASE / "orchestration-receipt-01"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, obj):
    dest = OUT / name
    assert not dest.exists(), "保留已核证回收，不重复覆盖"
    dest.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    delivery = load(BASE / "design/delivery-check.json")
    session = load(BASE / "design/session.json")
    report = (ROOT / "DocuN/results/TASK-108-result.md").read_bytes()
    assert len(report) == delivery["result"]["bytes"] == 67263
    assert sha(report) == delivery["result"]["sha256"] == session["result_sha256"]
    text = report.decode("utf-8")
    assert all(title in text for title in ["## A ", "## B ", "## C ", "## D "])
    assert "*" not in text and delivery["pass_count"] == 1 and delivery["not_program_test"]
    assert session["runs"] == session["product_writes"] == delivery["fees"] == 0
    assert len(session["official_pages"]) == 6
    assert delivery["active_upper_bound_seconds"] == 3814.6
    assert delivery["metadata_upper_bound_seconds"] == 3814.6
    baseline = load(BASE / "orchestration-setup-20261008/design-input.json")
    current = baseline["current_files"]
    assert len(current) == 363
    checks = []
    for rel, expected in current.items():
        actual = sha((ROOT / rel).read_bytes())
        assert actual == expected, rel
        checks.append({"path": rel, "sha256": actual})
    for item in baseline["contract_inputs"]:
        assert sha(Path(item["path"]).read_bytes()) == item["sha256"]
    for item in baseline["locked_rules"]:
        assert sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"]
    extra = load(BASE / "design/fact-addendum.json")
    for item in extra["files"]:
        assert sha(Path(item["path"]).read_bytes()) == item["sha256"]
    facts = load(BASE / "design/source-function-facts.json")
    trees = {}
    for row in facts:
        rel = row["file"]
        if rel not in trees:
            tree = ast.parse((ROOT / rel).read_text(encoding="utf-8-sig"))
            trees[rel] = {(node.name, node.lineno, node.end_lineno) for node in ast.walk(tree)
                          if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert (row["name"], row["line"], row["end"]) in trees[rel]
    assert len(trees) == 11 and len(facts) == 221
    for link in delivery["local_links"]:
        assert Path(link["target"]).exists()
    image = load(BASE / "design/known-image-metadata.json")
    assert image["id"] == "sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac"
    assert image["cached"] and not image["started"] and not image["pulled"]
    before = []
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuS/文档变更记录.MD", "DocuN/results/TASK-108-work-decision.md"]:
        data = (ROOT / rel).read_bytes()
        copy = OUT / "before" / rel
        assert not copy.exists()
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(data)
        before.append({"path": rel, "bytes": len(data), "sha256": sha(data)})
    saved = OUT / "TASK-108-as-returned.md"
    assert not saved.exists()
    saved.write_bytes(report)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    save("identity-checks.json", checks)
    save("current-baseline.json", current)
    save("before-manifest.json", before)
    evidence = []
    for path in sorted((BASE / "design").glob("*.json")):
        data = path.read_bytes()
        evidence.append({"path": str(path), "bytes": len(data), "sha256": sha(data)})
    save("evidence-identities.json", evidence)
    save("receipt.json", {"at": now, "TASK": "TASK-108", "R": "R-102", "actual_return": True,
          "report_bytes": len(report), "report_sha256": sha(report), "source_objects": len(current),
          "contract_inputs": len(baseline["contract_inputs"]), "locked_rules": len(baseline["locked_rules"]),
          "extra_read_files": len(extra["files"]), "function_files": len(trees), "function_positions": len(facts),
          "document_check": "一次文档一致性自检，普通核证身份与合同对应，不是程序或独立安全审计",
          "acceptance": "接受并关闭108只读A—D设计交付；G11-P待一次具体采用，运行安全和产品未通过",
          "scope_conditions": ["NavigationGate全协议事前否决尚无可实现锚", "固定非root/seccomp/privateIPC实际sandbox尚未运行",
                               "镜像实际Node/browser/许可证未完整核", "精确容器物理树空证明待运行"],
          "proposal_sequence": "先现有API/固定宿主可实现性与H0关口，成立后才四表/接口/模型/完整接线；失败不转盲试",
          "new_native_engine_component_not_in_package": True,
          "old70_roots_budget_FAIL_UNKNOWN_money_not_reset": True,
          "active_upper_bound": 3814.6, "metadata_upper_bound": 3814.6,
          "exact_split": "未知，metadata按全部active重叠保守，不当两项可相加墙钟",
          "official_pages": session["official_pages"], "metadata_errors": session["failures"],
          "design_permit_ended": True, "implementation_authorized": False,
          "TASK109_R103": "仅未来计划未占/未出/未派", "B01": "仍开放",
          "main_product_writes_compile_test_build_SQL_Docker_starts": 0})
    print(json.dumps({"report_bytes": len(report), "source_objects": len(current), "contracts": len(baseline["contract_inputs"]),
          "rules": len(baseline["locked_rules"]), "extra": len(extra["files"]), "AST_positions": len(facts),
          "design_accepted": True, "G11_pending": True, "runtime": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
