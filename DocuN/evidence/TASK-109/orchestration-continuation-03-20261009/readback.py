"""一次完整任务前缀与保护身份核证，非产品或浏览器测试。"""
from pathlib import Path
import hashlib
import json

ROOT=Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT=ROOT/"DocuN/evidence/TASK-109/orchestration-continuation-03-20261009"


def sha(data): return hashlib.sha256(data).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))


def main():
    proof=load(OUT/"delivery-proof.json"); card=(ROOT/"DocuN/tasks/TASK-109.md").read_bytes()
    prefix=card[:proof["prefix_bytes"]]; text=prefix.decode("utf-8")
    assert sha(prefix)==proof["prefix_sha256"] and sha(card)==proof["card_sha256"]
    assert all("## "+s in text for s in proof["sections"]) and "*" not in text and "|" not in text
    assert "v2.27" in text and "v1.05" in text
    incoming=load(OUT/"continuation-input.json")
    for rel,expected in incoming["current_files"].items(): assert sha((ROOT/rel).read_bytes())==expected
    for rule in load(ROOT/"DocuN/evidence/v4-migration-20260930/rules-snapshot.json"):
        assert sha(Path(rule["absolute_path"]).read_bytes())==rule["sha256"]
    old=OUT/"before"
    assert card.endswith((old/"DocuN/tasks/TASK-109.md").read_bytes())
    for rel in ["DocuS/执行动态文档.MD","DocuS/架构动态文档.MD","DocuN/results/TASK-109-work-decision.md"]:
        assert (ROOT/rel).read_bytes().endswith((old/rel).read_bytes())
    ledger=(ROOT/"DocuS/文档变更记录.MD").read_bytes()
    assert ledger.startswith((old/"DocuS/文档变更记录.MD").read_bytes()) and b"CHG-1094" in ledger and b"CHG-1095" not in ledger
    assert sha(Path(incoming["report_before"]["path"]).read_bytes())==incoming["report_before"]["sha256"]
    assert incoming["budget"]["original_deadline_ns"]==795901594189000 and incoming["budget"]["new_root"]==1
    assignment=load(OUT/"window-assignment.json"); assert not assignment["sent"] and not assignment["received"] and not assignment["started"]
    assert not (ROOT/"DocuN/tasks/TASK-110.md").exists()
    result={"status":"一次文档与保护身份核对通过","prefix_bytes":len(prefix),"full_card_sha256":sha(card),"source_scope":len(incoming["current_files"]),
        "history_report_rules_unchanged":True,"old_deadline_not_extended":True,"image_not_rebuilt":True,"bootstrap_dir_scope_only":True,
        "one_evidenced_repair_inside_card":True,"business_frozen":True,"next_CHG":1095,"dispatch":"待转交","main_runtime":0}
    p=OUT/"readback-result.json"; assert not p.exists(); p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__": main()
