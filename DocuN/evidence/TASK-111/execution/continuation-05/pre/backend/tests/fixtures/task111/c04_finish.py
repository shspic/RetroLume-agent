"""业务已停止后的真实资源核对、停止原因协议回归与原件回收。"""
import ast,ctypes,difflib,hashlib,io,json,os,struct,subprocess,threading,time
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from .control import ROOT,CONTINUE_ROOT,C03_ROOT,EVIDENCE,atomic,batch,phase,source_snapshot,read_state,locked
from .resources import DOCKER,shell_env
from app.preview.process import birth,GlobalOwner
from app.preview.production_supervisor import PreviewController
from app.preview.description import canonical

def protocol(out):
    result=[]
    for primary in ('control_lost','reaper_lost','source_invalid',None):
        c=dict(preview_id='bda36134-89df-4fe0-a732-aa645c594716',generation=1,artifact_sha256='a'*64,channel_nonce='b'*64,error_code=primary,stop=threading.Event(),pipe_eof=False)
        body=canonical(dict(state='stopping',reason_code='user')).encode();head=dict(protocol='retrolume.preview.v2',type='status',preview_id=c['preview_id'],generation=1,artifact_sha256=c['artifact_sha256'],channel_nonce=c['channel_nonce'],seq=0,body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest());raw=canonical(head).encode()
        packet=struct.pack('!I',len(raw))+raw+body;c['attach']=SimpleNamespace(stdout=io.BytesIO(packet));controller=PreviewController.__new__(PreviewController);controller._event_sink=None
        controller._read(c);assert c['error_code']==(primary or 'user') and c['pipe_eof'] and c['stop'].is_set()
        result.append(dict(initial_cause=primary,later_status='user',retained_cause=c['error_code'],packet_sha256=hashlib.sha256(packet).hexdigest(),actual_production_decoder=True,scope='内存管道协议回归；不代替真实owner失联生命周期'))
    atomic(out/'primary-cause-protocol-regression.json',dict(status='PASS_PRODUCTION_READER_PROTOCOL_ONLY',cases=result,real_postfix_owner_loss='NOT_RUN_REAL_ROOTS_EXHAUSTED'))

def cleanup(out):
    rows=[];owners=[]
    prior=json.loads((ROOT/'DocuN/evidence/TASK-111/orchestration-receipt-04/resource-recheck.json').read_text(encoding='utf-8-sig'))['objects'];targets={r['id']:r for r in prior}
    fmt='{"id":{{json .Id}},"name":{{json .Name}},"image":{{json .Image}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"restart_count":{{json .RestartCount}},"started":{{json .State.StartedAt}},"finished":{{json .State.FinishedAt}}}'
    for p in (CONTINUE_ROOT/'synthetic/control').glob('*/registry.json'):
        r=json.loads(p.read_text(encoding='utf-8'))
        if r.get('cid'):targets[r['cid']]=dict(id=r['cid'],name='/'+r['intent']['name'],image=r['intent']['image_id'])
        for role,data in (('parent',r.get('parent')),('reaper',r.get('reaper_owner')),('reaper_launcher',r.get('reaper_launcher')),('attach',dict(pid=r.get('attach_pid'),birth=r.get('attach_birth')))):
            if not data or not data.get('pid'):continue
            current=birth(data['pid']);assert current['state']=='exited' or current['state']=='running' and current['birth']!=data['birth']
            owners.append(dict(role=role,pid=data['pid'],expected_birth=data['birth'],current=current,path=p.relative_to(ROOT).as_posix()))
    for cid,expected in targets.items():
        command=subprocess.run([DOCKER,'inspect','--format',fmt,cid],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW);assert command.returncode==0
        row=json.loads(command.stdout);assert row['id']==cid and row['name']==expected['name'] and row['image']==expected['image'] and not row['running'] and row['pid']==0 and row['restart_count']==0;rows.append(row)
    # 注册API、browser Node及协调/守护进程，仅核本卡具体pid，不枚举或结束无关对象。
    for p in CONTINUE_ROOT.rglob('*.json'):
        if p.name not in ('api-owner.json','api-actual-bound.json','actual-step-owner.json','actor-owner.json','browser-host-owner.json','owner.json','guardian-ready.json','guardian-launcher.json'):continue
        r=json.loads(p.read_text(encoding='utf-8'));pid=r.get('node_pid') or r.get('pid');expected=r.get('birth')
        if not pid:continue
        if isinstance(expected,dict):expected=expected.get('birth')
        current=birth(pid);assert current['state']=='exited' or expected is not None and current['state']=='running' and current['birth']!=expected
        owners.append(dict(role=p.name,pid=pid,expected_birth=expected,current=current,path=p.relative_to(ROOT).as_posix()))
    mutex=GlobalOwner('Global\\RetroLumePreviewV2Task111')
    try:assert mutex.acquire()=='acquired';global_identity=mutex.identity()
    finally:mutex.close()
    atomic(out/'exact-resource-final.json',dict(at_utc=datetime.now(timezone.utc).isoformat(),objects=rows,owners=owners,global_exclusive=global_identity,physical_only_for_old_unknown=True,new_containers=len(targets)-len(prior),old_unknown_R_not_changed=True))

