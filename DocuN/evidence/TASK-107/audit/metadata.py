import datetime
import hashlib
import json
import pathlib
import time

# 只读审计工具，不导入业务或验证夹具。
ROOT = pathlib.Path(r"D:/shspic/project_NO3_RetroLume-agent")
OWN = ROOT / "DocuN/evidence/TASK-107/audit"


def path(value):
    p = pathlib.Path(value)
    return p if p.is_absolute() else ROOT / p


def raw(value):
    return path(value).read_bytes()


def load(value):
    return json.loads(raw(value).decode("utf-8-sig"))


def sha(value):
    return hashlib.sha256(value).hexdigest()


def identity(value):
    data = raw(value)
    return {"path": str(path(value)), "bytes": len(data), "sha256": sha(data)}


def save(name, value):
    p = OWN / name
    if not p.resolve().is_relative_to(OWN.resolve()):
        raise RuntimeError("审计原件写入目录越界")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def check_deadline():
    r = load(OWN / "receipt.json")
    if time.monotonic_ns() >= r["deadline_ns"]:
        raise RuntimeError("本卡主动截止已到")


def shape(value):
    if isinstance(value, dict):
        return {"type": "dict", "keys": list(value), "length": len(value)}
    if isinstance(value, list):
        return {"type": "list", "length": len(value)}
    return value
