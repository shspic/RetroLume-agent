"""最终R02包及hash失败目标；来源停止后依次恢复，failed目标永久保留。"""
from profiles_batch import *
from app.data_exit.contracts import DataError

def final_restore(run,*,runtime=None,keep_source=False):
    runtime=runtime or runtime_config(run);context=runtime.context();assert context.mode=='normal'
    scope={'mode':'all','source_ids':[],'activity_ids':[],'allow_incomplete':False}
    with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:
        vectors=verify_persistent_retrieval(db)
        facts={'vectors':vectors,'space_count':db.execute('SELECT count(*) AS n FROM retrieval_spaces').fetchone()['n'],'grant_metadata':db.execute('SELECT count(*) AS n FROM activities WHERE outbound_grant_sha256 IS NOT NULL').fetchone()['n'],'unknown':db.execute("SELECT count(*) AS n FROM activity_operations WHERE state='unknown'").fetchone()['n'],'deleted_sources':db.execute("SELECT count(*) AS n FROM data_tombstones WHERE entity_kind='source'").fetchone()['n']}
    assert facts['space_count']>=2 and facts['grant_metadata']>=1 and facts['unknown']>=1 and facts['deleted_sources']>=1,facts
    job=runtime.hub.create_or_get_job(DataJobCommand('restore_checkpoint',str(uuid4()),scope),context)
    receipt=runtime.packages.capture_and_publish(job['job_id'],scope)
    package=runtime.packages.path(receipt['package_id']);c.write(C01/'source-r02-final-package.json',{'receipt':receipt,'facts':facts})
    with PackageReader(package) as reader:assert reader.schema_profile.name==R02 and len(reader.schema_profile.tables)==31
    prepared=[]
    for label in ('hash-fault','valid'):
        upload=str(uuid4());incoming=runtime.incoming/(upload+'.rldata');shutil.copyfile(package,incoming)
        plan=runtime.restore.prepare(upload,'respect_current_deletions',context)
        job=runtime.hub.create_or_get_job(DataJobCommand('restore',str(uuid4()),{'plan_id':plan['plan_id'],'plan_sha256':plan['plan_sha256']}),context)
        if label=='hash-fault':
            with incoming.open('ab') as stream:stream.write(b'TASK117 deliberate post-plan hash fault')
        prepared.append((label,job,plan));c.write(C01/('final-r02-'+label+'-plan.json'),{'job_id':job['job_id'],'plan':plan,'source_facts':facts})
    if not keep_source:rc.stop_pg('source')
    for label,job,plan in prepared:
        if label=='hash-fault':
            try:runtime.restore.verify(job['job_id'],plan['plan_sha256'])
            except DataError as exc:assert exc.code=='integrity_failed',exc.code
            else:raise RuntimeError('corrupt_package_accepted')
            failed=runtime.hub.get(job['job_id']);assert failed['state']=='failed',failed
            targets=[x for x in runtime.hub.state()['targets'].values() if x['job_id']==job['job_id']]
            assert len(targets)==1 and targets[0]['slot_id']=='r02-fault' and targets[0]['state']=='failed' and targets[0]['temporary_credentials_revoked']
            c.write(C01/'final-r02-hash-failed.json',{'receipt':failed,'target':targets[0],'selection':runtime.hub.state()['selection'],'PG':rc.metadata(targets[0]['cid'])})
        else:
            verified=runtime.restore.verify(job['job_id'],plan['plan_sha256'])
            assert verified['state']=='verified' and runtime.hub.state()['targets'][verified['target_id']]['slot_id']=='r02'
            c.write(C01/'final-r02-verified.json',{'receipt':verified,'plan':plan,'facts_before':facts,'selection':runtime.hub.state()['selection'],'application_view':'deferred to serial read-only viewer, no extra SQL restart'})
    assert runtime.hub.state()['selection'] is None
    return {'r02_verified':True,'failed_hash_target_preserved':True,'source_not_activated':True,'facts':facts}
