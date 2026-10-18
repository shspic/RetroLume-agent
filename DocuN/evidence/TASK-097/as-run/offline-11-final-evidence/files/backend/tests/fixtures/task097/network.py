"""测试进程Python网络边界守卫，只允许097明确loopback端口。"""
import errno
import json
import os
from pathlib import Path
import socket
import threading

ALLOWED={18097,15197,55441}


def install():
    original_connect=socket.socket.connect
    original_ex=socket.socket.connect_ex
    original_dns=socket.getaddrinfo
    original_pair=socket.socketpair
    pair_context=threading.local()
    def allowed(address):
        return isinstance(address,tuple) and len(address)>=2 and (
            (address[0]=="127.0.0.1" and address[1] in ALLOWED)
            or (getattr(pair_context,"active",False) and address[0] in {"127.0.0.1","::1"}))
    def socketpair(*args,**kwargs):
        # 标准库自管socketpair的临时端口只在本线程同步创建期间许可。
        # 普通connect/DNS仍仅097固定端口，不将任意回环端口加入白名单。
        pair_context.active=True
        try:return original_pair(*args,**kwargs)
        finally:pair_context.active=False
    def blocked(event,address):
        evidence=os.environ.get("RETROLUME_TASK097_OUT")
        if evidence:
            with (Path(evidence)/f"network-blocked-{os.getpid()}.jsonl").open("a",encoding="utf-8") as file:
                file.write(json.dumps({"event":event,"host":str(address[0])[:128],"port":str(address[1])})+"\n")
    def connect(self,address):
        if not allowed(address):
            blocked("connect",address);raise OSError("097 network guard blocked address")
        return original_connect(self,address)
    def connect_ex(self,address):
        if not allowed(address):blocked("connect_ex",address);return errno.EHOSTUNREACH
        return original_ex(self,address)
    def dns(host,port,*args,**kwargs):
        if host!="127.0.0.1" or (port not in ALLOWED and str(port) not in {str(x) for x in ALLOWED}):
            blocked("dns",(host,port));raise OSError("097 DNS guard blocked address")
        return original_dns(host,port,*args,**kwargs)
    socket.socket.connect=connect;socket.socket.connect_ex=connect_ex;socket.getaddrinfo=dns;socket.socketpair=socketpair
