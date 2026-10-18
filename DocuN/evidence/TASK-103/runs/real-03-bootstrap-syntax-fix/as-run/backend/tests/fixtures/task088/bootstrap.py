"""TASK-088 仅测试自举：替换固定SUP启动模块与worker argv；产品无选择器。

来源：复制自 fixtures/task085/bootstrap.py（TASK-085 既有受控调用模式）。
差异：label 集合缩减为本卡两例（json/text）；正文模式经 task088 合成
label 读取；本文件永不进入产品导入链。
"""
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
    raise SystemExit(main())
