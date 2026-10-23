"""本卡只需的Windows内存、当前SID、文件归属、端口及自有进程实体观察。"""
import ctypes as c
from ctypes import wintypes as w
import os
from pathlib import Path
import socket

kernel = c.WinDLL("kernel32", use_last_error=True)
advapi = c.WinDLL("advapi32", use_last_error=True)
kernel.GetCurrentProcess.restype = w.HANDLE
kernel.CloseHandle.argtypes = [w.HANDLE]
kernel.LocalFree.argtypes = [c.c_void_p]


def require(value):
    if not value:
        raise OSError(c.get_last_error(), "native_observation_failed")


class Memory(c.Structure):
    _fields_ = [("length", w.DWORD), ("load", w.DWORD)] + [(name, c.c_ulonglong) for name in (
        "total_phys", "available_phys", "total_page", "available_page", "total_virtual", "available_virtual", "extended")]


def available_mib():
    info = Memory()
    info.length = c.sizeof(info)
    require(kernel.GlobalMemoryStatusEx(c.byref(info)))
    return info.available_phys / 1048576


def sid_string(sid):
    value = w.LPWSTR()
    advapi.ConvertSidToStringSidW.argtypes = [c.c_void_p, c.POINTER(w.LPWSTR)]
    require(advapi.ConvertSidToStringSidW(sid, c.byref(value)))
    try:
        return value.value
    finally:
        kernel.LocalFree(value)


def current_sid():
    token, length = w.HANDLE(), w.DWORD()
    advapi.OpenProcessToken.argtypes = [w.HANDLE, w.DWORD, c.POINTER(w.HANDLE)]
    advapi.GetTokenInformation.argtypes = [w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.POINTER(w.DWORD)]
    require(advapi.OpenProcessToken(kernel.GetCurrentProcess(), 8, c.byref(token)))
    try:
        advapi.GetTokenInformation(token, 1, None, 0, c.byref(length))
        buffer = c.create_string_buffer(length.value)
        require(advapi.GetTokenInformation(token, 1, buffer, length, c.byref(length)))
        return sid_string(c.c_void_p.from_buffer(buffer).value)
    finally:
        kernel.CloseHandle(token)


def owner_sid(path):
    owner, descriptor = c.c_void_p(), c.c_void_p()
    advapi.GetNamedSecurityInfoW.argtypes = [w.LPWSTR, w.DWORD, w.DWORD, c.POINTER(c.c_void_p),
        c.c_void_p, c.c_void_p, c.c_void_p, c.POINTER(c.c_void_p)]
    result = advapi.GetNamedSecurityInfoW(str(path), 1, 1, c.byref(owner), None, None, None, c.byref(descriptor))
    if result:
        raise OSError(result, "owner_observation_failed")
    try:
        return sid_string(owner)
    finally:
        kernel.LocalFree(descriptor)


def file_identity(path):
    path = Path(path)
    info = path.lstat()
    if getattr(info, "st_file_attributes", 0) & 0x400:
        raise OSError("reparse_refused")
    return {"path": str(path), "device": info.st_dev, "file_id": info.st_ino, "owner_sid": owner_sid(path)}


class Tcp4(c.Structure):
    _fields_ = [(name, w.DWORD) for name in ("state", "local_address", "local_port", "remote_address", "remote_port", "pid")]


class Tcp6(c.Structure):
    _fields_ = [("local_address", c.c_ubyte * 16), ("local_scope", w.DWORD), ("local_port", w.DWORD),
               ("remote_address", c.c_ubyte * 16), ("remote_scope", w.DWORD), ("remote_port", w.DWORD),
               ("state", w.DWORD), ("pid", w.DWORD)]


