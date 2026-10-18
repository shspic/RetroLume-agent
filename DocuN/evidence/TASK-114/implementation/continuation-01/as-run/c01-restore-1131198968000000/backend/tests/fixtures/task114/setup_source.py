"""只创建卡面新合成 source，首 SQL 前核完整 CID，异常和 finally 均精确停止。"""
import argparse
import ctypes
import json
import os
from pathlib import Path
import secrets
import socket
import sys
import time
from uuid import uuid4

from budget import Budget,ROOT,CONTROL,EVIDENCE
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.control import ControlHub,CredentialVault
from app.data_exit.contracts import digest
from app.data_exit.restore import TargetRef,docker_call,inspect_target,TargetFactory

IMAGE='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
NAME='retrolume-task-114-data-source'
VOLUME=NAME+'-data'
DB='retrolume_task114_source'
PREFIX='retrolume_task114_'
SYNTHETIC=ROOT/'DocuN/evidence/TASK-114/synthetic'
REFERENCE=CONTROL/'source-reference.json'


class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total_phys',ctypes.c_ulonglong),
              ('available_phys',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('available_page',ctypes.c_ulonglong),
              ('total_virtual',ctypes.c_ulonglong),('available_virtual',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]


def memory_guard():
    value=Memory();value.length=ctypes.sizeof(value)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)):raise RuntimeError('内存观察不可用')
    result={'available_bytes':value.available_phys,'total_bytes':value.total_phys,'minimum_bytes':2*1024**3,
            'monotonic_ns':time.monotonic_ns(),'ready':value.available_phys>=2*1024**3}
    path=EVIDENCE/'observations'/('memory-before-'+str(time.monotonic_ns())+'.json')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def reference():
    value=json.loads(REFERENCE.read_text(encoding='utf-8'))
    target=TargetRef(**{**value['target'],'data_root':Path(value['target']['data_root'])})
    hub=ControlHub(SYNTHETIC/'control-root')
    credentials=CredentialVault(hub).read(value['credentials'])
    return target,credentials


def start_source(budget,target):
    identity=inspect_target(target,IMAGE)
    if identity['running']:raise RuntimeError('不借未登记 Running source')
    observation=memory_guard()
    if not observation['ready']:return False
    budget.reserve('pg_start');budget.begin(target.cid)
    try:
        docker_call(['start',target.cid]);budget.event('running_observed',inspect_target(target,IMAGE))
    except BaseException:
        stop_source(budget,target);raise
    return True


