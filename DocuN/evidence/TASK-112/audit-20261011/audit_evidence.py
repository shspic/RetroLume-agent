"""TASK-112 原件解析与独立数值核算；仅标准库、文件元数据，不执行产品。"""
import pathlib,json,hashlib,sys,math,datetime,time,collections
ROOT=pathlib.Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=pathlib.Path(__file__).resolve().parent

def load(path):
    p=pathlib.Path(path);p=p if p.is_absolute() else ROOT/p
    b=p.read_bytes()
    with (OUT/'reads.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic=time.perf_counter(),path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),purpose='raw-evidence-analysis'),ensure_ascii=False)+'\n')
    data=b.decode('utf-8-sig')
    return ([json.loads(line) for line in data.splitlines() if line.strip()] if p.suffix=='.jsonl' else json.loads(data)),p

def persist(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(saved=str(OUT/name),summary=brief(value)),ensure_ascii=False,indent=2))

def brief(v,depth=0):
    if depth>=3:
        if isinstance(v,list):return {'count':len(v),'sample':v[0] if v and not isinstance(v[0],(dict,list)) else None}
        if isinstance(v,dict):return {'keys':list(v)}
        return v
    if isinstance(v,dict):return {k:brief(x,depth+1) for k,x in v.items()}
    if isinstance(v,list):return {'count':len(v),'first':brief(v[0],depth+1) if v else None}
    return v

with (OUT/'commands.jsonl').open('a',encoding='utf-8') as f:
    f.write(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic=time.perf_counter(),argv=sys.argv,scope='只读原件与数值oracle'),ensure_ascii=False)+'\n')

mode=sys.argv[1];x,p=load(sys.argv[2])
if mode=='brief':
    print(json.dumps(brief(x),ensure_ascii=False,indent=2))
elif mode=='ui':
    acks=[];previous={}
    for entry in x['acks']:
        b=entry.get('body',{});values=b.get('input_values',{});reads=b.get('readouts',[]);figures=b.get('figures',[])
        result=dict(preview_id=b.get('preview_id'),generation=b.get('generation'),seq=b.get('seq'),accepted=b.get('accepted'),error=b.get('error_code'),input_values=values,readouts=reads,figures=figures)
        if values and b.get('accepted'):
            if 'hctl_m' in values:
                expected=float(values['hctl_m'])*9.8*float(values['hctl_h'])
                result['oracle']=expected;result['readout_matches']=all(abs(float(r['value'])-expected)<=1e-9 for r in reads)
                result['figure_matches']=len(figures)==1 and len(figures[0]['points'])==1 and abs(figures[0]['points'][0][1]-expected)<=1e-9
            elif 'hctl_n' in values:
                n=int(values['hctl_n']);k=int(values['hctl_k']);q=float(values['hctl_p'])
                probs=[math.comb(n,i)*q**i*(1-q)**(n-i) for i in range(n+1)]
                result['oracle']=probs[k];result['readout_matches']=all(abs(float(r['value'])-probs[k])<=1e-9 for r in reads)
                result['figure_matches']=len(figures)==1 and len(figures[0]['points'])==len(probs) and all(abs(row[1]-expected)<=1e-9 for row,expected in zip(figures[0]['points'],probs))
                result['probability_sum']=sum(probs)
            previous[b.get('preview_id')]=(values,reads,figures)
        elif b.get('accepted') is False:
            result['preserves_last_snapshot']=previous.get(b.get('preview_id'))==(values,reads,figures)
        acks.append(result)
    frames=[]
    for row in x['frames']:
        bp=p.parent/row['file'];b=bp.read_bytes();h=hashlib.sha256(b).hexdigest()
        frames.append(dict(path=str(bp),sha256=h,match=h==row['sha256'],bytes=len(b),preview_id=row['preview_id'],generation=row['generation'],dimensions=[int.from_bytes(b[16:20],'big'),int.from_bytes(b[20:24],'big')]))
    records=[brief(row) for row in x['records']]
    persist('normal-ui-oracle.json',dict(source=str(p),acks=acks,frames=frames,records=records,requests=len(x['requests'])))
