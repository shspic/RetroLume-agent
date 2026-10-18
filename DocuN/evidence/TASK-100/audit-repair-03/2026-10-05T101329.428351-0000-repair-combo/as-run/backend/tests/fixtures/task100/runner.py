"""TASK-100 续作02唯一入口：先离线控制和完整构建，再一批实际整链。"""
from __future__ import annotations
import argparse
import ast
import contextlib
import hashlib
import importlib
import json
import os
import secrets
import socket
import subprocess
import sys
import time
import traceback
import unittest
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
BACKEND=Path(__file__).resolve().parents[3]
ROOT=BACKEND.parent
sys.path.insert(0,str(BACKEND))
from tests.fixtures.task100.control import *
PYTHON=BACKEND/'.venv/Scripts/python.exe'
OFFLINE_TESTS=['tests.test_teaching_contracts','tests.test_teaching_policy',
    'tests.test_teaching_recovery.SupervisionFactsOfflineTests','tests.test_teaching_api.WorkspaceProjectionOfflineTests',
    'tests.test_teaching_api.DtoOfflineTests','tests.test_task100_control','tests.test_task100_content']
PG_TESTS=['tests.test_teaching_repository.TeachingLedgerPGTests','tests.test_teaching_recovery.RecoveryPgTests','tests.test_task100_integration.IntegrationPGTests']
STAGES=('container','database','migration_scenarios','repository','application','http','windows','browser')

