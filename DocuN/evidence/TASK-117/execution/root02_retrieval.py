"""普通新应用角色+真实PG+真实Windows监督的索引/query/回读证明。"""
import asyncio
import io
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from datetime import datetime,timedelta,timezone
from control import ROOT,HERE,count,event,write,state,failure,guard
from runtime_control import dsn,credentials,stop_pg
sys.path.insert(0,str(ROOT/'backend'))
fixture=ROOT/'backend/tests/fixtures/step018'
sys.path.insert(0,str(fixture))
os.environ['RETROLUME_TASK117_SYNTHETIC']='TASK-117-STEP018-INTEGRATION-S01-20261014'
os.environ['RETROLUME_TASK117_TRANSPORT_LOG']=str(HERE/'root02-transport.jsonl')
os.environ['RETROLUME_TASK117_TRACE_PG']='1'
os.environ['PYTHONPATH']=str(fixture)+os.pathsep+str(ROOT/'backend')
from runtime_fixture import install
install()
from app.runtime import psycopg_compatible_loop_factory
from app.activities.repository import PostgresAdmissionLedger,ActivitySpec,SourceSnapshot
from app.materials.repository import PostgresMaterials
from app.storage.originals import OriginalStore
from app.data_exit.config import DataRuntime
from app.data_exit.schema_checks import assert_data_schema_sync
from app.retrieval.service import RetrievalService,IntegrationConfig
from app.retrieval.contracts import RetrievalCommandInput,RetrievalRef
from app.capabilities.embedding import EmbeddingServiceConfig,vector_digest
import psycopg
from psycopg.rows import dict_row


