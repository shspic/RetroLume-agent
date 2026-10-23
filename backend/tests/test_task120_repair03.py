"""Control-flow checks only; connection replacement is not PostgreSQL evidence."""
import unittest
from unittest.mock import patch, AsyncMock
from types import SimpleNamespace as NS
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from app.activities.repository import PostgresAdmissionLedger
from app.data_exit.q_store import QAuthority, POLICY, method_name, is_read_method
from app.data_exit.contracts import DataError

class Connection:
    def __init__(self):self.sql=[]
    async def __aenter__(self):return self
    async def __aexit__(self,*args):pass
    @asynccontextmanager
    async def transaction(self):yield
    async def execute(self,sql,*args):self.sql.append(sql);return self
    async def fetchone(self):
        return dict(activity={},head=None,sources=[],record_sources=[],pending=[],history=[],bodies=[],exposures=[],
                    command={'context_body':'{}'},memory_qualified=True,memory_selected=False,read_at=datetime.now(timezone.utc))

class Repair03(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ledger=PostgresAdmissionLedger('CONTROL_FLOW_ONLY');self.ledger.data_enabled=False
        self.authority=object.__new__(QAuthority);self.authority.hub=NS(control_id='control-flow')
        self.connection=Connection();self.connect=AsyncMock(return_value=self.connection)
        self.aid='01800000-0000-4000-8000-000000000003';self.key='00000000-0000-4000-8000-000000000001'

    async def test_actual_read_closure_inside_inherited_shared_policy(self):
        observed=[];transaction=self.ledger._transaction
        async def record(operation,**kw):
            observed.append(method_name(operation));return await transaction(operation,**kw)
        token=POLICY.set(('control-flow',True))
        try:
            with patch('app.data_exit.q_store.authority_for',return_value=self.authority),patch('psycopg.AsyncConnection.connect',self.connect),\
                 patch.object(self.ledger,'_transaction',record),patch.object(self.ledger,'_memory_teaching_sql',AsyncMock(side_effect=lambda c,s:s)):
                value=await self.ledger.read_teaching_command(self.aid,self.key)
            self.assertEqual(observed,['_teaching_read_snapshot']);self.assertTrue(is_read_method(observed[0]))
            self.assertIsNotNone(value);self.connect.assert_awaited_once();self.assertTrue(self.connection.sql)
            self.assertEqual(POLICY.get(),('control-flow',True))
        finally:POLICY.reset(token)

    async def test_actual_write_closure_denied_before_connection_or_SQL(self):
        captured=[]
        async def capture(operation,**kw):captured.append(operation);raise StopAsyncIteration
        with patch.object(self.ledger,'_transaction',capture):
            with self.assertRaises(StopAsyncIteration):await self.ledger.cancel_activity(self.aid)
        self.assertEqual(method_name(captured[0]),'cancel_activity');self.assertFalse(is_read_method(method_name(captured[0])))
        token=POLICY.set(('control-flow',True))
        try:
            with patch('app.data_exit.q_store.authority_for',return_value=self.authority),patch('psycopg.AsyncConnection.connect',self.connect):
                with self.assertRaises(DataError) as error:await self.ledger._transaction(captured[0])
            self.assertEqual(error.exception.code,'q_policy_upgrade_forbidden');self.connect.assert_not_called();self.assertEqual(self.connection.sql,[])
        finally:POLICY.reset(token)

    async def test_actual_interview_and_HTML_read_validators_do_not_upgrade_shared(self):
        class ReachedReadValidator(Exception):pass
        for name,helper in [('validate_interview_request','_interview_lock'),('verify_html_request','_memory_lock_prefix')]:
            with self.subTest(name=name):
                token=POLICY.set(('control-flow',True));self.connect.reset_mock()
                try:
                    with patch('app.data_exit.q_store.authority_for',return_value=self.authority),patch('psycopg.AsyncConnection.connect',self.connect),\
                         patch.object(self.ledger,helper,AsyncMock(side_effect=ReachedReadValidator)):
                        with self.assertRaises(ReachedReadValidator):
                            if name=='validate_interview_request':await self.ledger.validate_interview_request(NS(activity_id=self.aid),NS(business_key=self.key),None)
                            else:await self.ledger.verify_html_request(NS(activity_id=self.aid))
                    self.connect.assert_awaited_once();self.assertTrue(is_read_method(name))
                finally:POLICY.reset(token)

    async def test_v2_v3_read_branches_with_and_without_selected_memory(self):
        from app.learning.teaching_adapter import validate_teaching_request
        from app.learning.teaching_contracts import TeachingMemoryProfile,TeachingHybridProfile,TeachingMemoryFrozenContext,TeachingHybridFrozenContext
        from app.capabilities.contracts import Message
        from app.learning.contracts import sha,canonical
        messages=[Message(role='user',content='CONTROL_FLOW_ONLY')];dumped=[m.model_dump(mode='json',exclude_none=True) for m in messages]
        for version,selected in [('teaching.v3',False),('teaching.v2',True),('teaching.v3',True)]:
            with self.subTest(version=version,selected=selected):
                refs=[];profile=NS(profile=version,activity_id=self.aid,scope_revision=1,max_output_tokens=64,command_key=self.key,request_sha256='a'*64,
                    context_sha256='b'*64,memory_selection_sha256='c'*64,memory_refs=refs,retrieval_ref=None,memory_dependency_sha256='d'*64,
                    messages_sha256=sha(canonical(dumped)),catalog=[])
                profile.model_dump=lambda:{}
                cls=TeachingHybridFrozenContext if version=='teaching.v3' else TeachingMemoryFrozenContext
                frozen=cls.model_construct(context_sha256=profile.context_sha256,memory_refs=refs,retrieval_ref=None,memory_dependency_sha256='d'*64,
                    recipe={} if selected else None,messages=None if selected else dumped,assembled_messages_sha256=profile.messages_sha256,catalog=[])
                request=NS(teaching_profile=profile,learning_profile=None,allowed_tools=[],max_output_tokens=64,messages=messages,retrieval_ref=None)
                context=NS(activity_id=self.aid,scope_revision=1,operation_id='teach8m.'+self.key+'.'+'a'*64)
                token=POLICY.set(('control-flow',True))
                try:
                    with patch('app.data_exit.q_store.authority_for',return_value=self.authority),patch('psycopg.AsyncConnection.connect',self.connect),\
                         patch.object(self.ledger,'_memory_teaching_sql',AsyncMock(side_effect=lambda c,s:s)),\
                         patch.object(TeachingMemoryProfile,'model_validate',return_value=profile),patch.object(TeachingHybridProfile,'model_validate',return_value=profile),\
                         patch('app.learning.teaching_contracts.parse_frozen_context',return_value=frozen),\
                         patch('app.memory.context.materialize_recipe',AsyncMock(return_value=dumped)),\
                         patch.object(self.ledger,'read_memory_selection',AsyncMock(return_value={'selection_sha256':'c'*64,'selected':selected})),\
                         patch.object(self.ledger,'read_learning_snapshot',AsyncMock(return_value={'sources':[]})):
                        self.assertIsNone(await validate_teaching_request(context,request,self.ledger))
                finally:POLICY.reset(token)

class ProvenanceRepair03(unittest.TestCase):
    def setUp(self):
        self.authority=NS(bundle={'templates':[],'template_atoms':['messages','role','user','content','html_profile','context_json']},
            manifest=NS(fixed_inputs=[],fragments=[],model_dump=lambda **kw:{}))
        self.state={'activity':{'id':'a'},'sources':[],'commands':[],'parents':[]}

    def test_only_exact_qualified_parent_history_is_derived(self):
        from app.capabilities.q_context import validate_provenance
        from app.capabilities.q_protocol import canonical
        from app.capabilities.contracts import AdmissionDenied
        history=canonical({'kind':'answer','segments':[{'text':'parent-body','citations':['lc_parent']}],'questions':[],'message':'parent-message'})
        request={'messages':[{'role':'user','content':history}]}
        validate_provenance(self.authority,request,{},self.state,[],[history],'followup')
        for derived,text in [([],history),([history],history.replace('parent-body','foreign-body')),([history],history+' ')]:
            with self.assertRaises(AdmissionDenied):validate_provenance(self.authority,{'messages':[{'role':'user','content':text}]},{},self.state,[],derived,'followup')

    def test_HTML_config_hash_requires_server_command_metadata(self):
        from app.capabilities.q_context import validate_provenance
        from app.capabilities.q_protocol import canonical
        from app.capabilities.contracts import AdmissionDenied
        request={'html_profile':{'context_json':canonical({'config_sha256':'a'*64})}}
        self.state['commands']=[{'metadata':['a'*64]}]
        validate_provenance(self.authority,request,{},self.state,[],[],'generate')
        self.state['commands']=[]
        with self.assertRaises(AdmissionDenied):validate_provenance(self.authority,request,{},self.state,[],[],'generate')
        self.state['commands']=[{'metadata':['b'*64]}]
        with self.assertRaises(AdmissionDenied):validate_provenance(self.authority,request,{},self.state,[],[],'generate')

    def test_teaching_node_id_requires_frozen_server_command_identity(self):
        from app.capabilities.q_context import validate_provenance
        from app.capabilities.contracts import AdmissionDenied
        self.state['commands']=[{'metadata':['n1']}]
        validate_provenance(self.authority,{'node_id':'n1'},{},self.state,[],[],'exercise')
        with self.assertRaises(AdmissionDenied):validate_provenance(self.authority,{'node_id':'n2'},{},self.state,[],[],'exercise')
        self.state['commands']=[]
        with self.assertRaises(AdmissionDenied):validate_provenance(self.authority,{'node_id':'n1'},{},self.state,[],[],'exercise')

class HistoricalAbandonRepair03(unittest.TestCase):
    def test_only_exact_obsolete_unknown_without_other_pending_can_be_abandoned(self):
        from app.interview.policy import transition
        from app.interview.contracts import InterviewRefusal
        head={'phase':'ready','pending_key':None};body={'pending_key':'old-key'}
        target={'business_key':'old-key','status':'unknown','obsolete':True}
        transition('abandon',head,body,abandon_target=target)
        for changed in [None,dict(target,obsolete=False),dict(target,status='committed'),dict(target,business_key='foreign')]:
            with self.assertRaises(InterviewRefusal):transition('abandon',head,body,abandon_target=changed)
        with self.assertRaises(InterviewRefusal):transition('abandon',dict(head,pending_key='different'),body,abandon_target=target)
        transition('abandon',dict(head,pending_key='old-key'),body)

class TeachingNodeFieldsRepair03(unittest.TestCase):
    def test_only_typed_path_node_location_admits_parent_rationale(self):
        from app.capabilities.q_context import validate_provenance
        from app.capabilities.q_protocol import canonical
        from app.capabilities.contracts import AdmissionDenied
        authority=NS(bundle={'templates':[],'template_atoms':['messages','role','user','content','teaching_profile','task','path_nodes']},
            manifest=NS(fixed_inputs=[],fragments=[],model_dump=lambda **kw:{}))
        state={'activity':{'id':'a'},'sources':[],'commands':[],'parents':[]}
        def request(document):return {'teaching_profile':{},'messages':[{'role':'user','content':canonical(document)}]}
        body={'task':{'path_nodes':[{'rationale':'verified-parent-rationale'}]}}
        validate_provenance(authority,request(body),{},state,[],['verified-parent-rationale'],'exercise')
        for document,derived in [(body,[]),({'task':{'rationale':'verified-parent-rationale'}},['verified-parent-rationale']),({'task':{'path_nodes':[{'invented_field':'verified-parent-rationale'}]}},['verified-parent-rationale'])]:
            with self.assertRaises(AdmissionDenied):validate_provenance(authority,request(document),{},state,[],derived,'exercise')

class RetrievalReceiptsRepair03(unittest.TestCase):
    def test_cache_ready_requires_index_and_current_complete_cache(self):
        from tests.fixtures.task120.repair03 import terminal_retrieval
        receipt={'status':'terminal','terminal_disposition':'cache_ready'}
        ready={'ready':True,'fragments':4,'cached_fragments':4}
        self.assertTrue(terminal_retrieval('source_index',receipt,ready))
        self.assertFalse(terminal_retrieval('query',receipt,ready))
        self.assertFalse(terminal_retrieval('source_index',receipt,dict(ready,cached_fragments=3)))
        self.assertFalse(terminal_retrieval('source_index',receipt,dict(ready,ready=False)))
        self.assertFalse(terminal_retrieval('source_index',receipt,None))
        self.assertTrue(terminal_retrieval('query',dict(receipt,terminal_disposition='received')))
        self.assertFalse(terminal_retrieval('query',dict(receipt,terminal_disposition='unknown')))

class HttpRejectionRepair03(unittest.TestCase):
    def test_bounded_nested_codes_saved_without_error_bodies(self):
        from tests.fixtures.task120.api_runtime import Client
        for response in [{'code':'q_denied'},{'detail':{'code':'q_denied'}},{'detail':{'error':{'code':'q_denied'}}}]:
            client=object.__new__(Client);client.headers={};client.timeline=[]
            client.client=NS(request=lambda *args,**kw:NS(status_code=409,json=lambda:response))
            with self.assertRaisesRegex(RuntimeError,'task120_http_409_q_denied'):client.request('POST','/TESTONLY',{})
            self.assertEqual(client.timeline[0]['rejection_code'],'q_denied');self.assertNotIn('detail',client.timeline[0])
        client.client=NS(request=lambda *args,**kw:NS(status_code=409,json=lambda:{'code':'untrusted arbitrary error body'}))
        with self.assertRaisesRegex(RuntimeError,'task120_http_409_http_rejected'):client.request('POST','/TESTONLY',{})
        self.assertIsNone(client.timeline[-1]['rejection_code'])

if __name__=='__main__':unittest.main()
