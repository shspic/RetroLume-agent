"""全部新故障共用唯一根；独立取证者持有实际管道和Job，不借换根解封。"""
import asyncio,ctypes,hashlib,json,msvcrt,os,subprocess,sys,threading,time
from ctypes import wintypes
from pathlib import Path
from uuid import uuid4
from .control import ROOT,CONTINUE_ROOT,PERMIT,atomic,read_state,registry_root
from .resources import shell_env
from .core import Harness
from app.preview import docker_control as dc
from app.preview.process import birth,terminate_owned
from app.preview.host_job import HostJob,job_name
from app.preview.business_contracts import OpenPreview,HtmlRefusal
from app.runtime import psycopg_compatible_loop_factory

NAMES=('node_busy','reaper_death','owner_control_lost','pipe_corrupt','supervisor_death','both_supervisors_death','control_path_lost','hard_deadline')

class Witness:
    def __init__(self,row):
        self.row=row;self.streams=[];self.jobs=[];self.threads=[];self.results=[]
        api=ctypes.WinDLL('kernel32',use_last_error=True)
        api.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);api.OpenProcess.restype=wintypes.HANDLE
        api.GetCurrentProcess.restype=wintypes.HANDLE;api.CloseHandle.argtypes=(wintypes.HANDLE,)
        api.DuplicateHandle.argtypes=(wintypes.HANDLE,wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.HANDLE),wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);api.DuplicateHandle.restype=wintypes.BOOL
        assert birth(row['actor_pid'])['birth']==row['actor_birth']
        process=api.OpenProcess(0x0040,False,row['actor_pid'])
        if not process:raise OSError(ctypes.get_last_error(),'witness_process')
        try:
            for handle in row['pipe_handles']:
                duplicate=wintypes.HANDLE()
                if not api.DuplicateHandle(process,handle,api.GetCurrentProcess(),ctypes.byref(duplicate),0,False,2):raise OSError(ctypes.get_last_error(),'witness_pipe')
                self.streams.append(os.fdopen(msvcrt.open_osfhandle(duplicate.value,os.O_RDONLY|os.O_BINARY),'rb',buffering=0))
            for role in ('SUP','REAP'):self.jobs.append(HostJob(job_name(row['preview_id'],row['nonce'],role),existing=True))
        finally:api.CloseHandle(process)
    def drain(self):
        def read(stream,index):
            total=0;sha=hashlib.sha256();error=None;eof=False
            try:
                while True:
                    block=stream.read(65536)
                    if not block:eof=True;break
                    total+=len(block);sha.update(block)
                    if total>16*1024*1024:raise RuntimeError('witness_bounded_pipe')
            except Exception as exc:error=type(exc).__name__
            self.results.append(dict(index=index,bytes=total,sha256=sha.hexdigest(),actual_eof=eof,error_type=error,at_ns=time.monotonic_ns()))
        for i,stream in enumerate(self.streams):
            t=threading.Thread(target=read,args=(stream,i),daemon=False);t.start();self.threads.append(t)
    def finish(self,out):
        for job in self.jobs:job.finish()
        for thread in self.threads:thread.join(5)
        assert len(self.results)==2 and all(r['actual_eof'] for r in self.results) and not any(t.is_alive() for t in self.threads)
        proofs={role:job.finish() for role,job in zip(('SUP','REAP'),self.jobs)}
        atomic(out/'independent-pipe-and-jobs.json',dict(pipes=sorted(self.results,key=lambda x:x['index']),jobs=proofs,actor_pid=self.row['actor_pid'],actor_birth=self.row['actor_birth'],
          duplicate_before_trigger=True,read_only_after_actor_exit=True,held_job_handles_note='独立取证者预持有同一Job句柄；生产故障后精确CID停止，Job查询/终止由既有恢复路径和取证者完成，不冒双监督自主停止'))
        return proofs
    def close(self):
        for job in self.jobs:job.close()
        for stream in self.streams:stream.close()

