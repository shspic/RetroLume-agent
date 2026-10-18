"""本卡固定截止、动作前计数及限时日志；不替代产品权威。"""
from __future__ import annotations
import contextlib
import hashlib
import json
import math
import msvcrt
import os
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "DocuN" / "evidence" / "TASK-103"
PERMIT = "TASK-103-G9-20261006"
COUNTS = {"offline":6,"build":3,"entry":24,"container_create":3,"volume_create":3,
          "container_start":24,"listener_start":12,"sup":64,"browser":3,"driver":3}
LIMITS = {"offline":1800,"real":7200,"cleanup":900,"metadata":600}
SECRET_VALUES: set[str] = set()


class BudgetDenied(RuntimeError):
    pass


def finite(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise BudgetDenied("invalid finite budget")
    return value


def utc():
    return datetime.now(timezone.utc).isoformat()


def aggregate(records, exit_code):
    if type(exit_code) is not int or type(records) is not list or not records:
        return 'BLOCKED'
    if exit_code != 0 or any(r.get('status')=='FAIL' for r in records):
        return 'FAIL'
    if any(r.get('status')!='PASS' or r.get('executed') is not True for r in records):
        return 'BLOCKED'
    return 'PASS'


def redact(text):
    for value in sorted(SECRET_VALUES, key=len, reverse=True):
        if value:
            text = text.replace(value, "[REDACTED]")
    import re
    text = re.sub(r"(?i)(postgres(?:ql)?://)[^\s\"']+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(x-retrolume-session|authorization)([\"': =]+)[^\s,}]+",
                  r"\1\2[REDACTED]", text)
    return text


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


class Control:
    def __init__(self, path=None):
        self.path = Path(path) if path else EVIDENCE / "session.json"
        self.lock = self.path.with_suffix(".lock")
        self.receipt = EVIDENCE / "receipt.json"

    @contextlib.contextmanager
    def locked(self):
        self.lock.parent.mkdir(parents=True, exist_ok=True)
        with self.lock.open("a+b") as file:
            file.seek(0, 2)
            if file.tell() == 0:
                file.write(b"\0"); file.flush()
            file.seek(0)
            msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                file.seek(0); msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)

    def validate(self, data):
        if data.get("permit") != PERMIT or data.get("task") != "TASK-103":
            raise BudgetDenied("permit mismatch")
        for name in ("start_ns", "deadline_ns"):
            if type(data.get(name)) is not int or data[name] <= 0:
                raise BudgetDenied("invalid fixed clock")
        receipt = json.loads(self.receipt.read_text(encoding="utf-8-sig"))
        if any(data[name] != receipt[name] for name in ("start_ns", "deadline_ns", "permit")):
            raise BudgetDenied("fixed deadline changed")
        if data["deadline_ns"] - data["start_ns"] != 28800 * 10**9:
            raise BudgetDenied("active budget changed")
        for key, maximum in COUNTS.items():
            value = data["counts"].get(key)
            if type(value) is not int or not 0 <= value <= maximum:
                raise BudgetDenied("invalid count")
        for key, maximum in LIMITS.items():
            value = finite(data["used_seconds"].get(key))
            if value > maximum:
                raise BudgetDenied("time exhausted")
        return data

    def load(self):
        return self.validate(json.loads(self.path.read_text(encoding="utf-8")))

    def reserve(self, kind, detail=None):
        with self.locked():
            data = self.load()
            if time.monotonic_ns() >= data["deadline_ns"]:
                raise BudgetDenied("active deadline")
            if kind not in COUNTS or data["counts"][kind] >= COUNTS[kind]:
                raise BudgetDenied("count exhausted")
            data["counts"][kind] += 1
            data["actions"].append({"kind":kind,"count":data["counts"][kind],
                                   "at":utc(),"ns":time.monotonic_ns(),"detail":detail or {}})
            atomic_json(self.path, data)
            return data["counts"][kind]

    def remaining(self, bucket, maximum):
        maximum = finite(maximum)
        if maximum <= 0 or bucket not in LIMITS:
            raise BudgetDenied("invalid requested budget")
        data = self.load()
        deadline=data['deadline_ns']+(900*10**9 if bucket=='cleanup' else 0)
        amount = min(maximum, LIMITS[bucket] - data["used_seconds"][bucket],
                     (deadline - time.monotonic_ns()) / 1e9)
        if amount <= 0:
            raise BudgetDenied("time exhausted")
        return amount

    def charge(self, bucket, seconds, detail):
        seconds = finite(seconds)
        with self.locked():
            data = self.load()
            data["used_seconds"][bucket] += seconds
            data["actions"].append({"kind":"charge","bucket":bucket,"seconds":seconds,
                                   "at":utc(),"detail":detail})
            atomic_json(self.path, data)

    def record(self, detail):
        with self.locked():
            data = self.load()
            data["actions"].append({"kind":"observation","at":utc(),"detail":detail})
            atomic_json(self.path, data)

    def run(self, name, argv, bucket, maximum, count=None, cwd=None, env=None):
        if count:
            self.reserve(count, {"name":name})
        allowed = self.remaining(bucket, maximum)
        start = time.monotonic()
        directory = EVIDENCE / "runs" / name
        directory.mkdir(parents=True, exist_ok=False)
        before = freeze(directory / "as-run")
        result = {"name":name,"argv":[redact(str(x)) for x in argv],"cwd":str(cwd or ROOT),
                  "started_at":utc(),"allowed_seconds":allowed,"before":before}
        process = subprocess.Popen(argv, cwd=cwd or ROOT, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            stdout, stderr = process.communicate(timeout=allowed)
            result["exit_code"] = process.returncode
        except subprocess.TimeoutExpired:
            # 根进程句柄仍是本调用所创建对象，不按名字扫其他进程。
            process.terminate()
            stdout, stderr = process.communicate(timeout=10)
            result.update(exit_code=process.returncode, timed_out=True)
        finally:
            elapsed = time.monotonic() - start
            self.charge(bucket, elapsed, {"name":name})
        (directory / "stdout.txt").write_text(redact(stdout.decode("utf-8", "replace")), encoding="utf-8")
        (directory / "stderr.txt").write_text(redact(stderr.decode("utf-8", "replace")), encoding="utf-8")
        result.update(ended_at=utc(), elapsed_seconds=elapsed,
                      after=identities(), passed=process.returncode == 0 and not result.get("timed_out"))
        atomic_json(directory / "execution.json", result)
        return result


def identities():
    paths = list((ROOT/"backend/app").rglob("*.py")) + list((ROOT/"backend/migrations").glob("*.sql"))
    paths += list((ROOT/"backend/tests").rglob("*.py")) + list((ROOT/"frontend/src").rglob("*"))
    paths += list((ROOT/"frontend/tests").glob("task103-*"))
    result = []
    for path in sorted(set(p for p in paths if p.is_file()), key=str):
        if "__pycache__" not in path.parts:
            result.append({"path":path.relative_to(ROOT).as_posix(),
                           "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    return result


def freeze(directory):
    rows = identities()
    for row in rows:
        target = Path(directory) / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/row["path"]).read_bytes())
    atomic_json(Path(directory)/"identities.json", rows)
    return rows
