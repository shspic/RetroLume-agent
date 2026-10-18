"""Read-only version and control metadata; no original function execution."""
from pathlib import Path
import ast
import collections
import datetime as dt
import hashlib
import json
import stat
import time

ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=ROOT/'DocuN/evidence/TASK-115/review-02'
C03=ROOT/'DocuN/evidence/TASK-114/implementation/continuation-03'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def norm(p):return Path(str(p).replace('\\\\','/').replace('\\','/'))
def identity(p):
    p=norm(p)
    for parent in [p,*p.parents]:
        if parent.exists() and getattr(parent.lstat(),'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT:raise RuntimeError('reparse refused '+str(parent))
    value={'path':str(p),'exists':p.is_file()}
    if value['exists']:
        b=p.read_bytes();value.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    return value
def write(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

protected={row['path']:row for row in read(OUT/'protected-before.json')}
methods=read(C03/'final/method-index.json')['methods']
binding_checks=[]
for method in methods:
    base=ROOT/norm(method['as_run'])
    for row in method.get('tested_file_bindings',[]):
        rel=norm(row['path'])
        p=base/rel
        if not p.exists() and (base/'source'/rel).exists():p=base/'source'/rel
        actual=identity(p)
        final=identity(ROOT/rel)
        computed=actual['exists'] and actual['sha256']==final.get('sha256')
        entry={'label':method['label'],'relative_path':row['path'],'as_run_actual':actual,'final_actual':final,'as_run_hash_matches_record':actual.get('sha256')==row.get('as_run_sha256'),'final_hash_matches_record':final.get('sha256')==row.get('final_sha256'),'computed_same_final':computed,'same_final_flag_matches':computed==row['same_final_bytes']}
        binding_checks.append(entry)
        protected[actual['path']]=actual
write('tested-file-binding-checks.json',binding_checks)

result=read(C03/'batches/c03-browser-1210447187000000/result.json')
requests=result['requests']
post_counts=collections.Counter(r['path'] for r in requests if r['method']=='POST')
asset_gets=[r for r in requests if r['method']=='GET' and r['path'].startswith('/assets/')]
actions=[r for r in requests if r['method']=='POST' and (r['path'] in ['/api/data/restore-jobs','/api/data/jobs'] or r['path'].endswith('/activate-readonly'))]

control=read(OUT/'control-original-analysis.json')
old=read(C03/'pre/receipt.json')
resources=control['resources']
delivery=control['final_delivery']
new_resources=[r for r in resources if r not in old.get('resources',{})] if isinstance(resources,dict) else [r for r in resources if r not in old.get('resources',[])]
observations=[{'path':str(p),'value':read(p)} for p in sorted((C03/'observations').glob('*.json'))]
accepted=read(C03/'accepted.json')

current_rules=read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
rules_no_replacement=[{'path':r['absolute_path'],'contains_U_FFFD':'\ufffd' in r['absolute_path'],'current_hash':identity(norm(r['absolute_path']))['sha256'],'locked_hash':r['sha256']} for r in current_rules]
files=[row for row in read(C03/'final/manifest.json')['files'] if row['path'] in ['backend/app/data_exit/reference.py','backend/app/data_exit/restore.py','backend/app/data_exit/operations.py','backend/app/data_exit/readability.py','backend/app/data_exit/api.py','backend/app/data_exit/schema.py','backend/tests/test_data_exit_c03.py','frontend/src/data/DataWorkspace.tsx','frontend/src/data/context.tsx','frontend/src/data/dataApi.ts','frontend/src/data/ReadonlyRecords.tsx','frontend/src/main.tsx','frontend/tests/task114-c03-inputs.mjs','frontend/dist/index.html','frontend/dist/assets/index-DZduJTtr.js']]
summary={'sample':{'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'mono_ns':time.monotonic_ns()},'binding_count':len(binding_checks),'binding_record_mismatches':[b for b in binding_checks if not(b['as_run_hash_matches_record'] and b['final_hash_matches_record'] and b['same_final_flag_matches'])],'false_final_bindings':[{'method':b['label'],'path':b['relative_path']} for b in binding_checks if not b['computed_same_final']],'POST_counts':dict(post_counts),'explicit_consumer_actions':actions,'loaded_final_asset_requests':asset_gets,'no_current_rule_replacement_character':all(not r['contains_U_FFFD'] for r in rules_no_replacement),'rules':rules_no_replacement,'final_files':files,'observations':observations,'accepted_preflight_failures':accepted['preflight_failures'],'accepted_correction':accepted['rule_path_resolution_correction'],'C03_control_old_resources_exact':control['resources_old_exact'],'C03_control_old_continuations_exact':control['continuation_history_old_exact'],'C03_old_events_prefix_exact':control['old_events_exact_prefix'],'new_resources':new_resources,'new_resource_close':delivery['new_resource_closure'],'new_event_count':len(control['new_events']),'new_event_shapes':[{'keys':list(e),'kind':e.get('kind')} for e in control['new_events'][:3]],'all_new_resources_stopped':all(r['state']=='stopped' and r['last_stop']['process_ended'] and r['last_stop']['actual_browser_close'] for r in delivery['new_resource_closure'])}
write('final-binding-and-control-summary.json',summary)
write('protected-before.json',list(protected.values()))
print(json.dumps({'binding_count':len(binding_checks),'binding_mismatch_count':len(summary['binding_record_mismatches']),'false_final_bindings':summary['false_final_bindings'],'POST_counts':dict(post_counts),'loaded_bundle_requests':[r for r in asset_gets if r['path']=='/assets/index-DZduJTtr.js'],'old_resources_exact':summary['C03_control_old_resources_exact'],'old_continuations_exact':summary['C03_control_old_continuations_exact'],'old_events_prefix':summary['C03_old_events_prefix_exact'],'new_resources_closed':summary['all_new_resources_stopped'],'observations':[{'path':o['path'],'ready':o['value'].get('ready'),'available_bytes':o['value'].get('available_bytes')} for o in observations],'protected_count':len(protected)},ensure_ascii=True,indent=2))
