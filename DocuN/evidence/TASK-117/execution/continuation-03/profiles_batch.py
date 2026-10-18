"""S02首次真实批：所有自有PG先登记截止闭包；不启动API或浏览器。"""
from pathlib import Path
import sys, os, json, shutil, time, subprocess, traceback
from types import SimpleNamespace
from uuid import uuid4
C01=Path(__file__).resolve().parent
EXEC=C01.parent
ROOT=EXEC.parents[3]
sys.path[:0]=[str(EXEC),str(ROOT/'backend'),str(ROOT/'backend/tests'),str(ROOT/'backend/tests/fixtures/step018')]
import control as c
import runtime_control as rc
from lifecycle import BoundedResources
import psycopg
from psycopg.rows import dict_row
from app.activities.repository import PostgresAdmissionLedger
from app.materials.repository import PostgresMaterials
from app.storage.originals import OriginalStore
from app.data_exit.config import DataRuntime
from app.data_exit.contracts import DataJobCommand, PROFILE, canonical
from app.data_exit.schema_profiles import R02, extra_shape_queries, check_extra_shape, normalized_extra_shape
from app.data_exit.schema_checks import assert_data_schema_sync
from app.data_exit.packages import PackageReader
from test_step018_profiles_pg import verify_readonly_target
from test_step018_retrieval_pg import verify_persistent_retrieval


def listeners():
    raw=subprocess.run(['powershell','-NoProfile','-Command',
      "Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in 15481,15482,15483,15484,15485,15486,15487,18118} | Select-Object LocalAddress,LocalPort,OwningProcess | ConvertTo-Json -Compress"],capture_output=True,timeout=15).stdout.decode('utf-8','replace').strip()
    return json.loads(raw) if raw else []


class Hooks:
    def __init__(self,run,factory):self.run,self.factory,self.targets=run,factory,{}
    def before_create(self,slot):
        self.run.check()
        sid=slot['id']
        # 登记在create前。即使create已经生效却未返回，仍按精确名字+工厂持久意图核身份。
        self.run.register('restore-'+sid,lambda:self.close_slot(slot),priority=0)
        rc.pg_memory_gate('restore-create-'+sid);rc.port_gate(slot['port'])
        c.count('pg_create_attempts');c.count('volumes')
        rc.save_resource({'id':'pg-'+sid,'kind':'pg','slot':sid,'name':slot['name'],'volume':slot['volume'],'port':slot['port'],'database':slot['database'],'image':rc.PG_IMAGE,'intent':c.sample(),'cid':None,'running':False})
    def close_slot(self,slot):
        target=self.targets.get(slot['id'])
        if target is not None:
            self.factory.stop(target)
            proof=rc.metadata(target.cid)
        else:
            cid=rc.docker(['ps','-aq','--filter','name=^/'+slot['name']+'$'])
            if not cid:return {'not_created':True,'name':slot['name']}
            proof=rc.metadata(cid)
            intent=next((t for t in self.factory.hub.state()['targets'].values() if t['slot_id']==slot['id']),None)
            if (not intent or proof['name']!=slot['name'] or proof['image']!=rc.PG_IMAGE
              or proof['labels'].get('retrolume.data.job')!=intent['job_id']
              or proof['labels'].get('retrolume.data.profile')!=self.factory.profile['id']
              or proof['labels'].get('retrolume.data.target')!=intent['target_id']):raise RuntimeError('partial_target_identity_unknown')
            if proof['running']:rc.docker(['stop','--time','10',cid],timeout=20)
            proof=rc.metadata(cid)
        if proof['running'] or proof['pid']!=0:raise RuntimeError('target_stop_unknown')
        return proof
    def created(self,target,identity):
        sid=target.name.removeprefix('retrolume-step018-syn-');self.targets[sid]=target
        c.count('pg_objects')
        row=next(r for r in c.state()['resources'] if r['id']=='pg-'+sid)
        row.update(cid=target.cid,created=c.sample(),factory_job_id=target.job_id,factory_profile_id=target.profile_id)
        rc.save_resource(row);c.event('restore_target_created',identity=rc.metadata(target.cid))
    def before_start(self,target):
        self.run.check();rc.pg_memory_gate('restore-start-'+target.name);rc.port_gate(target.port);c.count('pg_starts')
        row=next(r for r in c.state()['resources'] if r.get('cid')==target.cid)
        row.update(running=True,holding_start=c.sample());rc.save_resource(row)
    def started(self,target,identity):c.event('restore_target_started',identity=rc.metadata(target.cid))
    def stopped(self,target,identity):
        row=next(r for r in c.state()['resources'] if r.get('cid')==target.cid);stamp=c.sample()
        if row.get('running'):row.setdefault('holding_intervals',[]).append({'start':row['holding_start'],'end':stamp,'segment':c.state()['active_segment']})
        row.update(running=False,stopped=stamp);rc.save_resource(row)
        c.event('restore_target_stopped',identity=rc.metadata(target.cid))