class Batch:
    def __init__(self,name,deadline,env=None):
        self.name=name; self.deadline=deadline; self.env=dict(os.environ) if env is None else env
        self.directory=EVIDENCE/(utc().replace(':','').replace('+','-')+'-'+name)
        self.directory.mkdir(parents=True,exist_ok=False); self.results=[]; self.app=None; self.app_out=None; self.app_err=None
        self.started_container=False; self.state={}
        self.env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONUNBUFFERED='1',
            RETROLUME_TASK100_DEADLINE=str(deadline.end),RETROLUME_TASK100_BATCH_DIR=str(self.directory))
    def stage(self,name,fn,dependencies=()):
        before=time.monotonic(); begun=utc()
        if any(next((r['status'] for r in self.results if r['name']==d),'not_run')!='pass' for d in dependencies):
            fact={'name':name,'status':'not_run','reason':'dependency_failed','dependencies':list(dependencies),'elapsed':0}
        else:
            try:
                self.deadline.timeout(1)
                class Tee:
                    def __init__(self,file,console): self.file=file;self.console=console
                    def write(self,text): self.file.write(text);self.file.flush();return self.console.write(text)
                    def flush(self): self.file.flush();self.console.flush()
                with (self.directory/(name+'-stdout.txt')).open('w',encoding='utf-8') as out,(self.directory/(name+'-stderr.txt')).open('w',encoding='utf-8') as err:
                    with contextlib.redirect_stdout(Tee(out,sys.stdout)),contextlib.redirect_stderr(Tee(err,sys.stderr)):
                        value=fn()
                if isinstance(value,dict) and 'status' in value:
                    fact={'name':name,**value}
                else: fact={'name':name,'status':'pass','facts':value}
            except BaseException as exc:
                (self.directory/(name+'-exception.txt')).write_text(traceback.format_exc(),encoding='utf-8')
                fact={'name':name,'status':'fail','error_type':type(exc).__name__}
            fact.update(started_at=begun,ended_at=utc(),elapsed=time.monotonic()-before)
            fact.setdefault('exit_code',0 if fact['status']=='pass' else 1)
        self.results.append(fact); atomic_json(self.directory/'segments.json',self.results)
        print(name,fact['status'],round(fact['elapsed'],3),flush=True)
        return fact
    def process(self,name,argv,stage=300,env=None,cwd=BACKEND):
        return run_process(argv,self.deadline,stage,self.directory/name,env=env or self.env,cwd=cwd)
    def docker(self,args,stage=30):
        timeout=self.deadline.timeout(stage)
        result=subprocess.run(['docker',*args],capture_output=True,timeout=timeout,encoding='utf-8',errors='replace')
        if result.returncode: raise ControlRefusal('docker_command_failed')
        return result.stdout
    def container(self):
        fact=json.loads(self.docker(['inspect',CID]))[0]
        validate_container(fact,require_limits=False)
        if fact['State']['Running']: raise ControlRefusal('unexpected_running_container')
        host=fact['HostConfig']
        if (host.get('Memory'),host.get('NanoCpus'),host.get('PidsLimit'))!=(536870912,1000000000,128):
            self.docker(['update','--memory','512m','--cpus','1','--pids-limit','128',CID])
            fact=json.loads(self.docker(['inspect',CID]))[0]
        validate_container(fact)
        safe={key:fact[key] for key in ('Id','Name','Image','State','Mounts','NetworkSettings')}
        safe['HostConfig']={k:fact['HostConfig'].get(k) for k in ('Memory','NanoCpus','PidsLimit','RestartPolicy','PortBindings','NetworkMode','Privileged','CapAdd','Devices')}
        atomic_json(self.directory/'container-before.json',safe)
        # 初始化账号仅从已核身份容器的环境取到内存，不保存或回显。
        variables=dict(item.split('=',1) for item in fact['Config'].get('Env',[]) if '=' in item)
        from psycopg.conninfo import make_conninfo
        user=variables.get('POSTGRES_USER')
        password=variables.get('POSTGRES_PASSWORD')
        if not user or not password: raise ControlRefusal('cluster_credentials_missing')
        self.state['super_dsn']=switched_dsn(make_conninfo(host='127.0.0.1',port='55442',dbname='postgres',user=user,password=password),'postgres')
        Ledger().consume('container_starts',{'container_id':CID})
        # 尝试创建后立即进入 finally 的所有权记录，即使 start 返回失败也保留。
        self.started_container=True
        self.docker(['start',CID],60)
        after=json.loads(self.docker(['inspect',CID]))[0]; validate_container(after)
        if not after['State']['Running']: raise ControlRefusal('container_not_running')
        ready=Deadline(self.deadline.timeout(45))
        while True:
            try:
                from tests.fixtures.task100.pg_setup import connection
                with connection(self.state['super_dsn'],'postgres',autocommit=True): pass
                break
            except Exception:
                ready.timeout(1); time.sleep(min(.4,ready.timeout(.4)))
        return {'container_id':CID,'running':True,'password_not_logged':True}
    def database(self):
        from tests.fixtures.task100 import pg_setup
        passwords={role:secrets.token_urlsafe(30) for role in ROLES}
        super_dsn=self.state['super_dsn']
        pg_setup.DEADLINE=self.deadline
        pg_setup.create_roles(super_dsn,passwords)
        for db in (MAIN_DB,FAULT_DB): pg_setup.create_database(super_dsn,db)
        admin=switched_dsn(super_dsn,MAIN_DB,ROLES[0],passwords[ROLES[0]])
        app=switched_dsn(super_dsn,MAIN_DB,ROLES[1],passwords[ROLES[1]])
        fault=switched_dsn(super_dsn,FAULT_DB,ROLES[0],passwords[ROLES[0]])
        denied=switched_dsn(super_dsn,FAULT_DB,ROLES[2],passwords[ROLES[2]])
        self.deadline.timeout(1); pg_setup.apply_migrations(admin)
        self.deadline.timeout(1); pg_setup.grant_table_privileges(admin)
        self.env.update(RETROLUME_TASK100_PG_DSN=app,RETROLUME_TASK100_ADMIN_DSN=admin,
            RETROLUME_TASK100_FAULT_DSN=fault,RETROLUME_TASK100_DENIED_DSN=denied,
            RETROLUME_TASK100_EXPECTED_DB=MAIN_DB,RETROLUME_TASK100_EXPECTED_ROLE=ROLES[1])
        self.state.update(app_dsn=app,admin_dsn=admin)
        return {'database':MAIN_DB,'owner':ROLES[0],'runtime_role':ROLES[1],'retained':True}
    def application(self):
        for port in (18100,):
            with socket.socket() as sock:
                if sock.connect_ex(('127.0.0.1',port))==0: raise ControlRefusal('app_port_in_use')
        data=ROOT/('backend/tests/data/task100/audit-repair-03' if IS_REPAIR else 'backend/tests/data/task100/continuation-02')
        backups=data/'backups' if IS_REPAIR else ROOT/'backend/tests/data/task100/continuation-02-backups'
        data.mkdir(parents=True,exist_ok=True);backups.mkdir(parents=True,exist_ok=True)
        # Fixture 与应用使用同一原件根，仓储测试也写在这个真实项目目录。
        originals=data/'originals'; originals.mkdir(exist_ok=True)
        self.env['RETROLUME_TASK100_ORIGINALS_DIR']=str(originals)
        config=ROOT/'backend/tests/fixtures/task100/activity.synthetic.json'
        self.env.update(RETROLUME_DATABASE_URL=self.state['app_dsn'],RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backups),
            RETROLUME_ACTIVITY_CONFIG=str(config),RETROLUME_TASK100_SYNTHETIC_KEY='task100-synthetic-not-a-real-key',
            RETROLUME_TASK100_FIXTURE=PERMIT,RETROLUME_TASK100_DEADLINE=str(self.deadline.end),
            RETROLUME_TASK100_OBSERVATIONS=str(self.directory/'observations'),RETROLUME_TASK100_MODE=str(self.directory/'mode.json'),
            RETROLUME_TASK100_RELEASE=str(self.directory/'release-normal'),RETROLUME_TEACHING_HTTP_BASE='http://127.0.0.1:18100',
            RETROLUME_TASK100_BATCH_DIR=str(self.directory),
            PYTHONPATH=os.pathsep.join((str(BACKEND/'tests/fixtures/task100/bootstrap'),str(BACKEND),str(BACKEND/'.venv/Lib/site-packages'))))
        atomic_json(self.directory/'mode.json',{'mode':'normal'})
        self.app_out=(self.directory/'app-stdout.txt').open('wb'); self.app_err=(self.directory/'app-stderr.txt').open('wb')
        Ledger().consume('app_starts',{'port':18100})
        self.app=subprocess.Popen([str(PYTHON),'-B','-m','tests.fixtures.task100.app_entry'],cwd=BACKEND,env=self.env,stdout=self.app_out,stderr=self.app_err)
        Ledger().note('app_created',{'pid':self.app.pid,'batch':str(self.directory)})
        ready=Deadline(self.deadline.timeout(45))
        while True:
            if self.app.poll() is not None: raise ControlRefusal('app_start_failed')
            try:
                with urllib.request.urlopen('http://127.0.0.1:18100/health',timeout=ready.timeout(2)) as response:
                    if response.status==200: break
            except OSError: ready.timeout(1);time.sleep(min(.2,ready.timeout(.2)))
        with urllib.request.urlopen('http://127.0.0.1:18100/api/session',timeout=self.deadline.timeout(3)) as response:
            bootstrap=json.loads(response.read())
        if not bootstrap.get('token') or not bootstrap.get('storage_configured'): raise ControlRefusal('session_bootstrap_not_ready')
        # 不落盘 token；测试与浏览器从真实 /api/session 自行获取。
        return {'pid':self.app.pid,'health':200,'bootstrap':'/api/session','storage_configured':True}
    def cleanup(self):
        began=time.monotonic(); remaining=self.state.get('cleanup_remaining',180)
        cleanup_deadline=Deadline(min(180,remaining)); facts=[]
        try:
            if self.app is not None and self.app.poll() is None:
                try:
                    outcome=subprocess.run(['taskkill','/PID',str(self.app.pid),'/T','/F'],capture_output=True,timeout=cleanup_deadline.timeout(20))
                    facts.append({'action':'owned_app_tree_stop','pid':self.app.pid,'exit_code':outcome.returncode})
                    self.app.wait(timeout=cleanup_deadline.timeout(10))
                except BaseException as exc: facts.append({'action':'owned_app_tree_stop','error_type':type(exc).__name__})
        finally:
            for stream in (self.app_out,self.app_err):
                if stream is not None: stream.close()
            if self.started_container:
                try:
                    result=subprocess.run(['docker','stop','--time','10',CID],capture_output=True,timeout=cleanup_deadline.timeout(40))
                    facts.append({'action':'exact_container_stop','exit_code':result.returncode})
                except BaseException as exc: facts.append({'action':'exact_container_stop','error_type':type(exc).__name__})
            try:
                raw=subprocess.run(['docker','inspect',CID],capture_output=True,timeout=cleanup_deadline.timeout(15))
                fact=json.loads(raw.stdout)[0]; validate_container(fact)
                facts.append({'action':'final_container','id':fact['Id'],'state':fact['State']})
                if fact['State']['Running'] or fact['State']['Pid']!=0: facts.append({'error_type':'container_not_stopped'})
            except BaseException as exc: facts.append({'action':'final_container','error_type':type(exc).__name__})
            for port in (55442,18100):
                try:
                    with socket.socket() as sock:
                        sock.settimeout(cleanup_deadline.timeout(2)); open_port=sock.connect_ex(('127.0.0.1',port))==0
                    facts.append({'action':'port_check','port':port,'open':open_port})
                    if open_port:facts.append({'error_type':'owned_port_still_open','port':port})
                except BaseException as exc:facts.append({'action':'port_check','port':port,'error_type':type(exc).__name__})
            # 只核本次实际观察所得 PID/创建时点及具名 Job，未知归属不关闭。
            try:
                from app.worker.windows_job import NamedJob,JobOpenError,ERROR_FILE_NOT_FOUND,job_name
                identities=set();jobs=set()
                for path in (self.directory/'observations').glob('*.json'):
                    raw=json.loads(path.read_text(encoding='utf-8'));value=raw['value']
                    if raw['kind']=='sup_created':identities.add((value['pid'],value['created_100ns']))
                    if raw['kind']=='session_outcome':
                        for pid_name,created_name in (('manager_pid','manager_created_100ns'),('pid','worker_created_100ns')):
                            if value.get(pid_name) and value.get(created_name):identities.add((value[pid_name],value[created_name]))
                    if raw['kind']=='job_created':
                        if job_name(value['activity_id'],value['generation'])!=value['job_name']:raise ControlRefusal('observed_job_identity')
                        jobs.add((value['activity_id'],value['generation']))
                for pid,created in identities:
                    cleanup_deadline.timeout(1);identity=process_identity(pid,created)
                    if identity['state']=='alive':
                        stopped=subprocess.run(['taskkill','/PID',str(pid),'/T','/F'],capture_output=True,timeout=cleanup_deadline.timeout(10))
                        identity['stop_exit_code']=stopped.returncode
                        identity['after']=process_identity(pid,created)
                    if identity['state']=='unconfirmed' or identity.get('after',{}).get('state') in ('alive','unconfirmed'):
                        identity['error_type']='owned_process_not_closed'
                    facts.append({'action':'owned_process_final',**identity})
                for aid,generation in jobs:
                    job=None
                    try:
                        job=NamedJob.open_existing(aid,generation)
                        if job.active_processes():job.terminate();job.wait_empty_until(time.monotonic_ns()+int(cleanup_deadline.timeout(5)*1e9))
                        active=job.active_processes();facts.append({'action':'owned_job_final','job_name':job.name,'active_processes':active})
                        if active:facts.append({'error_type':'owned_job_not_empty','job_name':job.name})
                    except JobOpenError as exc:
                        facts.append({'action':'owned_job_final','job_name':job_name(aid,generation),'windows_error':exc.code,
                            **({} if exc.code==ERROR_FILE_NOT_FOUND else {'error_type':'job_query_unconfirmed'})})
                    finally:
                        if job is not None:job.close()
            except BaseException as exc:facts.append({'action':'owned_identity_final','error_type':type(exc).__name__})
            try: Ledger().charge('cleanup',time.monotonic()-began,{'batch':str(self.directory)})
            except BaseException as exc:facts.append({'action':'cleanup_ledger','error_type':type(exc).__name__})
            status='fail' if any(f.get('error_type') for f in facts) else 'pass'
            atomic_json(self.directory/'cleanup.json',{'started_at':utc(),'elapsed':time.monotonic()-began,'status':status,'facts':facts,'data_deleted':False})
            self.results.append({'name':'cleanup','status':status,'elapsed':time.monotonic()-began})
        return facts

