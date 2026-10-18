"""一次文档与文件身份回读，不运行产品或测试。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE = ROOT / "DocuN/evidence/TASK-107/orchestration-setup-20261008"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    proof = load(BASE / "delivery-proof.json")
    incoming = load(BASE / "audit-input.json")
    card_path = ROOT / "DocuN/tasks/TASK-107.md"
    card = card_path.read_bytes()
    text = card.decode("utf-8")
    assert len(card) == proof["card"]["bytes"] and sha(card) == proof["card"]["sha256"]
    assert len(incoming["current_files"]) == 363
    for rel, expected in incoming["current_files"].items():
        assert sha((ROOT / rel).read_bytes()) == expected, rel
    freeze_in_card = [
        "backend/app/activities/interview_repository.py", "backend/app/interview/service.py",
        "frontend/src/activities/InterviewWorkspace.tsx", "frontend/src/activities/interviewApi.ts",
        "frontend/src/activities/interviewIntents.ts", "frontend/dist/index.html",
        "frontend/dist/assets/index-DZFU8Isw.js"]
    for rel in freeze_in_card:
        assert incoming["current_files"][rel] in text, rel
    assert all("## " + h in text for h in proof["seven_sections"])
    assert "*" not in text and "|" not in text
    assert "v2.21" in text and "v0.99" in text
    assert incoming["contract"]["sha256"] in text
    receipt = load(ROOT / "DocuN/evidence/TASK-106/orchestration-receipt-02/receipt.json")
    assert sha((ROOT / "DocuN/results/TASK-106-result.md").read_bytes()) == receipt["report_sha256"]
    before = ROOT / "DocuN/evidence/TASK-106/orchestration-receipt-02/before"
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuN/results/TASK-106-work-decision.md"]:
        assert (ROOT / rel).read_bytes().endswith((before / rel).read_bytes())
    changes = (ROOT / "DocuS/文档变更记录.MD").read_bytes()
    assert changes.startswith((before / "DocuS/文档变更记录.MD").read_bytes())
    assert b"CHG-1029" in changes and b"CHG-1030" not in changes
    assert not (ROOT / "DocuN/results/TASK-107-result.md").exists()
    assignment = load(BASE / "window-assignment.json")
    assert not assignment["sent"] and not assignment["received"] and not assignment["started"]
    result = {"status": "文件与文档一次核证通过", "card": str(card_path), "card_bytes": len(card),
              "card_sha256": sha(card), "source_scope": 363, "freeze_hashes_in_card": len(freeze_in_card),
              "history_exact": True, "report106_unchanged": True, "CHG": "1018—1029",
              "dispatch": "待转交", "business_starts_SQL_tests_build": 0,
              "metadata_registration_error": "首步字节截断解码错误已记录，无产品或占号效果；一次有据修正后登记成功"}
    path = BASE / "readback-result.json"
    assert not path.exists()
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
