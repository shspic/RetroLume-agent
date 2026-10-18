"""精确既有对象收尾与账修正；不启动业务、模型、API或browser。"""
import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
from .control import ROOT,CONTINUE_ROOT,EVIDENCE,registry_root,atomic,batch,phase,read_state,locked,event,source_snapshot
from .resources import DOCKER,shell_env
from app.preview.process import birth,GlobalOwner

def main():
    out=CONTINUE_ROOT/'final';out.mkdir(exist_ok=True);phase('cleanup')
    with batch('cleanup','C05 exact registered physical resource verification',maximum=120):
        prior=json.loads((ROOT/'DocuN/evidence/TASK-111/orchestration-receipt-05/resource-recheck.json').read_text(encoding='utf-8-sig'))['objects'];targets={r['id']:r for r in prior};owners=[]
        accepted=json.loads((CONTINUE_ROOT/'cleanup-only/sessions-final.json').read_text(encoding='utf-8'));ids={r['preview_id'] for r in accepted}
        for p in registry_root().glob('*/registry.json'):
            r=json.loads(p.read_text(encoding='utf-8'))
            if r['preview_id'] not in ids:continue
            if r.get('cid'):targets[r['cid']]=dict(id=r['cid'],name='/'+r['intent']['name'],image=r['intent']['image_id'])
            for role,data in (('parent',r.get('parent')),('reaper',r.get('reaper_owner')),('reaper_launcher',r.get('reaper_launcher')),('attach',dict(pid=r.get('attach_pid'),birth=r.get('attach_birth')))):
                if not data or not data.get('pid'):continue
                current=birth(data['pid']);assert current['state']=='exited' or current['state']=='running' and current['birth']!=data['birth'];owners.append(dict(role=role,instance=data,current=current))
        for p in CONTINUE_ROOT.rglob('*.json'):
            if p.name not in ('actual-step-owner.json','actor-owner.json','api-actual-bound.json','browser-host-owner.json','owner.json','guardian-ready.json'):continue
            r=json.loads(p.read_text(encoding='utf-8'));pid=r.get('node_pid') or r.get('pid');expected=r.get('birth')
            if not pid:continue
            if isinstance(expected,dict):expected=expected.get('birth')
            current=birth(pid);assert current['state']=='exited' or expected is not None and current['state']=='running' and current['birth']!=expected;owners.append(dict(path=p.relative_to(ROOT).as_posix(),pid=pid,birth=expected,current=current))
        objects=[];fmt='{"id":{{json .Id}},"name":{{json .Name}},"image":{{json .Image}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"restart_count":{{json .RestartCount}}}'
        for cid,r in targets.items():
            result=subprocess.run([DOCKER,'inspect','--format',fmt,cid],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW);assert result.returncode==0;row=json.loads(result.stdout)
            assert row['id']==cid and row['image']==r['image'] and row['name']==r['name'] and not row['running'] and row['pid']==0 and row['restart_count']==0;objects.append(row)
        owner=GlobalOwner('Global\\RetroLumePreviewV2Task111')
        try:assert owner.acquire()=='acquired';identity=owner.identity()
        finally:owner.close()
        atomic(out/'exact-resources-final.json',dict(at_utc=datetime.now(timezone.utc).isoformat(),objects=objects,owners=owners,global_exclusive=identity,old_unknown_physical_metadata_only=True,new_rows=len(accepted),new_created_containers=len(targets)-len(prior)))
    phase('implementation_offline')
    # 跨根元数据间隔与根退出后PG停机间隔亦全计real，不后移deadline。
    events=[json.loads(x) for x in (EVIDENCE/'events.jsonl').read_text(encoding='utf-8').splitlines()]
    end15=[x for x in events if x['kind']=='batch_end' and x['data'].get('kind')=='real' and x['data'].get('number')==15][-1]
    end16=[x for x in events if x['kind']=='batch_end' and x['data'].get('kind')=='real' and x['data'].get('number')==16][-1]
    start16=end16['at_ns']-int(end16['data']['elapsed']*1e9)
    stops=[x for x in events if x['kind']=='c03_exact_pg_cleanup' and x['at_ns']>end16['at_ns']]
    mainstop=stops[0];gap=max(0,(start16-end15['at_ns'])/1e9);tail=max(0,(mainstop['at_ns']-end16['at_ns'])/1e9)
    with locked():
        b=read_state();b['time_seconds']['real']+=gap+tail;assert b['time_seconds']['real']<=14400;atomic(EVIDENCE/'budget.json',b)
    event('C05_PG_interroot_and_postroot_full_time',dict(interroot_seconds=gap,postroot_seconds=tail,deadline_extended=False),cleanup=True)
    atomic(out/'execution-receipt.json',dict(permit='TASK-111-G11-C05-20261011',counts=b['counts'],time_seconds=b['time_seconds'],active_batch=b['active_batch'],whole_task_completed=False,root15_seconds=end15['data']['elapsed'],root16_seconds=end16['data']['elapsed'],PG_time_extra=dict(gap=gap,tail=tail),stop_reason='真实根/主browser/API已使用到限；内部browser时限与陈旧换根命令造成未完',old_unknown_R60_kept=True))
    unchanged=[]
    for r in json.loads((CONTINUE_ROOT/'entry-identity.json').read_text(encoding='utf-8'))['sources']:
        if r['path'].startswith(('deploy/','frontend/src/','backend/migrations/')) or r['path']=='backend/app/preview/schema-fingerprint.json':
            h=hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest();assert h==r['sha256'];unchanged.append(dict(path=r['path'],sha256=h,match=True))
    atomic(out/'accepted_unchanged_runtime_frontend_SQL.json',unchanged);source_snapshot(out)

if __name__=='__main__':main()