def source_paths():
    preparation=json.loads((EVIDENCE/'preparation.json').read_text(encoding='utf-8'))
    paths=list((BACKEND/'app').rglob('*.py'))+list((ROOT/'frontend/src').rglob('*'))+list((BACKEND/'tests/fixtures/task100').rglob('*.py'))
    paths+=list((BACKEND/'tests').glob('*teaching*.py'))+list((BACKEND/'tests').glob('*task100*.py'))+list((ROOT/'frontend/tests').glob('*100*'))
    paths+=[BACKEND/'migrations/009_teaching.sql',BACKEND/'tests/fixtures/task100/activity.synthetic.json',ROOT/'frontend/package.json',ROOT/'README.md']
    return [p for p in paths if p.is_file() and '__pycache__' not in p.parts]

def execution_plan():
    suites={}
    for name in OFFLINE_TESTS+PG_TESTS+['tests.test_teaching_api.HttpTests']:
        suite=unittest.defaultTestLoader.loadTestsFromName(name)
        def ids(suite):
            for item in suite:
                if isinstance(item,unittest.TestSuite): yield from ids(item)
                else:
                    if item.__class__.__name__=='_FailedTest': raise ControlRefusal('test_discovery_failed_'+name)
                    yield item.id()
        suites[name]=list(ids(suite))
        if not suites[name] or any('_FailedTest' in t for t in suites[name]): raise ControlRefusal('test_class_missing_'+name)
    windows=importlib.import_module('tests.fixtures.task100.windows_chain')
    scenario_names=['normal_h1','late_goal','late_answer','late_source','late_cancel','unknown_and_abandon','invalid_and_explicit_retry','hard_stop']
    for name in scenario_names:
        if not callable(getattr(windows,name,None)): raise ControlRefusal('windows_scenario_missing_'+name)
    browser=ROOT/'frontend/tests/task100-browser.cjs'
    if not browser.is_file(): raise ControlRefusal('browser_entry_missing')
    checked=subprocess.run(['node','--check',str(browser)],capture_output=True,timeout=5)
    if checked.returncode:raise ControlRefusal('browser_entry_syntax')
    runtime=subprocess.run(['node','-e',"process.stdout.write(require('playwright').chromium.executablePath())"],cwd=ROOT/'frontend',capture_output=True,timeout=5,encoding='utf-8')
    if runtime.returncode or not Path(runtime.stdout).is_file():raise ControlRefusal('existing_browser_runtime_missing')
    value={'permit':PERMIT,'created_at':utc(),'roots':{'project':str(ROOT),'rules_entry':str(ROOT/'AGENTS.md')},
        'tests':suites,'windows_module':str(BACKEND/'tests/fixtures/task100/windows_chain.py'),'windows_functions':scenario_names,
        'browser_entry':str(browser),'browser_runtime':{'kind':'existing local playwright and installed chromium only','executable':runtime.stdout,'exists':True},
        'dependencies':{'database':['container'],'migration_scenarios':['database'],'repository':['database'],'application':['database','repository'],
            'http':['application'],'windows':['http'],'browser':['windows']},
        'expected_evidence':['segments.json','as-run-files.json','stdout.txt','stderr.txt','result.json','migration-facts.json',
            'windows-facts.json','observations/*.json','browser-facts.json','screenshots','cleanup.json'],
        'resources':{'container_id':CID,'name':NAME,'image':IMAGE,'volume':VOLUME,'pg_port':55442,'app_port':18100,'databases':[MAIN_DB,FAULT_DB],'roles':list(ROLES)},
        'limits':effective_limits(Ledger().load()),'original_limits':LIMITS,'time_limits':TIME_LIMITS,
        'supplementary_permit':Ledger().load().get('supplementary_permit'),
        'per_batch_seconds':1800,'files':hash_files(source_paths())}
    target=EVIDENCE/'execution-plan.json'
    if target.exists(): atomic_json(EVIDENCE/('execution-plan-'+utc().replace(':','').replace('+','-')+'.json'),json.loads(target.read_text(encoding='utf-8')))
    atomic_json(target,value); print('execution-plan saved',sum(len(t) for t in suites.values()),'tests')
    return value

