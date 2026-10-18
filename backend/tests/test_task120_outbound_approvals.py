import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from pydantic import ValidationError,SecretStr
from app.capabilities.q_protocol import load_json,canonical,digest,DecisionBody,utcnow
from app.capabilities.q_context import validate_provenance
from app.capabilities.contracts import AdmissionDenied,ModelCallRequest,ModelServiceConfig,CallContext
from app.data_exit.contracts import DataError
from app.data_exit.q_store import QAuthority
from app.operator.q_request import principal_id
from app.worker.one_call import OneCallInput
from tests.fixtures.task120.offline import store,prepared,AID,TEXT

if os.name=='nt':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class ApprovalTests(unittest.TestCase):
    def test_json_is_unambiguous_and_decision_has_no_self_reference(self):
        for value in ('{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}'):
            with self.assertRaises(ValueError):load_json(value)
        self.assertNotIn('approval_id',DecisionBody.model_fields)
        with self.assertRaises(ValueError):canonical(float('nan'))

    def test_exact_decision_seq_idempotence_revoke_and_renewal(self):
        authority=store();row=prepared(authority);pid=row['prepared_id'];principal=principal_id()
        first=authority.approve(pid,principal,current=True)
        self.assertEqual(first['approval_id'],digest(first['body']))
        size=authority.hub.path.stat().st_size
        self.assertEqual(authority.approve(pid,principal,current=True),first)
        self.assertEqual(authority.hub.path.stat().st_size,size)
        authority.revoke(pid,principal)
        with self.assertRaises(DataError):authority.check_reference({'root_sha256':authority.manifest.sha256,'prepared_id':pid,'prepared_sha256':row['prepared_sha256'],'approval_id':first['approval_id'],'approval_event_seq':first['body']['event_seq']})
        renewed=authority.approve(pid,principal,current=True)
        self.assertNotEqual(first['approval_id'],renewed['approval_id'])
        self.assertGreater(renewed['body']['event_seq'],first['body']['event_seq'])
        self.assertEqual(authority.hub.state()['q']['approval_events'],2)

    def test_expiration_currentness_and_claim_never_enable_resend(self):
        authority=store();row=prepared(authority);pid=row['prepared_id'];principal=principal_id()
        earlier=utcnow()-timedelta(minutes=16)
        with patch('app.data_exit.q_store.utcnow',return_value=earlier):authority.approve(pid,principal,current=True)
        self.assertEqual(authority.projection(authority.request(pid))['state'],'expired')
        approval=authority.approve(pid,principal,current=True)
        self.assertGreater(approval['body']['event_seq'],1)
        ref=authority.reference(authority.request(pid))
        context=CallContext(activity_id=AID,operation_id='offline.request',executor_id='fixture',execution_generation=1,scope_revision=1)
        authority.check_reference(ref,context=context)
        with self.assertRaises(DataError):authority.check_reference(ref,context=context)
        with self.assertRaises(DataError):authority.approve(pid,principal,current=True)
        self.assertEqual(authority.projection(authority.request(pid))['state'],'consumed')

    def test_same_key_different_bytes_and_first_slot_are_closed(self):
        authority=store();row=prepared(authority)
        with self.assertRaises(DataError):prepared(authority,key=row['prepared']['business_key'],request={'goal':TEXT+' '})
        with self.assertRaises(DataError):prepared(authority,operation_id='other.first')

    def test_missing_artifact_replaced_hub_and_readonly_root_fail_closed(self):
        authority=store();row=prepared(authority)
        artifact=authority.hub.artifact_path('q-prepared',row['prepared_id'])
        backup=artifact.with_suffix('.held');artifact.rename(backup)
        with self.assertRaises((DataError,OSError)):authority.artifact(row)
        backup.rename(artifact)
        old=authority.binding.hub_control_id
        authority.hub.control_id='00000000-0000-4000-8000-000000000000'
        with self.assertRaises(DataError):QAuthority(authority.hub)
        authority.hub.control_id=old
        authority.hub.commit('maintenance.fence',{'origin':{},'state':'frozen'})
        with self.assertRaises(DataError):authority.check_root()

    def test_finite_literals_have_distinct_raw_and_json_hashes_and_purposes(self):
        authority=store();s=authority.manifest.sources[0]
        state={'activity':{'id':AID},'sources':[dict(source_id=s['source_id'],version_id=s['source_version_id'])],'commands':[]}
        request={'goal':TEXT};payload={'messages':[{'role':'user','content':canonical(request)}]}
        proof=validate_provenance(authority,request,payload,state,[],[],'first')
        self.assertTrue(any(x['kind']=='literal' for x in proof))
        self.assertNotEqual(authority.manifest.fixed_inputs[0].raw_text_sha256,authority.manifest.fixed_inputs[0].json_string_sha256)
        for text in (TEXT+' ',TEXT+'未批准秘密','未知标题'):
            with self.assertRaises(AdmissionDenied):validate_provenance(authority,{'goal':text},payload,state,[],[],'first')
        with self.assertRaises(AdmissionDenied):validate_provenance(authority,{'question':TEXT},payload,state,[],[],'first')
        with self.assertRaises(AdmissionDenied):validate_provenance(authority,{'record_id':'ffffffff-ffff-4fff-8fff-ffffffffffff'},payload,state,[],[],'first')

    def test_testonly_never_dispatches_to_external_transport(self):
        authority=store();row=prepared(authority);authority.approve(row['prepared_id'],principal_id(),current=True)
        with self.assertRaises(DataError):authority.check_reference(authority.reference(authority.request(row['prepared_id'])),external=True)

    def test_wire3_original_bytes_have_no_new_default_fields(self):
        service=ModelServiceConfig(provider='deepseek_chat_completions',base_url='https://api.deepseek.com',model='deepseek-chat',api_key=SecretStr('synthetic'),max_request_bytes=65536,max_response_bytes=65536)
        wire=OneCallInput('legacy',ModelCallRequest(messages=[{'role':'user','content':'old'}],max_output_tokens=1),service).to_wire()
        self.assertNotIn('protocol',wire)
        self.assertNotIn('outbound_authorization',wire['service'])
        self.assertNotIn('returned_models',wire['service'])
        self.assertEqual(OneCallInput.from_wire(wire).to_wire(),wire)


