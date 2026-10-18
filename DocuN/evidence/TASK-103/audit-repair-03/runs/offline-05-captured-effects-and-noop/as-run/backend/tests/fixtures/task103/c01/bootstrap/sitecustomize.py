"""本轮显式permit才加载低层合成transport，不触发旧bootstrap。"""
import os
if os.environ.get('RETROLUME_TASK103_C01_FIXTURE'):
 try:
  if os.environ['RETROLUME_TASK103_C01_FIXTURE']!='TASK-103-G9-C01-20261006':raise RuntimeError('permit mismatch')
  import socket
  connect_before=socket.socket.connect;connect_ex_before=socket.socket.connect_ex
  def check(address):
   if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):raise OSError('C01 external network denied')
  def connect(self,address):check(address);return connect_before(self,address)
  def connect_ex(self,address):check(address);return connect_ex_before(self,address)
  socket.socket.connect=connect;socket.socket.connect_ex=connect_ex
  from tests.fixtures.task103.c01.runtime import install
  install()
 except BaseException:
  import sys
  sys.stderr.write('TASK103 C01 fixture failed closed\n');os._exit(86)