async def main():
    guard()
    if state()['active_root']!=2:raise RuntimeError('root_identity')
    base=HERE/'synthetic/source-data';backup=HERE/'synthetic/source-backup';control=HERE/'synthetic/source-control';restore=HERE/'synthetic/source-restore'
    for path in (base,backup,control,restore):path.mkdir(parents=True,exist_ok=True)
    originals=base/'originals';originals.mkdir(exist_ok=True)
    os.environ.update(RETROLUME_DATA_DIR=str(base),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_CONTROL_ROOT=str(control),RETROLUME_RESTORE_ROOT=str(restore),
      RETROLUME_DATABASE_URL=dsn('source'),RETROLUME_TASK117_SNAPSHOT=dsn('source','snapshot'),RETROLUME_TASK117_MAINTENANCE=credentials('source')['maintenance_key'])
    ledger=PostgresAdmissionLedger(dsn('source'));materials=PostgresMaterials(dsn('source'));store=OriginalStore(originals)
    app=SimpleNamespace(state=SimpleNamespace(activities_ledger=ledger,materials=materials,originals=store,preview_controller=None,preview_policy=None))
    data=DataRuntime(app,SimpleNamespace(data_dir=base,backup_dir=backup),{'maintenance_key_env':'RETROLUME_TASK117_MAINTENANCE','snapshot_url_env':'RETROLUME_TASK117_SNAPSHOT'})
    samples=json.loads((ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json').read_text(encoding='utf-8'))
    prior=HERE/'root02-index.json'
    if prior.exists():
        original=json.loads(prior.read_text(encoding='utf-8'))
        if original['terminal_disposition'] not in ('not_sent','unknown'):raise RuntimeError('already_effectful_input_keep_saved_proof')
        aid=original['activity_id'];material=materials.get(original['source_refs'][0]['source_id'])
        archive=HERE/('root02-index-attempt-'+str(state()['counts']['native_windows'])+'.json')
        if not archive.exists():archive.write_bytes(prior.read_bytes())
        event('explicit_grounded_index_retry',activity_id=aid,old_key=original['business_key'],reason='原窗口返回但未保存元数据，新增限定SUP元数据观察，保留原失败；复用同活动/资料/额度，新命令仍明确确认')
    else:
        source=samples['sources'][0];raw=source['text'].encode('utf-8');sha=__import__('hashlib').sha256(raw).hexdigest()
        prepared=data.references.prepare_reference(sha,len(raw))
        with data.references.acquire_shared(prepared) as pin:
            obj=store.put(io.BytesIO(raw),max_bytes=5*1024**2,reference_pin=pin)
            material=materials.save(source_id=None,expected_version=None,filename=source['filename'],format='md',sha256=obj.sha256,size=obj.size,reference_pin=pin,prepared_ids=prepared)
        aid=str(uuid4())
        await ledger.create_activity(ActivitySpec(aid,(SourceSnapshot(material['id'],material['version_id'],material['revision']),),datetime.now(timezone.utc)+timedelta(hours=24),80,20000000,250000,65536,4096,3600,(('deepseek_chat_completions','deepseek-chat'),('zhipu_embeddings','embedding-3')),('finite_calculate',),max_tool_calls=8))
    config=IntegrationConfig(EmbeddingServiceConfig(api_key='synthetic-transport-only',timeout_seconds=10.0),None,8)
    with psycopg.connect(dsn('source'),row_factory=dict_row) as connection:
        baseline=connection.execute('SELECT requests_reserved,(SELECT count(*) FROM activity_operations WHERE activity_id=%s) AS operations FROM activities WHERE id=%s',(aid,aid)).fetchone()
    service=RetrievalService(ledger,materials,store)
    index=RetrievalCommandInput(business_key=str(uuid4()),action='source_index',expected_scope_revision=1,expected_domain_revision=0,confirmed=True)
    count('native_windows');event('native_window_expected',activity=aid,purpose='source_index',batches=1)
    indexed=await service.submit(aid,index,config)
    write(HERE/'root02-index.json',indexed)
    if indexed['terminal_disposition']!='received':raise RuntimeError('index_not_received:'+str(indexed.get('error_code')))
    same=await service.submit(aid,index,config)
    if same['result_sha256']!=indexed['result_sha256']:raise RuntimeError('same_key_changed')
    cache_input=RetrievalCommandInput(business_key=str(uuid4()),action='source_index',expected_scope_revision=1,expected_domain_revision=0,confirmed=True)
    cached=await service.submit(aid,cache_input,config)
    if cached['batch_count']!=0 or cached['terminal_disposition']!='cache_ready':raise RuntimeError('cache_effect_invalid')
    query=RetrievalCommandInput(business_key=str(uuid4()),action='query',expected_scope_revision=1,expected_domain_revision=0,query='平均速度与分钟换秒',confirmed=True)
    count('native_windows');event('native_window_expected',activity=aid,purpose='query',batches=1)
    result=await service.submit(aid,query,config)
    write(HERE/'root02-query.json',result)
    if result['terminal_disposition']!='received':raise RuntimeError('query_not_received:'+str(result.get('error_code')))
    entries=await service.catalog(aid,RetrievalRef.model_validate(result['retrieval_ref']),'1'*64,top_k=4,max_chars=4000,max_bytes=8000)
    with psycopg.connect(dsn('source'),row_factory=dict_row) as connection:
        assert_data_schema_sync(connection)
        rows=connection.execute('SELECT evidence_id,vector_value::text AS vector,vector_sha256,public.retrieval_vector_digest(vector_value) AS sql_sha FROM retrieval_chunks ORDER BY evidence_id').fetchall()
        if len(rows)!=4 or any(vector_digest(json.loads(r['vector']))!=r['vector_sha256'] or r['vector_sha256']!=r['sql_sha'] for r in rows):raise RuntimeError('stored_vector_digest_mismatch')
        facts=connection.execute('SELECT id,status,execution_generation,requests_reserved,cost_reserved_microunits,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s',(aid,)).fetchone()
        operations=connection.execute('SELECT operation_id,kind,state,request_bytes,max_output_tokens,reserved_cost_microunits FROM activity_operations WHERE activity_id=%s ORDER BY operation_id',(aid,)).fetchall()
        if len(operations)!=baseline['operations']+2 or facts['requests_reserved']!=baseline['requests_reserved']+2 or facts['running_reserved_seconds']!=0:raise RuntimeError('ledger_or_stop_mismatch')
        role=connection.execute('SELECT rolsuper,rolcreaterole,rolcreatedb,rolbypassrls FROM pg_roles WHERE rolname=SESSION_USER').fetchone()
        if any(role.values()):raise RuntimeError('ordinary_role_not_proved')
    from app.data_exit.codec import plain
    write(HERE/'root02-retrieval-proof.json',{'activity_id':aid,'material':material,'index':indexed,'cache':cached,'query':result,'catalog':[e.model_dump() for e in entries],
      'stored_vectors':rows,'facts':plain(facts),'operations':operations,'ordinary_role':True,'actual_native_windows':2,'actual_provider_calls':0,'actual_fee':0,
      'layers':['PG事务与float32实际回读','普通应用角色','原Windows SUP/Job','明确最低合成传输'],'semantic_Q':'NOT_RUN'})
    # 本根不保活资源等后续编码；原CID/卷/库/行均保留。
    stop_pg('source');stop_pg('compat')
    from control import end_root
    end_root(result='014 nonempty upgrade + R01 golden package + ordinary PG native embedding/index/query/cache and actual vector digest proved')
    print('ROOT02 real PG/native index/query/cache committed; stored hashes equal; own PGs stopped')


if __name__=='__main__':
    try:
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(main())
    except Exception as error:
        failure('ROOT02-retrieval',type(error).__name__+':'+str(error)[:300],effect='保存实际失败和在途账；不重建PG或清除已提交行')
        raise