WINDOWS_INHERIT_BATCH='2026-10-05T033911.225278-0000-main-combo'

def verify_run_files(current,planned,events):
    # README 不被产品或夹具加载；并发归档导航维护单独记字节，不耗业务入口。
    def runtime(files):return {p:h for p,h in files.items() if p!='README.md'}
    if runtime(current)!=runtime(planned):raise ControlRefusal('plan_source_drift')
    if not any(e.get('event')=='offline_batch_pass' and runtime(e['detail']['files'])==runtime(current) for e in events):
        raise ControlRefusal('offline_batch_for_current_files_missing')
    return [{'path':'README.md','planned_sha256':planned.get('README.md'),'as_run_sha256':current.get('README.md')}]

def inherit_windows(source_batch,current,evidence=EVIDENCE):
    """仅继承已保存的17窗原件；总批曾失败不覆盖已通过的子段。纯文件核对。"""
    if source_batch!=WINDOWS_INHERIT_BATCH:raise ControlRefusal('windows_inheritance_batch_not_allowed')
    directory=Path(evidence)/source_batch
    names=('summary.json','cleanup.json','as-run-files.json','windows-facts.json','browser-input.json','browser-main/facts.json')
    try: saved={name:json.loads((directory/name).read_text(encoding='utf-8')) for name in names}
    except (OSError,ValueError):raise ControlRefusal('windows_inheritance_evidence_missing') from None
    windows=[s for s in saved['summary.json'].get('segments',[]) if s.get('name')=='windows']
    facts=saved['windows-facts.json'];outcomes=facts.get('session_outcomes',[])
    if (len(windows)!=1 or windows[0].get('status')!='pass' or saved['cleanup.json'].get('status')!='pass'
            or len(facts.get('cases',[]))!=8 or any(c.get('status')!='pass' for c in facts['cases'])
            or len(outcomes)!=17 or facts.get('provider_real') is not False or facts.get('user_program_executed') is not False
            or any(o.get('active_processes_at_end')!=0 or o.get('cleanup_incomplete') is not False
                or not all(o.get(k) for k in ('manager_pid','manager_created_100ns','worker_created_100ns','job_name')) for o in outcomes)
            or saved['browser-main/facts.json'].get('status')!='pass'):
        raise ControlRefusal('windows_inheritance_not_passed')
    def relevant(path):
        return path.startswith(('backend/app/','backend/migrations/','frontend/src/')) or path=='frontend/package.json' or (
            path.startswith('backend/tests/fixtures/task100/') and path.endswith('.py') and Path(path).name not in ('runner.py','control.py','browser_budget.py'))
    prior=saved['as-run-files.json']
    if {p:h for p,h in prior.items() if relevant(p)}!={p:h for p,h in current.items() if relevant(p)}:
        raise ControlRefusal('windows_inheritance_product_drift')
    identity=saved['browser-input.json']
    if not identity.get('activity_id') or not identity.get('title'):raise ControlRefusal('windows_inheritance_activity_missing')
    return {'status':'pass','inherited_from':source_batch,'elapsed':0,'session_outcomes':17,
        'files':{name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in names},'browser_input':identity}

