"""本卡显式白名单才激活；失败即退出本卡进程，防真实外发。"""
import os
if os.environ.get('RETROLUME_TASK100_FIXTURE'):
    try:
        if (os.environ.get('RETROLUME_TASK100_FIXTURE')!='TASK-100-audit-repair-03-20261005'
                or os.environ.get('RETROLUME_TASK100_PERMIT')!='TASK-100-audit-repair-03-20261005'):
            raise RuntimeError('current fixture permit required; old permit ended')
        import socket
        _connect=socket.socket.connect
        _connect_ex=socket.socket.connect_ex
        def _local(address):
            if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):
                raise OSError('TASK-100 fixture rejects external network')
        def connect(self,address): _local(address); return _connect(self,address)
        def connect_ex(self,address): _local(address); return _connect_ex(self,address)
        socket.socket.connect=connect
        socket.socket.connect_ex=connect_ex
        from tests.fixtures.task100.fixture_runtime import install
        install()
    except BaseException:
        import sys
        sys.stderr.write('TASK-100 fixture initialization failed closed\n')
        os._exit(86)
