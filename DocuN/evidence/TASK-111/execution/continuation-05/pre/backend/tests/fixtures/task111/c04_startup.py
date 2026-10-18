"""实际生产路径的Windows读句柄替换拒绝，精确检查挂起/EOF/Job。"""
import asyncio,ctypes,json,secrets,time
from ctypes import wintypes
from uuid import uuid4
from .control import atomic,registry_root
from .core import Harness
from .c01_seeds import diagnostic_artifact
from .c03_matrix import Session
from app.preview.business_contracts import OpenPreview
from app.preview.process import atomic_json,birth
from app.preview import docker_control as dc

class ReaderLock:
    def __init__(self,path):
        self.api=ctypes.WinDLL('kernel32',use_last_error=True)
        self.api.CreateFileW.argtypes=(wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE);self.api.CreateFileW.restype=wintypes.HANDLE
        self.api.CloseHandle.argtypes=(wintypes.HANDLE,)
        self.handle=self.api.CreateFileW(str(path),0x80000000,1,None,3,0,None)
        if self.handle==ctypes.c_void_p(-1).value:raise OSError(ctypes.get_last_error(),'fixture_reader_lock')
    def close(self):
        if self.handle:self.api.CloseHandle(self.handle);self.handle=None

async def execute(resource,built,out):
    h=Harness(resource,built,out);original=h.controller._registry;witness={};holder=None
    try:
        await h.controller.recover();assert not h.controller.blocked
        if h.controller.current_file.exists():
            pointer=json.loads(h.controller.current_file.read_text(encoding='utf-8'));previous=json.loads((__import__('pathlib').Path(pointer['folder'])/'registry.json').read_text(encoding='utf-8'))
            row=await h.ledger.read_html_preview(previous['activity_id'],previous['preview_id']);atomic(out/'same-root-prior-recovery.json',dict(pointer=pointer,row=row))
        item=await diagnostic_artifact(h,'energy');atomic(out/'fixture-item.json',item)
        def locked_registry(c):
            nonlocal holder
            if c['registry'].get('attach_pid') and not witness:
                holder=ReaderLock(c['folder']/'registry.json')
                witness.update(stage='suspended_attach_registry',cid=c['cid'],preview_id=c['preview_id'],attach_pid=c['attach'].pid,attach_birth=c['attach'].birth,attach_resumed=c['attach'].resumed,
                  windows_job=c['host_job'].name,job_active=c['host_job'].active(),reader_started=c['reader'].is_alive(),stderr_reader_started=c['stderr_reader'].is_alive(),before=dc.inspect_owned(h.policy.docker,c['cid'],c['intent']))
                assert not witness['attach_resumed'] and witness['before']['state']['Status']=='created' and witness['before']['state']['StartedAt'].startswith('0001-')
                begin=time.monotonic_ns()
                try:original(c)
                except PermissionError as error:witness.update(error_type=type(error).__name__,errno=error.errno,winerror=getattr(error,'winerror',None),rejected_seconds=(time.monotonic_ns()-begin)/1e9);raise
                else:raise AssertionError('真实读句柄没有阻止关键登记替换')
                finally:holder.close();holder=None
            return original(c)
        h.controller._registry=locked_registry
        opened=await h.controller.open(item['activity_id'],item['receipt']['artifact_id'],OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=item['receipt']['artifact_sha256'],input_owner_key=secrets.token_hex(32),confirmed=True));c=h.controller.current
        await asyncio.to_thread(c['thread'].join,15);assert not c['thread'].is_alive()
        row=await h.ledger.read_html_preview(item['activity_id'],opened['preview_id']);result=json.loads((c['folder']/'supervisor-result.json').read_text(encoding='utf-8'))
        assert row['state']=='failed_unstarted' and row['starts_used']==1 and row['reserved_seconds']==0
        assert result['confirmed'] and result['proof']['tree_confirmation']=='never_started'
        assert birth(witness['attach_pid'])['state']=='exited' and result['proof']['supervisor_cli_windows_job']['ActiveProcesses']==0
        witness.update(after=dc.inspect_owned(h.policy.docker,c['cid'],c['intent']),row=row,result=result,old_attempt_not_refunded=True)
        atomic(out/'real-suspended-start-rejection.json',witness);h.controller._registry=original
        # 同一路径解除读锁后成功；随后真实已ready的观察日志锁故障仍必须排空停止。
        target=out/'released-and-postready';target.mkdir();s=Session(h,item,target);await s.open();c=s.c
        observation=c['folder']/'engine-observation-1.json';atomic_json(observation,{'fixture':'preexisting_target_for_real_read_handle'});holder=ReaderLock(observation)
        try:
            try:await s.input('h','3')
            except Exception:pass
            row,result=await s.finish(request_stop=False)
            assert c['pipe_eof'] and not c['reader'].is_alive() and not c['stderr_reader'].is_alive()
            denied=[x for x in result.get('diagnostics',[]) if x['type']=='PermissionError' and x['path_alias']=='engine-observation-1.json'];assert denied
            assert result['proof']['supervisor_cli_windows_job']['ActiveProcesses']==0 and result['proof']['reaper_windows_job']['ActiveProcesses']==0
            atomic(out/'real-postready-log-rejection.json',dict(status='PASS_REAL_LOCK_DRAIN_AND_COMPLETE_STOP',diagnostics=denied,actual_ready=c['received_ready'],pipe_eof=True,stop=result,row=row,successful_released_start=True))
        finally:holder.close();holder=None
    finally:
        h.controller._registry=original
        if holder:holder.close()
        await h.controller.close()
