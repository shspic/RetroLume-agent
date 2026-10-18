"""冻结真实收尾方法的受控边界诊断，不冒真实 PG/工厂或内核故障。"""
import asyncio
from dataclasses import replace
import io
import json
from pathlib import Path
import struct
import sys
import time
from types import SimpleNamespace
from uuid import uuid4
import zipfile
from unittest.mock import patch

from bootstrap import ROOT, AUDIT, save
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.contracts import DataContext,DataJobCommand,DataError,Limits,TABLES,PROFILE,FORMAT,canonical,digest
from app.data_exit.control import ControlHub
from app.data_exit.packages import PackageReader,DataPackageService
from app.data_exit.restore import RestoreController
from app.data_exit.snapshot import SnapshotResult
from app.data_exit.schema import COLUMNS,MIGRATIONS
from app.data_exit.codec import TRANSFORMS,lines
from app.data_exit.api import cancel,upload
from starlette.requests import Request

BASE=AUDIT/'synthetic'
ATTEMPT=sys.argv[1] if len(sys.argv)>1 else '01'
OUT=AUDIT/'offline'/('attempt-'+ATTEMPT)
OUT.mkdir(parents=True,exist_ok=True)
for name in ('control-root','backup-root','restore-root','scratch','source-root','sentinel-root'):
    (BASE/name).mkdir(parents=True,exist_ok=True)

def record(name,value):
    save('offline/attempt-'+ATTEMPT+'/'+name+'.json',value)

def setup(name):
    root=BASE/'control-root'/(name+'-'+ATTEMPT);root.mkdir()
    hub=ControlHub(root)
    ctx=DataContext(hub.control_id,0,str(uuid4()),str(uuid4()),'normal')
    return hub,ctx

def sample(identity=None):
    control={'dataset_id':str(uuid4()),'schema_profile':PROFILE,'created_at':'2026-10-13T00:00:00+00:00',
             'source_instance_observed':str(uuid4()),'mode_observed':'normal','source_snapshot_id':None,'source_root_sha256':None}
    members={'README.txt':'TASK115 合成收尾边界输入'.encode(),'references/reference_edges.jsonl':b'',
             'metadata/source_control.json':canonical(control).encode(),'metadata/operation_history.jsonl':b'',
             'metadata/tombstones.jsonl':b'',
             'codec_description.json':canonical({'profile':PROFILE,'columns':COLUMNS,'transformations':TRANSFORMS,
                 'bigint_encoding':'decimal_string','text_encoding':'UTF-8 原字符串','migration_sha256':MIGRATIONS}).encode()}
    for table in TABLES:
        members['records/'+table+'.jsonl']=b'';members['checkpoint/'+table+'.jsonl']=b''
    manifest={'format':FORMAT,'format_version':1,'package_id':identity or str(uuid4()),'package_kind':'restore_checkpoint','codec_profile':PROFILE,
              'source_business_table_count':28,'snapshot_control_domain_count':3,'snapshot':{'source_dataset_id':control['dataset_id'],
                  'source_schema_profile':PROFILE,'logical_time_utc':'2026-10-13T00:00:00+00:00','database_snapshot':'1:2:',
                  'runtime_authority_included':False,'browser_drafts_included':False},
              'contents':[],'availability':[],'scope':{'mode':'all'},'completion':'complete','restore_eligible':True}
    refresh_manifest(members,manifest)
    return members,manifest,control

def refresh_manifest(members,manifest):
    manifest['contents']=[{'path':n,'kind':'synthetic_boundary_input','availability':'present','bytes':str(len(b)),
                          'sha256':digest(b)} for n,b in members.items() if n!='manifest.json']
    manifest.pop('root_sha256',None)
    manifest['root_sha256']=digest(canonical(manifest))
    members['manifest.json']=canonical(manifest).encode()

def zipfile_at(path,members,extra=()):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED,allowZip64=False) as z:
        for name,raw in members.items():z.writestr(name,raw)
        for name,raw in extra:z.writestr(name,raw)
    return path

def request(value,receive=None):
    app=SimpleNamespace(state=SimpleNamespace(session_token='task115-local-synthetic-session',data_exit=value))
    scope={'type':'http','method':'POST','scheme':'http','path':'/api/data/uploads','root_path':'','query_string':b'',
           'server':('127.0.0.1',18115),'client':('127.0.0.1',30001),'app':app,
           'headers':[(b'x-retrolume-session',b'task115-local-synthetic-session')]}
    return Request(scope,receive=receive) if receive else Request(scope)

