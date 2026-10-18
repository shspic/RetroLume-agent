"""从root09真实持久断点接续；不重放已提交教学链。"""
from batch_runtime import *
from frozen_http import FrozenFlow
from root09_batch import baseline
from preview_case import run_preview
import traceback

def main():
    preflight('root10',preview=True)
    with Batch(10,'ROOT10-current-head-resume-and-interview') as batch:
        c.write(C01/('root10-as-run-'+batch.id+'.json'),{'sample':c.sample(),'node_script_sha256':c.sha((ROOT/'frontend/tests/step018-flow.mjs').read_bytes()),'bundle':json.loads((C01/'bundle-4.json').read_text()),'files':{p:c.sha((ROOT/p).read_bytes()) for p in json.loads((C01/'changes.json').read_text()) if (ROOT/p).is_file()}})
        rc.start_pg('source');batch.start_api()
        flow=FrozenFlow('root10')
        try:
            previous=json.loads((C01/'browser-3/proof.json').read_text());aid=previous['teaching_activity_id']
            current=flow.call('GET',f'/api/activities/{aid}')
            workspace=flow.call('GET',f'/api/activities/{aid}/teaching/workspace')
            last=previous['receipts'][-1]['value'];original=flow.call('GET',f"/api/activities/{aid}/teaching/commands/{last['business_key']}")
            c.write(C01/'root10-original-committed-readback.json',{'activity':current,'workspace':workspace,'last_command':original,'old_browser_failure_unchanged':True})
            assert workspace['head']['revision']==last['applied_revision'] and workspace['head']['phase']=='answer_saved'
            result=batch.start_browser('continue-root09',resume=C01/'browser-3/proof.json')
            c.write(C01/'root10-browser-receipt.json',result)
            proof_path=C01/f"browser-{result['attempt']}/proof.json"
            c.write(C01/'pending-normal-reopen-browser.json',{'proof_path':str(proof_path),'teaching_activity_id':aid,'interview_activity_id':result['interview_activity_id']})
            batch.close_browser()
            try:run_preview(batch,flow,aid,result['html_artifact_id'])
            except Exception as exc:
                c.failure('S02-L10',type(exc).__name__+':'+str(exc)[:250],effect='固定preview/API原闭包收尾；失败不覆盖，独立checkpoint继续')
                (C01/'L10-failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
            # Same L01 activity, legitimate local answer revision pending a new post-reopen evaluation.
            w=flow.call('GET',f'/api/activities/{aid}/teaching/workspace');h=w['head']
            revised=flow.teaching(aid,'answer',{'exercise_record_id':h['exercise_record_id'],'kind':'revision','supersedes_answer_record_id':h['answer_record_id'],'text':'4米每秒；240米用1分钟，先换成60秒，240÷60=4。'})
            c.write(C01/'L01-answer-before-normal-reopen.json',{'activity_id':aid,'workspace':revised})
            baseline('root10-before-normal-reopen-pg.json')
        finally:flow.close()
    print('ROOT10 exact continuation complete; no replay of root09 successful teaching commands')

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        c.failure('S02-ROOT10',type(exc).__name__+':'+str(exc)[:300],effect='同根原截止清场；不换key重发已提交动作')
        (C01/('root10-error-'+str(time.time_ns())+'.txt')).write_text(traceback.format_exc(),encoding='utf-8');raise
