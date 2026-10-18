"""浏览器原件与最终资产的标准库核对；不开浏览器、服务或HTTP。"""
import collections,json,time
from urllib.parse import urlsplit
from review_io import ROOT,OWN,load,save,sha
from review_evidence import BASE,BATCHES
started=time.perf_counter();b3=BASE/BATCHES['B3'];b4=BASE/BATCHES['B4'];final=load(b4/'as-run/manifest.json')
oldfacts=load(b3/'repair-browser/facts.json');oldtimeline=load(b3/'repair-browser/timeline.json')
facts=load(b4/'readonly-browser/facts.json');requests=load(b4/'readonly-browser/requests.json');timeline=load(b4/'readonly-browser/timeline.json');assets=load(b4/'readonly-browser/served-assets.json');inputs=load(b4/'readonly-browser-input.json');projection=load(b4/'readonly-projection-raw.json');drafts=load(b4/'readonly-browser/drafts.json')
snapshots=[r['value'] for r in oldtimeline if r.get('kind')=='actual_api' and r.get('method')=='GET' and r.get('url')==f"/api/activities/{inputs['ui']['activity_id']}/teaching/workspace"]
asset_checks=[]
for asset in assets:
    rel='frontend/dist'+urlsplit(asset['url']).path
    asset_checks.append({'path':rel,'captured_sha256':asset['sha256'],'final_sha256':sha(ROOT/rel),'manifest_sha256':final[rel],'bytes':asset['bytes'],'matches':asset['sha256']==sha(ROOT/rel)==final[rel]})
project_values={r['path']:r['value'] for r in projection};native_citations=[]
for route,value in inputs['routes'].items():
    if '/citations/' in route:native_citations.append({'route':route,'actual_projection_equal':value==project_values.get(route),'record_id':route.split('/records/')[1].split('/')[0]})
checks={'7_checks':len(facts['checks'])==7 and all(c['status']=='pass' for c in facts['checks']),'56_GET_0_other':len(requests)==56 and all(r['method']=='GET' for r in requests),'no_external':not any(r.get('grade')=='blocked_outside_virtual_origin' for r in requests),'no_page_asset_error':not any(r.get('kind') in ('pageerror','asset_capture_error') for r in timeline),'final_assets':all(a['matches'] for a in asset_checks),'A1_original_HTTP':inputs['workspace_A1'] in snapshots,'A2_original_HTTP':inputs['workspace_A2'] in snapshots,'same_exercise_distinct_answer':inputs['workspace_A1']['head']['exercise_record_id']==inputs['workspace_A2']['head']['exercise_record_id'] and inputs['workspace_A1']['head']['answer_record_id']!=inputs['workspace_A2']['head']['answer_record_id'],'native_read_50':len(projection)==50,'PG_no_business_write':inputs['pg_before']==inputs['pg_after'],'native_citation_equal':all(c['actual_projection_equal'] for c in native_citations)}
method=json.loads((OWN/'independent-method-bindings-v2.json').read_text(encoding='utf-8'))
counts={k:len(v['methods']) for k,v in method.items() if isinstance(v,dict) and 'methods' in v}
out={'B3_status':oldfacts['status'],'B3_error':oldfacts['error'],'B3_completed_checks':[{'name':c['name'],'status':c['status'],'grade':c.get('grade')} for c in oldfacts['checks']],'B3_actual_UI_POST_actions':[r['body']['action'] for r in oldtimeline if r.get('kind')=='request' and r.get('method')=='POST' and r.get('url','').endswith('/teaching/commands')],'B4_checks':checks,'B4_check_labels':[{'name':c['name'],'status':c['status'],'grade':c.get('grade')} for c in facts['checks']],'requests_counter':dict(collections.Counter(r['method'] for r in requests)),'asset_checks':asset_checks,'native_citations':native_citations,'A1_head':inputs['workspace_A1']['head'],'A2_head':inputs['workspace_A2']['head'],'native_drafts':drafts,'snapshot_controls':inputs['snapshot_controls'],'methods_corrected_counts':counts,'limit':'B4虚拟同源只读回放，不是新HTTP认证/POST/业务事务；PG投影50读使用合成request上下文；native WebLocks/IDB/UI为真实浏览器动作。'}
save('independent-browser-binding.json',out)
for k,v in out.items():
    if k not in ('native_drafts','native_citations'):print(k,json.dumps(v,ensure_ascii=False))
print('drafts',len(drafts),'all_checks',all(checks.values()))
with (OWN/'helpers.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'action':'browser binding','seconds':time.perf_counter()-started})+'\n')
