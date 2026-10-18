"""根14，精确双库修补与一次有区别的正常提交对照。"""
from batch_runtime import *
from profiles_batch import runtime_config
import importlib.util,re,traceback,asyncio
import psycopg
from psycopg.rows import dict_row
from psycopg import sql
from app.data_exit.schema_checks import assert_data_schema_sync,check_data_shape,FUNCTION_QUERY,ROLE_QUERY,TRIGGER_QUERY,CONSTRAINT_QUERY,DATA_ROLES
from app.data_exit.schema import DATA_FUNCTIONS
from app.data_exit.schema_profiles import extra_shape_queries,normalized_extra_shape,check_extra_shape,R02
from app.data_exit.contracts import canonical

OLD=C01.parent/'continuation-01'
spec=importlib.util.spec_from_file_location('app.data_exit._s03_trusted_old',OLD/'ordinary-db-fixes/pre/backend/app/data_exit/schema_profiles.py')
legacy=importlib.util.module_from_spec(spec);sys.modules[spec.name]=legacy;spec.loader.exec_module(legacy)

def snapshot(db):
    names=[r['relname'] for r in db.execute("SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' ORDER BY c.relname").fetchall()]
    result={}
    for name in names:
        rows=db.execute(sql.SQL('SELECT to_jsonb(t)::text AS body FROM public.{} t ORDER BY to_jsonb(t)::text').format(sql.Identifier(name))).fetchall()
        result[name]={'count':len(rows),'sha256':c.sha('\n'.join(x['body'] for x in rows).encode())}
    return result

def apply(slot):
    rc.start_pg(slot)
    row=next(r for r in c.state()['resources'] if r.get('id')=='pg-'+slot);meta=rc.metadata(row['cid'])
    assert meta['name']==row['name'] and meta['image']==rc.PG_IMAGE
    assert meta['memory']==512*1024**2 and meta['nano_cpus']==1000000000 and meta['pids_limit']==128
    assert meta['port_bindings']=={'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':str(row['port'])}]}
    assert len(meta['mounts'])==1 and meta['mounts'][0]['Name']==row['volume'] and meta['mounts'][0]['Destination']=='/var/lib/postgresql/data'
    before={};after={}
    with psycopg.connect(rc.dsn(slot,'admin'),row_factory=dict_row,autocommit=True) as db:
        who=db.execute('SELECT current_user,current_database() AS database').fetchone()
        assert who=={'current_user':rc.credentials(slot)['admin_user'],'database':row['database']}
        control=db.execute('SELECT schema_profile,mode_observed FROM data_export_control_v1').fetchone();assert control=={'schema_profile':R02,'mode_observed':'normal'}
        role=db.execute("SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname='retrolume_interview_owner'").fetchone()
        assert role and not any(v for k,v in role.items() if k!='rolname')
        shape={k:db.execute(q).fetchall() for k,q in legacy.extra_shape_queries().items()}
        current_new={k:db.execute(q).fetchall() for k,q in extra_shape_queries().items()}
        expected=json.loads((OLD/'ordinary-db-fixes/derived-shape.json').read_text())['shape']
        projected=normalized_extra_shape(current_new)
        for item in projected['functions']:
            if item['proname']=='retrieval_chunk_guard':item['prosrc']=item['prosrc'].replace('\r\n','\n')
        already_increment=projected==normalized_extra_shape(expected)
        if not already_increment:legacy.check_extra_shape(shape)
        check_data_shape(db.execute(FUNCTION_QUERY,(list(DATA_FUNCTIONS),)).fetchall(),db.execute(ROLE_QUERY,(DATA_ROLES,)).fetchall(),db.execute(TRIGGER_QUERY).fetchall(),db.execute(CONSTRAINT_QUERY).fetchall(),R02)
        fn=next(x for x in shape['functions'] if x['proname']=='retrieval_chunk_guard')
        assert c.sha(re.sub(r'\s+','',fn['prosrc']).encode())==('2b8801abe7c42eaaa8c2ffc5e4117e251c459c593110c16faf0016d696431bab' if already_increment else '4efdb6c4b774ef67c00534c26e7c1b9963d4341b6113a7d1c9ce339e0aaddf55')
        data_before=snapshot(db)
        before={'who':who,'mode':control,'role':role,'shape':shape,'data':data_before}
        before_path=C01/(slot+'-SQL-before.json')
        if before_path.exists():
            assert json.loads(before_path.read_text())['data']==data_before
            before_path=C01/(slot+'-SQL-before-readback-'+str(time.time_ns())+'.json')
        c.write(before_path,before)
        repair=(OLD/'ordinary-db-fixes/pending-forward-repair.sql').read_bytes()
        assert c.sha(repair)=='c8d84e69876572c4b00236cacc78ac127918b7ddb6e61b4269d18eb5a1632abe'
        # 受信派生DDL通过文本模式产生LF；执行也采用同一行尾，原批准文件字节不改。
        # 首次compat的CRLF存入prosrc导致精确目录拒绝；仅行尾差已按完整目录精确解释。
        try:db.execute(repair.decode().replace('\r\n','\n'),prepare=False)
        except BaseException:db.execute('ROLLBACK');raise
        assert_data_schema_sync(db)
        new={k:db.execute(q).fetchall() for k,q in extra_shape_queries().items()};check_extra_shape(new)
        assert data_before==snapshot(db),'修补不得更改业务行、四账或UNKNOWN'
        new_fn=next(x for x in new['functions'] if x['proname']=='retrieval_chunk_guard')
        assert {k:v for k,v in fn.items() if k!='prosrc'}=={k:v for k,v in new_fn.items() if k!='prosrc'}
        assert c.sha(re.sub(r'\s+','',new_fn['prosrc']).encode())=='2b8801abe7c42eaaa8c2ffc5e4117e251c459c593110c16faf0016d696431bab'
        after={'shape':new,'data_unchanged':True,'shape_sha256':c.sha(canonical(normalized_extra_shape(new)).encode()),'migration_014':c.sha((ROOT/'backend/migrations/014_step018_retrieval.sql').read_bytes()),'scope':'仅批准GRANT SELECT及函数别名；没有重跑迁移链'}
        c.write(C01/(slot+'-SQL-after.json'),after)
    if slot!='source':rc.stop_pg(slot)
    return {'slot':slot,'cid':row['cid'],'passed':True,'old_shape':legacy.R02_EXTRA_SHAPE_SHA,'new_shape':after['shape_sha256']}

