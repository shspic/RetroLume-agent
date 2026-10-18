"""107自己的最低替身入口；不导入或启用任何旧driver/control。"""
import os

if os.environ.get("RETROLUME_TASK107_FIXTURE"):
    try:
        if os.environ["RETROLUME_TASK107_FIXTURE"] != "TASK-107-G10-AUDIT-20261008":
            raise RuntimeError("107许可不匹配")
        import socket
        connect_original = socket.socket.connect
        connect_ex_original = socket.socket.connect_ex

        def local_address(address):
            if not isinstance(address, tuple) or address[0] not in ("127.0.0.1", "::1"):
                raise OSError("107明确禁止外网")

        def connect(self, address):
            local_address(address)
            return connect_original(self, address)

        def connect_ex(self, address):
            local_address(address)
            return connect_ex_original(self, address)

        socket.socket.connect = connect
        socket.socket.connect_ex = connect_ex
        from tests.fixtures.task107.runtime import install
        install()
    except BaseException:
        import sys
        sys.stderr.write("107最低夹具入口失败关闭\n")
        os._exit(86)
