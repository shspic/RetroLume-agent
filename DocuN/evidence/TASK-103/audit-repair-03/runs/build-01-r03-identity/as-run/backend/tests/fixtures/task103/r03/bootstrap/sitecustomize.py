"""R03显式许可，仅loopback及SUP禁止观察，不替换产品transport。"""
import os
if os.environ.get('RETROLUME_TASK103_R03_FIXTURE'):
 try:
  if os.environ['RETROLUME_TASK103_R03_FIXTURE']!='TASK-103-G9-R03-20261007':raise RuntimeError('permit mismatch')
  import socket
  old_connect=socket.socket.connect;old_connect_ex=socket.socket.connect_ex
  def check(address):
   if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1'):raise OSError('R03 external network denied')
  def connect(self,address):check(address);return old_connect(self,address)
  def connect_ex(self,address):check(address);return old_connect_ex(self,address)
  socket.socket.connect=connect;socket.socket.connect_ex=connect_ex
  from tests.fixtures.task103.r03.runtime import install
  install()
 except BaseException:
  import sys
  sys.stderr.write('TASK103 R03 fixture failed closed\n');os._exit(86)
