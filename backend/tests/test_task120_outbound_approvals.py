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
    def test_admission_kernel_witness_cannot_survive_completion(self):
        from app.data_exit.q_kernel import AdmissionSignal,admission_active
        signal=AdmissionSignal()
        self.assertTrue(admission_active(signal.name))
        signal.close()
        self.assertFalse(admission_active(signal.name))
        self.assertFalse(admission_active('Local\\untrusted'))

    def test_q_rejects_silent_text_normalization_and_preserves_schema_alias(self):
        from types import SimpleNamespace
        from uuid import uuid4
        from app.capabilities.q_context import check_input_bytes
        from app.learning.teaching_contracts import TeachingCommandInput
        from app.interview.contracts import parse_command
        service=SimpleNamespace(outbound_grant={'schema':'retrolume.outbound-grant.v2'})
        raw={'business_key':str(uuid4()),'action':'goal','expected_revision':0,'expected_goal_version':0,'expected_scope_revision':1,'body':{'goal':' '+TEXT+' '}}
        parsed=TeachingCommandInput.model_validate(raw)
        with self.assertRaises(ValueError):check_input_bytes(raw,parsed,service)
        check_input_bytes(raw,parsed,SimpleNamespace(outbound_grant=None))
        raw={'schema':'interview.command.v1','business_key':str(uuid4()),'action':'start','expected_head_revision':0,'expected_goal_version':0,'expected_scope_revision':1,'body':{'goal':{'target':TEXT}}}
        check_input_bytes(raw,parse_command(raw),service)

    def test_admission_intent_retains_real_process_witness_and_uncertain_ack_closes(self):
        authority=store();row=prepared(authority);pid=row['prepared_id']
        authority.approve(pid,principal_id(),current=True);ref=authority.reference(authority.request(pid))
        context=CallContext(activity_id=AID,operation_id='offline.request',executor_id='fixture',execution_generation=1,scope_revision=1)
        authority.check_reference(ref,context=context)
        authority.admission_intent(ref,context)
        self.assertEqual(authority.request(pid)['admission_owner']['pid'],os.getpid())
        authority.admission_failed(ref,definitely_denied=False)
        self.assertEqual(authority.request(pid)['closed'],'admission_unconfirmed')
        with self.assertRaises(DataError):authority.check_reference(ref,context=context,claimed=True)

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

    def test_wire4_carries_private_authorization_without_provider_message_change(self):
        authority=store();row=prepared(authority);authority.approve(row['prepared_id'],principal_id(),current=True)
        service=ModelServiceConfig(provider='deepseek_chat_completions',base_url='https://api.deepseek.com',model='deepseek-flash',api_key=SecretStr('synthetic'),
            max_request_bytes=65536,max_response_bytes=65536,outbound_grant=authority.bundle['grant'],outbound_source_manifest=authority.bundle['manifest'],
            outbound_authorization=authority.reference(authority.request(row['prepared_id'])),returned_models=('deepseek-flash',))
        request=ModelCallRequest(messages=[{'role':'user','content':TEXT}],max_output_tokens=1)
        wire=OneCallInput('offline.request',request,service).to_wire()
        self.assertEqual(wire['protocol'],4)
        self.assertEqual(OneCallInput.from_wire(wire).to_wire(),wire)
        payload=__import__('app.capabilities.gateway',fromlist=['ControlledModelGateway']).ControlledModelGateway(service)._build_payload(request)
        self.assertNotIn('outbound_authorization',canonical(payload));self.assertNotIn(row['prepared_id'],canonical(payload))

    def test_v1_keeps_80_20_while_v2_is_100_25(self):
        from app.capabilities.embedding import OutboundGrant
        authority=store();value=dict(authority.bundle['grant']);value.pop('instance_binding_sha256')
        value.update(schema='retrolume.outbound-grant.v1',global_max_requests=80,global_max_cost_microunits=20000000,
            provider_capabilities=['deepseek_chat_completions/deepseek-chat','zhipu_embeddings/embedding-3'])
        self.assertEqual(OutboundGrant.from_wire(value).global_max_requests,80)
        with self.assertRaises(ValueError):OutboundGrant.from_wire({**value,'global_max_requests':100})
        self.assertEqual(authority.grant.global_max_requests,100)


class ConfigurationTests(unittest.TestCase):
    def test_normal_examples_are_inert_without_reading_user_configuration(self):
        from app.service_config import load_activity_config
        from app.retrieval.service import load_integration_config
        from app.operator.q_request import read_config
        project=Path(__file__).resolve().parents[2]
        with patch.dict(os.environ,{},clear=True):
            activity=load_activity_config(project/'config/activity.example.json')
            integration=load_integration_config(project/'config/integration.example.json')
            approval=read_config(project/'config/q-approval.example.json')
        self.assertFalse(activity.create_layer.available)
        self.assertFalse(activity.continue_layer.available)
        self.assertFalse(activity.learning_layer.available)
        self.assertFalse(integration.available)
        self.assertFalse(integration.public()['real_outbound_authorized'])
        self.assertFalse(approval['enabled'])
        self.assertIsNone(approval['root_file'])

    def test_operator_configuration_rejects_untrusted_path_types(self):
        from app.operator.q_request import read_config
        authority=store();path=authority.hub.root/'invalid-q-config.json'
        body={'schema':'retrolume.q-approval-config.v2','enabled':True,'control_root':42,
            'database_url_env':'RETROLUME_TASK120_FLOW_TEST_DATABASE_URL','root_file':[]}
        path.write_text(json.dumps(body),encoding='utf-8')
        with self.assertRaises(DataError):read_config(path)


class LockTests(unittest.IsolatedAsyncioTestCase):
    async def test_shared_upgrade_is_rejected_and_exclusive_wait_is_bounded(self):
        authority=store()
        async with authority.async_policy(shared=True):
            with self.assertRaises(DataError):
                async with authority.async_policy():pass
        async with authority.async_policy():
            async with authority.async_policy(shared=True):pass


class RuntimeControlTests(unittest.TestCase):
    def test_actual_job_members_restore_after_nested_python_exit(self):
        import sys,time,subprocess
        from uuid import uuid4
        from tests.fixtures.task120.resources import root_job,ROOT
        identity=str(uuid4())
        with root_job(identity) as job:
            job.spawn_suspended([sys._base_executable,'-m','tests.fixtures.task120.merged',identity],cwd=str(ROOT/'backend'))
            job.resume();self.assertTrue(job.wait_empty_until(time.monotonic_ns()+8_000_000_000))
            self.assertEqual(job.primary_exit_code(),0)

    def test_fixed_subbatches_expire_without_implicit_retry(self):
        import time
        from tests.fixtures.task120.merged import validate,await_request
        good={'ordinal':1,'phase':'flow','seconds':20,'previous_exit':None}
        self.assertEqual(validate(good,1,None),good)
        for bad in ({**good,'phase':'arbitrary-command'},{**good,'seconds':301},{**good,'previous_exit':0}):
            with self.assertRaises(ValueError):validate(bad,1,None)
        path=store().hub.root/'not-submitted.json';start=time.monotonic()
        self.assertIsNone(await_request(path,start+.03));self.assertLess(time.monotonic()-start,.5)

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
