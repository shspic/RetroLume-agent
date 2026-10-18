"""封存C02实际字节/diff/方法导航，结果追加原字节前缀，旧成果永不覆盖。"""
from datetime import datetime,timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import time
from budget import ROOT,EVIDENCE,CONTROL,Budget


def main():
    budget=Budget();receipt=budget.check(cleanup=True)
    assert not any(r['state']=='running' for r in receipt['resources'])
    before=json.loads((EVIDENCE/'pre-manifest.json').read_bytes());prior={e['path']:e for e in before};paths=set(prior)
    for directory in ('backend/app/data_exit','frontend/src/data','backend/tests/fixtures/task114','frontend/dist'):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for pattern in ('backend/tests/test_data_exit*.py','frontend/tests/task114*.mjs'):paths.update(p.relative_to(ROOT).as_posix() for p in ROOT.glob(pattern))
    paths.update(('README.md','frontend/src/main.tsx'))
    final=EVIDENCE/'final';(final/'source').mkdir(parents=True);(final/'diff').mkdir()
    manifest=[];changed=[];added=[];removed=[]
    for name in sorted(paths):
        path=ROOT/name;pre=EVIDENCE/'pre'/name;raw=path.read_bytes() if path.exists() else None
        sha=hashlib.sha256(raw).hexdigest() if raw is not None else None
        old=prior.get(name,{}).get('sha256')
        change='added' if raw is not None and name not in prior else 'modified' if raw is not None and sha!=old else 'deleted' if raw is None and old else 'unchanged'
        item={'path':name,'bytes':len(raw) if raw is not None else None,'sha256':sha,'change':change,'before_exists':bool(old),'before_sha256':old};manifest.append(item)
        if raw is not None:
            target=final/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        if change in ('modified','deleted'):changed.append(name)
        if change=='added':added.append(name)
        if change=='deleted':removed.append(name)
        if change!='unchanged' and name.endswith(('.py','.tsx','.ts','.md','.json','.html','.mjs')) and not name.startswith('frontend/dist/assets/'):
            old_text=pre.read_text(encoding='utf-8-sig') if pre.exists() else ''
            new_text=raw.decode('utf-8-sig') if raw is not None else ''
            diff=''.join(difflib.unified_diff(old_text.splitlines(True),new_text.splitlines(True),fromfile='pre/'+name,tofile='final/'+name))
            target=final/'diff'/(name+'.diff');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(diff,encoding='utf-8')
    (final/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    # 核原报告/独审/规则未漂移；最终产品副本必须与工作区相同。
    result_path=ROOT/'DocuN/results/TASK-114-result.md';original=result_path.read_bytes()
    assert len(original)==53842 and hashlib.sha256(original).hexdigest()=='c0f970d48ac57d1081e79afa90bcab5822d4c6058e60ed7f9fb6f9b0cd770e2e'
    assert hashlib.sha256((ROOT/'DocuN/results/TASK-115-result.md').read_bytes()).hexdigest()=='7d34ec7e7f433effe3bf51367c68229a566dc525361a30c4b2c496702f4ca67a'
    for item in manifest:
        if item['sha256']:assert hashlib.sha256((final/'source'/item['path']).read_bytes()).hexdigest()==item['sha256']
    for rule in json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_bytes()):assert hashlib.sha256(Path(rule['absolute_path']).read_bytes()).hexdigest()==rule['sha256']
    events=[json.loads(line) for line in (CONTROL/'events.jsonl').read_text(encoding='utf-8').splitlines()]
    offline=[e for e in events if e['kind']=='offline' and e.get('log','').startswith('DocuN/evidence/TASK-114/implementation/continuation-02/')]
    # PG入口工具返回的exit/argv回补明确标示，绝不伪造当时未记录的精确方法时长。
    commands=[]
    for folder in sorted((EVIDENCE/'batches').iterdir()):
        if not folder.is_dir():continue
        result=(folder/'result.json');failure=(folder/'failure.json');browser=(folder/'browser-result.json')
        succeeded=result.exists() or (folder/'result.json').exists()
        label=folder.name
        if label.startswith('c02-source-init-'):script,args='c02_create.py',[]
        elif label.startswith('c02-pg-source-resume-'):script,args='c02_pg_run.py',['source-resume']
        elif label.startswith('c02-pg-source-'):script,args='c02_pg_run.py',['source']
        elif label.startswith('c02-pg-cancel-'):script,args='c02_pg_run.py',['cancel']
        elif label.startswith('c02-pg-normal-'):script,args='c02_pg_run.py',['normal']
        elif label.startswith('c02-http-source-'):script,args='c02_http.py',[]
        elif label.startswith('c02-activate-'):script,args='c02_activate.py',[]
        elif label.startswith('c02-final-http-'):script,args='c02_final_http.py',[]
        elif label.startswith('c02-browser-'):script,args='c02_browser.py',[]
        else:script,args=None,[]
        interpreter='python' if label=='c02-source-init-1155316625000000' else str(ROOT/'backend/.venv/Scripts/python.exe')
        commands.append({'batch':folder.name,'result':str(result.relative_to(ROOT)) if result.exists() else None,
          'arguments':[interpreter,'-B','-X','utf8',str(ROOT/'backend/tests/fixtures/task114'/script),*args] if script else None,
          'failure':str(failure.relative_to(ROOT)) if failure.exists() else None,'known_exit_code':0 if succeeded else 1 if failure.exists() else None,
          'exit_basis':'tool completion/result or failure; delivery backfill, not claimed same-point sampling','duration':'resource intervals in original events; method wall time not independently sampled'})
    (final/'method-index.json').write_text(json.dumps({'offline_exact':offline,'runtime_batches':commands},ensure_ascii=False,indent=2),encoding='utf-8')
    now=datetime.now(timezone.utc);cont=receipt['continuation'];active=sum(((s['end_ns'] or time.monotonic_ns())-s['begin_ns'])/1e9 for s in cont['active_segments'])
    summary={'at':now.isoformat(),'counts':receipt['counts'],'limits':receipt['limits'],'holding_seconds':receipt['real_holding_seconds'],
      'offline_seconds':receipt['offline_seconds'],'C02_active_observed_seconds':active,'activity_basis':'all intervals continuously charged; no pause',
      'changed':changed,'added':added,'removed':removed,'current_files':sum(e['sha256'] is not None for e in manifest),'original_result_sha256':hashlib.sha256(original).hexdigest()}
    (final/'delivery-observation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    report=(EVIDENCE/'report-prefix.md').read_bytes()
    result_path.write_bytes(report+original)
    saved=result_path.read_bytes();assert saved.endswith(original) and saved[:len(report)]==report
    # 全部源/diff/结果已实际保存后才封口活动段；保存动作也在本段内。
    receipt=budget.load();end=time.monotonic_ns();end_utc=datetime.now(timezone.utc).isoformat()
    for root in receipt['continuation']['real_batches']:
        if root['end_ns'] is None:root['end_ns']=end
    segment=receipt['continuation']['active_segments'][-1];segment.update(end_ns=end,end_utc=end_utc,end_reason='C02 result saved and all exact consumers confirmed stopped')
    receipt['continuation'].update(status='delivered_candidate_for_TASK115_review01',result_sha256=hashlib.sha256(saved).hexdigest())
    budget.save(receipt);budget.event('continuation.delivered',{'permit':cont['permit'],'result_sha256':hashlib.sha256(saved).hexdigest(),'old_result_suffix_bytes':len(original),'current_files':summary['current_files'],'counts':receipt['counts']})
    active_final=sum((s['end_ns']-s['begin_ns'])/1e9 for s in receipt['continuation']['active_segments'])
    (final/'delivery.json').write_text(json.dumps({'state':'saved_candidate','path':str(result_path),'bytes':len(saved),'sha256':hashlib.sha256(saved).hexdigest(),
      'old_suffix_preserved':True,'old_suffix_bytes':len(original),'old_suffix_sha256':hashlib.sha256(original).hexdigest(),'active_final_seconds':active_final,'counts':receipt['counts'],'all_owned_stopped':True},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'saved':str(result_path),'old_suffix_preserved':True,'current_files':summary['current_files'],'active_final_seconds':active_final,'bytes':len(saved)}))


if __name__=='__main__':main()
