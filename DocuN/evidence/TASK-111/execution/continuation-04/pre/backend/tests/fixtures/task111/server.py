"""仅本卡合成专库/进程可用的真实API夹具，无公开候选配置开关。"""
from __future__ import annotations
import asyncio
import json
import os
from pathlib import Path
import secrets
import sys,threading,time
from pydantic import SecretStr
import uvicorn
from .control import ROOT,EVIDENCE,CONTINUE_ROOT,PERMIT,reserve,event,atomic,preview_name,synthetic_root


def main():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("fixture permit")
    from app.preview.process import birth
    atomic(CONTINUE_ROOT/("api-actual-"+str(os.getpid())+".json"),{"pid":os.getpid(),"birth":birth(os.getpid())["birth"]})
    database=os.environ.get("RETROLUME_INTERACTIVE_TEST_DATABASE_URL","")
    import psycopg
    if psycopg.conninfo.conninfo_to_dict(database).get("dbname")!="retrolume_task111_main":raise RuntimeError("fixture database")
    policy_data=json.loads(os.environ["RETROLUME_TASK111_POLICY"])
    from app.main import create_app
    from app.preview.host_policy import HostPolicy
    from app.preview.production_supervisor import PreviewController
    from app.capabilities.contracts import ModelServiceConfig
    from app.service_config import ActivityConfig,LayerState
    from app.runtime import psycopg_compatible_loop_factory
    os.environ["RETROLUME_DATABASE_URL"]=database
    os.environ["RETROLUME_ACTIVITY_CONFIG"]=str(ROOT/"config/activity.example.json")
    data=synthetic_root()/"data";backup=synthetic_root()/"backup";data.mkdir(parents=True,exist_ok=True);backup.mkdir(exist_ok=True)
    os.environ["RETROLUME_DATA_DIR"]=str(data);os.environ["RETROLUME_BACKUP_DIR"]=str(backup)
    app=create_app()
    app.state.session_token=os.environ["RETROLUME_TASK111_SESSION"]
    app.state.activity_config=ActivityConfig(provider="deepseek_chat_completions",model="task111-synthetic",quota_preview=None,
      model_service=ModelServiceConfig(provider="deepseek_chat_completions",base_url="https://api.deepseek.com",model="task111-synthetic",
        api_key=SecretStr(secrets.token_urlsafe(32)),timeout_seconds=1.0,max_request_bytes=65536,max_response_bytes=65536,max_output_tokens_limit=4096),
      create_layer=LayerState(True),continue_layer=LayerState(True),teaching_layer=LayerState(True),teaching_output_tokens=2048,html_generation_layer=LayerState(True),html_output_tokens=4096)
    policy=HostPolicy(**policy_data,registry_dir=(synthetic_root()/"http-control").resolve(),authorization=PERMIT,owner_name="Global\\RetroLumePreviewV2Task111")
    def name(pid,generation):
        return preview_name(pid,generation)
    def observer(kind,data):
        if kind=="start_attempt":reserve("preview_starts",data)
        event("preview_"+kind,data)
    app.state.preview_controller=PreviewController(app.state.activities_ledger,policy,name_supplier=name,event_sink=observer)
    if (EVIDENCE/"continuation-01/timing.json").is_file():
        from .c01_fault_control import read_commands
        threading.Thread(target=read_commands,args=(app,sys.stdin),daemon=True,name="task111-fixture-control").start()
    @app.middleware("http")
    async def count(request,call_next):
        reserve("HTTP_total",{"path":request.url.path,"method":request.method})
        if request.url.path.endswith("/frames"):reserve("public_PNG_gets_subset",{})
        if request.url.path.endswith("/inputs"):reserve("public_inputs_subset",{})
        return await call_next(request)
    server=uvicorn.Server(uvicorn.Config(app,host="127.0.0.1",port=18111,log_level="warning",access_log=False,loop="none"))
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(server.serve())


if __name__=="__main__":main()