def rollback_trigger():
    proof={}
    with psycopg.connect(rc.dsn('source','admin'),row_factory=dict_row) as db:
        db.execute('SELECT public.data_mutation_enter()')
        found=db.execute('SELECT space_id,evidence_id FROM retrieval_chunks ORDER BY evidence_id LIMIT 1').fetchone();assert found
        try:db.execute('DELETE FROM retrieval_chunks WHERE space_id=%s AND evidence_id=%s',(found['space_id'],found['evidence_id']))
        except psycopg.Error as exc:
            assert exc.sqlstate=='P0001' and 'retrieval_purge_not_authorized' in str(exc)
            proof={'actual_DELETE_branch':True,'sqlstate':exc.sqlstate,'expected_refusal':'retrieval_purge_not_authorized','rollback':True,'alias_ambiguity_absent':True}
        else:raise AssertionError('未授权删除必须被拒')
        db.rollback()
    c.write(C01/'guard-rollback-regression.json',proof)

def checkpoint():
    with psycopg.connect(rc.dsn('source','admin'),row_factory=dict_row) as db:
        heads=db.execute("SELECT a.id,a.deadline_at,a.status,a.requests_reserved,a.cost_reserved_microunits,a.running_reserved_seconds,a.execution_generation,h.revision,h.phase,h.answer_record_id FROM activities a LEFT JOIN teaching_heads h ON h.activity_id=a.id WHERE a.id=ANY(%s) ORDER BY a.id",(['b7f32142-b5b3-4a5c-b561-f927bcbe1b6d','bbe0617f-0417-4490-8a8f-354ab0e10ae3'],)).fetchall()
        unknown=db.execute('SELECT * FROM retrieval_commands WHERE business_key=%s',('95a0b55e-b5fb-45d7-ad6e-310f3bc4b572',)).fetchone()
        orphan=db.execute("SELECT a.id,a.deadline_at,a.status FROM activities a WHERE NOT EXISTS(SELECT 1 FROM interview_heads h WHERE h.activity_id=a.id) AND EXISTS(SELECT 1 FROM activity_scope_sources s WHERE s.activity_id=a.id AND s.source_id=%s) AND EXISTS(SELECT 1 FROM activity_memory_choices m WHERE m.activity_id=a.id) ORDER BY a.created_at DESC LIMIT 5",(json.loads((C01/'frozen-source-bindings.json').read_text())['R']['id'],)).fetchall()
        c.write(C01/'actual-checkpoint.json',{'sample':c.sample(),'teaching':json.loads(json.dumps(heads,default=str)),'unknown_original_key':json.loads(json.dumps(unknown,default=str)),'unstarted_R_memory':json.loads(json.dumps(orphan,default=str))})

def main():
    preflight('S03-root14-SQL-and-minimal-commit')
    with Batch(14,'S03_SQL_and_new_intent_control') as run:
        repaired=[apply(s) for s in ('compat','source')]
        c.write(C01/'SQL-repair-summary.json',{'sample':c.sample(),'targets':repaired,'R01_untouched':True})
        rollback_trigger();checkpoint()
        run.start_api(launcher=True)
        from frozen_http import FrozenFlow
        flow=FrozenFlow('minimal-diagnostic-commit')
        try:
            mapping=json.loads((C01/'frozen-source-bindings.json').read_text())
            aid=flow.create([mapping['N']]);c.write(C01/'new-diagnostic-intent.json',{'activity_id':aid,'intent':'S03移除高成本trace后的独立正常提交对照；不是原UNKNOWN重试','original_unknown_key':'95a0b55e-b5fb-45d7-ad6e-310f3bc4b572','original_unknown_reposted':False})
            flow.index(aid);w=flow.teaching(aid,'goal',{'goal':'S03诊断对照：平均速度的分钟换秒'})
            ref=flow.query(aid,{**w['head'],'scope_revision':1},'平均速度 分钟换秒')
            c.write(C01/'minimal-commit-received.json',{'activity_id':aid,'ref':ref,'trace':'off','definitive_root_cause':'未确定；本次为有区别对照'})
        finally:flow.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        p=C01/('root14-failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc(),encoding='utf-8');c.failure('S03-root14',p.name,effect='保留失败，按共享控制器清场；仅修正已定位原因');raise
