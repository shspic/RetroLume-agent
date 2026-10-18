"""Bounded JSON/hash reconciliation of existing browser facts. No browser/Node."""
import datetime as dt,hashlib,json,sys,time
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');R=Path('D:/shspic/project_NO3_RetroLume-agent');C=R/'DocuN/evidence/TASK-117/execution/continuation-07';O=R/'DocuN/evidence/TASK-118/audit/review-01';T=time.perf_counter();access=[]
def raw(p):
 b=p.read_bytes();access.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
v=load(C/'root-25/attempt-03/proof.json');timeline=load(C/'network-timeline.json');asrun=load(C/'browser-as-run.json');images=load(C/'screenshots.json')
facts=[]
for case in v['cases']:
 rows=[r for r in v['requests'] if r.get('case')==case['name']];posts=[r for r in rows if r['method']=='POST'];queries=[r for r in posts if r['path'].endswith('/retrieval/commands') and r['body'].get('action')=='query'];domains=[r for r in posts if r['path'].endswith('/teaching/commands')]
 facts.append({'name':case['name'],'request_count':len(rows),'POSTs':[{'at':r['at'],'path':r['path'],'action':r['body'].get('action'),'business_key':r['body'].get('business_key')} for r in posts],
 'query_count':len(queries),'domain_count':len(domains),'declared_domain_posts':case.get('post_query_domain_posts'),
 'same_activity':case.get('same_activity'),'query_key_matches_observed':None if not queries else queries[0]['body']['business_key']==case.get('query_key'),
 'original_key_GET_received':None if 'original_key_GET' not in case else case['original_key_GET']['http']==200 and case['original_key_GET']['body']['business_key']==case['query_key'],
 'original_key_GET_observed':None if 'query_key' not in case else any(r['method']=='GET' and r['path'].endswith('/retrieval/commands/'+case['query_key']) for r in rows),
 'draft_retained_observed_by_native_fixture':case.get('draft_full_body_retained'),'domain_sent':case.get('domain_sent'),'changed_only':case.get('changed_only'),
 'owner_changed':None if 'original_owner' not in case else case['original_owner']!=case['owner_after'],'disclosure':case.get('identities'),'model_enabled':case.get('model_enabled'),'no_POST':not posts})
assetchecks=[]
for row in v['assets']:
 p=R/'frontend/dist/assets'/row['url'].rsplit('/',1)[1];b=raw(p);assetchecks.append({'url':row['url'],'expected':row['sha256'],'actual':hashlib.sha256(b).hexdigest(),'match':row['sha256']==hashlib.sha256(b).hexdigest()})
bindings=[]
for row in asrun['script_and_source']:
 p=Path(row['path']) if Path(row['path']).is_absolute() else R/row['path'];b=raw(p);bindings.append({'path':str(p),'match':hashlib.sha256(b).hexdigest()==row['sha256']})
screenchecks=[]
for row in images['files']:
 b=raw(Path(row['path']));screenchecks.append({'path':row['path'],'match':len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']})
result={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'cases':facts,'proof_requests_equal_timeline':v['requests']==timeline['requests'],'proof_assets_equal_timeline':v['assets']==timeline['actual_asset_responses'],
 'asset_count':len(assetchecks),'asset_distinct_paths':sorted({x['url'] for x in assetchecks}),'asset_mismatches':[x for x in assetchecks if not x['match']],
 'asrun_bindings':bindings,'screen_checks':screenchecks,'external_attempts':v['external_attempts'],'unknown_routes':v['unknown_routes'],'observer_errors':v['observation_errors'],
 'context_closed':v['context_closed'],'server_closed':v['server_closed'],'accesses':access,'elapsed_seconds':time.perf_counter()-T}
(O/'browser-facts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='accesses'},ensure_ascii=False,indent=2))
