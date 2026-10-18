"""根17仅补normal余项，继承两域历史；不做只读选择。"""
from batch_runtime import *
from frozen_http import FrozenFlow,SAMPLES
from business import generate
from preview_case import run_preview
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import traceback


def save(name,value):c.write(C01/(name+'.json'),{'sample':c.sample(),**value})


def independent_cleanup(flow,mapping):
    # 公开记忆合同的删除正文入口为确认revoke+purge，不捏造DELETE接口。
    mid=str(uuid4());key=str(uuid4())
    flow.call('POST','/api/memories/commands',{'business_key':key,'memory_id':mid,'expected_revision':0,'action':'save','body':{'kind':'preference','title':'S04独立清理','text':SAMPLES['inputs']['memory_body']}})
    memory=flow.call('GET','/api/memories/'+mid);aid=flow.create([mapping['N']],memory)
    flow.teaching(aid,'goal',{'goal':'平均速度与分钟换秒'});flow.index(aid)
    status=flow.call('GET',f'/api/activities/{aid}/retrieval/status')
    gate=C01/'late-transport';gate.mkdir(exist_ok=True)
    if (gate/'ready.json').exists() or (gate/'release').exists():raise RuntimeError('fresh_cleanup_gate_required')
    command={'business_key':str(uuid4()),'action':'query','expected_scope_revision':status['scope_revision'],'expected_domain_revision':status['domain_revision'],'query':'S02晚到记忆','confirmed':True}
    save('independent-memory-cleanup-intent',{'memory_id':mid,'activity_id':aid,'query':command,'mode':'public_revoke_with_content_cleanup'})
    c.count('http');c.count('native_windows')
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(flow.client.post,f'/api/activities/{aid}/retrieval/commands',json=command)
        try:
            until=time.monotonic()+25
            while not (gate/'ready.json').exists():
                if future.done() or time.monotonic()>until:raise RuntimeError('cleanup_not_dispatched')
                time.sleep(.03)
            current=flow.call('GET','/api/memories/'+mid)
            impact=flow.call('GET',f"/api/memories/{mid}/impact?expected_revision={current['revision']}&action=revoke")
            changed=flow.call('POST','/api/memories/commands',{'business_key':str(uuid4()),'memory_id':mid,'expected_revision':current['revision'],'action':'revoke','body':{'impact_token':impact['impact_token'],'confirm_revoke':True,'purge_memory_content':True}})
        finally:(gate/'release').write_text('release',encoding='ascii')
        response=future.result(timeout=105);receipt=response.json()
    after=flow.call('GET','/api/memories/'+mid);selection=flow.call('GET',f'/api/activities/{aid}/memory-selection')
    assert not receipt['current'] and receipt['terminal_disposition']=='invalidated'
    assert not selection['eligible'] and after['body'] is None and after['purge_state']=='done'
    save('X02-independent-content-cleanup',{'activity_id':aid,'memory_id':mid,'actual_query':command,'HTTP':response.status_code,'late_receipt':receipt,'change':changed,'after':after,'selection':selection,'new_protocol_action':False})


