"""Exact-anchor Windows handle/identity repair; source hash checked by caller."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "backend/app/worker/windows_job.py"
data = path.read_text(encoding="utf-8")


def once(old: str, new: str) -> None:
    global data
    assert data.count(old) == 1, data.count(old)
    data = data.replace(old, new)


once(
    "class _IO_COUNTERS(ctypes.Structure):\n",
    "class _FILETIME(ctypes.Structure):\n    _fields_ = [(\"dwLowDateTime\", wintypes.DWORD), (\"dwHighDateTime\", wintypes.DWORD)]\n\n\nclass _IO_COUNTERS(ctypes.Structure):\n",
)
once(
    "    api.GetExitCodeProcess.restype = wintypes.BOOL\n",
    "    api.GetExitCodeProcess.restype = wintypes.BOOL\n    api.GetProcessTimes.argtypes = [wintypes.HANDLE, ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME)]\n    api.GetProcessTimes.restype = wintypes.BOOL\n",
)
once(
    "    def close(self) -> None:\n        if self.owned:\n            self.api.ReleaseMutex(self.handle)\n            self.owned = False\n        if self.handle:\n            self.api.CloseHandle(self.handle)\n            self.handle = None\n",
    "    def close(self) -> None:\n        failures = []\n        if self.owned:\n            if not self.api.ReleaseMutex(self.handle):\n                failures.append(\"ReleaseMutex\")\n            else:\n                self.owned = False\n        if self.handle:\n            if not self.api.CloseHandle(self.handle):\n                failures.append(\"CloseHandle(mutex)\")\n            else:\n                self.handle = None\n        if failures:\n            raise JobUnknown(\"/\".join(failures))\n",
)
once(
    "    @property\n    def pid(self) -> int | None:\n",
    "    def process_creation_time_100ns(self) -> int:\n        if not self.process.hProcess:\n            raise JobUnknown(\"主进程句柄不存在\")\n        created, exited, kernel, user = (_FILETIME() for _ in range(4))\n        if not self.api.GetProcessTimes(self.process.hProcess, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)):\n            raise _error(\"GetProcessTimes\")\n        return (int(created.dwHighDateTime) << 32) | int(created.dwLowDateTime)\n\n    @property\n    def pid(self) -> int | None:\n",
)
once(
    "    def close(self) -> None:\n        if self.process.hThread:\n            self.api.CloseHandle(self.process.hThread)\n            self.process.hThread = None\n        if self.process.hProcess:\n            self.api.CloseHandle(self.process.hProcess)\n            self.process.hProcess = None\n        if self.handle:\n            self.api.CloseHandle(self.handle)\n            self.handle = None\n",
    "    def close(self) -> None:\n        failures = []\n        for label, holder, field in (\n            (\"thread\", self.process, \"hThread\"),\n            (\"process\", self.process, \"hProcess\"),\n            (\"job\", self, \"handle\"),\n        ):\n            handle = getattr(holder, field)\n            if handle:\n                if self.api.CloseHandle(handle):\n                    setattr(holder, field, None)\n                else:\n                    failures.append(label)\n        if failures:\n            raise JobUnknown(\"CloseHandle失败: \" + \",\".join(failures))\n",
)
path.write_text(data, encoding="utf-8", newline="")
