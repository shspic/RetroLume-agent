"""预览控制CLI的Windows Job；悬停创建→入Job→恢复，独立于模型四账Job。"""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import contextlib
import os
import subprocess
import threading
import time
import uuid
import _winapi
import msvcrt
from app.worker.windows_job import _kernel,_EXTENDED_LIMIT,_BASIC_ACCOUNTING
from .process import OwnershipUnknown,birth

_local=threading.local()


class HostJob:
    def __init__(self,name,existing=False):
        if not name.startswith("Global\\RetroLume.Preview."):raise OwnershipUnknown("job_scope")
        self.api=_kernel();self.name=name
        if existing:self.handle=self.api.OpenJobObjectW(0x0004|0x0008,False,name)
        else:
            ctypes.set_last_error(0);self.handle=self.api.CreateJobObjectW(None,name)
            if self.handle and ctypes.get_last_error()==183:self.api.CloseHandle(self.handle);self.handle=None
        if not self.handle:raise OwnershipUnknown("host_job_unavailable")
        if not existing:
            limits=_EXTENDED_LIMIT();limits.BasicLimitInformation.LimitFlags=0x2000|0x8|0x200
            limits.BasicLimitInformation.ActiveProcessLimit=4;limits.JobMemoryLimit=256*1024*1024
            if not self.api.SetInformationJobObject(self.handle,9,ctypes.byref(limits),ctypes.sizeof(limits)):
                self.close();raise OwnershipUnknown("host_job_limits")
    def active(self):
        data=_BASIC_ACCOUNTING()
        if not self.api.QueryInformationJobObject(self.handle,1,ctypes.byref(data),ctypes.sizeof(data),None):raise OwnershipUnknown("host_job_query")
        return int(data.ActiveProcesses)
    def terminate(self):
        if self.active() and not self.api.TerminateJobObject(self.handle,1):raise OwnershipUnknown("host_job_terminate")
    def finish(self,seconds=2):
        self.terminate();deadline=time.monotonic()+seconds
        while self.active():
            if time.monotonic()>=deadline:raise OwnershipUnknown("host_job_not_empty")
            time.sleep(.02)
        return {"name":self.name,"ActiveProcesses":0,"kill_on_close":True,"assignment":"suspended_before_resume","at_ns":time.monotonic_ns()}
    def close(self):
        if self.handle:self.api.CloseHandle(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*_):self.close()


def job_name(preview_id,nonce,role):
    if len(nonce)!=64 or role not in ("SUP","REAP","REC","CALL"):raise OwnershipUnknown("job_identity")
    return "Global\\RetroLume.Preview."+uuid.UUID(preview_id).hex+"."+nonce+"."+role


@contextlib.contextmanager
def scope(job):
    old=getattr(_local,"job",None);_local.job=job
    try:yield
    finally:_local.job=old


def current_job():return getattr(_local,"job",None)


class JobChild:
    """仅固定内部argv/clean Env的Popen接口，三个匿名管道不继承其他handle。"""
    def __init__(self,args,job,*,env,cwd=None,devnull=False):
        self.args=args;self.job=job;self._handle=None;self.stdin=self.stdout=self.stderr=None
        children=[];parents=[];streams=[]
        try:
            for index in range(3):
                if devnull:
                    fd=os.open(os.devnull,os.O_RDONLY if index==0 else os.O_WRONLY);handle=msvcrt.get_osfhandle(fd)
                    children.append((handle,fd));parents.append(None)
                else:
                    read,write=_winapi.CreatePipe(None,0)
                    child,parent=(read,write) if index==0 else (write,read)
                    children.append((child,None));parents.append(parent)
            for handle,_ in children:os.set_handle_inheritable(handle,True)
            startup=subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESTDHANDLES,
                hStdInput=children[0][0],hStdOutput=children[1][0],hStdError=children[2][0],lpAttributeList={"handle_list":[x[0] for x in children]})
            hp,ht,pid,tid=_winapi.CreateProcess(args[0],subprocess.list2cmdline(args),None,None,True,0x4|0x08000000,env,cwd,startup)
            self._handle=hp;self.pid=pid
            try:
                if not job.api.AssignProcessToJobObject(job.handle,int(hp)):raise OwnershipUnknown("host_job_assignment")
                self.birth=birth(pid)
                if self.birth["state"]!="running":raise OwnershipUnknown("host_child_birth")
                if job.api.ResumeThread(int(ht))==0xffffffff:raise OwnershipUnknown("host_child_resume")
            except BaseException:
                job.api.TerminateProcess(int(hp),1);job.api.WaitForSingleObject(int(hp),2000);raise
            finally:_winapi.CloseHandle(ht)
            if not devnull:
                for index,handle in enumerate(parents):
                    fd=msvcrt.open_osfhandle(handle,os.O_BINARY|(os.O_WRONLY if index==0 else os.O_RDONLY))
                    streams.append(os.fdopen(fd,"wb" if index==0 else "rb",buffering=0));parents[index]=None
                self.stdin,self.stdout,self.stderr=streams
        except BaseException:
            for stream in streams:stream.close()
            self.close();raise
        finally:
            for handle,fd in children:
                if fd is not None:os.close(fd)
                else:_winapi.CloseHandle(handle)
            for handle in parents:
                if handle is not None:_winapi.CloseHandle(handle)
    def poll(self):
        if self._handle is None:raise OwnershipUnknown("child_handle_closed")
        if _winapi.WaitForSingleObject(self._handle,0)==258:return None
        return _winapi.GetExitCodeProcess(self._handle)
    def wait(self,timeout=None):
        milliseconds=0xffffffff if timeout is None else max(0,int(timeout*1000))
        if _winapi.WaitForSingleObject(self._handle,milliseconds)==258:raise subprocess.TimeoutExpired(self.args,timeout)
        return _winapi.GetExitCodeProcess(self._handle)
    def terminate(self):
        if self.poll() is None:_winapi.TerminateProcess(self._handle,1)
    kill=terminate
    def communicate(self,timeout=2):
        output=[bytearray(),bytearray()];errors=[]
        def reader(stream,index):
            try:
                while True:
                    block=stream.read(4096)
                    if not block:break
                    output[index].extend(block)
                    if len(output[index])>(65536 if index==0 else 8192):raise OwnershipUnknown("host_cli_output_limit")
            except Exception as error:errors.append(error)
        threads=[threading.Thread(target=reader,args=(stream,i),daemon=False) for i,stream in enumerate((self.stdout,self.stderr))]
        for thread in threads:thread.start()
        self.stdin.close()
        try:self.wait(timeout)
        except subprocess.TimeoutExpired:
            self.terminate();self.wait(2)
            for thread in threads:thread.join(2)
            raise
        for thread in threads:thread.join(2)
        if errors or any(thread.is_alive() for thread in threads):raise OwnershipUnknown("host_cli_pipe_unconfirmed")
        return bytes(output[0]),bytes(output[1])
    def close(self):
        for stream in (self.stdin,self.stdout,self.stderr):
            if stream and not stream.closed:stream.close()
        if self._handle is not None:_winapi.CloseHandle(self._handle);self._handle=None
