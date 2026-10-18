"""两个独立目标对照默认删除覆盖与显式snapshot只读，原source不改。"""
import json
from uuid import uuid4
from budget import ROOT,EVIDENCE
from app.data_exit.contracts import DataJobCommand
from app.data_exit.restore import inspect_target
from setup_source import IMAGE

def overlay_group(budget,evidence,source,credentials):
    from continue_run import runtime_for
    import psycopg
    from app.materials.repository import PostgresMaterials
    if inspect_target(source,IMAGE)['running']:raise RuntimeError('恢复组要求source stopped')
    app,rt=runtime_for(credentials,budget)
    selected=json.loads((EVIDENCE/'batches/c01-race-1134754921000000/result.json').read_bytes())
    out=[]
    for name in ('respect_plan','snapshot_plan'):
        public=selected[name];plan=rt.restore.plan(public['plan_id'],public['plan_sha256'])
        job=rt.hub.create_or_get_job(DataJobCommand('restore','c01-overlay-'+str(uuid4()),{'plan_id':public['plan_id'],'plan_sha256':public['plan_sha256']}),rt.context())
        evidence.observe(name+'-01-job',job)
        verified=rt.restore.verify(job['job_id'],public['plan_sha256']);evidence.observe(name+'-02-verified',verified)
        target=rt.factory.target(verified['target_id']);credential=rt.factory.readonly_credentials(target.target_id)
        rt.factory.start(target)
        try:
            rt.factory._wait_pg(credential['readonly_dsn'])
            from app.data_exit.repository import DataRepository
            safe=DataRepository(credential['readonly_dsn']).safe_state()
            material=PostgresMaterials(credential['readonly_dsn']).get(selected['deleted_old_source_id'])
            with psycopg.connect(credential['readonly_dsn'],connect_timeout=3) as conn:
                tomb=conn.execute("SELECT entity_kind,entity_id,effective_revision FROM public.data_export_tombstones_v1 WHERE entity_kind='source' AND entity_id=%s",(selected['deleted_old_source_id'],)).fetchall()
                clock=conn.execute('SELECT starts_used,reserved_seconds,settled_seconds FROM public.html_preview_budgets').fetchall()
            if name=='respect_plan' and (material is not None or len(tomb)!=1):raise RuntimeError('当前删除没有覆盖旧包')
            if name=='snapshot_plan' and (material is None or tomb):raise RuntimeError('显式快照策略错误或改源墓碑')
            result={'policy':plan['deletion_policy'],'verified_job':verified,'target_id':target.target_id,'safe_control':safe,'old_source_lookup':material,'source_tombstones':tomb,
                    'preview_accounting':clock,'readonly_probe':rt.factory._probe_readonly(credential['readonly_dsn'],target),'source_unchanged_stopped':not inspect_target(source,IMAGE)['running']}
            evidence.observe(name+'-03-actual',result);out.append(result)
        finally:rt.factory.stop(target)
    return {'state':'passed','comparison':out,'source_tombstone_not_revoked':True}
