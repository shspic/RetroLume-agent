"""097测试专用自举；真实launcher、SUP、Job、worker及仓储主体不替换。"""
from __future__ import annotations

import atexit
import ctypes
from dataclasses import asdict
import hashlib
import importlib.machinery
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"backend"))
OUT=Path(os.environ["RETROLUME_TASK097_OUT"])


def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")


def install_hash_loader():
    loaded={}
    original=importlib.machinery.SourceFileLoader.get_code
    def get_code(self,fullname):
        path=Path(self.path).resolve()
        if path.is_relative_to(ROOT/"backend/app") or path.is_relative_to(HERE):
            raw=self.get_data(self.path)
            loaded[fullname]={"path":path.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(raw).hexdigest()}
            save(f"imports-{os.getpid()}.json",loaded)
            return self.source_to_code(raw,self.path)
        return original(self,fullname)
    importlib.machinery.SourceFileLoader.get_code=get_code
    save(f"boot-{os.getpid()}.json",{"mode":sys.argv[1],"pid":os.getpid(),"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    atexit.register(lambda:save(f"imports-{os.getpid()}.json",loaded))
    return loaded


def install_launcher():
    from app.worker import launcher
    lock=threading.Lock()
    def create(cls,mapping_name):
        # 计数在真实CreateProcessW之前，未claim/失败也消耗一次监督会话。
        with lock:
            total=len(list((ROOT/"DocuN/evidence/TASK-097").glob("integration-*/sup-launch-*.json")))
            if total>=16:raise RuntimeError("097监督启动额度已用尽")
            event=OUT/f"sup-launch-{secrets.token_hex(8)}.json"
            facts={"attempted_at":time.time(),"caller_pid":os.getpid(),"created":False,"pid":None,"created_100ns":None}
            event.write_text(json.dumps(facts),encoding="utf-8")
        api=launcher._api();exe=str(sys._base_executable)
        argv=[exe,"-B",str(HERE/"bootstrap.py"),"sup",mapping_name]
        command=ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        environment=launcher._environment_block()
        startup=launcher._STARTUPINFOW();startup.cb=ctypes.sizeof(startup)
        info=launcher._PROCESS_INFORMATION()
        created=api.CreateProcessW(exe,command,None,None,False,
            launcher.CREATE_SUSPENDED|launcher.CREATE_NO_WINDOW|launcher.CREATE_UNICODE_ENVIRONMENT,
            ctypes.cast(environment,ctypes.c_void_p),str(launcher._BACKEND),ctypes.byref(startup),ctypes.byref(info))
        if not created:
            partial=cls(api,info) if info.hProcess or info.hThread else None
            raise launcher.ProcessCreationError(ctypes.get_last_error(),partial)
        if not info.hProcess or not info.hThread:raise launcher.ProcessCreationError(0,cls(api,info))
        instance=cls(api,info)
        facts.update(created=True,pid=instance.pid,created_100ns=instance.creation_time_100ns())
        event.write_text(json.dumps(facts),encoding="utf-8")
        return instance
    launcher._SuspendedSupervisor.create=classmethod(create)
    from app.worker import one_call
    original=one_call.run_one_call
    def observed(*args,**kwargs):
        result=original(*args,**kwargs)
        data=asdict(result)
        # 协议回执只含身份/账面/hash；绝不记录调用映射、DSN或服务秘密。
        save(f"session-{result.run_tag}.json",data)
        return result
    one_call.run_one_call=observed


def sup():
    from app.worker.windows_job import NamedJob
    original_close=NamedJob.close
    def close(self):
        count=self.active_processes() if self.handle else None
        save(f"job-close-{os.getpid()}.json",{"job_name":self.name,"active_processes_before_close":count})
        return original_close(self)
    NamedJob.close=close
    from app.worker.command import WorkerCommand
    original=WorkerCommand.argv
    def argv(self,mapping_name=None):
        validated=original(self,mapping_name)
        if self.task=="one_call":
            return [validated[0],"-B",str(HERE/"bootstrap.py"),"worker",mapping_name]
        return validated
    WorkerCommand.argv=argv
    from app.worker.supervisor_main import main
    sys.argv=["supervisor_main",sys.argv[2]]
    return main()


def worker():
    from app.worker.gate import ClosingCallGate
    original_close=ClosingCallGate.close
    async def close(self,**kwargs):
        try:return await original_close(self,**kwargs)
        finally:save(f"gate-close-{os.getpid()}.json",{"closed":self.closed,"active_calls":self.active_calls})
    ClosingCallGate.close=close
    from app.capabilities.transport import HttpxModelTransport,TransportResponse,DeliveryUnknown,RequestNotSent
    sends=0
    async def send(self,**kwargs):
        nonlocal sends
        sends+=1
        if sends!=1:raise RuntimeError("097单次传输禁止重复")
        payload=kwargs["payload"]
        user=payload["messages"][-1]["content"]
        try:data=json.loads(user)
        except (ValueError,TypeError):data={}
        text=str(data.get("question") or data.get("goal") or user)
        evidence=data.get("evidence",[])
        save(f"transport-{os.getpid()}.json",{"pid":os.getpid(),"sends":sends,"at":time.time(),
            "payload":payload,"no_dns_or_socket_performed":True})
        if "cancel" in text.casefold():
            # 阻塞worker事件循环，要求真实自有Job停止树，不弱化停止主体。
            time.sleep(120 if "hardstop" in text.casefold() else 60)
        if "unknown" in text.casefold():raise DeliveryUnknown()
        if "not_sent" in text.casefold():raise RequestNotSent()
        if evidence:
            selected=[]
            for origin,fmt in [("original","txt"),("original","md"),("original","pdf"),("user_supplement","pdf")]:
                item=next((e for e in evidence if e.get("origin_kind")==origin and
                    ((fmt=="pdf")==(e.get("physical_page") is not None))),None)
                if item and item not in selected:selected.append(item)
            if not selected:selected=evidence[:1]
            unsafe=next((e for e in evidence if "<img" in e["text"]),None)
            if unsafe and unsafe not in selected:selected.append(unsafe)
            if "conflict" in text.casefold():
                selected=[evidence[0]]
                other=next((e for e in evidence if e["source"]!=evidence[0]["source"]),None)
                if other:selected.append(other)
            value={"kind":"conflict" if "conflict" in text.casefold() else "answer",
                "message":"合成资料学习要点；引用可回查，结论仍需审阅。",
                "segments":[{"text":e["text"][:1024],"citations":[e["id"]]} for e in selected],"questions":[]}
            if "invalid" in text.casefold():value["segments"][0]["citations"]=["lc_forged"]
            if "clarification" in text.casefold():value={"kind":"clarification","message":"请确认具体学习层次","segments":[],"questions":["需要概念还是实践步骤？"]}
            if "no_evidence" in text.casefold():value={"kind":"no_evidence","message":"给定片段不足以回答该细节","segments":[],"questions":[]}
        else:
            value={"summary":"ordinary synthetic model result", "input":"显式旧普通调用"}
        raw=json.dumps({"model":payload["model"],"choices":[{"finish_reason":"stop","message":{
            "role":"assistant","content":json.dumps(value,ensure_ascii=False)}}],
            "usage":{"prompt_tokens":10,"completion_tokens":32,"total_tokens":42}},ensure_ascii=False).encode()
        save(f"response-{os.getpid()}.json",{"model_output":value,"response_sha256":hashlib.sha256(raw).hexdigest()})
        return TransportResponse(200,raw,len(raw))
    HttpxModelTransport.send=send
    from app.worker.worker_main import main
    sys.argv=["worker_main","one_call",sys.argv[2]]
    return main()


def app():
    install_launcher()
    import asyncio
    import uvicorn
    from app.main import create_app
    from app.runtime import psycopg_compatible_loop_factory
    application=create_app()
    server=uvicorn.Server(uvicorn.Config(application,host="127.0.0.1",port=18097,access_log=False,log_level="warning"))
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(server.serve())
    return 0


if __name__=="__main__":
    install_hash_loader()
    from tests.fixtures.task097.network import install
    install()
    mode=sys.argv[1]
    try:
        raise SystemExit({"app":app,"sup":sup,"worker":worker}[mode]())
    except SystemExit:raise
    except BaseException:
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