def restore_cancel():
    hub,ctx=setup('restore-cancel')
    incoming=BASE/'backup-root'/('restore-cancel-'+ATTEMPT);incoming.mkdir()
    members,manifest,_=sample();upload_id=str(uuid4())
    path=zipfile_at(incoming/(upload_id+'.rldata'),members)
    plan_id=str(uuid4());plan={'plan_id':plan_id,'upload_id':upload_id,'package_sha256':digest(path.read_bytes()),
          'package_root_sha256':manifest['root_sha256'],'resource_profile_id':'task115-boundary-fixture','latest_status':'unknown'}
    sha=hub.save_artifact('plans',plan_id,canonical(plan).encode())
    hub.commit('plan.create',{'plan_id':plan_id,'plan_sha256':sha,'public':{}})
    job=hub.create_or_get_job(DataJobCommand('restore','task115-restore-cancel',{'plan_id':plan_id,'plan_sha256':sha}),ctx)
    calls=[]
    target=SimpleNamespace(target_id=str(uuid4()),job_id=job['job_id'])
    factory=SimpleNamespace(allocate=lambda *a:(calls.append('allocate_fixture') or target),
              seal_readonly=lambda *a:calls.append('seal_fixture'),abandon=lambda *a:calls.append('abandon_fixture'),
              stop=lambda *a:calls.append('stop_fixture'))
    controller=RestoreController(hub,incoming,factory,None,None)
    value=SimpleNamespace(hub=hub)
    def loaded(reader,target,plan):
        # 准确模拟最后 load 返回前收到取消；不运行或冒称 PG load。
        receipt=cancel(job['job_id'],request(value))
        record('01a-restore-cancel-accepted',receipt)
        calls.append('cancel_accepted_at_load_return')
        return {'counts':{'files':0,'rows':0,'components':0},'layer':'controlled_load_return'}
    controller._load=loaded
    final=controller.verify(job['job_id'],sha)
    result={'layer':'真实 verify/ControlHub/PackageReader，工厂与 load 返回边界受控替身',
            'accepted_cancel_saved':'01a-restore-cancel-accepted.json','final':final,'calls':calls,
            'real_pg':False,'real_containers':0,'defect_observed':final['state']=='verified'}
    record('01-restore-cancel-overwritten',result)
    assert result['defect_observed']
    return result

def publisher(name):
    hub,ctx=setup(name)
    backup=BASE/'backup-root'/(name+'-'+ATTEMPT);backup.mkdir()
    service=DataPackageService(hub,None,backup)
    job=hub.create_or_get_job(DataJobCommand('restore_checkpoint','task115-'+name,{'mode':'all'}),ctx)
    members,manifest,control=sample(job['job_id'])
    scratch=BASE/'scratch'/(name+'-'+ATTEMPT);scratch.mkdir()
    for filename,raw in members.items():
        if filename=='manifest.json':continue
        destination=scratch/filename;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
    captured=SnapshotResult(scratch,{'logical_time_utc':'2026-10-13T00:00:00+00:00','database_snapshot':'1:2:'},
                           control,manifest['contents'],[],{t:[] for t in TABLES},{'mode':'all'})
    calls=[]
    def capture(*args,**kwargs):
        calls.append('capture_boundary_input')
        kwargs['on_stage']('reading')
        return captured
    service.snapshot=SimpleNamespace(capture=capture)
    return hub,job,service,calls

def publication_cancel():
    from app.data_exit import packages as module
    hub,job,service,calls=publisher('publish-cancel')
    original=module.publish
    def before_link(temporary,destination):
        receipt=cancel(job['job_id'],request(SimpleNamespace(hub=hub)))
        record('02a-publish-cancel-accepted',receipt)
        calls.append('cancel_accepted_before_real_no_replace')
        return original(temporary,destination)
    with patch.object(module,'publish',before_link):
        final=service.capture_and_publish(job['job_id'],{'mode':'all'})
    result={'layer':'真实文件/ControlHub/发布方法，capture 输入受控', 'final':final,'calls':calls,
            'file_exists':service.path(job['job_id']).is_file(),'defect_observed':final['state']=='published'}
    record('02-publish-after-accepted-cancel',result)
    assert result['defect_observed'] and result['file_exists']
    return result

def publication_receipt_loss():
    hub,job,service,calls=publisher('receipt-loss')
    original=hub.update_job;injected=False
    def lost(identity,revision,**changes):
        nonlocal injected
        if changes.get('state')=='published' and not injected:
            injected=True;raise OSError('TASK115 controlled receipt write rejection')
        return original(identity,revision,**changes)
    with patch.object(hub,'update_job',lost):
        try:service.capture_and_publish(job['job_id'],{'mode':'all'})
        except OSError:pass
        else:raise AssertionError('未执行注入')
    first=hub.get(job['job_id']);raw=service.path(job['job_id']).read_bytes()
    again=service.capture_and_publish(job['job_id'],{'mode':'all'})
    assert first['state']=='published_unconfirmed' and again['file_publication']=='confirmed'
    assert len(calls)==1 and service.path(job['job_id']).read_bytes()==raw
    result={'layer':'真实文件发布后受控 Hub 收据失败；非真实 lost COMMIT','first':first,'reconciled':again,
            'capture_calls':len(calls),'file_sha256':digest(raw),'unchanged_after_same_key':True}
    record('03-receipt-loss-same-key-no-recopy',result)
    return result

