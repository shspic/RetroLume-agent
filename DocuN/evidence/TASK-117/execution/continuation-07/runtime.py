"""只托管S08合成HTTP与浏览器；独立Job闭包、截止、内存与父退出检查。"""
import ctypes
from ctypes import wintypes
from datetime import datetime,timedelta,timezone
import json
import os
import socket
import subprocess
import sys
import time
from control import N,E,ROOT,K,PERMIT,Job,birth,available_mib,sample,state,segment,guard,limits,count,write,event,failure

def port_free():
    with socket.socket() as stream:
        stream.settimeout(.5)
        return stream.connect_ex(('127.0.0.1',18119))!=0

def identities(job):
    class List(ctypes.Structure):_fields_=[('assigned',wintypes.DWORD),('returned',wintypes.DWORD),('pids',ctypes.c_size_t*512)]
    data=List();K.QueryInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.c_void_p]
    if not K.QueryInformationJobObject(job.handle,3,ctypes.byref(data),ctypes.sizeof(data),None):raise ctypes.WinError(ctypes.get_last_error())
    rows=[];K.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];K.OpenProcess.restype=wintypes.HANDLE
    for pid in list(data.pids)[:data.returned]:
        handle=K.OpenProcess(0x1000|0x100000,False,pid)
        if handle:
            try:rows.append({'pid':pid,'birth_filetime':birth(handle)})
            finally:K.CloseHandle(handle)
    return rows

