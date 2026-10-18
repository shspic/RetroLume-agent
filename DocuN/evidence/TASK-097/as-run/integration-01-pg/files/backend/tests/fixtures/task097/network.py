"""测试进程Python网络边界守卫，只允许097明确loopback端口。"""
import errno
import json
import os
from pathlib import Path
import socket

ALLOWED={18097,15197,55441}


def install():
    original_connect=socket.socket.connect
    original_ex=socket.socket.connect_ex
    original_dns=socket.getaddrinfo
    def allowed(address):
        return isinstance(address,tuple) and len(address)>=2 and address[0]=="127.0.0.1" and address[1] in ALLOWED
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
    socket.socket.connect=connect;socket.socket.connect_ex=connect_ex;socket.getaddrinfo=dns
