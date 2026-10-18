"""六个固定 schema 的实际迁移反例；已有资源先核查，绝不 SKIP 冒充通过。"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4
import psycopg
from psycopg import sql
from .pg_setup import MIGRATIONS,TEACHING_MIGRATION,connection
from .control import BACKEND,FAULT_DB,ROLES,atomic_json
SCHEMA_NAMES={'nonempty':'task100_m01_nonempty','duplicate':'task100_m02_duplicate','missing':'task100_m03_missing',
              'tampered':'task100_m04_tampered','midway':'task100_m05_midway','denied':'task100_m06_denied'}
M009=(BACKEND/'migrations'/TEACHING_MIGRATION).read_text(encoding='utf-8')

def connect(schema,denied=False):
    dsn=os.environ['RETROLUME_TASK100_DENIED_DSN' if denied else 'RETROLUME_TASK100_FAULT_DSN']
    conn=connection(dsn,FAULT_DB,ROLES[2] if denied else ROLES[0],autocommit=True)
    conn.execute(sql.SQL('SET search_path TO {}').format(sql.Identifier(schema)))
    return conn

def teaching_objects(conn):
    return conn.execute("SELECT tablename FROM pg_tables WHERE schemaname=current_schema() AND tablename LIKE 'teaching%%' ORDER BY tablename").fetchall()

def baseline(schema,upto=8):
    with connect(schema) as conn:
        tables=conn.execute("SELECT tablename FROM pg_tables WHERE schemaname=current_schema()").fetchall()
        if not tables:
            for name in MIGRATIONS[:upto]: conn.execute((BACKEND/'migrations'/name).read_text(encoding='utf-8'))
        elif conn.execute("SELECT to_regclass('activity_operations') AS r").fetchone()['r'] is None:
            raise RuntimeError('partial_existing_schema_preserved')

def fingerprints(conn):
    value={}
    for table in ('material_sources','material_versions','activities','activity_operations','activity_operation_results'):
        rows=conn.execute(sql.SQL('SELECT to_jsonb(t) AS value FROM {} t').format(sql.Identifier(table))).fetchall()
        text=json.dumps(sorted((r['value'] for r in rows),key=lambda x:json.dumps(x,sort_keys=True)),sort_keys=True,default=str)
        value[table]={'count':len(rows),'sha256':hashlib.sha256(text.encode()).hexdigest()}
    return value

def seed(conn):
    if conn.execute('SELECT count(*) AS n FROM activities').fetchone()['n']:
        return
    sid,vid,aid,admission=map(str,(uuid4(),uuid4(),uuid4(),uuid4()))
    conn.execute('INSERT INTO material_sources(id,title,revision) VALUES (%s,%s,1)',(sid,'合成旧资料'))
    conn.execute("INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'legacy.md','md',%s,12)",(vid,sid,'a'*64))
    conn.execute('UPDATE material_sources SET current_version=%s WHERE id=%s',(vid,sid))
    conn.execute("INSERT INTO activities(id,status,scope_revision,deadline_at,max_requests,max_cost_microunits,reserve_cost_microunits,max_request_bytes,max_output_tokens,max_running_seconds) VALUES (%s,'pending',1,now()+interval '1 hour',10,100000,1000,65536,2048,900)",(aid,))
    conn.execute("INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,execution_generation,scope_revision,provider,configured_model,request_bytes,max_output_tokens,reserved_cost_microunits,state,disposition,recorded_at) VALUES (%s,'learn-first-v1.legacy',%s,'legacy',1,1,'deepseek_chat_completions','synthetic-model-100',100,256,1000,'received','received',now())",(aid,admission))
    # 特意留下原 received 无正文；009 不补造它。

def expect_reject(conn,text,sqlstate=None):
    before=teaching_objects(conn)
    try: conn.execute(text)
    except psycopg.Error as exc:
        # 多语句 BEGIN 出错后必须原事务回滚；不清除数据或对象。
        conn.execute('ROLLBACK')
        if sqlstate is not None and exc.sqlstate!=sqlstate: raise AssertionError('unexpected_sqlstate_'+str(exc.sqlstate))
        after=teaching_objects(conn)
        assert before==after
        return {'sqlstate':exc.sqlstate,'message':exc.diag.message_primary,'objects_unchanged':True}
    raise AssertionError('migration_unexpectedly_succeeded')

def run():
    results=[]
    with connection(os.environ['RETROLUME_TASK100_FAULT_DSN'],FAULT_DB,ROLES[0],autocommit=True) as conn:
        for schema in SCHEMA_NAMES.values():
            old=conn.execute('SELECT pg_get_userbyid(nspowner) AS owner FROM pg_namespace WHERE nspname=%s',(schema,)).fetchone()
            if old and old['owner']!=ROLES[0]: raise RuntimeError('schema_owner_changed')
            if not old: conn.execute(sql.SQL('CREATE SCHEMA {} AUTHORIZATION {}').format(sql.Identifier(schema),sql.Identifier(ROLES[0])))
    for name,schema in SCHEMA_NAMES.items():
        try:
            baseline(schema,7 if name=='missing' else 8)
            with connect(schema) as conn:
                if name=='nonempty':
                    seed(conn); before=fingerprints(conn)
                    if teaching_objects(conn):
                        result={'status':'not_run','reason':'existing_009_without_current_as_run_binding_preserved'}
                    else:
                        conn.execute(M009);after=fingerprints(conn)
                        assert before==after and len(teaching_objects(conn))==3
                        assert conn.execute('SELECT count(*) AS n FROM teaching_heads').fetchone()['n']==0
                        result={'status':'pass','legacy_before':before,'legacy_after':after,'no_backfill':True}
                elif name=='duplicate':
                    if not teaching_objects(conn): conn.execute(M009)
                    result={'status':'pass',**expect_reject(conn,M009,'P0001')}
                elif name=='missing': result={'status':'pass',**expect_reject(conn,M009,'P0001')}
                elif name=='tampered':
                    # 反例改变仅位于会失败并回滚的事务；保存同名宽松约束也应拒绝。
                    conn.execute('BEGIN')
                    old=conn.execute("SELECT conname FROM pg_constraint WHERE conrelid='activity_operations'::regclass AND conname='activity_operations_kind_domain'").fetchone()
                    if old: conn.execute('ALTER TABLE activity_operations DROP CONSTRAINT activity_operations_kind_domain')
                    conn.execute('ALTER TABLE activity_operations ADD CONSTRAINT activity_operations_kind_domain CHECK (true)')
                    result={'status':'pass',**expect_reject(conn,M009,'P0001'),'same_name_tamper':True}
                elif name=='midway':
                    altered=M009.replace('CREATE TABLE teaching_records (',"DO $$ BEGIN RAISE EXCEPTION 'TASK100_midway_after_two_tables'; END $$;\nCREATE TABLE teaching_records (",1)
                    assert altered!=M009
                    result={'status':'pass',**expect_reject(conn,altered,'P0001')}
                else:
                    conn.execute(sql.SQL('GRANT USAGE ON SCHEMA {} TO {}').format(sql.Identifier(schema),sql.Identifier(ROLES[2])))
                    tables=conn.execute('SELECT tablename FROM pg_tables WHERE schemaname=current_schema()').fetchall()
                    for table in tables:
                        if not table['tablename'].startswith('teaching'):
                            conn.execute(sql.SQL('GRANT SELECT ON {} TO {}').format(sql.Identifier(table['tablename']),sql.Identifier(ROLES[2])))
                    with connect(schema,True) as denied:
                        result={'status':'pass',**expect_reject(denied,M009,'42501')}
            result.update(name=name,schema=schema)
        except BaseException as exc:
            import traceback
            traceback.print_exc()
            result={'name':name,'schema':schema,'status':'fail','error_type':type(exc).__name__}
        results.append(result);print('MIGRATION',json.dumps(result,ensure_ascii=False),flush=True)
    target=Path(os.environ['RETROLUME_TASK100_BATCH_DIR'])/'migration-facts.json'
    atomic_json(target,{'009_sha256':hashlib.sha256(M009.encode()).hexdigest(),'cases':results,'deleted':False})
    return 0 if all(r['status']=='pass' for r in results) else 1
if __name__=='__main__': raise SystemExit(run())
