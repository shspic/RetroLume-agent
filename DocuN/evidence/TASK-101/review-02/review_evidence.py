"""仅标准库读本次原件；不导入或执行产品、测试、作者oracle。"""
import ast, collections, hashlib, json, pathlib, re, sys, time
from review_io import ROOT, OWN, load, read, save, sha
BASE = ROOT/'DocuN/evidence/TASK-100/audit-repair-03'
BATCHES = {
 'B1':'2026-10-05T101329.428351-0000-repair-combo',
 'B2':'2026-10-05T101919.561049-0000-repair-combo',
 'B3':'2026-10-05T103020.095611-0000-repair-combo',
 'B4':'2026-10-05T110007.993696-0000-readonly-browser-combo',
 'offline':'2026-10-05T105948.833483-0000-offline',
 'build':'2026-10-05T105833.370399-0000-frontend-build',
}
def obj(value):
    return load(BASE/value)
def compact(value, depth=1):
    if isinstance(value, dict):
        return {k:compact(v,depth-1) if depth else ('dict '+str(list(v)[:20]) if isinstance(v,dict) else 'list '+str(len(v)) if isinstance(v,list) else str(v)[:160]) for k,v in value.items()}
    if isinstance(value,list):return {'length':len(value),'first':compact(value[0],depth) if value else None}
    return value
def peek(values):
    for name in values:print(name,json.dumps(compact(obj(name)),ensure_ascii=False))
def versions():
    results={}
    for label, name in BATCHES.items():
        folder=BASE/name; manifest=folder/'as-run-files.json'
        if not manifest.exists():continue
        before=load(manifest);after=load(folder/'after-files.json'); items=[]
        for filename,digest in before.items():
            rel=pathlib.Path(filename)
            if rel.is_absolute():rel=rel.relative_to(ROOT)
            snap=folder/'as-run'/rel;current=ROOT/rel
            items.append({'path':rel.as_posix(),'as_run_sha256':digest,'full_copy_sha256':sha(snap) if snap.is_file() else None,'after_sha256':after.get(filename),'current_sha256':sha(current) if current.is_file() else None})
        methods=[]
        for rawdir in ('repository-raw','http-raw','common-raw','repair-raw'):
            log=folder/rawdir/'stderr.txt'
            if not log.exists():continue
            lines=read(log)
            for line in lines:
                match=re.match(r'(test_\w+) \((.+)\) \.\.\. (.+)$',line)
                if match:methods.append({'method':match[1],'class':match[2],'outcome':match[3],'log':str(log)})
        results[label]={'items':items,'methods':methods,'not_copy_matched':[r['path'] for r in items if r['full_copy_sha256']!=r['as_run_sha256']],'during_drift':[r['path'] for r in items if r['after_sha256']!=r['as_run_sha256']],'changed_current':[r['path'] for r in items if r['current_sha256']!=r['as_run_sha256']]}
    save('independent-as-run-versions.json',results)
    for label,v in results.items():print(label,'files',len(v['items']),'methods',len(v['methods']),'bad_copies',v['not_copy_matched'],'during_drift',v['during_drift'],'changed_final',v['changed_current'])
def observations():
    folder=BASE/BATCHES['B3']; observations=[]
    for p in sorted((folder/'observations').glob('*.json')):
        observations.append({'file':str(p),'sha256':sha(p),'raw':load(p)})
    save('independent-observations.json',observations)
    counts=collections.Counter(o['raw'].get('kind',o['raw'].get('name','?')) for o in observations)
    print('kinds',dict(counts))
    for kind in counts:
        example=next(o for o in observations if o['raw'].get('kind',o['raw'].get('name','?'))==kind)
        print(kind,json.dumps(compact(example['raw']),ensure_ascii=False))
def windows_overview():
    folder=BASE/BATCHES['B3'];facts=load(folder/'repair-windows-facts.json')
    print('cases',json.dumps(facts['cases'],ensure_ascii=False))
    for fact in facts['facts']:print('fact',json.dumps(fact,ensure_ascii=False))
    for s in facts['session_outcomes']:
        print('session',json.dumps({k:v for k,v in s.items() if k not in ('timing_diagnostic','model_receipt','tool_receipt')},ensure_ascii=False))
    obs=json.loads((OWN/'independent-observations.json').read_text(encoding='utf-8'))
    for o in obs:
        if o['raw']['kind']=='provider_started':
            v=o['raw']['value'];print('provider_input',v['marker'],o['raw']['pid'])
            messages=v['payload']['messages']
            for m in messages:
                if m.get('role')=='user':print('user',str(m['content'])[:3500]);break
            break
