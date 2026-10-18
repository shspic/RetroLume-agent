"""Read-only preservation/termination confirmation; no business connection/action."""
from __future__ import annotations
import ctypes
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task100.control import CID,EVIDENCE,Ledger,atomic_json,process_identity,utc,validate_container
from app.worker.windows_job import _kernel,_BASIC_ACCOUNTING,JOB_OBJECT_QUERY,JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION_CLASS

begun=time.monotonic();facts=[]
try:
    result=subprocess.run(['docker','inspect',CID],capture_output=True,encoding='utf-8',timeout=10)
    if result.returncode:raise RuntimeError('exact Docker inspect unavailable')
    container=json.loads(result.stdout)[0];validate_container(container)
    facts.append({'action':'read_exact_container','id':CID,'state':container['State'],'mounts':container['Mounts']})
    assert container['State']['Running'] is False and container['State']['Pid']==0
    for port in (18100,55442):
        with socket.socket() as sock:
            sock.settimeout(1);open_port=sock.connect_ex(('127.0.0.1',port))==0
        facts.append({'action':'listener_only_check_no_PG_protocol','port':port,'open':open_port});assert not open_port
    observations=EVIDENCE/'2026-10-05T103020.095611-0000-repair-combo/observations'
    identities=set();jobs=set()
    for path in observations.glob('*.json'):
        event=json.loads(path.read_text('utf-8'));value=event['value']
        if event['kind']=='sup_created':identities.add((value['pid'],value['created_100ns']))
        if event['kind']=='session_outcome':
            identities.add((value['pid'],value['worker_created_100ns']))
            identities.add((value['manager_pid'],value['manager_created_100ns']))
            jobs.add(value['job_name'])
    for pid,birth in sorted(identities):
        identity=process_identity(pid,birth);facts.append({'action':'owned_PID_birth_read_only',**identity})
        assert identity['state'] in ('absent','exited','reused')
    api=_kernel()
    for name in sorted(jobs):
        handle=api.OpenJobObjectW(JOB_OBJECT_QUERY,False,name)
        if not handle:
            error=ctypes.get_last_error();facts.append({'action':'owned_Job_query_only','name':name,'windows_error':error});assert error==2
        else:
            try:
                accounting=_BASIC_ACCOUNTING()
                assert api.QueryInformationJobObject(handle,JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION_CLASS,
                    ctypes.byref(accounting),ctypes.sizeof(accounting),None)
                facts.append({'action':'owned_Job_query_only','name':name,'active_processes':accounting.ActiveProcesses})
                assert accounting.ActiveProcesses==0
            finally:api.CloseHandle(handle)
    browser_probe="@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^chrome' -and $_.CommandLine -match 'playwright_chromiumdev_profile' } | Select-Object ProcessId,ParentProcessId,Name) | ConvertTo-Json -Compress"
    probe=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',browser_probe],capture_output=True,encoding='utf-8',timeout=10)
    assert probe.returncode==0
    browser_candidates=json.loads(probe.stdout) if probe.stdout.strip() else []
    facts.append({'action':'readonly_playwright_profile_process_candidates','candidates':browser_candidates})
    assert not browser_candidates
    status='pass'
except BaseException as exc:
    facts.append({'action':'read_only_confirmation_error','type':type(exc).__name__,'message':str(exc)})
    status='fail'
finally:
    elapsed=time.monotonic()-begun
    Ledger().charge('cleanup',elapsed,{'mode':'final_readonly_resource_confirmation_no_business_or_stop_action'})
    Ledger().checkpoint_active()
    atomic_json(EVIDENCE/'final-resource-read.json',{'at':utc(),'status':status,'elapsed':elapsed,'facts':facts,
        'data_deleted':False,'business_connections':0,'new_resources':0,'stop_actions':0})
    print(json.dumps({'status':status,'facts':len(facts),'elapsed':elapsed}))
sys.exit(0 if status=='pass' else 1)