def actual_main(selected,reason,repository_tests=None,http_tests=None,reuse_windows_batch=None,browser_controls_only=False):
    ledger=Ledger(); value=ledger.load()
    # 实际模式一进入就记尝试；计划/版本预检失败也不释放入口。
    ledger.consume('real_entries',{'stages':selected,'reason':reason})
    if value['counts']['real_entries'] and not reason: raise ControlRefusal('corrected_affected_scope_reason_required')
    if not value['counts']['real_entries'] and selected!=list(STAGES): raise ControlRefusal('first_entry_must_be_complete')
    plan=json.loads((EVIDENCE/'execution-plan.json').read_text(encoding='utf-8'))
    current=hash_files(source_paths())
    documents=verify_run_files(current,plan['files'],value['events'])
    builds=[e for e in value['events'] if e.get('event')=='frontend_build_pass']
    if not builds:raise ControlRefusal('frontend_dist_build_missing')
    built=builds[-1]['detail']
    if any(digest!=current.get(path) for path,digest in built['files'].items() if path.startswith('frontend/src/') or path=='frontend/package.json'):
        raise ControlRefusal('frontend_source_changed_after_only_build')
    if hash_files(list((ROOT/'frontend/dist').rglob('*')))!=built['dist']:raise ControlRefusal('frontend_dist_changed')
    inherited=inherit_windows(reuse_windows_batch,current) if reuse_windows_batch else None
    if browser_controls_only and (not inherited or 'windows' in selected or 'browser' not in selected):
        raise ControlRefusal('controls_only_requires_validated_windows_inheritance')
    remaining=TIME_LIMITS['real']-value['seconds']['real']
    batch=Batch('main-combo',Deadline(min(1800,remaining,active_remaining(value))))
    batch.state['cleanup_remaining']=TIME_LIMITS['cleanup']-value['seconds']['cleanup']
    atomic_json(batch.directory/'as-run-files.json',current)
    atomic_json(batch.directory/'as-run-documentation.json',documents)
    started=time.monotonic()
    try:
        batch.stage('container',batch.container)
        batch.stage('database',batch.database,('container',))
        data=ROOT/'backend/tests/data/task100/continuation-02/originals';data.mkdir(parents=True,exist_ok=True)
        batch.env['RETROLUME_TASK100_ORIGINALS_DIR']=str(data)
        if 'migration_scenarios' in selected:
            batch.stage('migration_scenarios',lambda:batch.process('migration-raw',[str(PYTHON),'-B','-m','tests.fixtures.task100.pg_migration_scenarios'],300),('database',))
        if 'repository' in selected:
            batch.stage('repository',lambda:batch.process('repository-raw',[str(PYTHON),'-B','-m','unittest',*(repository_tests or PG_TESTS),'-v'],300),('database',))
        else: batch.results.append({'name':'repository','status':'pass','inherited_from':reason,'elapsed':0})
        if any(s in selected for s in ('application','http','windows','browser')):
            batch.stage('application',batch.application,('database','repository'))
        if 'http' in selected:
            batch.stage('http',lambda:batch.process('http-raw',[str(PYTHON),'-B','-m','unittest',*(http_tests or ['tests.test_teaching_api.HttpTests']),'-v'],120),('application',))
        else: batch.results.append({'name':'http','status':'pass','inherited_from':reason,'elapsed':0})
        if 'windows' in selected:
            batch.stage('windows',lambda:batch.process('windows-raw',[str(PYTHON),'-B','-m','tests.fixtures.task100.windows_chain'],800),('http',))
        elif inherited:
            batch.results.append({'name':'windows',**{k:v for k,v in inherited.items() if k!='browser_input'}})
            identity={**inherited['browser_input'],'batch_dir':str(batch.directory),'inherited_windows_batch':reuse_windows_batch}
            atomic_json(batch.directory/'browser-input.json',identity)
            atomic_json(batch.directory/'windows-inheritance.json',inherited)
        if 'browser' in selected:
            def browser():
                Ledger().consume('driver',{'entry':'frontend/tests/task100-browser.cjs'})
                argv=['node',str(ROOT/'frontend/tests/task100-browser.cjs')]
                if browser_controls_only:argv.append('--controls-only')
                return batch.process('browser-raw',argv,240,cwd=ROOT/'frontend')
            batch.stage('browser',browser,('windows',))
    finally:
        elapsed=time.monotonic()-started
        try: ledger.charge('real',elapsed,{'batch':str(batch.directory),'stages':batch.results})
        finally: batch.cleanup()
        atomic_json(batch.directory/'summary.json',{'status':aggregate(batch.results),'segments':batch.results,'elapsed':elapsed,'cleanup_budget_separate':True})
    return 0 if aggregate(batch.results)=='pass' else 1

