"""TASK-120 bounded offline commands; never starts Docker or a service."""
from __future__ import annotations
import argparse
import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'backend'))


def write_json(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temp, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--child', action='store_true')
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()
    path = Path(args.manifest).resolve()
    if path.parent != EVIDENCE or not path.name.startswith('command-'):
        raise ValueError('manifest outside exact task evidence')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if set(manifest) != {'label','seconds','argv','cwd'} or not 0 < manifest['seconds'] <= 300:
        raise ValueError('closed bounded command required')
    cwd = (ROOT / manifest['cwd']).resolve()
    if not cwd.is_relative_to(ROOT) or not cwd.is_dir():
        raise ValueError('cwd outside project')
    if args.child:
        # This process is assigned, suspended, to the owning kill-on-close Job.
        import subprocess
        out = EVIDENCE / (path.stem + '.log')
        with out.open('wb') as log:
            argv=list(manifest['argv'])
            if Path(argv[0]).resolve()==(ROOT/'backend/.venv/Scripts/python.exe').resolve():
                argv[0]=sys._base_executable
            result = subprocess.run(argv, cwd=cwd, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=manifest['seconds']-3)
        return result.returncode
    from tests.fixtures.task120.control_job import NamedJob
    budget_path = EVIDENCE.parent / 'budget.json'
    budget = json.loads(budget_path.read_text(encoding='utf-8'))
    now = datetime.now(timezone.utc)
    prior=json.loads((EVIDENCE/'budget.json.before.bytes').read_text(encoding='utf-8'))
    elapsed=(now-datetime.fromisoformat(budget['targeted_repair08']['first_observed_tool_clock_utc'])).total_seconds()+1
    measured=(budget.get('controlled_command_wall_seconds',0)-prior.get('controlled_command_wall_seconds',0))+(budget.get('runtime_command_wall_seconds',0)-prior.get('runtime_command_wall_seconds',0))
    budget['targeted_repair08_unwrapped_command_wall_upper_seconds']=max(0,elapsed-measured)
    deadline = min(datetime.fromisoformat(budget['calendar_deadline_utc'].replace('Z','+00:00')),datetime.fromisoformat(budget['targeted_repair08']['finish_deadline_utc']))
    final_save_only = (path.name.startswith('command-')
                       and manifest['label'] == 'repair08-filesystem-return'
                       and manifest['seconds'] == 60 and manifest['cwd'] == '.'
                       and manifest['argv'] == [str(ROOT/'backend/.venv/Scripts/python.exe'), str(EVIDENCE/'finalize.py')])
    # The card keeps bounded saving/cleanup independent from business runtime.
    # This exact filesystem-only return cannot start a service or a business root.
    if (deadline-now).total_seconds() <= 1800 and not final_save_only:
        raise ValueError('save-only calendar margin')
    if 'pre_controller_wall_upper_seconds' not in budget:
        first = datetime.fromisoformat(budget['actual_first_tool_utc'].replace('Z','+00:00'))
        # Includes thinking/editing. A conservative ceiling, not fabricated measured CPU/wall.
        budget['pre_controller_wall_upper_seconds'] = (now-first).total_seconds()
        budget['command_wall_accounting_note'] = 'Pre-controller receipt gaps bounded by entire elapsed calendar; later commands measured.'
    ceiling = (budget['pre_controller_wall_upper_seconds'] + budget.get('controlled_command_wall_seconds',0)
               +budget.get('runtime_command_wall_seconds',0)+budget.get('unwrapped_metadata_wall_reserved_seconds',0)
               +budget.get('continuation_metadata_uncertainty_reserved_seconds',0)+budget.get('continuation02_unwrapped_command_wall_upper_seconds',0)+budget.get('repair03_unwrapped_command_wall_upper_seconds',0)+budget.get('validation04_unwrapped_command_wall_upper_seconds',0)+budget.get('finalization05_unwrapped_command_wall_upper_seconds',0)+budget.get('continuation06_unwrapped_command_wall_upper_seconds',0)+budget.get('audit_repair07_unwrapped_command_wall_upper_seconds',0)+budget.get('targeted_repair08_unwrapped_command_wall_upper_seconds',0))
    if ceiling + manifest['seconds'] > budget['command_wall_cap_seconds']:
        raise ValueError('cumulative command wall ceiling')
    if budget.get('active_command') or budget.get('active_root'):
        raise ValueError('unreconciled command must be inspected first')
    start = time.monotonic()
    command_id = str(uuid4())
    budget['active_command'] = {'id':command_id,'manifest':path.name,'start_utc':now.isoformat()}
    write_json(budget_path,budget)
    record = {'command_id':command_id,'manifest':path.name,'start_utc':now.isoformat(),'limit_seconds':manifest['seconds']}
    try:
        if manifest['label'] in ('frontend-final-build','root-control-probe'):
            from tests.fixtures.task120.resources import root_job,count
            if manifest['label']=='frontend-final-build':count('frontend_builds')
            owner=root_job(command_id)
        else:owner=NamedJob.create(command_id,1,max_processes=4)
        with owner as job:
            # Avoid two Windows venv redirector processes consuming the finite
            # controller Job. Same interpreter, explicit existing dependency path.
            os.environ['PYTHONPATH']=str(ROOT/'backend/.venv/Lib/site-packages')+os.pathsep+str(ROOT/'backend')
            job.spawn_suspended([sys._base_executable,str(Path(__file__).resolve()),'--child','--manifest',str(path)],cwd=str(ROOT))
            record.update(pid=job.pid,birth_100ns=job.process_creation_time_100ns(),job=job.name)
            job.resume()
            while job.active_processes() and time.monotonic()-start < manifest['seconds']:
                time.sleep(.05)
            if job.active_processes():
                record['timeout'] = True
                job.terminate()
            record['tree_empty'] = job.wait_empty_until(time.monotonic_ns()+2_000_000_000)
            record['exit_code'] = job.primary_exit_code()
    except BaseException as exc:
        record['controller_error'] = type(exc).__name__
        record.setdefault('exit_code',1)
        raise
    finally:
        record.update(wall_seconds=time.monotonic()-start,end_utc=datetime.now(timezone.utc).isoformat())
        budget = json.loads(budget_path.read_text(encoding='utf-8'))
        budget['controlled_command_wall_seconds'] = budget.get('controlled_command_wall_seconds',0)+record['wall_seconds']
        budget['active_command'] = None
        if record['exit_code']:
            budget['failures'].append({'case':manifest['label'],'exit_code':record['exit_code'],'receipt':'audit-repair-08/'+path.stem+'.receipt.json'})
        accounting_keys = ('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds','continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds','validation04_unwrapped_command_wall_upper_seconds','finalization05_unwrapped_command_wall_upper_seconds','continuation06_unwrapped_command_wall_upper_seconds','audit_repair07_unwrapped_command_wall_upper_seconds','targeted_repair08_unwrapped_command_wall_upper_seconds')
        budget['command_wall_conservative_upper_seconds'] = sum(budget.get(k,0) for k in accounting_keys)
        write_json(budget_path,budget)
        write_json(EVIDENCE/(path.stem+'.receipt.json'),record)
        print(json.dumps(record))
    return record['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
