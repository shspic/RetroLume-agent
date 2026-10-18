"""读完实际结果才决定修正/停止；同PG跨新根，清场不走业务闸。"""
import json,os,subprocess,sys,time
from .control import ROOT,CONTINUE_ROOT,CONTINUATION,PERMIT,atomic,batch,phase,read_state,source_snapshot,CAPS,event
from .resources import pg_resume,shell_env
from .c03_resources import guardian,cleanup
from app.preview.process import birth,terminate_owned

def main():
    assert CONTINUATION=='TASK-111-G11-C05-20261011' and os.environ.get('RETROLUME_TASK111_FIXTURE')==PERMIT
    prior=read_state();timing=json.loads((CONTINUE_ROOT/'timing.json').read_text(encoding='utf-8'));remaining=min(1800-(prior['time_seconds']['real']-timing['prior_time_seconds']['real']),14400-prior['time_seconds']['real'])
    deadline=min(prior['business_deadline_ns'],time.monotonic_ns()+int((remaining-15)*1e9));resource=None;guard=None;step=0;stop=False;phase('real')
    lease=CONTINUE_ROOT/'integrated-holder';lease.mkdir(exist_ok=False);atomic(lease/'owner.json',dict(pid=os.getpid(),birth=birth(os.getpid()),deadline_ns=deadline))
    try:
        for n in range(prior['counts']['real_batches']+1,CAPS['real_batches']+1):
            if stop or time.monotonic_ns()>=deadline-20*10**9:break
            root=CONTINUE_ROOT/('root-'+str(n));root.mkdir()
            with batch('real','C05 remaining client and death recovery',maximum=min(1500,(deadline-time.monotonic_ns())/1e9)) as active:
                source_snapshot(root);atomic(CONTINUE_ROOT/'coordinator-ready.json',dict(pid=os.getpid(),birth=birth(os.getpid()),root=n,root_deadline_ns=active['deadline_ns'],hold_deadline_ns=deadline))
                while time.monotonic_ns()<min(active['deadline_ns'],deadline)-15*10**9:
                    path=CONTINUE_ROOT/('command-'+str(step+1).zfill(2)+'.json')
                    if not path.exists():time.sleep(.05);continue
                    command=json.loads(path.read_text(encoding='utf-8'));step+=1;action=command['action']
                    if action=='stop':stop=True;break
                    if action=='next_root':break
                    out=root/('step-'+str(step).zfill(2)+'-'+action);out.mkdir()
                    if action!='job_probe' and resource is None:guard=guardian(lease,deadline);resource=pg_resume(out)
                    env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource or {}),PYTHONPATH=str(ROOT/'backend/tests/fixtures/task111/bootstrap')+os.pathsep+str(ROOT/'backend'))
                    with (out/'stdout.bin').open('wb') as stdout,(out/'stderr.bin').open('wb') as stderr:
                        child=subprocess.Popen([sys.executable,'-B','-m','tests.fixtures.task111.c05_step',action,str(out)],cwd=ROOT/'backend',env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW);atomic(out/'launcher.json',dict(pid=child.pid,birth=birth(child.pid)))
                        try:child.wait(timeout=min(900,max(.1,(min(active['deadline_ns'],deadline)-time.monotonic_ns())/1e9-20)))
                        except subprocess.TimeoutExpired:
                            owner=json.loads((out/'actual-step-owner.json').read_text(encoding='utf-8'));terminate_owned(owner['pid'],owner['birth']);child.wait(5)
                    atomic(CONTINUE_ROOT/'step-complete.json',dict(step=step,action=action,exit=child.returncode,folder=str(out),resource_held=resource is not None))
                    # 成功与普通失败均回到等待结果决策；从不预排终止。
    finally:
        phase('cleanup')
        if guard:cleanup(lease,guard)
        phase('implementation_offline')

if __name__=='__main__':main()
