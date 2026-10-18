"""TASK085离线合同与真实gateway核心；不访问网络/数据库。"""
import asyncio
from dataclasses import asdict
import json
import hashlib
import struct
from pathlib import Path
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from app.capabilities.contracts import *
from app.capabilities.gateway import ControlledModelGateway
from app.capabilities.transport import DeliveryUnknown, TransportResponse
from app.worker.one_call import *
from app.worker.worker_main import execute_one_call, run_internal_task
from app.worker.command import WorkerCommand
from app.worker.supervisor_ipc import pack_frame, unpack_frame, SLOT_SIZE, IpcUnknown
from app.worker.session import SessionConfig
from app.worker.launcher import _request
from app.worker.supervisor_main import _validated_request
from app.activities import ActivityLease, PostgresAdmissionLedger
from datetime import datetime, timezone


def service(**kw):
    values = dict(provider="deepseek_chat_completions", base_url="https://api.deepseek.com",
                  model="synthetic-model", api_key="synthetic-secret-085", timeout_seconds=.03,
                  max_request_bytes=4096, max_response_bytes=4096)
    return ModelServiceConfig(**(values | kw))


def request(**kw):
    return ModelCallRequest(**(dict(messages=[{"role":"user", "content":"synthetic-body-085"}],
                                   max_output_tokens=40, response_mode="text") | kw))


def frame():
    lease = ActivityLease(str(uuid4()), "executor", 7, 3, datetime.now(timezone.utc), 12, 1)
    call = OneCallInput("operation-085", request(), service())
    return worker_request(call, dict(dsn="synthetic-dsn", connect_timeout_seconds=1,
                          statement_timeout_ms=500, lock_timeout_ms=100), lease,
                          "run-085", time.monotonic_ns()+10_000_000_000, .5)


class Ledger:
    def __init__(self, denied=False):
        self.events = []
        self.context = None
        self.seen = set()
        self.denied = denied

    async def admit(self, intent):
        self.events.append("admit")
        self.context = intent.context
        if self.denied or intent.context.operation_id in self.seen:
            raise AdmissionDenied()
        self.seen.add(intent.context.operation_id)
        return AdmissionPermit("permit", intent.context.operation_id, intent.context.executor_id)

    async def mark_dispatch_started(self, permit):
        self.events.append("mark")

    async def record_outcome(self, permit, outcome):
        self.events.append(outcome.disposition.value)


class Transport:
    def __init__(self, ledger, mode="success"):
        self.ledger, self.mode, self.calls = ledger, mode, 0

    async def send(self, **kw):
        self.calls += 1
        self.ledger.events.append("send")
        if self.mode == "unknown":
            raise DeliveryUnknown()
        if self.mode == "timeout":
            await asyncio.sleep(.2)
        if self.mode == "failed":
            return TransportResponse(503, b"{}", 2)
        message = {"role":"assistant", "content":"synthetic-answer-085"}
        finish = "stop"
        if self.mode == "tool":
            finish = "tool_calls"
            message["tool_calls"] = [{"id":"calc", "type":"function", "function":{
                "name":"finite_calculate", "arguments":'{"operation":"add","left":1,"right":2}'}}]
        raw = json.dumps({"model":"synthetic-model", "choices":[{"message":message,"finish_reason":finish}],
                          "usage":{"prompt_tokens":2,"completion_tokens":1,"total_tokens":3}}).encode()
        return TransportResponse(200, raw, len(raw))


