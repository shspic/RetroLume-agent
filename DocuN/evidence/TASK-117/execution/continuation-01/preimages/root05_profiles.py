"""两份可信profile的真实隔离恢复和回读；成功/失败对象均保留。"""
from control import *
from runtime_control import *
import os,sys,json,shutil,asyncio
from types import SimpleNamespace
from uuid import uuid4
sys.path.insert(0,str(ROOT/'backend'));sys.path.insert(0,str(ROOT/'backend/tests'))
import psycopg
from psycopg.rows import dict_row
from app.activities.repository import PostgresAdmissionLedger
from app.materials.repository import PostgresMaterials
from app.storage.originals import OriginalStore
from app.data_exit.config import DataRuntime
from app.data_exit.contracts import DataJobCommand,PROFILE
from app.data_exit.schema_profiles import R02
from app.data_exit.packages import PackageReader
from test_step018_profiles_pg import verify_readonly_target
from test_step018_retrieval_pg import verify_persistent_retrieval

class Hooks:
    def before_create(self,slot):
        memory_gate('restore-create-'+slot['id']);port_gate(slot['port']);count('pg_create_attempts');count('volumes')
        save_resource({'id':'pg-'+slot['id'],'kind':'pg','slot':slot['id'],'name':slot['name'],'volume':slot['volume'],'port':slot['port'],'database':slot['database'],'image':PG_IMAGE,'intent':sample(),'cid':None,'running':False})
    def created(self,target,identity):
        count('pg_objects');row=next(x for x in state()['resources'] if x['id']=='pg-'+target.name.removeprefix('retrolume-step018-syn-'))
        row.update(cid=target.cid,created=sample(),factory_job_id=target.job_id,factory_profile_id=target.profile_id);save_resource(row);event('restore_target_created',identity=metadata(target.cid))
    def before_start(self,target):
        memory_gate('restore-start-'+target.name);port_gate(target.port);count('pg_starts');row=next(x for x in state()['resources'] if x.get('cid')==target.cid);row.update(running=True,holding_start=sample());save_resource(row)
    def started(self,target,identity):event('restore_target_started',identity=metadata(target.cid))
    def stopped(self,target,identity):
        row=next(x for x in state()['resources'] if x.get('cid')==target.cid);stamp=sample()
        if row.get('running'):row.setdefault('holding_intervals',[]).append({'start':row['holding_start'],'end':stamp})
        row.update(running=False,stopped=stamp);save_resource(row);event('restore_target_stopped',identity=metadata(target.cid))

