"""同批最终回读修正批准措辞及指纹，不能因此追认用户批准。"""
from pathlib import Path
import hashlib
import json

root = Path(r"D:\shspic\project_NO3_RetroLume-agent")
base = root / "DocuN/evidence/TASK-105/orchestration-receipt-20261008"
decision = root / "DocuN/results/TASK-105-work-decision.md"
body = decision.read_bytes()
assert "合成实现与相称定向验证，" in body.decode("utf-8")
p = base / "adoption-package.json"
value = json.loads(p.read_text(encoding="utf-8"))
assert value["implementation_authorized"] is False and value["user_adoption_received"] is False
value["work_decision_sha256"] = hashlib.sha256(body).hexdigest()
value["adoption_scope"] = "合成实现与相称定向验证，精确运行对象和预算随后由正式卡限定；原建议次数不自动授执行"
p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
p = base / "delivery-proof.json"
proof = json.loads(p.read_text(encoding="utf-8"))
assert proof["new_user_approval_received"] is False
proof["decision_sha256"] = value["work_decision_sha256"]
proof["adoption_package_sha256"] = hashlib.sha256((base / "adoption-package.json").read_bytes()).hexdigest()
proof["same_batch_final_wording"] = "采用包写为合成实现与验证，避免把正常后续验证误限为仅准备；仍未批准/未运行"
p.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"decision_sha256": proof["decision_sha256"], "approved": False, "runtime": 0}))
