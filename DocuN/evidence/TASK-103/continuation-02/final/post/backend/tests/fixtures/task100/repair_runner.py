"""Audit-repair03 finite entry. Existing objects only; no migration/grants/data deletion.

The outer controller bounds the complete worker, including builtin PG calls. The worker
has the same monotonic deadline and always performs separately charged cleanup.
"""
from __future__ import annotations
import argparse
import importlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path
from .control import *
from .runner import Batch, PYTHON, OFFLINE_TESTS, source_paths, verify_run_files

REPOSITORY_TESTS=[
    'tests.test_teaching_repository.TeachingLedgerPGTests.'+n for n in (
        'test_local_command_commits_head_and_record_atomically',
        'test_identical_replay_is_idempotent_and_conflict_is_refused',
        'test_revision_cas_blocks_stale_head','test_goal_version_zero_only_for_first_goal',
        'test_semantic_slot_ignores_business_key_and_retry','test_head_projection_is_rebuildable_and_never_claims_mastered',
        'test_command_identity_guard_blocks_status_rewrite','test_workspace_read_requires_goal_before_plan_actions')]
REPOSITORY_TESTS+=['tests.test_teaching_recovery.RecoveryPgTests']
REPOSITORY_TESTS+=['tests.test_task100_integration.IntegrationPGTests.'+n for n in (
    'test_actual_frozen_context_binds_goal_path_exercise_answer',
    'test_pending_closed_settled_state_is_launchable','test_zero_fee_answer_preserved_at_exhausted_budget',
    'test_database_admit_requires_trusted_binding_before_reservation',
    'test_answer_change_after_admit_blocks_mark_before_dispatch',
    'test_invalid_teaching_result_rolls_back_original_007_and_terminal',
    'test_real_concurrent_answer_slot_has_one_effect_and_no_fork',
    'test_teaching_already_present_replay_after_settle_is_read_only',
    'test_correction_and_opposite_feedback_preserve_contested_observation')]
REPOSITORY_TESTS+=['tests.test_task100_repair.RepairPGTests']
HTTP_TESTS=['tests.test_task100_repair.RepairHttpTests']
REPAIR_OFFLINE=['tests.test_task100_repair.RepairOfflineTests','tests.test_task100_repair.RepairControlOfflineTests',
                'tests.test_task100_bootstrap.RepairBootstrapTests','tests.test_task100_readonly.ReadonlyControlTests']
STAGES=('container','database','repository','application','http','windows','browser')
READONLY_STAGES=('container','database','readonly-snapshots','browser-readonly')
SCENARIOS=('recover_model_and_tool','numeric_small_conflict','grounded_three_scenarios','prepare_browser')
BROWSER=ROOT/'frontend/tests/task100-repair-browser.cjs'
READONLY_BROWSER=ROOT/'frontend/tests/task100-repair-readonly-browser.cjs'


def snapshot_bytes(directory, files):
    directory.mkdir(parents=True,exist_ok=False)
    for relative, digest in files.items():
        target=directory/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,target)
        if __import__('hashlib').sha256(target.read_bytes()).hexdigest()!=digest:
            raise ControlRefusal('as_run_copy_drift')
    atomic_json(directory/'manifest.json',files)


def discover(names):
    result={}
    def ids(suite):
        for item in suite:
            if isinstance(item,unittest.TestSuite):yield from ids(item)
            else:
                if item.__class__.__name__=='_FailedTest':raise ControlRefusal('test_discovery_failed')
                yield item.id()
    for name in names:
        result[name]=list(ids(unittest.defaultTestLoader.loadTestsFromName(name)))
        if not result[name]:raise ControlRefusal('empty_test_suite')
    return result


