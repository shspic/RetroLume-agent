"""C02真实loopback API及已构建dist；没有控制HTTP或资格替身。"""
import asyncio
from app.main import create_app
from app.runtime import psycopg_compatible_loop_factory
from app.worker.session import SessionConfig
import uvicorn
def main():
 app=create_app();app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2,startup_limit_seconds=5,
  manager_db_timeout_seconds=5,cleanup_seconds=5,mutex_wait_seconds=3,manager_overhead_seconds=30,single_host_single_session_recovery=False)
 with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
  runner.run(uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=18103,loop='none',access_log=False,log_level='warning')).serve())
if __name__=='__main__':main()
