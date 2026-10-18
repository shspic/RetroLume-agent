"""可信本地根、稳定文件对象锁和不得覆盖的准确发布。"""
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import stat
import time
from .contracts import DataError


def safe_root(value):
    path = Path(value)
    if not path.is_absolute() or str(path).startswith(("\\\\", "//")):
        raise DataError("storage_unavailable", 503)
    for part in reversed((path, *path.parents)):
        info = part.lstat()
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise DataError("storage_unavailable", 503)
    return path


def independent_roots(*roots):
    roots = tuple(safe_root(r) for r in roots)
    for i, a in enumerate(roots):
        for b in roots[i + 1:]:
            if a == b or a in b.parents or b in a.parents:
                raise DataError("storage_unavailable", 503)
    return roots


def regular(path):
    info = Path(path).lstat()
    if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise DataError("integrity_failed", 422)
    return info


def publish(temporary, destination):
    temporary, destination = Path(temporary), Path(destination)
    safe_root(temporary.parent)
    safe_root(destination.parent)
    regular(temporary)
    with temporary.open("r+b") as stream:
        os.fsync(stream.fileno())
    os.link(temporary, destination)
    regular(destination)


def private_file(path):
    """新控制文件只给当前 Windows 用户、SYSTEM 和管理员完整访问。"""
    path=Path(path)
    regular(path)
    if os.name!='nt':
        os.chmod(path,0o600);return
    api=ctypes.WinDLL('advapi32',use_last_error=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.GetCurrentProcess.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    kernel.LocalFree.argtypes=[ctypes.c_void_p]
    api.OpenProcessToken.argtypes=[wintypes.HANDLE,wintypes.DWORD,ctypes.POINTER(wintypes.HANDLE)]
    api.GetTokenInformation.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)]
    api.ConvertSidToStringSidW.argtypes=[ctypes.c_void_p,ctypes.POINTER(wintypes.LPWSTR)]
    api.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,ctypes.POINTER(ctypes.c_void_p),ctypes.c_void_p]
    api.SetFileSecurityW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,ctypes.c_void_p]
    token=wintypes.HANDLE();sid_text=wintypes.LPWSTR();descriptor=ctypes.c_void_p()
    try:
        if not api.OpenProcessToken(kernel.GetCurrentProcess(),8,ctypes.byref(token)):raise ctypes.WinError(ctypes.get_last_error())
        length=wintypes.DWORD();api.GetTokenInformation(token,1,None,0,ctypes.byref(length))
        storage=ctypes.create_string_buffer(length.value)
        if not api.GetTokenInformation(token,1,storage,length,ctypes.byref(length)):raise ctypes.WinError(ctypes.get_last_error())
        sid=ctypes.c_void_p.from_buffer(storage).value
        if not api.ConvertSidToStringSidW(sid,ctypes.byref(sid_text)):raise ctypes.WinError(ctypes.get_last_error())
        sddl='D:P(A;;FA;;;SY)(A;;FA;;;BA)(A;;FA;;;'+sid_text.value+')'
        if not api.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl,1,ctypes.byref(descriptor),None):raise ctypes.WinError(ctypes.get_last_error())
        if not api.SetFileSecurityW(str(path),0x80000004,descriptor):raise ctypes.WinError(ctypes.get_last_error())
    finally:
        if descriptor.value:kernel.LocalFree(descriptor)
        if sid_text:kernel.LocalFree(sid_text)
        if token.value:kernel.CloseHandle(token)


if os.name == "nt":
    class Overlapped(ctypes.Structure):
        _fields_ = [("Internal", ctypes.c_size_t), ("InternalHigh", ctypes.c_size_t),
                    ("Offset", wintypes.DWORD), ("OffsetHigh", wintypes.DWORD), ("hEvent", wintypes.HANDLE)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                                  wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.LockFileEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(Overlapped)]
    kernel.UnlockFileEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(Overlapped)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]


class HeldLease:
    def __init__(self, lock, handle, overlapped, exclusive):
        self.lock, self.handle, self.overlapped = lock, handle, overlapped
        self.exclusive, self.live = exclusive, True

    def check(self):
        if not self.live:
            raise DataError("reference_pin_invalid")
        self.lock.check()

    def close(self):
        if not self.live:
            return
        self.live = False
        if os.name == "nt":
            try:
                if not kernel.UnlockFileEx(self.handle, 0, 1, 0, ctypes.byref(self.overlapped)):
                    raise ctypes.WinError(ctypes.get_last_error())
            finally:
                kernel.CloseHandle(self.handle)
        else:
            import fcntl
            fcntl.flock(self.handle, fcntl.LOCK_UN)
            os.close(self.handle)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class RootLease:
    """每次取锁使用非继承句柄，常驻句柄禁止锁文件被删除或替换。"""
    def __init__(self, root, name=".reference.lock"):
        self.root = safe_root(root)
        if name not in (".reference.lock", ".journal.lock", ".mutation.lock", ".operation.lock", ".admission.lock"):
            raise ValueError("锁名称未受信")
        self.path = self.root / name
        self._keeper = self._open()
        self.identity = self._identity()

    def _identity(self):
        info = regular(self.path)
        return info.st_dev, info.st_ino

    def check(self):
        safe_root(self.root)
        if self.identity != self._identity():
            raise DataError("storage_unavailable", 503)

    def _open(self):
        safe_root(self.root)
        if self.path.exists():
            regular(self.path)
        if os.name == "nt":
            handle = kernel.CreateFileW(str(self.path), 0x80000000 | 0x40000000, 3, None, 4, 0x00200000, None)
            if handle == ctypes.c_void_p(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            return handle
        return os.open(self.path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)

    def acquire(self, exclusive=False, timeout=30):
        self.check()
        handle = self._open()
        end = time.monotonic() + timeout
        overlapped = Overlapped() if os.name == "nt" else None
        try:
            while True:
                if os.name == "nt":
                    ok = kernel.LockFileEx(handle, 1 | (2 if exclusive else 0), 0, 1, 0, ctypes.byref(overlapped))
                    if not ok and ctypes.get_last_error() not in (33, 158):
                        raise ctypes.WinError(ctypes.get_last_error())
                else:
                    import fcntl
                    try:
                        fcntl.flock(handle, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
                        ok = True
                    except BlockingIOError:
                        ok = False
                if ok:
                    self.check()
                    return HeldLease(self, handle, overlapped, exclusive)
                if time.monotonic() >= end:
                    raise DataError("operation_timeout", 504)
                time.sleep(min(0.01, max(0, end - time.monotonic())))
        except BaseException:
            if os.name == "nt":
                kernel.CloseHandle(handle)
            else:
                os.close(handle)
            raise

    def close(self):
        handle, self._keeper = self._keeper, None
        if handle is not None:
            kernel.CloseHandle(handle) if os.name == "nt" else os.close(handle)

    def __del__(self):
        try:
            if getattr(self,'_keeper',None) is not None:self.close()
        except Exception:pass
