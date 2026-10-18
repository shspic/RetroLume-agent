import datetime
import hashlib
import json
import pathlib
import time

# 本脚本只读文件和记录本轮审计原件，不导入产品或测试。
ROOT = pathlib.Path(r"D:/shspic/project_NO3_RetroLume-agent")
OWN = ROOT / "DocuN/evidence/TASK-104/review-02"


def check_deadline():
    receipt = load(OWN / "audit-receipt.json")
    if time.perf_counter() >= receipt["active_deadline_monotonic"]:
        raise RuntimeError("本轮主动预算已触顶")


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
    destination = OWN / name
    if destination.parent.resolve() != OWN.resolve():
        raise RuntimeError("本轮审计材料只能写入指定目录")
    destination.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
