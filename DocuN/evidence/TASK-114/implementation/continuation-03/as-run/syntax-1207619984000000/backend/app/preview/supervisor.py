"""容器外的精确资源身份、有限Docker调用和Windows进程出生核对。"""
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
import subprocess
import time

PERMIT = "TASK-109-G11-20261009"
INSPECT_FORMAT = '{"id":{{json .Id}},"image":{{json .Image}},"labels":{{json .Config.Labels}},"user":{{json .Config.User}},"state":{{json .State}},"host":{{json .HostConfig}},"mounts":{{json .Mounts}},"ports":{{json .NetworkSettings.Ports}}}'


def clean_env():
    names = ("SystemRoot", "WINDIR", "PATH", "TEMP", "TMP", "LOCALAPPDATA", "USERPROFILE", "PROGRAMFILES", "PROGRAMFILES(X86)")
    return {name: os.environ[name] for name in names if name in os.environ}


def process_birth(pid):
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    api.OpenProcess.restype = wintypes.HANDLE
    api.GetProcessTimes.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME))
    api.GetProcessTimes.restype = wintypes.BOOL
    api.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    api.GetExitCodeProcess.restype = wintypes.BOOL
    api.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = api.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        exit_code = wintypes.DWORD()
        if not api.GetExitCodeProcess(handle, ctypes.byref(exit_code)) or exit_code.value != 259:
            return None
        values = [wintypes.FILETIME() for _ in range(4)]
        if not api.GetProcessTimes(handle, ctypes.byref(values[0]), ctypes.byref(values[1]), ctypes.byref(values[2]), ctypes.byref(values[3])):
            return None
        return (values[0].dwHighDateTime << 32) + values[0].dwLowDateTime
    finally:
        api.CloseHandle(handle)


def docker_call(docker, args, timeout=2):
    start = time.monotonic_ns()
    value = subprocess.run([docker] + args, capture_output=True, timeout=timeout, env=clean_env(), creationflags=subprocess.CREATE_NO_WINDOW)
    return {"args": args, "code": value.returncode, "stdout": value.stdout.decode("utf-8", "replace")[:65536], "stderr": value.stderr.decode("utf-8", "replace")[:8192], "elapsed_seconds": (time.monotonic_ns() - start) / 1000000000}


def inspect_owned(docker, cid, image, nonce, *, timeout=8):
    result = docker_call(docker, ["inspect", "--format", INSPECT_FORMAT, cid], timeout)
    if result["code"]:
        raise RuntimeError("专用容器身份读取失败")
    value = json.loads(result["stdout"])
    labels = value["labels"] or {}
    if value["id"] != cid or value["image"] != image or labels.get("retrolume.task") != "TASK-109" or labels.get("retrolume.permit") != PERMIT or labels.get("retrolume.nonce") != nonce:
        raise RuntimeError("专用容器归属漂移，不能停止其他对象")
    fields = ("CapAdd", "CapDrop", "NanoCpus", "Memory", "MemorySwap", "PidsLimit", "NetworkMode", "ReadonlyRootfs", "Privileged", "Binds", "PidMode", "IpcMode", "Init", "ShmSize", "Tmpfs", "RestartPolicy", "SecurityOpt", "PortBindings")
    value["host"] = {key: value["host"].get(key) for key in fields}
    options = []
    for option in value["host"]["SecurityOpt"] or []:
        if option.startswith("seccomp="):
            content = option[len("seccomp="):]
            options.append({"type": "seccomp", "value_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()})
        else:
            options.append(option)
    value["host"]["SecurityOpt"] = options
    return value


def atomic_json(path, value):
    temporary = path.with_suffix(".new.json")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
