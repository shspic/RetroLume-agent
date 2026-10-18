"""固定107许可、动作前计数和脱敏记录；不改变产品资格。"""
from __future__ import annotations
import contextlib
import hashlib
import json
import msvcrt
import os
import pathlib
import time
from datetime import datetime, timezone
from urllib.parse import quote

ROOT = pathlib.Path(r"D:/shspic/project_NO3_RetroLume-agent")
EVIDENCE = ROOT / "DocuN/evidence/TASK-107"
PERMIT = "TASK-107-G10-AUDIT-20261008"
LIMITS = {"root": 3, "container_start": 3, "listener_start": 3, "browser": 3, "driver": 3,
          "offline_batch": 3, "SUP_attempt": 8, "transport_send": 8, "password_reset": 2,
          "product_build": 0, "product_compile": 0, "product_unittest": 0,
          "migration": 0, "container_create": 0, "volume_create": 0, "database_create": 0, "role_create": 0}
SECOND_LIMITS = {"metadata": 10800, "offline": 600, "real": 1800, "cleanup": 600}
SECRET_VALUES = set()


def utc():
    return datetime.now(timezone.utc).isoformat()


def register_secret(value):
    if value:
        SECRET_VALUES.update((str(value), quote(str(value), safe="")))


def redact(value):
    text = str(value)
    for secret in sorted(SECRET_VALUES, key=len, reverse=True):
        text = text.replace(secret, "<已脱敏>")
    return text


def serial(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def atomic_json(path, value):
    path = pathlib.Path(path)
    if not path.resolve().is_relative_to(EVIDENCE.resolve()):
        raise RuntimeError("107证据写入越界")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=serial), encoding="utf-8")
    os.replace(tmp, path)


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))


def checksum(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


@contextlib.contextmanager
def locked():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with (EVIDENCE / "control.lock").open("a+b") as file:
        file.seek(0, 2)
        if not file.tell():
            file.write(b"\0"); file.flush()
        file.seek(0)
        msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            file.seek(0); msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)


def initialize():
    with locked():
        target = EVIDENCE / "session.json"
        if target.exists():
            return load(target)
        receipt = load(EVIDENCE / "audit/receipt.json")
        state = dict(permit=PERMIT, start_ns=receipt["start_ns"], deadline_ns=receipt["deadline_ns"],
                     counts={k: 0 for k in LIMITS}, count_limits=LIMITS, seconds={k: 0.0 for k in SECOND_LIMITS},
                     second_limits=SECOND_LIMITS, actions=[], checkpoints={}, closed=False,
                     previous_real_roots=67, root_deadline_ns=None, root_name=None)
        atomic_json(target, state)
        return state


def state():
    value = load(EVIDENCE / "session.json")
    receipt = load(EVIDENCE / "audit/receipt.json")
    if value["permit"] != PERMIT or value["start_ns"] != receipt["start_ns"] or value["deadline_ns"] != receipt["deadline_ns"]:
        raise RuntimeError("107许可或固定时钟发生变化")
    if value["count_limits"] != LIMITS or value["second_limits"] != SECOND_LIMITS:
        raise RuntimeError("107上限发生变化")
    return value


def event(kind, detail):
    with locked():
        value = state()
        value["actions"].append(dict(kind=kind, utc=utc(), ns=time.monotonic_ns(), pid=os.getpid(), detail=detail))
        atomic_json(EVIDENCE / "session.json", value)


def reserve(kind, detail=None):
    with locked():
        value = state(); now = time.monotonic_ns()
        if value["closed"] or now >= value["deadline_ns"]:
            raise RuntimeError("107许可已结束或到截止")
        if kind not in LIMITS or value["counts"][kind] >= LIMITS[kind]:
            raise RuntimeError("107动作额度不足：" + kind)
        if kind not in ("root", "offline_batch"):
            if not value["root_deadline_ns"] or now >= value["root_deadline_ns"]:
                raise RuntimeError("107真实根未生效或到截止")
        if kind == "root":
            if value["seconds"]["real"] >= SECOND_LIMITS["real"]:
                raise RuntimeError("107真实秒数额度不足")
            value["root_deadline_ns"] = min(now + 900 * 10**9, value["deadline_ns"])
            value["root_name"] = detail["name"]
        value["counts"][kind] += 1
        value["actions"].append(dict(kind=kind, count=value["counts"][kind], utc=utc(), ns=now,
                                     pid=os.getpid(), detail=detail or {}))
        atomic_json(EVIDENCE / "session.json", value)
        return value["counts"][kind]


def charge(bucket, seconds, detail):
    if bucket not in SECOND_LIMITS or not 0 <= seconds < float("inf"):
        raise RuntimeError("107计费输入非法")
    with locked():
        value = state()
        value["seconds"][bucket] += seconds
        value["actions"].append(dict(kind="charge", bucket=bucket, seconds=seconds, utc=utc(), detail=detail))
        atomic_json(EVIDENCE / "session.json", value)


def remaining(bucket, maximum):
    value = state()
    deadline = value["deadline_ns"] if bucket == "metadata" else value["root_deadline_ns"] or value["deadline_ns"]
    if bucket == "cleanup":
        deadline = value["deadline_ns"] + 600 * 10**9
    amount = min(maximum, SECOND_LIMITS[bucket] - value["seconds"][bucket], (deadline - time.monotonic_ns()) / 1e9)
    if amount <= 0:
        raise RuntimeError("107时间预算不足：" + bucket)
    return amount


def checkpoint(name, value):
    with locked():
        data = state(); data["checkpoints"][name] = value
        atomic_json(EVIDENCE / "session.json", data)


def require_runtime():
    data = state()
    if os.environ.get("RETROLUME_TASK107_FIXTURE") != PERMIT or data["closed"] or not data["root_deadline_ns"]:
        raise RuntimeError("107运行标记或根许可缺失")
    if time.monotonic_ns() >= min(data["root_deadline_ns"], data["deadline_ns"]):
        raise RuntimeError("107根截止已到")
    return data
