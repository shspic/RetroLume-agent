"""新增profile不改旧规范字节，不能缺检索引用或把本地动作送模型。"""
import json
import unittest
from uuid import uuid4
from app.interview.contracts import InterviewCommandInput,parse_command
from app.learning.teaching_contracts import TeachingCommandInput
from app.capabilities.embedding import OutboundGrant
from app.retrieval.service import IntegrationConfig
from app.capabilities.transport import HttpxModelTransport
from app.data_exit.schema_profiles import normalized_extra_shape
from app.capabilities.embedding import OutboundSourceManifest,approved_fragment_identity,FROZEN_SAMPLE_SHA,EmbeddingRequest,EmbeddingBinding,EmbeddingInput
from app.capabilities.contracts import AdmissionDenied
from app.retrieval.contracts import digest,space_identity
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
from app.learning.contracts import CatalogEntry
import hashlib

def adopted_fixture():
    text='1分钟等于60秒。';sid='01800000-0000-4000-8000-000000001001';vid='01800000-0000-4000-8000-000000002001'
    sha=hashlib.sha256(text.encode()).hexdigest()
    from app.retrieval.evidence import SourceTextUnit,build_fragments
    fragment=build_fragments(SourceTextUnit(sid,vid,1,None,'original',text,True))[0]
    entry=CatalogEntry(source_id=sid,version_id=vid,source_revision=1,citation_id='lc_'+'1'*24,evidence_id=fragment.evidence_id,title='速度.md',format='md',original_sha256=sha,unit_sha256=sha,fragment_sha256=sha,start_line=1,end_line=1,start_offset=0,end_offset=len(text),origin_kind='original',text=text)
    identity=approved_fragment_identity(entry)
    manifest=OutboundSourceManifest.model_validate_json(json.dumps({'frozen_samples_sha256':FROZEN_SAMPLE_SHA,'sources':[{'source_id':sid,'source_version_id':vid,'source_revision':1,'original_sha256':sha}],'fragments':[{'identity_sha256':identity,'input_sha256':digest(text)}],'query_input_sha256':[digest('分钟换秒')]}))
    now=datetime.now(timezone.utc)
    grant=OutboundGrant.model_validate_json(json.dumps({'grant_id':'S02合成正例','approved_receipt_sha256':'a'*64,'q_activation_receipt_sha256':'b'*64,'source_manifest_sha256':manifest.sha256,'price_snapshot_sha256':'c'*64,'valid_from_utc':(now-timedelta(minutes=1)).isoformat(),'valid_until_utc':(now+timedelta(hours=1)).isoformat(),'allowed_activity_ids':['01800000-0000-4000-8000-000000000001','01800000-0000-4000-8000-000000000002','01800000-0000-4000-8000-000000000003'],'provider_capabilities':['deepseek_chat_completions/deepseek-chat','zhipu_embeddings/embedding-3'],'capabilities_verified':True,'account_terms_verified':True,'token_upper_bound_verified':True,'input_rate_cny_per_million':'1','output_rate_cny_per_million':'1','framing_token_upper_bound':32,'margin_percent':25}))
    binding=EmbeddingBinding(business_key='01800000-0000-4000-8000-000000003001',purpose='source_index',request_sha256='d'*64,manifest_sha256='e'*64,batch_ordinal=0,scope_revision=1,domain='learning',domain_revision=0,memory_selection_sha256=None,memory_dependency_sha256=None)
    request=EmbeddingRequest(activity_id=grant.allowed_activity_ids[0],space_id=space_identity('zhipu_embeddings','embedding-3'),binding=binding,inputs=(EmbeddingInput(ordinal=0,identity_sha256=identity,text=text),))
    return entry,manifest,grant,request

