"""TASK-083 job-run-07 post-run verification. Read-only.

1. Re-hash run chain + direct deps: prove the batch wrote nothing to sources/fixtures.
2. Parse run-batch-stdout.log JSON lines: extract the controller's observed facts.
3. Precise leftover check for the exact PIDs the controller printed:
   OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION) + GetProcessTimes creation-time
   comparison vs recorded created_100ns. No name/port batch kills; unknown objects
   are reported for manual handling, not guessed at.
4. Supplementary read-only scan for processes whose command line still references
   task083 (clearly NOT a Job-tree-empty proof; supplementary only). Self matches
   (the scan's own powershell command line) are filtered out.
"""
import ctypes
import hashlib
import json
import subprocess
from ctypes import wintypes
from pathlib import Path

ROOT = Path(r"D:\shspic\project_NO3_RetroLume-agent")
EVID = ROOT / "Ndocu" / "evidence" / "task-083" / "job-run-07"

RUN_CHAIN = {
    "backend/tests/fixtures/task083/job_batch.py": "648e419cea693aa10630326cb28176e010a82b9f2c3380c33b42169c19bdef5b",
    "backend/tests/fixtures/task083/job_control.py": "5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2",
    "backend/tests/fixtures/task083/scenario_child.py": "98f132f272b952c22ac887efbf8026c5b00ec618838b6d484a3deec3c73f3f36",
    "backend/tests/fixtures/task083/fixture.py": "c9970b8ddc718da1a4e83c6d206a67f6bd000d715578e028c0a0964d9f53dc7f",
}
DIRECT_DEPS = {
    "backend/app/worker/windows_job.py": "d05ca259d5c99e6cc8f67c7fcea01667068a2901066b865239e920bd0f5246f6",
    "backend/app/worker/session.py": "502a37436de83fa5e56636d54ae5a4f694639f18c5e474e02749162e4e15f16c",
    "backend/app/worker/command.py": "b0e91c3a2e65de19656b3c902df49a33bdd29dc135bc9c292e7732e300a5e273",
    "backend/app/worker/worker_main.py": "5d065b5e44b678c08dc34c9e611a5dcaaa2d0aa3ed2c6e588fe7a70ca25a1454",
    "backend/app/worker/launcher.py": "703ceb0344e21a174f3d70e81b05ede5635d700ed84f53e26e9ae70037d2acea",
    "backend/app/worker/supervisor_ipc.py": "57be00aead15114673b180b1abb436dde10ef426a618d56f30d0031e3201ac96",
    "backend/app/worker/supervisor_main.py": "98c420e75671b3ad1823ea5a72a3866221e7cb0fc1defe032feb0a5822afb145",
    "backend/app/worker/gate.py": "7e7588a58869038f53d850816c027aab00ecd1270d2c893d1fc4902978d32674",
    "backend/tests/test_worker_session.py": "720385a66045ce9f576bf7753024ee359fda2dfbae1defc081ba73516f18352c",
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(FILETIME)] * 4
kernel32.GetProcessTimes.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL


def probe_pid(pid: int, created_100ns):
    """Read-only existence check for one exact PID. 0x1000 = PROCESS_QUERY_LIMITED_INFORMATION."""
    ctypes.set_last_error(0)
    handle = kernel32.OpenProcess(0x1000, False, int(pid))
    if not handle:
        return {"open": False, "open_last_error": ctypes.get_last_error(),
                "interpretation": "process gone (or query denied) - not provably alive"}
    try:
        times = [FILETIME() for _ in range(4)]
        ok = kernel32.GetProcessTimes(handle, *(ctypes.byref(x) for x in times))
        if not ok:
            return {"open": True, "get_times": False, "get_times_last_error": ctypes.get_last_error(),
                    "interpretation": "alive but creation time unreadable - unconfirmed"}
        stamp = (int(times[0].dwHighDateTime) << 32) | int(times[0].dwLowDateTime)
        if created_100ns is None:
            return {"open": True, "alive": True, "creation_100ns_now": stamp,
                    "interpretation": "alive; no recorded creation time to compare - needs manual attribution"}
        if stamp == int(created_100ns):
            return {"open": True, "alive": True, "creation_100ns_now": stamp,
                    "interpretation": "LEFTOVER: same exact PID AND creation time as this run's worker"}
        return {"open": True, "alive": True, "creation_100ns_now": stamp,
                "interpretation": "PID reused by a different process; original worker gone"}
    finally:
        kernel32.CloseHandle(handle)


report = {"tool": "post_check_07.py", "hash_recheck": {}, "stdout_lines": [], "pid_checks": [], "supplementary_scan": None}

# 1. zero-write proof
for rel, expect in {**RUN_CHAIN, **DIRECT_DEPS}.items():
    p = ROOT / rel
    actual = sha256(p) if p.exists() else None
    report["hash_recheck"][rel] = {"sha256": actual, "expected": expect, "unchanged": actual == expect}

# 2. parse controller output
raw = (EVID / "run-batch-stdout.log").read_text(encoding="utf-8", errors="replace")
for line in raw.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        report["stdout_lines"].append(json.loads(line))
    except ValueError:
        report["stdout_lines"].append({"unparsed_line": line})

# 3. precise PID checks for PIDs actually printed by the controller
for obj in report["stdout_lines"]:
    if not isinstance(obj, dict) or obj.get("status") != "observed":
        continue
    mode = obj.get("mode")
    pid = obj.get("pid")
    if pid is None:
        outcome = obj.get("outcome")
        if isinstance(outcome, dict):
            pid = outcome.get("pid")
    created = obj.get("created_100ns")
    if pid is None:
        report["pid_checks"].append({"mode": mode, "pid": None,
                                     "note": "controller output carries no PID for this mode; cleanup evidence is Job ActiveProcesses=0 + cleanup_incomplete=false"})
        continue
    entry = {"mode": mode, "pid": pid, "recorded_created_100ns": created}
    entry.update(probe_pid(pid, created))
    report["pid_checks"].append(entry)

# 4. supplementary read-only command-line scan (NOT a tree-empty proof)
try:
    query = ("Get-CimInstance Win32_Process -Filter \"CommandLine LIKE '%task083%'\" | "
             "Select-Object ProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Compress")
    proc = subprocess.run(["powershell", "-NoProfile", "-Command", query], capture_output=True, text=True, timeout=30)
    entries = []
    if proc.stdout and proc.stdout.strip():
        data = json.loads(proc.stdout)
        if isinstance(data, dict):
            data = [data]
        for item in data or []:
            cmdline = item.get("CommandLine") or ""
            if "Get-CimInstance" in cmdline or "post_check" in cmdline:
                continue  # the scan's own query
            entries.append(item)
    report["supplementary_scan"] = {"available": True, "matches": entries, "note": "read-only name filter; NOT a Job tree-empty proof"}
except Exception as exc:  # noqa: BLE001 - scan is supplementary only
    report["supplementary_scan"] = {"available": False, "error": type(exc).__name__}

out = EVID / "post-run-check.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
summary = {
    "hash_all_unchanged": all(v["unchanged"] for v in report["hash_recheck"].values()),
    "observed_modes": [o.get("mode") for o in report["stdout_lines"] if isinstance(o, dict) and o.get("status") == "observed"],
    "other_lines": [o for o in report["stdout_lines"] if isinstance(o, dict) and o.get("status") != "observed"],
    "pid_checks": report["pid_checks"],
    "supplementary_scan": report["supplementary_scan"],
    "output": str(out),
}
print(json.dumps(summary, ensure_ascii=False))
