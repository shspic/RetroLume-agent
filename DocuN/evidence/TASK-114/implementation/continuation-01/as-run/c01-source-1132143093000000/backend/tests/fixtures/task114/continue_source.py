"""原source有限补证：准确guard前向修复、权限、同T、共享删除和重试。"""
import ast
import asyncio
from contextlib import contextmanager
from datetime import datetime,timezone,timedelta
import io
import json
from pathlib import Path
import re
import threading
import time
from uuid import uuid4
from budget import ROOT,EVIDENCE
from setup_source import start_source,stop_source
from app.data_exit.contracts import DataError,DataJobCommand,canonical,digest,TABLES
from app.runtime import psycopg_compatible_loop_factory

def prior_literal(name):
    tree=ast.parse((EVIDENCE/'pre/backend/app/data_exit/schema.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):return ast.literal_eval(node.value)
    raise RuntimeError('旧受信身份缺失')

def material(runtime,content,name,source=None):
    raw=content.encode('utf-8');ref=runtime.references
    prepared=ref.prepare_reference(digest(raw),len(raw),source_id=source['id'] if source else None)
    with ref.acquire_shared(prepared) as pin:
        original=runtime.app.state.originals.put(io.BytesIO(raw),max_bytes=5*1024**2,reference_pin=pin)
        return runtime.app.state.materials.save(source_id=source['id'] if source else None,expected_version=source['version_id'] if source else None,
             filename=name,format='md',sha256=original.sha256,size=original.size,reference_pin=pin,prepared_ids=prepared)

def source_group(budget,evidence,target,credentials):
    import psycopg
    from psycopg.rows import dict_row
    from seed_legacy import business_rows
    from continue_run import runtime_for
    if not start_source(budget,target):raise RuntimeError('source实时内存门不足')
    try:
        before=business_rows(credentials['admin_dsn']);evidence.observe('01-before-fields',before)
        with psycopg.connect(credentials['admin_dsn'],connect_timeout=3,row_factory=dict_row) as conn:
            row=conn.execute("SELECT p.prosrc,p.prosecdef,r.rolname AS owner FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner WHERE n.nspname='public' AND p.proname='memory_body_guard'").fetchone()
            old=prior_literal('BUSINESS_FUNCTIONS_013')['memory_body_guard']
            from app.data_exit.schema import BUSINESS_FUNCTIONS_013
            observed=digest(re.sub(r'\s+','',row['prosrc']))
            if row['owner']!='retrolume_memory_owner' or row['prosecdef']:raise RuntimeError('memory guard授权身份漂移')
            if observed!=BUSINESS_FUNCTIONS_013['memory_body_guard']:
                if observed!=old:raise RuntimeError('memory guard原文漂移')
                migration=(ROOT/'backend/migrations/013_data_exit.sql').read_text(encoding='utf-8')
                statement=re.search(r'CREATE OR REPLACE FUNCTION public.memory_body_guard\(.*? AS \$(\w+)\$.*?\$\1\$;',migration,re.S).group()
                conn.execute(statement)
        after=business_rows(credentials['admin_dsn'])
        if before!=after:raise RuntimeError('前向修复改变已有业务值')
        evidence.observe('02-forward-memory-guard',{'before_sha256':observed,'after_sha256':BUSINESS_FUNCTIONS_013['memory_body_guard'],'business_values_equal':True,'source_not_reinitialized':True})
        app,runtime=runtime_for(credentials,budget)
        evidence.observe('03-source-state',runtime.source.state())
        # 精确原始权限观察；每个拒绝独立事务，不能被前个abort污染。
        probes=[]
        statements=["UPDATE public.activities SET requests_reserved=requests_reserved",'SELECT maintenance_key_sha256 FROM public.data_control',
                    'SELECT pin_nonce_sha256 FROM public.data_operation_jobs',"SELECT public.data_source_delete(NULL,0,'x',NULL,'[]','wrong')"]
        for statement in statements:
            try:
                with psycopg.connect(credentials['snapshot_dsn'],connect_timeout=3) as conn:conn.execute(statement)
            except psycopg.Error as error:
                probes.append({'statement':statement,'sqlstate':error.sqlstate,'message_primary':error.diag.message_primary})
                if error.sqlstate!='42501':raise
            else:raise RuntimeError('snapshot越权')
        with psycopg.connect(credentials['app_dsn'],connect_timeout=3) as conn:
            conn.execute("SET retrolume.restore_mode='loading'")
            flags=conn.execute("SELECT public.data_loading_allowed(),pg_has_role(SESSION_USER,'retrolume_data_restore_loader','MEMBER')").fetchone()
            if any(flags):raise RuntimeError('source自授loading')
        evidence.observe('04-permissions',{'snapshot_negative':probes,'source_set_cannot_authorize_loading':list(flags)})
        from app.data_exit.schema_checks import assert_data_schema_sync
        failures=[]
        for statement in ("DROP TRIGGER data_restore_budget_shape ON public.html_preview_budgets",
                          "ALTER TABLE public.teaching_commands ALTER CONSTRAINT teaching_commands_activity_id_parent_record_id_fkey NOT DEFERRABLE"):
            with psycopg.connect(credentials['admin_dsn'],connect_timeout=3,row_factory=dict_row) as conn:
                conn.execute(statement)
                try:assert_data_schema_sync(conn)
                except DataError as error:
                    if error.code!='data_schema_not_ready':raise
                    failures.append({'statement':statement,'rejected':error.code})
                else:raise RuntimeError('缺失或坏定义没有被指纹拒绝')
                conn.rollback()
        evidence.observe('05-final-constraint-negatives',failures)
        a=material(runtime,'C01 同T原版本\n','C01快照.md')
        b=material(runtime,'C01 共享准确原件\n','C01共享甲.md')
        shared=material(runtime,'C01 共享准确原件\n','C01共享乙.md')
        single=material(runtime,'C01 精确清理暂时失败\n','C01清理.md')
        evidence.observe('06-new-material-identities',{'snapshot':a,'shared_a':b,'shared_b':shared,'single':single})
        # 一个真正RR snapshot已取point后，第二连接正常提交替换；真实结果保同T旧指针。
        coordinator=runtime.packages.snapshot
        original_connection=coordinator.repository.connection
        replacement={};interposed=False
        @contextmanager
        def concurrent_connection(**kwargs):
            nonlocal interposed
            with original_connection(**kwargs) as conn:
                class Wrapped:
                    def execute(self,statement,*args,**k):
                        nonlocal interposed
                        result=conn.execute(statement,*args,**k)
                        if 'pg_current_snapshot()' in str(statement) and not interposed:
                            interposed=True
                            worker=threading.Thread(target=lambda:replacement.update(material(runtime,'C01 同T之后正常替换\n','C01新版本.md',a)))
                            worker.start();worker.join(10)
                            if worker.is_alive() or not replacement:raise RuntimeError('并发替换没有有界确认')
                        return result
                    def cursor(self,*args,**k):return conn.cursor(*args,**k)
                yield Wrapped()
        coordinator.repository.connection=concurrent_connection
        capture=coordinator.capture(str(uuid4()),'restore_checkpoint',{'mode':'all'})
        coordinator.repository.connection=original_connection
        old=next(row for row in capture.rows['material_sources'] if row['id']==a['id'])
        versions=[row['id'] for row in capture.rows['material_versions'] if row['source_id']==a['id']]
        if old['current_version']!=a['version_id'] or replacement['version_id'] in versions:raise RuntimeError('多个T被拼接')
        evidence.observe('07-real-snapshot-concurrency',{'point':capture.point,'snapshot_source':old,'snapshot_version_ids':versions,'post_T_replacement':replacement,'raw_spool':str(capture.root),
              'single_connection_repeatable_read':True,'source_current':app.state.materials.get(a['id'])})
        # 真正公开删除服务：共享保留、非共享失败pending、原键重试不增修订。
        async def deletions():
            impact=runtime.deletions.preview(b['id'],b['revision'])
            deleted=await runtime.deletions.confirm(b['id'],b['revision'],impact['impact_sha256'],'c01-share-delete-'+str(uuid4()))
            evidence.observe('08-shared-delete',{'impact':impact,'receipt':deleted,'other_material':app.state.materials.get(shared['id']),
                'deleted_lookup':app.state.materials.get(b['id']),'shared_hash_exists':(app.state.originals.root/b['sha256']).exists()})
            if deleted['state']!='deleted' or app.state.materials.get(b['id']) is not None or not (app.state.originals.root/b['sha256']).exists():raise RuntimeError('共享准确清理错误')
            impact=runtime.deletions.preview(single['id'],single['revision'])
            key='c01-pending-delete-'+str(uuid4());unlink=app.state.originals.unlink_exact
            def failure(original,*,lease):
                if original.sha256==single['sha256']:raise OSError('C01 exact registered file failure')
                return unlink(original,lease=lease)
            app.state.originals.unlink_exact=failure
            try:pending=await runtime.deletions.confirm(single['id'],single['revision'],impact['impact_sha256'],key)
            finally:app.state.originals.unlink_exact=unlink
            evidence.observe('09-pending-delete',pending)
            if pending['state']!='deleted_pending':raise RuntimeError('物理unknown被冒done')
            retry=await runtime.deletions.retry_cleanup(pending['job_id'])
            evidence.observe('10-retry',{'receipt':retry,'removed':not (app.state.originals.root/single['sha256']).exists()})
            if retry['state']!='deleted':raise RuntimeError('清理重试未完成')
            with runtime.source.connection(readonly=True) as conn:
                row=conn.execute('SELECT revision,current_version FROM public.material_sources WHERE id=%s',(single['id'],)).fetchone()
            if row['revision']!=single['revision']+1 or row['current_version'] is not None:raise RuntimeError('重试二次删除')
            evidence.observe('11-idempotent-revision',row)
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(deletions())
        # 只保存新计划，复用旧包；后续独立目标核删除覆盖与快照策略。
        record=runtime.hub.state()['plans']['271e9dd7-e982-4daa-9854-4beffac445a1']
        old_plan=runtime.restore.plan(record['plan_id'],record['plan_sha256'])
        current_plan=runtime.restore.prepare(old_plan['upload_id'],'respect_current_deletions',runtime.context())
        evidence.observe('12-current-deletions-plan',current_plan)
        evidence.observe('13-latest-accounting',runtime.source.latest())
        return {'state':'passed','source_fixture_reused':True,'new_materials':[a['id'],b['id'],shared['id'],single['id']],'current_plan':current_plan}
    finally:stop_source(budget,target)