def plan():
    suites=discover(OFFLINE_TESTS+REPAIR_OFFLINE+REPOSITORY_TESTS+HTTP_TESTS)
    windows=importlib.import_module('tests.fixtures.task100.repair_windows')
    if not all(callable(getattr(windows,n,None)) for n in SCENARIOS):raise ControlRefusal('missing_repair_scenario')
    for browser in (BROWSER,READONLY_BROWSER):
        syntax=subprocess.run(['node','--check',str(browser)],capture_output=True,timeout=5)
        if syntax.returncode:raise ControlRefusal('repair_browser_syntax')
    runtime=subprocess.run(['node','-e',"process.stdout.write(require('playwright').chromium.executablePath())"],
        cwd=ROOT/'frontend',capture_output=True,timeout=5,encoding='utf-8')
    if runtime.returncode or not Path(runtime.stdout).is_file():raise ControlRefusal('installed_browser_missing')
    value={'permit':PERMIT,'created_at':utc(),'tests':suites,'repository':REPOSITORY_TESTS,'http':HTTP_TESTS,
        'windows_module':'tests.fixtures.task100.repair_windows','windows_functions':list(SCENARIOS),
        'browser_entry':str(BROWSER),'browser_runtime':runtime.stdout,
        'readonly_final_browser':{'stages':list(READONLY_STAGES),'entry':str(READONLY_BROWSER),
            'projection_module':'tests.fixtures.task100.repair_readonly','source_batch':'2026-10-05T103020.095611-0000-repair-combo',
            'no_application_server':True,'no_POST_SUP_business_writes':True,
            'grade':'native_browser_IDB_WebLocks_final_dist_labelled_readonly_snapshots'},
        'dependencies':{'database':['container'],'repository':['database'],'application':['repository'],
                        'http':['application'],'windows':['http'],'browser':['windows']},
        'expected_evidence':['as-run/manifest.json','segments.json','repository-raw','http-raw',
            'repair-windows-facts.json','content-oracle.json','repair-browser/facts.json','observations','cleanup.json'],
        'resources':{'container_id':CID,'image':IMAGE,'volume':VOLUME,'ports':[55442,18100],
                     'databases':[MAIN_DB,FAULT_DB],'roles':list(ROLES),'new_objects':False},
        'limits':LIMITS,'time_limits':TIME_LIMITS,'per_batch_seconds':1800,
        'clock':'fixed shared Windows monotonic; outer worker kill; independent bounded finally',
        'reuse':'009 and unchanged original authority; no old migration/17-window rerun',
        'files':hash_files(source_paths())}
    previous=EVIDENCE/'execution-plan.json'
    if previous.exists():shutil.copyfile(previous,EVIDENCE/('execution-plan-before-'+str(time.time_ns())+'.json'))
    atomic_json(previous,value);return value


