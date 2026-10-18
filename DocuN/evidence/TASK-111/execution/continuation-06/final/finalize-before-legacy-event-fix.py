"""五项原件、最终源和精确已停止资源对账；无新增业务资源。"""
import difflib,hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
from .control import ROOT,CONTINUE_ROOT,CONTINUATION,EVIDENCE,CAPS,registry_root,atomic,batch,phase,read_state,locked,source_snapshot
from .resources import DOCKER,shell_env
from app.preview.process import birth,GlobalOwner
from app.preview.host_job import valid_job_end,job_name
from app.preview.description import digest

def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def ref(path):return dict(path=str(Path(path).resolve()),sha256=sha(path),bytes=Path(path).stat().st_size)
def object_value(value):return json.loads(value) if isinstance(value,str) else value

def main():
    out=CONTINUE_ROOT/'final';out.mkdir(exist_ok=True);phase('cleanup')
    assert read_state()['active_batch'] is None
    with batch('cleanup','C06 terminal evidence and exact physical metadata'):
        rows=load(CONTINUE_ROOT/'root-17/step-04-final_data/sessions-final.json');assert len(rows)==5 and all(x['state']=='stopped' for x in rows)
        old=load(CONTINUE_ROOT/'root-17/step-04-final_data/old-unknown-kept.json');assert old['state']=='cleanup_unconfirmed' and old['reserve_seconds']==60 and old['elapsed_seconds'] is None
        methods=load(CONTINUE_ROOT/'root-17/step-01-tail/client-methods-accepted.json');assert set(methods)=={'real_hidden','READY_unload','READY_active_refresh'}
        prior=load(EVIDENCE/'continuation-05/final/exact-resources-final.json');targets={x['id']:x for x in prior['objects']};owners=[];index=[]
        for row in rows:
            pid=row['preview_id'];folder=registry_root()/pid;reg=load(folder/'registry.json');kernel=load(folder/'kernel-premises.json');confirmation=object_value(row['confirmation_receipt'])
            recovered=(folder/'recovery-proof.json').exists();proofpath=folder/('recovery-proof.json' if recovered else 'supervisor-result.json')
            actual=load(proofpath);actual=actual if recovered else actual['proof'];assert digest(confirmation)==digest(actual)
            assert confirmation['tree_confirmation']=='private_pid_init_terminated' and confirmation['attach_eof_confirmed'] is True and confirmation['owned_reaper_ended'] is True
            assert confirmation['cid']==reg['cid'] and confirmation['image_id']==reg['intent']['image_id']==row['image_id'] and confirmation['nonce']==reg['intent']['nonce']
            assert confirmation['kernel_premises_sha256']==digest(kernel) and confirmation['wait']['code']==0 and reg['complete'] is True
            events=[json.loads(line) for line in confirmation['events']['stdout'].splitlines() if line.strip()];assert any(x['Actor']['ID']==reg['cid'] and x['Action']=='die' for x in events)
            jobs={}
            for role,key in [('REAP','reaper_windows_job'),('SUP','supervisor_cli_windows_job')]:
                proof=confirmation[key];assert valid_job_end(proof,job_name(pid,reg['intent']['nonce'],role),reg['job_premises'][role]);jobs[role]=proof
                if recovered:assert proof['termination_evidence']=='job_destroyed' and proof['open_error']==2 and 'ActiveProcesses' not in proof and proof['observer_terminated'] is False
            for role,data in [('parent',reg['parent']),('attach',dict(pid=reg['attach_pid'],birth=reg['attach_birth'])),('reaper',reg['reaper_owner']),('reaper_launcher',reg['reaper_launcher'])]:
                now=birth(data['pid']);assert now['state']=='exited' or now['state']=='running' and now['birth']!=data['birth'];owners.append(dict(preview_id=pid,role=role,instance=data,current=now))
            targets[reg['cid']]=dict(id=reg['cid'],name='/'+reg['intent']['name'],image=reg['intent']['image_id'])
            index.append(dict(preview_id=pid,activity_id=row['activity_id'],name=reg['intent']['name'],cid=reg['cid'],nonce=reg['intent']['nonce'],image_id=row['image_id'],reserve_seconds=row['reserve_seconds'],elapsed_seconds=row['elapsed_seconds'],state=row['state'],deadline_at=row['deadline_at'],deadline_ns=reg['deadline_ns'],confirmation_sha256=digest(confirmation),source_proof=ref(proofpath),kernel=ref(folder/'kernel-premises.json'),jobs=jobs,persistent_confirmation_matches=True))
        assert len(targets)==39
        fmt='{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"restart_count":{{json .RestartCount}}}'
        result=subprocess.run([DOCKER,'inspect','--format',fmt,*targets],capture_output=True,timeout=15,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        (out/'exact-inspect.stdout.bin').write_bytes(result.stdout);(out/'exact-inspect.stderr.bin').write_bytes(result.stderr);assert result.returncode==0
        objects=[json.loads(line) for line in result.stdout.splitlines()];assert len(objects)==len(targets)
        for got in objects:
            expected=targets[got['id']];assert got['name']==expected['name'] and got['image']==expected['image'] and got['running'] is False and got['pid']==0 and got['restart_count']==0
        for path in CONTINUE_ROOT.rglob('*.json'):
            if path.name not in ('actual-step-owner.json','actor-owner.json','api-actual-bound.json','browser-host-owner.json','owner.json','guardian-ready.json'):continue
            data=load(path);pid=data.get('node_pid') or data.get('pid');expected=data.get('birth');expected=expected.get('birth') if isinstance(expected,dict) else expected
            if not pid:continue
            now=birth(pid);assert now['state']=='exited' or expected is not None and now['state']=='running' and now['birth']!=expected
            owners.append(dict(path=str(path.relative_to(ROOT)),pid=pid,birth=expected,current=now))
        owner=GlobalOwner('Global\\RetroLumePreviewV2Task111')
        try:assert owner.acquire()=='acquired';identity=owner.identity()
        finally:owner.close()
        port_command="$taskRows = @(Get-NetTCPConnection -State Listen -LocalPort 18111,55451 -ErrorAction SilentlyContinue); ConvertTo-Json -InputObject $taskRows -Compress; exit 0"
        port_result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',port_command],capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
        (out/'ports-final.stdout.bin').write_bytes(port_result.stdout);(out/'ports-final.stderr.bin').write_bytes(port_result.stderr);assert port_result.returncode==0
        ports=json.loads(port_result.stdout);assert ports==[];atomic(out/'ports-final.json',dict(command=port_command,ports=ports,confirmed=True))
        pointer=load(registry_root()/'current.json');assert pointer['complete'] is True and pointer['preview_id']==rows[-1]['preview_id']
        atomic(out/'exact-resources-final.json',dict(at_utc=datetime.now(timezone.utc).isoformat(),objects=objects,owners=owners,global_exclusive=identity,same_control_root=str(registry_root()),current_pointer=pointer,new_rows=5,new_created_containers=5,old_unknown_preserved=old,browser_close=load(CONTINUE_ROOT/'root-17/step-01-tail/browser-host-final.json'),PG_cleanup=load(CONTINUE_ROOT/'integrated-holder/pg-cleanup.json'),no_new_resource_start=True))
        atomic(out/'session-proof-index.json',index)
        refresh=methods['READY_active_refresh']['row'];refreshfolder=Path(methods['READY_active_refresh']['path']).parent;effects=load(refreshfolder/'tail-effects.json')
        pre=[r for r in effects['requests'] if r['phase']=='READY_active_refresh' and r['source']=='ownerless_oracle'][0]['at_ms']/1000
        first=refresh['requests'][0]['at_ms']/1000;end=[r for r in effects['records'] if r['label']=='external_cleanup_after_validation'][-1]['at_ms']/1000
        raw_events=[json.loads(line) for line in (EVIDENCE/'events.jsonl').read_text(encoding='utf-8').splitlines()]
        api=load(CONTINUE_ROOT/'root-17/step-01-tail/api-actual-bound.json')['pid']
        http=[r for r in raw_events if r['pid']==api and r['kind']=='reserved' and r['data'].get('category')=='HTTP_total']
        roots=[r for r in http if r['data']['detail']['path']=='/' and pre<datetime.fromisoformat(r['at_utc']).timestamp()<first];assert len(roots)==1
        reload_event=roots[0];window=[r for r in http if r['event']>=reload_event['event'] and datetime.fromisoformat(r['at_utc']).timestamp()<end]
        assert window and all(r['data']['detail']['method']=='GET' for r in window) and all(not r['owner_present'] for r in refresh['requests'])
        refresh_supervisor=load(registry_root()/refresh['preview_id']/'supervisor-result.json');assert refresh_supervisor['error_code']=='control_lost' and refresh_supervisor['confirmed'] is True
        atomic(out/'active-refresh-complete-HTTP.json',dict(source_events=ref(EVIDENCE/'events.jsonl'),api_instance=api,actual_reload_request=reload_event,validation_end_ms=end*1000,all_routes_http=window,preview_ownerless_requests=refresh['requests'],same_deadline=refresh['before']['deadline_at']==refresh['after']['deadline_at'],same_starts=refresh['before']['starts_used']==refresh['after']['starts_used'],stop_error_code=refresh_supervisor['error_code'],owner_after_reload=refresh['owner_after_reload'],external_cleanup_excluded=True))
        faults=[]
        for step,name in [(2,'control_path_lost'),(3,'hard_deadline')]:
            folder=CONTINUE_ROOT/'root-17'/('step-'+str(step).zfill(2)+'-'+name)/name
            scenario=load(folder/'scenario-result.json');assert scenario['status']=='PASS_REAL_REMAINING_SCENARIO'
            recovery=load(folder/'same-root-persistent-recovery.json');assert recovery['root']==str(registry_root()) and recovery['after']['elapsed_seconds']==recovery['before']['reserve_seconds']==60 and recovery['after']['reserved_seconds']==0
            passive=load(folder/'natural-pipe-observation.json');assert len(passive['pipes'])==2 and all(r['actual_eof'] for r in passive['pipes']) and passive['extra_job_handles_held'] is False and passive['observer_terminated'] is False
            trigger=load(folder/'trigger.json');runtime=Path(trigger['runtime_folder']);assert runtime.parent==registry_root().resolve()
            item=dict(scenario=scenario,pretrigger=ref(folder/'pretrigger.json'),trigger=ref(folder/'trigger.json'),before_external_cleanup=ref(folder/'before_external_cleanup.json'),natural_EOF=ref(folder/'natural-pipe-observation.json'),same_root_recovery=ref(folder/'same-root-persistent-recovery.json'),external_kill_used=recovery['external_kill_used'],actor_source=ref(folder/'source-identity.json'))
            if name=='hard_deadline':
                freeze=load(folder/'hard-deadline-freeze.json');reaper=load(runtime/'reaper-receipt.json');bound=load(runtime/'reaper-bound.json')
                deadline=trigger['deadline_ns'];assert freeze['entries'][0]['entered_ns']<deadline and freeze['entries'][0]['released_ns']>=deadline+10**9
                assert bound['deadline_ns']==deadline and reaper['reason']=='deadline' and reaper['end_ns']<=deadline and recovery['external_kill_used'] is False
                finish=datetime.fromisoformat(reaper['after']['state']['FinishedAt'].replace('Z','+00:00'));utc_deadline=datetime.fromisoformat(recovery['before']['deadline_at']);assert finish<=utc_deadline
                item['original_deadline']=dict(monotonic_ns=deadline,utc=utc_deadline.isoformat(),freeze_trigger_ns=freeze['trigger_ns'],freeze_entered_ns=freeze['entries'][0]['entered_ns'],freeze_released_ns=freeze['entries'][0]['released_ns'],reaper_started_ns=reaper['start_ns'],reaper_ended_ns=reaper['end_ns'],FinishedAt=finish.isoformat(),finished_before_D_seconds=(utc_deadline-finish).total_seconds(),reaper_receipt=ref(runtime/'reaper-receipt.json'),freeze_receipt=ref(folder/'hard-deadline-freeze.json'))
            faults.append(item)
        atomic(out/'five-methods-final.json',dict(client=methods,stops=faults,inherited=load(CONTINUE_ROOT/'inherited-evidence.json'),status='PASS_ALL_FIVE_CURRENT_SCOPED_METHODS',new_model_calls=0,new_OneCall=0))
        changes=[];received=load(ROOT/'DocuN/evidence/TASK-111/orchestration-receipt-06/received.json')
        for old_source in received['sources']:
            path=ROOT/old_source['path'];current=sha(path)
            if current==old_source['sha256']:continue
            prefile=CONTINUE_ROOT/'source-pre'/old_source['path'];assert prefile.exists() and sha(prefile)==old_source['sha256']
            postfile=CONTINUE_ROOT/'source-post'/old_source['path'];postfile.parent.mkdir(parents=True,exist_ok=True);postfile.write_bytes(path.read_bytes())
            diff=CONTINUE_ROOT/'source-diff'/(old_source['path'].replace('/','__')+'.diff');diff.parent.mkdir(exist_ok=True)
            diff.write_text(''.join(difflib.unified_diff(prefile.read_text(encoding='utf-8').splitlines(True),postfile.read_text(encoding='utf-8').splitlines(True),fromfile='pre/'+old_source['path'],tofile='post/'+old_source['path'])),encoding='utf-8')
            changes.append(dict(path=old_source['path'],pre=ref(prefile),post=ref(postfile),diff=ref(diff),product=False))
        assert {x['path'] for x in changes}=={'backend/tests/fixtures/task111/control.py','backend/tests/fixtures/task111/core.py','backend/tests/fixtures/task111/c01_seeds.py','backend/tests/fixtures/task111/c05_fault_actor.py'}
        for path in list((ROOT/'backend/tests/fixtures/task111').glob('c06*.py'))+list((ROOT/'frontend/tests/task111').glob('c06*.cjs')):
            post=CONTINUE_ROOT/'source-post'/path.relative_to(ROOT);post.parent.mkdir(parents=True,exist_ok=True);post.write_bytes(path.read_bytes());changes.append(dict(path=path.relative_to(ROOT).as_posix(),pre=None,new_file=True,post=ref(post),product=False))
        atomic(out/'source-changes.json',changes)
        unchanged=[dict(path=x['path'],sha256=x['sha256'],match=sha(ROOT/x['path'])==x['sha256']) for x in received['sources'] if x['path'].startswith(('backend/app/','frontend/src/','backend/migrations/','deploy/'))]
        assert all(x['match'] for x in unchanged);atomic(out/'accepted-product-unchanged.json',unchanged);source_snapshot(out)
        as_run=dict(client_attempt=ref(CONTINUE_ROOT/'root-17/step-01-tail/browser-attempt-3.json'),client_exact_source_sha256=load(CONTINUE_ROOT/'root-17/step-01-tail/browser-attempt-3.json')['source_sha256'],control_path_source=ref(CONTINUE_ROOT/'root-17/step-02-control_path_lost/control_path_lost/source-identity.json'),hard_deadline_source=ref(CONTINUE_ROOT/'root-17/step-03-hard_deadline/hard_deadline/source-identity.json'),product_sources_unchanged=True)
        assert as_run['client_exact_source_sha256']==sha(ROOT/'frontend/tests/task111/c06_tail.cjs');atomic(out/'as-run-bindings.json',as_run)
    phase('implementation_offline')
    with locked():
        b=read_state();atomic(out/'budget-before-legacy-label-alignment.json',b)
        # 旧别名无执行消费者；原值明确移作C05历史，当前标签与实际C06选择器对齐。
        b['prior_C05_continuation_permit']=b.get('continuation_permit');b['prior_C05_continuation_caps']=b.get('continuation_caps')
        b['continuation_permit']=CONTINUATION;b['continuation_caps']=load(CONTINUE_ROOT/'timing.json')['hard_count_caps'];atomic(EVIDENCE/'budget.json',b)
    t=load(CONTINUE_ROOT/'timing.json');delta={k:b['counts'][k]-load(ROOT/'DocuN/evidence/TASK-111/orchestration-receipt-06/continuation-budget.json')['prior_used'][k] for k in b['counts']}
    assert b['active_batch'] is None and b['counts']['real_batches']==17 and b['time_seconds']['real']-t['prior_time_seconds']['real']<=1800 and b['time_seconds']['real']<=16200
    assert all(CAPS[k] is None or b['counts'][k]<=CAPS[k] for k in b['counts'] if k in CAPS)
    atomic(out/'execution-receipt.json',dict(TASK='TASK-111',R='R-105',permit=CONTINUATION,counts=b['counts'],new_counts=delta,time_seconds=b['time_seconds'],new_real_seconds=b['time_seconds']['real']-t['prior_time_seconds']['real'],lease_accounting=load(CONTINUE_ROOT/'lease-accounting.json'),active_batch=b['active_batch'],only_new_root=17,root18_unused=True,preview_names_remaining=load(CONTINUE_ROOT/'preview-name-plan.json'),new_model_or_OneCall=0,old_unknown_R60_kept=True,ended_on_five_actual_passes=True,legacy_labels_aligned_without_count_time_rewrite=True))
    atomic(out/'delivery-boundaries.json',dict(implementation='STABLE_SCOPED_CANDIDATE_UNCHANGED_PRODUCT',evidence='PASS_ALL_FIVE_REMAINING_METHODS_WITH_INHERITED_ACCEPTED_SCOPE',execution_control='PASS_C06_ROOT_AND_TOTAL_DEADLINES_RESULT_DRIVEN',stable_full_candidate=True,full_audit_ready=True,G11_signed=False,independent_audit_pending=True,old_unknown_R60_kept=True,pending_engineering_methods=[],no_new_product_interface_or_image_or_role_change=True))
    print(json.dumps(dict(status='PASS_C06_FINAL_EVIDENCE_AND_EXACT_RESOURCES',objects=len(objects),new_rows=len(rows),new_real_seconds=b['time_seconds']['real']-t['prior_time_seconds']['real'],counts=b['counts'])))

if __name__=='__main__':main()