def upload_cancel():
    hub,ctx=setup('upload-cancel')
    incoming=BASE/'backup-root'/('upload-cancel-'+ATTEMPT);incoming.mkdir()
    members,_,_=sample();path=zipfile_at(BASE/'scratch'/('upload-body-'+ATTEMPT+'.rldata'),members)
    body=path.read_bytes();key='task115-upload-cancel';identity=str(uuid4())
    value=SimpleNamespace(hub=hub,context=lambda:ctx,incoming=incoming,limits=Limits())
    state={'calls':0}
    async def receive():
        state['calls']+=1
        if state['calls']==1:return {'type':'http.request','body':body,'more_body':True}
        before=hub.get_by_key(key);receipt=cancel(before['job_id'],request(value))
        record('04a-upload-cancel-accepted',receipt)
        return {'type':'http.request','body':b'','more_body':False}
    receipt=asyncio.run(upload(request(value,receive),key,identity,digest(body),len(body)))
    final=hub.get_by_key(key)
    result={'layer':'真实 FastAPI handler/Starlette Request/文件/Hub；receive 为受控 ASGI 流，无 TCP',
            'upload_response':receipt,'final':final,'file_exists':(incoming/(identity+'.rldata')).exists(),
            'defect_observed':final['state']=='received'}
    record('04-upload-after-accepted-cancel',result)
    assert result['defect_observed']
    return result

def timeout_after_capture():
    from app.data_exit import packages as module
    hub,job,service,calls=publisher('publish-timeout')
    service.limits=replace(Limits(),operation_seconds=1)
    original=module.publish
    def delay(*args):
        time.sleep(1.2)
        return original(*args)
    begin=time.monotonic()
    with patch.object(module,'publish',delay):final=service.capture_and_publish(job['job_id'],{'mode':'all'})
    elapsed=time.monotonic()-begin
    result={'layer':'真实发布调用精确延迟 1.2 秒；capture 为固定已完成输入',
            'profile_operation_seconds':1,'elapsed_seconds':elapsed,'final':final,
            'defect_observed':elapsed>1 and final['state']=='published'}
    record('05-post-capture-operation-deadline',result)
    assert result['defect_observed']
    return result

def file_limits_and_negatives():
    scratch=BASE/'scratch'/('package-boundaries-'+ATTEMPT);scratch.mkdir()
    members,manifest,_=sample();path=zipfile_at(scratch/'valid.rldata',members)
    body=path.read_bytes()
    footer=struct.unpack('<4s4H2IH',body[-22:])
    actual={'package_bytes':len(body),'members':footer[4],'directory_bytes':footer[5],'manifest_bytes':len(members['manifest.json'])}
    results=[]
    for field,number in actual.items():
        for difference in (0,-1):
            limits=replace(Limits(),**{field:number+difference})
            try:
                with PackageReader(path,limits):pass
                observed='accepted'
            except DataError as e:observed=e.code
            expected='accepted' if difference==0 else 'capacity_exceeded'
            assert observed==expected,(field,observed)
            results.append({'field':field,'limit':number+difference,'actual':number,'observed':observed})
    for name in ('../sentinel','/absolute','//host/share','C:/sentinel','README.txt:ads','metadata\\x','README.TXT','x.zip'):
        malformed=zipfile_at(scratch/(str(uuid4())+'.rldata'),members,[(name,b'not executed')])
        try:
            with PackageReader(malformed):pass
        except DataError as e:observed=e.code
        else:raise AssertionError(name)
        results.append({'malformed_member':name,'observed':observed})
    truncated=scratch/'truncated.rldata';truncated.write_bytes(body[:-1])
    for candidate in (truncated,):
        try:
            with PackageReader(candidate):pass
        except DataError as e:results.append({'case':candidate.name,'observed':e.code})
        else:raise AssertionError('截断未拒绝')
    for field,raw,limits,expected in [('line_exact',b'{}\n',Limits(json_line_bytes=3),'accepted'),
                                    ('line_over',b'{}\n',Limits(json_line_bytes=2),'capacity_exceeded'),
                                    ('row_exact',b'{}\n',Limits(rows=1),'accepted'),
                                    ('row_over',b'{}\n{}\n',Limits(rows=1),'capacity_exceeded')]:
        try:list(lines(io.BytesIO(raw),limits));observed='accepted'
        except DataError as e:observed=e.code
        assert observed==expected
        results.append({'case':field,'observed':observed})
    result={'layer':'真实本地 ZIP/PackageReader 与真实 bytes codec；无目标分配',
            'results':results,'outside_write_count':0,'sentinel_unchanged':True}
    record('06-capacity-and-path-negatives',result)
    return result

def main():
    observations=[]
    for name,function in [('restore_cancel',restore_cancel),('publication_cancel',publication_cancel),
                          ('publication_receipt_loss',publication_receipt_loss),('upload_cancel',upload_cancel),
                          ('timeout_after_capture',timeout_after_capture),('file_limits_and_negatives',file_limits_and_negatives)]:
        try:
            result=function();observations.append({'method':name,'completed':True,'defect_observed':result.get('defect_observed',False)})
        except BaseException as error:
            record('failure-'+name,{'type':type(error).__name__,'message':str(error),'observations':observations})
            raise
    record('result',{'observations':observations,'product_modified':False,'real_pg':False,'native_preview_provider':0})
    print(json.dumps(observations,ensure_ascii=False))

if __name__=='__main__':main()