class RepairBatch(Batch):
    def container(self):
        validate_container(json.loads(self.docker(['inspect',CID]))[0])
        return super().container()

    def database(self):
        from . import pg_setup
        from psycopg import sql
        pg_setup.DEADLINE=self.deadline
        with pg_setup.connection(self.state['super_dsn'],'postgres',autocommit=True) as conn:
            roles=conn.execute('SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls '
                'FROM pg_roles WHERE rolname=ANY(%s) ORDER BY rolname',(list(ROLES),)).fetchall()
            if len(roles)!=3 or any(any(r[k] for k in r if k!='rolname') for r in roles):
                raise ControlRefusal('existing_roles_required_and_minimal')
            for role in ROLES:
                if conn.execute('SELECT count(*) AS n FROM pg_auth_members WHERE member='
                    '(SELECT oid FROM pg_roles WHERE rolname=%s)',(role,)).fetchone()['n']:
                    raise ControlRefusal('unexpected_role_membership')
            owners=conn.execute('SELECT datname,pg_get_userbyid(datdba) AS owner FROM pg_database '
                'WHERE datname=ANY(%s) ORDER BY datname',([MAIN_DB,FAULT_DB],)).fetchall()
            if len(owners)!=2 or any(r['owner']!=ROLES[0] for r in owners):raise ControlRefusal('existing_database_owner')
            passwords={role:secrets.token_urlsafe(32) for role in ROLES}
            # Only existing exact test-role passwords are reset, in memory. No CREATE.
            for role in ROLES:
                conn.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(role),sql.Literal(passwords[role])))
        admin=switched_dsn(self.state['super_dsn'],MAIN_DB,ROLES[0],passwords[ROLES[0]])
        app=switched_dsn(self.state['super_dsn'],MAIN_DB,ROLES[1],passwords[ROLES[1]])
        fault=switched_dsn(self.state['super_dsn'],FAULT_DB,ROLES[0],passwords[ROLES[0]])
        expected=(BACKEND/'migrations/009_teaching.sql').read_text(encoding='utf-8')
        facts={'roles':roles,'owners':owners,'009_sha256':hash_files([BACKEND/'migrations/009_teaching.sql'])}
        with pg_setup.connection(admin,MAIN_DB,ROLES[0],autocommit=True) as conn:
            tables=conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename").fetchall()
            if not set(pg_setup.TEACHING_TABLES).issubset({r['tablename'] for r in tables}):raise ControlRefusal('existing_teaching_schema')
            normalize=lambda text:re.sub(r'\s+','',text).lower()
            functions=[]
            for name in ('teaching_records_immutable','teaching_command_identity_guard'):
                row=conn.execute("SELECT prosrc FROM pg_proc WHERE proname=%s AND pronamespace='public'::regnamespace",(name,)).fetchone()
                body=re.search(r'CREATE FUNCTION '+name+r'\(\).*?AS \$\$(.*?)\$\$;',expected,re.S).group(1)
                if row is None or normalize(row['prosrc'])!=normalize(body):raise ControlRefusal('009_guard_changed_no_repair_authority')
                functions.append({'name':name,'matches_009':True})
            triggers=conn.execute("SELECT tgname,tgenabled FROM pg_trigger WHERE tgrelid IN "
                "('teaching_records'::regclass,'teaching_commands'::regclass) AND NOT tgisinternal").fetchall()
            if not all(any(r['tgname']==n and r['tgenabled']=='O' for r in triggers) for n in
                       ('teaching_records_immutable','teaching_command_identity_guard')):raise ControlRefusal('009_trigger_changed')
            acl=conn.execute("SELECT table_name,column_name,privilege_type FROM information_schema.column_privileges "
                "WHERE grantee=%s AND table_schema='public' AND table_name LIKE 'teaching_%%' "
                'ORDER BY table_name,column_name,privilege_type',(ROLES[1],)).fetchall()
            if any(r['table_name']=='teaching_records' and r['privilege_type'] in ('UPDATE','REFERENCES') for r in acl):
                raise ControlRefusal('records_column_privilege')
            permissions=conn.execute("SELECT has_table_privilege(%s,'teaching_records','SELECT') AS sel, "
                "has_table_privilege(%s,'teaching_records','INSERT') AS ins, "
                "has_table_privilege(%s,'teaching_records','UPDATE') AS upd, "
                "has_table_privilege(%s,'teaching_records','DELETE') AS del, "
                "has_any_column_privilege(%s,'teaching_records','UPDATE') AS col_upd, "
                "has_table_privilege(%s,'teaching_records','SELECT') AS denied_sel",(ROLES[1],)*5+(ROLES[2],)).fetchone()
            if permissions!={'sel':True,'ins':True,'upd':False,'del':False,'col_upd':False,'denied_sel':False}:
                raise ControlRefusal('existing_acl_not_minimal')
            facts.update(functions=functions,triggers=triggers,column_privileges=acl,permissions=permissions)
        with pg_setup.connection(fault,FAULT_DB,ROLES[0],autocommit=True) as conn:
            facts['retained_fault_schemas']=conn.execute("SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name LIKE 'task100_m%%' ORDER BY schema_name").fetchall()
        atomic_json(self.directory/'database-identity-acl.json',facts)
        originals=ROOT/'backend/tests/data/task100/audit-repair-03/data/originals';originals.mkdir(parents=True,exist_ok=True)
        self.env.update(RETROLUME_TASK100_PG_DSN=app,RETROLUME_TASK100_ADMIN_DSN=admin,
            RETROLUME_TASK100_EXPECTED_DB=MAIN_DB,RETROLUME_TASK100_EXPECTED_ROLE=ROLES[1],
            RETROLUME_TASK100_ORIGINALS_DIR=str(originals))
        self.state.update(app_dsn=app,admin_dsn=admin)
        return {'existing_only':True,'migrations_executed':0,'grants_executed':0,'data_deleted':False}


