"""S07接收登记。只核新卡冻结输入并追加唯一工程账，不接触原业务资源。"""
from pathlib import Path
from datetime import datetime,timedelta,timezone
import json,time,hashlib,shutil
N=Path(__file__).resolve().parent;E=N.parent;ROOT=E.parents[3]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    assert not (N/'receipt.json').exists(),'已接收，禁止重置'
    manifest=json.loads((ROOT/'DocuN/evidence/TASK-117/orchestration-s07-20261017/input-manifest.json').read_text())
    permit=json.loads((ROOT/'DocuN/evidence/TASK-117/orchestration-s07-20261017/continuation-permit.json').read_text())
    records=[*manifest['rules'],*manifest['reports'],*manifest['sources'],manifest['audit_frozen_input'],manifest['contract']];verified=[]
    for row in records:
        p=Path(row.get('path',row.get('absolute_path')));exists=p.exists();actual=sha(p.read_bytes()) if exists else None
        assert exists==row.get('exists',True) and actual==row['sha256'],str(p)
        verified.append({'path':str(p),'exists':exists,'bytes':p.stat().st_size if exists else 0,'sha256':actual})
    before=(E/'budget.json').read_bytes();b=json.loads(before)
    assert b['phase']=='S06_returned_engineering_candidate' and b['active_root'] is None and b['counts']==permit['baseline_counts']
    for name in ('budget.json','events.jsonl','case-index.json'):
        raw=(E/name).read_bytes();(N/('before-'+name)).write_bytes(raw);write(N/('before-'+name+'-identity.json'),{'bytes':len(raw),'sha256':sha(raw)})
    old=(ROOT/'DocuN/results/TASK-117-result.md').read_bytes();assert len(old)==79709 and sha(old)=='b596ab87ae3facc605dab65acbf9c708c784c11b1f8581b75ddc6611ad802ac9'
    (N/'before-result.md').write_bytes(old)
    first={'utc':'2026-10-17T01:14:01.3954920Z','qpc':1325394486213,'frequency':10000000}
    now=datetime.now(timezone.utc);mono=time.monotonic_ns();utc=datetime.fromisoformat(first['utc']);qpc_ns=first['qpc']*100
    bridge=mono-int((now-utc).total_seconds()*1e9);anchor=min(qpc_ns,bridge)-20_000_000
    baseline={**b['counts'],'fixture_server_starts':0};caps={**permit['cumulative_caps'],'fixture_server_starts':3}
    segment={'permit':permit['id'],'stage':'S07','status':'active','start_utc':utc.isoformat(),'start_mono_ns':anchor,'calendar_deadline_utc':(utc+timedelta(hours=48)).isoformat(),'activity_cap_seconds':21600,'save_only_after_seconds':20400,'save_reserve_seconds':1200,'runtime_holding_cap_seconds':3600,'offline_process_run_cap_seconds':3600,'offline_process_run_seconds':0,'offline_process_run_active':None,'offline_cap_seconds':None,'cumulative_offline_cap_seconds':None,'offline_cursor_mono_ns':anchor,'paused_seconds':0,'suspensions':[],'root_business_seconds':1500,'root_cleanup_seconds':300,'baseline_counts':baseline,'segment_caps':{**permit['new_counts'],'roots':3},'cumulative_caps':caps,'evidence_directory':str(N),'runtime_kind':'loopback fixture/browser union only; no original PG/API/Native permission','fixture_binding':'127.0.0.1:18119'}
    b['segments'].append(segment);b['active_segment']=permit['id'];b['counts']['fixture_server_starts']=0;b['phase']='S07_offline_implementation';write(E/'budget.json',b)
    receipt={'TASK':'TASK-117','R':'R-111','permit':permit['id'],'first_tool':first,'controller_anchor_mono_ns':anchor,'qpc_utc_bridge_difference_seconds':(qpc_ns-bridge)/1e9,'sample':{'utc':now.isoformat(),'mono_ns':mono},'actual_model':'Codex desktop / GPT-6，A+为资源标签，具体服务端变体未披露','verified_inputs':verified,'baseline_counts':baseline,'old_report_sha256':sha(old),'Q':'FROZEN','runtime_started':False,'old_PG_stop_reference_only':'continuation-05 final stop at2026-10-16T15:45:05Z; not resampled','old_accounting_unchanged':True}
    write(N/'receipt.json',receipt)
    with (E/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'kind':'S07_received','utc':now.isoformat(),'mono_ns':mono,'permit':permit['id'],'verified':len(verified),'Q':'FROZEN'},ensure_ascii=False)+'\n')
    bundle=json.loads((E/'continuation-05/final-bundle-7-binding.json').read_text());saved=[]
    for row in bundle['files']:
        src=ROOT/row['path'];raw=src.read_bytes();assert sha(raw)==row['sha256'];dest=N/'bundle-7-before'/Path(row['path']).relative_to('frontend/dist');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);saved.append({'source':row['path'],'backup':str(dest),'bytes':len(raw),'sha256':sha(raw)})
    write(N/'bundle-7-before.json',{'files':saved,'source_not_changed':True})
    print(json.dumps({'permit':permit['id'],'verified':len(verified),'bundle7_saved':len(saved),'activity_elapsed_seconds':(mono-anchor)/1e9,'runtime':0,'Q':'FROZEN'},ensure_ascii=False))
if __name__=='__main__':main()
