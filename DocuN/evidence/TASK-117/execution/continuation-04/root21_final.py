"""Last authorized API start: exact whole-step budget counterexample and conditional fixed preview."""
from batch_runtime import *
from frozen_http import FrozenFlow

def main():
    preflight('S05-final-normal')
    with Batch(21,'S05-final-normal-budget-and-preview') as batch:
        rc.start_pg('source');batch.start_api(max_requests=1);flow=FrozenFlow('one-request-boundary')
        try:
            mapping=json.loads((EXEC/'continuation-02/frozen-source-bindings.json').read_text())
            path=C01/'one-request-intent.json'
            if path.exists():aid=json.loads(path.read_text())['activity_id']
            else:
                aid=flow.create([mapping['N']]);flow.teaching(aid,'goal',{'goal':'用当前速度资料核对单位换算。'});flow.index(aid)
                c.write(path,{'sample':c.sample(),'activity_id':aid,'operator_max_requests':1})
            before=flow.call('GET',f'/api/activities/{aid}');status=flow.call('GET',f'/api/activities/{aid}/retrieval/status')
            assert before['activity']['max_requests']==1 and before['activity']['requests_reserved']==0 and status['remaining_requests']==1
            if rc.available_memory_bytes()>=768*1024**2:
                proof=batch.start_browser('budget');batch.close_browser();c.count('http',proof['observed_requests']);c.event('browser_HTTP_reconciled',attempt=batch.browser_attempt,count=proof['observed_requests'])
            else:c.write(C01/'X07-UI-memory-gate.json',{'sample':c.sample(),'available':rc.available_memory_bytes(),'minimum':768*1024**2,'browser_started':False})
            after=flow.call('GET',f'/api/activities/{aid}');assert before['activity']['requests_reserved']==after['activity']['requests_reserved']==0
            assert before['activity']['cost_reserved_microunits']==after['activity']['cost_reserved_microunits']==0
            c.write(C01/'X07-one-request-actual-budget.json',{'sample':c.sample(),'before':before,'status':status,'after':after,'no_partial_admission':True})
            # Actual deletion closure is left open by the user's explicit instruction. Read-only overlay preflight only.
            from app.data_exit.control import ControlHub
            from app.data_exit.repository import DataRepository
            hub=ControlHub(EXEC/'synthetic/source-control');state=hub.state();job=state['jobs']['55957ddd-20dc-498b-972f-66f3805679cb']
            plan=json.loads(hub.read_artifact('plans',job['scope']['plan_id'],job['scope']['plan_sha256']))
            latest=DataRepository(rc.dsn('source')).latest();assert latest['status']=='known'
            covered={(r['entity_kind'],r['entity_id'],r['effective_revision']) for r in plan['overlay']}
            missing=[r for r in latest['tombstones'] if (r['entity_kind'],r['entity_id'],r['effective_revision']) not in covered]
            c.write(C01/'R02-overlay-dependency-preflight.json',{'sample':c.sample(),'plan_id':job['scope']['plan_id'],'plan_sha256':job['scope']['plan_sha256'],
                'old_sealed_target':job['target_id'],'current_tombstones':latest['tombstones'],'original_overlay':plan['overlay'],'current_missing':missing,
                'new_delete_would_require_new_prepare_if_tuple_absent':True,'independent_delete_contract':'user confirmed preserve gap for controller','activation_attempted':False,'success02_created':False,
                'selector':state['selection'],'fence':state['fence']})
            old_aid='0305ee4c-be33-489e-bab6-8f2f55e59573';artifact='b263cb39-b6e8-4edf-8573-9c84ee1c5326'
            qualification=flow.call('GET',f'/api/activities/{old_aid}/html/artifacts/{artifact}')
            available=rc.available_memory_bytes()
            if available>=1024*1024**2:
                from preview_case import run_preview
                run_preview(batch,flow,old_aid,artifact)
                c.write(C01/'L10-fixed-host-completed.json',{'sample':c.sample(),'activity_id':old_aid,'artifact_id':artifact,'real_host':True})
            else:c.write(C01/'L10-current-memory-gate.json',{'sample':c.sample(),'available':available,'minimum':1024*1024**2,'preview_create_start_attempted':False,'original_artifact_sha256':qualification['artifact_sha256'],'browser_stopped_before_sample':batch.browser is None})
        finally:flow.close()

if __name__=='__main__':main()
