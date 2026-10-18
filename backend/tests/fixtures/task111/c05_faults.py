"""六项剩余故障：只保留同步进程句柄/管道读副本，自主窗内无主动清理。"""
import asyncio,ctypes,hashlib,json,msvcrt,os,subprocess,sys,threading,time
from ctypes import wintypes
from pathlib import Path
from uuid import uuid4
from .control import ROOT,CONTINUE_ROOT,PERMIT,atomic,read_state,registry_root
from .resources import shell_env
from .core import Harness
from .c05_job_probe import SyncProcess
from app.preview import docker_control as dc
from app.preview.process import birth,terminate_owned
from app.preview.host_job import observe_job_end
from app.preview.business_contracts import OpenPreview,HtmlRefusal
from app.runtime import psycopg_compatible_loop_factory

NAMES=('owner_control_lost','pipe_corrupt','supervisor_death','both_supervisors_death','control_path_lost','hard_deadline')

class PassiveWitness:
    def __init__(self,row):
        self.row=row;self.streams=[];self.sync=[];self.results=[];self.threads=[]
        api=ctypes.WinDLL('kernel32',use_last_error=True);api.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);api.OpenProcess.restype=wintypes.HANDLE
        api.GetCurrentProcess.restype=wintypes.HANDLE;api.CloseHandle.argtypes=(wintypes.HANDLE,)
        api.DuplicateHandle.argtypes=(wintypes.HANDLE,wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.HANDLE),wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);api.DuplicateHandle.restype=wintypes.BOOL
        self.observer=dict(pid=os.getpid(),birth=birth(os.getpid())['birth'])
        for r in [row['parent'],row['attach'],row['reaper_owner']]:self.sync.append(SyncProcess(r))
        process=api.OpenProcess(0x40,False,row['actor_pid'])
        if not process:raise RuntimeError('pipe observer source process')
        try:
            for handle in row['pipe_handles']:
                duplicate=wintypes.HANDLE()
                if not api.DuplicateHandle(process,handle,api.GetCurrentProcess(),ctypes.byref(duplicate),0,False,2):raise RuntimeError('pipe read duplication')
                self.streams.append(os.fdopen(msvcrt.open_osfhandle(duplicate.value,os.O_RDONLY|os.O_BINARY),'rb',buffering=0))
        finally:api.CloseHandle(process)
    def drain(self,out):
        assert self.sync[0].ended(),'不能与存活生产reader争读'
        def read(stream,index):
            size=0;sha=hashlib.sha256();error=None;eof=False
            try:
                while True:
                    data=stream.read(65536)
                    if not data:eof=True;break
                    size+=len(data);sha.update(data)
                    if size>16*1024*1024:raise RuntimeError('bounded pipe capture')
            except Exception as exc:error=type(exc).__name__
            self.results.append(dict(index=index,bytes=size,sha256=sha.hexdigest(),actual_eof=eof,error_type=error,at_ns=time.monotonic_ns()))
        for i,stream in enumerate(self.streams):
            thread=threading.Thread(target=read,args=(stream,i),daemon=False);thread.start();self.threads.append(thread)
        for thread in self.threads:thread.join(5)
        assert len(self.results)==2 and all(r['actual_eof'] for r in self.results) and not any(t.is_alive() for t in self.threads)
        obs=dict(preview_id=self.row['preview_id'],cid=self.row['cid'],nonce=self.row['nonce'],image_id=self.row['image_id'],source_parent=self.row['parent'],source_attach=self.row['attach'],observer=self.observer,
          captured_before_trigger=True,read_after_parent_exit=True,pipes=sorted(self.results,key=lambda x:x['index']),extra_job_handles_held=False,observer_terminated=False)
        atomic(out/'natural-pipe-observation.json',obs);return obs
    def close_pipes(self):
        for stream in self.streams:stream.close()
    def close(self):
        self.close_pipes()
        for handle in self.sync:handle.close()