def controls():
    allraw={}
    for label in ('B1','B2','B3','B4'):
        print('BATCH',label)
        folder=BASE/BATCHES[label];batch={}
        for fname in ('summary.json','segments.json','controller-result.json','cleanup.json','controller-launch.json'):
            p=folder/fname
            if p.exists():batch[fname]=load(p)
        allraw[label]=batch
        print('summary',batch['summary.json']['status'],'segments',[(s['name'],s['status'],round(s.get('elapsed',0),3),s.get('exit_code'),s.get('reason'),s.get('error')) for s in batch['segments.json']])
        for fname in ('controller-result.json','cleanup.json','controller-launch.json'):print(fname,json.dumps(compact(batch.get(fname)),ensure_ascii=False))
    for fname in ('attempt-ledger.json','final-freeze-before-package-tail.json','final-freeze-and-usage.json','final-resource-read.json'):
        allraw[fname]=obj(fname)
    save('independent-control-raw.json',allraw)
    ledger=allraw['attempt-ledger.json'];counter=collections.Counter();seconds=collections.Counter()
    for e in ledger['events']:
        print('event',json.dumps(e,ensure_ascii=False))
        if e['event']=='consume':counter.update([e.get('kind',e.get('resource','?'))])
        if e['event']=='charge':seconds[e.get('kind',e.get('resource','?'))]+=e.get('seconds',0)
    print('ledger_counts',ledger['counts'],'ledger_seconds',ledger['seconds'],'basic_event_counts',dict(counter),'basic_event_seconds',dict(seconds))
def content_pairs():
    obs=json.loads((OWN/'independent-observations.json').read_text(encoding='utf-8'))
    inputs={o['raw']['pid']:o for o in obs if o['raw']['kind']=='provider_started'}
    paired=[]
    def claims(value,trail=''):
        if isinstance(value,dict):
            if value.get('citations'):
                yield {'path':trail,'claim':{k:v for k,v in value.items() if k!='citations'},'citations':value['citations']}
            for k,v in value.items():yield from claims(v,trail+'/'+k)
        elif isinstance(value,list):
            for i,v in enumerate(value):yield from claims(v,trail+'/'+str(i))
    for returned in obs:
        raw=returned['raw']
        if raw['kind']!='provider_returned':continue
        started=inputs[raw['pid']];iv=started['raw']['value'];rv=raw['value']
        user=json.loads(next(m['content'] for m in iv['payload']['messages'] if m.get('role')=='user'))
        evidence={e['id']:e for e in user['evidence']}
        item={'pid':raw['pid'],'marker':iv['marker'],'mode':iv['mode'],'started_file':started['file'],'returned_file':returned['file'],'task':user['task'],'evidence':user['evidence'],'output':rv['content'],'claims':[]}
        for c in claims(rv['content']):
            c['matches']=[evidence.get(cid) for cid in c['citations']];item['claims'].append(c)
        paired.append(item)
        print('OUTPUT',iv['marker'],iv['mode'],'TASK',user['task'].get('kind'),'CLAIMS',len(item['claims']))
        for c in item['claims']:print(json.dumps(c,ensure_ascii=False))
    save('independent-content-pairs-before-oracle.json',paired)
    print('normal_claim_count',sum(len(p['claims']) for p in paired if p['mode']!='false_met'),'all_claim_count',sum(len(p['claims']) for p in paired))