def offline(mode):
    ledger=Ledger(); value=ledger.load()
    batch=Batch(mode,Deadline(min(600,TIME_LIMITS['offline']-value['seconds']['offline'],active_remaining(value))))
    files=hash_files(source_paths());atomic_json(batch.directory/'as-run-files.json',files)
    start=time.monotonic()
    try:
        if mode=='offline':
            result=batch.process('offline-raw',[str(PYTHON),'-B','-m','unittest',*OFFLINE_TESTS,'-v'],600)
        elif mode=='typecheck':
            result=batch.process('typecheck-raw',['node',str(ROOT/'frontend/node_modules/typescript/bin/tsc'),'--noEmit'],300,cwd=ROOT/'frontend')
        elif mode=='browser-artifacts':
            result=batch.process('artifact-raw',[str(PYTHON),'-B','-m','tests.fixtures.task100.browser_artifacts'],30)
        else:
            ledger.consume('frontend_build',{'command':'npm run build'})
            result=batch.process('build-raw',['cmd','/c','npm','run','build'],600,cwd=ROOT/'frontend')
        atomic_json(batch.directory/'summary.json',result)
        if result['status']=='pass':
            if mode=='offline': ledger.note('offline_batch_pass',{'files':files,'batch':str(batch.directory)})
            if mode=='frontend-build': ledger.note('frontend_build_pass',{'files':files,'batch':str(batch.directory),
                'dist':hash_files(list((ROOT/'frontend/dist').rglob('*')))})
        print(mode,result['status'],str(batch.directory))
        return 0 if result['status']=='pass' else 1
    finally: ledger.charge('offline',time.monotonic()-start,{'mode':mode,'batch':str(batch.directory)})

