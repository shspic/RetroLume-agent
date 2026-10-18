"""仅核自有PID、出生时刻和命令身份，收尾不处理其他服务。"""
import ctypes
from ctypes import wintypes
import json
import subprocess
import time

kernel = ctypes.WinDLL("kernel32", use_last_error=True)
kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
kernel.OpenProcess.restype = wintypes.HANDLE
kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
kernel.GetProcessTimes.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME))
kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
kernel.WaitForSingleObject.restype = wintypes.DWORD
kernel.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)


def state(pid):
    handle = kernel.OpenProcess(0x1000 | 0x100000, False, int(pid))
    if not handle:
        return dict(pid=int(pid), exists=False)
    try:
        values = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(x) for x in values)):
            raise RuntimeError("107自有PID出生时刻无法读取")
        birth = values[0].dwHighDateTime << 32 | values[0].dwLowDateTime
        return dict(pid=int(pid), exists=True, created_100ns=birth, running=kernel.WaitForSingleObject(handle, 0) == 258)
    finally:
        kernel.CloseHandle(handle)


def inventory():
    command = "@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name) | ConvertTo-Json -Depth 3 -Compress"
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError("107进程元数据获取失败")
    values = json.loads(result.stdout or "[]")
    return values if isinstance(values, list) else [values]


def descendants(roots):
    values = inventory(); selected = set(int(x) for x in roots); changed = True
    while changed:
        changed = False
        for row in values:
            if row["ParentProcessId"] in selected and row["ProcessId"] not in selected:
                selected.add(row["ProcessId"]); changed = True
    output = []
    for row in values:
        if row["ProcessId"] not in selected:
            continue
        pid = int(row["ProcessId"])
        command = "Get-CimInstance Win32_Process -Filter 'ProcessId=" + str(pid) + "' | Select-Object -ExpandProperty CommandLine"
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
        output.append(dict(state(pid), name=row["Name"], command=result.stdout.strip(), parent=row["ParentProcessId"]))
    return output


def terminate(expected):
    current = state(expected["pid"])
    if not current.get("exists") or current.get("created_100ns") != expected.get("created_100ns") or not current.get("running"):
        return current
    handle = kernel.OpenProcess(0x1000 | 0x100000 | 1, False, expected["pid"])
    if not handle:
        raise RuntimeError("107自有PID无法收尾")
    try:
        values = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(x) for x in values)):
            raise RuntimeError("107停止前出生时刻核对失败")
        birth = values[0].dwHighDateTime << 32 | values[0].dwLowDateTime
        if birth != expected["created_100ns"]:
            raise RuntimeError("107PID已被复用，不停止")
        if not kernel.TerminateProcess(handle, 0):
            raise RuntimeError("107自有PID停止失败")
        kernel.WaitForSingleObject(handle, 5000)
    finally:
        kernel.CloseHandle(handle)
    return state(expected["pid"])