def control_recalc():
    raw=json.loads((OWN/'independent-control-raw.json').read_text(encoding='utf-8'))
    ledger=raw['attempt-ledger.json'];counts=collections.Counter();seconds=collections.Counter();seq={};events=[]
    for e in ledger['events']:
        if e['event']=='before_action':
            counter=e['counter'];counts[counter]+=1;seq.setdefault(counter,[]).append(e['count'])
        if e['event']=='elapsed':seconds[e['category']]+=e['seconds']
        small={k:v for k,v in e.items() if k!='detail'}
        detail=e.get('detail');small['detail']={k:v for k,v in detail.items() if k not in ('files','dist','accepted_source_changes')} if isinstance(detail,dict) else detail
        events.append(small);print(json.dumps(small,ensure_ascii=False))
    result={'counts_recomputed':dict(counts),'counter_sequence':seq,'seconds_recomputed':dict(seconds),'counts_match':dict(counts)==ledger['counts'],'seconds_match':all(abs(seconds[k]-v)<0.000001 for k,v in ledger['seconds'].items() if k!='active'),'events':events}
    save('independent-control-recalculation.json',result)
    print('RECOMPUTED',json.dumps({k:v for k,v in result.items() if k!='events'},ensure_ascii=False))
    for label in ('B1','B2','B3','B4'):
        print('CLEANUP',label,json.dumps(raw[label]['cleanup.json'],ensure_ascii=False))
    print('FINAL_RESOURCE',json.dumps(raw['final-resource-read.json'],ensure_ascii=False))
def binding_discover():
    facts=obj(BATCHES['B3']+'/repair-windows-facts.json');timeline=obj(BATCHES['B3']+'/repair-windows-http.json')
    for s in facts['session_outcomes']:
        receipt=s['model_receipt'] or s['tool_receipt'];print('receipt',s['run_tag'],json.dumps(compact(receipt,2),ensure_ascii=False))
        if s['model_receipt']:break
    for t in timeline:
        if '/citations/' in t['path']:print('HTTP_CITATION',json.dumps(t,ensure_ascii=False));break
    print('RECORD_PATHS',[(i,t['path'],list(t['response'])[:12] if isinstance(t.get('response'),dict) else None) for i,t in enumerate(timeline) if '/records/' in t['path']])
