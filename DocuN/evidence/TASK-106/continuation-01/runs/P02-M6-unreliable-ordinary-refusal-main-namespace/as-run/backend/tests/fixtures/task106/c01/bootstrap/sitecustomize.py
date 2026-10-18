"""C01 only. Never import initial106 bootstrap/control; fail closed."""
import os
if os.environ.get('RETROLUME_TASK106_C01_FIXTURE'):
    try:
        if os.environ['RETROLUME_TASK106_C01_FIXTURE']!='TASK-106-G10-C01-20261008' or os.environ.get('RETROLUME_TASK106_FIXTURE'):raise RuntimeError('C01 permit mismatch')
        import socket
        original=socket.socket.connect;original_ex=socket.socket.connect_ex
        def check(address):
            if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):raise OSError('C01 external network denied')
        def connect(self,address):check(address);return original(self,address)
        def connect_ex(self,address):check(address);return original_ex(self,address)
        socket.socket.connect=connect;socket.socket.connect_ex=connect_ex
        from tests.fixtures.task106.c01.runtime import install
        install()
    except BaseException:
        import sys
        sys.stderr.write('C01 bootstrap failed closed\n');os._exit(86)
