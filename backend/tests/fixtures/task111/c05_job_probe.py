"""实际HostJob生命周期边界；不以观测句柄代替自然最后关闭。"""
import ctypes,json,os,subprocess,sys,time
from ctypes import wintypes
from pathlib import Path
from uuid import uuid4
from .control import atomic,ROOT
from .resources import shell_env
from app.preview.process import birth,OwnershipUnknown
from app.preview.host_job import HostJob,JobChild,job_name,observe_job_end

class SyncProcess:
    def __init__(self,row):
        self.row=row;self.api=ctypes.WinDLL('kernel32',use_last_error=True)
        self.api.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);self.api.OpenProcess.restype=wintypes.HANDLE
        self.api.WaitForSingleObject.argtypes=(wintypes.HANDLE,wintypes.DWORD);self.api.CloseHandle.argtypes=(wintypes.HANDLE,)
        self.handle=self.api.OpenProcess(0x1000|0x100000,False,row['pid'])
        if not self.handle or birth(row['pid']).get('birth')!=row['birth']:raise OwnershipUnknown('sync_process_birth')
    def ended(self):return self.api.WaitForSingleObject(self.handle,0)==0
    def close(self):
        if self.handle:self.api.CloseHandle(self.handle);self.handle=None

def actor(out):
    own=dict(pid=os.getpid(),birth=birth(os.getpid())['birth']);job=HostJob(job_name(str(uuid4()),'1'*64,'SUP'))
    child=JobChild([sys.executable,'-c','import time; time.sleep(120)'],job,env=shell_env(),devnull=True,suspended=True)
    premise=job.premise(own);atomic(out/'ready.json',dict(owner=own,child=dict(pid=child.pid,birth=child.birth['birth']),premise=premise));child.resume()
    until=time.monotonic()+30
    while not (out/'exit.flag').exists():
        if time.monotonic()>until:os._exit(74)
        time.sleep(.02)
    os._exit(73)

def run(out):
    results=[]
    for mode in ('last_handle_closes','extra_handle_retained'):
        folder=out/mode;folder.mkdir();child=subprocess.Popen([sys.executable,'-B','-m','tests.fixtures.task111.c05_job_probe','actor',str(folder)],cwd=ROOT/'backend',env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        until=time.monotonic()+8
        while not (folder/'ready.json').exists():
            if child.poll() is not None or time.monotonic()>until:raise RuntimeError('Job probe owner not ready')
            time.sleep(.03)
        row=json.loads((folder/'ready.json').read_text(encoding='utf-8'));owner=SyncProcess(row['owner']);member=SyncProcess(row['child']);held=None
        try:
            if mode=='extra_handle_retained':held=HostJob(row['premise']['name'],existing=True)
            (folder/'exit.flag').write_text('exit own test controller',encoding='ascii');child.wait(5)
            assert owner.ended()
            if held:
                assert not member.ended() and held.active()>0
                atomic(folder/'before_last_handle_close.json',dict(owner_ended=True,child_still_running=True,actual_job_active=held.active(),observer_called_terminate=False))
                held.close();held=None
            until=time.monotonic()+3
            while not member.ended() and time.monotonic()<until:time.sleep(.02)
            assert member.ended();proof=observe_job_end(row['premise']['name'],row['premise']);assert proof['termination_evidence']=='job_destroyed' and 'ActiveProcesses' not in proof
            denied=[]
            for label,name,premise in (('wrong_name',row['premise']['name']+'.wrong',row['premise']),('never_created',job_name(str(uuid4()),'2'*64,'SUP'),None)):
                try:observe_job_end(name,premise)
                except OwnershipUnknown as error:denied.append(dict(case=label,refusal=str(error)))
                else:raise AssertionError('不存在被冒作已销毁')
            results.append(dict(mode=mode,natural_owner_exit=child.returncode,proof=proof,negative=denied,no_terminate_job_object=True));atomic(out/'job-lifecycle-result.json',results)
        finally:
            if held:held.close()
            owner.close();member.close()
    denied_access(out)

def denied_access(out):
    # 本机专有空Job收紧DACL；既有持有句柄不变，不改文件权限或其它对象。
    job=HostJob(job_name(str(uuid4()),'3'*64,'SUP'));owner=dict(pid=os.getpid(),birth=birth(os.getpid())['birth']);premise=job.premise(owner)
    api=ctypes.WinDLL('advapi32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    api.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes=(wintypes.LPCWSTR,wintypes.DWORD,ctypes.POINTER(ctypes.c_void_p),ctypes.POINTER(wintypes.DWORD));api.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype=wintypes.BOOL
    api.GetSecurityDescriptorDacl.argtypes=(ctypes.c_void_p,ctypes.POINTER(wintypes.BOOL),ctypes.POINTER(ctypes.c_void_p),ctypes.POINTER(wintypes.BOOL));api.GetSecurityDescriptorDacl.restype=wintypes.BOOL
    api.SetSecurityInfo.argtypes=(wintypes.HANDLE,ctypes.c_int,wintypes.DWORD,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p);api.SetSecurityInfo.restype=wintypes.DWORD
    kernel.LocalFree.argtypes=(ctypes.c_void_p,);sd=ctypes.c_void_p();present=wintypes.BOOL();defaulted=wintypes.BOOL();acl=ctypes.c_void_p()
    try:
        assert api.ConvertStringSecurityDescriptorToSecurityDescriptorW('D:P(D;;0x0004;;;WD)(A;;GA;;;OW)',1,ctypes.byref(sd),None)
        assert api.GetSecurityDescriptorDacl(sd,ctypes.byref(present),ctypes.byref(acl),ctypes.byref(defaulted));assert api.SetSecurityInfo(job.handle,6,4,None,None,acl,None)==0
        native=job.api;ctypes.set_last_error(0);handle=native.OpenJobObjectW(4,False,job.name);error=ctypes.get_last_error();assert not handle and error==5
        # 准确原生错误5保守拒绝；当前owner活着也不能进入结束分支。
        try:observe_job_end(job.name,premise)
        except OwnershipUnknown as refusal:result=str(refusal)
        else:raise AssertionError('拒绝访问被冒作零任务')
        atomic(out/'job-access-denied-result.json',dict(actual_open_error=error,refusal=result,accepted=False,object_empty_before_acl=True,other_objects_or_file_acl_changed=False))
    finally:
        if sd.value:kernel.LocalFree(sd)
        job.close()

if __name__=='__main__':
    if sys.argv[1]=='actor':actor(Path(sys.argv[2]).resolve())
    else:run(Path(sys.argv[1]).resolve())