def actual_bindings():
    folder=BASE/BATCHES['B3'];facts=load(folder/'repair-windows-facts.json');timeline=load(folder/'repair-windows-http.json')
    obs=json.loads((OWN/'independent-observations.json').read_text(encoding='utf-8'))
    pairs=json.loads((OWN/'independent-content-pairs-before-oracle.json').read_text(encoding='utf-8'))
    sessions=[];normal_by_operation={}
    for s in facts['session_outcomes']:
        events=[o['raw'] for o in obs if o['raw'].get('value',{}).get('job_name')==s['job_name']]
        order=[e['kind'] for e in events];wanted=['job_created','job_spawn_suspended','job_resume','job_wait_empty_until','job_close','session_outcome']
        providers=[p for p in pairs if next(o['raw']['at'] for o in obs if o['file']==p['started_file'])>=events[0]['at'] and next(o['raw']['at'] for o in obs if o['file']==p['returned_file'])<=events[-1]['at']]
        receipt=s['model_receipt'] or s['tool_receipt']
        good=order==wanted and events[-1]['value']==s and all(e['value']['worker_pid']==s['pid'] for e in events if e['kind'] in ('job_spawn_suspended','job_resume')) and s['state']=='settled' and s['active_processes_at_end']==0 and s['reserved_seconds']==0 and s['pending_fold_seconds']==0 and not s['cleanup_incomplete'] and receipt['business_commit']=='committed' and receipt['result']['status']=='succeeded'
        entry={'run_tag':s['run_tag'],'activity_id':s['activity_id'],'generation':s['generation'],'job_name':s['job_name'],'worker_pid':s['pid'],'worker_birth':s['worker_created_100ns'],'manager_pid':s['manager_pid'],'manager_birth':s['manager_created_100ns'],'events_order':order,'one_provider':len(providers),'model':s['model_receipt'] is not None,'operation_id':receipt['context']['operation_id'],'payload_sha256':receipt['result']['payload_sha256'],'all_checks':good,'settled_seconds':s['settled_seconds']}
        if providers:
            entry['provider_marker']=providers[0]['marker'];entry['provider_mode']=providers[0]['mode']
            normal_by_operation[entry['operation_id']]=providers[0]
        sessions.append(entry)
    # This export is read only after our independent pairing and reasoning were saved.
    exported=load(folder/'content-oracle.json')['actual_records'];bound=[]
    source_text='\n'.join(read(folder/'as-run/backend/tests/fixtures/task100/synthetic_content.py'))
    tree=ast.parse(source_text);material=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MATERIAL' for t in n.targets))
    material_sha=hashlib.sha256(material.encode()).hexdigest()
    for record in exported:
        session=next(s for s in sessions if s['operation_id']==record['operation_id'])
        paired=normal_by_operation[record['operation_id']]
        for claim in record['claims']:
            key=claim['claim_key']
            if key.startswith('n'):
                desired='/nodes/'+str(int(key[1:])-1)
            elif key.startswith('p'):
                desired=next(c['path'] for c in paired['claims'] if c['claim'].get('point_id')==key)
            else:
                group,number=re.match(r'([a-z_]+)([0-9]+)$',key).groups();desired='/'+group+'/'+number
            own=next(c for c in paired['claims'] if c['path']==desired and claim['citation_id'] in c['citations'])
            observed_claim=own['claim'];observed_text=(observed_claim['objective']+'；'+observed_claim['rationale']) if key.startswith('n') else observed_claim.get('text',observed_claim.get('explanation'))
            evidence=next(e for e in own['matches'] if e['id']==claim['citation_id'])
            reqpath=f"/api/activities/{record['activity_id']}/teaching/records/{record['record_id']}/citations/{claim['citation_id']}"
            rawhttp=next(t for t in timeline if t['path']==reqpath and t['status']==200)
            http=rawhttp['response']['citation']
            line_text='\n'.join(material.splitlines()[claim['start_line']-1:claim['end_line']])
            checks={'actual_007_receipt_identity':session['payload_sha256']==record['payload_sha256'],'actual_output_claim_text_equal':observed_text==claim['claim_text'],'catalog_provider_text_equal':evidence['text']==claim['catalog_text'],'HTTP_export_equal':http==claim['http_citation'],'HTTP_original_source_sha':http['original_sha256']==material_sha,'source_line_text_equal':line_text.strip()==claim['catalog_text'].strip(),'version_source_equal':http['version_id']==claim['version_id'] and http['source_id']==claim['source_id'],'fragment_sha_equal':hashlib.sha256(http['text'].encode()).hexdigest()==http['fragment_sha256']}
            bound.append({'activity_id':record['activity_id'],'record_id':record['record_id'],'operation_id':record['operation_id'],'payload_sha256':record['payload_sha256'],'claim_key':claim['claim_key'],'independent_output_path':own['path'],'claim_text':claim['claim_text'],'citation_id':claim['citation_id'],'checks':checks,'all_checks':all(checks.values())})
    result={'sessions':sessions,'claims':bound,'material_sha256':material_sha,'exported_records':len(exported),'claim_count':len(bound),'normal_provider_output_count':sum(p['mode']=='normal' for p in pairs),'full_007_payload_independently_rehashed':False,'limit':'007原完整payload未单独导出；采用已绑定的实际JOIN/validate断言、SessionOutcome摘要与原HTTP文本，不冒称从全payload重算。'}
    save('independent-runtime-content-bindings-v3.json',result)
    print('sessions',len(sessions),'all_good',all(s['all_checks'] for s in sessions),'providers',sum(s['one_provider'] for s in sessions),'model',sum(s['model'] for s in sessions),'tool',sum(not s['model'] for s in sessions),'settled_sum',sum(s['settled_seconds'] for s in sessions))
    print('exports',len(exported),'claims',len(bound),'all_good',all(c['all_checks'] for c in bound),'material_sha',material_sha)
    for s in sessions:print('session_binding',json.dumps(s,ensure_ascii=False))
    for c in bound:
        if not c['all_checks']:print('bad_claim',json.dumps(c,ensure_ascii=False))
if __name__=='__main__':
    started=time.perf_counter()
    if sys.argv[1]=='peek':peek(sys.argv[2:])
    elif sys.argv[1]=='versions':versions()
    elif sys.argv[1]=='observations':observations()
    elif sys.argv[1]=='windows-overview':windows_overview()
    elif sys.argv[1]=='controls':controls()
    elif sys.argv[1]=='content-pairs':content_pairs()
    elif sys.argv[1]=='control-recalc':control_recalc()
    elif sys.argv[1]=='binding-discover':binding_discover()
    elif sys.argv[1]=='actual-bindings':actual_bindings()
    else:raise ValueError('unknown action')
    with (OWN/'helpers.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'action':'evidence '+sys.argv[1],'seconds':time.perf_counter()-started})+'\n')
