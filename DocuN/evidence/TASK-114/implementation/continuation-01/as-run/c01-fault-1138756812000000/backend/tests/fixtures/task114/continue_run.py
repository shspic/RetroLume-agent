"""续作合并入口：逐阶段原观察落盘，有限root/资源账和精确finally。"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
from uuid import uuid4
from budget import Budget,ROOT,CONTROL,EVIDENCE,FactoryHooks
sys.path.insert(0,str(ROOT/'backend'))
from setup_source import reference,memory_guard,IMAGE,stop_source
from matrix_pg import environment
from freeze import freeze
from app.data_exit.contracts import DataJobCommand,canonical,digest,TABLES
from app.data_exit.codec import plain
from app.data_exit.restore import inspect_target,TargetRef

PLAN_ID='271e9dd7-e982-4daa-9854-4beffac445a1'
PACKAGE_ID='737bf7ba-18c2-436c-a011-3aabbc1a8b2b'

class Evidence:
    def __init__(self,label,credentials):
        self.path=EVIDENCE/'batches'/label;self.path.mkdir(parents=True)
        self.secrets=[]
        from psycopg.conninfo import conninfo_to_dict
        for k,v in credentials.items():
            if isinstance(v,str):
                if k.endswith('_dsn'):self.secrets.extend([v,conninfo_to_dict(v).get('password','')])
                elif k=='maintenance_key':self.secrets.append(v)
    def scrub(self,value):
        for secret in sorted(self.secrets,key=len,reverse=True):
            if secret:value=value.replace(secret,'[private value removed]')
        return value
    def observe(self,name,value):
        raw=self.scrub(json.dumps(plain(value),ensure_ascii=False,indent=2))
        with (self.path/(name+'.json')).open('x',encoding='utf-8') as f:f.write(raw)
        print(json.dumps({'observation':name,'path':str(self.path/(name+'.json'))}),flush=True)
    def fail(self,error):
        (self.path/'failure.txt').write_text(self.scrub(traceback.format_exc()),encoding='utf-8')
        causes=[];cause=error
        for _ in range(10):
            if cause is None:break
            causes.append({'type':type(cause).__name__,'sqlstate':getattr(cause,'sqlstate',None),'code':getattr(cause,'code',None),'message_primary':getattr(getattr(cause,'diag',None),'message_primary',None)})
            cause=cause.__cause__ or cause.__context__
        self.observe('failure',{'state':'failed','causes':causes})

def runtime_for(credentials,budget):
    environment(credentials)
    from app.main import create_app
    app=create_app();runtime=app.state.data_exit
    if runtime is None:raise RuntimeError('合成配置入口不可用')
    runtime.factory.hooks=FactoryHooks(budget)
    return app,runtime

def restore_group(budget,evidence,source,credentials):
    if inspect_target(source,IMAGE)['running']:raise RuntimeError('第一恢复要求source停止')
    app,runtime=runtime_for(credentials,budget)
    initialize=runtime.factory._initialize
    def observed_initialize(target,credential,slot):
        initialize(target,credential,slot)
        state=runtime.hub.state()['targets'][target.target_id]
        evidence.observe('03a-initialized',{'target_id':target.target_id,'slot':slot['id'],'schema_identity':state['schema_identity'],'identity':inspect_target(target,IMAGE)})
        import psycopg
        with psycopg.connect(credential['loader_dsn'],connect_timeout=3) as conn:
            evidence.observe('03b-loading-role',{'allowed':conn.execute('SELECT public.data_loading_allowed()').fetchone()[0],
                'attributes':conn.execute("SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolbypassrls FROM pg_roles WHERE rolname=SESSION_USER").fetchone(),
                'two_fks':conn.execute("SELECT conname,condeferrable,condeferred FROM pg_constraint WHERE conrelid='public.teaching_commands'::regclass AND contype='f' ORDER BY conname").fetchall()})
    runtime.factory._initialize=observed_initialize
    load=runtime.restore._load
    def observed_load(reader,target,plan):
        proof=load(reader,target,plan);evidence.observe('03c-loaded',proof);return proof
    runtime.restore._load=observed_load
    record=runtime.hub.state()['plans'].get(PLAN_ID)
    if record is None:raise RuntimeError('准确旧plan缺失')
    plan=runtime.restore.plan(PLAN_ID,record['plan_sha256'])
    path=runtime.incoming/(plan['upload_id']+'.rldata')
    if digest(path.read_bytes())!='45177d58ea58fcaa704bfdd48641aceade7ca6e6f4fe5d6759b3a46bf2671665':raise RuntimeError('旧包漂移')
    if plan['deletion_policy']!='respect_current_deletions':raise RuntimeError('旧删除策略不符')
    evidence.observe('01-plan-identity',{'plan_id':PLAN_ID,'plan_sha256':record['plan_sha256'],'package_sha256':plan['package_sha256'],'package_root_sha256':plan['package_root_sha256'],'latest_status_observed':plan['latest_status'],'overlay_count':len(plan['overlay']),'source_latest_live_now':'unknown-source-stopped','source_stopped':True})
    command=DataJobCommand('restore','c01-restore-'+str(uuid4()),{'plan_id':PLAN_ID,'plan_sha256':record['plan_sha256']})
    job=runtime.hub.create_or_get_job(command,runtime.context());evidence.observe('02-restore-job',job)
    verified=runtime.restore.verify(job['job_id'],record['plan_sha256'])
    evidence.observe('03-verified',verified)
    state=runtime.hub.state();target=runtime.factory.target(verified['target_id'])
    evidence.observe('04-seal', {k:v for k,v in state['targets'][target.target_id].items() if k not in ('credential_ref',)})
    credential=runtime.factory.readonly_credentials(target.target_id)
    runtime.factory.start(target)
    try:
        runtime.factory._wait_pg(credential['readonly_dsn'])
        import psycopg
        from seed_legacy import business_rows
        actual=business_rows(credential['readonly_dsn'])
        evidence.observe('05-target-business-rows',actual)
        evidence.observe('06-readonly-rejections',runtime.factory._probe_readonly(credential['readonly_dsn'],target))
        with psycopg.connect(credential['readonly_dsn'],connect_timeout=3) as conn:
            evidence.observe('07-sealed-roles',conn.execute("SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,pg_has_role(rolname,'retrolume_data_restore_loader','MEMBER') FROM pg_roles WHERE rolname LIKE 'retrolume_task114_%' ORDER BY rolname").fetchall())
        evidence.observe('08-source-still-stopped',inspect_target(source,IMAGE))
    finally:runtime.factory.stop(target)
    return {'state':'passed','target_id':target.target_id,'restore_job_id':job['job_id']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('method',choices=['restore','source','race','fault']);args=parser.parse_args()
    budget=Budget();budget.check()
    if not memory_guard()['ready']:
        print(json.dumps({'state':'not_run','reason':'memory_gate'}));return 78
    source,credentials=reference()
    label='c01-'+args.method+'-'+str(time.monotonic_ns());evidence=Evidence(label,credentials)
    root='c01-'+args.method+'-group';budget.root(root)
    budget.event('command.begin',{'label':label,'arguments':sys.argv,'group_root':root})
    start=time.monotonic();runtime=None
    try:
        freeze(label)
        if args.method=='restore':result=restore_group(budget,evidence,source,credentials)
        elif args.method=='source':
            from continue_source import source_group
            result=source_group(budget,evidence,source,credentials)
        elif args.method=='race':
            from continue_race import race_group
            result=race_group(budget,evidence,source,credentials)
        else:
            from continue_fault import fault_group
            result=fault_group(budget,evidence,source,credentials)
        evidence.observe('result',result);budget.close_root(root);return 0
    except BaseException as error:
        evidence.fail(error);return 1
    finally:
        # 精确自有对象外层兜底；只读inspect不发全局停止。
        from app.data_exit.control import ControlHub
        hub=ControlHub(ROOT/'DocuN/evidence/TASK-114/synthetic/control-root')
        from app.data_exit.restore import docker_call
        for value in hub.state()['targets'].values():
            if 'cid' not in value:continue
            target=TargetRef(value['target_id'],value['job_id'],value['profile_id'],value['cid'],value['name'],value['volume'],value['port'],value['dataset_id'],value['instance_id'],value['root_id'],ROOT/'DocuN/evidence/TASK-114/synthetic/restore-root'/value['job_id'])
            identity=inspect_target(target,IMAGE)
            if identity['running']:docker_call(['stop','--time','10',target.cid],timeout=20)
            identity=inspect_target(target,IMAGE)
            if identity['running']:raise RuntimeError('准确目标停止未知')
            budget.end(target.cid,identity)
        evidence.observe('99-source-stop',inspect_target(source,IMAGE))
        budget.event('command.end',{'label':label,'seconds':time.monotonic()-start,'group_root':root})

if __name__=='__main__':raise SystemExit(main())
