"""098独立记录器、有限网络和精确身份收尾，不读取097许可。"""
from ctypes import wintypes
import ctypes
import errno
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUN = HERE / "runtime/run-01"
CID = "e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4"
DB = "retrolume_task097_g7"
ROLE = "retrolume_task097_synth"
ADMIN = "retrolume_task088_synth"


def publish(name, value, root=RUN):
    root = Path(root)
    target = root / name
    temp = root / (name + "." + secrets.token_hex(8) + ".tmp")
    with temp.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    # Windows rename失败时保留暂存原件，绝不覆盖旧记录。
    os.rename(temp, target)
    return target


def event(prefix, value):
    return publish(prefix + "-" + secrets.token_hex(10) + ".json", value)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def kernel():
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    api.OpenProcess.restype = wintypes.HANDLE
    api.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4)]
    api.GetProcessTimes.restype = wintypes.BOOL
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    return api


def handle_identity(api, handle, pid):
    values = [wintypes.FILETIME() for _ in range(4)]
    if not api.GetProcessTimes(handle, *[ctypes.byref(v) for v in values]):
        raise OSError("process_identity_unavailable")
    state = api.WaitForSingleObject(handle, 0)
    if state not in (0, 0x102):
        raise OSError("process_exit_unknown")
    return {"pid": pid, "created_100ns": (values[0].dwHighDateTime << 32) | values[0].dwLowDateTime,
            "alive": state == 0x102}


def identity(pid):
    api = kernel()
    handle = api.OpenProcess(0x00100000 | 0x1000, False, pid)
    if not handle:
        if ctypes.get_last_error() == 87:
            return None
        raise OSError("process_open_unknown")
    try:
        return handle_identity(api, handle, pid)
    finally:
        api.CloseHandle(handle)


def stop_exact(expected, max_seconds=25):
    deadline = time.monotonic() + max_seconds
    api = kernel()
    handle = api.OpenProcess(0x00100000 | 0x1000, False, expected["pid"])
    if not handle:
        if ctypes.get_last_error() == 87:
            return {**expected, "action": "already_exited", "zero": True}
        raise OSError("process_cleanup_identity_unknown")
    try:
        current = handle_identity(api, handle, expected["pid"])
        if current["created_100ns"] != expected["created_100ns"]:
            return {**expected, "action": "different_process_untouched", "zero": True}
        action = "already_exited"
        if current["alive"]:
            # 核身份并持有句柄直到结束，避免PID复用；只处理本卡记录的树。
            result = subprocess.run(["taskkill", "/PID", str(expected["pid"]), "/T", "/F"],
                                    capture_output=True, timeout=min(15, max_seconds * 0.6), creationflags=subprocess.CREATE_NO_WINDOW)
            action = "own_tree_terminated" if result.returncode == 0 else "termination_failed"
            api.WaitForSingleObject(handle, max(0, int(min(10, deadline - time.monotonic()) * 1000)))
        after = handle_identity(api, handle, expected["pid"])
        return {**expected, "action": action, "zero": not after["alive"]}
    finally:
        api.CloseHandle(handle)


def install_network():
    allowed_ports = {18098, 55441}
    original_connect, original_ex = socket.socket.connect, socket.socket.connect_ex
    original_dns, original_pair = socket.getaddrinfo, socket.socketpair
    local = threading.local()

    def allowed(address):
        return isinstance(address, tuple) and len(address) >= 2 and (
            address[0] == "127.0.0.1" and address[1] in allowed_ports or
            getattr(local, "pair_active", False) and address[0] in {"127.0.0.1", "::1"})

    def denied(kind):
        event("network-denied", {"kind": kind, "pid": os.getpid(), "at": time.time()})

    def connect(self, address):
        if not allowed(address):
            denied("connect")
            raise OSError("098_network_blocked")
        return original_connect(self, address)

    def connect_ex(self, address):
        if not allowed(address):
            denied("connect_ex")
            return errno.EHOSTUNREACH
        return original_ex(self, address)

    def dns(host, port, *args, **kwargs):
        if not (host == "127.0.0.1" and str(port) in {"18098", "55441"} or
                getattr(local, "pair_active", False) and host in {"127.0.0.1", "::1"}):
            denied("dns")
            raise OSError("098_dns_blocked")
        return original_dns(host, port, *args, **kwargs)

    def pair(*args, **kwargs):
        local.pair_active = True
        try:
            return original_pair(*args, **kwargs)
        finally:
            local.pair_active = False

    socket.socket.connect, socket.socket.connect_ex = connect, connect_ex
    socket.getaddrinfo, socket.socketpair = dns, pair


def free(port):
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        probe.bind(("127.0.0.1", port))


def docker(*args, input=None, timeout=20):
    return subprocess.run(["docker", *args], input=input, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout,
                          creationflags=subprocess.CREATE_NO_WINDOW)


def inspect_guard(timeout=20):
    result = docker("inspect", CID, timeout=timeout)
    if result.returncode:
        raise ValueError("container_inspect_failed")
    data = json.loads(result.stdout)[0]
    host = data["HostConfig"]
    ports = host["PortBindings"]
    mounts = data["Mounts"]
    assert data["Id"] == CID and data["Name"] == "/retrolume-task-088-g3-w1"
    assert data["Image"] == "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
    assert host["NanoCpus"] == 1000000000 and host["Memory"] == 536870912 and host["PidsLimit"] == 128
    assert host["NetworkMode"] == "bridge" and not host["Privileged"] and host["RestartPolicy"]["Name"] == "no"
    assert ports == {"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": "55441"}]}
    assert len(mounts) == 1 and mounts[0]["Type"] == "volume" and mounts[0]["Name"] == "retrolume-task-088-g3-w1-data"
    assert mounts[0]["Destination"] == "/var/lib/postgresql/data" and mounts[0]["RW"] is True
    assert all(x.split(":")[0] == "retrolume-task-088-g3-w1-data" for x in host.get("Binds") or [])
    return {"id": data["Id"], "name": data["Name"], "image": data["Image"], "ports": ports,
            "mounts": [{k: m[k] for k in ("Type", "Name", "Destination", "RW")} for m in mounts],
            "cpu": host["NanoCpus"], "memory": host["Memory"], "pids": host["PidsLimit"],
            "running": data["State"]["Running"], "pid": data["State"]["Pid"],
            "env_logged": False}
