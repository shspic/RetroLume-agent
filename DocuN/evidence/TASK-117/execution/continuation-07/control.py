"""S08独立许可、同宿主时钟域及准确自有进程闭包；不调用旧控制器。"""
from pathlib import Path
from datetime import datetime, timezone
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid

N=Path(__file__).resolve().parent; E=N.parent; ROOT=E.parents[3]
PERMIT='TASK-117-STEP018-AUDIT-REPAIR-S08-20261017'
INSTANCE=str(uuid.uuid4())
K=ctypes.WinDLL('kernel32',use_last_error=True)
K.GetTickCount64.restype=ctypes.c_ulonglong

def sample():
    now=datetime.now(timezone.utc)
    uptime=K.GetTickCount64()
    return {'utc':now.isoformat(),'mono_ns':time.monotonic_ns(),'boot_epoch_seconds':now.timestamp()-uptime/1000,'instance':INSTANCE,'pid':os.getpid()}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def state():return json.loads((E/'budget.json').read_text(encoding='utf-8'))
def segment(b):
    if b['active_segment']!=PERMIT:raise RuntimeError('S08许可身份不符')
    return next(s for s in b['segments'] if s['permit']==PERMIT)
def event(kind,**fields):
    with (E/'events.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'kind':kind,**sample(),**fields},ensure_ascii=False)+'\n')
def limits(b,now,*,allow_running=False):
    s=segment(b)
    if s['status']!='active':raise RuntimeError('S08未激活')
    old=s['last_clock']
    if abs(old['boot_epoch_seconds']-now['boot_epoch_seconds'])>2 or now['mono_ns']<old['mono_ns']:raise RuntimeError('S08时钟域不可续用，先核资源再重锚')
    if datetime.fromisoformat(now['utc']).timestamp()<datetime.fromisoformat(old['utc']).timestamp()-2:raise RuntimeError('S08 UTC倒退')
    calendar=(datetime.fromisoformat(s['calendar_deadline_utc'])-datetime.fromisoformat(now['utc'])).total_seconds()-1200
    external=N/'tool-receipts.json'
    upper=json.loads(external.read_text(encoding='utf-8'))['command_wall_upper_seconds'] if external.exists() else 10.7
    offline=3600-s['offline_process_run_seconds']-upper
    active=s.get('offline_process_run_active')
    if active and not allow_running:raise RuntimeError('S08上一命令未结束')
    if active:offline-=(now['mono_ns']-active['start_mono_ns'])/1e9
    held=sum(x['seconds'] for x in b['runtime_intervals'] if x.get('segment')==PERMIT)
    if s.get('holding_start_mono_ns') is not None:held+=(now['mono_ns']-s['holding_start_mono_ns'])/1e9
    remaining=[calendar,offline,3600-held]
    if b['active_root'] is not None:
        root=next(r for r in b['roots'] if r['id']==b['active_root'])
        if root.get('segment')!=PERMIT:raise RuntimeError('S08不能沿用旧根')
        remaining.append((root['business_deadline_mono_ns']-now['mono_ns'])/1e9)
    if min(remaining)<=0:raise RuntimeError('S08日历/进程/持有/根硬门关闭')
    return min(remaining)
def guard():
    b=state();now=sample();limits(b,now);segment(b)['last_clock']=now;write(E/'budget.json',b);return b
def check_count(b,name,number=1):
    s=segment(b)
    if type(number) is not int or number<1 or name not in s['cumulative_caps'] or b['counts'][name]+number>s['cumulative_caps'][name]:raise RuntimeError('S08累计次数门关闭 '+name)
def count(name,number=1):
    b=guard();check_count(b,name,number)
    b['counts'][name]+=number;write(E/'budget.json',b);event('S08_attempt_reserved',counter=name,total=b['counts'][name])
def pre(relative,defect):
    guard();p=(ROOT/relative).resolve();p.relative_to(ROOT)
    index=N/'changes.json';rows=json.loads(index.read_text(encoding='utf-8')) if index.exists() else {}
    if relative not in rows:
        raw=p.read_bytes() if p.exists() else b'';backup=N/'preimages'/relative;backup.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():backup.write_bytes(raw)
        rows[relative]={'exists':p.exists(),'bytes':len(raw),'sha256':sha(raw) if p.exists() else None,'backup':str(backup.relative_to(ROOT)) if p.exists() else None,'D':defect,'sample':sample()};write(index,rows)
def failure(label,error):
    b=state();row={'label':label,'reason':str(error),'segment':PERMIT,**sample()};b['failures'].append(row);write(E/'budget.json',b);event('failure',**row)

class Job:
    """句柄关闭即终止本次准确子树，子进程先挂起再加入，避免逃逸窗口。"""
    def __init__(self):
        class Basic(ctypes.Structure):_fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
        class IO(ctypes.Structure):_fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
        class Extended(ctypes.Structure):_fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
        K.CreateJobObjectW.restype=wintypes.HANDLE;K.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR]
        K.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
        K.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
        K.CloseHandle.argtypes=[wintypes.HANDLE]
        self.handle=K.CreateJobObjectW(None,None)
        info=Extended();info.BasicLimitInformation.LimitFlags=0x2000
        if not self.handle or not K.SetInformationJobObject(self.handle,9,ctypes.byref(info),ctypes.sizeof(info)):raise ctypes.WinError(ctypes.get_last_error())
    def spawn(self,command,**kwargs):
        child=subprocess.Popen(command,creationflags=0x00000004|0x08000000,**kwargs)
        if not K.AssignProcessToJobObject(self.handle,wintypes.HANDLE(int(child._handle))):
            child.kill();child.wait();raise ctypes.WinError(ctypes.get_last_error())
        resume=ctypes.WinDLL('ntdll').NtResumeProcess;resume.argtypes=[wintypes.HANDLE];resume.restype=ctypes.c_long
        if resume(wintypes.HANDLE(int(child._handle)))!=0:
            child.kill();child.wait();raise RuntimeError('准确子进程无法恢复')
        return child
    def close(self):
        if self.handle:K.CloseHandle(self.handle);self.handle=None
