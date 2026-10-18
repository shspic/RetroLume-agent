"""TASK-095 测试注入（仅由环境变量激活；产品文件零修改）。

- RETROLUME_TEST_NETWORK_GUARD=1：socket 守卫，仅允许回环连接；
- RETROLUME_TEST_WIN_CHAIN=1：应用进程内把固定 SUP 入口替换为 bootstrap95.py，
  外层 Job/CreateProcessW/句柄主体仍由真实 launcher 代码执行；
- 传输替身注入发生在 worker 进程（bootstrap95.py 内），不在此处。

异常直接抛出：注入失败应当在批次中响亮失败，而不是静默跑真实路径。
"""
from __future__ import annotations

import os


def _install_network_guard() -> None:
    if os.environ.get("RETROLUME_TEST_NETWORK_GUARD") != "1":
        return
    import errno
    import socket

    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex

    def _allowed(address):
        try:
            host = address[0]
        except Exception:
            return False
        return host in ("127.0.0.1", "::1", "localhost")

    def connect(self, address):
        if not _allowed(address):
            raise OSError("test network guard: non-loopback connect blocked")
        return original_connect(self, address)

    def connect_ex(self, address):
        if not _allowed(address):
            return errno.EHOSTUNREACH
        return original_connect_ex(self, address)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex


def _install_win_chain() -> None:
    if os.environ.get("RETROLUME_TEST_WIN_CHAIN") != "1":
        return
    evidence = os.environ["RETROLUME_TEST_WIN_EVIDENCE"]
    import ctypes
    import subprocess
    import sys

    from app.worker import launcher as launcher_module

    bootstrap = os.path.join(evidence, "win", "bootstrap95.py")

    def synthetic_create(cls, mapping_name):
        argv = [str(sys._base_executable), "-B", bootstrap, "sup", evidence, mapping_name]
        api = launcher_module._api()
        executable = str(sys._base_executable)
        command = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        environment = launcher_module._environment_block()
        startup = launcher_module._STARTUPINFOW()
        startup.cb = ctypes.sizeof(startup)
        info = launcher_module._PROCESS_INFORMATION()
        created = api.CreateProcessW(
            executable, command, None, None, False,
            launcher_module.CREATE_SUSPENDED | launcher_module.CREATE_NO_WINDOW
            | launcher_module.CREATE_UNICODE_ENVIRONMENT,
            ctypes.cast(environment, ctypes.c_void_p),
            str(launcher_module._BACKEND),
            ctypes.byref(startup), ctypes.byref(info),
        )
        if not created:
            partial = cls(api, info) if info.hProcess or info.hThread else None
            raise launcher_module.ProcessCreationError(ctypes.get_last_error(), partial)
        return cls(api, info)

    launcher_module._SuspendedSupervisor.create = classmethod(synthetic_create)


_install_network_guard()
_install_win_chain()
