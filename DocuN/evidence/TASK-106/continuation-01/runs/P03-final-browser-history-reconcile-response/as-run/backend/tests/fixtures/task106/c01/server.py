"""Actual routes. Fixture cancellation targets the real request task only."""
import asyncio,json,sys,time
import uvicorn
from app.main import create_app
from app.worker.session import SessionConfig
from .control import EVIDENCE,atomic_json,event

class CancelRoute:
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        key=dict(scope.get('headers',[])).get(b'x-c01-cancel-key',b'').decode('ascii') if scope['type']=='http' else ''
        current=asyncio.current_task();watch=None
        async def watcher():
            folder=EVIDENCE/'barriers'/key;until=time.perf_counter()+20;seen=set()
            while time.perf_counter()<until:
                for name in ('cancel.json','cancel2.json'):
                    if name not in seen and (folder/name).exists():
                        seen.add(name);event('real-http-task-cancel',dict(key=key,request_path=scope['path'],cancel=name,at_ns=time.perf_counter_ns()));current.cancel()
                await asyncio.sleep(.015)
        if key:watch=asyncio.create_task(watcher())
        async def observed(message):
            if scope['type']=='http' and dict(scope.get('headers',[])).get(b'x-c01-drop-committed')==b'yes' and message['type']=='http.response.body':
                value=json.loads(message['body']);event('committed-http-response-drop',dict(key=value['business_key'],activity=value['activity_id'],status=value['status'],effect=value['effect_applied']))
                raise RuntimeError('C01 declared actual response disconnect after committed route')
            await send(message)
        try:await self.app(scope,receive,observed)
        except asyncio.CancelledError:
            if key:atomic_json(EVIDENCE/'barriers'/key/'route-cancelled.json',dict(at_ns=time.perf_counter_ns(),actual_task_cancelled=True))
            raise
        finally:
            if watch:watch.cancel()

if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
app=create_app();app.state.interview_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2);app.state.teaching_session_config=app.state.interview_session_config
app.add_middleware(CancelRoute)
if __name__=='__main__':asyncio.run(uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=18106,log_level='warning',access_log=False,loop='asyncio')).serve())
