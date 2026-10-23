"""One normal application, loopback HTTP, real Windows SUP, owned root only."""
from contextlib import contextmanager
import asyncio
import threading
import time
import httpx
import uvicorn
from . import resources as r,setup
from .transport import install
from app.runtime import psycopg_compatible_loop_factory


def run(coro):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(coro)


class Client:
    def __init__(self,app):
        self.app=app;self.base='http://127.0.0.1:'+str(r.state()['ports']['api'])
        self.client=httpx.Client(base_url=self.base,timeout=25,trust_env=False)
        self.headers={'x-retrolume-session':app.state.session_token,'Origin':self.base,
            'x-retrolume-data-context':__import__('app.capabilities.q_protocol',fromlist=['canonical']).canonical(app.state.data_exit.context().public())}
        self.timeline=[]

    def request(self,method,path,body=None,*,expect=(200,202)):
        start=time.monotonic_ns()
        result=self.client.request(method,path,json=body,headers=self.headers)
        try:response=result.json()
        except ValueError:response={}
        self.timeline.append({'at_ns':start,'method':method,'path':path,'status':result.status_code,
            'receipt':{key:response.get(key) for key in ('status','error_code','operation_id','retry_policy','model_called')},
            'body_sha256':__import__('app.capabilities.q_protocol',fromlist=['digest']).digest(body) if body is not None else None})
        if result.status_code not in expect:
            try:value=result.json();detail=value.get('detail',value);code=detail.get('code') if isinstance(detail,dict) else 'http_rejected'
            except ValueError:code='non_json'
            raise RuntimeError('task120_http_'+str(result.status_code)+'_'+str(code))
        return result.json()

    def approve(self,aid,key):
        from app.data_exit.q_store import authority_for
        from app.operator.q_request import inspect_request,approve_request
        authority=authority_for(self.app.state.activities_ledger)
        rows=[row for row in authority.hub.state()['q']['requests'].values() if row['prepared']['activity_id']==aid and row['prepared']['business_key']==key]
        if not rows:raise RuntimeError('task120_missing_prepared')
        for row in rows:
            inspection=run(inspect_request(self.app.state.activities_ledger,row['prepared_id']))
            if not inspection['request_available']:raise RuntimeError('task120_inspection_not_current')
            decision=run(approve_request(self.app.state.activities_ledger,row['prepared_id'],inspection['prepared_sha256']))
            r.event('explicit_testonly_operator_approval',prepared_id=row['prepared_id'],approval_id=decision['approval_id'],request_available=True)
        return rows


@contextmanager
def application(slot):
    setup.environment(slot,include_admin=False);install()
    if slot=='flow':setup.host_environment(slot)
    from app.main import create_app
    app=create_app()
    if app.state.data_exit_error or not app.state.q_readiness['available']:raise RuntimeError('normal_assembly_not_ready_'+str(app.state.q_readiness.get('reason')))
    class Diagnostic:
        def __init__(self,application):self.application=application
        async def __call__(self,scope,receive,send):
            if scope['type']=='http':r.count('http')
            try:await self.application(scope,receive,send)
            except BaseException as exc:
                import traceback
                r.event('actual_api_exception',error_type=type(exc).__name__,code=getattr(exc,'code',str(exc) if isinstance(exc,__import__('app.capabilities.contracts',fromlist=['AdmissionDenied']).AdmissionDenied) else None),
                    q_path=getattr(exc,'q_path',None),q_value_sha256=getattr(exc,'q_value_sha256',None),
                    frames=[{'file':str(item.filename).replace(str(r.ROOT),'PROJECT'),'line':item.lineno,'function':item.name} for item in traceback.extract_tb(exc.__traceback__)])
                raise
    r.memory_gate('api');r.count('api_starts')
    server=uvicorn.Server(uvicorn.Config(Diagnostic(app),host='127.0.0.1',port=r.state()['ports']['api'],access_log=False,log_level='critical',lifespan='on'))
    errors=[]
    def serve():
        try:run(server.serve())
        except BaseException as exc:errors.append(type(exc).__name__)
    thread=threading.Thread(target=serve,daemon=True,name='TASK120-loopback-api');thread.start()
    until=time.monotonic()+12
    while not server.started:
        if not thread.is_alive() or time.monotonic()>=until:raise RuntimeError('task120_api_start_failed')
        time.sleep(.02)
    client=Client(app)
    try:yield client
    finally:
        client.client.close();server.should_exit=True;thread.join(4)
        import os
        suffix=('-batch-'+os.environ['RETROLUME_TASK120_BATCH'].zfill(2)) if os.environ.get('RETROLUME_TASK120_BATCH') else ''
        r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}{suffix}-http-timeline.json",client.timeline)
        if thread.is_alive() or errors:raise RuntimeError('task120_api_stop_unconfirmed')


def financials(slot):
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(setup.dsn(slot),row_factory=dict_row) as connection:
        rows=connection.execute('SELECT id::text,requests_reserved,cost_reserved_microunits,running_reserved_seconds,running_settled_seconds FROM activities ORDER BY id').fetchall()
        ops=connection.execute('SELECT activity_id::text,operation_id,admission_id::text,state FROM activity_operations ORDER BY activity_id,operation_id').fetchall()
    return {'activities':rows,'operations':ops,'requests':sum(row['requests_reserved'] for row in rows),'cost':sum(row['cost_reserved_microunits'] for row in rows)}