elif mode=='refs':
    items=[]
    def visit(v):
        if isinstance(v,dict):
            q=v.get('path');h=v.get('sha256')
            if isinstance(q,str) and isinstance(h,str) and len(h)==64:
                pp=pathlib.Path(q);pp=pp if pp.is_absolute() else p.parent/pp
                if pp.exists():
                    bb=pp.read_bytes();hh=hashlib.sha256(bb).hexdigest();items.append(dict(path=str(pp),expected=h,actual=hh,match=hh==h,bytes=len(bb)))
                else:items.append(dict(path=str(pp),expected=h,match=False,missing=True))
            for vv in v.values():visit(vv)
        elif isinstance(v,list):
            for vv in v:visit(vv)
    visit(x);persist(sys.argv[3],dict(source=str(p),count=len(items),mismatches=[r for r in items if not r['match']],items=items))
elif mode=='stop':
    proof=x.get('proof',x);registry=None
    rp=p.parent/'registry.json'
    if rp.exists():registry,_=load(rp)
    kp=p.parent/'kernel-premises.json';kernel=None
    if kp.exists():kernel,_=load(kp)
    events=proof.get('events',{});rows=[json.loads(line) for line in events.get('stdout','').splitlines() if line.strip()]
    aft=proof.get('after',proof.get('inspect',{}));s=aft.get('state',{});host=aft.get('host',{})
    prem=kernel.get('processes',{}) if kernel else {};pid1=next((r for r in prem.get('rows',[]) if r.get('pid')==1),{})
    cdigest=lambda v:hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()
    result=dict(source=str(p),preview_id=x.get('preview_id',registry.get('preview_id') if registry else None),state=x.get('state'),confirmed=x.get('confirmed'),error=x.get('error_code'),tree=proof.get('tree_confirmation'),cid=proof.get('cid'),image=proof.get('image_id'),nonce=proof.get('nonce'),start_ns=proof.get('start_ns'),end_ns=proof.get('end_ns'),wait_code=proof.get('wait',{}).get('code'),event_call_code=events.get('code'),die_events=[row for row in rows if row.get('Actor',{}).get('ID')==proof.get('cid') and row.get('Action')=='die'],attach_eof=proof.get('attach_eof_confirmed'),reaper_ended=proof.get('owned_reaper_ended'),after_state=s,host=host,kernel_digest_matches=kernel is not None and cdigest(kernel)==proof.get('kernel_premises_sha256'),kernel=brief(prem),pid1=pid1,jobs={k:proof.get(k) for k in ('supervisor_cli_windows_job','reaper_windows_job')},registry_deadline=registry.get('deadline_ns') if registry else None,premises=registry.get('job_premises') if registry else None)
    persist(sys.argv[3],result)
elif mode=='records':
    for i,row in enumerate(x.get('records',x if isinstance(x,list) else [])):
        print(i,json.dumps(brief(row,1),ensure_ascii=False))
elif mode=='lifecycle':
    result={k:v for k,v in x.items() if k not in ('requests','held','discarded')}
    for key in ('held','discarded'):
        value=x.get(key,{})
        result[key]=value
    result['requests']=x.get('requests',[])
    persist(sys.argv[3],result)
elif mode=='normal-runtime':
    results=[]
    for kind,binding in x['bindings'].items():
        preview=binding['preview'];folder=ROOT/'DocuN/evidence/TASK-111/execution/continuation-04/synthetic/control'/preview['preview_id']
        ready,_=load(folder/'ready-packet.json');body=ready['body'];observations=[]
        def snap(v):
            return dict(frames=v.get('frames'),targets=v.get('targets'),dom=v.get('dom'),capability_events=v.get('capability_events'))
        initial=snap(body['observation'])
        for pp in sorted(folder.glob('engine-observation-*.json')):
            ob,_=load(pp);ss=snap(ob['observation'])
            observations.append(dict(file=str(pp),last_input_seq=ob['last_input_seq'],same_frames=ss['frames']==initial['frames'],same_targets=ss['targets']==initial['targets'],dom=ss['dom'],capability_events=ss['capability_events']))
        result,_=load(folder/'supervisor-result.json');registry,_=load(folder/'registry.json')
        results.append(dict(kind=kind,folder=str(folder),image_id=registry['intent']['image_id'],cid=registry['cid'],nonce=registry['intent']['nonce'],node=body['node'],playwright=body['playwright'],version=body['version'],argv=body['arguments'],sandbox=body['sandbox'],renderer=body['renderer_sha256'],load=body['load_manifest_sha256'],description=body['description_sha256'],initial=initial,observations=observations,stop=result))
    persist('normal-runtime-originals-analysis.json',results)
