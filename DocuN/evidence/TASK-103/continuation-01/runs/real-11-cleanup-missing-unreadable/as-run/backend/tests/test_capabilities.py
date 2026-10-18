import asyncio
import json
import re
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.capabilities import (
    AdmissionDenied,
    AdmissionPermit,
    AssistantToolCall,
    CallContext,
    CallStatus,
    ControlledModelGateway,
    DeliveryUnknown,
    LedgerDisposition,
    Message,
    ModelCallRequest,
    ModelServiceConfig,
    Provider,
    RecordOutcome,
    RequestNotSent,
    ResponseMode,
    TOOL_NAME,
    ToolRegistry,
    ToolFunctionCall,
    ToolValidationError,
    TransportResponse,
)


SECRET = "secret-that-must-not-leak"

# 固定合成 UUID：替代旧替身样本 "activity-1"（非 UUID，违反真实账本 ID 契约）。
ACTIVITY_UUID = "3f2b8c64-1d4e-4f5a-9b6c-7e8d9a0b1c2d"


def config(**changes):
    values = {
        "provider": Provider.DEEPSEEK_CHAT_COMPLETIONS,
        "base_url": "https://api.deepseek.com",
        "model": "configured-model",
        "api_key": SECRET,
        "timeout_seconds": 3,
        "max_output_tokens_limit": 100,
        "max_request_bytes": 4096,
        "max_response_bytes": 4096,
    }
    values.update(changes)
    return ModelServiceConfig(**values)


def context():
    return CallContext(
        activity_id=ACTIVITY_UUID,
        operation_id="operation-1",
        executor_id="worker-1",
        execution_generation=2,
        scope_revision=3,
    )


def request(**changes):
    values = {
        "messages": (Message(role="user", content="Return JSON."),),
        "max_output_tokens": 40,
        "response_mode": ResponseMode.JSON_OBJECT,
    }
    values.update(changes)
    return ModelCallRequest(**values)


