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
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from tests.fixtures.task120.lifecycle import BoundedResources
from app.preview.process import birth
from app.worker.windows_job import NamedJob,JobOpenError


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
    r.write(r.EVIDENCE/f'root-{root_id:02d}-as-run.json',{'utc':r.utc(),'files':files})


def execute(phase,seconds):
    before=r.state()
    if before.get('active_root') is not None or before.get('active_command') is not None:raise RuntimeError('previous_root_or_command_unreconciled')
    now=datetime.now(timezone.utc)
    # Calendar gaps, approval waits and user interruptions are never CPU/wall.
    # Retain the measured receipts plus the separately declared metadata ceiling.
    upper=(before['pre_controller_wall_upper_seconds']+before.get('controlled_command_wall_seconds',0)
        +before.get('runtime_command_wall_seconds',0)+before.get('unwrapped_metadata_wall_reserved_seconds',0))
    calendar=datetime.fromisoformat(before['calendar_deadline_utc'].replace('Z','+00:00'))
    remaining=min((calendar-now).total_seconds()-1800,before['command_wall_cap_seconds']-upper,
                  10800-before.get('runtime_holding_union_seconds',0),1800)
    if remaining<150:raise RuntimeError('root_time_margin_exhausted')
    root_id=r.count('roots');identity=str(uuid4());start=time.monotonic_ns()
    cleanup_deadline=start+int(remaining*1e9)
    business_deadline=cleanup_deadline-120_000_000_000
    slot={'id':root_id,'identity':identity,'phase':phase,'start_utc':r.utc(),'start_ns':start,
        'business_deadline_ns':business_deadline,'cleanup_deadline_ns':cleanup_deadline,
        'clock':'host time.monotonic_ns/QPC within same running host','owner':birth(os.getpid()),'counts_at_entry':r.state()['counts'].copy()}
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
            monitor.register('pg',r.stop_pg,priority=0)
            # Register ownership before creating the suspended root process.
            monitor.register('browser-api-native-test-job',lambda:cleanup_job(identity) if job else {'created':False},priority=60)
            monitor.check();r.choose_ports();monitor.check();r.start_pg();monitor.check()
            job=r.root_job(identity)
            child_env=r.public_environment()
            child_env.update(PYTHONPATH=str(ROOT/'backend'),PYTHONIOENCODING='utf-8',
                RETROLUME_TASK120_ROOT_ID=str(root_id),RETROLUME_TASK120_TESTONLY='TASK-120-Q-PREP-IMPLEMENTATION-20261018')
            # CreateProcess inherits this process environment. Replace only the
            # controller's own mapping; never enumerate or print user env.
            os.environ.clear();os.environ.update(child_env)
            job.spawn_suspended([sys.executable,'-m','tests.fixtures.task120.run',phase],cwd=str(ROOT/'backend'))
            r.event('root_child_started',root=root_id,pid=job.pid,birth_100ns=job.process_creation_time_100ns(),job=job.name)
            job.resume()
            subdeadline=min(business_deadline,time.monotonic_ns()+int(seconds*1e9))
            while job.active_processes() and time.monotonic_ns()<subdeadline and not monitor.closing:time.sleep(.1)
            if job.active_processes():
                r.event('root_subbatch_timeout_or_pressure',root=root_id)
                job.terminate()
                if not job.wait_empty_until(time.monotonic_ns()+5_000_000_000):raise RuntimeError('subbatch_tree_unknown')
            code=job.primary_exit_code()
    except BaseException as exc:
        r.event('root_exception',root=root_id,error_type=type(exc).__name__,safe_code=str(exc) if type(exc) is RuntimeError else None)
        code=1
    finally:
        if monitor is not None:report=monitor.close('normal_exit' if code==0 else 'exception')
        else:
            try:report={'pg':r.stop_pg(),'all_confirmed':True}
            except BaseException as exc:report={'all_confirmed':False,'error_type':type(exc).__name__}
        if job is not None:job.close()
        ports={}
        for name,port in r.state().get('ports',{}).items():
            with socket.socket() as probe:
                probe.settimeout(.3);ports[name]={'port':port,'listening':probe.connect_ex(('127.0.0.1',port))==0}
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


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',nargs='?',choices=('bootstrap','flow','ui','budget','reopen'))
    parser.add_argument('--seconds',type=int,default=280);parser.add_argument('--watchdog')
    args=parser.parse_args()
    if args.watchdog:raise SystemExit(watchdog(args.watchdog))
    if not args.phase or not 1<=args.seconds<=300:raise SystemExit('bounded phase required')
    raise SystemExit(execute(args.phase,args.seconds))
