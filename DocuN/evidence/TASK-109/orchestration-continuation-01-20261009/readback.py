"""一次前缀、保护文件、原报告和文档对应检查，不运行产品。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-109"
OUT = BASE / "orchestration-continuation-01-20261009"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    proof = load(OUT / "delivery-proof.json")
    card = (ROOT / "DocuN/tasks/TASK-109.md").read_bytes()
    prefix = card[:proof["card_prefix_bytes"]]
    text = prefix.decode("utf-8")
    assert sha(card) == proof["full_card_sha256"] and sha(prefix) == proof["card_prefix_sha256"]
    assert all("## " + s in text for s in proof["seven_sections"]) and "*" not in text and "|" not in text
    assert "v2.25" in text and "v1.03" in text
    prior = BASE / "orchestration-receipt-01/before"
    assert card.endswith((prior / "DocuN/tasks/TASK-109.md").read_bytes())
    incoming = load(OUT / "continuation-input.json")
    for rel, expected in incoming["current_files"].items():
        assert sha((ROOT / rel).read_bytes()) == expected
    for item in load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json"):
        assert sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"]
    assert sha(Path(incoming["report_before"]["path"]).read_bytes()) == incoming["report_before"]["sha256"]
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuN/results/TASK-109-work-decision.md"]:
        assert (ROOT / rel).read_bytes().endswith((prior / rel).read_bytes())
    ledger = (ROOT / "DocuS/文档变更记录.MD").read_bytes()
    assert ledger.startswith((prior / "DocuS/文档变更记录.MD").read_bytes())
    assert b"CHG-1072" in ledger and b"CHG-1073" not in ledger
    budget = incoming["budget"]
    assert budget["original_deadline_ns"] == 795901594189000 and budget["new_root_limit"] == 1
    assignment = load(OUT / "window-assignment.json")
    assert not assignment["sent"] and not assignment["received"] and not assignment["started"]
    assert not (ROOT / "DocuN/tasks/TASK-110.md").exists()
    result = {"status": "一次文档与身份回读通过", "prefix_bytes": len(prefix), "full_card_sha256": sha(card),
              "current_scope": len(incoming["current_files"]), "history_report_rules_unchanged": True,
              "first_program_diagnostic_not_production_gate": True, "business_frozen": True,
              "new_root_one": True, "original_deadline_unchanged": True, "new_used": 0, "dispatch": "待转交",
              "next_CHG": 1073, "main_product_runs": 0,
              "document_correction": "新CHG1063非实据数字32删去；首patch时间戳未匹配无写入，再按真实行一次修正，不影响源或执行"}
    p = OUT / "readback-result.json"; assert not p.exists()
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
