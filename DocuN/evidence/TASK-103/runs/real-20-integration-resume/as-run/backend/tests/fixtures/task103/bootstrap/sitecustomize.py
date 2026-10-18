"""只有本卡子进程显式许可才安装最低传输替身和观察器。"""
import os
if os.environ.get("RETROLUME_TASK103_FIXTURE"):
    try:
        if os.environ.get("RETROLUME_TASK103_FIXTURE")!="TASK-103-G9-20261006":
            raise RuntimeError("fixture permit mismatch")
        import socket
        original_connect=socket.socket.connect
        original_connect_ex=socket.socket.connect_ex
        def local(address):
            if not isinstance(address,tuple) or address[0] not in ("127.0.0.1","::1"):
                raise OSError("TASK103 external network denied")
        def connect(self,address):local(address);return original_connect(self,address)
        def connect_ex(self,address):local(address);return original_connect_ex(self,address)
        socket.socket.connect=connect
        socket.socket.connect_ex=connect_ex
        from tests.fixtures.task103.fixture_runtime import install
        install()
    except BaseException:
        import sys
        sys.stderr.write("TASK103 fixture failed closed\n")
        os._exit(86)