def stop_source(budget,target):
    identity=inspect_target(target,IMAGE)
    if identity['running']:docker_call(['stop','--time','10',target.cid],timeout=20)
    identity=inspect_target(target,IMAGE)
    if identity['running'] or identity['status'] not in ('exited','created'):raise RuntimeError('source 停止未知')
    budget.end(target.cid,identity)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fix-013',action='store_true');parser.add_argument('--resume-created',action='store_true');args=parser.parse_args()
    if args.fix_013 and args.resume_created:raise RuntimeError('续跑入口不可混用')
    budget=Budget();budget.check()
    observation=memory_guard()
    if not observation['ready']:
        print(json.dumps({'state':'not_run','reason':'available_memory_below_2GiB','available_bytes':observation['available_bytes']}))
        return 78
    hub=ControlHub(SYNTHETIC/'control-root')
    if REFERENCE.exists():
        if not (args.fix_013 or args.resume_created):raise RuntimeError('source 已登记，不自动重建或重复安装')
        if args.resume_created and json.loads(REFERENCE.read_text(encoding='utf-8'))['stage']!='created':raise RuntimeError('source 已执行初始化，不采用空库续跑')
        target,credentials=reference()
    else:
        if args.fix_013 or args.resume_created:raise RuntimeError('缺原 source，不能修正或续跑')
        if docker_call(['ps','-aq','--filter','name=^/'+NAME+'$']):raise RuntimeError('source 名称碰撞')
        if VOLUME in docker_call(['volume','ls','--format','{{.Name}}']).splitlines():raise RuntimeError('source 卷碰撞')
        with socket.socket() as probe:probe.bind(('127.0.0.1',55461))
        image=json.loads(docker_call(['image','inspect',IMAGE]))[0]
        if (image['Id'],image['Os'],image['Architecture'])!=(IMAGE,'linux','amd64'):raise RuntimeError('镜像身份不符')
        budget.reserve('pg_create')
        password=secrets.token_urlsafe(32);environment=dict(os.environ)
        environment.update(POSTGRES_USER=PREFIX+'admin',POSTGRES_PASSWORD=password,POSTGRES_DB=DB)
        job_id=str(uuid4())
        cid=docker_call(['create','--name',NAME,'--label','retrolume.task=TASK-114','--label','retrolume.data.job='+job_id,
            '--label','retrolume.data.profile=TASK-114-PG17','--cpus','1','--memory','512m','--pids-limit','128','--restart','no',
            '--publish','127.0.0.1:55461:5432','--mount',f'type=volume,src={VOLUME},dst=/var/lib/postgresql/data',
            '--env','POSTGRES_USER','--env','POSTGRES_PASSWORD','--env','POSTGRES_DB',IMAGE],environment=environment)
        target=TargetRef(str(uuid4()),job_id,'TASK-114-PG17',cid,NAME,VOLUME,55461,str(uuid4()),str(uuid4()),str(uuid4()),SYNTHETIC/'source-root')
        identity=inspect_target(target,IMAGE);budget.reserve('pg_success');budget.created(cid,'pg',identity)
        from psycopg.conninfo import make_conninfo
        credentials={'admin_dsn':make_conninfo(host='127.0.0.1',port=55461,dbname=DB,user=PREFIX+'admin',password=password),
                     'maintenance_key':secrets.token_hex(32)}
        credential_ref=CredentialVault(hub).save(credentials)
        data={'target':{**target.__dict__,'data_root':str(target.data_root)},'credentials':credential_ref,'stage':'created'}
        REFERENCE.write_text(json.dumps(data,indent=2),encoding='utf-8')
    if not start_source(budget,target):
        print(json.dumps({'state':'not_run','reason':'available_memory_changed'}));return 78
    try:
        TargetFactory._wait_pg(credentials['admin_dsn'])
        import psycopg
        from psycopg import sql
        from psycopg.conninfo import make_conninfo
        from app.data_exit.schema import MIGRATIONS,MIGRATION_013
        with psycopg.connect(credentials['admin_dsn'],autocommit=True,connect_timeout=3) as connection:
            count=connection.execute("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r'").fetchone()[0]
            if not args.fix_013 and count!=0:raise RuntimeError('source 非空，拒绝安装')
            if args.fix_013 and connection.execute("SELECT to_regclass('public.data_control')").fetchone()[0] is not None:raise RuntimeError('013 已存在，不能覆盖')
            for path in sorted((ROOT/'backend/migrations').glob('*.sql')):
                number=int(path.name[:3])
                if not 1<=number<=13 or (args.fix_013 and number!=13):continue
                if digest(path.read_bytes())!=(MIGRATION_013 if number==13 else MIGRATIONS[path.name]):raise RuntimeError('迁移字节漂移')
                if number==13:
                    from seed_legacy import seed_before_013
                    legacy=seed_before_013(credentials['admin_dsn'])
                connection.execute(path.read_text(encoding='utf-8-sig'))
            from seed_legacy import business_rows
            after=business_rows(credentials['admin_dsn'])
            if after!=legacy['business_rows']:raise RuntimeError('013 改写了已有业务值')
            (CONTROL/'source-013-business-preservation.json').write_text(json.dumps({'before':legacy['business_rows'],'after':after,'equal':True},indent=2),encoding='utf-8')
            connection.execute("INSERT INTO public.data_control(dataset_id,instance_id,schema_profile,mode,originals_root_id,maintenance_key_sha256) VALUES(%s,%s,'data_exit.v1.r01','normal',%s,%s)",
                               (target.dataset_id,target.instance_id,target.root_id,digest(credentials['maintenance_key'])))
            for suffix in ('app','snapshot','readonly','loader','denied'):
                password=secrets.token_urlsafe(32)
                connection.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}').format(sql.Identifier(PREFIX+suffix),sql.Literal(password)))
                credentials[suffix+'_dsn']=make_conninfo(host='127.0.0.1',port=55461,dbname=DB,user=PREFIX+suffix,password=password)
            for role in ('retrolume_data_app','retrolume_memory_app','retrolume_interview_app','retrolume_html_app'):
                connection.execute(sql.SQL('GRANT {} TO {}').format(sql.Identifier(role),sql.Identifier(PREFIX+'app')))
            for suffix in ('snapshot','readonly'):
                connection.execute(sql.SQL('GRANT retrolume_data_snapshot TO {}').format(sql.Identifier(PREFIX+suffix)))
            connection.execute('GRANT SELECT,INSERT,UPDATE ON public.material_sources,public.material_versions,public.pdf_review_candidates,public.pdf_extracted_pages,public.pdf_review_pages,public.pdf_user_supplements,public.activities,public.activity_scope_sources,public.activity_allowed_models,public.activity_operations,public.activity_operation_results,public.teaching_commands,public.teaching_records,public.teaching_heads TO retrolume_data_app')
            version=int(connection.execute('SHOW server_version_num').fetchone()[0])
            if version//10000!=17:raise RuntimeError('server major 不符')
            roles=connection.execute("SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname LIKE 'retrolume_data_%' OR rolname LIKE 'retrolume_task114_%' ORDER BY rolname").fetchall()
        credential_ref=CredentialVault(hub).save(credentials)
        data={'target':{**target.__dict__,'data_root':str(target.data_root)},'credentials':credential_ref,'stage':'initialized'}
        REFERENCE.write_text(json.dumps(data,indent=2),encoding='utf-8')
        (CONTROL/'source-schema-role-identity.json').write_text(json.dumps({'cid':target.cid,'server_version_num':version,'roles':roles,'dataset_id':target.dataset_id,'instance_id':target.instance_id},indent=2),encoding='utf-8')
        print(json.dumps({'state':'initialized','cid':target.cid,'server_version_num':version}))
        return 0
    except BaseException as error:
        budget.event('source_initialization_failed',{'error_type':type(error).__name__,'sqlstate':getattr(error,'sqlstate',None)})
        (CONTROL/('source-initialization-failure-'+str(time.monotonic_ns())+'.txt')).write_text(str(error),encoding='utf-8')
        print(json.dumps({'state':'failed','error_type':type(error).__name__,'sqlstate':getattr(error,'sqlstate',None)}))
        return 1
    finally:stop_source(budget,target)


if __name__=='__main__':raise SystemExit(main())