async def recover(resource,built,out,witness,unknown):
    trigger=json.loads((out/'trigger.json').read_text(encoding='utf-8'));folder=Path(trigger['runtime_folder']);registry=json.loads((folder/'registry.json').read_text(encoding='utf-8'))
    facts=json.loads((folder/'kernel-premises.json').read_text(encoding='utf-8'));assert registry_root().resolve()==folder.parent.resolve()
    h=Harness(resource,built,out)
    try:
        row=await h.ledger.read_html_preview(trigger['activity_id'],trigger['preview_id'])
        if unknown:
            assert row['reserved_seconds']>=row['reserve_seconds'] and row['elapsed_seconds'] is None
            item=json.loads((out/'fixture-item.json').read_text(encoding='utf-8'))
            try:await h.controller.open(trigger['activity_id'],item['receipt']['artifact_id'],OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=item['receipt']['artifact_sha256'],input_owner_key='1'*64,confirmed=True))
            except HtmlRefusal as exc:assert exc.code=='cleanup_unconfirmed'
            else:raise AssertionError('新UNKNOWN解封了新start')
        physical=dc.inspect_owned(h.policy.docker,registry['cid'],registry['intent'])
        if physical['state']['Running']:
            result=dc.call(h.policy.docker,['kill',registry['cid']]);atomic(out/'external-exact-kill.json',result);assert result['code']==0
        # EOF来自触发前已复制的真实匿名管道，不能用Pid0代替。
        witness.drain()
        terminate_owned(registry['attach_pid'],registry['attach_birth'])
        reaper=registry['reaper_owner'];terminate_owned(reaper['pid'],reaper['birth'])
        jobs=witness.finish(out)
        proof=dc.stop_owned(h.policy.docker,registry['cid'],registry['intent'],facts,attach_ended=True)
        proof.update(supervisor_cli_windows_job=jobs['SUP'],reaper_windows_job=jobs['REAP'],owned_reaper_ended=True,actual_parent_ended=birth(registry['parent']['pid'])['state']=='exited',external_acceptance_cleanup=True)
        assert proof['tree_confirmation']=='private_pid_init_terminated' and proof['actual_parent_ended']
        atomic(out/'external-complete-stop-proof.json',proof)
        await h.controller.recover();assert not h.controller.blocked,'同根持久恢复失败'
        after=await h.ledger.read_html_preview(trigger['activity_id'],trigger['preview_id']);assert after['state']=='stopped' and after['reserved_seconds']==0
        if unknown:assert after['elapsed_seconds']==row['reserve_seconds']
        if trigger['scenario']=='hard_deadline':
            from datetime import datetime
            state=dc.inspect_owned(h.policy.docker,registry['cid'],registry['intent'])['state']
            # Docker纳秒文本由datetime按微秒截取；比较原DB UTC截止。
            assert datetime.fromisoformat(state['FinishedAt'].replace('Z','+00:00'))<=datetime.fromisoformat(row['deadline_at'])
        atomic(out/'persistent-same-root-recovery.json',dict(before=row,after=after,unknown_full_R_settled=unknown,root=str(registry_root()),actual_EOF_and_Job_zero=proof))
    finally:await h.controller.close()

def run_all(resource,production,folder):
    built=json.loads((CONTINUE_ROOT/'fault-build.json').read_text(encoding='utf-8'));plan=json.loads((CONTINUE_ROOT/'matrix-plan.json').read_text(encoding='utf-8'));results=[]
    for name in NAMES:
        out=folder/name;out.mkdir();command=dict(scenario=name,activity_id=plan['objects']['fault_'+name]['activity_id'],registry=str(registry_root().resolve()),out=str(out));atomic(out/'command.json',command)
        env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource))
        witness=None
        with (out/'actor.stdout.bin').open('wb') as stdout,(out/'actor.stderr.bin').open('wb') as stderr:
            child=subprocess.Popen([sys.executable,'-B','-m','tests.fixtures.task111.c04_fault_actor',str(out/'command.json')],cwd=ROOT/'backend',env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            atomic(out/'launcher.json',dict(pid=child.pid,birth=birth(child.pid)))
            until=time.monotonic()+15
            while not (out/'pretrigger.json').is_file():
                if child.poll() is not None or time.monotonic()>until:raise RuntimeError('故障在真实READY取证前失败:'+name)
                time.sleep(.03)
            witness=Witness(json.loads((out/'pretrigger.json').read_text(encoding='utf-8')));atomic(out/'witness-bound.json',dict(actual_pid=os.getpid(),birth=birth(os.getpid()),exact_pipes_duplicated=True))
            try:
                child.wait(timeout=min(120,max(.1,(read_state()['active_batch']['deadline_ns']-time.monotonic_ns())/1e9-5)))
                expected=71 if name=='supervisor_death' else 72 if name=='both_supervisors_death' else 0
                assert child.returncode==expected,'actor exit '+str(child.returncode)
                unknown=name in ('both_supervisors_death','control_path_lost','hard_deadline');restart=name in ('supervisor_death','both_supervisors_death','control_path_lost','hard_deadline')
                if name=='supervisor_death':
                    until=time.monotonic()+8;runtime=Path(json.loads((out/'trigger.json').read_text(encoding='utf-8'))['runtime_folder'])
                    while not (runtime/'reaper-receipt.json').exists() and time.monotonic()<until:time.sleep(.03)
                    assert (runtime/'reaper-receipt.json').exists()
                if restart:
                    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(recover(resource,built,out,witness,unknown))
                else:
                    witness.drain();witness.finish(out);report=json.loads((out/'actor-result.json').read_text(encoding='utf-8'));assert report['stop']['confirmed']
                results.append(dict(scenario=name,status='PASS_ACTUAL_FAULT_AND_SAME_ROOT_CONFIRMATION',actor_exit=child.returncode,unknown_then_recovered=unknown,fault_image=built['image']['id'],production_navigation_claim=False));atomic(folder/'fault-results.json',results)
            finally:
                if child.poll() is None:
                    actual=json.loads((out/'actor-owner.json').read_text(encoding='utf-8'));terminate_owned(actual['pid'],actual['birth']);child.wait(5)
                if witness:witness.close()