elif mode=='load-manifest':
    results=[]
    for name,h in x['files'].items():
        bb=(p.parent/name).read_bytes();actual=hashlib.sha256(bb).hexdigest();results.append(dict(file=name,expected=h,actual=actual,match=actual==h,bytes=len(bb)))
    persist(sys.argv[3],dict(source=str(p),actual_manifest_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),metadata={k:v for k,v in x.items() if k!='files'},count=len(results),mismatches=[r for r in results if not r['match']],objects=results))
elif mode=='ledger':
    kinds=collections.Counter(row.get('kind','missing') for row in x)
    categories=collections.Counter(row.get('data',{}).get('category') for row in x if row.get('kind')=='reserved')
    examples={}
    for row in x:examples.setdefault(row.get('kind','missing'),row)
    control=[row for row in x if any(key in row.get('kind','').lower() for key in ('batch','permit','continue','limit','root','time','sampl','budget','cleanup'))]
    persist(sys.argv[3],dict(source=str(p),count=len(x),kinds=dict(kinds),categories=dict(categories),examples=examples,control=control))
elif mode=='refresh-audit':
    ev,ep=load(x['source_events']['path']);start=x['actual_reload_request'];endms=x['validation_end_ms']
    end=datetime.datetime.fromtimestamp(endms/1000,datetime.timezone.utc)
    rows=[r for r in ev if r.get('kind')=='reserved' and r.get('pid')==x['api_instance'] and r.get('data',{}).get('category')=='HTTP_total' and r.get('event',0)>=start['event'] and datetime.datetime.fromisoformat(r['at_utc'])<=end]
    recorded=x['all_routes_http'];baseline=[r for r in ev if r.get('event') in (3167,3169)]
    cleanup=[r for r in ev if r.get('kind')=='reserved' and r.get('pid')==x['api_instance'] and r.get('data',{}).get('category')=='HTTP_total' and datetime.datetime.fromisoformat(r['at_utc'])>end and r['data']['detail'].get('method')=='POST']
    persist('refresh-independent-window.json',dict(source=str(p),event_source=str(ep),start_event=start,validation_end_utc=end.isoformat(),computed_count=len(rows),recorded_count=len(recorded),exact_original_rows_equal=rows==recorded,verbs=dict(collections.Counter(r['data']['detail']['method'] for r in rows)),ownerless_client_count=len(x['preview_ownerless_requests']),any_owner_after_reload=any(r.get('owner_present') for r in x['preview_ownerless_requests']),same_deadline=x['same_deadline'],same_starts=x['same_starts'],stop_error_code=x['stop_error_code'],document_events=x['native_document_events'],baseline_stop_attempts=baseline,external_cleanup_POSTs=cleanup))
