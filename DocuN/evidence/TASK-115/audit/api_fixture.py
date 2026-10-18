"""本卡 HTTP 输入夹具，实际路由/Hub/文件，业务 DB 和 selector 均不冒真实。"""
import os
from pathlib import Path
import secrets
import sys
from types import SimpleNamespace
from uuid import uuid4
from bootstrap import ROOT,AUDIT
sys.path.insert(0,str(ROOT/'backend'))
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.data_exit.api import router
from app.data_exit.contracts import DataContext,DataJobCommand,DataError,Limits,TABLES
from app.data_exit.control import ControlHub
from app.data_exit.packages import DataPackageService
from app.data_exit.snapshot import SnapshotResult
from offline_cases import sample

def app():
    base=AUDIT/'synthetic'
    suffix=os.environ.get('TASK115_HTTP_ATTEMPT','01')
    control=base/'control-root'/('http-'+suffix);control.mkdir()
    backup=base/'backup-root'/('http-'+suffix);backup.mkdir()
    scratch=base/'scratch'/('http-'+suffix);scratch.mkdir()
    incoming=backup/'incoming';incoming.mkdir()
    hub=ControlHub(control)
    context=DataContext(hub.control_id,0,str(uuid4()),str(uuid4()),'normal')
    service=DataPackageService(hub,None,backup)
    def capture(identity,kind,scope,**kwargs):
        members,manifest,source=sample(identity)
        root=scratch/identity;root.mkdir()
        for name,raw in members.items():
            if name=='manifest.json':continue
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        kwargs['on_stage']('reading')
        return SnapshotResult(root,{'logical_time_utc':'2026-10-13T00:00:00+00:00','database_snapshot':'1:2:'},
                     source,manifest['contents'],[],{t:[] for t in TABLES},{'mode':'all'})
    service.snapshot=SimpleNamespace(capture=capture)
    value=SimpleNamespace(hub=hub,context=lambda:context,packages=service,factory=None,deletions=None,
         incoming=incoming,limits=Limits(),tasks={})
    value.caps=lambda:{**context.public(),'format':'data_exit.v1.r01','backup_available':True,
         'restore_executor_configured':False,'source_delete_available':False,'permanent_readonly_restore':True,
         'browser_drafts_included':False,'limits':value.limits.__dict__}
    application=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
    application.state.session_token=secrets.token_urlsafe(32)
    application.state.data_exit=value
    application.state.activities_ledger=None
    async def data_error(request,error):
        return JSONResponse({'detail':'本卡测试动作未完成','code':error.code},status_code=error.status)
    application.add_exception_handler(DataError,data_error)
    @application.get('/health')
    def health():return {'status':'ok','layer':'task115_fixture'}
    @application.get('/api/session')
    def session():return {'token':application.state.session_token,'storage_configured':True,'max_bytes':5242880,'data_context':context.public()}
    @application.get('/api/materials')
    def materials():return {'items':[],'next_offset':None}
    @application.get('/api/activities')
    def activities():return {'items':[]}
    application.include_router(router)
    application.mount('/',StaticFiles(directory=ROOT/'frontend/dist',html=True),name='frozen_final_bundle')
    return application

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app(),host='127.0.0.1',port=18115,log_level='warning',access_log=False)
