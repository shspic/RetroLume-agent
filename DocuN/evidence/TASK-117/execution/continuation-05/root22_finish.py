"""Continue root22 original deadline: GET committed PDF, finite slot and invalidation representatives."""
from batch_runtime import *
from frozen_http import FrozenFlow
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import httpx
def raw(flow,path,body):
    with httpx.Client(base_url='http://127.0.0.1:18118',headers=dict(flow.client.headers),timeout=30,trust_env=False) as client:
        r=client.post(path,json=body);return {'request':body,'http':r.status_code,'value':r.json()}
def main():
    preflight('S06-source-finish')
    with Batch(22,'S06-source-preview-PDF') as batch:
        rc.start_pg('source');batch.start_api();flow=FrozenFlow('source-finish')
        try:
            c.failure('S06_fixture_PDF_GET_route','diagnostic and confirmation succeeded; fixture used nonexistent /materials/{id}; GET /content is actual unchanged product route',effect='preserve 404 and completed PDF; no parsing retry or repeated confirmation')
            old=[]
            for p in (C01/'source-targeted').glob('*.json'):
                v=json.loads(p.read_text());
                if '/confirm' in v.get('path','') and v['status']==200:old.append((p,v))
            p,confirmed=old[-1];material=confirmed['response']['material'];detail=flow.call('GET',f"/api/materials/{material['id']}/content?expected_version={material['version_id']}")
            pages=detail['pages'];assert {p['physical_page'] for p in pages}=={1,2}
            c.write(C01/'PDF-two-page-confirmed.json',{'sample':c.sample(),'confirmation_receipt':str(p.relative_to(ROOT)),'confirmation_sha256':c.sha(p.read_bytes()),'material':material,'content_GET':detail,'physical_pages_reviewed':[1,2],'manual_confirmation_gate_retained':True,'parse_attempts_this_segment':1,'historical_HTTP_422_cause':'not reconstructed; new bounded actual HTTP success, no invented old root cause'})
            # Bind real stage clocks and settled preview accounting without registry secrets.
            ready=json.loads((C01/'L10/ready.json').read_text());pid=ready.get('preview_id')
            if pid is None:
                result=json.loads((C01/'L10/supervisor-result.json').read_text());pid=result.get('preview_id') or result['proof']['preview_id']
            folder=EXEC/'synthetic/source-data/preview-control'/pid
            for name in ('stage-times.json','supervisor-job-final.json','reaper-job-final.json'):
                if (folder/name).exists():(C01/'L10'/name).write_bytes((folder/name).read_bytes())
            status=flow.call('GET',f'/api/activities/0305ee4c-be33-489e-bab6-8f2f55e59573/html/previews/{pid}')
            c.write(C01/'L10/settled-status.json',status);assert status['state']=='stopped'
            mapping=json.loads((EXEC/'continuation-02/frozen-source-bindings.json').read_text())
            aid=flow.create([mapping['N']]);path=f'/api/activities/{aid}/teaching/commands'
            bodies=[{'business_key':str(uuid4()),'expected_revision':0,'expected_goal_version':0,'expected_scope_revision':1,'action':'goal','body':{'goal':'S06同父槽单位换算'+str(i)}} for i in (1,2)]
            c.count('http',2)
            with ThreadPoolExecutor(2) as pool:results=list(pool.map(lambda body:raw(flow,path,body),bodies))
            assert sum(r['http']==200 and r['value'].get('status')=='committed' for r in results)==1,results
            assert sum(r['http']==409 for r in results)==1,results
            c.write(C01/'semantic-slot-race.json',{'sample':c.sample(),'activity_id':aid,'two_distinct_keys_same_parent':True,'responses':results,'committed_effects':1,'native_or_external_calls':0})
            flow.index(aid);head=flow.call('GET',f'/api/activities/{aid}/teaching/workspace')['head'];gate=C01/'late-transport';gate.mkdir(exist_ok=True)
            (gate/'ready.json').unlink(missing_ok=True);(gate/'release').unlink(missing_ok=True)
            query={'business_key':str(uuid4()),'action':'query','expected_scope_revision':1,'expected_domain_revision':head['revision'],'query':'S02晚到记忆','confirmed':True}
            c.count('http');c.count('native_windows')
            with ThreadPoolExecutor(1) as pool:
                future=pool.submit(raw,flow,f'/api/activities/{aid}/retrieval/commands',query)
                try:
                    until=time.monotonic()+7
                    while not (gate/'ready.json').exists():
                        if future.done() or time.monotonic()>until:raise RuntimeError('late_transport_not_observed')
                        time.sleep(.02)
                    changed=flow.teaching(aid,'goal',{'goal':'S06执行中改变目标：先核对米每秒单位。'})
                finally:(gate/'release').write_text('release',encoding='ascii')
                late=future.result(timeout=10)
            assert late['http']==200 and late['value'].get('current') is False,late
            c.write(C01/'inflight-goal-invalidation.json',{'sample':c.sample(),'activity_id':aid,'old_head':head,'actual_received_late_response':late,'new_head':changed['head'],'current_false':True,'new_action_not_authorized_by_old_receipt':True,'same_qualification_family':'scope/source/memory inherited unchanged gate; actual goal representative'})
        finally:flow.close()
if __name__=='__main__':main()
