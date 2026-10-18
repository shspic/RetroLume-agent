"""C01自有loopback服务器，合成配置变更只由新控制文件通知。"""
import asyncio,json,os
from pathlib import Path
from app.main import create_app
from app.runtime import psycopg_compatible_loop_factory
from app.worker.session import SessionConfig
from app.service_config import load_activity_config
from .control import EVIDENCE,atomic_json
import uvicorn
def main():
 app=create_app();app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2,startup_limit_seconds=5,manager_db_timeout_seconds=5,cleanup_seconds=5,mutex_wait_seconds=3,manager_overhead_seconds=30)
 async def config_watch():
  file=EVIDENCE/'workspace/browser-config-reload.json';last=None
  while True:
   if file.exists():
    value=file.read_bytes()
    if value!=last:
     app.state.activity_config=load_activity_config(Path(os.environ['RETROLUME_ACTIVITY_CONFIG']));last=value
     atomic_json(EVIDENCE/'workspace/browser-config-reloaded.json',json.loads(value))
   await asyncio.sleep(.05)
 async def serve():
  watch=asyncio.create_task(config_watch())
  try:await uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=18103,loop='none',access_log=False,log_level='warning')).serve()
  finally:watch.cancel()
 with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as r:r.run(serve())
if __name__=='__main__':main()