def response_body(*, content='{"answer":42}', finish_reason="stop", tool_calls=None):
    message = {"role": "assistant", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return json.dumps(
        {
            "id": "remote-1",
            "model": "returned-model",
            "choices": [{"index": 0, "finish_reason": finish_reason, "message": message}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14},
        }
    ).encode()


class RecordingLedger:
    def __init__(self, *, deny=False, fail_dispatch=False, fail_record=False):
        self.deny = deny
        self.fail_dispatch = fail_dispatch
        self.fail_record = fail_record
        self.intents = []
        self.dispatches = []
        self.outcomes = []

    async def admit(self, intent):
        self.intents.append(intent)
        if self.deny:
            raise AdmissionDenied("denied")
        return AdmissionPermit("admission-1", intent.context.operation_id, intent.context.executor_id)

    async def mark_dispatch_started(self, permit):
        self.dispatches.append(permit)
        if self.fail_dispatch:
            raise RuntimeError("db unavailable")

    async def record_outcome(self, permit, outcome):
        self.outcomes.append((permit, outcome))
        if self.fail_record:
            raise RuntimeError("db unavailable")
        return RecordOutcome.RECORDED


class FakeTransport:
    def __init__(self, value):
        self.value = value
        self.calls = []

    async def send(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.value, BaseException):
            raise self.value
        return self.value


class SlowStreamingTransport:
    """模拟持续产生小块数据、永远不会触发 IO 空闲超时的 transport。"""

    def __init__(self):
        self.calls = 0

    async def send(self, **kwargs):
        del kwargs
        self.calls += 1
        while True:
            await asyncio.sleep(0.005)


def normal_transport(body=None, **changes):
    values = {
        "status_code": 200,
        "body": response_body() if body is None else body,
        "response_bytes": 200,
        "remote_request_id": "request-1",
    }
    values.update(changes)
    return FakeTransport(TransportResponse(**values))


class CapabilitiesTests(unittest.IsolatedAsyncioTestCase):
    async def test_config_and_default_ledger_fail_closed(self):
        self.assertNotIn(SECRET, repr(config()))
        with self.assertRaises(ValidationError):
            config(base_url="http://127.0.0.1:9999")
        transport = normal_transport()
        result = await ControlledModelGateway(config(), transport=transport).call(context(), request())
        self.assertEqual(CallStatus.REJECTED, result.status)
        self.assertEqual("admission_unavailable", result.error_code)
        self.assertEqual([], transport.calls)

    async def test_structured_success_has_bounded_request_and_sanitized_facts(self):
        ledger, transport = RecordingLedger(), normal_transport()
        result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(context(), request())
        self.assertEqual(CallStatus.SUCCEEDED, result.status)
        self.assertEqual({"answer": 42}, result.json_object)
        self.assertEqual("returned-model", result.returned_model)
        self.assertRegex(result.payload_sha256 or "", r"^[0-9a-f]{64}$")
        self.assertEqual(1, len(transport.calls))
        sent = transport.calls[0]
        self.assertEqual(40, sent["payload"]["max_tokens"])
        self.assertFalse(sent["payload"]["stream"])
        self.assertEqual({"type": "disabled"}, sent["payload"]["thinking"])
        self.assertEqual(3, sent["timeout_seconds"])
        self.assertEqual(1, len(ledger.outcomes))
        facts = repr(ledger.outcomes[0][1])
        self.assertNotIn(SECRET, facts)
        self.assertNotIn("answer", facts)

    async def test_blank_truncated_and_invalid_json_are_rejected_as_received(self):
        examples = [
            (response_body(content="  "), "empty_output"),
            (response_body(content='{"partial":', finish_reason="length"), "truncated_output"),
            (response_body(content="not-json"), "invalid_output_json"),
            (response_body(content='{"value":1e999}'), "invalid_response_json"),
        ]
        for body, error_code in examples:
            with self.subTest(error_code=error_code):
                ledger, transport = RecordingLedger(), normal_transport(body)
                result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(context(), request())
                self.assertEqual(CallStatus.FAILED, result.status)
                self.assertEqual(error_code, result.error_code)
                self.assertEqual(LedgerDisposition.RECEIVED, ledger.outcomes[0][1].disposition)
                self.assertEqual(1, len(transport.calls))

        ledger, transport = RecordingLedger(), normal_transport()
        with patch("app.capabilities.gateway._safe_json_loads", side_effect=RecursionError):
            recursive = await ControlledModelGateway(
                config(), ledger=ledger, transport=transport
            ).call(context(), request())
        self.assertEqual(CallStatus.FAILED, recursive.status)
        self.assertEqual("invalid_response_json", recursive.error_code)
        self.assertEqual(LedgerDisposition.RECEIVED, ledger.outcomes[0][1].disposition)

    async def test_transport_not_sent_and_unknown_are_distinct_and_never_retried(self):
        examples = [
            (RequestNotSent("no connection"), CallStatus.NOT_SENT, LedgerDisposition.NOT_SENT),
            (DeliveryUnknown("read timeout"), CallStatus.UNKNOWN, LedgerDisposition.UNKNOWN),
        ]
        for failure, status, disposition in examples:
            with self.subTest(status=status):
                ledger, transport = RecordingLedger(), FakeTransport(failure)
                result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(context(), request())
                self.assertEqual(status, result.status)
                self.assertEqual(disposition, ledger.outcomes[0][1].disposition)
                self.assertEqual(1, len(transport.calls))

    async def test_absolute_deadline_stops_continuous_slow_stream_as_unknown(self):
        ledger, transport = RecordingLedger(), SlowStreamingTransport()
        gateway = ControlledModelGateway(
            config(timeout_seconds=0.03), ledger=ledger, transport=transport
        )
        result = await gateway.call(context(), request())
        self.assertEqual(CallStatus.UNKNOWN, result.status)
        self.assertEqual("deadline_exceeded", result.error_code)
        self.assertEqual(1, transport.calls)
        self.assertEqual(LedgerDisposition.UNKNOWN, ledger.outcomes[0][1].disposition)

    async def test_dispatch_or_admission_failure_prevents_network(self):
        for ledger, error_code in (
            (RecordingLedger(deny=True), "admission_denied"),
            (RecordingLedger(fail_dispatch=True), "admission_internal_error"),
        ):
            with self.subTest(error_code=error_code):
                transport = normal_transport()
                result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(context(), request())
                self.assertEqual(CallStatus.REJECTED, result.status)
                self.assertEqual(error_code, result.error_code)
                self.assertEqual([], transport.calls)

    def test_call_context_rejects_ids_violating_ledger_contract(self):
        base = {
            "operation_id": "operation-1",
            "executor_id": "worker-1",
            "execution_generation": 2,
            "scope_revision": 3,
        }
        bad_activity_ids = [
            "activity-1",
            "",
            "  ",
            "活动一",
            "3f2b8c64-1d4e-4f5a-9b6c-7e8d9a0b1c2",  # 缺一位的伪 UUID
        ]
        for activity_id in bad_activity_ids:
            with self.subTest(activity_id=activity_id):
                with self.assertRaises(ValidationError):
                    CallContext(activity_id=activity_id, **base)
        bad_names = ["", " ", "操作一", "op id", "op#1"]
        for field in ("operation_id", "executor_id"):
            for name in bad_names:
                with self.subTest(field=field, name=name):
                    with self.assertRaises(ValidationError):
                        CallContext(activity_id=ACTIVITY_UUID, **{**base, field: name})
        # 有效 UUID 与合法 operation/executor 保持通过。
        self.assertEqual(ACTIVITY_UUID, context().activity_id)

    async def test_unexpected_admission_errors_are_distinguishable_and_sanitized(self):
        async def broken_admit(intent):
            del intent
            raise RuntimeError(f"admit exploded with {SECRET}")

        ledger, transport = RecordingLedger(), normal_transport()
        ledger.admit = broken_admit
        with self.assertLogs("app.capabilities.gateway", level="WARNING") as captured:
            result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(context(), request())
        self.assertEqual(CallStatus.REJECTED, result.status)
        self.assertEqual("admission_internal_error", result.error_code)
        self.assertEqual([], transport.calls)
        first_log = "\n".join(captured.output)
        self.assertIn("admission_internal_error", first_log)
        self.assertIn("stage=admit", first_log)
        self.assertIn("exception_type=RuntimeError", first_log)
        self.assertNotIn(SECRET, first_log)

        async def broken_mark(permit):
            del permit
            raise RuntimeError(f"mark exploded with {SECRET}")

        ledger2, transport2 = RecordingLedger(), normal_transport()
        ledger2.mark_dispatch_started = broken_mark
        with self.assertLogs("app.capabilities.gateway", level="WARNING") as captured2:
            result2 = await ControlledModelGateway(config(), ledger=ledger2, transport=transport2).call(context(), request())
        self.assertEqual(CallStatus.REJECTED, result2.status)
        self.assertEqual("admission_internal_error", result2.error_code)
        self.assertEqual([], transport2.calls)
        second_log = "\n".join(captured2.output)
        self.assertIn("stage=mark_dispatch", second_log)
        self.assertIn("exception_type=RuntimeError", second_log)
        self.assertNotIn(SECRET, second_log)
        correlation_ids = re.findall(r"correlation_id=([0-9a-f]{32})", first_log + "\n" + second_log)
        self.assertEqual(2, len(correlation_ids))
        self.assertNotEqual(correlation_ids[0], correlation_ids[1])

    async def test_ledger_record_failure_makes_apparent_success_unknown(self):
        ledger, transport = RecordingLedger(fail_record=True), normal_transport()
        result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(context(), request())
        self.assertEqual(CallStatus.UNKNOWN, result.status)
        self.assertEqual("record_unconfirmed", result.error_code)

    async def test_tool_suggestion_is_validated_and_only_returns_plan(self):
        tool_calls = [{
            "id": "call-1",
            "type": "function",
            "function": {"name": TOOL_NAME, "arguments": '{"operation":"divide","left":6,"right":2}'},
        }]
        ledger, transport = RecordingLedger(), normal_transport(
            response_body(content=None, finish_reason="tool_calls", tool_calls=tool_calls)
        )
        result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(
            context(), request(allowed_tools=frozenset({TOOL_NAME}))
        )
        self.assertEqual(CallStatus.TOOL_PLAN, result.status)
        tool_result = ToolRegistry().execute(result.tool_plans[0])
        self.assertEqual("3", tool_result)
        self.assertEqual(1, len(transport.calls))

        followup_transport = normal_transport(response_body(content='{"answer":3}'))
        followup = request(
            allowed_tools=frozenset({TOOL_NAME}),
            messages=(
                Message(role="user", content="Calculate 6 / 2."),
                Message(
                    role="assistant",
                    tool_calls=(
                        AssistantToolCall(
                            id="call-1",
                            function=ToolFunctionCall(
                                name=TOOL_NAME,
                                arguments='{"operation":"divide","left":6,"right":2}',
                            ),
                        ),
                    ),
                ),
                Message(role="tool", tool_call_id="call-1", content=tool_result),
            ),
        )
        completed = await ControlledModelGateway(
            config(), ledger=RecordingLedger(), transport=followup_transport
        ).call(context(), followup)
        self.assertEqual(CallStatus.SUCCEEDED, completed.status)
        sent_messages = followup_transport.calls[0]["payload"]["messages"]
        self.assertEqual("call-1", sent_messages[1]["tool_calls"][0]["id"])
        self.assertEqual("call-1", sent_messages[2]["tool_call_id"])

    async def test_unknown_unauthorized_and_extra_tool_fields_are_rejected(self):
        examples = [
            ("unknown_tool", '{"operation":"add","left":1,"right":2}', frozenset({TOOL_NAME})),
            (TOOL_NAME, '{"operation":"add","left":1,"right":2}', frozenset()),
            (TOOL_NAME, '{"operation":"add","left":1,"right":2,"extra":3}', frozenset({TOOL_NAME})),
        ]
        for name, arguments, allowed in examples:
            with self.subTest(name=name, allowed=allowed):
                calls = [{"id": "c", "type": "function", "function": {"name": name, "arguments": arguments}}]
                ledger, transport = RecordingLedger(), normal_transport(
                    response_body(content=None, finish_reason="tool_calls", tool_calls=calls)
                )
                result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(
                    context(), request(allowed_tools=allowed)
                )
                self.assertEqual(CallStatus.FAILED, result.status)
                self.assertEqual("invalid_tool_calls", result.error_code)

        ledger, transport = RecordingLedger(), normal_transport()
        orphan = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(
            context(),
            request(messages=(Message(role="tool", tool_call_id="orphan", content="3"),)),
        )
        self.assertEqual(CallStatus.REJECTED, orphan.status)
        self.assertEqual("invalid_request", orphan.error_code)
        self.assertEqual([], transport.calls)

        with patch("app.capabilities.tools.json.loads", side_effect=RecursionError):
            with self.assertRaises(ToolValidationError):
                ToolRegistry().plan(
                    "deep",
                    TOOL_NAME,
                    '{"operation":"add","left":1,"right":2}',
                    frozenset({TOOL_NAME}),
                )

    def test_calculator_rejects_nonfinite_and_resource_abuse(self):
        registry = ToolRegistry()
        oversized = registry.plan("c", TOOL_NAME, '{"operation":"power","left":1000000000000,"right":12}', frozenset({TOOL_NAME}))
        with self.assertRaises(ToolValidationError):
            registry.execute(oversized)
        with self.assertRaises(ToolValidationError):
            registry.plan("c", TOOL_NAME, '{"operation":"add","left":1e999,"right":2}', frozenset({TOOL_NAME}))
        plan = registry.plan("c", TOOL_NAME, '{"operation":"divide","left":1,"right":3}', frozenset({TOOL_NAME}))
        self.assertEqual("0.33333333333333333333333333333333333333333333333333", registry.execute(plan))

    async def test_response_size_and_http_failure_are_received_without_body_echo(self):
        examples = [
            (normal_transport(b"private", body_too_large=True, response_bytes=5000), "response_too_large"),
            (normal_transport(b"private", status_code=402), "remote_http_402"),
        ]
        for transport, error_code in examples:
            with self.subTest(error_code=error_code):
                ledger = RecordingLedger()
                result = await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(context(), request())
                self.assertEqual(CallStatus.FAILED, result.status)
                self.assertEqual(error_code, result.error_code)
                self.assertNotIn("private", repr(result))

    async def test_cancellation_is_recorded_unknown_then_propagated(self):
        ledger, transport = RecordingLedger(), FakeTransport(asyncio.CancelledError())
        with self.assertRaises(asyncio.CancelledError):
            await ControlledModelGateway(config(), ledger=ledger, transport=transport).call(context(), request())
        self.assertEqual(LedgerDisposition.UNKNOWN, ledger.outcomes[0][1].disposition)
        self.assertEqual("cancelled", ledger.outcomes[0][1].error_code)

    async def test_request_limits_reject_before_admission(self):
        ledger, transport = RecordingLedger(), normal_transport()
        gateway = ControlledModelGateway(config(max_request_bytes=1024), ledger=ledger, transport=transport)
        too_many_tokens = await gateway.call(context(), request(max_output_tokens=101))
        too_much_context = await gateway.call(
            context(),
            request(messages=(Message(role="user", content="x" * 2000),)),
        )
        self.assertEqual("output_token_limit", too_many_tokens.error_code)
        self.assertEqual("context_limit", too_much_context.error_code)
        self.assertEqual([], ledger.intents)
        self.assertEqual([], transport.calls)


if __name__ == "__main__":
    unittest.main()