elif mode=='verify-final-sessions':
    results=[]
    cdigest=lambda v:hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()
    for item in x:
        original,op=load(item['source_proof']['path']);proof=original.get('proof',original);kernel,kp=load(item['kernel']['path']);reg,rp=load(op.parent/'registry.json')
        intent=reg['intent'];after=proof['after'];state=after['state'];host=after['host'];process=kernel['processes']
        own=next((r for r in process['rows'] if r['pid']==process['own_pid']),{});init=next((r for r in process['rows'] if r['pid']==1),{})
        dies=[json.loads(l) for l in proof['events']['stdout'].splitlines() if l.strip()]
        jobchecks={}
        for role,key in [('SUP','supervisor_cli_windows_job'),('REAP','reaper_windows_job')]:
            job=proof[key];premise=reg.get('job_premises',{}).get(role)
            name='Global\\RetroLume.Preview.'+item['preview_id'].replace('-','')+'.'+item['nonce']+'.'+role
            checks={'name':job.get('name')==name,'actual_zero_or_destroyed':type(job.get('ActiveProcesses')) is int and job['ActiveProcesses']==0}
            if job.get('termination_evidence')=='job_destroyed':
                checks.update(no_fake_zero='ActiveProcesses' not in job,error2=job.get('open_error')==2,premise_hash=cdigest(premise)==job['premise_sha256'],no_observer_termination=job.get('observer_terminated') is False,private_actual=premise.get('actual_query') is True and premise.get('handle_noninheritable') is True and premise.get('kill_on_close') is True and premise.get('breakaway_allowed') is False,flags=bool(premise['limit_flags']&0x2000) and not premise['limit_flags']&(0x800|0x1000),instances=[v['instance'] for v in job['instances']]==[premise['owner'],*premise['members']],ended=all(v['current'].get('state')=='exited' or v['current'].get('state')=='running' and v['current'].get('birth')!=v['instance']['birth'] for v in job['instances']))
                checks['actual_zero_or_destroyed']=all(v for k,v in checks.items() if k!='actual_zero_or_destroyed')
            jobchecks[role]=checks
        checks=dict(identity=proof['cid']==item['cid']==reg['cid']==after['id'] and proof['image_id']==item['image_id']==intent['image_id']==after['image'] and proof['nonce']==item['nonce']==intent['nonce'],labels=all(after['labels'].get(k)==v for k,v in intent['labels'].items()),kernel_hash=cdigest(kernel)==proof['kernel_premises_sha256'],kernel_expected=process['kernel']==intent['kernel_release']=='6.6.114.1-microsoft-standard-WSL2',private_pid=process['own_namespace']==process['init_namespace']==init.get('pid_namespace')==own.get('pid_namespace') and init.get('NSpid')=='1' and bool(init.get('birth_ticks')),uid_gid=process['own_uid']==process['own_gid']==10001 and own.get('NoNewPrivs')=='1' and own.get('CapEff')=='0000000000000000',wait=proof['wait']['code']==0,die=any(d.get('Action')=='die' and d.get('Actor',{}).get('ID')==item['cid'] and d['Actor']['Attributes'].get('retrolume.nonce')==item['nonce'] for d in dies),ended=state['Running'] is False and state['Pid']==0 and state['Restarting'] is False,init_no_restart=host['Init'] is True and host['PidMode']=='' and host['IpcMode']=='private' and host['RestartPolicy']['Name']=='no',physical_limits=host['Memory']==host['MemorySwap']==1073741824 and host['NanoCpus']==1000000000 and host['PidsLimit']==256 and host['ShmSize']==67108864,isolation=host['NetworkMode']=='none' and host['ReadonlyRootfs'] is True and host['Privileged'] is False and host['CapDrop']==['ALL'] and not host['CapAdd'] and after['user']=='10001:10001' and not after['ports'] and all(m['Type']=='tmpfs' for m in after['mounts']),proof_kind=proof['tree_confirmation']=='private_pid_init_terminated',EOF=proof.get('attach_eof_confirmed') is True,reaper=proof.get('owned_reaper_ended') is True,persistent_hash=cdigest(proof)==item['confirmation_sha256'],original_D=reg['deadline_ns']==item['deadline_ns'])
        results.append(dict(preview_id=item['preview_id'],name=item['name'],source=str(op),checks=checks,jobs=jobchecks,physical_finished=state['FinishedAt'],deadline=item['deadline_at'],elapsed=item['elapsed_seconds'],reserve=item['reserve_seconds'],all_checks=all(checks.values()) and all(all(j.values()) for j in jobchecks.values())))
    persist('final-session-proof-verification.json',results)
