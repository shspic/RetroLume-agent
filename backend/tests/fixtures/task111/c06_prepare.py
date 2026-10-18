"""本次改动的一批离线检查及只读精确资源预检；不启动真实资源。"""
import ast,hashlib,json,os,subprocess,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
from .control import ROOT,CONTINUATION,CONTINUE_ROOT,CAPS,EVIDENCE,registry_root,synthetic_root,atomic,batch,phase,read_state,source_snapshot
from .resources import DOCKER,shell_env
from .c06_coordinator import command_decision
from app.preview.process import birth,GlobalOwner

def main():
    out=CONTINUE_ROOT/'prepared-offline';out.mkdir(exist_ok=True);phase('implementation_offline')
    with batch('offline','C06 changed entries, deadlines and exact resource preflight',maximum=(read_state()['business_deadline_ns']-time.monotonic_ns())/1e9):
        assert CONTINUATION=='TASK-111-G11-C06-20261011'
        t=json.loads((CONTINUE_ROOT/'timing.json').read_text(encoding='utf-8'));b=read_state()
        assert b['deadline_ns']==t['deadline_ns'] and b['business_deadline_ns']==t['business_deadline_ns'] and b['active_batch']['kind']=='offline'
        assert t['deadline_ns']-t['accepted_ns']==10800*10**9 and t['deadline_ns']-t['business_deadline_ns']==600*10**9
        assert (CAPS['real_batches'],CAPS['preview_creates'],CAPS['preview_starts'],CAPS['API_listener_starts'],CAPS['main_browser_starts'],CAPS['PG_container_starts'])==(18,47,43,12,11,14)
        assert registry_root().resolve()==(EVIDENCE/'continuation-04/synthetic/control').resolve() and synthetic_root()==CONTINUE_ROOT/'synthetic'
        assert json.loads((CONTINUE_ROOT/'preview-name-plan.json').read_text(encoding='utf-8'))==[str(n) for n in range(50,58)]
        changed=['control.py','core.py','c01_seeds.py','c06_coordinator.py','c06_step.py','c06_prepare.py']
        for name in changed:
            p=ROOT/'backend/tests/fixtures/task111'/name;ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
        for name in ('c06_tail.cjs','c06_browser_host.cjs'):
            p=ROOT/'frontend/tests/task111'/name;r=subprocess.run(['node','--check',str(p)],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
            assert r.returncode==0;r.stdout and (out/(name+'.stdout')).write_bytes(r.stdout);r.stderr and (out/(name+'.stderr')).write_bytes(r.stderr)
        decisions=[];base=dict(permit=CONTINUATION,expected_root=17,action='stop',command_id='test-prequeued',submitted_ns=1,observed_step=0)
        decisions.append(command_decision(base,17,None,set()));assert decisions[-1]=='reject_prequeued_control'
        last=dict(step=3,completed_ns=10)
        decisions.append(command_decision({**base,'command_id':'stale','action':'next_root','expected_root':16,'submitted_ns':11,'observed_step':3},17,last,set()));assert decisions[-1]=='ignore_stale_root'
        decisions.append(command_decision({**base,'command_id':'current','submitted_ns':11,'observed_step':3},17,last,set()));assert decisions[-1]=='stop'
        seen={'duplicate'};decisions.append(command_decision({**base,'command_id':'duplicate'},17,last,seen));assert decisions[-1]=='ignore_identity'
        text=(ROOT/'backend/tests/fixtures/task111/c06_coordinator.py').read_text(encoding='utf-8')
        assert 'min(900' not in text and 'min(650' not in text and 'min(600' not in text
        tail=(ROOT/'frontend/tests/task111/c06_tail.cjs').read_text(encoding='utf-8')
        assert 'readdirSync' not in tail and 'explicit_inherited_C05_combo_no_replay' in tail and "{enabled:false}" in tail
        from .c05_reaper_unreachable import main as wrapper
        assert 'registry_root().resolve()' in (ROOT/'backend/tests/fixtures/task111/c05_reaper_unreachable.py').read_text(encoding='utf-8')
        prior=json.loads((EVIDENCE/'continuation-05/final/exact-resources-final.json').read_text(encoding='utf-8'))
        fmt='{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"restart_count":{{json .RestartCount}}}'
        r=subprocess.run([DOCKER,'inspect','--format',fmt,*[x['id'] for x in prior['objects']]],capture_output=True,timeout=15,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        assert r.returncode==0;objects=[json.loads(line) for line in r.stdout.splitlines()];assert len(objects)==34
        for got,expected in zip(objects,prior['objects']):assert got==expected
        owners=[]
        for row in prior['owners']:
            pid=row.get('pid') or row.get('instance',{}).get('pid');expected=row.get('birth') or row.get('instance',{}).get('birth')
            if isinstance(expected,dict):expected=expected['birth']
            now=birth(pid);later_reuse=False
            if expected is None and row['current']['state']=='exited' and now['state']=='running':
                later_reuse=datetime(1601,1,1,tzinfo=timezone.utc)+timedelta(microseconds=now['birth']/10)>datetime.fromisoformat(prior['at_utc'])
            assert now['state']=='exited' or expected is not None and now['state']=='running' and now['birth']!=expected or later_reuse
            owners.append(dict(pid=pid,expected_birth=expected,current=now,prior_confirmed_exit_followed_by_new_birth=later_reuse,prior_observed_at=prior['at_utc']))
        owner=GlobalOwner('Global\\RetroLumePreviewV2Task111')
        try:assert owner.acquire()=='acquired';identity=owner.identity()
        finally:owner.close()
        atomic(out/'resource-preflight.json',dict(objects=objects,owners=owners,global_exclusive=identity,no_real_start=True))
        source_snapshot(out)
        atomic(out/'offline-result.json',dict(status='PASS_CHANGED_C06_ENTRIES_ONLY',decisions=decisions,selector=CONTINUATION,registry_root=str(registry_root()),per_root_seconds=1800,new_real_seconds=1800,cumulative_real_seconds=16200,deadline_ns=t['deadline_ns'],business_deadline_ns=t['business_deadline_ns'],fresh_seeds_no_model_or_OneCall=True,only_UI_methods=['real_hidden','READY_unload','READY_active_refresh'],only_stop_methods=['control_path_lost','hard_deadline']))
    print(json.dumps(dict(status='PASS_C06_OFFLINE_PREFLIGHT',objects=len(objects),owners=len(owners),counts=read_state()['counts'])))

if __name__=='__main__':main()
