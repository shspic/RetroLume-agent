"""本卡唯一真实loopback应用服务器，配置和凭据由owned root环境提供。"""
import asyncio
from app.main import create_app
from app.runtime import psycopg_compatible_loop_factory
from app.worker.session import SessionConfig
import uvicorn

def main():
 app=create_app()
 app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
 cfg=uvicorn.Config(app,host="127.0.0.1",port=18103,loop="none",access_log=False,log_level="warning")
 with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(uvicorn.Server(cfg).serve())

if __name__=="__main__":main()