def main():
    if state()['active_root'] is None:begin_root('ROOT05-R01-R02隔离恢复与向量往返','runtime')
    if state()['active_root']!=5:raise RuntimeError('root_identity')
    start_pg('source')
    base=HERE/'synthetic/source-data';backup=HERE/'synthetic/source-backup';control=HERE/'synthetic/source-control';restore=HERE/'synthetic/source-restore'
    os.environ.update(RETROLUME_CONTROL_ROOT=str(control),RETROLUME_RESTORE_ROOT=str(restore),RETROLUME_DATABASE_URL=dsn('source'),RETROLUME_TASK117_SNAPSHOT=dsn('source','snapshot'),RETROLUME_TASK117_MAINTENANCE=credentials('source')['maintenance_key'])
    ledger=PostgresAdmissionLedger(dsn('source'));materials=PostgresMaterials(dsn('source'));originals=OriginalStore(base/'originals')
    app=SimpleNamespace(state=SimpleNamespace(activities_ledger=ledger,materials=materials,originals=originals,preview_controller=None,preview_policy=None))
    factory={'id':'TASK117-S01-fixed-restores','image_id':PG_IMAGE,'login_prefix':'step018_','pg_major':17,'source_name':'retrolume-step018-syn-source','slots':[{'id':slot,'name':'retrolume-step018-syn-'+slot,'volume':'retrolume-step018-syn-'+slot+'-data','port':SLOTS[slot][0],'database':SLOTS[slot][1],'schema_profile':profile} for slot,profile in [('r01',PROFILE),('r02',R02)]]}
    runtime=DataRuntime(app,SimpleNamespace(data_dir=base,backup_dir=backup),{'maintenance_key_env':'RETROLUME_TASK117_MAINTENANCE','snapshot_url_env':'RETROLUME_TASK117_SNAPSHOT','factory':factory})
    runtime.factory.hooks=Hooks()
    context=runtime.context();scope={'mode':'all','source_ids':[],'activity_ids':[],'allow_incomplete':False}
    with psycopg.connect(dsn('source'),row_factory=dict_row) as connection:before_vectors=verify_persistent_retrieval(connection)
    write(HERE/'root05-source-vectors.json',before_vectors)
    marker=HERE/'source-r02-package-receipt.json'
    if marker.exists():receipt=json.loads(marker.read_text())
    else:
        job=runtime.hub.create_or_get_job(DataJobCommand('restore_checkpoint',str(uuid4()),scope),context)
        receipt=runtime.packages.capture_and_publish(job['job_id'],scope);write(marker,receipt)
    r01=json.loads((HERE/'compat-r01-package-receipt.json').read_text())
    inputs=[(PROFILE,HERE/'synthetic/compat-backup/packages'/f"{r01['package_id']}.rldata"),(R02,runtime.packages.path(receipt['package_id']))]
    proof=[]
    for profile,package in inputs:
        if any(t.get('schema_profile',PROFILE)==profile for t in runtime.hub.state()['targets'].values()):raise RuntimeError('prior_target_exists_review_before_any_reuse')
        with PackageReader(package) as reader:
            assert reader.schema_profile.name==profile
            event('restore_package_preflight',profile=profile,root_sha=reader.manifest['root_sha256'],tables=len(reader.schema_profile.tables))
        upload=str(uuid4());targetfile=runtime.incoming/(upload+'.rldata');shutil.copyfile(package,targetfile)
        plan=runtime.restore.prepare(upload,'snapshot_only_readonly' if profile==PROFILE else 'respect_current_deletions',context)
        job=runtime.hub.create_or_get_job(DataJobCommand('restore',str(uuid4()),{'plan_id':plan['plan_id'],'plan_sha256':plan['plan_sha256']}),context)
        write(HERE/('root05-'+profile.rsplit('.',1)[-1]+'-plan.json'),{'plan':plan,'job_id':job['job_id']})
        result=runtime.restore.verify(job['job_id'],plan['plan_sha256'])
        target=runtime.factory.target(result['target_id']);runtime.factory.start(target)
        try:
            credential=runtime.factory.readonly_credentials(target.target_id)
            with psycopg.connect(credential['readonly_dsn'],row_factory=dict_row) as connection:
                item=verify_readonly_target(connection,profile)
                if profile==R02:
                    item['vectors']=verify_persistent_retrieval(connection);assert item['vectors']==before_vectors
                try:
                    connection.execute('UPDATE public.activities SET requests_reserved=requests_reserved')
                except psycopg.Error as exc:item['write_refused_sqlstate']=exc.sqlstate;connection.rollback()
                else:raise RuntimeError('sealed_target_accepted_write')
            item.update(target_id=target.target_id,cid=target.cid,job_id=job['job_id'],receipt=result);proof.append(item);write(HERE/'root05-restores.json',proof)
        finally:runtime.factory.stop(target)
    runtime.references.lease.close();stop_pg('source');end_root(result='R01/R02 exact fresh factory targets restored/sealed; readonly privilege and actual float32 vectors roundtripped')
    print('R01/R02 restored, permanently sealed, stopped; actual vectors roundtripped')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        failure('ROOT05-profiles',type(exc).__name__+':'+str(exc)[:400],effect='成功/失败目标和卷保留，不重建或复用失败对象')
        for row in state()['resources']:
            if row.get('slot')=='source' and row.get('running'):stop_pg('source')
        raise
