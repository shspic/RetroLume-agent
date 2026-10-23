"""Compare saved records and hashes only; never imports project/test modules."""
import collections, datetime, difflib, hashlib, json, re
from pathlib import Path
ROOT=Path(r'D:\shspic\project_NO3_RetroLume-agent')
EX=ROOT/'DocuN/evidence/TASK-120/execution'
ENG=EX/'audit-repair-08'
OUT=ROOT/'DocuN/evidence/TASK-121/audit/review-02'
INP=ROOT/'DocuN/evidence/TASK-121/orchestration-review02-20261021'
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def current(p):
    p=Path(p); p=p if p.is_absolute() else ROOT/p
    return sha(p.read_bytes()) if p.is_file() else None
checks=[]
def check(n,ok,detail=None):
    checks.append(dict(check=n,ok=bool(ok),detail=detail))

# Exact preimage identities already verified by review_meta. These two provided
# diffs contain doubled CRs in embedded source lines; strip CRs before parsing.
patch_rows=[]
for name in ('source.diff','fixture-completed.diff'):
    lines=(ENG/name).read_bytes().decode('utf-8-sig').replace('\r','').splitlines();i=0
    while i<len(lines):
        if not lines[i].startswith('--- '): i+=1; continue
        oldname=lines[i][4:]; newname=lines[i+1][4:];rel=newname.removeprefix('after/');i+=2
        old=[] if oldname=='/dev/null' else (ENG/'preimage'/rel).read_text(encoding='utf-8-sig').splitlines()
        new=(ROOT/rel).read_text(encoding='utf-8-sig').splitlines();out=[];pos=0;hunks=[];valid=True
        while i<len(lines) and not lines[i].startswith('--- '):
            m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i])
            if not m: i+=1;continue
            a,ac,b,bc=(int(m[1]),int(m[2] or 1),int(m[3]),int(m[4] or 1));i+=1
            start=a-1 if ac else a;out.extend(old[pos:start]);pos=start;removed=[];added=[]
            while i<len(lines) and not lines[i].startswith(('@@ ','--- ')):
                s=lines[i];i+=1
                if not s or s.startswith('\\ No newline'):continue
                if s[0] in (' ','-'): removed.append(s[1:])
                if s[0] in (' ','+'): added.append(s[1:])
            same=removed==old[pos:pos+ac] and len(removed)==ac and len(added)==bc
            valid=valid and same;pos+=ac;out.extend(added);hunks.append(dict(old_start=a,old_count=ac,new_start=b,new_count=bc,old_context_matches=same))
        out.extend(old[pos:]);valid=valid and out==new
        patch_rows.append(dict(patch=name,path=rel,hunks=hunks,reconstructs_current_normalized_lines=valid))
        check('provided_diff_reconstructs:'+rel,valid)
save('provided-diff-reconstruction.json',patch_rows)

# Bind all saved product rows, and separately retain actual fixture differences.
asrun=[]
for name in ('root-62-batch-01-as-run.json','root-63-batch-01-as-run.json','root-64-batch-01-as-run.json','root-64-batch-02-as-run.json'):
    d=load(ENG/name);products=[r for r in d['files'] if r['path'].startswith(('backend/app/','frontend/src/','frontend/dist/'))]
    drift=[dict(r,actual=current(r['path'])) for r in products if current(r['path'])!=r['sha256']]
    nonproduct=[dict(r,actual=current(r['path'])) for r in d['files'] if r not in products and current(r['path'])!=r['sha256']]
    check('saved_products_equal_final:'+name,not drift,len(products))
    asrun.append(dict(path=name,utc=d['utc'],sha256=current(ENG/name),stage=d['stage'],product_count=len(products),product_drift=drift,fixture_differences=nonproduct))
scope=load(INP/'scope-index.json')
registered=load(INP/'audit-inputs.json')['registered_current_files']
check('registered18_changes15',len(registered)==18 and len(scope['changes'])==15)
fixture_rows=[]
for folder,rel in [('asrun-root063','backend/tests/fixtures/task120/repair08_memory.py'),('asrun-root063','frontend/tests/task120-repair08-memory.mjs'),('asrun-root064','frontend/tests/task120-repair08-memory.mjs'),('asrun-command1000','backend/tests/test_q_repair08.py')]:
    raw=(ENG/folder/rel).read_bytes();now=(ROOT/rel).read_bytes()
    delta='\n'.join(difflib.unified_diff(raw.decode('utf-8-sig').splitlines(),now.decode('utf-8-sig').splitlines(),fromfile=folder+'/'+rel,tofile='final/'+rel,n=3))
    fixture_rows.append(dict(folder=folder,path=rel,saved_sha256=sha(raw),final_sha256=sha(now),normalized_diff=delta))
