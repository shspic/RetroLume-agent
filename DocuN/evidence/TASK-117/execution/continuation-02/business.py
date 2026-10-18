"""根15最终bundle新场景，两域回答及UNKNOWN之后同normal库真实重开。"""
from batch_runtime import *
from frozen_http import FrozenFlow,SAMPLES
from uuid import uuid4
import traceback
import psycopg
from psycopg.rows import dict_row

def budgets(flow,aids):
    return {a:flow.call('GET',f'/api/activities/{a}') for a in aids}

def generate(flow,aid):
    w=flow.call('GET',f'/api/activities/{aid}/teaching/workspace');h=w['head'];rid=h['feedback_record_id']
    record=flow.call('GET',f'/api/activities/{aid}/teaching/records/{rid}')
    caps=flow.call('GET',f'/api/activities/{aid}/html/capabilities');assert caps['available'],caps
    result=flow.call('POST',f'/api/activities/{aid}/html/commands',{'business_key':str(uuid4()),'parent':{'kind':'teaching','record_id':rid,'body_sha256':record['body_sha256'],'point_id':None},'focus':'分钟换秒与平均速度d/t','expected_config_sha256':caps['config_sha256'],'confirmed':True},native=1)
    assert result['artifact_id'];return result

def main():
    preflight('S03-root15-final-bundle-business')
    with Batch(15,'S03_new_two_domains_and_normal_reopen') as batch:
        rc.start_pg('source');batch.start_api(launcher=True)
        first=FrozenFlow('root15-before')
        try:
            binding=C01/'minimal-memory-interview-start.json'
            if not binding.exists():
                mapping=json.loads((C01/'frozen-source-bindings.json').read_text());memory=first.call('GET','/api/memories/'+json.loads((C01/'frozen-memory-binding.json').read_text())['memory_id'])
                aid=first.create([mapping['R'],mapping['M']],memory)
                c.write(C01/'minimal-memory-start-intent.json',{'activity_id':aid,'intent':'五表SELECT修补的独立零费真实回归，不替代I01'})
                w=first.interview(aid,'start',{'goal':{'target':SAMPLES['inputs']['interview_goal'],'material_roles':[{'source_id':mapping['R']['id'],'role':'resume'},{'source_id':mapping['M']['id'],'role':'measurement'}]}})
                assert w['head']['phase']=='ready';c.write(binding,{'activity_id':aid,'workspace':w,'Native':0,'ordinary_API_v2_start':True})
            prior=C01/'browser-5/proof.json'
            recovering=prior.exists() and json.loads(prior.read_text()).get('interview_activity_id')
            if recovering and not (C01/'original-ask-explicit-recovery.json').exists():
                saved=json.loads((prior.parent/'storage.json').read_text());drafts=[]
                for origin in saved['origins']:
                    for db in origin.get('indexedDB',[]):
                        if 'interview-drafts' in db['name']:
                            for store in db['stores']:drafts.extend(r['value'] for r in store.get('records',[]))
                draft=next(d for d in drafts if d['command']['action']=='ask' and d['activity_id']==recovering)
                from app.interview.contracts import parse_command
                parsed=parse_command(draft['command']);assert parsed.request_hash(recovering)==draft['hash']
                key=draft['key'];original=first.call('GET',f'/api/activities/{recovering}/interview/commands/{key}',expected=404)
                c.write(C01/'original-ask-recovery-before.json',{'activity_id':recovering,'business_key':key,'request_sha256':draft['hash'],'GET_original':original,'reason':'原500发生在freeze前，未被claim；长目标词项有界修补已完成','layer':'真实HTTP显式同键重交；不恢复或冒用缺失旧tab owner'})
                result=first.call('POST',f'/api/activities/{recovering}/interview/commands',draft['command'],native=1)
                assert result['status']=='committed';c.write(C01/'original-ask-explicit-recovery.json',result)
            proof=batch.start_browser('s03-recover-before' if recovering else 's03-before-restart',resume=prior if recovering else None);batch.close_browser()
            aids=[proof['teaching_activity_id'],proof['interview_activity_id']]
            c.write(C01/'new-business-identities.json',{'teaching_activity_id':aids[0],'interview_activity_id':aids[1],'old_expired_teaching':'b7f32142-b5b3-4a5c-b561-f927bcbe1b6d','old_deadline_unchanged':True,'old_qualification_not_inherited':True})
            heads={'learning':first.call('GET',f'/api/activities/{aids[0]}/teaching/workspace'),'interview':first.call('GET',f'/api/activities/{aids[1]}/interview/workspace')}
            h=heads['learning']['head'];unknown_key=str(uuid4())
            unknown=first.call('POST',f'/api/activities/{aids[0]}/retrieval/commands',{'business_key':unknown_key,'action':'query','expected_scope_revision':1,'expected_domain_revision':h['revision'],'query':'S02合成超时','confirmed':True},native=1)
            assert unknown['terminal_disposition']=='unknown'
            baseline={'sample':c.sample(),'aids':aids,'heads':heads,'unknown_key':unknown_key,'unknown':unknown,'budgets':budgets(first,aids)}
            c.write(C01/'X09-before-normal-reopen.json',baseline)
        finally:first.close()
        batch.close_api()
        stopped=rc.metadata(next(r['cid'] for r in c.state()['resources'] if r.get('id')=='pg-source'));assert stopped['running']
        # 正常启动器复用已有PG，不拥有其停机权；该PG继续由同一个根控制器持有。
        # 本项证明正常应用停止重开同库，不声称PG进程曾重启。
        c.write(C01/'X09-source-between-reopen.json',stopped)
        second=batch.fresh_api_handle();second.start_api(launcher=True)
        flow=FrozenFlow('root15-after')
        try:
            before=json.loads((C01/'X09-before-normal-reopen.json').read_text());aids=before['aids']
            after={'learning':flow.call('GET',f'/api/activities/{aids[0]}/teaching/workspace'),'interview':flow.call('GET',f'/api/activities/{aids[1]}/interview/workspace')}
            for kind in ('learning','interview'):assert before['heads'][kind]['head']==after[kind]['head']
            unknown=flow.call('GET',f'/api/activities/{aids[0]}/retrieval/commands/{before["unknown_key"]}')
            assert unknown['terminal_disposition']=='unknown' and unknown['business_key']==before['unknown_key']
            c.write(C01/'X09-GET-only-after-reopen.json',{'heads':after,'unknown':unknown,'budgets':budgets(flow,aids),'POSTs_before_explicit_continue':0,'same_source_cid':stopped['cid'],'source_profile':'data_exit.v1.r02'})
            proof2=second.start_browser('s03-resume',resume=C01/f'browser-{batch.browser_attempt}/proof.json');second.close_browser()
            final={'teaching':flow.call('GET',f'/api/activities/{aids[0]}/teaching/workspace'),'interview':flow.call('GET',f'/api/activities/{aids[1]}/interview/workspace')}
            assert final['teaching']['head']['phase']=='feedback_ready' and final['interview']['head']['phase']=='ended'
            c.write(C01/'L01-L05-I01-X09-final.json',{'sample':c.sample(),'source_cid':stopped['cid'],'aids':aids,'final':final,'browser_before':batch.browser_attempt,'browser_after':second.browser_attempt,'Q':'NOT_ENABLED'})
            artifact=generate(flow,aids[0]);c.write(C01/'L10-current-artifact.json',{'activity_id':aids[0],'artifact':artifact})
        finally:flow.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        p=C01/('root15-failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc(),encoding='utf-8');c.failure('S03-root15',p.name,effect='保留已提交步骤，清场后仅从实际head接续，不整体重跑');raise