class LockTests(unittest.IsolatedAsyncioTestCase):
    async def test_shared_upgrade_is_rejected_and_exclusive_wait_is_bounded(self):
        authority=store()
        async with authority.async_policy(shared=True):
            with self.assertRaises(DataError):
                async with authority.async_policy():pass
        async with authority.async_policy():
            async with authority.async_policy(shared=True):pass


class RuntimeControlTests(unittest.TestCase):
    def test_deadline_and_two_low_samples_close_in_reverse_order(self):
        import time
        from tests.fixtures.task120.lifecycle import BoundedResources
        calls=[];samples=iter([300,200,200])
        with BoundedResources(deadline=time.monotonic()+3) as run:
            run.register('pg',lambda:calls.append('pg') or True,priority=0)
            run.register('api',lambda:calls.append('api') or True,priority=30)
            run.register('browser',lambda:calls.append('browser') or True,priority=60)
            run.monitor_memory(lambda:next(samples)*1024**2,every=.01)
            run.wake();self.assertTrue(run.closed.wait(2))
            self.assertEqual(run.report['reason'],'memory_pressure')
            self.assertEqual(calls,['browser','api','pg'])
            with self.assertRaises(RuntimeError):run.check()

    def test_partial_start_failure_still_runs_all_cleanup(self):
        import time
        from tests.fixtures.task120.lifecycle import BoundedResources
        calls=[]
        def fail():calls.append('api');raise OSError('synthetic cleanup failure')
        with BoundedResources(deadline=time.monotonic()+3) as run:
            run.register('pg',lambda:calls.append('pg') or True)
            run.register('api-intent',fail,priority=30)
        self.assertEqual(calls,['api','pg'])
        self.assertFalse(run.report['all_confirmed'])

    def test_real_own_controller_job_is_terminated_by_deadline(self):
        import sys,time
        from uuid import uuid4
        from tests.fixtures.task120.resources import root_job,event,ROOT
        from tests.fixtures.task120.lifecycle import BoundedResources
        identity=str(uuid4())
        with root_job(identity) as job:
            job.spawn_suspended([sys.executable,'-c','import time; time.sleep(20)'],cwd=str(ROOT/'backend'))
            event('offline_controller_job',job=job.name,pid=job.pid,birth_100ns=job.process_creation_time_100ns())
            def cleanup():
                job.terminate()
                return job.wait_empty_until(time.monotonic_ns()+2_000_000_000)
            with BoundedResources(deadline=time.monotonic()+.2) as run:
                run.register('controller-child',cleanup)
                job.resume();self.assertTrue(run.closed.wait(3))
                self.assertTrue(run.report['all_confirmed'])
                self.assertEqual(job.active_processes(),0)


if __name__=='__main__':unittest.main()