jsold=(ENG/'asrun-root063/frontend/tests/task120-repair08-memory.mjs').read_bytes()
jsnew=(ROOT/'frontend/tests/task120-repair08-memory.mjs').read_bytes()
rebuilt=jsold.replace(b'api-reopened.json',b'verify-page-reopen.json').replace(b'second-API-reopened-done',b'page-reopened-done')
check('browser64_exact_two_literal_reconstruction',rebuilt==jsnew)
check('browser64_saved_copy_equal', (ENG/'asrun-root064/frontend/tests/task120-repair08-memory.mjs').read_bytes()==jsnew)
save('as-run-comparison.json',dict(products=asrun,fixtures=fixture_rows,browser_extra_hash_timing='post-stop reconstruction, not a contemporaneous pre-execution JS digest',offline_identity_limit='1002 method/log and later checkpoint support coverage; no invented contemporaneous all-product hash receipt'))

f02=load(ENG/'F02-ADMIN-delegation-SET-combination-PASS.json');f=f02['facts']
check('F02_root62',f02['root']==62)
check('F02_before_after_whole_role_privilege_graph_equal',f['before']==f['after'])
check('F02_actual_subject_grant',f['actual_after_GRANT']=={'actor':'task120_flow_snapshot','can_set_app':True})
check('F02_actual_SET_app_DELETE',f['actual_SET_ROLE']=={'actor':'retrolume_data_app','delete':True})
check('F02_initial_no_DELETE_or_SET',f['before_capability']=={'delete':False,'can_set_app':False})
check('F02_product_denial_before_amplification',f['strict_check_before_delegation']=='data_role_capability_mismatch')
g=f['observed_graph'];ids={r['rolname']:r['oid'] for r in g['roles']}
names={r['oid']:r['rolname'] for r in g['roles']}
relevant=[]
for e in g['members']:
    if e['member'] in (ids['task120_flow_snapshot'],ids['retrolume_task120_audit07_bridge1']): relevant.append(dict(e,member_name=names[e['member']],role_name=names[e['roleid']]))
offline=[]
for i in (1000,1001,1002):
    rec=load(ENG/f'command-{i}.receipt.json');log=(ENG/f'command-{i}.log').read_text(encoding='utf-8-sig')
    offline.append(dict(command=i,receipt=rec,passed_cases=[s for s in log.splitlines() if s.startswith('test_') and s.endswith('... ok')]))
check('offline_final_five_methods_pass',len(offline[-1]['passed_cases'])==5 and offline[-1]['receipt']['exit_code']==0)
save('F02-record-comparison.json',dict(endpoint=f['endpoint'],subject=f['subject'],initial=f['before_capability'],actual_subject_grant=f['actual_after_GRANT'],actual_set=f['actual_SET_ROLE'],graph_roles_before=len(f['before']['roles']),graph_roles_during=len(g['roles']),graph_members_before=len(f['before']['members']),graph_members_during=len(g['members']),relevant_edges=relevant,offline=offline,claims_limited_to_saved_transaction_and_reviewed_algorithm=True))

pending=load(ENG/'F03-memory-failure-POST-and-three-GETs-PASS.json');reopen=load(ENG/'F03-memory-API-reopen-pending-PASS.json');done=load(ENG/'F03-memory-explicit-UI-retry-done-PASS.json');final=load(ENG/'F03-memory-final-reopen-confirmed-PASS.json');ui=load(ENG/'F03-memory-browser-root-64.json')
mid=pending['facts']['POST']['memory_id'];key=pending['facts']['POST']['business_key'];manifest=pending['facts']['POST']['manifest_sha256']
views=[]
for label,d,state in [('failure',pending,'pending'),('api_reopen',reopen,'pending'),('explicit_retry',done,'done'),('final',final,'done')]:
    v=d['facts']['views'];rec=v['receipt'];detail=v['detail_without_body'];listing=v['listed_item'];db=v['actual_DB_fact']
    check('F03_same_identity:'+label,rec['memory_id']==detail['memory_id']==listing['memory_id']==mid and rec['business_key']==key and rec['manifest_sha256']==manifest)
    check('F03_combined_views:'+label,rec['purge_state_now']==detail['purge_state']==listing['purge_state']==state)
    check('F03_DB_COMMIT_never_rewritten:'+label,db==dict(state='revoked',revision=2,purge_state='done',body_rows=0))
    check('F03_GET_no_writable_authority:'+label,v['QAuthority_initializations_during_three_GETs']==0)
    views.append(dict(label=label,root=d['root'],views=v,closed=d['facts'].get('closed')))