def offline(mode):
    ledger=Ledger();value=ledger.checkpoint_active()
    batch=RepairBatch(mode,Deadline(min(600,TIME_LIMITS['offline']-value['seconds']['offline'],active_remaining(value)-480)))
    files=hash_files(source_paths());snapshot_bytes(batch.directory/'as-run',files)
    begun=time.monotonic()
    try:
        if mode=='offline':
            # Old offline controls use isolated temp ledgers under their historical constants.
            # They do not open any PG/SUP/browser or resurrect a historical real entry.
            oldenv=dict(batch.env);oldenv.pop('RETROLUME_TASK100_PERMIT',None)
            batch.stage('common-offline',lambda:batch.process('common-raw',[str(PYTHON),'-B','-m','unittest',*OFFLINE_TESTS,'-v'],300,env=oldenv))
            batch.stage('repair-offline',lambda:batch.process('repair-raw',[str(PYTHON),'-B','-m','unittest',*REPAIR_OFFLINE,'-v'],300),('common-offline',))
            batch.stage('discovery-plan',plan,('repair-offline',))
            status=aggregate(batch.results)
            if status=='pass':ledger.note('offline_batch_pass',{'files':files,'batch':str(batch.directory)})
        else:
            ledger.consume('frontend_build',{'command':'npm run build','mode':'repair'})
            result=batch.stage('build',lambda:batch.process('build-raw',['cmd','/c','npm','run','build'],600,cwd=ROOT/'frontend'))
            status=result['status']
            if status=='pass':ledger.note('frontend_build_pass',{'files':files,'batch':str(batch.directory),
                'dist':hash_files([p for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()])})
        atomic_json(batch.directory/'summary.json',{'status':status,'segments':batch.results})
        print(mode,status,str(batch.directory));return 0 if status=='pass' else 1
    finally:
        ledger.charge('offline',time.monotonic()-begun,{'batch':str(batch.directory),'mode':mode});ledger.checkpoint_active()


def verified_reuse(source,stage,current):
    if not source or Path(source).name!=source:raise ControlRefusal('reuse_batch_identity')
    directory=EVIDENCE/source
    summary=json.loads((directory/'summary.json').read_text(encoding='utf-8'))
    segment=next((s for s in summary['segments'] if s['name']==stage),None)
    if not segment or segment['status']!='pass':raise ControlRefusal('reuse_stage_not_passed')
    if json.loads((directory/'cleanup.json').read_text(encoding='utf-8'))['status']!='pass':raise ControlRefusal('reuse_cleanup_missing')
    prior=json.loads((directory/'as-run-files.json').read_text(encoding='utf-8'))
    after=json.loads((directory/'after-files.json').read_text(encoding='utf-8'))
    def relevant(p):
        if p.startswith('backend/app/') or p=='backend/migrations/009_teaching.sql':return True
        if stage=='repository':
            return p in ['backend/'+n.replace('.','/')+'.py' for n in
                ('tests.test_teaching_repository','tests.test_teaching_recovery','tests.test_task100_integration','tests.test_task100_repair')]
        if stage=='windows':
            return p.startswith('backend/tests/fixtures/task100/') and Path(p).name not in ('runner.py','repair_runner.py','browser_budget.py','repair_readonly.py')
        if stage=='http':
            return p=='backend/tests/test_task100_repair.py' or (p.startswith('backend/tests/fixtures/task100/')
                and Path(p).name in ('support.py','seed_helpers.py','repair_cases.py','synthetic_content.py','activity.synthetic.json','windows_chain.py','fixture_runtime.py','control.py'))
        return p.startswith('backend/tests/') and ('teaching' in p or 'task100' in p) and Path(p).name not in ('runner.py','repair_runner.py','browser_budget.py')
    if stage=='repository':
        selected=['support.py','seed_helpers.py','repair_cases.py','synthetic_content.py','activity.synthetic.json']
        relevant_original=relevant
        def relevant(p):return relevant_original(p) or p.startswith('backend/tests/fixtures/task100/') and Path(p).name in selected
    expected={p:h for p,h in prior.items() if relevant(p)}
    if expected!={p:h for p,h in after.items() if relevant(p)} or expected!={p:h for p,h in current.items() if relevant(p)}:
        raise ControlRefusal('reuse_loaded_dependency_drift')
    return {'name':stage,'status':'pass','inherited_from':source,'executed_now':False,'elapsed':0,
            'original_result':segment,'exact_dependencies':expected}