def final_sources(out):
    rows=source_snapshot(out);changes=[]
    for row in rows:
        p=ROOT/row['path'];before=CONTINUE_ROOT/'pre'/row['path']
        if before.exists() and before.read_bytes()!=p.read_bytes():
            target=out/'diffs'/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            target.with_suffix(target.suffix+'.diff').write_text(''.join(difflib.unified_diff(before.read_text(encoding='utf-8-sig').splitlines(True),p.read_text(encoding='utf-8-sig').splitlines(True),fromfile='C04-pre/'+row['path'],tofile=row['path'])),encoding='utf-8');changes.append(dict(**row,pre_sha256=hashlib.sha256(before.read_bytes()).hexdigest()))
    atomic(out/'source-differences.json',changes)
    for p in (ROOT/'backend/app/preview').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    for p in (ROOT/'backend/tests/fixtures/task111').glob('c04*.py'):ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    # 只核未授权范围与冻结runtime/renderer；无旧G3—G10重跑。
    rules=[]
    for row in json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig')):
        actual=hashlib.sha256(Path(row['absolute_path']).read_bytes()).hexdigest();assert actual==row['sha256'];rules.append(dict(path=row['absolute_path'],sha256=actual,match=True))
    unchanged=[]
    entry=json.loads((CONTINUE_ROOT/'entry-identity.json').read_text(encoding='utf-8'))
    for row in entry['sources']:
        if row['path'].startswith('deploy/') or row['path'].startswith('frontend/src/') or row['path'] in ('backend/app/activities/repository.py','backend/app/capabilities/contracts.py','backend/app/capabilities/gateway.py'):
            actual=hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest();assert actual==row['sha256'];unchanged.append(dict(path=row['path'],match=True,sha256=actual))
    bundle=json.loads((C03_ROOT/'frontend-bundle.json').read_text(encoding='utf-8'))
    for r in bundle:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
    atomic(out/'unchanged-rules-runtime-and-front-bundle.json',dict(rules=rules,unchanged=unchanged,frontend_bundle=bundle,frontend_new_source_changes=0,image_builds_added=0))

def main():
    out=CONTINUE_ROOT/'final';out.mkdir(exist_ok=True);phase('implementation_offline')
    with batch('offline','C04 final source and stop-cause regression',maximum=120):protocol(out);final_sources(out)
    phase('cleanup')
    with batch('cleanup','C04 exact registered resources',maximum=120):cleanup(out)
    phase('implementation_offline')
    budget=read_state();atomic(out/'execution-receipt.json',dict(permit='TASK-111-G11-C04-20261011',counts=budget['counts'],time_seconds=budget['time_seconds'],active_batch=budget['active_batch'],whole_task_completed=False,stop_reason='两个真实根已使用且原固定截止已过；主browser/API已达上限，未完成方法不冒通过',stopped_at_real_condition=True))

if __name__=='__main__':main()
