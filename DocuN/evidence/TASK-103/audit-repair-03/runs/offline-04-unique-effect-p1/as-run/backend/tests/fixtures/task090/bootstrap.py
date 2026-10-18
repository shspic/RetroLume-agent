"""TASK-090 仅测试自举：复制task088，新增单次发送防护/加载hash；产品无选择器。

来源：复制自 fixtures/task085/bootstrap.py（TASK-085 既有受控调用模式）。
差异：label 集合缩减为本卡两例（json/text）；正文模式经 task088 合成
label 读取；本文件永不进入产品导入链。
"""
from pathlib import Path
import hashlib
import json
import os
import sys
BACKEND=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(BACKEND))

if __name__=="__main__":
    mode=sys.argv.pop(1)
    evidence=Path(sys.argv.pop(1)).resolve()
    assert evidence.is_relative_to(BACKEND.parent / "Ndocu/evidence/task-090")
    import importlib.machinery
    loaded_bytes={}
    original_get_code=importlib.machinery.SourceFileLoader.get_code
    def capture_code(self, fullname):
        if fullname == "app" or fullname.startswith("app."):
            path=Path(self.get_filename(fullname)).resolve()
            raw=self.get_data(str(path))
            loaded_bytes[path.relative_to(BACKEND.parent).as_posix()]=hashlib.sha256(raw).hexdigest()
            return self.source_to_code(raw,str(path))
        return original_get_code(self,fullname)
    importlib.machinery.SourceFileLoader.get_code=capture_code
    root = BACKEND.parent
    files = sorted((BACKEND / "app").rglob("*.py"))
    before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    if mode=="sup":
        from app.worker.command import WorkerCommand, _INTERPRETER
        original=WorkerCommand.argv
        def test_argv(self,mapping_name=None):
            if self.task=="one_call":
                return [str(_INTERPRETER),"-B",str(Path(__file__).resolve()),"worker",str(evidence),"one_call",mapping_name]
            return original(self,mapping_name)
        WorkerCommand.argv=test_argv
        from app.worker.supervisor_main import main
    elif mode=="worker":
        import asyncio
        import json
        import time
        from app.capabilities.transport import HttpxModelTransport, TransportResponse, DeliveryUnknown
        sends = 0
        async def send(self,**kwargs):
            global sends
            sends += 1
            if sends != 1:
                raise RuntimeError("test transport forbids resending")
            # 模式只从测试合成正文读取；本文件永不进入产品导入链。
            payload=kwargs["payload"]
            assert "input_result" not in payload
            messages=payload["messages"]
            assert [x["role"] for x in messages]==["assistant","user"]
            assert messages[0]["content"]=='{"parent":"低信任历史"}'
            assert messages[1]["content"]=="explicit-followup-090"
            globals()["parent_low_trust_verified"]=True
            globals()["reference_excluded_verified"]=True
            label="json"
            content='{"synthetic":true}' if label=="json" else "synthetic-response-088"
            message={"role":"assistant","content":content}
            raw=json.dumps({"model":"synthetic-model","choices":[{"message":message,"finish_reason":"stop"}],
                            "usage":{"prompt_tokens":2,"completion_tokens":1,"total_tokens":3}}).encode()
            return TransportResponse(200,raw,len(raw))
        HttpxModelTransport.send=send
        from app.capabilities.tools import ToolRegistry
        def forbidden(*args,**kwargs): raise RuntimeError("tool execution forbidden in one_call")
        ToolRegistry.execute=forbidden
        from app.worker.worker_main import main
    else:
        raise SystemExit(2)
    import time
    trace=[]
    def observe(frame,event,arg):
        if event == "line" and frame.f_code.co_filename.endswith("session.py"):
            trace.append({"line":frame.f_lineno,"time_ns":time.monotonic_ns()})
        return observe
    if mode == "sup": sys.settrace(observe)
    try:
        code = main()
    finally:
        sys.settrace(None)
        loaded = {}
        for name, module in tuple(sys.modules.items()):
            filename = getattr(module, "__file__", None)
            if filename and name.startswith("app."):
                path = Path(filename).resolve()
                if path.is_relative_to(root) and path.suffix == ".py":
                    loaded[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        target = evidence / f"bootstrap-{mode}-{os.getpid()}.json"
        target.write_text(json.dumps({"mode": mode, "pid": os.getpid(), "session_line_trace": trace, "before": before,
                          "loaded_modules": loaded, "loaded_source_bytes": loaded_bytes, "source_unchanged": before == after,
                          "transport_sends": globals().get("sends"), "parent_low_trust_verified": globals().get("parent_low_trust_verified"), "reference_excluded_verified": globals().get("reference_excluded_verified")}, indent=2), encoding="utf-8")
    raise SystemExit(code)
