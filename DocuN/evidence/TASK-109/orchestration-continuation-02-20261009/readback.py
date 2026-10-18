"""一次新前缀与完整历史、身份和预算对应核证，不执行产品。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-109"
OUT = BASE / "orchestration-continuation-02-20261009"


def sha(data): return hashlib.sha256(data).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))


def main():
    proof = load(OUT / "delivery-proof.json")
    card = (ROOT / "DocuN/tasks/TASK-109.md").read_bytes()
    prefix = card[:proof["card_prefix_bytes"]]
    text = prefix.decode("utf-8")
    assert sha(card) == proof["full_card_sha256"] and sha(prefix) == proof["card_prefix_sha256"]
    assert all("## " + h in text for h in proof["seven_sections"]) and "*" not in text and "|" not in text
    assert "v2.26" in text and "v1.04" in text
    incoming = load(OUT / "continuation-input.json")
    for rel, expected in incoming["current_files"].items(): assert sha((ROOT / rel).read_bytes()) == expected
    for item in load(ROOT / "DocuN/evidence/v4-migration-20260930/rules-snapshot.json"):
        assert sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"]
    assert sha(Path(incoming["report_before"]["path"]).read_bytes()) == incoming["report_before"]["sha256"]
    assert incoming["immutable_image"]["id"] in text
    before = OUT / "before"
    assert card.endswith((before / "DocuN/tasks/TASK-109.md").read_bytes())
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuN/results/TASK-109-work-decision.md"]:
        assert (ROOT / rel).read_bytes().endswith((before / rel).read_bytes())
    ledger = (ROOT / "DocuS/文档变更记录.MD").read_bytes()
    assert ledger.startswith((before / "DocuS/文档变更记录.MD").read_bytes())
    assert b"CHG-1083" in ledger and b"CHG-1084" not in ledger
    budget = incoming["budget"]
    assert budget["original_deadline_ns"] == 795901594189000 and budget["new_root"] == 1
    assert budget["new_image_save_build"] == 0
    assignment = load(OUT / "window-assignment.json")
    assert not assignment["sent"] and not assignment["received"] and not assignment["started"]
    assert not (ROOT / "DocuN/tasks/TASK-110.md").exists()
    result = {"status":"一次文档与身份核对通过", "prefix_bytes":len(prefix),"card_sha256":sha(card),"current_scope":len(incoming["current_files"]),
        "existing_image_reused_no_save_build":True,"history_report_rule_source_preserved":True,"new_used":0,"dispatch":"待转交",
        "business_frozen":True,"next_CHG":1084,"main_product_runs":0,
        "document_fix":"新state的save退出0语序澄清；首patch用局部字符串未匹配无效果，按完整实际行一次修正"}
    p = OUT / "readback-result.json"; assert not p.exists(); p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__ == "__main__": main()