check('F03_same_control_replay',reopen['facts']['same_control']==final['facts']['same_control'])
check('F03_before_after_operations_007_prepared_financials',final['facts']['before']==final['facts']['after'])
posts=[(i,x) for i,x in enumerate(ui['requests']) if x['method']=='POST']
check('browser_exact_one_purge_POST',len(posts)==1 and posts[0][1]['path']=='/api/memories/commands' and ui['explicit_retry_receipt']['action']=='purge')
check('browser_four_steps',[(x['state'],x['posts']) for x in ui['steps']]==[('pending',0),('pending',0),('done',1),('done',1)])
check('browser_original_manifest_revision',ui['explicit_retry_receipt']['memory_id']==mid and ui['explicit_retry_receipt']['manifest_sha256']==manifest and ui['explicit_retry_receipt']['revocation_key']==key and ui['explicit_retry_receipt']['revision_after']==2)
asset_checks=[dict(x,actual=current('frontend/dist'+x['path']),match=current('frontend/dist'+x['path'])==x['sha256']) for x in ui['assets']]
check('browser_loaded_formal_asset_bytes',len(asset_checks)==6 and all(x['match'] for x in asset_checks))
check('browser_no_response_errors',ui['errors']==[])
delete=load(ENG/'F03-new-exact-delete-manifest.json');new=delete['new_files'][0]
check('one_exact_Q_body_delete_cumulative_seven',len(delete['new_files'])==1 and delete['prior_deleted_count']==6 and delete['cumulative_delete_files']==7 and delete['maximum']==16 and new['memory_id']==mid)
check('delete_path_is_only_registered_prepared',Path(new['path']).is_relative_to(Path(delete['root'])) and Path(new['path']).name=='q-prepared-'+new['prepared_id']+'.bin')
adoption=load(ENG/'sample-method-user-adoption.json')
check('explicit_narrow_sample_adoption',adoption['explicitly_approved'] and adoption['user_answer']=='允许这个最小清理夹具调整')
save('F03-record-comparison.json',dict(memory_id=mid,revoke_key=key,manifest_sha256=manifest,views=views,browser_steps=ui['steps'],browser_POSTs=posts,assets=asset_checks,delete_manifest=delete,adoption=adoption,witness_before=final['facts']['before'],witness_after=final['facts']['after'],proof_scope='non-authorizing cleanup dependency fixture plus normal HTTP cleanup/projection/reopen/retry; not normal request assembly, provenance qualification, external use, or a new full worker negative'))

# Preserve old roots/failures/events as exact saved history; compare final sole ledger.
b=load(EX/'budget.json');before=load(ENG/'budget.json.before.bytes');eventraw=(EX/'events.jsonl').read_bytes();eventold=(ENG/'events.jsonl.before.bytes').read_bytes()
check('old60_roots_exact',b['roots'][:len(before['roots'])]==before['roots'])
check('old141_failures_exact',b['failures'][:len(before['failures'])]==before['failures'])
check('old_events_exact_byte_prefix',eventraw.startswith(eventold))
events=[json.loads(x) for x in eventraw[len(eventold):].decode('utf-8-sig').splitlines() if x]
check('sole_count_caps',all(b['counts'][k]<=v for k,v in b['caps'].items()))
check('root_and_PG_caps_exhausted',b['counts']['roots']==b['caps']['roots']==64 and b['counts']['pg_starts']==b['caps']['pg_starts']==64)
check('no_active_runtime',b['active_root'] is None and b['active_command'] is None)
check('latest_failure149',len(b['failures'])==149 and b['failures'][-1]['case']=='repair08-completed-postsave-readback-initial')
check('save_snapshot148_then149',load(ENG/'budget-summary-completed.json')['failure_records']==148 and load(ENG/'post-save-verification-completed.json')['failures']==149)
check('wall_and_holding_bounded',b['command_wall_conservative_upper_seconds']<=72000 and b['runtime_holding_union_seconds']<=21600)
old_reserves={k:v for k,v in before.items() if ('reserved' in k or 'uncertainty' in k or 'unwrapped' in k or k.endswith('_timing')) and not k.startswith('targeted_repair08')}
check('old_reserves_and_timing_preserved',all(b[k]==v for k,v in old_reserves.items()))
newroots=[]
for root in b['roots'][60:]:
    stop=root.get('result',{});newroots.append(dict(id=root['id'],identity=root['identity'],start_utc=root['start_utc'],owner=root['owner'],exit_code=stop.get('exit_code'),stop_utc=stop.get('utc'),wall=stop.get('wall_seconds'),holding=stop.get('runtime_holding_union_seconds')))
