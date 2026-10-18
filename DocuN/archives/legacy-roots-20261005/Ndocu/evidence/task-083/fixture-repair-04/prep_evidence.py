"""fixture-repair-04 改前证据：三冻结文件字节副本与SHA-256核对。

任务卡冻结值（review-03/hashes.txt一致）：
- job_control.py  F76F0A4E598A5B9ACB8524697FBC0A4F5C1F95D52D16526D20B6FAF3463DCB95
- focused_unit.py 0887ADEE55BFFBCB7DBEBC1FDD3A5514620711DDFB4DD12FAF1B6529A8CFF6D4
- offline_unit.py 3E79CE9715BB3F66AA5F91E37A8432FBF75E519797111F33CA65F15B1795CB04
不符即退出，不做任何修改。
"""
import hashlib
from pathlib import Path

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
EV = ROOT / "Ndocu/evidence/task-083/fixture-repair-04"
PRE = EV / "pre"
EXPECTED = {
    "backend/tests/fixtures/task083/job_control.py":
        "f76f0a4e598a5b9acb8524697fbc0a4f5c1f95d52d16526d20b6faf3463dcb95",
    "backend/tests/fixtures/task083/focused_unit.py":
        "0887adee55bffbcb7dbebc1fdd3a5514620711ddfb4dd12faf1b6529a8cff6d4",
    "backend/tests/fixtures/task083/offline_unit.py":
        "3e79ce9715bb3f66aa5f91e37a8432fbf75e519797111f33ca65f15b1795cb04",
}
PRE.mkdir(parents=True, exist_ok=True)
lines = ["TASK-083 fixture-repair-04 pre-repair byte copies; SHA256 must match card freeze"]
for rel, expected in EXPECTED.items():
    src = ROOT / rel
    data = src.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise SystemExit(f"FREEZE_MISMATCH {rel} actual={actual} expected={expected}")
    copy_name = rel.replace("/", "__")
    (PRE / copy_name).write_bytes(data)
    lines.append(f"{rel} pre_sha256={actual} copy=pre/{copy_name} MATCH")
(EV / "pre-hashes.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("PRE_OK")
print("\n".join(lines))
