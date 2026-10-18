"""根16原截止内修复后定向宿主验证，复用已获准且仍normal的compat原CID。"""
from batch_runtime import *
from frozen_http import FrozenFlow,SAMPLES
from business import generate
from preview_case import run_preview
from uuid import uuid4
from urllib.parse import quote
import traceback

def main():
    preflight('root16-preview-ordinary-fix-recheck',preview=True)
    c.write(C01/'preview-recheck-intent.json',{'sample':c.sample(),'root':16,'source_slot':'compat','reason':'HTML资格ACL投影遗漏已通过真实普通PG指纹修复。source已完成不可逆R02选择，不能回normal；复用本卡已修补且保留normal的原compat库建立独立纯合成N父反馈','inherited_L01_performance':False,'scope':'普通产品app、既有normal合成库、冻结N、一个新合法父feedback及固定宿主；不改R01/R02或旧迁移/旧业务行','API_remaining':19-c.state()['counts']['api_starts'],'PG_remaining':28-c.state()['counts']['pg_starts'],'Browser_started':0})
    with Batch(16,'S03_root16_preview_after_catalog_repair') as batch:
        rc.start_pg('compat');batch.start_api(source_slot='compat')
        flow=FrozenFlow('root16-preview-compat')
        try:
            session=flow.call('GET','/api/session');assert session['data_context']['mode']=='normal'
            source=next(s for s in SAMPLES['sources'] if s['alias']=='N')
            rows=flow.call('GET','/api/materials')['items'];wanted=c.sha(source['text'].encode())
            material=next((r for r in rows if r['sha256']==wanted and r['title']==source['filename']),None)
            if material is None:material=flow.call('POST','/api/materials?filename='+quote(source['filename']),content=source['text'].encode())['material']
            aid=flow.create([material]);c.write(C01/'preview-dedicated-parent-intent.json',{'activity_id':aid,'source_slot':'compat','source_id':material['id'],'purpose':'独立明确的固定预览合成父成果，不追认原L01资格','memory':None})
            flow.index(aid);w=flow.teaching(aid,'goal',{'goal':'根据速度.md核对平均速度的分钟换秒。'})
            w=flow.teaching(aid,'plan',{'confirmed':True})
            w=flow.teaching(aid,'accept_path',{'proposal_record_id':w['proposal']['record_id']})
            w=flow.teaching(aid,'select_node',{'path_record_id':w['head']['path_record_id'],'node_id':'n1'})
            w=flow.teaching(aid,'exercise',{'confirmed':True,'path_record_id':w['head']['path_record_id'],'node_id':'n1','purpose':'initial'})
            w=flow.teaching(aid,'answer',{'exercise_record_id':w['head']['exercise_record_id'],'kind':'initial','text':'1米每秒；2分钟是120秒，120米除以120秒。'})
            w=flow.teaching(aid,'evaluate',{'confirmed':True,'exercise_record_id':w['head']['exercise_record_id'],'answer_record_id':w['head']['answer_record_id']})
            artifact=generate(flow,aid);c.write(C01/'L10-repaired-parent-artifact.json',{'activity_id':aid,'feedback':w,'artifact':artifact,'normal_slot':'compat'})
            run_preview(batch,flow,aid,artifact['artifact_id'])
            c.write(C01/'L10-real-fixed-host-complete.json',{'sample':c.sample(),'activity_id':aid,'artifact_id':artifact['artifact_id'],'normal_slot':'compat','S_fixed_host':True,'U_application_browser':'NOT_RUN; cap8','Q':'NOT_ENABLED'})
        finally:flow.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        p=C01/('preview-recheck-failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc(),encoding='utf-8');c.failure('S03-preview-recheck',p.name,effect='保存真实失败和自动清场，不换名重复运行');raise
