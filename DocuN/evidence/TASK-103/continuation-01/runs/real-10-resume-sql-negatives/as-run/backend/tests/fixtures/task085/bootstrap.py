"""仅测试自举：替换固定SUP启动模块与worker argv；产品无选择器。"""
from pathlib import Path
import sys
BACKEND=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(BACKEND))

if __name__=="__main__":
    mode=sys.argv.pop(1)
    if mode=="sup":
        from app.worker.command import WorkerCommand, _INTERPRETER
        original=WorkerCommand.argv
        def test_argv(self,mapping_name=None):
            if self.task=="one_call":
                return [str(_INTERPRETER),"-B",str(Path(__file__).resolve()),"worker","one_call",mapping_name]
            return original(self,mapping_name)
        WorkerCommand.argv=test_argv
        from app.worker.supervisor_main import main
    elif mode=="worker":
        import asyncio
        import json
        import time
        from app.capabilities.transport import HttpxModelTransport, TransportResponse, DeliveryUnknown
        async def send(self,**kwargs):
            # 模式只从测试合成正文读取；本文件永不进入产品导入链。
            label=kwargs["payload"]["messages"][0]["content"]
            if label=="hard":
                time.sleep(30)
            if label=="unknown":
                raise DeliveryUnknown("synthetic")
            content='{"synthetic":true}' if label=="json" else "synthetic response"
            message={"role":"assistant","content":content}
            finish="stop"
            if label=="tool":
                finish="tool_calls"
                message["tool_calls"]=[{"id":"calc","type":"function","function":{
                    "name":"finite_calculate","arguments":'{"operation":"add","left":1,"right":2}'}}]
            raw=json.dumps({"model":"synthetic-model","choices":[{"message":message,"finish_reason":finish}],
                            "usage":{"prompt_tokens":2,"completion_tokens":1,"total_tokens":3}}).encode()
            return TransportResponse(200,raw,len(raw))
        HttpxModelTransport.send=send
        from app.capabilities.tools import ToolRegistry
        def forbidden(*args,**kwargs): raise RuntimeError("tool execution forbidden in one_call")
        ToolRegistry.execute=forbidden
        from app.worker.worker_main import main
    else:
        raise SystemExit(2)
    raise SystemExit(main())
