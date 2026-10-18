"""续作01只读基线与许可冻结；不接触资源或配置秘密。"""
from pathlib import Path
import hashlib, json, shutil
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'DocuN/evidence/TASK-097'
C=E/'continuation-01'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    if (C/'permit.json').exists(): raise ValueError('不得重置许可/主动起点')
    manifest=json.loads((E/'post-manifest.json').read_text(encoding='utf-8'))
    rows=manifest['files'] if isinstance(manifest,dict) else manifest
    mismatches=[]
    for row in rows:
        p=ROOT/row['path']
        if sha(p)!=row['sha256']: mismatches.append(row['path'])
        dst=C/'pre/files'/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    assert not mismatches,mismatches
    rules=json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    rulefacts=[{'path':r['absolute_path'],'expected':r['sha256'],'actual':sha(Path(r['absolute_path']))} for r in rules]
    assert all(x['expected']==x['actual'] for x in rulefacts)
    write(C/'rules-check.json',rulefacts)
    extra=['DocuN/evidence/TASK-097/attempt-ledger.json','DocuN/evidence/TASK-097/supervision-ledger.json',
        'DocuN/results/TASK-097-result.md','DocuN/tasks/TASK-097.md','DocuN/results/TASK-097-work-decision.md',
        'DocuN/evidence/TASK-097/orchestration-receipt-01/receipt.json','DocuN/evidence/TASK-097/budget-final.json']
    for rel in extra:
        p=ROOT/rel;dst=C/'pre/files'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    receipt=ROOT/extra[-2]
    assert sha(receipt)=='319e4fb39b8226cdbd904a1820dcecb3d176074c22d9170a1ec9f95cb9bfe220'
    write(C/'pre-manifest.json',{'initial_files':rows,'extra':[{'path':r,'sha256':sha(ROOT/r),'bytes':(ROOT/r).stat().st_size} for r in extra],'mismatches':mismatches})
    write(C/'permit.json',{'task':'TASK-097','result':'R-091','permit':'continuation-01',
        'active_started_epoch':1790924106.880,'active_started_at':'2026-10-02T06:55:06.880+00:00',
        'prepared_at':datetime.now(timezone.utc).isoformat(),'card_sha256':sha(ROOT/'DocuN/tasks/TASK-097.md'),
        'baseline':{'entries':8,'starts':8,'sup':15,'browser_actual':3,'browser_driver':4,
            'business_seconds':226.312,'cleanup_seconds':4.937,'offline_seconds':111.140,'active_seconds':12681.232110738754},
        'added_limits':{'entries':4,'starts':4,'sup':8,'browser_actual':3,'browser_driver':3,
            'business_seconds':1200,'cleanup_seconds':240,'offline_seconds':600,'active_seconds':10800}})
    print('continuation-01 baseline 111 / rules 7 verified; old ledgers and result copied; no resource started')

if __name__=='__main__':main()
