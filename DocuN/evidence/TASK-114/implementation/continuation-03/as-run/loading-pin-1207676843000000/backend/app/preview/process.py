"""Windows出生身份与独占owner，不把拒绝读取当作进程死亡。"""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import secrets
import base64
import time


class OwnershipUnknown(RuntimeError):pass


class _Blob(ctypes.Structure):
    _fields_=[("size",wintypes.DWORD),("data",ctypes.POINTER(ctypes.c_ubyte))]


def protect_control_key(value):
    """只持久化当前Windows用户DPAPI密文，不把控制秘密写入证据或argv。"""
    return _crypt(value.encode("ascii"),False)


def unprotect_control_key(value):return _crypt(base64.b64decode(value,validate=True),True).decode("ascii")


def _crypt(data,decode):
    api=ctypes.WinDLL("crypt32",use_last_error=True);kernel=ctypes.WinDLL("kernel32",use_last_error=True)
    storage=(ctypes.c_ubyte*len(data)).from_buffer_copy(data);source=_Blob(len(data),storage);target=_Blob()
    fn=api.CryptUnprotectData if decode else api.CryptProtectData
    fn.argtypes=(ctypes.POINTER(_Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(_Blob));fn.restype=wintypes.BOOL
    kernel.LocalFree.argtypes=(ctypes.c_void_p,);kernel.LocalFree.restype=ctypes.c_void_p
    if not fn(ctypes.byref(source),None,None,None,None,1,ctypes.byref(target)):raise OwnershipUnknown("control_key_protection_failed")
    try:
        raw=ctypes.string_at(target.data,target.size)
        return raw if decode else base64.b64encode(raw).decode("ascii")
    finally:kernel.LocalFree(target.data)


def birth(pid):
    if type(pid) is not int or pid<1:return {"state":"unknown","error":"invalid_pid"}
    api=ctypes.WinDLL("kernel32",use_last_error=True)
    api.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);api.OpenProcess.restype=wintypes.HANDLE
    api.CloseHandle.argtypes=(wintypes.HANDLE,)
    api.GetProcessTimes.argtypes=(wintypes.HANDLE,ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME))
    api.GetExitCodeProcess.argtypes=(wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD))
    handle=api.OpenProcess(0x1000,False,pid)
    if not handle:
        error=ctypes.get_last_error()
        return {"state":"exited"} if error==87 else {"state":"unknown","error_code":error}
    try:
        code=wintypes.DWORD()
        if not api.GetExitCodeProcess(handle,ctypes.byref(code)):return {"state":"unknown","error_code":ctypes.get_last_error()}
        if code.value!=259:return {"state":"exited","exit_code":code.value}
        values=[wintypes.FILETIME() for _ in range(4)]
        if not api.GetProcessTimes(handle,*[ctypes.byref(v) for v in values]):return {"state":"unknown","error_code":ctypes.get_last_error()}
        return {"state":"running","birth":(values[0].dwHighDateTime<<32)+values[0].dwLowDateTime}
    finally:api.CloseHandle(handle)


def terminate_owned(pid,expected_birth):
    """只对已登记出生身份的自有CLI/救援进程终止，不按名字或复用PID杀进程。"""
    snapshot=birth(pid)
    if snapshot["state"]=="exited":return True
    if snapshot["state"]!="running" or snapshot["birth"]!=expected_birth:raise OwnershipUnknown("process_ownership_unconfirmed")
    api=ctypes.WinDLL("kernel32",use_last_error=True)
    api.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);api.OpenProcess.restype=wintypes.HANDLE
    api.GetProcessTimes.argtypes=(wintypes.HANDLE,ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME),ctypes.POINTER(wintypes.FILETIME))
    api.TerminateProcess.argtypes=(wintypes.HANDLE,wintypes.UINT);api.WaitForSingleObject.argtypes=(wintypes.HANDLE,wintypes.DWORD);api.CloseHandle.argtypes=(wintypes.HANDLE,)
    # TERMINATE | SYNCHRONIZE | QUERY_LIMITED_INFORMATION；出生核对也需要查询权。
    handle=api.OpenProcess(0x101001,False,pid)
    if not handle:raise OwnershipUnknown("process_ownership_unconfirmed")
    try:
        values=[wintypes.FILETIME() for _ in range(4)]
        # 同一handle再核出生，防止查询到打开handle之间发生PID复用。
        if not api.GetProcessTimes(handle,*[ctypes.byref(v) for v in values]) or ((values[0].dwHighDateTime<<32)+values[0].dwLowDateTime)!=expected_birth:
            raise OwnershipUnknown("process_ownership_unconfirmed")
        if not api.TerminateProcess(handle,1) or api.WaitForSingleObject(handle,2000)!=0:raise OwnershipUnknown("process_exit_unconfirmed")
        return True
    finally:api.CloseHandle(handle)


