"""单独新fault集群：可信迁移拒绝非空/已有role，不复用失败目标。"""
import json
from pathlib import Path
from uuid import uuid4
from budget import ROOT
from app.data_exit.contracts import DataError
from app.data_exit.restore import inspect_target
from setup_source import IMAGE

def fault_group(budget,evidence,source,credentials):
    from continue_run import runtime_for
    import psycopg
    app,rt=runtime_for(credentials,budget)
    try:rt.factory.allocate(str(uuid4()),'package-chosen-profile')
    except DataError as e:
        if e.code!='restore_executor_missing':raise
        evidence.observe('01-wrong-profile-rejected',{'code':e.code,'allocated':False})
    else:raise RuntimeError('包自选profile被采用')
    negatives=[]
    def stage(target,cred,slot):
        evidence.observe('02-fault-identity',inspect_target(target,IMAGE))
        directory=ROOT/'backend/migrations'
        files={int(p.name[:3]):p for p in directory.glob('*.sql') if int(p.name[:3])<=13}
        with psycopg.connect(cred['admin_dsn'],autocommit=True,connect_timeout=3) as conn:
            for n in (1,2,3):conn.execute(files[n].read_text(encoding='utf-8-sig'))
            for n in (4,5):
                conn.execute('BEGIN')
                cols='id,status,scope_revision,deadline_at,max_requests,max_cost_microunits,reserve_cost_microunits,max_request_bytes,max_output_tokens'
                vals="%s,'pending',1,CURRENT_TIMESTAMP+interval '1 hour',4,100,1,4096,128"
                if n==5:cols+=',max_running_seconds';vals+=',60'
                conn.execute('INSERT INTO public.activities('+cols+') VALUES('+vals+')',(str(uuid4()),))
                count=conn.execute('SELECT count(*) FROM public.activities').fetchone()[0]
                try:conn.execute(files[n].read_text(encoding='utf-8-sig'))
                except psycopg.Error as error:
                    if error.sqlstate!='P0001' or str(n).zfill(3) not in error.diag.message_primary:raise
                    negatives.append({'migration':files[n].name,'nonempty_count_in_actual_transaction':count,'sqlstate':error.sqlstate,'message_primary':error.diag.message_primary,'fixture_commit':'uncommitted legal row, explicitly rolled back after rejection'})
                else:raise RuntimeError('非空迁移未拒绝')
                conn.rollback();conn.execute(files[n].read_text(encoding='utf-8-sig'))
            for n in range(6,10):conn.execute(files[n].read_text(encoding='utf-8-sig'))
            for n,role in ((10,'retrolume_memory_owner'),(11,'retrolume_interview_owner')):
                conn.execute('BEGIN');conn.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE')
                try:conn.execute(files[n].read_text(encoding='utf-8-sig'))
                except psycopg.Error as error:
                    if error.sqlstate!='P0001':raise
                    negatives.append({'migration':files[n].name,'existing_role':role,'sqlstate':error.sqlstate,'message_primary':error.diag.message_primary,'injection_rolled_back':True})
                else:raise RuntimeError('已有角色未拒绝')
                conn.rollback();conn.execute(files[n].read_text(encoding='utf-8-sig'))
            evidence.observe('03-actual-migration-negatives',negatives)
            # 明确failed，不能把负例已用集群再接成恢复目标。
            raise DataError('c01_expected_fault_target',503)
    rt.factory._initialize=stage
    try:rt.factory.allocate(str(uuid4()),rt.factory.profile['id'])
    except DataError as e:
        if e.code!='c01_expected_fault_target':raise
    else:raise RuntimeError('fault target意外作为正常恢复')
    evidence.observe('04-failed-retained',{'source_stopped':not inspect_target(source,IMAGE)['running'],'negative_count':len(negatives),'failed_target_not_reused':True})
    return {'state':'passed','negative_count':len(negatives),'separate_fault_cluster':True}
