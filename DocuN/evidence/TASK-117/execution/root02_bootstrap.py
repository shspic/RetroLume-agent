"""仅初始化本卡两专用PG及非空迁移旧形状；不作为普通运行ACL证明。"""
from pathlib import Path
import asyncio
import io
import json
import sys
from uuid import uuid4
from datetime import datetime,timedelta,timezone
from control import ROOT,HERE,event,state,write,sha,failure,guard
from runtime_control import create_pg,dsn,credentials,PRIVATE
sys.path.insert(0,str(ROOT/'backend'))
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from app.data_exit.schema import MIGRATIONS,MIGRATION_013
from app.data_exit.contracts import digest,DataContext,DataJobCommand
from app.capabilities.contracts import build_business_payload
from app.activities.repository import PostgresAdmissionLedger,ActivitySpec,SourceSnapshot
from app.learning.teaching_contracts import TeachingCommandInput
from app.materials.repository import PostgresMaterials
from app.storage.originals import OriginalStore
from app.runtime import psycopg_compatible_loop_factory


def migration(connection,number):
    path=next((ROOT/'backend/migrations').glob(f'{number:03d}_*.sql'))
    actual=sha(path.read_bytes())
    if number<=12 and actual!=MIGRATIONS[path.name] or number==13 and actual!=MIGRATION_013:raise RuntimeError('old_trusted_migration_changed')
    event('migration_attempt',database=connection.info.dbname,name=path.name,sha256=actual)
    connection.execute(path.read_text(encoding='utf-8-sig'))
    event('migration_committed',database=connection.info.dbname,name=path.name)


def normal_control(slot):
    identity={'dataset_id':str(uuid4()),'instance_id':str(uuid4()),'originals_root_id':str(uuid4()),'schema_profile':'data_exit.v1.r01' if slot=='compat' else 'data_exit.v1.r02'}
    with psycopg.connect(dsn(slot,'admin')) as connection:
        connection.execute("INSERT INTO public.data_control(dataset_id,instance_id,originals_root_id,schema_profile,mode,maintenance_key_sha256) VALUES(%s,%s,%s,%s,'normal',%s)",
          (identity['dataset_id'],identity['instance_id'],identity['originals_root_id'],identity['schema_profile'],digest(credentials(slot)['maintenance_key'])))
        c=credentials(slot)
        for role in ('app','snapshot'):
            connection.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}').format(sql.Identifier(c[role+'_user']),sql.Literal(c[role+'_password'])))
            groups=['retrolume_data_snapshot'] if role=='snapshot' else ['retrolume_data_app','retrolume_memory_app','retrolume_interview_app','retrolume_html_app']+(['retrolume_retrieval_app'] if slot=='source' else [])
            for group in groups:connection.execute(sql.SQL('GRANT {} TO {}').format(sql.Identifier(group),sql.Identifier(c[role+'_user'])))
    write(HERE/f'{slot}-dataset.json',identity)