class OneCallTests(unittest.IsolatedAsyncioTestCase):
    def test_fixed_worker_idle_and_missing_configuration_fail_closed(self):
        import sys
        from app.worker.worker_main import main
        with patch.object(sys,"argv",["worker_main","idle"]):
            self.assertEqual(main(),0)
        with patch.object(sys,"argv",["worker_main","one_call"]), \
             patch("app.worker.worker_main.PostgresAdmissionLedger",side_effect=AssertionError("implicit fallback")):
            self.assertEqual(main(),2)

    def test_public_rejection_before_launcher_and_bounded_result_roundtrip(self):
        from app.worker.session import SessionOutcome
        from app.worker.launcher import _decode_outcome
        from app.worker.one_call import run_one_call
        value=frame()
        call,ctx=decode_worker_request(value)
        ledger=PostgresAdmissionLedger("synthetic-dsn")
        with patch("app.worker.launcher.run_supervised_window",side_effect=AssertionError("launched")):
            with self.assertRaises(ValueError):
                run_one_call(ledger,SessionConfig(),ctx.activity_id,ctx.executor_id,"op",request(),
                             service(timeout_seconds=20),run_tag="run")
        for result in (
            ModelCallResult(CallStatus.SUCCEEDED,ctx.operation_id,call.service.provider,call.service.model,
                            text="synthetic-answer-085",usage=Usage(2,1,3)),
            ModelCallResult(CallStatus.SUCCEEDED,ctx.operation_id,call.service.provider,call.service.model,
                            json_object={"answer":42},usage=Usage(2,1,3)),
            ModelCallResult(CallStatus.TOOL_PLAN,ctx.operation_id,call.service.provider,call.service.model,
                            tool_plans=(ToolCallPlan("calc","finite_calculate",{"operation":"add","left":1,"right":2}),)),
        ):
            original=receipt(result,ctx,"run")
            raw=pack_frame(original).ljust(SLOT_SIZE,b"\0")
            decoded=decode_receipt(unpack_frame(raw),ctx,"run")
            self.assertEqual(json.loads(json.dumps(asdict(decoded))),json.loads(json.dumps(asdict(result))))
            outcome=SessionOutcome("run","settled",ctx.activity_id,generation=ctx.execution_generation,model_receipt=original)
            self.assertNotIn("synthetic-answer",repr(outcome))
            self.assertNotIn("answer",repr(outcome))
            recovered=_decode_outcome(json.loads(json.dumps({"protocol":2,"run_tag":"run",
                "activity_id":ctx.activity_id,"outcome":asdict(outcome)})),"run",ctx.activity_id)
            self.assertEqual(json.loads(json.dumps(asdict(recovered))),json.loads(json.dumps(asdict(outcome))))

    def test_new_sources_compile_without_pyc(self):
        backend=Path(__file__).resolve().parents[1]
        for path in list((backend/"app/worker").glob("*.py"))+list((backend/"tests/fixtures/task085").glob("*.py")):
            compile(path.read_text(encoding="utf-8"),str(path),"exec")

    def test_mapping_owned_lifetime_and_malformed_json(self):
        from app.worker.supervisor_ipc import NamedMapping
        name="Local\\RetroLume.SUP."+uuid4().hex
        owner=NamedMapping.create(name)
        peer=None
        try:
            owner.write_request({"protocol":2})
            peer=NamedMapping.open_existing(name)
            self.assertEqual(peer.read_request(),{"protocol":2})
            peer.close();peer=None
        finally:
            if peer is not None:peer.close()
            owner.close()
        with self.assertRaises(IpcUnknown):NamedMapping.open_existing(name)
        for body in (b'{"a":1,"a":2}',b'{"a":NaN}'):
            raw=struct.pack("<I",len(body))+hashlib.sha256(body).digest()+body
            with self.assertRaises(IpcUnknown):unpack_frame(raw.ljust(SLOT_SIZE,b"\0"))

    async def test_real_gateway_single_send_claim_context_and_redaction(self):
        value = frame()
        ledger = Ledger()
        transport = Transport(ledger)
        with patch("app.worker.worker_main.PostgresAdmissionLedger", return_value=ledger), \
             patch("app.capabilities.gateway.HttpxModelTransport", return_value=transport):
            result = await execute_one_call(value)
        self.assertEqual(ledger.events, ["admit","mark","send","received"])
        self.assertEqual(transport.calls, 1)
        self.assertEqual((ledger.context.execution_generation,ledger.context.scope_revision), (7,3))
        parsed = decode_receipt(result, ledger.context, "run-085")
        self.assertEqual(parsed.status, CallStatus.SUCCEEDED)
        self.assertNotIn("synthetic-answer", repr(parsed))
        self.assertNotIn("synthetic-body", repr(OneCallInput.from_wire(value["call"])))
        self.assertNotIn("synthetic-secret", repr(OneCallInput.from_wire(value["call"])))
        self.assertEqual(result["business_commit"], "not_committed")

    async def test_unknown_timeout_failure_denial_and_no_operation_retry(self):
        for mode, status in (("unknown",CallStatus.UNKNOWN),("timeout",CallStatus.UNKNOWN),
                             ("failed",CallStatus.FAILED),("denied",CallStatus.REJECTED)):
            with self.subTest(mode=mode):
                ledger = Ledger(denied=mode=="denied")
                transport = Transport(ledger,mode)
                value = frame()
                call, ctx = decode_worker_request(value)
                gateway = ControlledModelGateway(call.service,ledger=ledger,transport=transport)
                result = await run_internal_task(gateway,"one_call",ctx,call.request,call_seconds=.5)
                self.assertEqual(result.status,status)
                second = await run_internal_task(gateway,"one_call",ctx,call.request,call_seconds=.5)
                self.assertEqual(second.status,CallStatus.REJECTED)
                self.assertEqual(transport.calls,0 if mode=="denied" else 1)
                if mode in ("unknown","timeout"):
                    self.assertIn("unknown",ledger.events)
                    self.assertNotIn("not_sent",ledger.events)

    async def test_tool_plan_never_executes(self):
        ledger = Ledger()
        transport = Transport(ledger,"tool")
        value=frame()
        call,ctx=decode_worker_request(value)
        gateway=ControlledModelGateway(call.service,ledger=ledger,transport=transport)
        with patch("app.capabilities.tools.ToolRegistry.execute",side_effect=AssertionError("executed")):
            result=await run_internal_task(gateway,"one_call",ctx,request(allowed_tools={"finite_calculate"}))
        self.assertEqual(result.status,CallStatus.TOOL_PLAN)
        self.assertEqual(transport.calls,1)

    async def test_missing_data_idle_and_actual_short_window(self):
        with self.assertRaises(ValueError):
            await run_internal_task(None,"one_call")
        self.assertIsNone(await run_internal_task(None,"idle"))
        value=frame()
        value["stop_ns"]=time.monotonic_ns()+100_000_000
        with patch("app.worker.worker_main.PostgresAdmissionLedger",side_effect=AssertionError("constructed")):
            with self.assertRaises(ValueError):
                await execute_one_call(value)

    def test_frame_limits_tamper_and_schema(self):
        raw=pack_frame({"x":"a"*(SLOT_SIZE-44)})
        self.assertEqual(len(raw),SLOT_SIZE)
        self.assertEqual(len(unpack_frame(raw)["x"]),SLOT_SIZE-44)
        with self.assertRaises(IpcUnknown): pack_frame({"x":"a"*(SLOT_SIZE-43)})
        with self.assertRaises(IpcUnknown): unpack_frame(raw[:-1]+b"x")
        value=frame()
        value["unexpected"]=True
        with self.assertRaises(ValueError): decode_worker_request(value)
        value=frame()
        value["context"]["operation_id"]="other"
        with self.assertRaises(ValueError): decode_worker_request(value)

    def test_input_bounds_and_fixed_argv(self):
        with self.assertRaises(ValueError): OneCallInput("op",request(),service(max_response_bytes=65537)).to_wire()
        with self.assertRaises(ValueError): OneCallInput("op",request(messages=[{"role":"user","content":"文"*50000}]),service()).to_wire()
        with self.assertRaises(ValueError): WorkerCommand("one_call").argv()
        argv=WorkerCommand("one_call").argv("Local\\RetroLume.SUP."+"a"*32)
        self.assertNotIn("synthetic-secret"," ".join(argv))
        self.assertNotIn("synthetic-body"," ".join(argv))
        for invalid in ("bad\nexecutor","bad executor",""):
            with self.assertRaises(ValueError): validate_identity(str(uuid4()),invalid,"op","run")

    async def test_receipt_wrong_identity_generation_missing_unknown_and_overlimit(self):
        ledger=Ledger()
        call,ctx=decode_worker_request(frame())
        result=await ControlledModelGateway(call.service,ledger=ledger,transport=Transport(ledger)).call(ctx,call.request)
        original=receipt(result,ctx,"run")
        for field,value in (("execution_generation",6),("scope_revision",2),("executor_id","wrong"),("execution_generation",True)):
            item=json.loads(json.dumps(original));item["context"][field]=value
            with self.assertRaises(ValueError): decode_receipt(item,ctx,"run")
        for mutate in (lambda x:x.update(extra=1),lambda x:x["result"].update(extra=1),
                       lambda x:x["result"].pop("status"),lambda x:x["result"].update(text="x"*131073)):
            item=json.loads(json.dumps(original));mutate(item)
            with self.assertRaises(ValueError): decode_receipt(item,ctx,"run")

    def test_sup_protocol_roundtrip_and_missing_configuration(self):
        from app.worker.launcher import _request
        name="Local\\RetroLume.SUP."+"a"*32
        ledger=PostgresAdmissionLedger("synthetic-dsn")
        cfg=SessionConfig()
        call=OneCallInput("op",request(),service())
        value=_request(ledger,cfg,str(uuid4()),"executor",WorkerCommand("one_call"),"run",name,time.monotonic_ns()+10**10,call)
        self.assertEqual(_validated_request(value,name)[-1].operation_id,"op")
        for mutate in (lambda x:x.update(protocol=1),lambda x:x.update(extra=1),lambda x:x.update(one_call=None)):
            item=json.loads(json.dumps(value));mutate(item)
            with self.assertRaises(ValueError): _validated_request(item,name)


if __name__ == "__main__": unittest.main()