elif mode=='budget-audit':
    budget,bp=load('DocuN/evidence/TASK-111/execution/budget.json')
    reserves=collections.Counter(r.get('data',{}).get('category') for r in x if r.get('kind')=='reserved')
    counters=dict(reserves);counters['offline_related_batches']+=2;counters['internal_inputs']+=sum(r['data']['added'] for r in x if r.get('kind')=='C03_late_input_accounting_correction')
    ends=[r for r in x if r.get('kind')=='batch_end'];real=[r for r in ends if r['data']['kind']=='real']
    corrections=[dict(basis='C02 PG持有总段差',seconds=1.329),dict(basis='C02 root8持有总段差',seconds=.078),dict(basis='C04 PG停机确认段',seconds=1),dict(basis='C05 cleanup-only PG持有',seconds=2.891),dict(basis='C05根间持有',seconds=.11),dict(basis='C05最后停机确认',seconds=1.062),dict(basis='C06 root17停机确认',seconds=1.078),dict(basis='C06 root18停机确认',seconds=.953)]
    recorded_real=sum(r['data']['elapsed'] for r in real)+sum(r['seconds'] for r in corrections)
    root6=next(r for r in real if r['data']['number']==6)
    before,beforep=load('DocuN/evidence/TASK-111/execution/cleanup-resume-20261010/pg-before.json');stop,stopp=load('DocuN/evidence/TASK-111/execution/cleanup-resume-20261010/pg-stop.json')
    pg_raw=(beforep.parent/'pg-before.stdout.bin').read_bytes();pg=json.loads(pg_raw)
    held=(stop['end_ns']-root6['at_ns'])/1e9
    result=dict(source=str(p),counts_from_original_events=counters,counts_from_budget=budget['counts'],counter_differences={k:[v,budget['counts'].get(k)] for k,v in counters.items() if budget['counts'].get(k)!=v},root_sum_seconds=sum(r['data']['elapsed'] for r in real),known_corrections=corrections,reproduced_recorded_real=recorded_real,recorded_budget_real=budget['time_seconds']['real'],offline_batch_sum=sum(r['data']['elapsed'] for r in ends if r['data']['kind']=='offline'),roots=[dict(number=r['data']['number'],event=r['event'],elapsed=r['data']['elapsed'],exceeded=r['data']['exceeded']) for r in real],C06_real=453.125+140.282+1.078+.953,current_C06_count_caps=budget['continuation_caps'],C06_new_real_limit=1800,cumulative_real_limit=16200,unaccounted_root6_PG_segment=dict(root_end_ns=root6['at_ns'],root_end_utc=root6['at_utc'],PG_before_inspect_start_ns=before['start_ns'],PG_before_inspect_end_ns=before['end_ns'],PG_running_before_cleanup=pg['running'],PID=pg['pid'],CID=pg['id'],stdout_hash_matches=hashlib.sha256(pg_raw).hexdigest()==before['stdout_sha256'],stop_start_ns=stop['start_ns'],stop_end_ns=stop['end_ns'],stop_return_code=stop['code'],complete_hold_to_stop_confirmation_seconds=held,recorded_plus_complete_hold_seconds=recorded_real+held,excess_vs_16200_if_continuous_hold=recorded_real+held-16200,certainty='PG在独立cleanup前仍运行及现batch账未计该区间为原件事实；从root6结束到stop确认的连续持有基于唯一PG及无中间stop/start记录，物理停机瞬时未采样，不伪作精确秒数。',source_before=str(beforep),source_stop=str(stopp)),offline_failed_27_seconds='缺batch-finally秒数；C06综合phase记时存在，不能把该批内秒数填0')
    persist('execution-budget-independent.json',result)
elif mode=='compiler-metadata':
    import base64,re
    runtime=ROOT/'deploy/preview';names=('runtime.cjs','runtime.css','runtime.html','descriptor.schema.json')
    files={n:hashlib.sha256((runtime/n).read_bytes()).hexdigest() for n in names}
    canon=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
    renderer=hashlib.sha256(canon(files).encode('utf-8')).hexdigest()
    script=(runtime/names[0]).read_text(encoding='utf-8');style=(runtime/names[1]).read_text(encoding='utf-8');template=(runtime/names[2]).read_text(encoding='utf-8')
    bh=lambda s:base64.b64encode(hashlib.sha256(s.encode('utf-8')).digest()).decode('ascii')
    policy="default-src 'none'; script-src 'sha256-"+bh(script)+"'; style-src 'sha256-"+bh(style)+"'; frame-src 'none'; connect-src 'none'; img-src 'none'; font-src 'none'; object-src 'none'; worker-src 'none'; form-action 'none'; base-uri 'none'"
    html=template.replace('__POLICY__',policy).replace('__STYLE__',style).replace('__SCRIPT__',script)
    htmlhash=hashlib.sha256(html.encode('utf-8')).hexdigest()
    sql=(ROOT/'backend/migrations/012_html_explanations.sql').read_text(encoding='utf-8')
    functions=dict(re.findall(r'CREATE FUNCTION public\.(html_\w+)\b.*?AS \$body\$(.*?)\$body\$;',sql,re.S))
    actual_functions=[dict(name=f['proname'],source_exact_matches=functions.get(f['proname'])==f['prosrc'],owner=f['owner'],search_path=f['proconfig'],security_definer=f['prosecdef'],acl=f['acl']) for f in x['functions']]
    fp,fp_path=load('backend/app/preview/schema-fingerprint.json');actualfp=hashlib.sha256(canon(x).encode('utf-8')).hexdigest()
    persist('compiler-and-SQL-metadata.json',dict(source=str(p),runtime_files=files,renderer_sha256=renderer,compiled_html_sha256=htmlhash,compiled_html_bytes=len(html.encode('utf-8')),renderer_matches_SQL=renderer in functions['html_expected_renderer'],html_matches_SQL=htmlhash in functions['html_expected_html'],schema_digest=actualfp,expected_schema=fp,expected_schema_matches=actualfp==fp['sha256'],functions=actual_functions,PDF_column_grants=[r for r in x['qualification_column_acls'] if r['column_acl']],roles=x['roles']))