def main():
    b=guard();assert b['active_root'] is None,'已有在途根，不能延长'
    assert port_free(),'18119已有监听，不动其它进程或换端口'
    memory=available_mib()
    if memory<768:failure('S08_browser_memory_gate',f'{memory:.2f}MiB <768，未启动');return 2
    started=sample();remaining=min(1500,limits(b,started))
    resume=int(sys.argv[2]) if len(sys.argv)==3 and sys.argv[1]=='--resume-root' else None
    if resume is None:
        count('roots');b=state();root_id=b['counts']['roots'];assert 25<=root_id<=27
        root={'id':root_id,'segment':PERMIT,'kind':'S08_closed_loopback_browser','start_utc':started['utc'],
          'start_mono_ns':started['mono_ns'],'business_deadline_mono_ns':started['mono_ns']+int(remaining*1e9),
          'business_deadline_utc':(datetime.fromisoformat(started['utc'])+timedelta(seconds=remaining)).isoformat(),
          'cleanup_deadline_utc':(datetime.fromisoformat(started['utc'])+timedelta(seconds=remaining+300)).isoformat(),
          'status':'active','initial_available_mib':memory,'attempt_number':1}
        b['roots'].append(root)
    else:
        root_id=resume;root=next(r for r in b['roots'] if r['id']==resume)
        assert root['segment']==PERMIT and root['status']=='closed' and root['stop']['child_exit_code']!=0
        assert not root['stop']['same_birth_alive'] and root['stop']['18119_no_listener']
        remaining=min(remaining,(root['business_deadline_mono_ns']-started['mono_ns'])/1e9)
        assert remaining>0,'原根截止已到，不能续期'
        root.setdefault('earlier_attempts',[]).append({'attempt_number':root.get('attempt_number',1),'stop':root['stop'],'evidence_directory':root['evidence_directory']})
        root['attempt_number']=root.get('attempt_number',1)+1;root['status']='active'
        event('S08_same_root_evidence_based_resume',root=root_id,attempt=root['attempt_number'],original_deadline=root['business_deadline_utc'],reason='已定位Playwright默认缓存指到sandbox子目录；明确使用现有缓存，不安装/换浏览器版本')
    b['active_root']=root_id;segment(b)['holding_start_mono_ns']=started['mono_ns'];write(E/'budget.json',b)
    directory=N/f'root-{root_id}'
    if root['attempt_number']>1:directory=directory/f"attempt-{root['attempt_number']:02d}"
    directory.mkdir(exist_ok=False)
    write(directory/'spec.json',{'root':root,'permit':PERMIT,'evidence':str(directory),'project':str(ROOT),'port':18119,
        'budget':str(E/'budget.json'),'profile':str(directory/'browser-profile'),'Q':'FROZEN'})
    env=dict(os.environ);env.update(S08_SPEC=str(directory/'spec.json'),TEMP=str(directory),TMP=str(directory),PLAYWRIGHT_BROWSERS_PATH='C:/Users/28432/AppData/Local/ms-playwright')
    job=Job();child=None;registered={};samples=[];reason='normal';parent=None
    K.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];K.OpenProcess.restype=wintypes.HANDLE
    K.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
    parent=K.OpenProcess(0x1000|0x100000,False,os.getppid())
    try:
        with (directory/'driver.log').open('wb') as output:
            child=job.spawn(['C:/Program Files/nodejs/node.exe',str(ROOT/'frontend/tests/step018-s08.mjs')],cwd=ROOT,env=env,
                            stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT)
            write(directory/'owned.json',{'controller':{'pid':os.getpid(),'birth_filetime':birth(K.GetCurrentProcess())},
                'node':{'pid':child.pid,'birth_filetime':birth(child._handle)},'kill_on_job_close':True,'root':root})
            low=0
            while child.poll() is None:
                clock=sample();mib=available_mib();rows=identities(job)
                for row in rows:registered[(row['pid'],row['birth_filetime'])]=row
                samples.append({'sample':clock,'available_mib':mib,'owned':rows})
                low=low+1 if mib<256 else 0
                parent_code=wintypes.DWORD(259)
                if parent:K.GetExitCodeProcess(parent,ctypes.byref(parent_code))
                if low>=2:reason='pressure_two_samples';break
                if parent_code.value!=259:reason='parent_exit';break
                if clock['mono_ns']>=root['business_deadline_mono_ns']:reason='original_root_deadline';break
                time.sleep(min(2,max(.01,(root['business_deadline_mono_ns']-clock['mono_ns'])/1e9)))
            if reason!='normal':
                try:child.stdin.write(b'STOP\n');child.stdin.flush()
                except (BrokenPipeError,OSError):pass
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:pass
    except BaseException as exc:
        reason='controller_exception:'+type(exc).__name__;failure('S08_runtime_controller',str(exc));raise
    finally:
        job.close()
        if child is not None:
            if child.stdin:child.stdin.close()
            child.wait(timeout=10)
        if parent:K.CloseHandle(parent)
        ended=sample();seconds=(ended['mono_ns']-started['mono_ns'])/1e9
        write(directory/'observations.json',samples)
        alive=[]
        for row in registered.values():
            handle=K.OpenProcess(0x1000|0x100000,False,row['pid'])
            if handle:
                try:
                    code=wintypes.DWORD();K.GetExitCodeProcess(handle,ctypes.byref(code))
                    if birth(handle)==row['birth_filetime'] and code.value==259:alive.append(row)
                finally:K.CloseHandle(handle)
        stopped={'sample':ended,'reason':reason,'registered_pid_births':list(registered.values()),'same_birth_alive':alive,
                 '18119_no_listener':port_free(),'child_exit_code':child.returncode if child else None,
                 'holding_union_upper_seconds':seconds,'old_PG_observed':False,'Job_handle_closed':True}
        write(directory/'stop.json',stopped)
        b=state();s=segment(b);entry=next(r for r in b['roots'] if r['id']==root_id)
        entry.update(status='closed',stop=stopped,evidence_directory=str(directory))
        b['active_root']=None;s['holding_start_mono_ns']=None;s['last_clock']=ended
        b['runtime_intervals'].append({'segment':PERMIT,'root':root_id,'start_utc':started['utc'],'end_utc':ended['utc'],
            'seconds':seconds,'basis':'自有driver全寿命上界覆盖server/browser并集，启动与清场几毫秒也保守保留'})
        s['offline_process_run_seconds']+=seconds
        write(E/'budget.json',b);event('S08_runtime_closed',root=root_id,seconds=seconds,reason=reason,stop=stopped)
        if alive or not stopped['18119_no_listener'] or child is None or child.returncode:
            failure('S08_browser_root_'+str(root_id),json.dumps(stopped,ensure_ascii=False))
    return 0 if reason=='normal' and child.returncode==0 and not alive and stopped['18119_no_listener'] else 1

if __name__=='__main__':raise SystemExit(main())