def worker(selected,batch_dir,deadline_end,reason,reuse_batch=None,repository_tests=None):
    directory=Path(batch_dir)
    if directory.parent!=EVIDENCE or not (directory/'controller-launch.json').is_file():raise ControlRefusal('worker_controller_missing')
    launch=json.loads((directory/'controller-launch.json').read_text(encoding='utf-8'))
    token=os.environ.get('RETROLUME_TASK100_WORKER_TOKEN','')
    token_sha=__import__('hashlib').sha256(token.encode()).hexdigest()
    if (not token or launch.get('token_sha256')!=token_sha or launch.get('deadline_end')!=deadline_end
            or launch.get('stages')!=selected):raise ControlRefusal('worker_controller_identity')
    def claim(value):
        if value['counts']['real_entries']!=launch['entry_number']:raise ControlRefusal('worker_entry_identity')
        if any(e.get('event')=='repair_worker_claim' and e.get('detail')==token_sha for e in value['events']):
            raise ControlRefusal('worker_already_used')
        value['events'].append({'at':utc(),'event':'repair_worker_claim','detail':token_sha})
    Ledger().update(claim)
    batch=RepairBatch('repair-combo',Deadline(max(.001,deadline_end-time.monotonic())))
    batch.deadline.end=deadline_end
    # The controller has already persisted this directory and full actual bytes.
    batch.directory=Path(batch_dir);batch.env['RETROLUME_TASK100_BATCH_DIR']=str(batch.directory)
    batch.env['RETROLUME_TASK100_DEADLINE']=str(deadline_end)
    batch.state['cleanup_remaining']=TIME_LIMITS['cleanup']-Ledger().load()['seconds']['cleanup']
    try:
        batch.stage('container',batch.container)
        batch.stage('database',batch.database,('container',))
        if selected==list(READONLY_STAGES):
            # Card section 6 permits labelled readonly snapshots. The application
            # cap has been reached; this branch never calls Batch.application.
            batch.env['RETROLUME_TASK100_FIXTURE']=PERMIT
            for stage in ('http','windows'):
                inherited=verified_reuse(reuse_batch,stage,hash_files(source_paths()))
                atomic_json(batch.directory/(stage+'-reuse.json'),inherited)
            batch.stage('readonly-snapshots',lambda:batch.process('readonly-snapshots-raw',
                [str(PYTHON),'-B','-m','tests.fixtures.task100.repair_readonly'],180),('database',))
            def readonly_browser():
                Ledger().consume('driver',{'entry':str(READONLY_BROWSER),'read_only':True})
                batch.env['RETROLUME_TASK100_BROWSER_ENTRY']='frontend/tests/task100-repair-readonly-browser.cjs'
                return batch.process('browser-readonly-raw',['node',str(READONLY_BROWSER)],300,cwd=ROOT/'frontend')
            batch.stage('browser-readonly',readonly_browser,('readonly-snapshots',))
            return 0 if aggregate(batch.results)=='pass' else 1
        if 'repository' in selected:batch.stage('repository',lambda:batch.process('repository-raw',[str(PYTHON),'-B','-m','unittest',*(repository_tests or REPOSITORY_TESTS),'-v'],600),('database',))
        elif reuse_batch:
            batch.results.append(verified_reuse(reuse_batch,'repository',hash_files(source_paths())))
            atomic_json(batch.directory/'repository-reuse.json',batch.results[-1])
        if any(s in selected for s in ('application','http','windows','browser')):
            batch.stage('application',batch.application,('database','repository'))
        if 'http' in selected:batch.stage('http',lambda:batch.process('http-raw',[str(PYTHON),'-B','-m','unittest',*HTTP_TESTS,'-v'],240),('application',))
        if 'windows' in selected:batch.stage('windows',lambda:batch.process('windows-raw',[str(PYTHON),'-B','-m','tests.fixtures.task100.repair_windows'],600),('http',) if 'http' in selected else ('application',))
        if 'browser' in selected:
            def browser():
                Ledger().consume('driver',{'entry':str(BROWSER)})
                return batch.process('browser-raw',['node',str(BROWSER)],300,cwd=ROOT/'frontend')
            batch.stage('browser',browser,('windows',))
    finally:
        batch.cleanup()
        atomic_json(batch.directory/'summary.json',{'status':aggregate(batch.results),'segments':batch.results,
                    'purpose':reason or 'complete affected chain','data_deleted':False})
    return 0 if aggregate(batch.results)=='pass' else 1


