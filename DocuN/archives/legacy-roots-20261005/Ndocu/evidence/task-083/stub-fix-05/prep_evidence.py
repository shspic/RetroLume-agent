"""stub-fix-05 改前取证：保存focused_unit.py真实字节副本并核对卡冻结SHA-256。

只读取证+副本写入证据目录，不触碰被改文件本身；不import任何项目模块。
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "backend/tests/fixtures/task083/focused_unit.py"
HERE = Path(__file__).resolve().parent
PRE_DIR = HERE / "pre"
PRE_DIR.mkdir(parents=True, exist_ok=True)
DST = PRE_DIR / "backend__tests__fixtures__task083__focused_unit.py"

data = SRC.read_bytes()
DST.write_bytes(data)
pre_hash = hashlib.sha256(data).hexdigest()
expected = "1e58eb039eb54e0400a8a730b649fb7e450bb558bb983d27e1db1a24c2a8ce08"
(HERE / "pre-hashes.txt").write_text(
    "TASK-083 stub-fix-05 pre-evidence: focused_unit.py real bytes before edit\n"
    f"backend/tests/fixtures/task083/focused_unit.py sha256={pre_hash}\n"
    f"card-frozen sha256={expected}\n"
    f"match={str(pre_hash == expected).lower()}\n",
    encoding="utf-8",
)
print(f"pre_bytes={len(data)} pre_sha256={pre_hash}")
print("MATCH" if pre_hash == expected else "MISMATCH_STOP")
