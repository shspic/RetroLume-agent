"""Bounded owning parent starts this hidden synthetic HTTP process only."""
import asyncio,sys
import uvicorn
from app.main import create_app
from app.worker.session import SessionConfig

if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
app=create_app()
app.state.interview_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
app.state.teaching_session_config=app.state.interview_session_config

if __name__=='__main__':
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=18106,log_level='warning',access_log=False,loop='asyncio'))
    asyncio.run(server.serve())
