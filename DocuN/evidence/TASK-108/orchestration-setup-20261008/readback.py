"""一次完整文档回读与保护身份核证，不运行产品。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-108/orchestration-setup-20261008"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    proof = load(BASE / "delivery-proof.json")
    card = (ROOT / "DocuN/tasks/TASK-108.md").read_bytes()
    text = card.decode("utf-8")
    assert len(card) == proof["card"]["bytes"] and sha(card) == proof["card"]["sha256"]
    assert all("## " + h in text for h in proof["seven_sections"])
    assert "*" not in text and "|" not in text and "v2.22" in text and "v1.00" in text
    assert all(s in text for s in ["A 当前事实", "B 唯一完整合同", "C 最小完整实施范围", "D 未来最小验证"])
    inputs = load(BASE / "design-input.json")
    for rel, expected in inputs["current_files"].items():
        assert sha((ROOT / rel).read_bytes()) == expected
    for item in inputs["contract_inputs"]:
        assert sha(Path(item["path"]).read_bytes()) == item["sha256"]
    for item in inputs["locked_rules"]:
        assert sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"]
    for key in ["report106", "report107"]:
        assert sha(Path(proof[key]["path"]).read_bytes()) == proof[key]["sha256"]
    prior = ROOT / "DocuN/evidence/TASK-107/orchestration-receipt-01/before"
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuN/results/TASK-106-work-decision.md", "DocuN/results/TASK-107-work-decision.md"]:
        assert (ROOT / rel).read_bytes().endswith((prior / rel).read_bytes())
    changes = (ROOT / "DocuS/文档变更记录.MD").read_bytes()
    assert changes.startswith((prior / "DocuS/文档变更记录.MD").read_bytes())
    assert b"CHG-1042" in changes and b"CHG-1043" not in changes
    assert not (ROOT / "DocuN/results/TASK-108-result.md").exists()
    assignment = load(BASE / "window-assignment.json")
    assert not assignment["sent"] and not assignment["received"] and not assignment["started"]
    work107 = (ROOT / "DocuN/results/TASK-107-work-decision.md").read_text(encoding="utf-8")
    assert "后续109相关HTML最终独立审计" not in work107
    result = {"status": "一次文档一致性核对通过", "card_bytes": len(card), "card_sha256": sha(card),
              "sections": 7, "A_D_complete": True, "current_protected_scope": len(inputs["current_files"]),
              "report106_107_and_all_old_history_exact": True, "next_CHG": 1043,
              "dispatch": "待转交", "product_SQL_tests_build_starts": 0,
              "same_check_correction": "107裁定新增前缀的未来109归属表述改为实现任务；不改原审计报告/历史/编号"}
    target = BASE / "readback-result.json"
    assert not target.exists()
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
