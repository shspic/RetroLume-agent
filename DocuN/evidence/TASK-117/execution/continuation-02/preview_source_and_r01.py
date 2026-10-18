"""根16原截止内修复后定向宿主验证，复用仍normal的source原CID，最后查看既有R01。"""
from batch_runtime import *
from frozen_http import FrozenFlow,SAMPLES
from business import generate
from preview_case import run_preview
from uuid import uuid4
from urllib.parse import quote
import traceback

def main():
    preflight('root16-preview-ordinary-fix-recheck',preview=True)
    c.write(C01/'preview-recheck-intent.json',{'sample':c.sample(),'root':16,'source_slot':'source','reason':'HTML资格ACL投影遗漏已通过真实普通PG指纹修复。source已完成不可逆R02选择，不能回normal；复用本卡已修补且保留normal的原compat库建立独立纯合成N父反馈','inherited_L01_performance':False,'scope':'普通产品app、既有normal合成库、冻结N、一个新合法父feedback及固定宿主；不改R01/R02或旧迁移/旧业务行','API_remaining':19-c.state()['counts']['api_starts'],'PG_remaining':28-c.state()['counts']['pg_starts'],'Browser_started':0})
    with Batch(16,'S03_root16_preview_after_catalog_repair') as batch:
        rc.start_pg('source');batch.start_api(launcher=True)
        flow=FrozenFlow('root16-preview-source')
        try:
            session=flow.call('GET','/api/session');assert session['data_context']['mode']=='normal'
            source=next(s for s in SAMPLES['sources'] if s['alias']=='N')
            rows=flow.call('GET','/api/materials')['items'];wanted=c.sha(source['text'].encode())
            material=next((r for r in rows if r['sha256']==wanted and r['title']==source['filename']),None)
            if material is None:material=flow.call('POST','/api/materials?filename='+quote(source['filename']),content=source['text'].encode())['material']
            aid=flow.create([material]);c.write(C01/'preview-dedicated-parent-intent.json',{'activity_id':aid,'source_slot':'source','source_id':material['id'],'purpose':'独立明确的固定预览合成父成果，不追认原L01资格','memory':None})
            flow.index(aid);w=flow.teaching(aid,'goal',{'goal':'根据速度.md核对平均速度的分钟换秒。'})
            w=flow.teaching(aid,'plan',{'confirmed':True})
            w=flow.teaching(aid,'accept_path',{'proposal_record_id':w['proposal']['record_id']})
            w=flow.teaching(aid,'select_node',{'path_record_id':w['head']['path_record_id'],'node_id':'n1'})
            w=flow.teaching(aid,'exercise',{'confirmed':True,'path_record_id':w['head']['path_record_id'],'node_id':'n1','purpose':'initial'})
            w=flow.teaching(aid,'answer',{'exercise_record_id':w['head']['exercise_record_id'],'kind':'initial','text':'1米每秒；2分钟是120秒，120米除以120秒。'})
            w=flow.teaching(aid,'evaluate',{'confirmed':True,'exercise_record_id':w['head']['exercise_record_id'],'answer_record_id':w['head']['answer_record_id']})
            artifact=generate(flow,aid);c.write(C01/'L10-repaired-parent-artifact.json',{'activity_id':aid,'feedback':w,'artifact':artifact,'normal_slot':'source'})
            run_preview(batch,flow,aid,artifact['artifact_id'])
            c.write(C01/'L10-real-fixed-host-complete.json',{'sample':c.sample(),'activity_id':aid,'artifact_id':artifact['artifact_id'],'normal_slot':'source','S_fixed_host':True,'U_application_browser':'NOT_RUN; cap8','Q':'NOT_ENABLED'})
        finally:flow.close()
        batch.close_api()
        from profiles_batch import runtime_config
        from remaining import readonly_view
        from app.runtime import psycopg_compatible_loop_factory
        import asyncio
        runtime=runtime_config(batch.run)
        saved=json.loads((C01.parent/'continuation-01/restore-r01-receipt.json').read_text())
        plan=runtime.restore.plan(saved['plan_id'],saved['plan_sha256'])
        assert plan['deletion_policy']=='snapshot_only_readonly'
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            selected=runner.run(runtime.restore.activate_readonly(saved['job_id'],saved['plan_sha256'],str(uuid4()),0))
        assert selected['state']=='active_readonly';c.write(C01/'R01-real-selector-activation.json',selected)
        rc.stop_pg('source')
        reader=batch.fresh_api_handle();reader.start_api(read_only_factory=True)
        view=FrozenFlow('root16-R01-readonly')
        try:c.write(C01/'P02-application-readonly.json',{'sample':c.sample(),'status':'passed_at_stated_layer','result':readonly_view(view),'R01_migrations_unchanged':True,'R02_failed_never_activated':True})
        finally:view.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        p=C01/('preview-recheck-failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc(),encoding='utf-8');c.failure('S03-preview-recheck',p.name,effect='保存真实失败和自动清场，不换名重复运行');raise