def birth(handle):
    K.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(wintypes.FILETIME)]*4)]
    values=[wintypes.FILETIME() for _ in range(4)]
    if not K.GetProcessTimes(wintypes.HANDLE(int(handle)),*(ctypes.byref(x) for x in values)):raise ctypes.WinError(ctypes.get_last_error())
    return (values[0].dwHighDateTime<<32)|values[0].dwLowDateTime
def available_mib():
    class Memory(ctypes.Structure):_fields_=[('length',wintypes.DWORD),('load',wintypes.DWORD),*[(x,ctypes.c_ulonglong) for x in ('total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','avail_extended')]]
    memory=Memory();memory.length=ctypes.sizeof(memory)
    if not K.GlobalMemoryStatusEx(ctypes.byref(memory)):raise ctypes.WinError(ctypes.get_last_error())
    return memory.avail_phys/1024**2
def run(command,label,*,timeout=120,cwd=None):
    b=guard();s=segment(b);start=sample();timeout=min(timeout,limits(b,start))
    env=dict(os.environ);temp=N/'temp';temp.mkdir(exist_ok=True)
    env.update(TEMP=str(temp),TMP=str(temp),S08_EVIDENCE=str(N),PYTHONPATH=os.pathsep.join([str(ROOT/'backend'),str(ROOT/'backend/.venv/Lib/site-packages'),str(ROOT/'backend/tests')]))
    s['offline_process_run_active']={'start_mono_ns':start['mono_ns'],'label':label,'timeout':timeout};write(E/'budget.json',b)
    job=Job();child=None
    try:
        child=job.spawn(command,cwd=cwd or ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
        write(N/(label+'-pid.json'),{'pid':child.pid,'birth_filetime':birth(child._handle),'deadline_utc':datetime.fromtimestamp(datetime.now(timezone.utc).timestamp()+timeout,timezone.utc).isoformat(),'command':command})
        output,_=child.communicate(timeout=timeout);(N/(label+'.log')).write_bytes(output)
        if child.returncode:failure(label,'退出码'+str(child.returncode))
        return child.returncode
    except subprocess.TimeoutExpired as error:
        job.close();output,_=child.communicate(timeout=10);(N/(label+'.log')).write_bytes(output);failure(label,'超时，关闭准确Job子树');raise
    finally:
        job.close()
        if child is not None and child.poll() is None:child.wait(timeout=10)
        end=sample();b=state();s=segment(b);seconds=(end['mono_ns']-start['mono_ns'])/1e9
        s['offline_process_run_seconds']+=seconds;s['offline_process_run_active']=None;s['last_clock']=end;write(E/'budget.json',b);event('S08_offline_process_end',label=label,seconds=seconds)
def py():return [sys._base_executable,'-X','utf8']

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('label');parser.add_argument('--timeout',type=float,default=120);parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args();command=args.command
    if command and command[0]=='--':command=command[1:]
    raise SystemExit(run(command,args.label,timeout=args.timeout))
