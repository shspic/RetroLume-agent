"""一次完整卡/状态/保护身份回读，非产品验证。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
OUT = ROOT / "DocuN/evidence/TASK-109/orchestration-setup-20261009"
STAGE = ROOT / "DocuN/evidence/TASK-108/orchestration-adoption-20261009"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    proof = load(OUT / "delivery-proof.json")
    data = (ROOT / "DocuN/tasks/TASK-109.md").read_bytes()
    text = data.decode("utf-8")
    assert len(data) == proof["card"]["bytes"] and sha(data) == proof["card"]["sha256"]
    assert all("## " + s in text for s in proof["seven_sections"])
    assert "*" not in text and "|" not in text and "v2.24" in text and "v1.02" in text
    incoming = load(OUT / "input-baseline.json")
    assert incoming["approved_package"]["adopted"] and incoming["approved_package"]["user_message"] == "批准"
    assert incoming["source_contract"]["sha256"] in text
    for rel, expected in incoming["current_files"].items():
        assert sha((ROOT / rel).read_bytes()) == expected
    package = load(STAGE / "playwright-local-files.json")
    for rel, expected in package["files"].items():
        assert sha((Path(package["path"]) / rel).read_bytes()) == expected
    for item in incoming["rules"]:
        assert sha(Path(item["absolute_path"]).read_bytes()) == item["sha256"]
    prior = OUT / "before"
    for rel in ["DocuS/执行动态文档.MD", "DocuS/架构动态文档.MD", "DocuN/results/TASK-108-work-decision.md"]:
        assert (ROOT / rel).read_bytes().endswith((prior / rel).read_bytes())
    changes = (ROOT / "DocuS/文档变更记录.MD").read_bytes()
    assert changes.startswith((prior / "DocuS/文档变更记录.MD").read_bytes())
    assert b"CHG-1061" in changes and b"CHG-1062" not in changes
    assert not (ROOT / "DocuN/results/TASK-109-result.md").exists()
    assert not (ROOT / "DocuN/tasks/TASK-110.md").exists()
    assignment = load(OUT / "window-assignment.json")
    assert not assignment["sent"] and not assignment["received"] and not assignment["started"]
    assert sha(Path(incoming["source_contract"]["path"]).read_bytes()) == incoming["source_contract"]["sha256"]
    result = {"status": "一次文件与文档核对通过", "card_bytes": len(data), "card_sha256": sha(data),
              "source_objects": len(incoming["current_files"]), "local_dependency_files": package["count"],
              "adopted": True, "first_gate_before_business": True, "shared_history_exact": True,
              "dispatch": "待转交", "next_CHG": 1062, "main_product_SQL_tests_build_starts": 0,
              "same_check_fix": "卡内测试通配符改成中文名称范围，格式核证失败发生在占号前，无执行域变化"}
    p = OUT / "readback-result.json"
    assert not p.exists()
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