hold_delta=b['runtime_holding_union_seconds']-before['runtime_holding_union_seconds']
check('new_holding_matches_four_saved_roots',abs(hold_delta-sum(x['holding'] or 0 for x in newroots))<1e-6)
api_groups=collections.defaultdict(list)
for e in events:
    if e['kind']=='actual_API_PG_connection':api_groups[e['pid']].append(e)
check('separate_API_actor_processes',len(api_groups)==2)
memory_gates=[e for e in events if e['kind']=='memory_gate']
check('unchanged_512MiB_launch_threshold',all(e['minimum_bytes']==536870912 for e in memory_gates))
stop=load(ENG/'final-stop-proof-completed.json');pids=stop['registered_processes'];jobs=stop['registered_jobs']
check('stop28process8job_no_unresolved',len(pids)==28 and len(jobs)==8 and stop['unresolved']==[])
for x in pids:
    o=x['observation'];good=o['state']=='exited' or (o['state']=='running' and int(o['birth'])!=int(x['registered_birth']))
    if o['state']=='unknown':good=bool(x['proof']) and 'Job membership' in x['proof']
    check('stop_exact_identity:'+str(x['pid']),good,x)
check('stop_all_jobs_absent_or_empty',all(not x.get('unknown') and (x.get('absent') or x.get('active_processes')==0) for x in jobs))
check('saved_stop_ports_no_listeners',all(x['listening'] is False for x in stop['ports'].values()))
check('saved_exact_source_and_target_stopped',stop['source_container']['state']['Running'] is False and stop['source_container']['state']['Pid']==0 and stop['restore_target']['running'] is False and stop['restore_target']['Pid']==0)
for i in (1005,1006):
    rec=load(ENG/f'command-{i}.receipt.json');check('metadata_self_exit:'+str(i),rec['exit_code']==0 and rec['tree_empty'])
after_stop=[e for e in events if e.get('utc','')>stop['utc'] and e['kind'] in ('pg_started','root_entered','root_child_started','actual_API_PG_connection','finite_stage_started')]
check('no_saved_business_restart_after_stop',not after_stop)
for e in stop['old079_unknown20_retained_with_review01_accepted_alternatives']:check('old_stop_alternative_identity:'+Path(e['path']).name,current(e['path'])==e['sha256'])
packages=load(ENG/'old-packages-preserved-completed.json')['ten_prior_ZIPs_including_blocked08_snapshot']
check('ten_old_archive_hashes_unchanged',len(packages)==10 and all(current(x['path'])==x['sha256'] for x in packages))
save('control-record-comparison.json',dict(counts=b['counts'],caps=b['caps'],new_delta={k:b['counts'][k]-before['counts'][k] for k in b['counts']},old_root_count=len(before['roots']),old_failure_count=len(before['failures']),failure_count=len(b['failures']),new_failures=b['failures'][141:],old_events_bytes=len(eventold),appended_event_count=len(events),new_roots=newroots,API_actor_processes={str(k):dict(count=len(v),first=v[0],last=v[-1]) for k,v in api_groups.items()},memory_gates=memory_gates,wall_upper=b['command_wall_conservative_upper_seconds'],holding=b['runtime_holding_union_seconds'],holding_delta=hold_delta,stop=stop,post_stop_runtime_events=after_stop,old_reserve_keys=list(old_reserves),ten_old_archives=packages,limits='Saved stop-time facts only; no current host/container/port probes; historical execution-control failure retained'))
save('record-checks.json',dict(checks=checks,count=len(checks),failures=[x for x in checks if not x['ok']]))
print(json.dumps(dict(check_count=len(checks),failed=[x for x in checks if not x['ok']],asrun_products=[(r['path'],r['product_count']) for r in asrun],API_pids=list(api_groups),stop_observation_counts=dict(collections.Counter(x['observation']['state'] for x in pids))),ensure_ascii=False))
