"""TASK-120 merged runtime entry. Bounded, serial, exact ownership only."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import threading
from uuid import uuid4

PG_TRANSITION=threading.Lock()
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from tests.fixtures.task120.lifecycle import BoundedResources
from app.preview.process import birth
from tests.fixtures.task120.control_job import NamedJob,JobOpenError


def cleanup_job(identity):
    try:job=NamedJob.open_existing(identity,1)
    except JobOpenError as exc:
        if getattr(exc,'code',None)==2 or getattr(exc,'winerror',None)==2:return {'job_absent':True}
        raise
    try:
        job.terminate()
        empty=job.wait_empty_until(time.monotonic_ns()+5_000_000_000)
        if not empty:raise RuntimeError('root_job_not_empty')
        return {'job':job.name,'active_processes':job.active_processes(),'tree_empty':True}
    finally:job.close()


def watchdog(identity):
    # Independent of the owner's event loop and product threads; not a Windows
    # service. Host/process-tree loss remains an explicit unknown on resumption.
    slot=next(x for x in r.state()['roots'] if x['identity']==identity)
    parent=slot['owner'];low=0
    while time.monotonic_ns()<slot['cleanup_deadline_ns']:
        budget=r.state()
        if budget.get('active_root')!=slot['id']:return 0
        actual=birth(parent['pid'])
        if actual['state']!='running' or actual.get('birth')!=parent['birth']:
            proof={'reason':'owner_exit','job':None,'pg':None}
            try:proof['job']=cleanup_job(identity)
            except BaseException as exc:proof['job_error']=type(exc).__name__
            try:proof['pg']=r.stop_pg()
            except BaseException as exc:proof['pg_error']=type(exc).__name__
            r.write(r.EVIDENCE/f"root-{slot['id']:02d}-orphan-stop.json",proof)
            return 0
        time.sleep(.5)
    # A dead/stuck owner cannot extend the original cleanup deadline.
    try:cleanup_job(identity)
    finally:r.stop_pg()
    return 0


def hashes(root_id):
    files=[]
    for folder,pattern in (('backend/app','*.py'),('backend/tests/fixtures/task120','*.py'),('frontend/src','*.tsx'),('frontend/src','*.ts'),('frontend/dist','*')):
        for path in sorted((ROOT/folder).rglob(pattern)):
            if path.is_file():files.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    files.append({'path':str(Path(__file__).resolve().relative_to(ROOT)),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    r.write(r.EVIDENCE/f'root-{root_id:02d}-as-run.json',{'utc':r.utc(),'files':files})


def execute(phase,seconds,plan_path):
    before=r.state()
    if before.get('active_root') is not None or before.get('active_command') is not None:raise RuntimeError('previous_root_or_command_unreconciled')
    now=datetime.now(timezone.utc)
    # Calendar gaps, approval waits and user interruptions are never CPU/wall.
    # Retain the measured receipts plus the separately declared metadata ceiling.
    upper=(before['pre_controller_wall_upper_seconds']+before.get('controlled_command_wall_seconds',0)
        +before.get('runtime_command_wall_seconds',0)+before.get('unwrapped_metadata_wall_reserved_seconds',0)
        +before.get('continuation_metadata_uncertainty_reserved_seconds',0))
    calendar=datetime.fromisoformat(before['calendar_deadline_utc'].replace('Z','+00:00'))
    remaining=min((calendar-now).total_seconds()-1800,before['command_wall_cap_seconds']-upper,
                  before['runtime_holding_union_cap_seconds']-before.get('runtime_holding_union_seconds',0),1800)
    if remaining<150:raise RuntimeError('root_time_margin_exhausted')
    root_id=r.count('roots');identity=str(uuid4());start=time.monotonic_ns()
    cleanup_deadline=start+int(remaining*1e9)
    business_deadline=cleanup_deadline-120_000_000_000
    slot={'id':root_id,'identity':identity,'phase':phase,'start_utc':r.utc(),'start_ns':start,
        'business_deadline_ns':business_deadline,'cleanup_deadline_ns':cleanup_deadline,
        'clock':'host time.monotonic_ns/QPC within same running host','owner':birth(os.getpid()),'counts_at_entry':r.state()['counts'].copy(),'permit_id':before['current_permit_id'],'plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest()}
    slot['owner']['pid']=os.getpid()
    def begin(value):
        value.setdefault('roots',[]).append(slot);value['active_root']=root_id
    r.update(begin)
    r.event('root_entered',root=root_id,phase=phase)
    hashes(root_id)
    monitor=None;job=None;code=1;report=None
    started=time.monotonic();watcher=None
    try:
        watcher=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--watchdog',identity],
            cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
        r.event('watchdog_started',root=root_id,watchdog={**birth(watcher.pid),'pid':watcher.pid})
        monitor=BoundedResources(deadline=business_deadline/1e9)
        monitor.monitor_memory(r.available_memory,every=2,minimum=256*1024**2)
        with monitor:
            monitor.register('pg',stop_existing_pg,priority=0)
            # Register ownership before creating the suspended root process.
            monitor.register('browser-api-native-test-job',lambda:cleanup_job(identity) if job else {'created':False},priority=60)
            monitor.check();r.choose_ports();monitor.check();start_existing_pg();monitor.check()
            job=r.root_job(identity)
            child_env=r.public_environment()
            child_env.update(PYTHONPATH=str(ROOT/'backend')+os.pathsep+str(ROOT/'backend/.venv/Lib/site-packages'),PYTHONIOENCODING='utf-8',
                RETROLUME_TASK120_ROOT_ID=str(root_id),RETROLUME_TASK120_TESTONLY='TASK-120-Q-PREP-IMPLEMENTATION-20261018',RETROLUME_TASK120_PLAN=str(plan_path),RETROLUME_TASK120_CONTINUATION=before['current_permit_id'])
            # CreateProcess inherits this process environment. Replace only the
            # controller's own mapping; never enumerate or print user env.
            os.environ.clear();os.environ.update(child_env)
            job.spawn_suspended([sys._base_executable,'-m','tests.fixtures.task120.run',phase],cwd=str(ROOT/'backend'))
            r.event('root_child_started',root=root_id,pid=job.pid,birth_100ns=job.process_creation_time_100ns(),job=job.name)
            job.resume()
            subdeadline=business_deadline if phase=='queue' else min(business_deadline,time.monotonic_ns()+int(seconds*1e9))
            while job.active_processes() and time.monotonic_ns()<subdeadline and not monitor.closing:time.sleep(.1)
            if job.active_processes():
                r.event('root_subbatch_timeout_or_pressure',root=root_id)
                job.terminate()
                if not job.wait_empty_until(time.monotonic_ns()+5_000_000_000):raise RuntimeError('subbatch_tree_unknown')
            code=job.primary_exit_code()
    except BaseException as exc:
        import traceback
        r.event('root_exception',root=root_id,error_type=type(exc).__name__,safe_code=str(exc) if type(exc) is RuntimeError else None,
            winerror=getattr(exc,'winerror',None),frames=[{'file':str(x.filename).replace(str(ROOT),'PROJECT'),'line':x.lineno,'function':x.name} for x in traceback.extract_tb(exc.__traceback__)])
        code=1
    finally:
        if monitor is not None:report=monitor.close('normal_exit' if code==0 else 'exception')
        else:
            try:report={'pg':r.stop_pg(),'all_confirmed':True}
            except BaseException as exc:report={'all_confirmed':False,'error_type':type(exc).__name__}
        if job is not None:job.close()
        ports={}
        # Settlement after any in-flight start is complete, including pressure.
        try:late_pg=stop_existing_pg()
        except BaseException as exc:
            report['all_confirmed']=False;report['settled_pg_error']=type(exc).__name__
        else:report['settled_pg_after_start']=late_pg
        for name,port in r.state().get('ports',{}).items():
            with socket.socket() as probe:
                probe.settimeout(.3);ports[name]={'port':port,'listening':probe.connect_ex(('127.0.0.1',port))==0}
        port_until=time.monotonic()+5
        while any(p['listening'] for p in ports.values()) and time.monotonic()<port_until:
            time.sleep(.1)
            for name,port in r.state().get('ports',{}).items():
                with socket.socket() as probe:
                    probe.settimeout(.2);ports[name]={'port':port,'listening':probe.connect_ex(('127.0.0.1',port))==0}
        final={'root':root_id,'phase':phase,'exit_code':code,'utc':r.utc(),'wall_seconds':time.monotonic()-started,
            'root_elapsed_seconds':(time.monotonic_ns()-start)/1e9,'cleanup':report,'ports':ports,'old_six_realtime_observation':'not_claimed'}
        holding_start=r.state()['roots'][-1].get('holding_started_ns')
        final['runtime_holding_union_seconds']=(time.monotonic_ns()-holding_start)/1e9 if holding_start is not None else 0
        r.write(r.EVIDENCE/f'root-{root_id:02d}-stop.json',final)
        def finish(value):
            value['active_root']=None if report and report.get('all_confirmed') and not any(p['listening'] for p in ports.values()) else root_id
            value['needs_reconcile']=value['active_root'] is not None
            value['runtime_holding_union_seconds']=value.get('runtime_holding_union_seconds',0)+final['runtime_holding_union_seconds']
            value['runtime_command_wall_seconds']=value.get('runtime_command_wall_seconds',0)+final['wall_seconds']
            value['roots'][-1]['result']=final
            if code:value['failures'].append({'root':root_id,'phase':phase,'receipt':f'root-{root_id:02d}-stop.json'})
        r.update(finish)
        if watcher is not None:
            try:watcher.wait(timeout=3)
            except subprocess.TimeoutExpired:
                watcher.terminate();watcher.wait(timeout=3)
        print(json.dumps(final,ensure_ascii=False))
    return code if report and report.get('all_confirmed',False) else 1


def start_existing_pg():
    with PG_TRANSITION:
        value=r.state();registry=value['pg_registry']
        if not value.get('no_new_container_or_volume_create'):raise RuntimeError('continuation_create_guard_missing')
        actual=r.owned(r.container(),registry)
        if actual['state']['Running']:raise RuntimeError('previous_pg_still_running')
        r.memory_gate('pg');r.count('pg_starts')
        r.update(lambda state:state['roots'][-1].update(holding_started_ns=time.monotonic_ns()))
        r.docker(['container','start',registry['Id']])
        r.event('pg_started',Id=registry['Id'],create_forbidden=True)


def stop_existing_pg():
    # A pressure callback waits for the finite Docker start invocation to
    # return. It cannot inspect the old stopped state and then miss its start.
    with PG_TRANSITION:return r.stop_pg()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--plan');parser.add_argument('--watchdog')
    args=parser.parse_args()
    if args.watchdog:raise SystemExit(watchdog(args.watchdog))
    if not args.plan:raise SystemExit('finite prewritten plan required')
    path=Path(args.plan).resolve()
    if path.parent!=Path(__file__).resolve().parent:raise SystemExit('plan outside continuation evidence')
    from tests.fixtures.task120.queued import read_plan
    plan=read_plan(path)
    if plan['root_id']!=r.state()['counts']['roots']+1:raise SystemExit('plan root identity changed')
    # Reject an oversized frozen queue before acquiring PG; no interactive tail.
    if sum(x['seconds'] for x in plan['stages'])>1680:raise SystemExit('finite plan exceeds root business window')
    raise SystemExit(execute('queue',300,path))
