"""新类型/旧wire、float32规范、有限输送和收费关门；仅合成传输。"""
import asyncio
from dataclasses import replace
import json
import math
import struct
import time
import unittest
from uuid import uuid4
from app.capabilities.contracts import (CallContext,CallStatus,ModelCallRequest,Message,ModelServiceConfig,Provider,
                                       LedgerDisposition,RecordOutcome,validate_business_payload,build_business_payload)
from app.capabilities.embedding import (EmbeddingRequest,EmbeddingBinding,EmbeddingInput,EmbeddingServiceConfig,
    EmbeddingAdmissionPermit,ControlledEmbeddingGateway,OutboundGrant,float32_values,vector_digest)
from app.capabilities.transport import TransportResponse,DeliveryUnknown
from app.retrieval.contracts import space_identity,digest,fused_rank
from app.worker.one_call import OneCallInput,worker_request,decode_worker_request,receipt,decode_receipt
from app.runtime import psycopg_compatible_loop_factory


def run_async(awaitable):
    from tests.fixtures.step018.s08_loop import ClosedLoop
    with asyncio.Runner(loop_factory=ClosedLoop) as runner:
        return runner.run(awaitable)


class SyntheticEmbeddingTransport:
    is_external=False
    def __init__(self,mode='normal'):self.mode=mode;self.calls=0
    async def send(self,**kwargs):
        self.calls+=1
        if self.mode=='unknown':raise DeliveryUnknown('合成发送后未知')
        data=[]
        for i,_ in enumerate(kwargs['payload']['input']):
            values=[0.1234567890123+i]+[0.002]*511
            if self.mode=='nonfinite':values[0]=float('nan')
            data.append({'index':i,'embedding':values})
        if self.mode=='missing':data.pop()
        if self.mode=='duplicate' and len(data)>1:data[1]['index']=0
        value={'id':'synthetic-embedding','model':'embedding-3','data':data,'usage':{'prompt_tokens':24,'total_tokens':24}}
        if self.mode=='wrong_model':value['model']='not-authorized'
        raw=json.dumps(value,separators=(',',':')).encode()
        return TransportResponse(200,raw,len(raw),'synthetic-embedding')


class SyntheticLedger:
    def __init__(self,fail=None):self.intents=[];self.outcomes=[];self.fail=fail
    async def admit_embedding(self,intent):
        self.intents.append(intent)
        return EmbeddingAdmissionPermit(str(uuid4()),intent.context.operation_id,intent.context.executor_id)
    async def mark_embedding_dispatch_started(self,permit):pass
    async def record_embedding_outcome(self,permit,outcome):
        if self.fail=='record':raise RuntimeError('合成COMMIT确认丢失')
        self.outcomes.append(outcome);return RecordOutcome.RECORDED


def fixture(n=1,purpose='source_index'):
    aid,key=str(uuid4()),str(uuid4())
    binding=EmbeddingBinding(business_key=key,purpose=purpose,request_sha256='a'*64,manifest_sha256='b'*64,
        batch_ordinal=0,scope_revision=1,domain='learning',domain_revision=1)
    inputs=tuple(EmbeddingInput(ordinal=i,identity_sha256=digest({'i':i}),text='合成片段'+str(i)) for i in range(n))
    request=EmbeddingRequest(activity_id=aid,space_id=space_identity('zhipu_embeddings','embedding-3'),binding=binding,inputs=inputs)
    config=EmbeddingServiceConfig(api_key='synthetic-not-a-real-key')
    context=CallContext(activity_id=aid,operation_id=('emb18q.' if purpose=='query' else 'emb18i.')+key+'.0',
        executor_id='synthetic',execution_generation=1,scope_revision=1)
    return context,request,config


