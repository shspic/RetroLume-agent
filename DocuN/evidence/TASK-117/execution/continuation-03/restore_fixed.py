"""根18只验证原617行包和原控制根的新成功slot；normal余项未闭，不激活选择器。"""
from batch_runtime import *
from profiles_batch import runtime_config,PackageReader,DataJobCommand
from uuid import uuid4
import shutil,traceback


def main():
    preflight('S04-root18-fixed-R02')
    gate=json.loads((C01/'restore-first-target-gate.json').read_text());assert gate['status']=='offline_gate_satisfied'
    package=EXEC/'synthetic/source-backup/packages/7a10f64c-26bc-4c89-a409-4417ddc1a6dc.rldata'
    assert c.sha(package.read_bytes())==gate['same_package_file_sha256']
    with PackageReader(package) as reader:
        assert reader.manifest['root_sha256']==gate['root_sha256'] and len(reader.schema_profile.tables)==31
    with Batch(18,'S04_original_617_rows_R02_loader_repair') as batch:
        rc.start_pg('source');runtime=runtime_config(batch.run);context=runtime.context()
        assert context.mode=='normal' and runtime.hub.state()['selection'] is None
        upload=str(uuid4());shutil.copyfile(package,runtime.incoming/(upload+'.rldata'))
        plan=runtime.restore.prepare(upload,'respect_current_deletions',context)
        job=runtime.hub.create_or_get_job(DataJobCommand('restore',str(uuid4()),{'plan_id':plan['plan_id'],'plan_sha256':plan['plan_sha256']}),context)
        files=[ROOT/'backend/app/data_exit/control.py',ROOT/'backend/app/data_exit/operations.py',ROOT/'backend/app/data_exit/restore.py',Path(__file__),C01/'profiles_batch.py']
        c.write(C01/'root18-before-create-as-run.json',{'sample':c.sample(),'job_id':job['job_id'],'plan':plan,'package_file_sha256':c.sha(package.read_bytes()),'original_full_control_journal_bytes':runtime.hub.path.stat().st_size,'files':[{'path':str(p.relative_to(ROOT)),'sha256':c.sha(p.read_bytes())} for p in files],'source_context':context.public(),'normal_UI_and_L10_unclosed':True,'activation_performed':False,'limits':runtime.limits.__dict__})
        start=time.monotonic();receipt=runtime.restore.verify(job['job_id'],plan['plan_sha256'])
        assert receipt['state']=='verified';target=runtime.hub.state()['targets'][receipt['target_id']]
        assert target['slot_id']=='r02-success-01' and target['state']=='sealed'
        proof=json.loads(runtime.hub.read_artifact('receipts',job['job_id'],target['verification_sha256']))
        assert len(proof['actual_rows'])==31 and proof['execution_authority'] is False
        state=runtime.hub.state();assert state['selection'] is None and state['fence'] is None
        c.write(C01/'P03-S04-verified.json',{'sample':c.sample(),'receipt':receipt,'plan':plan,'target':{k:v for k,v in target.items() if k!='credential_ref'},'proof':proof,'verify_seconds':time.monotonic()-start,'same_original_617_row_package':True,'scope':'产品_load逐列codec canonical回读相等，含512维float32/007/unknown/预留/删源覆盖；seal后真实只读角色SQL拒写和撤loader，非仅counts','inherited_source_facts':str(EXEC/'continuation-02/source-r02-final-package.json'),'R01_application_GET':'NOT_RUN','R02_application_GET':'NOT_RUN','reason_not_activated':'根17仍有normal前端/范围/记忆余项及固定宿主停止协议未闭；不以只读切换阻断后续normal工作','selection':None,'fence':None})


if __name__=='__main__':
    try:main()
    except BaseException:
        p=C01/('root18-failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc(),encoding='utf-8');c.failure('S04-root18',p.name,effect='保留失败目标和原617行包；不自动消费第二slot，不放宽30秒/约束或回正常');raise