def compat_repair():
    proof={}
    for slot in ('source','compat'):
        rc.start_pg(slot)
        with psycopg.connect(rc.dsn(slot,'admin'),row_factory=dict_row) as db:
            before=db.execute("SELECT has_table_privilege('retrolume_interview_owner','public.teaching_commands','SELECT') AS read,has_table_privilege('retrolume_interview_owner','public.teaching_commands','INSERT,UPDATE,DELETE') AS write").fetchone()
            old=db.execute('SELECT operation_id,kind,request_bytes,max_output_tokens,reserved_cost_microunits,state,disposition FROM public.activity_operations ORDER BY operation_id').fetchall()
            funcs=db.execute("SELECT p.proname,p.prosrc,p.prosecdef,p.provolatile,p.proconfig FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname IN('interview_head_guard','interview_record_insert_guard','interview_result_eligible') ORDER BY p.proname").fetchall()
            if before['write']:raise RuntimeError('unexpected_invoker_write_privilege')
            if slot=='compat' and not before['read']:db.execute('GRANT SELECT ON public.teaching_commands TO retrolume_interview_owner')
            after=db.execute("SELECT has_table_privilege('retrolume_interview_owner','public.teaching_commands','SELECT') AS read,has_table_privilege('retrolume_interview_owner','public.teaching_commands','INSERT,UPDATE,DELETE') AS write").fetchone()
            assert after=={'read':True,'write':False}
            assert old==db.execute('SELECT operation_id,kind,request_bytes,max_output_tokens,reserved_cost_microunits,state,disposition FROM public.activity_operations ORDER BY operation_id').fetchall()
            assert_data_schema_sync(db)
            shape={k:db.execute(q).fetchall() for k,q in extra_shape_queries().items()};check_extra_shape(shape)
            proof[slot]={'cid':next(x['cid'] for x in c.state()['resources'] if x['id']=='pg-'+slot),'before':before,'after':after,'legacy_operations':old,'functions':funcs,'extra_shape_sha':c.sha(canonical(normalized_extra_shape(shape)).encode()),'exact_schema':True,'migrations_rerun':0}
        rc.stop_pg(slot)
    assert proof['source']['functions']==proof['compat']['functions']
    baseline=json.loads((EXEC/'compat-catalog-before014.json').read_text(encoding='utf-8'))
    assert proof['compat']['legacy_operations']==baseline['legacy']
    c.write(C01/'compat-final-forward-repair.json',proof)


def factory_profile():
    return {'id':'TASK117-S02-fixed-restores','image_id':rc.PG_IMAGE,'login_prefix':'step018_','pg_major':17,'source_name':'retrolume-step018-syn-source','slots':[{'id':s,'name':'retrolume-step018-syn-'+s,'volume':'retrolume-step018-syn-'+s+'-data','port':rc.SLOTS[s][0],'database':rc.SLOTS[s][1],'schema_profile':p} for s,p in [('r01',PROFILE),('r02-fault',R02),('r02',R02),('r02-success-01',R02),('r02-success-02',R02)]]}

def runtime_config(run):
    base=EXEC/'synthetic/source-data';backup=EXEC/'synthetic/source-backup'
    os.environ.update(RETROLUME_CONTROL_ROOT=str(EXEC/'synthetic/source-control'),RETROLUME_RESTORE_ROOT=str(EXEC/'synthetic/source-restore'),RETROLUME_DATABASE_URL=rc.dsn('source'),RETROLUME_TASK117_SNAPSHOT=rc.dsn('source','snapshot'),RETROLUME_TASK117_MAINTENANCE=rc.credentials('source')['maintenance_key'])
    app=SimpleNamespace(state=SimpleNamespace(activities_ledger=PostgresAdmissionLedger(rc.dsn('source')),materials=PostgresMaterials(rc.dsn('source')),originals=OriginalStore(base/'originals'),preview_controller=None,preview_policy=None))
    profile=factory_profile()
    runtime=DataRuntime(app,SimpleNamespace(data_dir=base,backup_dir=backup),{'maintenance_key_env':'RETROLUME_TASK117_MAINTENANCE','snapshot_url_env':'RETROLUME_TASK117_SNAPSHOT','factory':profile})
    run.register('source-original-lease',runtime.references.lease.close,priority=1)
    runtime.factory.hooks=Hooks(run,runtime.factory)
    return runtime

