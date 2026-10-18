"""只读五方法原件及新前端版本，保存给编排的限定核证。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib,json
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
C06=ROOT/'DocuN/evidence/TASK-111/execution/continuation-06'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def linked(r):
    p=Path(r['path']);assert info(p)==dict(bytes=r['bytes'],sha256=r['sha256']);return load(p)
five=load(C06/'final/five-methods-final.json')
faults=[]
for r in five['stops']:
    scenario=r['scenario'];assert scenario['status']=='PASS_REAL_REMAINING_SCENARIO' and not scenario['extra_job_handles_held']
    for key in ('pretrigger','trigger','before_external_cleanup','natural_EOF','same_root_recovery','actor_source'):
        linked(r[key])
    recovery=linked(r['same_root_recovery']);before=recovery['before'];after=recovery['after'];pipes=linked(r['natural_EOF'])['pipes']
    assert before['reserve_seconds']==60 and before['elapsed_seconds'] is None and before['reserved_seconds']>=60
    assert after['state']=='stopped' and after['elapsed_seconds']==60 and after['reserved_seconds']==0
    assert len(pipes)==2 and all(p['actual_eof'] for p in pipes)
    assert r['external_kill_used'] is False
    faults.append(dict(scenario=scenario['scenario'],result=scenario['status'],recovery=r['same_root_recovery'],before_reserved=before['reserved_seconds'],after_elapsed=after['elapsed_seconds'],natural_EOF=True,external_kill=False,root=recovery['root']))
bindings=load(C06/'final/as-run-bindings.json')
build=linked(bindings['refresh_build'])
for key in ('hidden_unload_attempt','refresh_attempt','control_path_source','hard_deadline_source'):linked(bindings[key])
changes=load(C06/'final/source-changes.json')
for r in changes:
    for key in ('pre','post','diff'):
        record=r.get(key)
        if isinstance(record,dict) and record.get('path'):assert info(Path(record['path']))==dict(bytes=record['bytes'],sha256=record['sha256'])
product=[r['path'] for r in changes if r.get('product')]
assert product==['frontend/src/explanations/HtmlExplanationPanel.tsx']
result=dict(at=datetime.now(timezone(timedelta(hours=8))).isoformat(),faults=faults,build_metadata_keys=list(build),source_changes=len(changes),product_changes=product,
  hidden_unload_test_sha=bindings['hidden_unload_source_sha256'],refresh_test_sha=bindings['refresh_exact_source_sha256'],
  mixed_frontend_versions_require_auditor_scope_decision=True,full_parent_acceptance=False,no_dynamic_runs=True)
(OUT/'methods-byte-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
