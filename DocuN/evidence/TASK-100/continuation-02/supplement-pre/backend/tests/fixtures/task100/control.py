"""续作02有限控制：账本、单调截止、资源及子进程，离线可独立核验。"""
from __future__ import annotations
import contextlib
import hashlib
import json
import math
import os
import subprocess
import time
from datetime import datetime,timezone
from pathlib import Path
from psycopg.conninfo import conninfo_to_dict,make_conninfo

ROOT=Path(__file__).resolve().parents[4]
BACKEND=ROOT/'backend'
EVIDENCE=ROOT/'DocuN/evidence/TASK-100/continuation-02'
LEDGER=EVIDENCE/'attempt-ledger.json'
PERMIT='TASK-100-continuation-02-20261004'
LIMITS={'real_entries':3,'container_starts':3,'app_starts':3,'sup_creates':24,'browser':2,'driver':3,'frontend_build':1}
TIME_LIMITS={'offline':1800,'real':3600,'cleanup':480,'active':21600}
CID='80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d'
IMAGE='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
NAME='/retrolume-task-100-g8-pg1'
VOLUME='retrolume-task-100-g8-pg1-data'
MAIN_DB='retrolume_task100_g8_main'
FAULT_DB='retrolume_task100_g8_fault'
ROLES=('retrolume_task100_admin','retrolume_task100_app','retrolume_task100_denied')

class ControlRefusal(RuntimeError): pass

def utc(): return datetime.now(timezone.utc).isoformat()

def atomic_json(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    pending=path.with_suffix(path.suffix+'.pending')
    with pending.open('w',encoding='utf-8') as file:
        json.dump(value,file,ensure_ascii=False,indent=2); file.flush(); os.fsync(file.fileno())
    os.replace(pending,path)

@contextlib.contextmanager
def file_lock(path):
    import msvcrt
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as file:
        file.seek(0); file.write(b'0'); file.flush(); file.seek(0)
        end=time.monotonic()+5
        while True:
            try: msvcrt.locking(file.fileno(),msvcrt.LK_NBLCK,1); break
            except OSError:
                if time.monotonic()>=end: raise ControlRefusal('ledger_lock_timeout')
                time.sleep(.02)
        try: yield
        finally: file.seek(0); msvcrt.locking(file.fileno(),msvcrt.LK_UNLCK,1)

class Ledger:
    def __init__(self,path=LEDGER): self.path=Path(path)
    def load(self):
        try: value=json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError,ValueError): raise ControlRefusal('ledger_missing_or_corrupt') from None
        if not isinstance(value,dict) or value.get('permit')!=PERMIT or value.get('limits')!=LIMITS or value.get('time_limits')!=TIME_LIMITS:
            raise ControlRefusal('ledger_identity_invalid')
        for domain,limits in (('counts',LIMITS),('seconds',TIME_LIMITS)):
            if set(value.get(domain,{}))!=set(limits): raise ControlRefusal('ledger_shape_invalid')
            for name,maximum in limits.items():
                n=value[domain][name]
                if type(n) not in (int,float) or not math.isfinite(n) or n<0 or domain=='counts' and type(n) is not int:
                    raise ControlRefusal('ledger_number_invalid')
                if n>maximum: raise ControlRefusal('ledger_over_limit')
        if not isinstance(value.get('events'),list): raise ControlRefusal('ledger_events_invalid')
        return value
    def initialize(self,preparation):
        if self.path.exists(): raise ControlRefusal('ledger_already_exists')
        atomic_json(self.path,{'permit':PERMIT,'limits':LIMITS,'time_limits':TIME_LIMITS,
            'counts':{k:0 for k in LIMITS},'seconds':{k:0 for k in TIME_LIMITS},
            'active_started_at':preparation['active_started_at'],'initial_read_upper_seconds':preparation.get('initial_unclocked_read_upper_seconds',120),
            'old_usage':{'initial':'旧许可已结束，真实入口至少9、漏计5.940秒，部分启动投入未知',
                'continuation_01':'旧许可已结束，真实入口4/4、start1、app1、SUP0、browser0、driver0、build2',
                'references':['DocuN/evidence/TASK-100/attempt-ledger.json','DocuN/evidence/TASK-100/continuation-01/attempt-ledger-continuation.json']},
            'events':[{'at':utc(),'event':'explicit_new_permit_initialization'}]})
    def update(self,fn):
        with file_lock(self.path.with_suffix('.lock')):
            value=self.load(); fn(value); atomic_json(self.path,value)
        return value
    def consume(self,name,detail=None):
        def mutate(value):
            if name not in LIMITS or value['counts'][name]>=LIMITS[name]: raise ControlRefusal('attempt_limit_'+name)
            value['counts'][name]+=1
            value['events'].append({'at':utc(),'event':'before_action','counter':name,'count':value['counts'][name],'detail':detail})
        return self.update(mutate)
    def charge(self,category,seconds,detail=None):
        def mutate(value):
            value['seconds'][category]+=seconds
            value['events'].append({'at':utc(),'event':'elapsed','category':category,'seconds':seconds,'detail':detail})
        return self.update(mutate)
    def note(self,event,detail):
        return self.update(lambda v:v['events'].append({'at':utc(),'event':event,'detail':detail}))

class Deadline:
    def __init__(self,seconds,clock=time.monotonic):
        self.clock=clock; self.end=clock()+seconds
    def timeout(self,stage):
        remaining=self.end-self.clock()
        if remaining<=0: raise ControlRefusal('monotonic_deadline')
        return min(float(stage),remaining)

