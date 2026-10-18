"""Explicit new permit only; cannot activate an ended task's bootstrap."""
import os
if os.environ.get('RETROLUME_TASK106_FIXTURE'):
    try:
        if os.environ['RETROLUME_TASK106_FIXTURE']!='TASK-106-G10-20261008':raise RuntimeError('permit mismatch')
        import socket
        original=socket.socket.connect;original_ex=socket.socket.connect_ex
        def check(address):
            if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):raise OSError('TASK106 external network denied')
        def connect(self,address):check(address);return original(self,address)
        def connect_ex(self,address):check(address);return original_ex(self,address)
        socket.socket.connect=connect;socket.socket.connect_ex=connect_ex
        from tests.fixtures.task106.runtime import install
        install()
    except BaseException:
        import sys
        sys.stderr.write('TASK106 fixture failed closed\n');os._exit(86)
