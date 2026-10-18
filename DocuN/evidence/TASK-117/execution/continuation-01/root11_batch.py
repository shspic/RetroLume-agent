"""必要HTTP矩阵、正常启动器同库重开与最终恢复，一个原截止串行目标。"""
from batch_runtime import *
from frozen_http import FrozenFlow,SAMPLES
from http_remaining import *
from root09_batch import baseline
from final_restore import final_restore
from preview_case import run_preview

TEACHING='b7f32142-b5b3-4a5c-b561-f927bcbe1b6d'

def main(number=11):
    prefix=f'root{number}'
    preflight(prefix,preview=True)
    with Batch(number,f'ROOT{number}-uncommitted-HTTP-normal-reopen-and-R02') as batch:
        c.write(C01/(prefix+'-as-run-'+batch.id+'.json'),{'sample':c.sample(),'node_script_sha256':c.sha((ROOT/'frontend/tests/step018-flow.mjs').read_bytes()),'bundle':json.loads((C01/'bundle-4.json').read_text()),'files':{p:c.sha((ROOT/p).read_bytes()) for p in json.loads((C01/'changes.json').read_text()) if (ROOT/p).is_file()},'helpers':{p.name:c.sha(p.read_bytes()) for p in C01.glob('*.py')}})
        rc.start_pg('source')
        if number==12:
            from pg_observer import observe_pg
            observe_pg(batch.run,prefix)
        batch.start_api(launcher=number!=12)
        flow=FrozenFlow(prefix+'-before')
        mapping=json.loads((C01/'frozen-source-bindings.json').read_text());memory=json.loads((C01/'frozen-memory-binding.json').read_text())
        browser_result=None
        try:
            try:
                rc.memory_gate('root11-required-UI-after-only-PG-API',stage='browser')
                browser_result=batch.start_browser('continue-root09',resume=C01/'browser-3/proof.json')
            except Exception as exc:
                c.failure('S02-root11-UI',type(exc).__name__+':'+str(exc)[:240],effect='不强行勾选、不重放原教学；HTTP独立目标继续，真实UI不足保留')
            if browser_result:
                interview_id=browser_result['interview_activity_id'];artifact_id=browser_result['html_artifact_id'];batch.close_browser()
                c.write(C01/'root11-browser-receipt.json',browser_result)
            else:
                prior_browser={}
                if batch.browser is not None:
                    prior_browser=json.loads((C01/f'browser-{batch.browser_attempt}/proof.json').read_text())
                    batch.close_browser()
                    if any(r.get('response',{}).get('terminal_disposition')=='unknown' for r in prior_browser.get('retrieval_receipts',[])):
                        raise RuntimeError('post-fix_embedding_unknown_stop_affected_no_new_key_retry')
                current=flow.call('GET',f'/api/activities/{TEACHING}/teaching/workspace')
                feedback=evaluate(flow,TEACHING) if current['head']['phase']=='answer_saved' else current
                assert feedback['head']['phase']=='feedback_ready'
                c.write(C01/'L01-final-feedback-and-progress.json',feedback)
                interview_id=interview_before(flow,mapping,memory,prior_browser.get('interview_activity_id'))
                artifact_id=prior_browser.get('html_artifact_id')
                def generate():
                    rid=feedback['head']['feedback_record_id'];record=flow.call('GET',f'/api/activities/{TEACHING}/teaching/records/{rid}')
                    caps=flow.call('GET',f'/api/activities/{TEACHING}/html/capabilities');assert caps['available'],caps
                    result=flow.call('POST',f'/api/activities/{TEACHING}/html/commands',{'business_key':str(uuid4()),'parent':{'kind':'teaching','record_id':rid,'body_sha256':record['body_sha256'],'point_id':None},'focus':'分钟换秒与平均速度d/t','expected_config_sha256':caps['config_sha256'],'confirmed':True},native=1)
                    assert result['artifact_id'];return result
                if artifact_id is None:
                    artifact=case('L10-API-artifact',generate)
                    if artifact:artifact_id=artifact['artifact_id']
            if artifact_id:case('L10-fixed-host',lambda:run_preview(batch,flow,TEACHING,artifact_id))
            w=flow.call('GET',f'/api/activities/{TEACHING}/teaching/workspace');h=w['head']
            flow.teaching(TEACHING,'answer',{'exercise_record_id':h['exercise_record_id'],'kind':'revision','supersedes_answer_record_id':h['answer_record_id'],'text':'4米每秒；240米先除以60秒，明确分钟已换成秒。'})
            baseline(prefix+'-before-normal-reopen-pg.json')
            c.write(C01/'root11-pending-identities.json',{'teaching_activity_id':TEACHING,'interview_activity_id':interview_id,'memory_teaching_id':json.loads((C01/'memory-teaching-before-reopen.json').read_text())['activity_id']})
        finally:flow.close()
        batch.close_api() # Original stdin, normal lifespan and owned launch handle.
        stage=batch.fresh_api_handle();stage.start_api(launcher=True)
        flow=FrozenFlow(prefix+'-after')
        try:
            baseline(prefix+'-after-reopen-before-POST-pg.json')
            before=json.loads((C01/(prefix+'-before-normal-reopen-pg.json')).read_text());after=json.loads((C01/(prefix+'-after-reopen-before-POST-pg.json')).read_text())
            assert before['unknown']==after['unknown']
            keys=('id','requests_reserved','cost_reserved_microunits','tools_reserved')
            assert [{k:r[k] for k in keys} for r in before['activities']]==[{k:r[k] for k in keys} for r in after['activities']]
            case('X09-L01-new-feedback',lambda:evaluate(flow,TEACHING))
            memory_aid=json.loads((C01/'memory-teaching-before-reopen.json').read_text())['activity_id']
            case('X09-selected-memory-teaching',lambda:evaluate(flow,memory_aid))
            case('X09-I01-new-feedback-finish',lambda:interview_after(flow,interview_id))
            case('X03-X07-real-budget-and-concurrent-key',lambda:budget_and_keys(flow,mapping))
            answers=SAMPLES['inputs']['numeric_positive_answers']+SAMPLES['inputs']['numeric_negative_answers']+[SAMPLES['inputs']['numeric_ambiguous_answer']]
            case('L02-L04-numeric-frozen-variants',lambda:variants(flow,mapping,'N',SAMPLES['inputs']['numeric_goal'],answers))
            case('L06-concept-variants',lambda:variants(flow,mapping,'C',SAMPLES['inputs']['concept_goal'],[SAMPLES['inputs'][k] for k in ('concept_positive','concept_negative','concept_partial')]))
            case('L07-program-plain-reasoning',lambda:variants(flow,mapping,'P','阅读range(1,4)的循环并逐步推理，不执行程序。',[SAMPLES['inputs'][k] for k in ('program_positive','program_negative')]))
            case('L08-ambiguity',lambda:neutral(flow,mapping,['J-CODE','J-COFFEE'],SAMPLES['inputs']['ambiguous_goal'],'clarification'))
            case('L09-no-evidence',lambda:neutral(flow,mapping,['N'],SAMPLES['inputs']['no_evidence_query'],'no_evidence'))
            case('L09-conflict',lambda:neutral(flow,mapping,['N','N-CONFLICT'],SAMPLES['inputs']['conflict_query'],'conflict'))
            case('X02-late-learning-and-interview-memory',lambda:late_memory(flow,mapping,memory,memory_aid))
            case('X10-source-delete-no-007-cache-bypass',lambda:delete_auxiliary(flow))
        finally:flow.close()
        stage.close_api()
        # No API/browser survives into the restore stage or second PG window.
        case('P03-final-R02-and-failed-hash-target',lambda:final_restore(batch.run))
    print('ROOT11 serial targeted checks finished; all owned resources cleaned')

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        c.failure('S02-ROOT11',type(exc).__name__+':'+str(exc)[:300],effect='原控制器清场，已COMMIT与失败保存，不整体重跑')
        (C01/('root11-error-'+str(time.time_ns())+'.txt')).write_text(traceback.format_exc(),encoding='utf-8');raise