class EmbeddingContractTests(unittest.TestCase):
    def test_float32_hash_matches_storage_roundtrip(self):
        values=float32_values([0.1234567890123]+[0.002]*511,normalize=True)
        parsed=json.loads(json.dumps(list(values)))
        self.assertEqual(vector_digest(values),vector_digest(parsed))
        self.assertEqual(struct.pack('<512f',*values),struct.pack('<512f',*parsed))
        self.assertNotEqual(values[0],0.1234567890123/math.hypot(0.1234567890123,*([0.002]*511)))

    def test_dimensions_finite_nonzero_and_bool(self):
        for bad in ([1]*511,[0]*512,[float('nan')]+[1]*511,[float('inf')]+[1]*511,[True]+[1]*511):
            with self.subTest(kind=str(type(bad[0]))):
                with self.assertRaises(ValueError):float32_values(bad)

    def test_v4_embedding_closed_and_v3_unchanged(self):
        context,request,config=fixture(4)
        call=OneCallInput(context.operation_id,request,config);wire=call.to_wire()
        self.assertEqual(wire['protocol'],4);self.assertEqual(wire['capability_kind'],'embedding')
        self.assertEqual(OneCallInput.from_wire(wire).to_wire(),wire)
        wrong=dict(wire,capability_kind='model')
        with self.assertRaises(ValueError):OneCallInput.from_wire(wrong)
        old_config=ModelServiceConfig(provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,base_url='https://api.deepseek.com',
             model='deepseek-chat',api_key='synthetic',timeout_seconds=10,max_request_bytes=65536,max_response_bytes=65536)
        old=OneCallInput('old-v3',ModelCallRequest(messages=(Message(role='user',content='旧合成文字'),),max_output_tokens=10),old_config).to_wire()
        self.assertEqual(set(old),{'operation_id','request','service'})
        self.assertNotIn('outbound_grant',old['service']);self.assertNotIn('outbound_source_manifest',old['service']);self.assertNotIn('retrieval_ref',old['request'])
        self.assertEqual(OneCallInput.from_wire(old).to_wire(),old)

    def test_worker_bound_and_secret_not_argv_or_receipt(self):
        context,request,config=fixture()
        class Lease:
            activity_id=context.activity_id;executor_id=context.executor_id;execution_generation=1;scope_revision=1
        data=worker_request(OneCallInput(context.operation_id,request,config),{'dsn':'postgresql://synthetic@localhost/synthetic',
            'connect_timeout_seconds':1,'statement_timeout_ms':1000,'lock_timeout_ms':1000},Lease(),'synthetic',time.monotonic_ns()+20_000_000_000,10)
        decoded,actual=decode_worker_request(data)
        self.assertEqual(actual,context);self.assertEqual(decoded.capability_kind,'embedding')
        changed=dict(data,protocol=3)
        with self.assertRaises(ValueError):decode_worker_request(changed)

    def test_four_input_payload_with_007_hash(self):
        context,request,config=fixture(4);ledger=SyntheticLedger();transport=SyntheticEmbeddingTransport()
        result=run_async(ControlledEmbeddingGateway(config,ledger=ledger,transport=transport).call(context,request))
        self.assertIs(result.status,CallStatus.SUCCEEDED)
        self.assertEqual(len(ledger.outcomes),1);outcome=ledger.outcomes[0]
        validate_business_payload(outcome.payload,outcome.payload_format,outcome.payload_sha256)
        value=json.loads(outcome.payload)['value'];self.assertEqual(len(value['inputs']),4)
        record=receipt(result,context,'synthetic');self.assertEqual(record['capability_kind'],'embedding')
        self.assertNotIn('vector',json.dumps(record));self.assertNotIn(config.api_key.get_secret_value(),json.dumps(record))
        self.assertEqual(decode_receipt(record,context,'synthetic'),result)

    def test_response_bad_shape_received_without_body(self):
        for mode in ('nonfinite','missing','duplicate','wrong_model'):
            with self.subTest(mode=mode):
                context,request,config=fixture(2);ledger=SyntheticLedger()
                result=run_async(ControlledEmbeddingGateway(config,ledger=ledger,transport=SyntheticEmbeddingTransport(mode)).call(context,request))
                self.assertIs(result.status,CallStatus.FAILED);self.assertEqual(ledger.outcomes[0].disposition,LedgerDisposition.RECEIVED)
                self.assertIsNone(ledger.outcomes[0].payload)

    def test_unknown_retained_and_no_second_send(self):
        context,request,config=fixture();ledger=SyntheticLedger();transport=SyntheticEmbeddingTransport('unknown')
        result=run_async(ControlledEmbeddingGateway(config,ledger=ledger,transport=transport).call(context,request))
        self.assertIs(result.status,CallStatus.UNKNOWN);self.assertEqual(transport.calls,1)
        self.assertEqual(ledger.outcomes[0].disposition,LedgerDisposition.UNKNOWN);self.assertIsNone(result.payload_sha256)

    def test_record_uncertainty_not_business_commit(self):
        context,request,config=fixture();ledger=SyntheticLedger('record')
        result=run_async(ControlledEmbeddingGateway(config,ledger=ledger,transport=SyntheticEmbeddingTransport()).call(context,request))
        self.assertIs(result.status,CallStatus.UNKNOWN);self.assertEqual(receipt(result,context,'synthetic')['business_commit'],'unconfirmed')

    def test_actual_network_default_fails_before_admit(self):
        context,request,config=fixture();ledger=SyntheticLedger()
        result=run_async(ControlledEmbeddingGateway(config,ledger=ledger).call(context,request))
        self.assertIs(result.status,CallStatus.REJECTED);self.assertEqual(result.error_code,'outbound_not_authorized')
        self.assertEqual(ledger.intents,[])

    def test_input_binding_and_scope_identity_rejected(self):
        context,request,config=fixture();ledger=SyntheticLedger();transport=SyntheticEmbeddingTransport()
        bad=context.model_copy(update={'scope_revision':2})
        result=run_async(ControlledEmbeddingGateway(config,ledger=ledger,transport=transport).call(bad,request))
        self.assertIs(result.status,CallStatus.REJECTED);self.assertEqual(transport.calls,0)

    def test_query_capacity_and_space_isolation(self):
        context,request,config=fixture(purpose='query')
        self.assertNotEqual(request.space_id,space_identity('zhipu_embeddings','another-model'))
        data=request.model_dump(mode='json');data['inputs'][0]['text']='字'*1025
        with self.assertRaises(ValueError):EmbeddingRequest.model_validate_json(json.dumps(data))

    def test_rrf_has_frozen_deterministic_order(self):
        self.assertEqual(fused_rank(['b','a'],['a','c']),['a','b','c'])
        with self.assertRaises(ValueError):fused_rank(['a','a'],[])


if __name__=='__main__':unittest.main()
