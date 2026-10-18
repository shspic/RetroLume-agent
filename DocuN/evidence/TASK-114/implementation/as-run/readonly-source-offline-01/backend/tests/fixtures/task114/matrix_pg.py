"""固定新 source/target 的连续真实 PG 批次，有界预算及准确 finally。"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import shutil
import sys
import time
from uuid import uuid4
from budget import ROOT,CONTROL,Budget,FactoryHooks
sys.path.insert(0,str(ROOT/'backend'))
from setup_source import reference,start_source,stop_source,SYNTHETIC
from freeze import freeze
from app.data_exit.contracts import TABLES,canonical,DataJobCommand,DataError,digest
from app.data_exit.codec import plain
from app.data_exit.files import RootLease
from app.data_exit.packages import PackageReader
from app.data_exit.repository import DataRepository
from app.data_exit.restore import inspect_target
from app.runtime import psycopg_compatible_loop_factory


def profile():
    return {'enabled':True,'snapshot_url_env':'RETROLUME_DATA_SNAPSHOT_URL','maintenance_key_env':'RETROLUME_DATA_MAINTENANCE_KEY',
            'factory':{'id':'TASK-114-PG17','image_id':'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
                       'pg_major':17,'login_prefix':'retrolume_task114_','source_name':'retrolume-task-114-data-source',
                       'slots':[{'id':f'target{n:02}','name':f'retrolume-task-114-data-target{n:02}',
                                 'volume':f'retrolume-task-114-data-target{n:02}-data','port':55461+n,'database':'retrolume_task114_target'} for n in range(1,9)]}}


def environment(credentials):
    path=SYNTHETIC/'scratch/data-exit.json'
    expected=canonical(profile()).encode('utf-8')
    if path.exists() and path.read_bytes()!=expected:raise RuntimeError('本卡 host profile 发生漂移')
    if not path.exists():path.write_bytes(expected)
    values={'RETROLUME_DATA_DIR':str(SYNTHETIC/'source-root'),'RETROLUME_BACKUP_DIR':str(SYNTHETIC/'backup-root'),
            'RETROLUME_CONTROL_ROOT':str(SYNTHETIC/'control-root'),'RETROLUME_RESTORE_ROOT':str(SYNTHETIC/'restore-root'),
            'RETROLUME_DATABASE_URL':credentials['app_dsn'],'RETROLUME_DATA_SNAPSHOT_URL':credentials['snapshot_dsn'],
            'RETROLUME_DATA_MAINTENANCE_KEY':credentials['maintenance_key'],'RETROLUME_DATA_EXIT_CONFIG':str(path)}
    os.environ.update(values)
    os.environ.pop('RETROLUME_PREVIEW_CONFIG',None)
    return values


def permissions(runtime,credentials):
    import psycopg
    rejected=[]
    statements=["UPDATE public.activities SET requests_reserved=requests_reserved",'SELECT maintenance_key_sha256 FROM public.data_control',
                'SELECT pin_nonce_sha256 FROM public.data_operation_jobs',"SELECT public.data_source_delete(NULL,0,'x',NULL,'[]','wrong')"]
    for query in statements:
        try:
            with psycopg.connect(credentials['snapshot_dsn'],connect_timeout=3) as connection:connection.execute(query)
        except psycopg.Error as error:
            if error.sqlstate!='42501':raise
            rejected.append(error.sqlstate)
        else:raise RuntimeError('snapshot 权限越界')
    with psycopg.connect(credentials['app_dsn'],connect_timeout=3) as connection:
        member=connection.execute("SELECT pg_has_role(SESSION_USER,'retrolume_data_restore_loader','MEMBER')").fetchone()[0]
    if member:raise RuntimeError('source 不得有 loader 成员')
    return {'snapshot_rejections':rejected,'source_loader_member':member}


async def scenario(runtime,credentials,budget,output,seed_new):
    from seed_full import seed
    from seed_legacy import business_rows
    record=CONTROL/'source-full-fixture.json'
    if seed_new:
        if record.exists():raise RuntimeError('全域 fixture 已登记，不自动重复种子')
        identities=await seed(runtime)
        record.write_text(json.dumps(identities,ensure_ascii=False,indent=2),encoding='utf-8')
    elif not record.exists():raise RuntimeError('未有完整 fixture；先查原失败，不盲重播种')
    else:identities=json.loads(record.read_text(encoding='utf-8'))
    result={'permissions':permissions(runtime,credentials),'fixture':identities,'source_rows':business_rows(credentials['app_dsn'])}
    result['nonempty_tables']=[t for t,rows in result['source_rows'].items() if rows['count']]
    if len(result['nonempty_tables'])!=28:raise RuntimeError('全 28 表样本不完整')
    command=DataJobCommand('restore_checkpoint',str(uuid4()),{'mode':'all','source_ids':[],'activity_ids':[],'allow_incomplete':False})
    job=runtime.hub.create_or_get_job(command,runtime.context())
    receipt=await asyncio.to_thread(runtime.packages.capture_and_publish,job['job_id'],command.scope)
    backup=runtime.packages.download(job['job_id'])
    with PackageReader(backup) as reader:
        result['package']={'job':receipt,'manifest':reader.manifest,'file_sha256':digest(backup.read_bytes())}
        # 独立标准 JSON/ZIP 工具核逐表 hash 和 PDF/文本原字节，不依赖应用回查。
        import zipfile,hashlib
        with zipfile.ZipFile(backup) as archive:
            for entry in reader.manifest['contents']:
                raw=archive.read(entry['path'])
                if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise RuntimeError('独立 hash 核对失败')
                if entry['path'].endswith('.jsonl'):
                    for line in raw.splitlines():json.loads(line)
        result['independent_reader']={'jsonl':True,'sha256':True,'executed_code':False}
    upload=str(uuid4());destination=runtime.incoming/(upload+'.rldata')
    with destination.open('xb') as stream,backup.open('rb') as original:shutil.copyfileobj(original,stream,65536)
    plan=runtime.restore.prepare(upload,'respect_current_deletions',runtime.context())
    restore=runtime.hub.create_or_get_job(DataJobCommand('restore',str(uuid4()),{'plan_id':plan['plan_id'],'plan_sha256':plan['plan_sha256']}),runtime.context())
    verified=await asyncio.to_thread(runtime.restore.verify,restore['job_id'],plan['plan_sha256'])
    result.update(plan=plan,restore=verified,source_after=business_rows(credentials['app_dsn']))
    if result['source_after']!=result['source_rows']:raise RuntimeError('恢复改写 source 业务事实')
    target=runtime.factory.target(verified['target_id']);reference=runtime.factory.readonly_credentials(target.target_id)
    runtime.factory.start(target)
    try:
        runtime.factory._wait_pg(reference['readonly_dsn'])
        result['sealed_probe']=runtime.factory._probe_readonly(reference['readonly_dsn'],target)
        result['target_rows']=business_rows(reference['readonly_dsn'])
        result['target_identity']=inspect_target(target,runtime.factory.profile['image_id'])
    finally:runtime.factory.stop(target)
    result['status']='passed_this_batch'
    (output/'result.json').write_text(json.dumps(plain(result),ensure_ascii=False,indent=2),encoding='utf-8')
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('label');parser.add_argument('--seed-new',action='store_true');args=parser.parse_args()
    budget=Budget();budget.check()
    target,credentials=reference()
    if not start_source(budget,target):
        print(json.dumps({'state':'not_run','reason':'memory_start_guard'}));return 78
    output=ROOT/'DocuN/evidence/TASK-114/implementation/batches'/args.label
    output.mkdir(parents=True)
    runtime=None
    try:
        freeze(args.label)
        environment(credentials)
        from app.main import create_app
        app=create_app();runtime=app.state.data_exit
        if runtime is None:raise RuntimeError('新 source runtime 未就绪：'+str(app.state.data_exit_error))
        runtime.factory.hooks=FactoryHooks(budget)
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            result=runner.run(scenario(runtime,credentials,budget,output,args.seed_new))
        print(json.dumps({'state':result['status'],'nonempty_tables':len(result['nonempty_tables']),'batch':args.label}))
        return 0
    except BaseException as error:
        failure={'state':'failed','error_type':type(error).__name__,'code':getattr(error,'code',None),'sqlstate':getattr(error,'sqlstate',None)}
        budget.event('pg_batch_failure',{'label':args.label,**failure})
        import traceback
        message=traceback.format_exc()
        from psycopg.conninfo import conninfo_to_dict
        secrets=[credentials['maintenance_key']]
        for key,value in credentials.items():
            if key.endswith('_dsn'):secrets.extend([value,conninfo_to_dict(value).get('password','')])
        for secret in secrets:
            if secret:message=message.replace(secret,'[已隐藏私密值]')
        causes=[];cause=error
        for _ in range(8):
            if cause is None:break
            primary=getattr(getattr(cause,'diag',None),'message_primary',None)
            if primary:
                for secret in secrets:
                    if secret:primary=primary.replace(secret,'[已隐藏私密值]')
            causes.append({'type':type(cause).__name__,'sqlstate':getattr(cause,'sqlstate',None),'message_primary':primary})
            cause=cause.__context__
        (output/'causes.json').write_text(json.dumps(causes,ensure_ascii=False,indent=2),encoding='utf-8')
        (output/'failure.txt').write_text(message,encoding='utf-8')
        (output/'result.json').write_text(json.dumps(failure,indent=2),encoding='utf-8')
        print(json.dumps(failure));return 1
    finally:
        try:
            if runtime is not None:
                for value in runtime.hub.state()['targets'].values():
                    if 'cid' not in value:continue
                    from app.data_exit.restore import TargetRef
                    exact=TargetRef(value['target_id'],value['job_id'],value['profile_id'],value['cid'],value['name'],value['volume'],value['port'],value['dataset_id'],value['instance_id'],value['root_id'],runtime.factory.root/value['job_id'])
                    runtime.factory.stop(exact)
        finally:stop_source(budget,target)


if __name__=='__main__':raise SystemExit(main())