def atomic_json(path,value):
    path=Path(path);temporary=path.with_name(path.name+"."+secrets.token_hex(8)+".new")
    with temporary.open("x",encoding="utf-8") as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False);stream.flush();os.fsync(stream.fileno())
    # Windows读者短暂持有旧文件时，替换可能返回共享拒绝；有界等待不延业务截止。
    until=time.monotonic()+.1
    while True:
        try:os.replace(temporary,path);break
        except PermissionError:
            if time.monotonic()>=until:raise
            time.sleep(.005)


class GlobalOwner:
    def __init__(self,name):
        if not name.startswith("Global\\RetroLumePreviewV2"):raise OwnershipUnknown("owner_namespace")
        self.name=name
        self.api=ctypes.WinDLL("kernel32",use_last_error=True)
        self.api.CreateMutexW.argtypes=(ctypes.c_void_p,wintypes.BOOL,wintypes.LPCWSTR);self.api.CreateMutexW.restype=wintypes.HANDLE
        self.api.WaitForSingleObject.argtypes=(wintypes.HANDLE,wintypes.DWORD);self.api.ReleaseMutex.argtypes=(wintypes.HANDLE,);self.api.CloseHandle.argtypes=(wintypes.HANDLE,)
        self.handle=self.api.CreateMutexW(None,False,name)
        if not self.handle:raise OwnershipUnknown("owner_unavailable")
        self.held=False
    def acquire(self):
        result=self.api.WaitForSingleObject(self.handle,0)
        if result==0:self.held=True;return "acquired"
        if result==0x80:self.held=True;return "abandoned"
        if result==0x102:return "busy"
        raise OwnershipUnknown("owner_unknown")
    def release(self):
        if self.held:self.api.ReleaseMutex(self.handle);self.held=False
    def close(self):
        self.release()
        if self.handle:self.api.CloseHandle(self.handle);self.handle=None

    def identity(self):
        """核真实内核对象路径，不用传入Global字样代替作用域证据。"""
        class Unicode(ctypes.Structure):
            _fields_=[("length",wintypes.USHORT),("maximum",wintypes.USHORT),("buffer",ctypes.c_void_p)]
        api=ctypes.WinDLL("ntdll");fn=api.NtQueryObject
        fn.argtypes=(wintypes.HANDLE,wintypes.ULONG,ctypes.c_void_p,wintypes.ULONG,ctypes.POINTER(wintypes.ULONG));fn.restype=ctypes.c_long
        data=ctypes.create_string_buffer(4096);needed=wintypes.ULONG()
        if fn(self.handle,1,data,len(data),ctypes.byref(needed))<0:raise OwnershipUnknown("owner_object_path_unknown")
        value=Unicode.from_buffer(data)
        if value.length>4000 or not value.buffer:raise OwnershipUnknown("owner_object_path_unknown")
        name=ctypes.wstring_at(value.buffer,value.length//2)
        if name!="\\BaseNamedObjects\\"+self.name.removeprefix("Global\\"):raise OwnershipUnknown("owner_scope_mismatch")
        return {"requested_name":self.name,"kernel_object_path":name,"held":self.held,"scope":"same trusted deployment owner, global kernel namespace"}
