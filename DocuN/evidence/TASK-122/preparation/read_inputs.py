"""本卡限定的标准库静态读取与摘要记录，不导入产品。"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent

def read_file(name, first=1, last=None):
    path = Path(name)
    if not path.is_absolute():
        path = ROOT / path
    raw = path.read_bytes()
    lines = raw.decode("utf-8-sig").splitlines()
    end = len(lines) if last is None else min(last, len(lines))
    record = {"at": datetime.now(timezone.utc).isoformat(), "path": str(path),
              "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
              "requested_lines": [first, last], "returned_lines": [first, end]}
    with (OUT / "read-ledger.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, ensure_ascii=False))
    for number in range(first, end + 1):
        print(f"{number}: {lines[number - 1]}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for item in sys.argv[1:]:
        parts = item.rsplit("::", 2)
        read_file(parts[0], int(parts[1]) if len(parts) > 1 else 1,
                  int(parts[2]) if len(parts) > 2 and parts[2] else None)