async def recover(resource,built,out,witness,unknown):
    trigger=json.loads((out/'trigger.json').read_text(encoding='utf-8'));folder=Path(trigger['runtime_folder']);reg=json.loads((folder/'registry.json').read_text(encoding='utf-8'));h=Harness(resource,built,out)
    try:
        before=await h.ledger.read_html_preview(trigger['activity_id'],trigger['preview_id']);physical=dc.inspect_owned(h.policy.docker,reg['cid'],reg['intent'])
        atomic(out/'before_external_cleanup.json',dict(row=before,physical=physical,at_ns=time.monotonic_ns(),observer_has_not_killed=True,extra_job_handles_held=False))
        if unknown:
            assert before['reserved_seconds']>=before['reserve_seconds'] and before['elapsed_seconds'] is None
            item=json.loads((out/'fixture-item.json').read_text(encoding='utf-8'))
            try:await h.controller.open(trigger['activity_id'],item['receipt']['artifact_id'],OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=item['receipt']['artifact_sha256'],input_owner_key='1'*64,confirmed=True))
            except HtmlRefusal as error:assert error.code=='cleanup_unconfirmed'
            else:raise AssertionError('UNKNOWN允许start')
        if trigger['scenario']=='supervisor_death':
            assert not physical['state']['Running'],'生产Reaper未自主结束对象'
            receipt=json.loads((folder/'reaper-receipt.json').read_text(encoding='utf-8'));assert receipt['reason']=='parent_lost'
        if trigger['scenario']=='hard_deadline':
            from datetime import datetime
            assert not physical['state']['Running'];assert datetime.fromisoformat(physical['state']['FinishedAt'].replace('Z','+00:00'))<=datetime.fromisoformat(before['deadline_at'])
        if physical['state']['Running']:
            assert unknown and trigger['scenario'] in ('both_supervisors_death','control_path_lost')
            kill=dc.call(h.policy.docker,['kill',reg['cid']]);assert kill['code']==0;atomic(out/'external_exact_cleanup.json',dict(kill=kill,after_autonomous_or_unknown_observation=True))
        # 同步句柄不会保留Job；只在自主结果/预期UNKNOWN之后清登记实例。
        for instance in (reg['reaper_owner'],dict(pid=reg['attach_pid'],birth=reg['attach_birth'])):
            if birth(instance['pid'])['state']=='running':assert unknown;terminate_owned(instance['pid'],instance['birth'])
        obs=witness.drain(out);await h.controller.recover(recovery_observation=obs);assert not h.controller.blocked,'真实同根恢复未确认'
        after=await h.ledger.read_html_preview(trigger['activity_id'],trigger['preview_id']);assert after['state']=='stopped' and after['reserved_seconds']==0
        assert after['elapsed_seconds']==before['reserve_seconds'],'死亡/迟到恢复不能退款'
        proof=json.loads((folder/'recovery-proof.json').read_text(encoding='utf-8'))
        atomic(out/'same-root-persistent-recovery.json',dict(before=before,after=after,proof=proof,root=str(registry_root()),no_job_handle_preheld=True,external_kill_used=physical['state']['Running']))
    finally:await h.controller.close()

def run_all(resource,built,folder):
    results=[];witnesses=[]
    try:
        for name in NAMES:
            complete=folder/name/'scenario-result.json'
            if complete.exists():results.append(json.loads(complete.read_text(encoding='utf-8')));continue
            out=folder/name;out.mkdir(exist_ok=False);command=dict(scenario=name,activity_id=str(uuid4()),registry=str(registry_root().resolve()),out=str(out));atomic(out/'command.json',command)
            env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource))
            with (out/'actor.stdout.bin').open('wb') as stdout,(out/'actor.stderr.bin').open('wb') as stderr:
                child=subprocess.Popen([sys.executable,'-B','-m','tests.fixtures.task111.c05_fault_actor',str(out/'command.json')],cwd=ROOT/'backend',env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
                atomic(out/'launcher.json',dict(pid=child.pid,birth=birth(child.pid)))
                until=time.monotonic()+15
                while not (out/'pretrigger.json').exists():
                    if child.poll() is not None or time.monotonic()>until:raise RuntimeError('故障未到READY:'+name)
                    time.sleep(.02)
                witness=PassiveWitness(json.loads((out/'pretrigger.json').read_text(encoding='utf-8')));witnesses.append(witness);atomic(out/'witness-bound.json',dict(observer=witness.observer,no_job_handle_held=True,only_sync_and_read_pipe_handles=True))
                child.wait(timeout=min(120,max(.1,(read_state()['active_batch']['deadline_ns']-time.monotonic_ns())/1e9-15)))
                expected=71 if name=='supervisor_death' else 72 if name=='both_supervisors_death' else 0
                unknown=name in ('both_supervisors_death','control_path_lost','hard_deadline')
                if name=='supervisor_death':
                    runtime=Path(witness.row['runtime_folder']);until=time.monotonic()+10
                    while not (runtime/'reaper-receipt.json').is_file() and time.monotonic()<until:time.sleep(.02)
                    assert (runtime/'reaper-receipt.json').exists()
                if name in ('supervisor_death','both_supervisors_death','control_path_lost','hard_deadline'):
                    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(recover(resource,built,out,witness,unknown))
                else:
                    witness.drain(out);report=json.loads((out/'actor-result.json').read_text(encoding='utf-8'));assert report['stop']['confirmed']
                    atomic(out/'before_external_cleanup.json',dict(physical_tree_confirmed=report['stop']['proof'],observer_terminated=False,no_job_handles_held=True))
                witness.close_pipes()
                assert child.returncode==expected,'actor exit '+str(child.returncode)
                result=dict(scenario=name,status='PASS_REAL_REMAINING_SCENARIO',actor_exit=child.returncode,expected_unknown_then_recovered=unknown,extra_job_handles_held=False,source_image=built['image']['id']);results.append(result);atomic(out/'scenario-result.json',result);atomic(folder/'fault-results.json',results)
    finally:
        for witness in witnesses:witness.close()