def port_owners(ports):
    api = c.WinDLL("iphlpapi", use_last_error=True)
    api.GetExtendedTcpTable.argtypes = [c.c_void_p, c.POINTER(w.ULONG), w.BOOL, w.ULONG, c.c_int, w.ULONG]
    found = []
    for family, row_type in ((2, Tcp4), (23, Tcp6)):
        size = w.ULONG()
        api.GetExtendedTcpTable(None, c.byref(size), False, family, 5, 0)
        buffer = c.create_string_buffer(size.value)
        result = api.GetExtendedTcpTable(buffer, c.byref(size), False, family, 5, 0)
        if result:
            raise OSError(result, "port_owner_observation_failed")
        count = w.DWORD.from_buffer(buffer).value
        for index in range(count):
            row = row_type.from_buffer(buffer, 4 + index * c.sizeof(row_type))
            port = socket.ntohs(row.local_port & 65535)
            if port in ports:
                found.append({"family": family, "port": port, "pid": row.pid, "state": row.state})
    return found


class ProcessRef:
    def __init__(self, pid):
        kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        kernel.OpenProcess.restype = w.HANDLE
        kernel.GetProcessTimes.argtypes = [w.HANDLE] + [c.POINTER(w.FILETIME)] * 4
        kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
        kernel.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
        self.pid = pid
        self.handle = kernel.OpenProcess(0x100000 | 0x1000 | 1, False, pid)
        require(self.handle)
        created, ended, kern, user = (w.FILETIME() for unused in range(4))
        require(kernel.GetProcessTimes(self.handle, c.byref(created), c.byref(ended), c.byref(kern), c.byref(user)))
        self.birth = created.dwLowDateTime | created.dwHighDateTime << 32

    def alive(self):
        return kernel.WaitForSingleObject(self.handle, 0) == 258

    def stop(self):
        if self.alive():
            require(kernel.TerminateProcess(self.handle, 2))

    def close(self):
        kernel.CloseHandle(self.handle)


def descendants(parent_pid):
    class Entry(c.Structure):
        _fields_ = [("size", w.DWORD), ("usage", w.DWORD), ("pid", w.DWORD), ("heap", c.c_size_t),
                    ("module", w.DWORD), ("threads", w.DWORD), ("parent", w.DWORD), ("priority", w.LONG),
                    ("flags", w.DWORD), ("exe", w.WCHAR * 260)]
    kernel.CreateToolhelp32Snapshot.argtypes = [w.DWORD, w.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = w.HANDLE
    kernel.Process32FirstW.argtypes = [w.HANDLE, c.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [w.HANDLE, c.POINTER(Entry)]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == c.c_void_p(-1).value:
        raise OSError("process_snapshot_failed")
    try:
        rows, entry = [], Entry()
        entry.size = c.sizeof(entry)
        more = kernel.Process32FirstW(snapshot, c.byref(entry))
        while more:
            rows.append((entry.pid, entry.parent))
            more = kernel.Process32NextW(snapshot, c.byref(entry))
        found = {parent_pid}
        while True:
            expanded = found | {pid for pid, parent in rows if parent in found}
            if expanded == found:
                return sorted(found - {parent_pid})
            found = expanded
    finally:
        kernel.CloseHandle(snapshot)


class Blob(c.Structure):
    _fields_ = [("length", w.DWORD), ("data", c.POINTER(c.c_ubyte))]


def protect_secret(raw, *, decrypt=False):
    """仅本轮私有根的用户DPAPI二进制；真实秘密不序列化到JSON。"""
    crypt = c.WinDLL("crypt32", use_last_error=True)
    buffer = (c.c_ubyte * len(raw)).from_buffer_copy(raw)
    source, target = Blob(len(raw), buffer), Blob()
    if decrypt:
        fn = crypt.CryptUnprotectData
        fn.argtypes = [c.POINTER(Blob), c.c_void_p, c.c_void_p, c.c_void_p, c.c_void_p, w.DWORD, c.POINTER(Blob)]
        require(fn(c.byref(source), None, None, None, None, 1, c.byref(target)))
    else:
        fn = crypt.CryptProtectData
        fn.argtypes = [c.POINTER(Blob), w.LPCWSTR, c.c_void_p, c.c_void_p, c.c_void_p, w.DWORD, c.POINTER(Blob)]
        require(fn(c.byref(source), "TASK-127", None, None, None, 1, c.byref(target)))
    try:
        return c.string_at(target.data, target.length)
    finally:
        kernel.LocalFree(target.data)