def actual(selected,reason,reuse_batch=None,repository_tests=None):
    ledger=Ledger();value=ledger.checkpoint_active()
    ledger.consume('real_entries',{'stages':selected,'reason':reason})
    if value['counts']['real_entries'] and not reason:raise ControlRefusal('repair_reason_required')
    if not value['counts']['real_entries'] and selected!=list(STAGES):raise ControlRefusal('first_complete_entry_required')
    saved=json.loads((EVIDENCE/'execution-plan.json').read_text(encoding='utf-8'));current=hash_files(source_paths())
    if repository_tests:
        allowed={method for name in REPOSITORY_TESTS for method in saved['tests'][name]}
        if not reason or not all(n in allowed for n in repository_tests):raise ControlRefusal('affected_pg_method_not_allowed')
    docs=verify_run_files(current,saved['files'],value['events'])
    readonly=selected==list(READONLY_STAGES)
    if readonly:
        for stage in ('http','windows'):verified_reuse(reuse_batch,stage,current)
    elif 'repository' not in selected:
        verified_reuse(reuse_batch,'repository',current)
    builds=[e for e in value['events'] if e.get('event')=='frontend_build_pass']
    if not builds:raise ControlRefusal('frontend_build_missing')
    built=builds[-1]['detail']
    if any(h!=current.get(p) for p,h in built['files'].items() if p.startswith('frontend/src/') or p=='frontend/package.json'):
        raise ControlRefusal('frontend_source_after_build')
    dist=hash_files([p for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()])
    if dist!=built['dist']:raise ControlRefusal('dist_drift')
    deadline=Deadline(min(1800,TIME_LIMITS['real']-value['seconds']['real'],active_remaining(value)-480))
    directory=EVIDENCE/(utc().replace(':','').replace('+','-')+('-readonly-browser-combo' if readonly else '-repair-combo'));directory.mkdir()
    snapshot_bytes(directory/'as-run',{**current,**dist});atomic_json(directory/'as-run-files.json',current)
    atomic_json(directory/'as-run-documentation.json',docs)
    atomic_json(directory/'actual-execution-plan.json',{**saved,'actual_stages':selected,
        'actual_repository_methods':[] if readonly else (repository_tests or REPOSITORY_TESTS),'reason':reason,
        'reuse_batch':reuse_batch,'readonly_snapshot_replay':readonly,'application_server_started':False if readonly else None})
    token=secrets.token_urlsafe(32)
    atomic_json(directory/'controller-launch.json',{'token_sha256':__import__('hashlib').sha256(token.encode()).hexdigest(),
        'entry_number':value['counts']['real_entries']+1,'stages':selected,'deadline_end':deadline.end})
    env=dict(os.environ);env.update(PYTHONUTF8='1',PYTHONUNBUFFERED='1',PYTHONDONTWRITEBYTECODE='1',RETROLUME_TASK100_WORKER_TOKEN=token)
    begun=time.monotonic()
    try:
        argv=[str(PYTHON),'-B','-m','tests.fixtures.task100.repair_runner','_worker',
            '--stages',','.join(selected),'--batch-dir',str(directory),'--deadline-end',str(deadline.end),
            '--reason',reason or 'complete affected chain']
        if reuse_batch:argv+=['--reuse-batch',reuse_batch]
        if repository_tests:argv+=['--repository-tests',','.join(repository_tests)]
        outcome=run_process(argv,deadline,1800,directory/'controller-raw',env=env,cwd=BACKEND)
        atomic_json(directory/'controller-result.json',outcome)
        summary=json.loads((directory/'summary.json').read_text(encoding='utf-8')) if (directory/'summary.json').exists() else {'status':'fail'}
        if hash_files(source_paths())!=current:summary['status']='fail';summary['post_drift']=True
        atomic_json(directory/'after-files.json',hash_files(source_paths()))
        return 0 if outcome['status']=='pass' and summary['status']=='pass' else 1
    finally:
        elapsed=time.monotonic()-begun
        cleanup_path=directory/'cleanup.json'
        cleanup=json.loads(cleanup_path.read_text(encoding='utf-8')).get('elapsed',0) if cleanup_path.exists() else 0
        ledger.charge('real',max(0,elapsed-cleanup),{'batch':str(directory),'stages':selected,'outer_elapsed':elapsed,'separate_cleanup':cleanup})
        if not (directory/'cleanup.json').exists():
            # run_process has killed its owned complete worker tree on timeout/error.
            # Still execute container/observed exact PID/Job checks with separate budget.
            recovery=RepairBatch('emergency-cleanup',Deadline(1));recovery.directory=directory
            recovery.started_container=Ledger().load()['counts']['container_starts']>value['counts']['container_starts']
            recovery.state['cleanup_remaining']=TIME_LIMITS['cleanup']-Ledger().load()['seconds']['cleanup'];recovery.cleanup()
        ledger.checkpoint_active()


