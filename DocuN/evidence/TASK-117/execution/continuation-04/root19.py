"""S05 normal recovery and measured diagnostics, one original bounded root."""
from batch_runtime import *
from frozen_http import FrozenFlow
import asyncio,cProfile,pstats,io

def main():
    preflight('S05-normal',preview=True)
    with Batch(19,'S05-normal-and-targeted-diagnostics') as batch:
        rc.start_pg('source')
        batch.start_api()
        flow=FrozenFlow('normal-diagnostics')
        try:
            pid='5c508dc7-2ac6-44fb-922b-8e8de4b9f006'
            aid='0305ee4c-be33-489e-bab6-8f2f55e59573'
            old=EXEC/'synthetic/source-data/preview-control'/pid
            status=flow.call('GET',f'/api/activities/{aid}/html/previews/{pid}')
            from app.data_exit.control import ControlHub
            hub=ControlHub(EXEC/'synthetic/source-control')
            state=hub.state();proof=json.loads((old/'recovery-proof.json').read_text())
            outstanding=[v for v in state['owned'].values() if v['state']!='ended']
            c.write(C01/'old-preview-recovery.json',{'sample':c.sample(),'status':status,'proof':proof,
                'proof_sha256':c.sha((old/'recovery-proof.json').read_bytes()),'old_first_attempt':json.loads((old/'supervisor-result.json').read_text()),
                'owned':list(state['owned'].values())[-8:],'outstanding':outstanding,'old_failure_retained':True})
            assert status['state']=='failed_unstarted' and proof['tree_confirmation']=='never_started' and not outstanding
            artifact=flow.call('GET',f'/api/activities/{aid}/html/artifacts/b263cb39-b6e8-4edf-8573-9c84ee1c5326')
            c.write(C01/'original-artifact-qualification.json',artifact)
            # Read-only normal gate and ledger qualification; no reserve, preview or Docker create.
            from profiles_batch import runtime_config
            runtime=runtime_config(batch.run)
            timings=[]
            profiler=cProfile.Profile();profiler.enable()
            for label,func in [('context',runtime.context),('gate_check',lambda:check_gate(runtime)),('ledger_budget',lambda:read_budget(runtime.app.state.activities_ledger,aid))]:
                t=time.monotonic_ns();value=func();timings.append({'stage':label,'seconds':(time.monotonic_ns()-t)/1e9})
            profiler.disable();out=io.StringIO();pstats.Stats(profiler,stream=out).sort_stats('cumulative').print_stats(28)
            (C01/'preview-gate-profile.txt').write_text(out.getvalue(),encoding='utf-8')
            c.write(C01/'preview-readonly-stages.json',{'sample':c.sample(),'stages':timings,'new_preview_reserve_create_start':0,'outstanding_owned':outstanding})
            if '--preview' in sys.argv:
                from preview_case import run_preview
                assert artifact['artifact_sha256']=='0eb0af141ccb6a14c6037df8f6dad25164a33c3caa99551b41c456a7b60a0b70'
                c.write(C01/'preview-diagnosis-closed.json',{'sample':c.sample(),'measured_hotspot':'assert_writable full replay on every permit check',
                    'before':'preview-gate-profile.txt (first attempt retained below)','after_seconds':timings,
                    'change':'reuse verified complete current bytes identity cache and retain tail refusal; no deadline/lock/owned/security change',
                    'distinguishing_tests':'snapshot-targeted-tests-02.log','old_diagnostic':'preview-read-cost-initial.json'})
                run_preview(batch,flow,aid,artifact['artifact_id'])
                c.write(C01/'L10-fixed-host-completed.json',{'sample':c.sample(),'activity_id':aid,'artifact_id':artifact['artifact_id'],'real_host':True})
        finally:flow.client.close()

def check_gate(runtime):
    with runtime.gate.acquire(outgoing=True) as permit:
        permit.check(outgoing=True)
    return True

def read_budget(ledger,aid):
    from app.runtime import psycopg_compatible_loop_factory
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(ledger.html_preview_budget(aid))

if __name__=='__main__':main()
