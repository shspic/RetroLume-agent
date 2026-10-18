"""C06仅两个新根；真实结果驱动，根及总余时是唯一整组时限。"""
import json,os,subprocess,sys,time
from .control import ROOT,CONTINUE_ROOT,CONTINUATION,PERMIT,EVIDENCE,atomic,batch,phase,read_state,source_snapshot,CAPS,locked,event
from .resources import pg_resume,shell_env
from .c03_resources import guardian,cleanup
from app.preview.process import birth,terminate_owned

def command_decision(command,root,last,seen):
    identity=command.get('command_id')
    if not identity or identity in seen:return 'ignore_identity'
    seen.add(identity)
    if command.get('permit')!=CONTINUATION:return 'ignore_permit'
    if command.get('expected_root')!=root:return 'ignore_stale_root'
    action=command.get('action')
    if action in ('stop','next_root'):
        if not last or command.get('observed_step')!=last['step'] or command.get('submitted_ns',0)<=last['completed_ns']:return 'reject_prequeued_control'
        return action
    if action not in ('tail','control_path_lost','hard_deadline','final_data'):return 'reject_action'
    if action=='tail' and (not command.get('methods') or not set(command['methods'])<={'real_hidden','READY_unload','READY_active_refresh'}):return 'reject_methods'
    return action

def main():
    assert CONTINUATION=='TASK-111-G11-C06-20261011' and os.environ.get('RETROLUME_TASK111_FIXTURE')==PERMIT
    prior=read_state();timing=json.loads((CONTINUE_ROOT/'timing.json').read_text(encoding='utf-8'))
    remaining=min(timing['new_real_limit_seconds']-(prior['time_seconds']['real']-timing['prior_time_seconds']['real']),timing['cumulative_real_limit_seconds']-prior['time_seconds']['real'])
    deadline=min(prior['business_deadline_ns'],time.monotonic_ns()+int((remaining-15)*1e9))
    resource=None;guard=None;stop=False;last=None;segments=[];last_end=None;phase('real')
    decisions=[json.loads(p.read_text(encoding='utf-8')) for p in CONTINUE_ROOT.glob('command-decision-*.json')]
    step=max((d['step'] for d in decisions),default=0);seen={d['command']['command_id'] for d in decisions}
    lease=CONTINUE_ROOT/('integrated-holder' if prior['counts']['real_batches']==16 else 'integrated-holder-2');lease.mkdir(exist_ok=False);atomic(lease/'owner.json',dict(pid=os.getpid(),birth=birth(os.getpid()),deadline_ns=deadline))
    try:
        for n in range(prior['counts']['real_batches']+1,CAPS['real_batches']+1):
            if stop or time.monotonic_ns()>=deadline-20*10**9:break
            root=CONTINUE_ROOT/('root-'+str(n));root.mkdir()
            if last_end and resource:
                gap=(time.monotonic_ns()-last_end)/1e9
                with locked():
                    b=read_state();b['time_seconds']['real']+=gap;atomic(EVIDENCE/'budget.json',b)
                segments.append(dict(kind='PG_root_gap',seconds=gap))
            with batch('real','C06 five remaining methods',maximum=min(1800,(deadline-time.monotonic_ns())/1e9)) as active:
                source_snapshot(root);atomic(CONTINUE_ROOT/'coordinator-ready.json',dict(pid=os.getpid(),birth=birth(os.getpid()),root=n,root_deadline_ns=active['deadline_ns'],hold_deadline_ns=deadline))
                while time.monotonic_ns()<min(active['deadline_ns'],deadline)-15*10**9:
                    path=CONTINUE_ROOT/('command-'+str(step+1).zfill(2)+'.json')
                    if not path.exists():time.sleep(.05);continue
                    command=json.loads(path.read_text(encoding='utf-8'));step+=1
                    action=command_decision(command,n,last,seen)
                    atomic(CONTINUE_ROOT/('command-decision-'+str(step).zfill(2)+'.json'),dict(step=step,decision=action,root=n,command=command))
                    if action=='stop':stop=True;break
                    if action=='next_root':break
                    if action.startswith(('ignore_','reject_')):continue
                    out=root/('step-'+str(step).zfill(2)+'-'+action);out.mkdir()
                    if action=='tail':atomic(out/'selection.json',dict(methods=command['methods']))
                    if resource is None:guard=guardian(lease,deadline);resource=pg_resume(out)
                    env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource),PYTHONPATH=str(ROOT/'backend/tests/fixtures/task111/bootstrap')+os.pathsep+str(ROOT/'backend'))
                    with (out/'stdout.bin').open('wb') as stdout,(out/'stderr.bin').open('wb') as stderr:
                        child=subprocess.Popen([sys.executable,'-B','-m','tests.fixtures.task111.c06_step',action,str(out)],cwd=ROOT/'backend',env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
                        atomic(out/'launcher.json',dict(pid=child.pid,birth=birth(child.pid)))
                        try:child.wait(timeout=max(.1,(min(active['deadline_ns'],deadline)-time.monotonic_ns())/1e9-20))
                        except subprocess.TimeoutExpired:
                            owner=json.loads((out/'actual-step-owner.json').read_text(encoding='utf-8'));terminate_owned(owner['pid'],owner['birth']);child.wait(5)
                    last=dict(step=step,action=action,exit=child.returncode,folder=str(out),resource_held=True,completed_ns=time.monotonic_ns())
                    atomic(CONTINUE_ROOT/'step-complete.json',last)
            last_end=time.monotonic_ns()
    finally:
        phase('cleanup')
        if guard:
            receipt=cleanup(lease,guard)
            end=time.monotonic_ns();tail=(end-last_end)/1e9 if last_end else 0
            with locked():
                b=read_state();b['time_seconds']['real']+=tail;b['time_seconds']['cleanup']-=receipt['seconds'];atomic(EVIDENCE/'budget.json',b)
            segments.append(dict(kind='PG_after_root_through_cleanup_confirmation',seconds=tail,cleanup_seconds_reclassified_no_double_count=receipt['seconds']))
        atomic(CONTINUE_ROOT/('lease-accounting.json' if prior['counts']['real_batches']==16 else 'lease-accounting-2.json'),dict(segments=segments,budget=read_state(),no_overlap=True))
        phase('implementation_offline')

if __name__=='__main__':main()
