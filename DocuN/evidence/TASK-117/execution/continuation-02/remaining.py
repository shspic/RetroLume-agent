"""根16合并余项：持久业务、固定预览、传播与最终隔离恢复，串行消费者。"""
from batch_runtime import *
from frozen_http import FrozenFlow,SAMPLES
from http_remaining import case,interview_after,variants,neutral,late_memory,delete_auxiliary
from business import generate
from profiles_batch import runtime_config
from final_restore import final_restore
from preview_case import run_preview
from uuid import uuid4
import asyncio,traceback
from app.runtime import psycopg_compatible_loop_factory

def readonly_view(flow):
    session=flow.call('GET','/api/session');assert session['data_context']['mode']=='restored_readonly'
    caps=flow.call('GET','/api/data/capabilities');records={}
    for category in ('activities','teaching','interview','learning','memories'):
        records[category]=flow.call('GET','/api/data/saved-records?category='+category)
    refused=[]
    for path,body in (('/api/activities',{}),('/api/materials?filename=forbidden.md',{}),('/api/memories/commands',{})):
        value=flow.call('POST',path,body,expected=409);assert 'data_readonly' in str(value);refused.append({'path':path,'response':value})
    return {'session':{k:v for k,v in session.items() if k!='token'},'caps':caps,'records':records,'writes_refused':refused,'fallback_source':False}

def main():
    preflight('S03-root16-remaining-merged',preview=True)
    with Batch(16,'S03_remaining_business_preview_propagation_and_restores') as batch:
        rc.start_pg('source');batch.start_api(launcher=True)
        flow=FrozenFlow('root16-normal')
        aids=json.loads((C01/'X09-before-normal-reopen.json').read_text())['aids']
        try:
            # HTTP对正式bundle的真实加载只证明字节，不冒浏览器验证。
            bundle=json.loads((C01/'bundle-6.json').read_text());loaded=[]
            for row in bundle['files']:
                url='/'+row['path'].removeprefix('frontend/dist/');c.count('http');r=flow.client.get(url);assert r.status_code==200 and c.sha(r.content)==row['sha256'];loaded.append({'url':url,'sha256':c.sha(r.content)})
            c.write(C01/'bundle-6-actual-HTTP.json',{'sample':c.sample(),'files':loaded,'Browser':'NOT_RUN; cumulative cap8 reached'})
            result=case('I01-after-normal-reopen',lambda:interview_after(flow,aids[1]))
            teaching=flow.call('GET',f'/api/activities/{aids[0]}/teaching/workspace')
            assert teaching['head']['phase']=='feedback_ready'
            c.write(C01/'L01-L05-I01-X09-final.json',{'sample':c.sample(),'aids':aids,'teaching':teaching,'interview':result,'U_scope':'bundle5教学末评价及面试probe回答；原ask恢复及最终面试反馈为HTTP，bundle6没有新Browser证','normal_reopen':'原stdin/句柄关闭应用并同normal库重开；PG由原根控制器连续持有，没有声称PG重启'})
            artifact=case('L10-current-artifact',lambda:generate(flow,aids[0]))
            if artifact:
                c.write(C01/'L10-current-artifact.json',{'activity_id':aids[0],'artifact':artifact})
                case('L10-fixed-host',lambda:run_preview(batch,flow,aids[0],artifact['artifact_id']))
            mapping=json.loads((C01/'frozen-source-bindings.json').read_text())
            case('L06-concept-three-answers',lambda:variants(flow,mapping,'C',SAMPLES['inputs']['concept_goal'],[SAMPLES['inputs'][k] for k in ('concept_positive','concept_negative','concept_partial')]))
            case('L07-program-two-answers',lambda:variants(flow,mapping,'P','阅读range循环，逐步推理累加结果，不执行代码。',[SAMPLES['inputs'][k] for k in ('program_positive','program_negative')]))
            for name,aliases,goal,expected in [('L08-ambiguity',['J-CODE','J-COFFEE'],SAMPLES['inputs']['ambiguous_goal'],'clarification'),('L09-insufficient',['N'],SAMPLES['inputs']['no_evidence_query'],'no_evidence'),('L09-conflict',['N','N-CONFLICT'],SAMPLES['inputs']['conflict_query'],'conflict')]:
                case(name,lambda aliases=aliases,goal=goal,expected=expected:neutral(flow,mapping,aliases,goal,expected))
            memory=flow.call('GET','/api/memories/'+json.loads((C01/'frozen-memory-binding.json').read_text())['memory_id'])
            # 先固定预览，再修订被两域选中的背景；不破坏尚待预览的父来源。
            learning=json.loads((C01.parent/'continuation-01/memory-teaching-before-reopen.json').read_text())['activity_id']
            case('X02-late-memory',lambda:late_memory(flow,mapping,memory,learning))
            deletion=case('X10-real-deletion-overlay',lambda:delete_auxiliary(flow));assert deletion is not None
        finally:flow.close()
        batch.close_api()
        runtime=runtime_config(batch.run)
        restored=final_restore(batch.run,runtime=runtime,keep_source=True)
        c.write(C01/'P03-real-roundtrip.json',restored)
        verified=json.loads((C01/'final-r02-verified.json').read_text());receipt=verified['receipt'];plan=verified['plan']
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            activated=runner.run(runtime.restore.activate_readonly(receipt['job_id'],plan['plan_sha256'],str(uuid4()),0))
        assert activated['state']=='active_readonly';c.write(C01/'R02-real-selector-activation.json',activated)
        # 选择已发布，关闭源PG；应用启动只能绑定封印目标，不能回退source。
        rc.stop_pg('source')
        reader=batch.fresh_api_handle();reader.start_api(read_only_factory=True)
        view=FrozenFlow('root16-R02-readonly')
        try:case('P03-application-readonly',lambda:readonly_view(view))
        finally:view.close()

if __name__=='__main__':
    try:main()
    except BaseException:
        p=C01/('root16-failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc(),encoding='utf-8');c.failure('S03-root16',p.name,effect='保留所有已提交事实，清场；独立部分按精确断点继续，不重建目标');raise