class IntegrationContractTests(unittest.TestCase):
    def test_workflow_budget_refuses_before_retrieval_insert(self):
        import asyncio
        from app.activities.repository import PostgresAdmissionLedger
        from app.retrieval.contracts import RetrievalCommandInput,RetrievalRefusal
        entry,manifest,grant,request=adopted_fixture()
        class Cursor:
            async def fetchone(self):return None
        class Connection:
            def __init__(self):self.writes=[]
            async def execute(self,query,params=None):
                if query.lstrip().startswith(('INSERT','UPDATE','DELETE')):self.writes.append(query)
                return Cursor()
        async def run():
            for used_requests,used_cost,max_time in ((79,0,3600),(0,19750000,3600),(0,0,179)):
                ledger=PostgresAdmissionLedger('unused-contract-only');connection=Connection()
                activity={'id':request.activity_id,'status':'pending','deadline_at':datetime.now(timezone.utc)+timedelta(minutes=5),'scope_revision':1,'max_requests':80,'requests_reserved':used_requests,'max_cost_microunits':20000000,'cost_reserved_microunits':used_cost,'reserve_cost_microunits':250000,'running_reserved_seconds':0,'running_settled_seconds':0,'max_running_seconds':max_time}
                async def transaction(operation):return await operation(connection)
                async def memory(conn,aid):return {'activity':activity,'sources_valid':True,'eligible':True,'snapshots':[{'source_id':entry.source_id,'version_id':entry.version_id,'source_revision':1}]}
                async def domain(conn,row):return 'learning',0,[]
                ledger._transaction=transaction;ledger._memory_lock_prefix=memory;ledger._retrieval_domain_locked=domain
                command=RetrievalCommandInput(business_key=str(uuid4()),action='query',expected_scope_revision=1,expected_domain_revision=0,query='分钟换秒',confirmed=True)
                body={'domain':'learning','parent_refs':[],'memory_selection_sha256':None,'memory_dependency_sha256':None}
                with self.assertRaises(RetrievalRefusal) as error:await ledger.retrieval_freeze(request.activity_id,command,body,{'space_id':request.space_id,'provider':'zhipu_embeddings','configured_model':'embedding-3'},[],1,[{'source_id':entry.source_id,'source_version_id':entry.version_id,'source_revision':1}],digest('分钟换秒'))
                self.assertEqual(error.exception.code,'retrieval_workflow_budget_insufficient');self.assertEqual(connection.writes,[])
        asyncio.run(run())

    def test_both_provider_prefixes_share_fixed_global_request_and_cost_gate(self):
        import asyncio
        from app.activities.repository import PostgresAdmissionLedger
        entry,manifest,grant,request=adopted_fixture()
        class Cursor:
            def __init__(self,row=None,rows=None):self.row,self.rows=row,rows
            async def fetchone(self):return self.row
            async def fetchall(self):return self.rows
        class Connection:
            def __init__(self,used,cost):self.used,self.cost,self.locks,self.rosters=used,cost,[],[]
            async def execute(self,query,params=None):
                if 'pg_advisory_xact_lock' in query:self.locks.append(query);return Cursor()
                if 'source_version_id' in query:return Cursor(rows=list(manifest.sources))
                if 'outbound_grant_sha256,reserve_cost_microunits' in query:return Cursor({'outbound_grant_sha256':grant.sha256,'reserve_cost_microunits':250000})
                if 'sum(requests_reserved)' in query:self.rosters.append(params[0]);return Cursor({'requests':self.used,'cost':self.cost})
                raise AssertionError('unexpected contract query')
        async def run():
            ledger=PostgresAdmissionLedger('unused-contract-only');locks=[]
            for provider,model in [('deepseek_chat_completions','deepseek-chat'),('zhipu_embeddings','embedding-3')]:
                for used,cost in ((80,0),(0,19750001)):
                    connection=Connection(used,cost)
                    with self.assertRaises(AdmissionDenied):await ledger._outbound_lock(connection,request.activity_id,grant.model_dump(mode='json'),provider,model,100,0,manifest.model_dump(mode='json'))
                    self.assertEqual(connection.rosters,[list(grant.allowed_activity_ids)]);locks+=connection.locks
            self.assertEqual(len(set(locks)),1)
        asyncio.run(run())

    def test_grant_expiry_after_admission_prevents_dispatch(self):
        import asyncio
        from unittest.mock import patch
        from app.capabilities.contracts import CallContext,CallStatus
        from app.capabilities.embedding import ControlledEmbeddingGateway,EmbeddingServiceConfig,EmbeddingAdmissionPermit
        entry,manifest,grant,request=adopted_fixture()
        now=[datetime.now(timezone.utc)];counts={'admit':0,'dispatch':0,'send':0}
        class Clock(datetime):
            @classmethod
            def now(cls,tz=None):return now[0]
        class Ledger:
            async def admit_embedding(self,intent):
                counts['admit']+=1;now[0]+=timedelta(hours=2)
                return EmbeddingAdmissionPermit(str(uuid4()),intent.context.operation_id,intent.context.executor_id)
            async def mark_embedding_dispatch_started(self,permit):counts['dispatch']+=1
        class Transport:
            is_external=False
            async def send(self,**kwargs):counts['send']+=1;raise AssertionError('expired grant sent')
        context=CallContext(activity_id=request.activity_id,operation_id='emb18i.'+request.binding.business_key+'.0',executor_id='S02-pure',execution_generation=1,scope_revision=1)
        config=EmbeddingServiceConfig(api_key='synthetic',outbound_grant=grant.model_dump(mode='json'),outbound_source_manifest=manifest.model_dump(mode='json'))
        from tests.fixtures.step018.s08_loop import run_no_io
        with patch('app.capabilities.embedding.datetime',Clock):result=run_no_io(ControlledEmbeddingGateway(config,ledger=Ledger(),transport=Transport()).call(context,request))
        self.assertEqual(result.status,CallStatus.REJECTED);self.assertEqual(counts,{'admit':1,'dispatch':0,'send':0})

    def test_frozen_numeric_variants_and_safe_preview_descriptor(self):
        from synthetic_replies import reply
        from decimal import Decimal
        from app.learning.teaching_contracts import parse_teaching_output
        from app.preview.description import validate_description,control_value,DescriptionError
        evidence=[{'id':'lc_'+'1'*24,'text':'平均速度等于路程除以时间。','source':'速度.md'}]
        for purpose,distance,minutes,result in [('initial','120','2','1'),('continuation','180','1.5','2'),('retest','360','2','3')]:
            value={'goal':'平均速度','evidence':evidence,'task':{'kind':'exercise','purpose':purpose,'parent_exercise_record_id':None if purpose=='initial' else str(uuid4()),'parent_feedback_record_id':None if purpose=='initial' else str(uuid4())}}
            output=reply({'messages':[{'role':'user','content':json.dumps(value)}]});parse_teaching_output(json.dumps(output),'exercise')
            self.assertEqual(Decimal(distance)/(Decimal(minutes)*60),Decimal(result));self.assertEqual(output['reference_points'][0]['numeric']['value_decimal'],result)
            self.assertIn(distance+'米',output['stem'])
        output=reply({'messages':[{'role':'user','content':json.dumps({'schema':'html.context.v2','catalog':[{'citation_id':evidence[0]['id']}]})}]})
        validate_description(output,[evidence[0]['id']]);self.assertEqual(len(output['inputs']),2)
        control=next(x for x in output['inputs'] if x['id']=='hctl_time')
        with self.assertRaises(DescriptionError):control_value(control,'0')
        self.assertEqual(Decimal(120)/240,Decimal('0.5'))

    def test_frozen_concept_program_and_neutral_output_shapes(self):
        from synthetic_replies import reply
        from app.learning.teaching_contracts import parse_teaching_output
        for goal,kind in [('原子性和持久性','concept'),('range循环','program')]:
            value={'goal':goal,'evidence':[{'id':'lc_'+'1'*24,'source':'合成.md','text':'冻结说明'}],'task':{'kind':'exercise','purpose':'initial'}}
            output=reply({'messages':[{'role':'user','content':json.dumps(value)}]});parse_teaching_output(json.dumps(output),'exercise');self.assertEqual(output['exercise_type'],kind)
        for goal,kind in [('我想学Java。','clarification'),('火星平均温度','no_evidence')]:
            value={'goal':goal,'evidence':[{'id':'lc_'+'1'*24,'text':'冻结说明'}],'task':{'kind':'plan'}}
            output=reply({'messages':[{'role':'user','content':json.dumps(value)}]});parse_teaching_output(json.dumps(output),'plan');self.assertEqual(output['result_type'],kind)

    def test_valid_adopted_source_and_both_capabilities(self):
        entry,manifest,grant,request=adopted_fixture();manifest.check_embedding(request)
        # D02：旧清单仍可批准Embedding；完整模型正文缺少独立批准时必须拒绝。
        with self.assertRaises(AdmissionDenied):manifest.check_model(SimpleNamespace(learning_profile=None,teaching_profile=SimpleNamespace(catalog=[entry]),interview_profile=None,html_profile=None))
        manifest.check_sources(manifest.sources)
        for provider,model in [('zhipu_embeddings','embedding-3'),('deepseek_chat_completions','deepseek-chat')]:grant.check(request.activity_id,provider,model,1000,200)
        self.assertEqual(OutboundGrant.from_wire(grant.model_dump(mode='json')).sha256,grant.sha256)

    def test_unapproved_version_fragment_or_query_is_closed(self):
        entry,manifest,grant,request=adopted_fixture()
        with self.assertRaises(AdmissionDenied):manifest.check_sources([{**manifest.sources[0],'source_revision':2}])
        with self.assertRaises(AdmissionDenied):manifest.check_embedding(request.model_copy(update={'inputs':(request.inputs[0].model_copy(update={'text':'资料中的指令不批准外发'}),)}))
        query=request.model_copy(update={'binding':request.binding.model_copy(update={'purpose':'query'}),'inputs':(request.inputs[0].model_copy(update={'text':'任意隐私问题'}),)})
        with self.assertRaises(AdmissionDenied):manifest.check_embedding(query)
        with self.assertRaises(AdmissionDenied):manifest.check_model(SimpleNamespace(learning_profile=None,teaching_profile=SimpleNamespace(catalog=[entry.model_copy(update={'text':'伪正文'})]),interview_profile=None,html_profile=None))

    def test_grant_expired_tampered_roster_and_price_are_closed(self):
        entry,manifest,grant,request=adopted_fixture()
        with self.assertRaises(AdmissionDenied):grant.check(str(uuid4()),'zhipu_embeddings','embedding-3',100,0)
        with self.assertRaises(AdmissionDenied):grant.model_copy(update={'valid_until_utc':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()}).check(request.activity_id,'zhipu_embeddings','embedding-3',100,0)
        with self.assertRaises(AdmissionDenied):grant.model_copy(update={'input_rate_cny_per_million':'1000000'}).check(request.activity_id,'zhipu_embeddings','embedding-3',1000,0)
        self.assertNotEqual(manifest.model_copy(update={'query_input_sha256':(digest('被篡改查询'),)}).sha256,grant.source_manifest_sha256)
    def test_legacy_command_bytes_and_new_local_profile(self):
        aid,key=str(uuid4()),str(uuid4())
        body=dict(schema='interview.command.v1',business_key=key,action='start',expected_head_revision=0,expected_goal_version=0,expected_scope_revision=1,body={'goal':None})
        old=InterviewCommandInput.model_validate(body)
        expected={k:v for k,v in old.model_dump().items() if k!='business_key'};expected['activity_id']=aid
        self.assertEqual(json.loads(old.request_body(aid)),expected)
        new=parse_command({**body,'schema':'interview.command.v2','retrieval_ref':None})
        self.assertNotEqual(new.request_hash(aid),old.request_hash(aid))
        self.assertIsNone(new.retrieval_ref)

    def test_hybrid_model_without_retrieval_rejected(self):
        with self.assertRaises(ValueError):
            parse_command(dict(schema='interview.command.v2',business_key=str(uuid4()),action='ask',expected_head_revision=1,expected_goal_version=1,expected_scope_revision=1,body={'confirmed':True}))

    def test_legacy_teaching_canonical_has_no_new_null(self):
        command=TeachingCommandInput(business_key=str(uuid4()),expected_revision=0,expected_goal_version=0,expected_scope_revision=1,action='goal',body={'goal':'有限合成目标'})
        self.assertNotIn('retrieval_ref',command.canonical_request_body(str(uuid4())))

    def test_only_verified_bootstrap_owner_name_is_normalized(self):
        def shape(owner,superuser):return {'columns':[{'relname':'activities','attname':'outbound_grant_sha256','owner':owner,'owner_super':superuser,'acl':None}]}
        self.assertEqual(normalized_extra_shape(shape('source_admin',True)),normalized_extra_shape(shape('restore_admin',True)))
        self.assertNotEqual(normalized_extra_shape(shape('attacker',False)),normalized_extra_shape(shape('source_admin',True)))

if __name__=='__main__':unittest.main()