elif mode=='persistent-sessions':
    index,ip=load('DocuN/evidence/TASK-111/execution/continuation-06/final/session-proof-index.json');rows={r['preview_id']:r for r in x};results=[]
    for item in index:
        row=rows[item['preview_id']];confirmation=json.loads(row['confirmation_receipt']);source,sp=load(item['source_proof']['path']);proof=source.get('proof',source)
        results.append(dict(preview_id=item['preview_id'],state=row['state'],elapsed=row['elapsed_seconds'],reserve=row['reserve_seconds'],cid_from_confirmation=confirmation['cid'],confirmation_bytes=hashlib.sha256(row['confirmation_receipt'].encode('utf-8')).hexdigest(),same_source_proof=confirmation==proof,index_hash_matches=hashlib.sha256(row['confirmation_receipt'].encode('utf-8')).hexdigest()==item['confirmation_sha256']))
    persist('persistent-six-sessions-verification.json',dict(source=str(p),count=len(x),rows=results,new_unconfirmed=[r['preview_id'] for r in x if r['state'] not in ('stopped','failed_unstarted')]))
elif mode=='counterexamples':
    value=x['valid'][0].copy();value['constraints']=None
    body={"schema":"retrolume.preview.init.v2","description":x['valid'][0],"description_sha256":hashlib.sha256(json.dumps(x['valid'][0],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest(),"renderer_sha256":"6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597","viewport":{"width":640,"height":480}}
    body_bytes=json.dumps(body,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    header={"protocol":"retrolume.preview.v2","type":"init","preview_id":"00000000-0000-0000-0000-000000000001","generation":1,"artifact_sha256":"0"*64,"channel_nonce":"0"*64,"seq":0,"body_bytes":len(body_bytes),"body_sha256":hashlib.sha256(body_bytes).hexdigest()}
    hb=json.dumps(header,sort_keys=True,separators=(',',':')).encode('utf-8')
    bom=dict(nonproduction_identity_placeholders=True,canonical_header=header,BOM_header_hex=(bytes([239,187,191])+hb).hex(),body_sha256=header['body_sha256'],body_bytes=len(body_bytes),BOM_prefix='EF BB BF',mechanism='默认TextDecoder先移除起始BOM，比较解码text会漏原字节差异；该数据未被发送或运行')
    persist('static-counterexamples.json',dict(evidence_level='B，数据及源码路径反例，未运行产品或新测试',constraints_null_descriptor=value,BOM_header_metadata=bom,ready_schedule=dict(unit='t0后的ns',wait_enter=7998000000,wait_timeout=20000000,ready_deadline=8000000000,complete_ready_arrival=8005000000,wait_returns=True,deadline_checked_only_on_false=True),stderr_schedule=dict(chunks_bytes=[1024]*9,stderr_EOF_observed=False,stderr_thread_ended_by='超8192分支break',stdout_EOF_later=True,attach_process_ended=True,both_reader_threads_ended=True,production_attach_ended_predicate=True)))