def main():
    if not IS_REPAIR:raise ControlRefusal('repair_permit_required_old_permit_ended')
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['plan','offline','frontend-build','repair-combo','readonly-browser-combo','_worker'])
    parser.add_argument('--stages');parser.add_argument('--reason');parser.add_argument('--batch-dir');parser.add_argument('--deadline-end',type=float)
    parser.add_argument('--reuse-batch')
    parser.add_argument('--repository-tests')
    args=parser.parse_args();selected=args.stages.split(',') if args.stages else list(READONLY_STAGES if args.mode=='readonly-browser-combo' else STAGES)
    if any(s not in (*STAGES,*READONLY_STAGES) for s in selected):raise ControlRefusal('unknown_stage')
    if any(s in ('readonly-snapshots','browser-readonly') for s in selected) and selected!=list(READONLY_STAGES):
        raise ControlRefusal('readonly_stages_cannot_mix_application')
    if args.mode=='_worker':
        if not args.batch_dir or not args.deadline_end:raise ControlRefusal('worker_identity_missing')
        return worker(selected,args.batch_dir,args.deadline_end,args.reason,args.reuse_batch,args.repository_tests.split(',') if args.repository_tests else None)
    if args.mode in ('repair-combo','readonly-browser-combo'):return actual(selected,args.reason,args.reuse_batch,args.repository_tests.split(',') if args.repository_tests else None)
    if args.mode in ('offline','frontend-build'):return offline(args.mode)
    start=time.monotonic()
    try:Ledger().checkpoint_active();plan();return 0
    finally:Ledger().charge('offline',time.monotonic()-start,{'mode':'plan'})


if __name__=='__main__':
    try:raise SystemExit(main())
    except ControlRefusal as exc:print('CONTROL_REFUSED',str(exc),file=sys.stderr);raise SystemExit(2)