def main():
    preflight('S04-root17-normal-UI-preview',preview=True)
    with Batch(17,'S04_normal_UI_preview_and_remaining') as batch:
        rc.start_pg('source');batch.start_api(launcher=True)
        flow=FrozenFlow('root17-normal')
        try:
            session=flow.call('GET','/api/session');assert session['data_context']['current_mode']=='normal'
            # S03已提交旧场次只读继承，不重发其answer/probe/evaluate。
            save('inherited-S03-current',{'teaching':flow.call('GET','/api/activities/93852e50-f648-4cb1-a2e8-5f8283975567/teaching/workspace'),'interview':flow.call('GET','/api/activities/06c8a779-a936-423d-9554-010f9ebcfb8e/interview/workspace'),'old_unknown_reissued':False})
            mapping=json.loads((EXEC/'continuation-02/frozen-source-bindings.json').read_text())
            intent_path=C01/'normal-intent.json'
            if intent_path.exists():intent=json.loads(intent_path.read_text())
            else:
                tid=flow.create([mapping['N']]);iid=flow.create([mapping['R'],mapping['M']])
                intent={'teaching_activity_id':tid,'interview_activity_id':iid,'purpose':'S04无选记忆、最少合法父成果与最终UI；不替代S03两链表现','source_slot':'source'};c.write(intent_path,intent)
            tid,iid=intent['teaching_activity_id'],intent['interview_activity_id']
            w=flow.call('GET',f'/api/activities/{tid}/teaching/workspace')
            if w['head']['revision']==0:w=flow.teaching(tid,'goal',{'goal':'根据速度.md核对平均速度、分钟换秒。'})
            flow.index(tid)
            if not w['head']['path_record_id']:
                w=flow.teaching(tid,'plan',{'confirmed':True});w=flow.teaching(tid,'accept_path',{'proposal_record_id':w['proposal']['record_id']})
                w=flow.teaching(tid,'select_node',{'path_record_id':w['head']['path_record_id'],'node_id':'n1'})
            if not w['head']['exercise_record_id']:w=flow.teaching(tid,'exercise',{'confirmed':True,'path_record_id':w['head']['path_record_id'],'node_id':'n1','purpose':'initial'})
            iv=flow.call('GET',f'/api/activities/{iid}/interview/workspace')
            if not iv.get('head'):iv=flow.interview(iid,'start',{'goal':{'target':SAMPLES['inputs']['interview_goal'],'focus':'个人分工与测量口径','material_roles':[{'source_id':mapping['R']['id'],'role':'resume'},{'source_id':mapping['M']['id'],'role':'measurement'}]}})
            flow.index(iid);intent['interview_goal_record_id']=iv['head']['goal_record_id'];c.write(intent_path,intent)
            if not (C01/'final-UI-passed.json').exists():
                prior=C01/'browser-10/proof.json'
                resume=prior if prior.exists() and json.loads(prior.read_text()).get('dropped') else None
                if resume:
                    dropped=json.loads(prior.read_text())['dropped']
                    checks=[flow.call('GET',f"/api/activities/{tid}/teaching/commands/{row['request']['business_key']}") for row in dropped if row['kind']=='answer']
                    assert all(row['status']=='committed' for row in checks)
                    save('root17-original-answer-GET-before-resume',{'receipts':checks,'new_answer_POST':False,'owner_source':'Browser10真实session-storage/storage，不重造owner'})
                proof=batch.start_browser('s04-normal-final',resume=resume);batch.close_browser();save('final-UI-passed',{'proof':proof,'bundle':'bundle7','bundle_identity':intent['final_bundle_sha256'],'inherited_S03_business':True})
            w=flow.call('GET',f'/api/activities/{tid}/teaching/workspace');save('reason-insufficient-persistent',{'activity_id':tid,'workspace':w})
            if not (C01/'reason-sufficient-no-successor-persistent.json').exists():
                # 原长回答被有限单位parser保守判unchecked，不改旧答或冒独立资格。
                save('reason-unchecked-input-retained',{'workspace':w,'failure':'先前夹具给出多组数值，support_checks=unchecked；原revision10保留'})
                regression=C01/'reason-regression-activity.json'
                if regression.exists():rid=json.loads(regression.read_text())['activity_id']
                else:
                    rid=flow.create([mapping['N']]);save('reason-regression-activity',{'activity_id':rid,'purpose':'明确的新派生理由回归，不追造旧答资格'})
                w=flow.teaching(rid,'goal',{'goal':'根据速度.md核对平均速度与分钟换秒。'});flow.index(rid)
                w=flow.teaching(rid,'plan',{'confirmed':True});w=flow.teaching(rid,'accept_path',{'proposal_record_id':w['proposal']['record_id']})
                w=flow.teaching(rid,'select_node',{'path_record_id':w['head']['path_record_id'],'node_id':'n1'})
                w=flow.teaching(rid,'exercise',{'confirmed':True,'path_record_id':w['head']['path_record_id'],'node_id':'n1','purpose':'initial'})
                w=flow.teaching(rid,'answer',{'exercise_record_id':w['head']['exercise_record_id'],'kind':'initial','text':'1米每秒'})
                w=flow.teaching(rid,'evaluate',{'confirmed':True,'exercise_record_id':w['head']['exercise_record_id'],'answer_record_id':w['head']['answer_record_id']})
                h=w['head'];w=flow.teaching(rid,'exercise',{'confirmed':True,'path_record_id':h['path_record_id'],'node_id':h['node_id'],'purpose':'retest','parent_feedback_record_id':h['feedback_record_id']})
                h=w['head'];w=flow.teaching(rid,'answer',{'exercise_record_id':h['exercise_record_id'],'kind':'initial','text':'3米每秒'})
                h=w['head'];w=flow.teaching(rid,'evaluate',{'confirmed':True,'exercise_record_id':h['exercise_record_id'],'answer_record_id':h['answer_record_id']})
                assert w['reason']['body']['observations']['status']=='evidence_sufficient' and '没有满足前置条件' in w['reason']['body']['reason']
                save('reason-sufficient-no-successor-persistent',{'activity_id':rid,'workspace':w,'old_immutable_history_rewritten':False})
            if not (C01/'L10-fixed-host-completed.json').exists():
                artifact=generate(flow,tid);save('preview-parent-and-artifact',{'activity_id':tid,'artifact':artifact})
                run_preview(batch,flow,tid,artifact['artifact_id']);save('L10-fixed-host-completed',{'activity_id':tid,'artifact_id':artifact['artifact_id'],'real_host':True})
            if not (C01/'L08-JCODE-only-after-clarification.json').exists():
                original=flow.call('GET','/api/activities/c430ffb3-c9de-4ff0-aa32-8ac76b95cd86/teaching/workspace')
                aid=flow.create([mapping['J-CODE']]);flow.teaching(aid,'goal',{'goal':'只依据已选J-CODE资料学习Java编程语言，不讨论咖啡产地。'});flow.index(aid)
                narrowed=flow.teaching(aid,'plan',{'confirmed':True},query='Java 编程语言 J-CODE')
                assert narrowed['proposal'] is not None
                save('L08-JCODE-only-after-clarification',{'original_clarification':original,'explicit_new_scope_activity_id':aid,'source_ids':[mapping['J-CODE']['id']],'workspace':narrowed,'original_scope_not_mutated':True})
            if not (C01/'X02-independent-content-cleanup.json').exists():independent_cleanup(flow,mapping)
        finally:flow.close()


if __name__=='__main__':
    try:main()
    except BaseException:
        p=C01/('root17-failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc(),encoding='utf-8');c.failure('S04-root17',p.name,effect='保留真实已提交事实，完整控制器清场；后续仅按原key/head和原截止从未完成处接续');raise
