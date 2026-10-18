"""新许可、精确资源身份和本卡进程收尾。"""
from __future__ import annotations
import datetime, hashlib, json, os, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "DocuN/evidence/TASK-104"
PERMIT = "TASK-104-G9-AUDIT-20261007"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
DATABASE = "retrolume_task103_g9_main"
APP_ROLE = "retrolume_task103_app"
CIDS = (
    "4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11",
    "f96ac8dcb64648c76a2bc70f3f8b75969ada0ea0ea69b5896fe5ecb71affab85",
    "4b813f9e4317aef9c613eb140fcb2d40c55a6bd98ee5d79807ea5851975d7f68",
)
SECRETS = set()

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()

def clean(value):
    if isinstance(value, str):
        for secret in SECRETS:
            if secret:
                value = value.replace(secret, "[已脱敏]")
        return value
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value

def write(path, value):
    path = Path(path).resolve()
    if not path.is_relative_to(EVIDENCE.resolve()):
        raise RuntimeError("证据路径越界")
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".tmp")
    pending.write_text(json.dumps(clean(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)

class Control:
    def __init__(self):
        self.path = EVIDENCE / "runtime-ledger.json"
        if self.path.exists():
            self.state = json.loads(self.path.read_text("utf-8"))
            if self.state["permit"] != PERMIT:
                raise RuntimeError("新账许可不匹配")
        else:
            receipt = json.loads((EVIDENCE / "audit/audit-receipt.json").read_text("utf-8"))
            self.state = {
                "permit": PERMIT,
                "fixed_active_origin": receipt["fixed_active_monotonic_origin"],
                "fixed_active_deadline": receipt["fixed_active_deadline"],
                "counts": dict.fromkeys(("entry", "container_start", "listener_start", "browser", "driver", "fixture_offline", "password_reset"), 0),
                "limits": {"entry": 3, "container_start": 3, "listener_start": 3, "browser": 3, "driver": 3, "fixture_offline": 3, "password_reset": 1},
                "used": {"real": 0.0, "cleanup": 0.0, "fixture_offline": 0.0},
                "seconds": {"real": 600, "cleanup": 300, "fixture_offline": 300},
                "events": [],
                "business_writes": 0,
                "build": 0, "SUP": 0, "model": 0, "tool": 0,
            }
            self.save()
        self.deadline = None
        self.cleanup_mode = False

    def save(self):
        write(self.path, self.state)

    def reserve(self, kind, detail=None):
        if time.monotonic() >= self.state["fixed_active_deadline"]:
            raise RuntimeError("主动预算已到限")
        if self.state["counts"][kind] >= self.state["limits"][kind]:
            raise RuntimeError("动作次数已到限 " + kind)
        self.state["counts"][kind] += 1
        self.state["events"].append({"at": stamp(), "monotonic": time.monotonic(), "kind": kind, "number": self.state["counts"][kind], "detail": detail})
        self.save()

    def remaining(self, maximum=20):
        remaining = maximum if self.cleanup_mode else min(self.state["fixed_active_deadline"] - time.monotonic(), maximum)
        if self.deadline is not None:
            remaining = min(remaining, self.deadline - time.monotonic())
        if remaining <= 0:
            raise RuntimeError("当前分项截止已到")
        return remaining

    def begin_root(self):
        self.reserve("entry", {"scope": "GET/SELECT 引用迟到补证"})
        self.started = time.monotonic()
        allowed = min(300, 600 - self.state["used"]["real"], self.state["fixed_active_deadline"] - self.started - 300)
        if allowed <= 0 or self.state["used"]["cleanup"] >= 300:
            raise RuntimeError("没有可保留清理额的真实预算")
        self.deadline = self.started + allowed
        return self.state["counts"]["entry"]

    def begin_cleanup(self):
        self.state["used"]["real"] += time.monotonic() - self.started
        self.state["events"].append({"at": stamp(), "kind": "真实阶段结束", "elapsed": time.monotonic() - self.started})
        self.cleanup_started = time.monotonic()
        self.cleanup_mode = True
        self.deadline = self.cleanup_started + (300 - self.state["used"]["cleanup"])
        self.save()

    def end_cleanup(self):
        self.state["used"]["cleanup"] += time.monotonic() - self.cleanup_started
        self.state["events"].append({"at": stamp(), "kind": "清理结束"})
        self.deadline = None
        self.cleanup_mode = False
        self.save()

def command(argv, timeout=15, cwd=None, env=None):
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)

def inspect_owned(slot):
    response = command(["docker", "inspect", CIDS[slot - 1]])
    if response.returncode:
        raise RuntimeError("精确容器 inspect 失败")
    raw = json.loads(response.stdout)[0]
    public = {
        "cid": raw["Id"], "name": raw["Name"].lstrip("/"), "image": raw["Image"],
        "running": raw["State"]["Running"], "pid": raw["State"]["Pid"], "exit_code": raw["State"]["ExitCode"],
        "labels": raw["Config"].get("Labels", {}), "mounts": raw["Mounts"],
        "limits": {k: raw["HostConfig"].get(k) for k in ("NanoCpus", "Memory", "PidsLimit", "Privileged")},
        "restart": raw["HostConfig"]["RestartPolicy"]["Name"],
        "ports": raw["HostConfig"]["PortBindings"],
    }
    assert public["cid"] == CIDS[slot - 1] and public["image"] == IMAGE
    assert public["name"] == "retrolume-task-103-g9-pg" + str(slot)
    assert public["labels"].get("retrolume.permit") == "TASK-103-G9-20261006"
    assert public["labels"].get("retrolume.task") == "TASK-103" and public["labels"].get("retrolume.synthetic") == "true"
    assert public["restart"] == "no" and not public["limits"]["Privileged"]
    assert public["limits"]["NanoCpus"] == 1000000000 and public["limits"]["Memory"] == 536870912 and public["limits"]["PidsLimit"] == 128
    assert not raw["HostConfig"].get("Binds") and len(public["mounts"]) == 1
    mount = public["mounts"][0]
    assert mount["Type"] == "volume" and mount["Name"] == public["name"] + "-data"
    assert mount["Destination"] == "/var/lib/postgresql/data"
    assert public["ports"] == {"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(55442 + slot)}]}
    return public, raw

def process_tree(pid):
    text = "$taskAll=@(Get-CimInstance Win32_Process); $taskIds=[System.Collections.Generic.HashSet[int]]::new(); [void]$taskIds.Add(" + str(int(pid)) + "); $taskChanged=$true; while($taskChanged){$taskChanged=$false; foreach($taskProc in $taskAll){if($taskIds.Contains([int]$taskProc.ParentProcessId)){if($taskIds.Add([int]$taskProc.ProcessId)){$taskChanged=$true}}}}; @($taskAll | Where-Object {$taskIds.Contains([int]$_.ProcessId)} | ForEach-Object {[pscustomobject]@{pid=$_.ProcessId;parent=$_.ParentProcessId;created=$_.CreationDate.ToUniversalTime().ToString('o');command=$_.CommandLine;exe=$_.ExecutablePath}}) | ConvertTo-Json -Compress"
    result = command(["powershell.exe", "-NoProfile", "-Command", text], timeout=12)
    if result.returncode:
        raise RuntimeError("本卡进程出生身份读取失败")
    value = json.loads(result.stdout or "[]")
    return value if isinstance(value, list) else [value]

def process_one(pid):
    return next((v for v in process_tree(pid) if v["pid"] == pid), None)

def stop_witness(witness):
    actual = process_one(witness["pid"])
    if actual is None:
        return {"pid": witness["pid"], "state": "absent"}
    if actual["created"] != witness["created"] or actual["command"] != witness["command"]:
        return {"pid": witness["pid"], "state": "identity_changed_not_stopped"}
    result = command(["powershell.exe", "-NoProfile", "-Command", "Stop-Process -Id " + str(int(witness["pid"])) + " -Force"], timeout=8)
    return {"pid": witness["pid"], "state": "stopped" if process_one(witness["pid"]) is None else "unconfirmed", "exit_code": result.returncode}
