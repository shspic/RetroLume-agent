"""本卡子进程句柄、出生时点与命令身份；不按名字扫进程。"""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import json
import subprocess
from .control import BudgetDenied,ROOT

k=ctypes.WinDLL("kernel32",use_last_error=True)
k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
k.CloseHandle.argtypes=[wintypes.HANDLE]
k.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(wintypes.FILETIME)]*4)]
k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]


def process_state(pid):
    if type(pid) is not int or pid<=0:raise BudgetDenied("invalid pid")
    handle=k.OpenProcess(0x1000|0x100000,False,pid)
    if not handle:return {"pid":pid,"exists":False}
    try:
        times=[wintypes.FILETIME() for _ in range(4)];code=wintypes.DWORD()
        if not k.GetProcessTimes(handle,*[ctypes.byref(x) for x in times]) or not k.GetExitCodeProcess(handle,ctypes.byref(code)):
            raise BudgetDenied("unknown process identity")
        return {"pid":pid,"exists":True,"created_100ns":(times[0].dwHighDateTime<<32)|times[0].dwLowDateTime,
                "running":code.value==259,"exit_code":None if code.value==259 else code.value}
    finally:k.CloseHandle(handle)


def witness_matches(actual,expected,command):
    if actual.get("pid")!=expected.get("pid") or actual.get("created_100ns")!=expected.get("created_100ns"):
        raise BudgetDenied("process identity changed")
    if type(command) is not str or expected["module"] not in command or str(ROOT).lower() not in command.lower():
        raise BudgetDenied("process command identity changed")
    return True


def stop_owned(process,witness):
    state=process_state(witness["pid"])
    if not state["exists"] or not state.get("running"):
        return state
    cmd=f"(Get-CimInstance Win32_Process -Filter 'ProcessId={witness['pid']}').CommandLine"
    result=subprocess.run(["powershell.exe","-NoProfile","-Command",cmd],capture_output=True,timeout=15,
                          creationflags=subprocess.CREATE_NO_WINDOW)
    witness_matches(state,witness,result.stdout.decode("utf-8","replace").strip())
    # Popen保有本调用创建的句柄，PID复用校验后只停这个实例。
    process.terminate();process.wait(timeout=15)
    after=process_state(witness["pid"])
    if after.get("running"):raise BudgetDenied("owned process stop unconfirmed")
    return after