def main():
    raise ControlRefusal('continuation02_permit_ended_use_current_repair_runner')
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['init','plan','budget','offline','typecheck','frontend-build','browser-artifacts','main-combo'])
    parser.add_argument('--stages');parser.add_argument('--reason');parser.add_argument('--repository-tests');parser.add_argument('--http-tests')
    parser.add_argument('--reuse-windows-batch');parser.add_argument('--browser-controls-only',action='store_true');args=parser.parse_args()
    if args.mode=='init': Ledger().initialize(json.loads((EVIDENCE/'preparation.json').read_text(encoding='utf-8')));return 0
    if args.mode=='budget': print(json.dumps(Ledger().load(),ensure_ascii=False,indent=2));return 0
    value=Ledger().checkpoint_active()
    if args.mode=='plan':
        start=time.monotonic()
        try:execution_plan();return 0
        finally:Ledger().charge('offline',time.monotonic()-start,{'mode':'plan'})
    if args.mode=='main-combo':
        selected=args.stages.split(',') if args.stages else list(STAGES)
        if any(s not in STAGES for s in selected): raise ControlRefusal('stage_not_allowed')
        names=args.repository_tests.split(',') if args.repository_tests else None
        if names:
            tests=json.loads((EVIDENCE/'execution-plan.json').read_text(encoding='utf-8'))['tests']
            allowed=set(PG_TESTS)|{method for cls in PG_TESTS for method in tests[cls]}
            if not args.reason or any(n not in allowed for n in names):raise ControlRefusal('affected_repository_class_not_allowed')
        http_names=args.http_tests.split(',') if args.http_tests else None
        if http_names:
            tests=json.loads((EVIDENCE/'execution-plan.json').read_text(encoding='utf-8'))['tests']
            if not args.reason or any(n not in tests['tests.test_teaching_api.HttpTests'] for n in http_names):
                raise ControlRefusal('affected_http_method_not_allowed')
        return actual_main(selected,args.reason,names,http_names,args.reuse_windows_batch,args.browser_controls_only)
    return offline(args.mode)

if __name__=='__main__':
    try: raise SystemExit(main())
    except ControlRefusal as exc:
        print('CONTROL_REFUSED',str(exc),file=sys.stderr);raise SystemExit(2)
