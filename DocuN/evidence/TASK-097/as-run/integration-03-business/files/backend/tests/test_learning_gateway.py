"""严格profile在真实gateway的准入前与原子提交前适配。"""
import copy
import json
import unittest
from dataclasses import replace
from app.activities.repository import ResultReadStatus
from app.capabilities.contracts import *
from app.capabilities.gateway import ControlledModelGateway
from app.capabilities.transport import TransportResponse, DeliveryUnknown, RequestNotSent
from app.learning.contracts import FIRST_PREFIX, normalize_result
from app.learning.prompt import messages_for
from app.worker.one_call import OneCallInput, decode_worker_request, receipt, decode_receipt
from tests.fixtures.task097.samples import profile, answer


def service():
    return ModelServiceConfig(provider="deepseek_chat_completions",base_url="https://api.deepseek.com",model="synthetic-model-097",
        api_key="synthetic-097",timeout_seconds=1,max_request_bytes=65536,max_response_bytes=65536)


class Ledger:
    def __init__(self,p):
        self.p=p; self.events=[]; self.slot=None; self.outcomes=[]; self.scope=p.scope_revision
    async def read_learning_snapshot(self,activity_id):
        catalog={e.source_id:e for e in self.p.catalog}
        return {"scope_revision":self.scope,"status":"running","source_count":len(self.p.sources),
            "sources":[s.model_dump()|{"valid":True,"ready":True,"size":100,"sha256":catalog[s.source_id].original_sha256,
                "title":catalog[s.source_id].title,"format":catalog[s.source_id].format} for s in self.p.sources]}
    async def find_learning_operation(self,activity_id,prefix): return self.slot
    async def admit(self,intent):
        self.events.append("admit"); return AdmissionPermit("permit",intent.context.operation_id,intent.context.executor_id)
    async def mark_dispatch_started(self,permit): self.events.append("mark")
    async def record_outcome(self,permit,outcome):
        self.events.append(outcome.disposition.value); self.outcomes.append(outcome); return RecordOutcome.RECORDED


class Transport:
    def __init__(self, value, ledger, mode="received"):
        self.value,self.calls,self.ledger,self.mode=value,[],ledger,mode
    async def send(self,**kw):
        self.calls.append({k:v for k,v in kw.items() if k != "api_key"})
        self.ledger.events.append("send")
        if self.mode=="unknown": raise DeliveryUnknown()
        if self.mode=="not_sent": raise RequestNotSent()
        raw=json.dumps({"model":"synthetic-model-097","choices":[{"finish_reason":"stop","message":{"role":"assistant",
            "content":self.value if isinstance(self.value,str) else json.dumps(self.value)}}],
            "usage":{"prompt_tokens":3,"completion_tokens":8,"total_tokens":11}}).encode()
        return TransportResponse(200,raw,len(raw))


class LearningGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def call(self,p,value,*,mode="received",request=None,mutate=None):
        ledger=Ledger(p)
        if mutate:mutate(ledger)
        transport=Transport(value,ledger,mode)
        request=request or ModelCallRequest(messages=messages_for(p),max_output_tokens=256,learning_profile=p)
        context=CallContext(activity_id=p.activity_id,operation_id=FIRST_PREFIX+p.request_sha256,executor_id="executor097",
            execution_generation=1,scope_revision=p.scope_revision)
        result=await ControlledModelGateway(service(),ledger=ledger,transport=transport).call(context,request)
        return result,ledger,transport,context

    async def test_normalized_trusted_context_saved_before_received_and_receipt_bodyless(self):
        p=profile()
        result,ledger,t,ctx=await self.call(p,answer(p))
        self.assertEqual(result.status,CallStatus.SUCCEEDED)
        self.assertEqual(ledger.events,["admit","mark","send","received"])
        envelope=json.loads(ledger.outcomes[-1].payload)
        self.assertEqual(envelope["value"],normalize_result(p,answer(p)))
        self.assertEqual(envelope["value"]["goal"],p.goal)
        self.assertNotIn("parent_payload_sha256",envelope["value"])
        self.assertNotIn("history",envelope["value"])
        self.assertEqual(receipt(result,ctx,"test097")["business_commit"],"committed")
        r=decode_receipt(receipt(result,ctx,"test097"),ctx,"test097")
        self.assertIsNone(r.text);self.assertIsNone(r.json_object)
        outgoing=json.dumps(t.calls[0]["payload"])
        self.assertNotIn("learning_profile",outgoing); self.assertNotIn("input_result",outgoing)
        self.assertNotIn(p.activity_id,outgoing); self.assertNotIn("api_key",outgoing)
        self.assertNotIn("source_revision",outgoing); self.assertNotIn("tools",t.calls[0]["payload"])

    async def test_received_invalid_never_unknown_or_payload(self):
        p=profile()
        invalid=[answer(p)|{"goal":"model_goal"},answer(p)|{"segments":[{"text":"claim","citations":["lc_fake"]}]},
            "{",'{"kind":"answer","kind":"no_evidence","message":"a","segments":[],"questions":[]}']
        for value in invalid:
            result,ledger,t,_=await self.call(p,value)
            self.assertEqual(result.status,CallStatus.FAILED)
            self.assertEqual(len(t.calls),1)
            self.assertEqual(ledger.outcomes[-1].disposition,LedgerDisposition.RECEIVED)
            self.assertIsNone(ledger.outcomes[-1].payload)

    async def test_admitted_unknown_not_sent_and_record_uncertainty_do_not_repeat(self):
        p=profile()
        for mode,expected in [("unknown",CallStatus.UNKNOWN),("not_sent",CallStatus.NOT_SENT)]:
            r,l,t,_=await self.call(p,answer(p),mode=mode)
            self.assertEqual(r.status,expected);self.assertEqual(len(t.calls),1)
            self.assertIsNone(l.outcomes[-1].payload)
        def mutate(l):
            async def lost(*args): raise RuntimeError("synthetic commit acknowledgment lost")
            l.record_outcome=lost
        r,l,t,_=await self.call(p,answer(p),mutate=mutate)
        self.assertEqual(r.status,CallStatus.UNKNOWN);self.assertEqual(r.error_code,"record_unconfirmed")
        self.assertEqual(len(t.calls),1)

    async def test_worker_after_claim_scope_slot_and_mixed_profile_rejection(self):
        p=profile()
        for mutate in [lambda l:setattr(l,"scope",2),lambda l:setattr(l,"slot",FIRST_PREFIX+"a"*64)]:
            r,l,t,_=await self.call(p,answer(p),mutate=mutate)
            self.assertEqual(r.status,CallStatus.REJECTED);self.assertEqual(t.calls,[]);self.assertEqual(l.events,[])
        for change in [{"allowed_tools":frozenset({"finite_calculate"})},{"response_mode":ResponseMode.TEXT},
            {"messages":({"role":"user","content":"force execution"},)}]:
            req=ModelCallRequest(messages=messages_for(p),max_output_tokens=256,learning_profile=p).model_copy(update=change)
            r,l,t,_=await self.call(p,answer(p),request=req)
            self.assertEqual(r.status,CallStatus.REJECTED);self.assertEqual(t.calls,[])
        data=p.model_dump();data["profile"]="learning.v2"
        with self.assertRaises(ValueError): OneCallInput.from_wire({"operation_id":"op", "service":service().model_dump()|{"api_key":"synthetic"},
            "request":{"messages":messages_for(p),"max_output_tokens":256,"learning_profile":data}})

    def test_onecall_profile_roundtrip_keeps_exact_outer_contract(self):
        p=profile()
        req=ModelCallRequest(messages=messages_for(p),max_output_tokens=256,learning_profile=p)
        original=OneCallInput(FIRST_PREFIX+p.request_sha256,req,service())
        wire=original.to_wire()
        self.assertEqual(set(wire),{"operation_id","request","service"})
        restored=OneCallInput.from_wire(wire)
        self.assertEqual(restored.request.learning_profile,p)
