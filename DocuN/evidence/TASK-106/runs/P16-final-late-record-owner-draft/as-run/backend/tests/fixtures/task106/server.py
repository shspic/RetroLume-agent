"""Bounded owning parent starts this hidden synthetic HTTP process only."""
import asyncio,sys
import uvicorn
from app.main import create_app
from app.worker.session import SessionConfig
from .control import event

class CommitCut:
    """Fixture-only real socket response failure, after original route COMMIT."""
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        cut=scope['type']=='http' and (b'x-task106-cut-after-commit',b'yes') in scope.get('headers',[]) and scope.get('method')=='POST' and scope.get('path','').endswith('/interview/commands')
        async def observed(message):
            if cut and message['type']=='http.response.body':
                import json
                receipt=json.loads(message['body'])
                event('http-commit-cut',dict(activity_id=receipt['activity_id'],business_key=receipt['business_key'],status=receipt['status'],effect_applied=receipt['effect_applied']))
                raise RuntimeError('TASK106 declared response disconnect after original committed route')
            await send(message)
        await self.app(scope,receive,observed if cut else send)

if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
app=create_app()
app.state.interview_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
app.state.teaching_session_config=app.state.interview_session_config
app.add_middleware(CommitCut)

if __name__=='__main__':
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=18106,log_level='warning',access_log=False,loop='asyncio'))
    asyncio.run(server.serve())