def switched_dsn(dsn,dbname,user=None,password=None):
    if dbname not in (MAIN_DB,FAULT_DB,'postgres'): raise ControlRefusal('database_not_allowed')
    values=conninfo_to_dict(dsn)
    if values.get('host')!='127.0.0.1' or str(values.get('port'))!='55442': raise ControlRefusal('dsn_resource_not_allowed')
    values['dbname']=dbname
    if user is not None:
        if user not in ROLES: raise ControlRefusal('role_not_allowed')
        values['user']=user
    if password is not None: values['password']=password
    values['connect_timeout']='5'
    values['options']='-c statement_timeout=5000 -c lock_timeout=3000 -c idle_in_transaction_session_timeout=10000'
    return make_conninfo(**values)

def validate_container(fact, *, require_limits=True):
    host=fact['HostConfig']
    mount=fact.get('Mounts',[])
    if fact.get('Id')!=CID or fact.get('Name')!=NAME or fact.get('Image')!=IMAGE: raise ControlRefusal('container_identity')
    if len(mount)!=1 or mount[0].get('Type')!='volume' or mount[0].get('Name')!=VOLUME or mount[0].get('Destination')!='/var/lib/postgresql/data': raise ControlRefusal('container_mount')
    if host.get('Privileged') or host.get('CapAdd') or host.get('Devices') or host.get('NetworkMode') not in ('bridge','default') or host.get('RestartPolicy',{}).get('Name')!='no': raise ControlRefusal('container_privilege')
    if host.get('PortBindings')!={'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':'55442'}]}: raise ControlRefusal('container_port')
    if require_limits and (host.get('Memory')!=536870912 or host.get('NanoCpus')!=1000000000 or host.get('PidsLimit')!=128): raise ControlRefusal('container_limits')
    return True

def run_process(argv,deadline,stage,directory,*,env=None,cwd=BACKEND,stdin=None):
    """stdout/stderr 直接保留完整原件；异常也关闭已创建的实际进程。"""
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=False)
    start=time.monotonic(); began=utc(); process=None
    try:
        timeout=deadline.timeout(stage)
        with (directory/'stdout.txt').open('wb') as out,(directory/'stderr.txt').open('wb') as err:
            process=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,stdout=out,stderr=err)
            try: process.communicate(input=stdin,timeout=timeout)
            except subprocess.TimeoutExpired:
                stop_owned_tree(process)
                status='timeout'
            else: status='pass' if process.returncode==0 else 'fail'
        counts={}
        if '-m' in argv and 'unittest' in argv:
            import re
            raw=(directory/'stderr.txt').read_text(encoding='utf-8',errors='replace')
            matched=re.search(r'Ran (\d+) tests?',raw)
            skips=len(re.findall(r'\.\.\. skipped ',raw))
            counts={'tests':int(matched.group(1)) if matched else 0,'skipped':skips}
            if status=='pass' and (not matched or skips):status='fail'
        fact={'status':status,**counts,'exit_code':process.returncode,'started_at':began,'ended_at':utc(),'elapsed':time.monotonic()-start,'timeout':timeout,'pid':process.pid}
    except BaseException as exc:
        fact={'status':'started_failed' if process else 'not_run','error_type':type(exc).__name__,'started_at':began,'ended_at':utc(),'elapsed':time.monotonic()-start}
    finally:
        if process is not None and process.poll() is None:
            try: stop_owned_tree(process)
            except BaseException as exc:
                fact['status']='started_failed';fact['cleanup_error']=type(exc).__name__
    atomic_json(directory/'result.json',fact)
    return fact

def stop_owned_tree(process):
    # 只接收本入口 Popen 返回的对象；从不按名称寻找或关闭其他进程。
    if os.name=='nt' and type(process.pid) is int and process.pid>0:
        subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True,timeout=10)
    if process.poll() is None:process.kill()
    process.wait(timeout=10)

def process_identity(pid,created_100ns):
    """只读核 Windows PID 与创建时点；PID 复用不冒充本卡残留。"""
    import ctypes
    from ctypes import wintypes
    api=ctypes.WinDLL('kernel32',use_last_error=True)
    api.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];api.OpenProcess.restype=wintypes.HANDLE
    api.CloseHandle.argtypes=[wintypes.HANDLE];api.CloseHandle.restype=wintypes.BOOL
    api.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(wintypes.FILETIME)]*4)]
    api.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
    handle=api.OpenProcess(0x1000|0x100000,False,pid)
    if not handle:
        error=ctypes.get_last_error()
        return {'pid':pid,'state':'absent' if error==87 else 'unconfirmed','windows_error':error}
    try:
        files=[wintypes.FILETIME() for _ in range(4)];code=wintypes.DWORD()
        if not api.GetProcessTimes(handle,*[ctypes.byref(f) for f in files]) or not api.GetExitCodeProcess(handle,ctypes.byref(code)):
            return {'pid':pid,'state':'unconfirmed','windows_error':ctypes.get_last_error()}
        created=(files[0].dwHighDateTime<<32)|files[0].dwLowDateTime
        return {'pid':pid,'created_100ns':created,'expected_created_100ns':created_100ns,
                'state':'reused' if created!=created_100ns else 'alive' if code.value==259 else 'exited','exit_code':code.value}
    finally:api.CloseHandle(handle)

def hash_files(paths):
    return {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file()}

def aggregate(segments):
    return 'pass' if segments and all(s['status']=='pass' for s in segments) else 'fail'
