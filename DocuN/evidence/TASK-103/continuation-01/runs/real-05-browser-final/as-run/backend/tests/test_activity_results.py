"""TASK-088 G3 业务正文原子提交与受控恢复读取：离线合同与真实 PG 定向验证。

离线部分不访问网络/数据库；PG 部分仅在存在专用测试 DSN
（RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL）时运行，不回退任何用户库。
每例注册本例创建的活动/来源/版本 ID，清理只定向删除本例行，先 results
子表再旧 FK 链。测试数据全合成；transport 为测试替身，不冒充真实供应商。
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from app.activities import (
    ActivityLease,
    ActivityLedgerConflict,
    ActivitySpec,
    CommittedResultSnapshot,
    PostgresAdmissionLedger,
    ResultIntegrityError,
    ResultReadStatus,
    SettleResult,
    SourceSnapshot,
)
from app.capabilities import (
    BUSINESS_PAYLOAD_MAX_BYTES,
    AdmissionDenied,
    AdmissionIntent,
    AdmissionPermit,
    AdmissionUnavailable,
    CallContext,
    CallStatus,
    LedgerDisposition,
    LedgerOutcome,
    Message,
    ModelCallRequest,
    ModelServiceConfig,
    Provider,
    RecordOutcome,
    ResponseMode,
    TransportResponse,
    Usage,
    build_business_payload,
    canonical_payload_bytes,
    payload_digest,
    validate_business_payload,
)
from app.capabilities.gateway import ControlledModelGateway
from app.worker.one_call import OneCallInput, decode_receipt, receipt, run_one_call
from app.worker.session import SessionConfig, SingleWindowSupervisor
from app.worker.command import WorkerCommand
from app.runtime import psycopg_compatible_loop_factory

DSN = os.environ.get("RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL", "")
MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


class PsycopgLoopIsolatedAsyncioTestCase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self) -> None:
        assert self._asyncioRunner is None
        self._asyncioRunner = asyncio.Runner(
            debug=True,
            loop_factory=psycopg_compatible_loop_factory,
        )


# ---------------------------------------------------------------------------
# A. 离线：封套规范化与字节边界
# ---------------------------------------------------------------------------


class PayloadEnvelopeOfflineTests(unittest.TestCase):
    def test_canonical_stable_same_object_and_digest(self):
        envelope = {"format": "json", "value": {"b": [1, 2.5, None], "a": "文"}}
        first = canonical_payload_bytes(envelope)
        second = canonical_payload_bytes(envelope)
        self.assertEqual(first, second)
        self.assertEqual(payload_digest(envelope), hashlib.sha256(first).hexdigest())
        self.assertRegex(payload_digest(envelope), r"^[0-9a-f]{64}$")
        # 键序差异产生不同规范字节（字节等值，不承诺 JSON 语义等价）。
        reordered = {"value": {"a": "文", "b": [1, 2.5, None]}, "format": "json"}
        self.assertNotEqual(canonical_payload_bytes(reordered), first)
        # int 与 float 产生不同规范字节。
        self.assertNotEqual(
            canonical_payload_bytes({"format": "json", "value": {"n": 1}}),
            canonical_payload_bytes({"format": "json", "value": {"n": 1.0}}),
        )

    def test_legal_text_and_json_and_actual_byte_boundary(self):
        for payload_format, value in (("text", "plain-正文"), ("json", {"k": [True, None, -3]})):
            triple = (
                build_business_payload(text=value) if payload_format == "text"
                else build_business_payload(json_object=value)
            )
            fmt, text, sha = triple
            self.assertEqual(fmt, payload_format)
            self.assertEqual(validate_business_payload(text, fmt, sha), triple)
            self.assertLessEqual(len(text.encode("utf-8")), BUSINESS_PAYLOAD_MAX_BYTES)
        # 精确字节边界：envelope 恰为 131072 字节通过；多 1 字节拒绝。
        overhead = len('{"format":"text","value":""}'.encode("utf-8"))
        exact = "x" * (BUSINESS_PAYLOAD_MAX_BYTES - overhead)
        fmt, text, sha = build_business_payload(text=exact)
        self.assertEqual(len(text.encode("utf-8")), BUSINESS_PAYLOAD_MAX_BYTES)
        self.assertEqual(validate_business_payload(text, fmt, sha), (fmt, text, sha))
        with self.assertRaises(ValueError):
            build_business_payload(text=exact + "x")
        # 超 128KiB 非法样本在 helper 层直接合成，非供应商真实样本。
        big_json = {"k": "y" * (BUSINESS_PAYLOAD_MAX_BYTES - 30)}
        with self.assertRaises(ValueError):
            build_business_payload(json_object=big_json)

    def test_outcome_payload_only_with_received_and_all_or_nothing(self):
        """T03：仓储应用层 _payload_values 校验（不入库的应用侧拒绝）。"""
        from app.activities.repository import PostgresAdmissionLedger as _Ledger
        fmt, payload, sha = build_business_payload(text="t03")
        # 合法：RECEIVED + 三字段齐全。
        ok = LedgerOutcome(LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha)
        self.assertEqual((fmt, payload, sha), _Ledger._payload_values(ok))
        # 三字段同存同缺。
        for fields in (
            {"payload_format": fmt},
            {"payload": payload},
            {"payload_sha256": sha},
            {"payload_format": fmt, "payload": payload},
            {"payload": payload, "payload_sha256": sha},
        ):
            with self.subTest(fields=sorted(fields)):
                with self.assertRaises(AdmissionDenied):
                    _Ledger._payload_values(LedgerOutcome(LedgerDisposition.RECEIVED, **fields))
        # payload 仅随 RECEIVED：NOT_SENT/UNKNOWN 携带正文拒绝。
        for disposition in (LedgerDisposition.NOT_SENT, LedgerDisposition.UNKNOWN):
            with self.subTest(disposition=disposition):
                with self.assertRaises(AdmissionDenied):
                    _Ledger._payload_values(
                        LedgerOutcome(disposition, payload_format=fmt, payload=payload, payload_sha256=sha)
                    )
        # 伪 hash（regex 合法但字节不符）应用侧即拒。
        with self.assertRaises(AdmissionDenied):
            _Ledger._payload_values(
                LedgerOutcome(LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload,
                              payload_sha256=hashlib.sha256(b"fake").hexdigest())
            )

    def test_invalid_type_nonfinite_depth_nodes_fake_hash_noncanonical(self):
        fmt, text, sha = build_business_payload(text="sample")
        cases = [
            lambda: validate_business_payload(text, "yaml", sha),          # 非法 format
            lambda: validate_business_payload(text, fmt, "z" * 64),        # 伪 hash 字符
            lambda: validate_business_payload(text, fmt, sha.upper()),     # 非小写
            lambda: validate_business_payload(text, fmt, hashlib.sha256(b"other").hexdigest()),  # hash 不匹配
            lambda: validate_business_payload(" " + text, fmt, sha),       # 非规范字节
            lambda: validate_business_payload('{"format":"text","value":""}', "text", sha),  # 空 text
            lambda: validate_business_payload('{"format":"json","value":[]}', "json", sha),  # 非 dict value
            lambda: validate_business_payload('{"format":"text","value":"x","extra":1}', "text", sha),  # 封套多键
            lambda: validate_business_payload('{"value":"x"}', "text", sha),  # 封套缺键
            lambda: build_business_payload(json_object={"n": float("nan")}),   # 非有限
            lambda: build_business_payload(json_object={"n": float("inf")}),   # 非有限
        ]
        for index, case in enumerate(cases):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    case()
        # 深度 12 / 节点 2000 限制（与 gateway 成功解析不变式同界）。
        deep = value = {}
        for _ in range(13):
            value["k"] = {}
            value = value["k"]
        with self.assertRaises(ValueError):
            build_business_payload(json_object=deep)
        wide = {f"k{i}": i for i in range(2001)}
        with self.assertRaises(ValueError):
            build_business_payload(json_object=wide)
        # 重复键按解析后后值覆盖；覆盖后字节与封套一致则通过（沿用既有解析行为）。
        duplicate = '{"format":"text","value":"a","value":"b"}'
        digest = hashlib.sha256(canonical_payload_bytes({"format": "text", "value": "b"})).hexdigest()
        with self.assertRaises(ValueError):
            # 规范字节（解析后）与原文不同 → 非规范，拒绝；不另行承诺重复键拒绝。
            validate_business_payload(duplicate, "text", digest)


# ---------------------------------------------------------------------------
# A. 离线：gateway 提交确认三分类与协议 3 配对
# ---------------------------------------------------------------------------


def _config(**changes):
    values = {
        "provider": Provider.DEEPSEEK_CHAT_COMPLETIONS,
        "base_url": "https://api.deepseek.com",
        "model": "synthetic-model",
        "api_key": "synthetic-secret-088",
        "timeout_seconds": 3,
        "max_output_tokens_limit": 100,
        "max_request_bytes": 1_048_576,
        "max_response_bytes": 1_048_576,
    }
    values.update(changes)
    return ModelServiceConfig(**values)


def _context():
    return CallContext(
        activity_id="3f2b8c64-1d4e-4f5a-9b6c-7e8d9a0b1c2d",
        operation_id="operation-088",
        executor_id="worker-088",
        execution_generation=2,
        scope_revision=3,
    )


def _request(**changes):
    values = {
        "messages": (Message(role="user", content="Return JSON."),),
        "max_output_tokens": 40,
        "response_mode": ResponseMode.JSON_OBJECT,
    }
    values.update(changes)
    return ModelCallRequest(**values)


def _body(content='{"answer":42}', finish_reason="stop"):
    return json.dumps({
        "model": "synthetic-model",
        "choices": [{"index": 0, "finish_reason": finish_reason, "message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14},
    }).encode()


class _ConfirmLedger:
    def __init__(self, behavior="recorded"):
        self.behavior = behavior
        self.outcomes = []

    async def admit(self, intent):
        return AdmissionPermit("admission-088", intent.context.operation_id, intent.context.executor_id)

    async def mark_dispatch_started(self, permit):
        pass

    async def record_outcome(self, permit, outcome):
        self.outcomes.append(outcome)
        if self.behavior == "recorded":
            return RecordOutcome.RECORDED
        if self.behavior == "already_present":
            return RecordOutcome.ALREADY_PRESENT
        if self.behavior == "none":
            return None
        if self.behavior == "wrong_type":
            return "recorded"
        if self.behavior == "denied":
            raise AdmissionDenied("terminal conflict")
        if self.behavior == "unavailable":
            raise AdmissionUnavailable("db down")
        raise RuntimeError("unexpected")


class _Transport:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    async def send(self, **kwargs):
        del kwargs
        self.calls += 1
        return self.value


def _transport(body=None):
    return _Transport(TransportResponse(200, body if body is not None else _body(), 200, "request-088"))


class GatewayCommitConfirmationOfflineTests(unittest.IsolatedAsyncioTestCase):
    async def test_recorded_and_already_present_carry_hash_to_actual_result(self):
        for behavior in ("recorded", "already_present"):
            with self.subTest(behavior=behavior):
                ledger, transport = _ConfirmLedger(behavior), _transport()
                result = await ControlledModelGateway(_config(), ledger=ledger, transport=transport).call(_context(), _request())
                self.assertEqual(CallStatus.SUCCEEDED, result.status)
                self.assertRegex(result.payload_sha256 or "", r"^[0-9a-f]{64}$")
                self.assertEqual({"answer": 42}, result.json_object)
                outcome = ledger.outcomes[0]
                self.assertEqual("json", outcome.payload_format)
                self.assertEqual(result.payload_sha256, outcome.payload_sha256)
                self.assertNotIn("answer", repr(outcome))
                self.assertNotIn("synthetic-secret-088", repr(outcome))

    async def test_none_wrong_enum_denied_and_exceptions_map_to_unknown(self):
        cases = (
            ("none", "record_unconfirmed"),
            ("wrong_type", "record_unconfirmed"),
            ("denied", "record_denied"),
            ("unavailable", "record_unconfirmed"),
            ("raise", "record_unconfirmed"),
        )
        for behavior, error_code in cases:
            with self.subTest(behavior=behavior):
                ledger, transport = _ConfirmLedger(behavior), _transport()
                result = await ControlledModelGateway(_config(), ledger=ledger, transport=transport).call(_context(), _request())
                self.assertEqual(CallStatus.UNKNOWN, result.status)
                self.assertEqual(error_code, result.error_code)
                self.assertIsNone(result.payload_sha256)
                self.assertIsNone(result.json_object)
                # 无自动重发。
                self.assertEqual(1, transport.calls)

    async def test_tool_plan_and_failure_never_fake_payload_success(self):
        tool_body = _body(None, "tool_calls")
        data = json.loads(tool_body)
        data["choices"][0]["message"]["tool_calls"] = [{
            "id": "c1", "type": "function",
            "function": {"name": "finite_calculate", "arguments": '{"operation":"add","left":1,"right":2}'},
        }]
        ledger = _ConfirmLedger()
        transport = _transport(json.dumps(data).encode())
        result = await ControlledModelGateway(_config(), ledger=ledger, transport=transport).call(
            _context(), _request(allowed_tools=frozenset({"finite_calculate"}))
        )
        self.assertEqual(CallStatus.TOOL_PLAN, result.status)
        self.assertIsNone(result.payload_sha256)
        self.assertEqual(1, len(result.tool_plans))
        outcome = ledger.outcomes[0]
        self.assertIsNone(outcome.payload)
        self.assertIsNone(outcome.payload_format)
        self.assertIsNone(outcome.payload_sha256)

    async def test_payload_over_limit_is_received_failure_without_payload(self):
        overhead = len('{"format":"text","value":""}'.encode("utf-8"))
        content = "x" * (BUSINESS_PAYLOAD_MAX_BYTES - overhead + 1)
        ledger = _ConfirmLedger()
        result = await ControlledModelGateway(_config(), ledger=ledger, transport=_transport(_body(content))).call(
            _context(), _request(response_mode=ResponseMode.TEXT)
        )
        self.assertEqual(CallStatus.FAILED, result.status)
        self.assertEqual("payload_limit", result.error_code)
        outcome = ledger.outcomes[0]
        self.assertEqual(LedgerDisposition.RECEIVED, outcome.disposition)
        self.assertIsNone(outcome.payload)


class ResultPageBudgetOfflineTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_list_serializer_rejects_oversized_projected_page(self):
        # 仅替换数据库取行；执行实际list编码/预算分支。不是PG资格/查询动态证据。
        # 多字节元数据在SQL VARCHAR字符限制内，但不声称生产provider会产生它。
        activity_id, admission_id = str(uuid4()), str(uuid4())
        row = dict(activity_id=activity_id, operation_id="op", state="received", disposition="received",
                   result_admission_id=admission_id, op_admission_id=admission_id,
                   result_generation=1, op_generation=1, result_scope=1, op_scope=1,
                   provider="p" * 64, configured_model="m" * 128, finish_reason="f" * 64,
                   returned_model="m" * 128, remote_request_id="r" * 128,
                   prompt_tokens=1, completion_tokens=1, response_bytes=1,
                   payload_format="text", payload_sha256="a" * 64,
                   kind="model", tool_call_id=None, arguments_sha256=None, tool_names=[],
                   payload=None,
                   committed_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
                   activity_status_now="pending", activity_scope_revision_now=1,
                   binding_consistent=True, scope_current=True, sources_valid=True)
        rows = [dict(row, operation_id=f"{i:03d}-" + "x" * 124) for i in range(200)]
        class ProjectedRows:
            async def execute(self, sql, params):
                self.limit = params[-1]
                return self
            async def fetchall(self): return rows[:self.limit]
        connection = ProjectedRows()
        ledger = PostgresAdmissionLedger("unused-synthetic")
        async def transaction(operation): return await operation(connection)
        with patch.object(ledger, "_transaction", transaction):
            self.assertEqual(200, len(await ledger.list_committed_results(activity_id, limit=200)))
            for item in rows:
                item["configured_model"] = "模" * 128
                item["returned_model"] = "模" * 128
            self.assertEqual(100, len(await ledger.list_committed_results(activity_id, limit=100)))
            with self.assertRaisesRegex(ValueError, "256KiB"):
                await ledger.list_committed_results(activity_id, limit=200)


class ProtocolThreeOfflineTests(unittest.IsolatedAsyncioTestCase):
    async def _succeeded(self, behavior="recorded"):
        ledger = _ConfirmLedger(behavior)
        result = await ControlledModelGateway(_config(), ledger=ledger, transport=_transport()).call(_context(), _request())
        return result

    async def test_legal_pairings_and_stripped_payload(self):
        succeeded = await self._succeeded()
        frame = receipt(succeeded, _context(), "run-088")
        self.assertEqual(3, frame["protocol"])
        self.assertEqual("committed", frame["business_commit"])
        self.assertIsNone(frame["result"]["text"])
        self.assertIsNone(frame["result"]["json_object"])
        decoded = decode_receipt(frame, _context(), "run-088")
        self.assertEqual(succeeded.payload_sha256, decoded.payload_sha256)
        # succeeded 缺 hash 属内部错误即拒。
        from dataclasses import replace as dc_replace
        with self.assertRaises(ValueError):
            receipt(dc_replace(succeeded, payload_sha256=None), _context(), "run-088")
        # record阶段拒绝和异常均未确认，不能据此否认历史正文。
        for behavior, commit in (("unavailable", "unconfirmed"),):
            failed = await self._succeeded(behavior)
            self.assertEqual(CallStatus.UNKNOWN, failed.status)
            frame2 = receipt(failed, _context(), "run-088")
            self.assertEqual(commit, frame2["business_commit"])
            decode_receipt(frame2, _context(), "run-088")
        for behavior, commit in (("denied", "unconfirmed"),):
            failed = await self._succeeded(behavior)
            frame3 = receipt(failed, _context(), "run-088")
            self.assertEqual(commit, frame3["business_commit"])
            decode_receipt(frame3, _context(), "run-088")

    async def test_status_error_commit_truth_table_at_each_decoder(self):
        from dataclasses import asdict, replace
        from app.worker.launcher import _decode_outcome
        from app.worker.session import SessionOutcome
        base = await self._succeeded("denied")
        for status, error, expected in (
            (CallStatus.UNKNOWN, "record_denied", "unconfirmed"),
            (CallStatus.UNKNOWN, "record_unconfirmed", "unconfirmed"),
            (CallStatus.UNKNOWN, "delivery_unknown", "not_committed"),
            (CallStatus.UNKNOWN, None, "not_committed"),
            (CallStatus.FAILED, "invalid_payload", "not_committed"),
            (CallStatus.REJECTED, "admission_denied", "not_committed"),
            (CallStatus.NOT_SENT, "not_sent", "not_committed"),
        ):
            with self.subTest(status=status, error=error):
                result = replace(base, status=status, error_code=error)
                good = receipt(result, _context(), "run-089")
                self.assertEqual(expected, good["business_commit"])
                for commit in ("committed", "unconfirmed", "not_committed"):
                    item = json.loads(json.dumps(good))
                    item["business_commit"] = commit
                    data = asdict(SessionOutcome("run-089", "settled", _context().activity_id,
                                generation=2, model_receipt=item))
                    # 外2精确旧字段集：排除新tool_receipt（TASK-092）。
                    data.pop("tool_receipt")
                    outer = {"protocol": 2, "run_tag": "run-089", "activity_id": _context().activity_id,
                             "outcome": data}
                    recovered = _decode_outcome(json.loads(json.dumps(outer)), "run-089", _context().activity_id)
                    if commit == expected:
                        decode_receipt(item, _context(), "run-089")
                        decode_receipt(recovered.model_receipt, _context(), "run-089")
                    else:
                        with self.assertRaises(ValueError): decode_receipt(item, _context(), "run-089")
                        with self.assertRaises(ValueError): decode_receipt(recovered.model_receipt, _context(), "run-089")
        for status in (CallStatus.FAILED, CallStatus.REJECTED, CallStatus.NOT_SENT):
            with self.assertRaises(ValueError):
                receipt(replace(base, status=status), _context(), "run-089")
            bad = receipt(base, _context(), "run-089")
            bad["result"]["status"] = status.value
            bad["business_commit"] = "not_committed"
            with self.assertRaises(ValueError): decode_receipt(bad, _context(), "run-089")

    async def test_mixed_version_identity_hash_and_smuggled_payload_rejected(self):
        succeeded = await self._succeeded()
        frame = json.loads(json.dumps(receipt(succeeded, _context(), "run-088")))
        mutations = (
            lambda item: item.update(protocol=2),                      # 混版
            lambda item: item["context"].update(executor_id="other"),  # 身份
            lambda item: item.update(business_commit="not_committed"), # succeeded 必须 committed
            lambda item: item["result"].update(payload_sha256="Z" * 64),  # 非法 hash
            lambda item: item["result"].update(text="smuggled"),       # 夹带正文
            lambda item: item["result"].update(payload_sha256=None),   # 缺 hash
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                item = json.loads(json.dumps(frame))
                mutate(item)
                with self.assertRaises(ValueError):
                    decode_receipt(item, _context(), "run-088")
        # committed 不能出现在非 succeeded 回执。
        failed = await self._succeeded("denied")
        item = json.loads(json.dumps(receipt(failed, _context(), "run-088")))
        item["business_commit"] = "committed"
        with self.assertRaises(ValueError):
            decode_receipt(item, _context(), "run-088")

    async def test_n1_early_rejection_before_claim(self):
        config = SessionConfig(window_seconds=200, request_timeout_seconds=121.0)
        ledger = PostgresAdmissionLedger("synthetic-dsn")
        # one_call 内部合同要求配置 body ≤64KiB；用合规 service 隔离 N1 断言。
        service = _config(max_request_bytes=4096, max_response_bytes=4096, timeout_seconds=2.0)
        with patch("app.worker.launcher.run_supervised_window", side_effect=AssertionError("launched")):
            with self.assertRaises(ValueError) as raised:
                run_one_call(ledger, config, _context().activity_id, _context().executor_id,
                             "op-088", _request(), service, run_tag="run-088")
        self.assertIn("120", str(raised.exception))

        class _NoopLedger:
            def __init__(self):
                self.events = []

        supervisor = SingleWindowSupervisor(_NoopLedger(), config)
        call = OneCallInput("op-088", _request(), service)
        with self.assertRaises(ValueError) as raised2:
            await supervisor.run_once(
                _context().activity_id, _context().executor_id, WorkerCommand("one_call"),
                run_tag="run-088", manager_deadline_ns=time.monotonic_ns() + 60_000_000_000,
                one_call=call,
            )
        self.assertIn("120", str(raised2.exception))
        # idle 配置域不收紧：N1 检查仅在 one_call 分支内；idle 越过该检查后因
        # 替身无 inspect_window 失败（patch 掉真实 OS 资源，离线不建互斥体）。
        class _Owner:
            def __init__(self, *args, **kwargs):
                pass

            def close(self):
                pass

        idle_supervisor = SingleWindowSupervisor(_NoopLedger(), config)
        with patch("app.worker.session.current_process_session_id", return_value=1), \
             patch("app.worker.session.ActivityMutex", _Owner):
            outcome = await idle_supervisor.run_once(
                _context().activity_id, _context().executor_id, WorkerCommand("idle"),
                run_tag="run-088", manager_deadline_ns=time.monotonic_ns() + 60_000_000_000,
            )
        # run_once 捕获业务异常为 failed_closed；idle 越过 N1 检查推进到
        # inspect_window（替身缺失该方法）证明 N1 未收紧 idle 域。
        self.assertEqual("failed_closed", outcome.state)
        self.assertEqual("AttributeError", outcome.error_type)


# ---------------------------------------------------------------------------
# B. 真实 PG：迁移、原子提交、幂等、竞争、恢复读取
# ---------------------------------------------------------------------------


@unittest.skipUnless(DSN, "仅在 TASK-088 专用合成 PostgreSQL 中运行")
class ActivityResultsPostgresTests(PsycopgLoopIsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        import psycopg
        self.ledger = PostgresAdmissionLedger(DSN)
        self.activity_id = str(uuid4())
        self.source_id = str(uuid4())
        self.version_id = str(uuid4())
        self.extra_activity_ids: list[str] = []
        self.extra_source_ids: list[str] = []
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute(
                    "INSERT INTO material_sources(id, title, revision) VALUES (%s, 'synthetic-088', 0)",
                    (self.source_id,),
                )
                await connection.execute(
                    """INSERT INTO material_versions(id, source_id, filename, format, sha256, size)
                         VALUES (%s, %s, 'synthetic-088.txt', 'txt', %s, 9)""",
                    (self.version_id, self.source_id, "a" * 64),
                )
                await connection.execute(
                    "UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s",
                    (self.version_id, self.source_id),
                )

    async def asyncTearDown(self) -> None:
        import psycopg
        activity_ids = [self.activity_id, *self.extra_activity_ids]
        source_ids = [(self.source_id, self.version_id), *self.extra_source_ids]
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                for activity_id in activity_ids:
                    for sql in (
                        "DELETE FROM activity_operation_results WHERE activity_id = %s",
                        "DELETE FROM activity_operations WHERE activity_id = %s",
                        "DELETE FROM activity_allowed_models WHERE activity_id = %s",
                        "DELETE FROM activity_scope_sources WHERE activity_id = %s",
                        "DELETE FROM activities WHERE id = %s",
                    ):
                        await connection.execute(sql, (activity_id,))
                for source_id, version_id in source_ids:
                    await connection.execute(
                        "UPDATE material_sources SET current_version = NULL WHERE id = %s",
                        (source_id,),
                    )
                    await connection.execute("DELETE FROM material_versions WHERE source_id = %s", (source_id,))
                    await connection.execute("DELETE FROM material_sources WHERE id = %s", (source_id,))

    async def db_rows(self, sql, params=()):
        import psycopg
        from psycopg.rows import dict_row
        async with await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row) as connection:
            cursor = await connection.execute(sql, params)
            return list(await cursor.fetchall())

    async def db_row(self, sql, params=()):
        rows = await self.db_rows(sql, params)
        return rows[0] if rows else None

    async def build_activity(self, **changes):
        values = dict(
            activity_id=self.activity_id,
            sources=(SourceSnapshot(self.source_id, self.version_id, 1),),
            deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
            max_requests=8,
            max_cost_microunits=800,
            reserve_cost_microunits=100,
            max_request_bytes=1_048_576,
            max_output_tokens=256,
            max_running_seconds=3600,
            allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
            allowed_tools=(),
            scope_revision=1,
        )
        values.update(changes)
        spec = ActivitySpec(**values)
        await self.ledger.create_activity(spec)
        lease = await self.ledger.claim_lease(spec.activity_id, "worker-088", lease_seconds=300, window_seconds=300)
        self.assertIsNotNone(lease)
        return spec, lease

    @staticmethod
    def intent(spec, lease, operation_id="op-088-1"):
        return AdmissionIntent(
            context=CallContext(
                activity_id=spec.activity_id,
                operation_id=operation_id,
                executor_id=lease.executor_id,
                execution_generation=lease.execution_generation,
                scope_revision=lease.scope_revision,
            ),
            provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,
            configured_model="synthetic-model",
            request_bytes=512,
            max_output_tokens=64,
            tool_names=(),
        )

    @staticmethod
    def payload_outcome(text_value="synthetic-正文-088", **meta):
        fmt, payload, sha = build_business_payload(text=text_value)
        values = dict(
            disposition=LedgerDisposition.RECEIVED,
            remote_request_id="remote-088",
            returned_model="synthetic-model",
            finish_reason="stop",
            prompt_tokens=10,
            completion_tokens=4,
            response_bytes=200,
            payload_format=fmt,
            payload=payload,
            payload_sha256=sha,
        )
        values.update(meta)
        return LedgerOutcome(**values)

    async def dispatched_permit(self, spec, lease, operation_id="op-088-1"):
        permit = await self.ledger.admit(self.intent(spec, lease, operation_id))
        await self.ledger.mark_dispatch_started(permit)
        return permit

    # -- 迁移 007 ---------------------------------------------------------

    async def test_01_migration_007_on_legacy_baseline_and_no_backfill(self):
        """隔离 schema 内：001—006 基线含旧 received 操作，007 成功、不回填、重跑报错回滚。"""
        import psycopg
        schema = "task088_mig_check"
        async with await psycopg.AsyncConnection.connect(DSN, autocommit=True) as connection:
            await connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
            await connection.execute(f"CREATE SCHEMA {schema}")
            await connection.execute(f"SET search_path TO {schema}")
            for name in ("001_materials.sql", "002_activities.sql", "003_pdf_review.sql",
                         "004_activities_time_budget.sql", "005_activities_dispatch_closed.sql",
                         "006_activities_running_owner_session.sql"):
                await connection.execute((MIGRATIONS / name).read_text(encoding="utf-8"))
            # 旧基线：来源 + 活动 + 一条 received 无正文操作。
            source_id, version_id, activity_id = str(uuid4()), str(uuid4()), str(uuid4())
            async with connection.transaction():
                await connection.execute("INSERT INTO material_sources(id, title, revision) VALUES (%s, 'legacy', 0)", (source_id,))
                await connection.execute(
                    "INSERT INTO material_versions(id, source_id, filename, format, sha256, size) VALUES (%s, %s, 'l.txt', 'txt', %s, 3)",
                    (version_id, source_id, "b" * 64),
                )
                await connection.execute("UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s", (version_id, source_id))
                await connection.execute(
                    """INSERT INTO activities(id, status, scope_revision, execution_generation, deadline_at,
                           max_requests, max_cost_microunits, reserve_cost_microunits,
                           max_request_bytes, max_output_tokens, max_running_seconds)
                         VALUES (%s, 'pending', 1, 0, CURRENT_TIMESTAMP + interval '1 hour', 4, 400, 100, 4096, 256, 3600)""",
                    (activity_id,),
                )
                await connection.execute(
                    "INSERT INTO activity_scope_sources(activity_id, source_id, version_id, source_revision) VALUES (%s, %s, %s, 1)",
                    (activity_id, source_id, version_id),
                )
                await connection.execute(
                    """INSERT INTO activity_operations(activity_id, operation_id, admission_id, executor_id,
                           execution_generation, scope_revision, provider, configured_model,
                           request_bytes, max_output_tokens, reserved_cost_microunits,
                           state, disposition, recorded_at)
                         VALUES (%s, 'legacy-op', %s, 'legacy-worker', 1, 1, 'p', 'm', 8, 8, 100,
                                 'received', 'received', CURRENT_TIMESTAMP)""",
                    (activity_id, str(uuid4())),
                )
            await connection.execute((MIGRATIONS / "007_activity_operation_results.sql").read_text(encoding="utf-8"))
            row = await (await connection.execute(
                "SELECT count(*) AS n FROM information_schema.tables WHERE table_schema = %s AND table_name = 'activity_operation_results'",
                (schema,),
            )).fetchone()
            self.assertEqual(1, row[0])
            cursor = await connection.execute(f"SELECT count(*) AS n FROM {schema}.activity_operation_results")
            self.assertEqual(0, (await cursor.fetchone())[0])  # 旧 received 不回填
            # 重跑：明确重复对象错误且事务回滚。
            with self.assertRaises(psycopg.Error):
                await connection.execute((MIGRATIONS / "007_activity_operation_results.sql").read_text(encoding="utf-8"))
            await connection.execute("ROLLBACK")
            await connection.execute(f"DROP SCHEMA {schema} CASCADE")
            await connection.execute("SET search_path TO public")

    async def test_02_constraints_and_fk_and_rerun_rollback(self):
        """主 schema：非法正文/hash 被 CHECK 拒绝；孤立 results 行被 FK 拒绝。"""
        import psycopg
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        async def bad(sql, params):
            with self.assertRaises(Exception):
                async with await psycopg.AsyncConnection.connect(DSN) as connection:
                    await connection.execute(sql, params)
        columns = """(activity_id, operation_id, admission_id, execution_generation, scope_revision,
                      payload_format, payload, payload_sha256)"""
        base = (self.activity_id, "op-088-1", permit.admission_id, 1, 1, "text", "payload", "a" * 64)
        # 非法 format / 伪 hash / 超界字节。
        await bad(f"INSERT INTO activity_operation_results{columns} VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                  (*base[:5], "yaml", *base[6:]))
        await bad(f"INSERT INTO activity_operation_results{columns} VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                  (*base[:7], "Z" * 64))
        await bad(f"INSERT INTO activity_operation_results{columns} VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                  (*base[:6], "x" * 131073, base[7]))
        # FK：不存在的 operation。
        await bad(f"INSERT INTO activity_operation_results{columns} VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                  (self.activity_id, "missing-op", str(uuid4()), 1, 1, "text", "p", "b" * 64))

    # -- 原子提交与幂等 ----------------------------------------------------

    async def test_03_atomic_commit_idempotent_retry_and_conflict(self):
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        outcome = self.payload_outcome()
        first = await self.ledger.record_outcome(permit, outcome)
        self.assertEqual(RecordOutcome.RECORDED, first)
        rows = await self.db_rows("SELECT * FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,))
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual(outcome.payload_sha256, row["payload_sha256"])
        self.assertEqual(outcome.payload, row["payload"])
        self.assertEqual(str(row["admission_id"]), permit.admission_id)
        self.assertEqual(lease.execution_generation, row["execution_generation"])
        self.assertEqual(lease.scope_revision, row["scope_revision"])
        # 相同完整重试：不写、返回 ALREADY_PRESENT。
        second = await self.ledger.record_outcome(permit, outcome)
        self.assertEqual(RecordOutcome.ALREADY_PRESENT, second)
        self.assertEqual(1, len(await self.db_rows(
            "SELECT * FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,))))
        # 异文冲突：保留已有正文/终态。
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(permit, self.payload_outcome("different-正文"))
        # 无正文重放与带正文终态不等价：拒绝。
        bare = LedgerOutcome(
            LedgerDisposition.RECEIVED,
            remote_request_id="remote-088",
            returned_model="synthetic-model",
            finish_reason="stop",
            prompt_tokens=10,
            completion_tokens=4,
            response_bytes=200,
        )
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(permit, bare)
        # 关门/代次推进后相同历史提交仍可确认（不给新执行权）。
        await self.ledger.cancel_activity(spec.activity_id)
        again = await self.ledger.record_outcome(permit, outcome)
        self.assertEqual(RecordOutcome.ALREADY_PRESENT, again)
        still = await self.db_rows("SELECT payload_sha256 FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,))
        self.assertEqual(outcome.payload_sha256, still[0]["payload_sha256"])

    async def test_04_legacy_received_without_payload_cannot_backfill(self):
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        bare = LedgerOutcome(LedgerDisposition.RECEIVED, returned_model="synthetic-model",
                             finish_reason="stop", prompt_tokens=3, completion_tokens=2, response_bytes=80)
        self.assertEqual(RecordOutcome.RECORDED, await self.ledger.record_outcome(permit, bare))
        self.assertEqual(RecordOutcome.ALREADY_PRESENT, await self.ledger.record_outcome(permit, bare))
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(
                permit,
                self.payload_outcome(returned_model="synthetic-model", finish_reason="stop",
                                     prompt_tokens=3, completion_tokens=2, response_bytes=80),
            )
        self.assertEqual(0, len(await self.db_rows(
            "SELECT * FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,))))

    async def test_05_close_door_rejects_payload_write_but_allows_unknown(self):
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        await self.ledger.begin_window_close(spec.activity_id, lease.executor_id, lease.execution_generation)
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(permit, self.payload_outcome())
        op = await self.db_row("SELECT state FROM activity_operations WHERE admission_id = %s", (permit.admission_id,))
        self.assertEqual("dispatched", op["state"])
        self.assertEqual(0, len(await self.db_rows(
            "SELECT * FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,))))
        # 关门后 UNKNOWN 诊断合同不变。
        self.assertEqual(
            RecordOutcome.RECORDED,
            await self.ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="deadline_exceeded")),
        )

    async def test_06_stale_permit_generation_scope_lease_source_rejected(self):
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        # 失效来源（版本替换）→ 非 UNKNOWN 拒绝。
        new_version = str(uuid4())
        import psycopg
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute("SELECT id FROM material_sources WHERE id = %s FOR UPDATE", (self.source_id,))
                await connection.execute(
                    "INSERT INTO material_versions(id, source_id, filename, format, sha256, size) VALUES (%s, %s, 'r.txt', 'txt', %s, 11)",
                    (new_version, self.source_id, "c" * 64),
                )
                await connection.execute(
                    "UPDATE material_sources SET current_version = %s, revision = revision + 1 WHERE id = %s",
                    (new_version, self.source_id),
                )
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(permit, self.payload_outcome())
        self.assertEqual(0, len(await self.db_rows(
            "SELECT * FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,))))
        # 仍允许 UNKNOWN 诊断收敛。
        self.assertEqual(
            RecordOutcome.RECORDED,
            await self.ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="source_revoked")),
        )

    # -- 事务原子性：提交前失败无半写；提交后响应丢失可恢复 -----------------

    async def test_07_pre_commit_failure_leaves_no_partial_write(self):
        import psycopg
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                """CREATE FUNCTION task088_force_failure() RETURNS trigger LANGUAGE plpgsql AS $$
                     BEGIN
                       RAISE EXCEPTION 'synthetic results insert failure';
                     END $$"""
            )
            await connection.execute(
                """CREATE TRIGGER task088_force_failure BEFORE INSERT ON activity_operation_results
                     FOR EACH ROW EXECUTE FUNCTION task088_force_failure()"""
            )
        try:
            with self.assertRaises(AdmissionUnavailable):
                await self.ledger.record_outcome(permit, self.payload_outcome())
            op = await self.db_row("SELECT state, recorded_at FROM activity_operations WHERE admission_id = %s", (permit.admission_id,))
            self.assertEqual("dispatched", op["state"])
            self.assertIsNone(op["recorded_at"])
            self.assertEqual(0, len(await self.db_rows(
                "SELECT * FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,))))
        finally:
            async with await psycopg.AsyncConnection.connect(DSN) as connection:
                await connection.execute("DROP TRIGGER IF EXISTS task088_force_failure ON activity_operation_results")
                await connection.execute("DROP FUNCTION IF EXISTS task088_force_failure()")

    async def test_08_post_commit_response_loss_recovers_from_persistent_fact(self):
        """真实 COMMIT 后注入客户端响应丢失：gateway UNKNOWN/unconfirmed，
        read 可恢复正文，等值确认不再写，transport 总发送 1 次。

        注入点：仓储子类在 super().record_outcome 真实提交返回后抛
        AdmissionUnavailable（模拟 COMMIT 后响应丢失）。"""
        class LoseResponseLedger(PostgresAdmissionLedger):
            def __init__(self, dsn):
                super().__init__(dsn)
                self.lost = False

            async def record_outcome(self, permit, outcome):
                result = await super().record_outcome(permit, outcome)
                self.lost = True
                raise AdmissionUnavailable("synthetic response loss after commit")

        spec, lease = await self.build_activity()
        ledger = LoseResponseLedger(DSN)
        transport = _transport()
        gateway = ControlledModelGateway(_config(), ledger=ledger, transport=transport)
        context = CallContext(
            activity_id=spec.activity_id,
            operation_id="op-088-lost",
            executor_id=lease.executor_id,
            execution_generation=lease.execution_generation,
            scope_revision=lease.scope_revision,
        )
        result = await gateway.call(context, _request())
        self.assertEqual(CallStatus.UNKNOWN, result.status)
        self.assertEqual("record_unconfirmed", result.error_code)
        self.assertTrue(ledger.lost)
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-088-lost")
        self.assertEqual(ResultReadStatus.COMMITTED_CURRENT, snapshot.read_status)
        self.assertRegex(snapshot.payload_sha256 or "", r"^[0-9a-f]{64}$")
        self.assertIsNotNone(snapshot.payload)
        # 等值确认不再写：同一 outcome 重放返回 ALREADY_PRESENT，transport 仍 1 次。
        stored = snapshot
        replay = LedgerOutcome(
            LedgerDisposition.RECEIVED,
            remote_request_id="request-088",
            returned_model="synthetic-model",
            finish_reason="stop",
            prompt_tokens=10,
            completion_tokens=4,
            response_bytes=200,
            payload_format=stored.payload_format,
            payload=stored.payload,
            payload_sha256=stored.payload_sha256,
        )
        permit = await self.db_row("SELECT admission_id FROM activity_operations WHERE activity_id = %s AND operation_id = %s",
                                   (spec.activity_id, "op-088-lost"))
        from app.capabilities import AdmissionPermit as Permit
        confirm = await self.ledger.record_outcome(
            Permit(str(permit["admission_id"]), "op-088-lost", lease.executor_id), replay
        )
        self.assertEqual(RecordOutcome.ALREADY_PRESENT, confirm)
        self.assertEqual(1, transport.calls)

    # -- 竞争与取消 ---------------------------------------------------------

    async def _wait_for_lock_waiter(self, timeout=10.0):
        """以 pg_stat_activity 锁等待事件为屏障，非 sleep 推断。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            row = await self.db_row(
                "SELECT count(*) AS n FROM pg_stat_activity WHERE datname = current_database() AND wait_event_type = 'Lock'"
            )
            if row["n"] >= 1:
                return
            await asyncio.sleep(0.05)
        raise AssertionError("锁等待事件未出现")

    async def test_09_two_connections_compete_single_result_row(self):
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        outcome = self.payload_outcome()
        results = await asyncio.gather(
            PostgresAdmissionLedger(DSN).record_outcome(permit, outcome),
            PostgresAdmissionLedger(DSN).record_outcome(permit, outcome),
            return_exceptions=True,
        )
        outcomes = sorted(item.value if isinstance(item, RecordOutcome) else type(item).__name__ for item in results)
        self.assertEqual([RecordOutcome.ALREADY_PRESENT.value, RecordOutcome.RECORDED.value], outcomes)
        self.assertEqual(1, len(await self.db_rows(
            "SELECT * FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,))))

    async def test_10_source_replacement_races_payload_commit(self):
        """两种先后：替换先提交→拒写；record 先进入临界区→按锁内快照成功。

        顺序2用操作行锁屏障证明 record 在替换提交前已持源锁/活动锁进入临界区；
        替换 UPDATE 被 record 的源锁排队，record 提交后替换才完成。"""
        import psycopg
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        # 顺序1：替换已提交 → record 拒绝（不依赖屏障的确定性顺序）。
        new_version = str(uuid4())
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute("SELECT id FROM material_sources WHERE id = %s FOR UPDATE", (self.source_id,))
                await connection.execute(
                    "INSERT INTO material_versions(id, source_id, filename, format, sha256, size) VALUES (%s, %s, 'r.txt', 'txt', %s, 11)",
                    (new_version, self.source_id, "c" * 64),
                )
                await connection.execute(
                    "UPDATE material_sources SET current_version = %s, revision = revision + 1 WHERE id = %s",
                    (new_version, self.source_id),
                )
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(permit, self.payload_outcome())
        # 顺序2：屏障证明 record 先于替换提交进入临界区。
        activity_id2 = str(uuid4())
        self.extra_activity_ids.append(activity_id2)
        source2, version2 = str(uuid4()), str(uuid4())
        self.extra_source_ids.append((source2, version2))
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute("INSERT INTO material_sources(id, title, revision) VALUES (%s, 's2', 0)", (source2,))
                await connection.execute(
                    "INSERT INTO material_versions(id, source_id, filename, format, sha256, size) VALUES (%s, %s, 's2.txt', 'txt', %s, 9)",
                    (version2, source2, "d" * 64),
                )
                await connection.execute("UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s", (version2, source2))
        spec2, lease2 = await self.build_activity(
            activity_id=activity_id2, sources=(SourceSnapshot(source2, version2, 1),)
        )
        permit2 = await self.dispatched_permit(spec2, lease2)
        blocker = await psycopg.AsyncConnection.connect(DSN, autocommit=True)
        try:
            await blocker.execute("BEGIN")
            await blocker.execute(
                "SELECT admission_id FROM activity_operations WHERE activity_id = %s AND operation_id = %s FOR UPDATE",
                (activity_id2, "op-088-1"),
            )
            blocked_record = asyncio.create_task(
                PostgresAdmissionLedger(DSN).record_outcome(permit2, self.payload_outcome())
            )
            # 屏障：record 已持源锁/活动锁、等待操作行锁（锁等待事件，非 sleep）。
            await self._wait_for_lock_waiter()

            new_version2 = str(uuid4())

            async def replace_source():
                async with await psycopg.AsyncConnection.connect(DSN) as connection:
                    await connection.execute("SET statement_timeout = '15s'")
                    async with connection.transaction():
                        await connection.execute(
                            "INSERT INTO material_versions(id, source_id, filename, format, sha256, size) VALUES (%s, %s, 'r2.txt', 'txt', %s, 11)",
                            (new_version2, source2, "e" * 64),
                        )
                        await connection.execute(
                            "UPDATE material_sources SET current_version = %s, revision = revision + 1 WHERE id = %s",
                            (new_version2, source2),
                        )

            replacement = asyncio.create_task(replace_source())
            await blocker.execute("COMMIT")  # 放行 record；替换排队在 record 源锁之后。
            committed = await blocked_record
            await replacement
        finally:
            await blocker.close()
        self.assertEqual(RecordOutcome.RECORDED, committed)
        self.assertEqual(1, len(await self.db_rows(
            "SELECT * FROM activity_operation_results WHERE activity_id = %s", (activity_id2,))))
        # 替换随后已提交：同一正文此刻读被来源失配抑制（时间边界如实呈现）。
        snapshot = await self.ledger.read_committed_result(activity_id2, "op-088-1")
        self.assertEqual(ResultReadStatus.INVALIDATED_SOURCE, snapshot.read_status)
        self.assertIsNone(snapshot.payload)

    async def test_11_cancel_vs_commit_ordering_and_no_extra_settle(self):
        import psycopg
        spec, lease = await self.build_activity()
        permit = await self.dispatched_permit(spec, lease)
        # 顺序1：提交在前 → 取消后历史成果按有效读规则保留。
        self.assertEqual(RecordOutcome.RECORDED, await self.ledger.record_outcome(permit, self.payload_outcome()))
        generation = await self.ledger.cancel_activity(spec.activity_id)
        self.assertEqual(lease.execution_generation + 1, generation)
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-088-1")
        self.assertEqual(ResultReadStatus.COMMITTED_HISTORY_CANCELLED, snapshot.read_status)
        self.assertIsNotNone(snapshot.payload)
        # 取消后旧窗口不得额外结算。
        with self.assertRaises(ActivityLedgerConflict):
            await self.ledger.settle_execution_window(
                spec.activity_id, lease.executor_id, lease.execution_generation,
                window_seconds=300, elapsed_seconds=1.0,
            )
        # 顺序2：取消持锁在前（屏障证明），提交在后 → 拒绝且不留半写。
        activity_id2 = str(uuid4())
        self.extra_activity_ids.append(activity_id2)
        source2, version2 = str(uuid4()), str(uuid4())
        self.extra_source_ids.append((source2, version2))
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute("INSERT INTO material_sources(id, title, revision) VALUES (%s, 's3', 0)", (source2,))
                await connection.execute(
                    "INSERT INTO material_versions(id, source_id, filename, format, sha256, size) VALUES (%s, %s, 's3.txt', 'txt', %s, 9)",
                    (version2, source2, "f" * 64),
                )
                await connection.execute("UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s", (version2, source2))
        spec2, lease2 = await self.build_activity(
            activity_id=activity_id2, sources=(SourceSnapshot(source2, version2, 1),)
        )
        permit2 = await self.dispatched_permit(spec2, lease2)
        blocker = await psycopg.AsyncConnection.connect(DSN, autocommit=True)
        try:
            await blocker.execute("BEGIN")
            await blocker.execute("SELECT id FROM activities WHERE id = %s FOR UPDATE", (activity_id2,))
            blocked_record = asyncio.create_task(
                PostgresAdmissionLedger(DSN).record_outcome(permit2, self.payload_outcome())
            )
            await self._wait_for_lock_waiter()
            await blocker.execute(
                """UPDATE activities
                      SET status = 'cancelled', execution_generation = execution_generation + 1,
                          executor_id = NULL, lease_expires_at = NULL, cancelled_at = CURRENT_TIMESTAMP,
                          running_owner_session_id = NULL, dispatch_closed = TRUE,
                          running_reserved_seconds = 0,
                          running_settled_seconds = running_settled_seconds + running_reserved_seconds,
                          updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s""",
                (activity_id2,),
            )
            await blocker.execute("COMMIT")
            with self.assertRaises(AdmissionDenied):
                await blocked_record
        finally:
            await blocker.close()
        self.assertEqual(0, len(await self.db_rows(
            "SELECT * FROM activity_operation_results WHERE activity_id = %s", (activity_id2,))))

    # -- 恢复读取：失效抑制、状态映射、分页 ---------------------------------

    async def _commit_payload(self, spec, lease, operation_id="op-088-1", text="synthetic-正文-088"):
        permit = await self.dispatched_permit(spec, lease, operation_id)
        outcome = self.payload_outcome(text)
        await self.ledger.record_outcome(permit, outcome)
        return permit, outcome

    async def test_12_read_states_mapping(self):
        spec, lease = await self.build_activity()
        # NO_OPERATION：未知 operation；缺失活动同样未找到。
        missing = await self.ledger.read_committed_result(spec.activity_id, "no-such-op")
        self.assertEqual(ResultReadStatus.NO_OPERATION, missing.read_status)
        self.assertIsNone(missing.admission_id)
        no_activity = await self.ledger.read_committed_result(str(uuid4()), "op")
        self.assertEqual(ResultReadStatus.NO_OPERATION, no_activity.read_status)
        # reserved → UNRESOLVED。
        permit = await self.ledger.admit(self.intent(spec, lease, "op-reserved"))
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-reserved")
        self.assertEqual(ResultReadStatus.UNRESOLVED, snapshot.read_status)
        self.assertIsNotNone(snapshot.admission_id)
        # dispatched → UNRESOLVED。
        permit2 = await self.dispatched_permit(spec, lease, "op-dispatched")
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-dispatched")
        self.assertEqual(ResultReadStatus.UNRESOLVED, snapshot.read_status)
        # not_sent 无正文 → TERMINAL_WITHOUT_PAYLOAD。
        await self.ledger.record_outcome(permit2, LedgerOutcome(LedgerDisposition.NOT_SENT, error_code="request_not_sent"))
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-dispatched")
        self.assertEqual(ResultReadStatus.TERMINAL_WITHOUT_PAYLOAD, snapshot.read_status)
        self.assertIsNone(snapshot.payload)
        # received 无正文 → TERMINAL_WITHOUT_PAYLOAD。
        permit3 = await self.dispatched_permit(spec, lease, "op-bare")
        await self.ledger.record_outcome(
            permit3, LedgerOutcome(LedgerDisposition.RECEIVED, finish_reason="stop", response_bytes=10)
        )
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-bare")
        self.assertEqual(ResultReadStatus.TERMINAL_WITHOUT_PAYLOAD, snapshot.read_status)
        # unknown → UNRESOLVED。
        permit4 = await self.dispatched_permit(spec, lease, "op-unknown")
        await self.ledger.record_outcome(permit4, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="delivery_unknown"))
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-unknown")
        self.assertEqual(ResultReadStatus.UNRESOLVED, snapshot.read_status)
        # 合法正文 → COMMITTED_CURRENT，正文/hash 与存储一致。
        _, outcome = await self._commit_payload(spec, lease, "op-committed")
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-committed")
        self.assertEqual(ResultReadStatus.COMMITTED_CURRENT, snapshot.read_status)
        self.assertEqual(outcome.payload, snapshot.payload)
        self.assertEqual(outcome.payload_sha256, snapshot.payload_sha256)
        self.assertEqual("text", snapshot.payload_format)
        self.assertIsNotNone(snapshot.committed_at)

    async def test_13_read_suppression_scope_source_and_binding(self):
        import psycopg
        spec, lease = await self.build_activity()
        _, outcome = await self._commit_payload(spec, lease)
        # scope 改变（SQL 注入反例，G4 未落地的产品路径不存在）→ 抑制正文。
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "UPDATE activities SET scope_revision = scope_revision + 1 WHERE id = %s", (spec.activity_id,)
            )
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-088-1")
        self.assertEqual(ResultReadStatus.INVALIDATED_SCOPE_CHANGED, snapshot.read_status)
        self.assertIsNone(snapshot.payload)
        self.assertEqual(outcome.payload_sha256, snapshot.payload_sha256)
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "UPDATE activities SET scope_revision = scope_revision - 1 WHERE id = %s", (spec.activity_id,)
            )
        # 来源版本失配 → 抑制正文。
        new_version = str(uuid4())
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute(
                    "INSERT INTO material_versions(id, source_id, filename, format, sha256, size) VALUES (%s, %s, 'r.txt', 'txt', %s, 11)",
                    (new_version, self.source_id, "c" * 64),
                )
                await connection.execute(
                    "UPDATE material_sources SET current_version = %s, revision = revision + 1 WHERE id = %s",
                    (new_version, self.source_id),
                )
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-088-1")
        self.assertEqual(ResultReadStatus.INVALIDATED_SOURCE, snapshot.read_status)
        self.assertIsNone(snapshot.payload)
        # 恢复来源。
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s",
                (self.version_id, self.source_id),
            )
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-088-1")
        self.assertEqual(ResultReadStatus.COMMITTED_CURRENT, snapshot.read_status)
        self.assertIsNotNone(snapshot.payload)
        # 空来源集合 → 抑制正文。
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute("DELETE FROM activity_scope_sources WHERE activity_id = %s", (spec.activity_id,))
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-088-1")
        self.assertEqual(ResultReadStatus.INVALIDATED_SOURCE, snapshot.read_status)
        self.assertIsNone(snapshot.payload)
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "INSERT INTO activity_scope_sources(activity_id, source_id, version_id, source_revision) VALUES (%s, %s, %s, 1)",
                (spec.activity_id, self.source_id, self.version_id),
            )
        # 绑定损坏（直接 UPDATE 结果行 admission_id；FK 保护下可构造的反例）→ 完整性错误。
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "UPDATE activity_operation_results SET admission_id = %s WHERE activity_id = %s",
                (str(uuid4()), spec.activity_id),
            )
        with self.assertRaises(ResultIntegrityError):
            await self.ledger.read_committed_result(spec.activity_id, "op-088-1")
        # 缺失来源行（FK 下不可构造）：记录为约束保证的防御分支；version 失配
        # 已覆盖 NOT EXISTS 不匹配项，LEFT JOIN NULL 分支由同一 SQL 形状保护。
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "DELETE FROM activity_operation_results WHERE activity_id = %s", (spec.activity_id,)
            )
        _, outcome2 = await self._commit_payload(spec, lease, "op-second", "second-正文")
        self.assertEqual(
            ResultReadStatus.COMMITTED_CURRENT,
            (await self.ledger.read_committed_result(spec.activity_id, "op-second")).read_status,
        )

    async def test_14_list_pagination_metadata_only_and_bounds(self):
        spec, lease = await self.build_activity()
        committed = []
        for index in range(3):
            operation_id = f"op-list-{index}"
            _, outcome = await self._commit_payload(spec, lease, operation_id, f"list-正文-{index}")
            committed.append((operation_id, outcome.payload_sha256))
        # 无正文操作不混入列表。
        permit = await self.dispatched_permit(spec, lease, "op-list-bare")
        await self.ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.RECEIVED, response_bytes=4))
        page = await self.ledger.list_committed_results(spec.activity_id, limit=2)
        self.assertEqual(2, len(page))
        self.assertEqual(["op-list-0", "op-list-1"], [item.operation_id for item in page])
        self.assertTrue(all(item.payload is None for item in page))
        self.assertTrue(all(item.read_status is ResultReadStatus.COMMITTED_CURRENT for item in page))
        self.assertEqual([sha for _, sha in committed[:2]], [item.payload_sha256 for item in page])
        rest = await self.ledger.list_committed_results(spec.activity_id, limit=2, after_operation_id=page[-1].operation_id)
        self.assertEqual(1, len(rest))
        self.assertEqual("op-list-2", rest[0].operation_id)
        # 游标无重复、失效记录保留元数据。
        import psycopg
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "UPDATE activities SET scope_revision = scope_revision + 1 WHERE id = %s", (spec.activity_id,)
            )
        page = await self.ledger.list_committed_results(spec.activity_id, limit=10)
        self.assertEqual(3, len(page))
        self.assertEqual({item.operation_id for item in page}, {op for op, _ in committed})
        self.assertTrue(all(item.read_status is ResultReadStatus.INVALIDATED_SCOPE_CHANGED for item in page))
        self.assertTrue(all(item.payload is None and item.payload_sha256 for item in page))
        for bad_limit in (0, 201, True, "10"):
            with self.assertRaises(ValueError):
                await self.ledger.list_committed_results(spec.activity_id, limit=bad_limit)

    async def test_16_historical_binding_and_write_free_confirmation(self):
        import psycopg
        spec, lease = await self.build_activity()
        permit, outcome = await self._commit_payload(spec, lease)
        await self.ledger.cancel_activity(spec.activity_id)
        original = await self.db_row(
            "SELECT *, xmin::text AS row_version FROM activity_operation_results WHERE activity_id=%s",
            (spec.activity_id,))
        for column, bad in (("admission_id", str(uuid4())), ("execution_generation", 99), ("scope_revision", 99)):
            with self.subTest(column=column):
                async with await psycopg.AsyncConnection.connect(DSN) as conn:
                    await conn.execute(f"UPDATE activity_operation_results SET {column}=%s WHERE activity_id=%s",
                                       (bad, spec.activity_id))
                with self.assertRaises(AdmissionDenied):
                    await self.ledger.record_outcome(permit, outcome)
                with self.assertRaises(ResultIntegrityError):
                    await self.ledger.read_committed_result(spec.activity_id, permit.operation_id)
                async with await psycopg.AsyncConnection.connect(DSN) as conn:
                    await conn.execute(f"UPDATE activity_operation_results SET {column}=%s WHERE activity_id=%s",
                                       (original[column], spec.activity_id))
        before = await self.db_row(
            "SELECT xmin::text AS row_version FROM activity_operation_results WHERE activity_id=%s", (spec.activity_id,))
        self.assertEqual(RecordOutcome.ALREADY_PRESENT, await self.ledger.record_outcome(permit, outcome))
        after = await self.db_row(
            "SELECT xmin::text AS row_version FROM activity_operation_results WHERE activity_id=%s", (spec.activity_id,))
        self.assertEqual(before, after)

    async def test_17_new_payload_rejects_each_stale_authority(self):
        import psycopg
        for case in ("permit", "generation", "scope", "lease", "executor"):
            with self.subTest(case=case):
                activity_id = str(uuid4())
                self.extra_activity_ids.append(activity_id)
                spec, lease = await self.build_activity(activity_id=activity_id)
                permit = await self.dispatched_permit(spec, lease)
                mutations = {
                    "generation": "execution_generation=execution_generation+1",
                    "scope": "scope_revision=scope_revision+1",
                    "lease": "lease_expires_at=CURRENT_TIMESTAMP-interval '1 second'",
                    "executor": "executor_id='other-worker'",
                }
                if case == "permit":
                    permit = AdmissionPermit(str(uuid4()), permit.operation_id, permit.executor_id)
                else:
                    async with await psycopg.AsyncConnection.connect(DSN) as conn:
                        await conn.execute(f"UPDATE activities SET {mutations[case]} WHERE id=%s", (activity_id,))
                with self.assertRaises(AdmissionDenied):
                    await self.ledger.record_outcome(permit, self.payload_outcome())
                self.assertEqual([], await self.db_rows(
                    "SELECT 1 FROM activity_operation_results WHERE activity_id=%s", (activity_id,)))
                row = await self.db_row("SELECT state FROM activity_operations WHERE activity_id=%s", (activity_id,))
                self.assertEqual("dispatched", row["state"])

    async def test_18_stored_payload_integrity_and_sql_suppression(self):
        import psycopg
        spec, lease = await self.build_activity()
        permit, outcome = await self._commit_payload(spec, lease)
        for column, value in (("payload_sha256", "0" * 64), ("payload", '{"format":"text","value":"changed"}')):
            async with await psycopg.AsyncConnection.connect(DSN) as conn:
                await conn.execute(f"UPDATE activity_operation_results SET {column}=%s WHERE activity_id=%s", (value, spec.activity_id))
            with self.assertRaises(ResultIntegrityError) as raised:
                await self.ledger.read_committed_result(spec.activity_id, permit.operation_id)
            self.assertEqual("payload_integrity", str(raised.exception))
            async with await psycopg.AsyncConnection.connect(DSN) as conn:
                await conn.execute(f"UPDATE activity_operation_results SET {column}=%s WHERE activity_id=%s",
                                   (getattr(outcome, column), spec.activity_id))
        # 在数据库驱动取行点观察失效投影，不能只测试最终对象被隐藏。
        async with await psycopg.AsyncConnection.connect(DSN) as conn:
            await conn.execute("UPDATE activities SET scope_revision=scope_revision+1 WHERE id=%s", (spec.activity_id,))
        fetchone = psycopg.AsyncCursor.fetchone
        observed = []
        async def capture(cursor):
            row = await fetchone(cursor)
            if isinstance(row, dict) and "binding_consistent" in row:
                observed.append(row["payload"])
            return row
        with patch.object(psycopg.AsyncCursor, "fetchone", capture):
            hidden = await self.ledger.read_committed_result(spec.activity_id, permit.operation_id)
        self.assertEqual([None], observed)
        self.assertIsNone(hidden.payload)

    # -- 时间账与业务正文分离 ----------------------------------------------

    async def test_15_settle_failure_vs_response_loss_keep_payload(self):
        import psycopg

        class LoseSettleResponseLedger(PostgresAdmissionLedger):
            async def settle_execution_window(self, *args, **kwargs):
                await super().settle_execution_window(*args, **kwargs)
                raise AdmissionUnavailable("synthetic settle response loss after commit")

        # （i）settle 提交前失败：真实连接终止注入（pg_terminate_backend）→
        # R 残留，后续 claim 全额保守折叠；正文保留。
        spec, lease = await self.build_activity()
        _, outcome = await self._commit_payload(spec, lease)
        await self.ledger.begin_window_close(spec.activity_id, lease.executor_id, lease.execution_generation)
        killer = await psycopg.AsyncConnection.connect(DSN, autocommit=True)
        try:
            await killer.execute("BEGIN")
            await killer.execute("SELECT id FROM activities WHERE id = %s FOR UPDATE", (spec.activity_id,))
            settle_task = asyncio.create_task(
                PostgresAdmissionLedger(DSN).settle_execution_window(
                    spec.activity_id, lease.executor_id, lease.execution_generation,
                    window_seconds=300, elapsed_seconds=2.0,
                )
            )
            await self._wait_for_lock_waiter()
            victim = await self.db_row(
                """SELECT pid FROM pg_stat_activity
                    WHERE datname = current_database() AND wait_event_type = 'Lock' LIMIT 1"""
            )
            await killer.execute("SELECT pg_terminate_backend(%s)", (victim["pid"],))
            await killer.execute("COMMIT")
            with self.assertRaises(AdmissionUnavailable):
                await settle_task
        finally:
            await killer.close()
        row = await self.db_row(
            "SELECT status, running_reserved_seconds, running_settled_seconds FROM activities WHERE id = %s",
            (spec.activity_id,),
        )
        self.assertEqual("running", row["status"])
        self.assertEqual(300, row["running_reserved_seconds"])
        # 直接过期注入（仅本合成活动）：把租约到期拨到过去，新 claim 折叠真实残留。
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "UPDATE activities SET lease_expires_at = CURRENT_TIMESTAMP - interval '1 second' WHERE id = %s",
                (spec.activity_id,),
            )
        new_lease = await self.ledger.claim_lease(spec.activity_id, "worker-088-b", lease_seconds=60, window_seconds=60)
        self.assertIsNotNone(new_lease)
        row = await self.db_row(
            "SELECT running_reserved_seconds, running_settled_seconds FROM activities WHERE id = %s",
            (spec.activity_id,),
        )
        self.assertEqual(60, row["running_reserved_seconds"])
        self.assertEqual(300, row["running_settled_seconds"])  # 残留全额折叠
        snapshot = await self.ledger.read_committed_result(spec.activity_id, "op-088-1")
        self.assertIsNotNone(snapshot.payload)
        # 清理第二个租约。
        await self.ledger.cancel_activity(spec.activity_id)

        # （ii）settle 提交后响应丢失：R0/S 已结算不折叠；同 G/C 确认
        # ALREADY_SETTLED 不重复加账；正文保留。
        activity_id2 = str(uuid4())
        self.extra_activity_ids.append(activity_id2)
        source2, version2 = str(uuid4()), str(uuid4())
        self.extra_source_ids.append((source2, version2))
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute("INSERT INTO material_sources(id, title, revision) VALUES (%s, 's5', 0)", (source2,))
                await connection.execute(
                    "INSERT INTO material_versions(id, source_id, filename, format, sha256, size) VALUES (%s, %s, 's5.txt', 'txt', %s, 9)",
                    (version2, source2, "f" * 64),
                )
                await connection.execute("UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s", (version2, source2))
        spec2, lease2 = await self.build_activity(
            activity_id=activity_id2, sources=(SourceSnapshot(source2, version2, 1),)
        )
        _, outcome2 = await self._commit_payload(spec2, lease2)
        await self.ledger.begin_window_close(spec2.activity_id, lease2.executor_id, lease2.execution_generation)
        losing = LoseSettleResponseLedger(DSN)
        with self.assertRaises(AdmissionUnavailable):
            await losing.settle_execution_window(
                spec2.activity_id, lease2.executor_id, lease2.execution_generation,
                window_seconds=300, elapsed_seconds=2.0,
            )
        row = await self.db_row(
            "SELECT status, running_reserved_seconds, running_settled_seconds FROM activities WHERE id = %s",
            (spec2.activity_id,),
        )
        self.assertEqual("pending", row["status"])
        self.assertEqual(0, row["running_reserved_seconds"])
        self.assertEqual(2, row["running_settled_seconds"])
        confirm = await self.ledger.settle_execution_window(
            spec2.activity_id, lease2.executor_id, lease2.execution_generation,
            window_seconds=300, elapsed_seconds=2.0,
        )
        self.assertEqual(SettleResult.ALREADY_SETTLED, confirm)
        row = await self.db_row(
            "SELECT running_settled_seconds FROM activities WHERE id = %s", (spec2.activity_id,)
        )
        self.assertEqual(2, row["running_settled_seconds"])
        snapshot = await self.ledger.read_committed_result(spec2.activity_id, "op-088-1")
        self.assertIsNotNone(snapshot.payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