async def seed_legacy():
    folder=HERE/'synthetic/compat-data';folder.mkdir(parents=True,exist_ok=True);originals=folder/'originals';originals.mkdir(exist_ok=True)
    sample=json.loads((ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json').read_text(encoding='utf-8'))['sources'][0]
    raw=sample['text'].encode('utf-8');store=OriginalStore(originals);obj=store.put(io.BytesIO(raw),max_bytes=5*1024**2)
    materials=PostgresMaterials(dsn('compat','admin'))
    source=materials.save(source_id=None,expected_version=None,filename=sample['filename'],format='md',sha256=obj.sha256,size=obj.size)
    aid=str(uuid4());ledger=PostgresAdmissionLedger(dsn('compat','admin'))
    await ledger.create_activity(ActivitySpec(aid,(SourceSnapshot(str(source['id']),str(source['version_id']),source['revision']),),datetime.now(timezone.utc)+timedelta(hours=24),80,20000000,250000,65536,4096,3600,(('deepseek_chat_completions','deepseek-chat'),),('finite_calculate',),max_tool_calls=8))
    command=TeachingCommandInput(business_key=str(uuid4()),expected_revision=0,expected_goal_version=0,expected_scope_revision=1,action='goal',body={'goal':'根据速度.md学习单位换算。'})
    await ledger.apply_teaching_local(aid,command)
    fmt,body,body_sha=build_business_payload(text='合成迁移前已提交正文，仅用于旧字节与预算保留核对。')
    with psycopg.connect(dsn('compat','admin')) as connection:
        for name,kind,disposition in (('legacy-model','model','received'),('legacy-tool','tool','received'),('legacy-unknown','model','unknown')):
            admission=str(uuid4());tool=kind=='tool'
            connection.execute('''INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,execution_generation,scope_revision,provider,configured_model,request_bytes,max_output_tokens,tool_names,reserved_cost_microunits,kind,arguments_sha256,tool_call_id,state,disposition,recorded_at)
              VALUES(%s,%s,%s,'fixture.initialization',0,1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP)''',
              (aid,name,admission,None if tool else 'deepseek_chat_completions',None if tool else 'deepseek-chat',None if tool else 64,None if tool else 1,['finite_calculate'] if tool else [],0 if tool else 250000,kind,digest('synthetic.finite.add') if tool else None,'fixture-tool-call' if tool else None,disposition,disposition))
            if kind=='model' and disposition=='received':
                connection.execute('INSERT INTO activity_operation_results(activity_id,operation_id,admission_id,execution_generation,scope_revision,payload_format,payload,payload_sha256) VALUES(%s,%s,%s,0,1,%s,%s,%s)',(aid,name,admission,fmt,body,body_sha))
        connection.execute('UPDATE activities SET requests_reserved=2,cost_reserved_microunits=500000,tools_reserved=1 WHERE id=%s',(aid,))
    write(HERE/'compat-legacy-fixture.json',{'activity_id':aid,'source':source,'original_bytes':len(raw),'original_sha256':obj.sha256,
      'types':['model_received','tool_received_NULL_request_token_zero_cost','model_unknown','teaching_goal'],'provider_calls':0,'actual_fee':0,
      'initialization_role':'本卡新cluster bootstrap仅建迁移前golden rows；不作为普通角色运行/ACL证据'})


def r01_package():
    from app.data_exit.control import ControlHub
    from app.data_exit.repository import DataRepository
    from app.data_exit.packages import DataPackageService
    from app.data_exit.snapshot import SnapshotCoordinator
    from app.data_exit.files import RootLease
    base=HERE/'synthetic/compat-data';backup=HERE/'synthetic/compat-backup';backup.mkdir(exist_ok=True)
    control=HERE/'synthetic/compat-control';control.mkdir(exist_ok=True)
    hub=ControlHub(control);observed=DataRepository(dsn('compat')).state();hub.commit('source.register',observed)
    context=DataContext(hub.control_id,0,observed['dataset_id'],observed['instance_id'],'normal')
    scope={'mode':'all','source_ids':[],'activity_ids':[],'allow_incomplete':False}
    job=hub.create_or_get_job(DataJobCommand('restore_checkpoint',str(uuid4()),scope),context)
    store=OriginalStore(base/'originals');lease=RootLease(store.root)
    coordinator=SnapshotCoordinator(dsn('compat','snapshot'),store,lease,backup)
    service=DataPackageService(hub,coordinator,backup)
    receipt=service.capture_and_publish(job['job_id'],scope)
    write(HERE/'compat-r01-package-receipt.json',receipt)
    lease.close();event('r01_pre014_package_saved',receipt=receipt)


def catalog(slot):
    with psycopg.connect(dsn(slot,'admin'),row_factory=dict_row) as connection:
        return {'constraints':connection.execute("SELECT conname,pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conname IN('interview_command_execution','activity_operations_kind_domain','activity_operations_kind_shape') ORDER BY conname").fetchall(),
          'functions':connection.execute("SELECT p.proname,p.prosrc FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname IN('interview_head_guard','interview_record_insert_guard','interview_result_eligible') ORDER BY p.proname").fetchall(),
          'legacy':connection.execute('SELECT operation_id,kind,request_bytes,max_output_tokens,reserved_cost_microunits,state,disposition FROM activity_operations ORDER BY operation_id').fetchall()}


def main():
    guard()
    if state()['active_root']!=2:raise RuntimeError('root_identity')
    create_pg('compat')
    with psycopg.connect(dsn('compat','admin'),autocommit=True) as connection:
        for number in range(1,13):migration(connection,number)
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(seed_legacy())
    with psycopg.connect(dsn('compat','admin'),autocommit=True) as connection:migration(connection,13)
    normal_control('compat');write(HERE/'compat-catalog-before014.json',catalog('compat'))
    r01_package()
    with psycopg.connect(dsn('compat','admin'),autocommit=True) as connection:migration(connection,14)
    after=catalog('compat');write(HERE/'compat-catalog-after014.json',after)
    before=json.loads((HERE/'compat-catalog-before014.json').read_text(encoding='utf-8'))
    if before['legacy']!=after['legacy']:raise RuntimeError('legacy_values_changed')
    with psycopg.connect(dsn('compat','admin')) as connection:
        c=credentials('compat');connection.execute(sql.SQL('GRANT retrolume_retrieval_app TO {}').format(sql.Identifier(c['app_user'])))
    create_pg('source')
    with psycopg.connect(dsn('source','admin'),autocommit=True) as connection:
        for number in range(1,15):migration(connection,number)
    normal_control('source')
    event('root02_bootstrap_done',legacy_values_equal=True,R01_package_before014=True,ordinary_runtime_proof=False)
    print('Two own PGs initialized; R01 golden package retained; old values unchanged after014')


if __name__=='__main__':
    try:main()
    except Exception as error:
        failure('ROOT02-bootstrap',type(error).__name__+':'+str(error)[:300],effect='本卡在途资源保留，按具体根因核对；不删除/重建或清计数')
        raise
