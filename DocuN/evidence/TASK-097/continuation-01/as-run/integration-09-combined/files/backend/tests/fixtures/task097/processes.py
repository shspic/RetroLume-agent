"""精确PID与真实创建时间匹配后才清理本卡进程。"""
import ctypes
from ctypes import wintypes
import json
import subprocess


def identity(pid):
    api=ctypes.WinDLL("kernel32",use_last_error=True)
    api.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];api.OpenProcess.restype=wintypes.HANDLE
    api.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(wintypes.FILETIME)]*4)];api.GetProcessTimes.restype=wintypes.BOOL
    api.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];api.WaitForSingleObject.restype=wintypes.DWORD
    api.CloseHandle.argtypes=[wintypes.HANDLE];api.CloseHandle.restype=wintypes.BOOL
    handle=api.OpenProcess(0x00100000|0x1000,False,pid)
    if not handle:return None
    try:
        values=[wintypes.FILETIME() for _ in range(4)]
        if not api.GetProcessTimes(handle,*[ctypes.byref(v) for v in values]):raise OSError("进程创建时间不可核")
        created=(values[0].dwHighDateTime<<32)|values[0].dwLowDateTime
        return {"pid":pid,"created_100ns":created,"alive":api.WaitForSingleObject(handle,0)==0x102}
    finally:api.CloseHandle(handle)


def cleanup(out):
    owned=[]
    path=out/"owned-processes.json"
    if path.exists():owned+=json.loads(path.read_text(encoding="utf-8"))
    for file in out.glob("sup-launch-*.json"):
        fact=json.loads(file.read_text(encoding="utf-8"))
        if fact.get("created"):owned.append({"pid":fact["pid"],"created_100ns":fact["created_100ns"],"kind":"SUP"})
    report=[]
    for expected in owned:
        current=identity(expected["pid"])
        same=current is not None and current["created_100ns"]==expected["created_100ns"]
        action="already_exited"
        if same and current["alive"]:
            result=subprocess.run(["taskkill","/PID",str(expected["pid"]),"/T","/F"],capture_output=True,timeout=15)
            action="own_tree_terminated" if result.returncode==0 else "termination_failed"
        after=identity(expected["pid"])
        zero=after is None or after["created_100ns"]!=expected["created_100ns"] or not after["alive"]
        report.append({**expected,"action":action,"zero":zero})
    (out/"process-cleanup.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return all(x["zero"] for x in report)
