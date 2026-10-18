"""TASK-092 G5 工具次数、准入与类型隔离：离线合同加真实 PG 定向验证。

离线部分不访问网络/数据库；PG 部分仅在存在专用测试 DSN
（RETROLUME_TOOL_TEST_DATABASE_URL）时运行，不回退任何用户库。每例注册
本例创建的活动/来源/版本 ID，清理只定向删除本例行。全部数据合成；
工具执行是产品真实的有限计算，无供应商网络。
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from app.activities import (
    ActivityLedgerConflict,
    ActivitySpec,
    PostgresAdmissionLedger,
    ResultReadStatus,
    SettleResult,
    SourceSnapshot,
)
from app.activities.service import ActivityService
from app.capabilities.contracts import (
    MAX_TOOL_ARGUMENT_BYTES,
    AdmissionDenied,
    AdmissionIntent,
    AdmissionPermit,
    AdmissionUnavailable,
    CallContext,
    LedgerDisposition,
    LedgerOutcome,
    ModelCallRequest,
    ModelServiceConfig,
    Provider,
    RecordOutcome,
    ToolAdmissionPermit,
    ToolCallPlan,
    ToolCallStatus,
    ToolExecutionInput,
    ToolIntent,
    build_business_payload,
    canonical_tool_arguments,
    parse_tool_arguments,
    payload_digest,
    validate_business_payload,
)
from app.capabilities.tool_execution import ControlledToolExecutor
from app.capabilities.tools import ToolRegistry, ToolValidationError
from app.worker.session import SessionConfig
from app.runtime import psycopg_compatible_loop_factory

DSN = os.environ.get("RETROLUME_TOOL_TEST_DATABASE_URL", "")
MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


def make_call(operation_id="T1", call_id="calc.1", arguments=None) -> ToolExecutionInput:
    arguments = {"operation": "add", "left": 1, "right": 2} if arguments is None else arguments
    arguments_json, sha = canonical_tool_arguments(dict(arguments))
    return ToolExecutionInput(operation_id, call_id, "finite_calculate", arguments_json, sha)


def plan_for(call_id="calc.1", arguments=None) -> ToolCallPlan:
    arguments = {"operation": "add", "left": 1, "right": 2} if arguments is None else arguments
    return ToolCallPlan(call_id=call_id, name="finite_calculate", arguments=arguments)


class _ExplodingMapping(Mapping):
    def __getitem__(self, key):
        raise RuntimeError("synthetic mapping failure")

    def __iter__(self):
        raise RuntimeError("synthetic mapping failure")

    def __len__(self):
        return 0


class _OnceMapping(Mapping):
    """同一键第二次读取返回不同值；用于证明只读一次私有拷贝。"""

    def __init__(self, first, second):
        self._first, self._second, self._reads = first, second, {}

    def __getitem__(self, key):
        self._reads[key] = self._reads.get(key, 0) + 1
        return self._first[key] if self._reads[key] == 1 else self._second[key]

    def __iter__(self):
        return iter(self._first)

    def __len__(self):
        return len(self._first)


class CanonicalToolArgumentsTests(unittest.TestCase):
    def test_canonical_bytes_digest_and_schema(self):
        raw, sha = canonical_tool_arguments({"operation": "add", "left": 1, "right": 2})
        self.assertEqual(raw, '{"left":1,"operation":"add","right":2}')
        self.assertEqual(len(sha), 64)
        self.assertRegex(sha, r"^[0-9a-f]{64}$")
        # int/float 域表示保留：数学等价的 1 与 1.0 不承诺同摘要。
        raw_float, sha_float = canonical_tool_arguments({"operation": "add", "left": 1.0, "right": 2})
        self.assertEqual(raw_float, '{"left":1.0,"operation":"add","right":2}')
        self.assertNotEqual(sha, sha_float)

    def test_schema_and_domain_rejections(self):
        for bad in (
            {"operation": "add", "left": True, "right": 2},
            {"operation": "add", "left": 1, "right": float("nan")},
            {"operation": "add", "left": 1, "right": float("inf")},
            {"operation": "add", "left": 1, "right": 2, "extra": 1},
            {"operation": "add", "left": 1},
            {"operation": "add", "left": 1, "right": {"nested": 1}},
            {"operation": "add", "left": "1", "right": 2},
            {"operation": "add", "left": 1e13, "right": 2},
            {"operation": "divide", "left": 1, "right": 0},
            {"operation": "power", "left": 2, "right": 12.5},
            {"operation": "power", "left": 0, "right": -1},
            {"operation": "modulo", "left": 1, "right": 2},
        ):
            with self.subTest(case=bad), self.assertRaises(ValueError):
                canonical_tool_arguments(bad)

    def test_tool_execution_input_strict_wire(self):
        call = make_call()
        wire = call.to_wire()
        self.assertEqual(set(wire), {"operation_id", "call_id", "name", "arguments_json", "arguments_sha256"})
        self.assertEqual(ToolExecutionInput.from_wire(wire), call)
        # 伪造摘要、非规范字节、重复键、非有限常量与额外字段全部拒绝。
        for mutate in (
            lambda item: item.update(arguments_sha256="0" * 64),
            lambda item: item.update(arguments_json=item["arguments_json"].replace(":", ": ")),
            lambda item: item.update(arguments_json='{"left":1,"left":1,"operation":"add","right":2}'),
            lambda item: item.update(arguments_json='{"left":1,"operation":"add","right":NaN}'),
            lambda item: item.update(name="other_tool"),
            lambda item: item.update(call_id="bad call id"),
            lambda item: item.update(operation_id=""),
            lambda item: item.update(extra=1),
        ):
            item = dict(wire)
            mutate(item)
            with self.subTest(item=item), self.assertRaises(ValueError):
                ToolExecutionInput.from_wire(item)
        self.assertNotIn("left", repr(call))
        self.assertNotIn(call.arguments_sha256, repr(call))


class ServiceToolActionOfflineTests(unittest.IsolatedAsyncioTestCase):
    def ledger(self, snapshots):
        class ReadLedger:
            _bounded_name = staticmethod(PostgresAdmissionLedger._bounded_name)

            async def read_committed_result(self, activity_id, operation_id):
                return snapshots.get(operation_id, _no_operation(activity_id, operation_id))

        return ReadLedger()

    async def test_invalid_plan_fails_before_copy_or_supervision(self):
        ledger = self.ledger({})
        with patch("app.worker.one_tool.run_one_tool", side_effect=AssertionError("supervised")):
            for plan in (None, ToolCallPlan("calc.1", "finite_calculate", {"operation": "add", "left": True, "right": 2}),
                         ToolCallPlan("calc.1", "other", {"operation": "add", "left": 1, "right": 2}),
                         ToolCallPlan("calc.1", "finite_calculate", _ExplodingMapping())):
                with self.subTest(plan=plan):
                    outcome = await ActivityService(ledger).execute_tool_action(
                        str(uuid4()), "T1", plan, SessionConfig(), "executor", "run092")
                    self.assertEqual(outcome.status, "invalid_input")
                    self.assertIsNone(outcome.supervision)

    async def test_private_snapshot_single_read_and_immune_to_later_mutation(self):
        ledger = self.ledger({})
        captured = []

        def run(ledger_arg, config, activity_id, executor_id, call, *, run_tag):
            captured.append(call)
            return SimpleNamespace(settled_seconds=1, reserved_seconds=0, pending_fold_seconds=0,
                                   cleanup_incomplete=False, state="settled", tool_receipt=None)

        mapping = _OnceMapping({"operation": "add", "left": 1, "right": 2},
                               {"operation": "add", "left": 9, "right": 9})
        plan = ToolCallPlan("calc.1", "finite_calculate", mapping)
        with patch("app.worker.one_tool.run_one_tool", run):
            outcome = await ActivityService(ledger).execute_tool_action(
                str(uuid4()), "T1", plan, SessionConfig(), "executor", "run092")
        self.assertIsNotNone(outcome.supervision)
        self.assertEqual(len(captured), 1)
        expected = make_call(operation_id="T1")
        self.assertEqual(captured[0].arguments_json, expected.arguments_json)
        self.assertEqual(captured[0].arguments_sha256, expected.arguments_sha256)
        # 调用方 Mapping 后续读取变化不影响已捕获的规范输入。
        self.assertEqual(mapping["left"], 9)
        captured[0].to_wire()

    async def test_existing_same_key_identity_read_only_and_conflicts(self):
        activity = str(uuid4())
        same = _snapshot(activity, "T1", kind="tool", tool_call_id="calc.1",
                         arguments_sha256=make_call(operation_id="T1").arguments_sha256,
                         status=ResultReadStatus.COMMITTED_CURRENT)
        model_row = _snapshot(activity, "T1", kind="model",
                              status=ResultReadStatus.TERMINAL_WITHOUT_PAYLOAD)
        for snapshots, plan, expected in (
            ({"T1": same}, plan_for("calc.1"), "committed_current"),
            ({"T1": same}, plan_for("calc.2"), "tool_input_conflict"),
            ({"T1": same}, plan_for("calc.1", {"operation": "add", "left": 5, "right": 6}), "tool_input_conflict"),
            ({"T1": model_row}, plan_for("calc.1"), "operation_key_conflict"),
        ):
            with self.subTest(expected=expected):
                ledger = self.ledger(snapshots)
                with patch("app.worker.one_tool.run_one_tool", side_effect=AssertionError("supervised")):
                    outcome = await ActivityService(ledger).execute_tool_action(
                        activity, "T1", plan, SessionConfig(), "executor", "run092")
                self.assertEqual(outcome.status, expected)
                self.assertIsNone(outcome.supervision)

    async def test_known_config_conflict_rejects_before_supervision(self):
        ledger = self.ledger({})
        config = SessionConfig(window_seconds=200, request_timeout_seconds=121)
        with patch("app.worker.one_tool.run_one_tool", side_effect=AssertionError("supervised")):
            outcome = await ActivityService(ledger).execute_tool_action(
                str(uuid4()), "T1", plan_for(), config, "executor", "run092")
        self.assertEqual(outcome.status, "invalid_input")
        self.assertIsNone(outcome.supervision)

    async def test_tool_parent_never_consumed_by_model_continuation(self):
        activity = str(uuid4())
        fmt, payload, sha = build_business_payload(text="3")
        tool_parent = _snapshot(activity, "T1", kind="tool", tool_call_id="calc.1",
                                arguments_sha256="a" * 64, status=ResultReadStatus.COMMITTED_CURRENT,
                                payload_format=fmt, payload=payload, payload_sha256=sha)
        ledger = self.ledger({"T1": tool_parent})
        with patch("app.worker.one_call.run_one_call", side_effect=AssertionError("supervised")) as invoke:
            outcome = await ActivityService(ledger).continue_from_result(
                activity, "T1", "Q", "followup", _service(), SessionConfig(), "executor", "run092")
        self.assertEqual(outcome.status, "result_kind_not_consumable")
        self.assertIsNone(outcome.supervision)
        invoke.assert_not_called()

    async def test_supervision_result_maps_business_read_and_receipt(self):
        activity = str(uuid4())
        fmt, payload, sha = build_business_payload(text="3")
        committed = _snapshot(activity, "T1", kind="tool", tool_call_id="calc.1",
                              arguments_sha256=make_call(operation_id="T1").arguments_sha256,
                              status=ResultReadStatus.COMMITTED_CURRENT,
                              payload_format=fmt, payload=payload, payload_sha256=sha)
        receipt = {"protocol": 4, "business_commit": "committed",
                   "result": {"error_code": None, "payload_sha256": sha}}
        snapshots = {}

        def run(*args, **kw):
            # 监督返回时业务已持久提交：此后只读为 committed_current。
            snapshots["T1"] = committed
            return SimpleNamespace(settled_seconds=1, reserved_seconds=0, pending_fold_seconds=0,
                                   cleanup_incomplete=False, state="settled", tool_receipt=receipt)

        with patch("app.worker.one_tool.run_one_tool", run):
            outcome = await ActivityService(self.ledger(snapshots)).execute_tool_action(
                activity, "T1", plan_for(), SessionConfig(), "executor", "run092")
        self.assertEqual(outcome.status, "committed_current")
        self.assertEqual(outcome.business.snapshot.payload_sha256, sha)
        self.assertEqual(outcome.settlement.settled_seconds, 1)
        self.assertFalse(outcome.settlement.cleanup_incomplete)


def _snapshot(activity, operation_id, *, kind, tool_call_id=None, arguments_sha256=None,
              status=ResultReadStatus.NO_OPERATION, payload_format=None, payload=None, payload_sha256=None):
    from app.activities import CommittedResultSnapshot
    return CommittedResultSnapshot(
        activity, operation_id, status, scope_revision=1,
        payload_format=payload_format, payload=payload, payload_sha256=payload_sha256,
        kind=kind, tool_call_id=tool_call_id, arguments_sha256=arguments_sha256,
    )


def _no_operation(activity, operation_id):
    from app.activities import CommittedResultSnapshot
    return CommittedResultSnapshot(activity, operation_id, ResultReadStatus.NO_OPERATION)


def _service():
    return ModelServiceConfig(provider="deepseek_chat_completions", base_url="https://api.deepseek.com",
                              model="synthetic-model", api_key="synthetic-secret-092",
                              timeout_seconds=0.5, max_request_bytes=4096, max_response_bytes=4096)


class FakeToolLedger:
    """受控工具执行器的记录替身；只验证调用序与状态映射，不冒充PG事务。"""

    def __init__(self, *, admit=None, mark=None, record=None):
        self.events = []
        self.admit_behavior = admit
        self.mark_behavior = mark
        self.record_behavior = record
        self.recorded = []

    async def admit_tool_operation(self, intent):
        self.events.append("admit")
        if self.admit_behavior is not None:
            raise self.admit_behavior
        return ToolAdmissionPermit("admission", intent.call.operation_id, "executor",
                                   "activity", 1, 1, "finite_calculate", "calc.1", intent.call.arguments_sha256)

    async def mark_tool_started(self, permit, call):
        self.events.append("mark")
        if self.mark_behavior is not None:
            raise self.mark_behavior

    async def record_tool_outcome(self, permit, call, outcome):
        self.events.append("record")
        self.recorded.append(outcome)
        if self.record_behavior is not None:
            raise self.record_behavior
        return RecordOutcome.RECORDED


class CountingToolRegistry(ToolRegistry):
    def __init__(self):
        super().__init__()
        self.executions = 0

    def execute(self, plan):
        self.executions += 1
        return super().execute(plan)


class ControlledToolExecutorTests(unittest.IsolatedAsyncioTestCase):
    def context(self, operation_id="T1"):
        return CallContext(activity_id=str(uuid4()), operation_id=operation_id,
                           executor_id="executor", execution_generation=1, scope_revision=1)

    async def test_single_admit_mark_execute_record_and_committed_hash(self):
        ledger = FakeToolLedger()
        tools = CountingToolRegistry()
        call = make_call()
        result = await ControlledToolExecutor(ledger, tools=tools).call(self.context(), call)
        self.assertEqual(ledger.events, ["admit", "mark", "record"])
        self.assertEqual(tools.executions, 1)
        self.assertIs(result.status, ToolCallStatus.SUCCEEDED)
        self.assertEqual(len(result.payload_sha256), 64)
        outcome = ledger.recorded[0]
        self.assertIs(outcome.disposition, LedgerDisposition.RECEIVED)
        fmt, payload, sha = validate_business_payload(outcome.payload, outcome.payload_format, outcome.payload_sha256)
        self.assertEqual(payload, '{"format":"text","value":"3"}')
        self.assertEqual(sha, result.payload_sha256)
        self.assertNotIn("value", repr(outcome))

    async def test_forged_input_is_rejected_before_any_ledger_call(self):
        ledger = FakeToolLedger()
        forged = ToolExecutionInput("T1", "calc.1", "finite_calculate",
                                    '{"left":1,"operation":"add","right":2}', "0" * 64)
        with self.assertRaises(ValueError):
            await ControlledToolExecutor(ledger).call(self.context(), forged)
        self.assertEqual(ledger.events, [])

    async def test_denials_and_unconfirmed_map_without_execute(self):
        call = make_call()
        cases = (
            (FakeToolLedger(admit=AdmissionDenied("tool_limit_exhausted")), ToolCallStatus.REJECTED, "tool_limit_exhausted"),
            (FakeToolLedger(admit=AdmissionDenied("something private: dsn=hidden")), ToolCallStatus.REJECTED, "admission_denied"),
            (FakeToolLedger(admit=AdmissionUnavailable()), ToolCallStatus.UNKNOWN, "admission_unconfirmed"),
            (FakeToolLedger(mark=AdmissionDenied("qualification_invalid")), ToolCallStatus.REJECTED, "qualification_invalid"),
            (FakeToolLedger(mark=AdmissionUnavailable()), ToolCallStatus.UNKNOWN, "mark_unconfirmed"),
        )
        tools = CountingToolRegistry()
        for ledger, status, code in cases:
            with self.subTest(status=status, code=code):
                result = await ControlledToolExecutor(ledger, tools=tools).call(self.context(), call)
                self.assertIs(result.status, status)
                self.assertEqual(result.error_code, code)
                self.assertIsNone(result.payload_sha256)
                self.assertNotIn("record", ledger.events)
        self.assertEqual(tools.executions, 0)

    async def test_execution_failure_and_record_uncertainty_never_fake_success(self):
        call = make_call()
        class Failing(ToolRegistry):
            def execute(self, plan):
                raise ToolValidationError("计算无法在有限边界内完成")
        ledger = FakeToolLedger()
        result = await ControlledToolExecutor(ledger, tools=Failing()).call(self.context(), call)
        self.assertIs(result.status, ToolCallStatus.FAILED)
        self.assertEqual(result.error_code, "tool_execution_failed")
        outcome = ledger.recorded[0]
        self.assertIs(outcome.disposition, LedgerDisposition.RECEIVED)
        self.assertIsNone(outcome.payload)
        for record_exc, code in ((AdmissionDenied("closed"), "record_denied"), (AdmissionUnavailable(), "record_unconfirmed")):
            with self.subTest(code=code):
                ledger = FakeToolLedger(record=record_exc)
                result = await ControlledToolExecutor(ledger).call(self.context(), call)
                self.assertIs(result.status, ToolCallStatus.UNKNOWN)
                self.assertEqual(result.error_code, code)
                self.assertIsNone(result.payload_sha256)

    async def test_execute_exactly_once_and_no_retry_after_record_denied(self):
        call = make_call()
        tools = CountingToolRegistry()
        ledger = FakeToolLedger(record=AdmissionDenied("closed"))
        result = await ControlledToolExecutor(ledger, tools=tools).call(self.context(), call)
        self.assertEqual(tools.executions, 1)
        self.assertEqual(ledger.events, ["admit", "mark", "record"])
        self.assertIs(result.status, ToolCallStatus.UNKNOWN)


# ---------------------------------------------------------------------------
# 真实 PG：约束、绑定、计数、竞争、类型隔离与故障边界（C1—C9/C12目标项）
# ---------------------------------------------------------------------------


@unittest.skipUnless(DSN, "专用TASK092工具合成库未注入")
class ToolPostgresBase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self):
        self._asyncioRunner = asyncio.Runner(loop_factory=psycopg_compatible_loop_factory)

    async def asyncSetUp(self):
        import psycopg
        self.psycopg = psycopg
        self.ids = []
        self.sources = []
        self.ledger = PostgresAdmissionLedger(DSN)
        identity = await self.row("SELECT current_database() AS db, current_user AS role")
        assert identity == {"db": "retrolume_task092_tools", "role": "retrolume_task092_synth"}
        self.source = await self.new_source()
        self.activity = str(uuid4())
        self.ids.append(self.activity)
        await self.create(self.activity)

    async def create(self, activity, *, max_tool_calls=4, allowed_tools=("finite_calculate",), max_running_seconds=300):
        await self.ledger.create_activity(ActivitySpec(
            activity, (self.source,), datetime.now(timezone.utc) + timedelta(minutes=10),
            8, 800, 100, 65536, 256, max_running_seconds,
            (("deepseek_chat_completions", "synthetic-model"),),
            allowed_tools, max_tool_calls=max_tool_calls))

    async def asyncTearDown(self):
        async with await self.psycopg.AsyncConnection.connect(DSN) as c:
            for a in self.ids:
                for table in ("activity_operation_results", "activity_operations",
                              "activity_allowed_models", "activity_scope_sources"):
                    await c.execute("DELETE FROM " + table + " WHERE activity_id=%s", (a,))
                await c.execute("DELETE FROM activities WHERE id=%s", (a,))
            for source, version in self.sources:
                await c.execute("UPDATE material_sources SET current_version=NULL WHERE id=%s", (source,))
                await c.execute("DELETE FROM material_versions WHERE source_id=%s", (source,))
                await c.execute("DELETE FROM material_sources WHERE id=%s", (source,))

    async def rows(self, sql, params=()):
        from psycopg.rows import dict_row
        async with await self.psycopg.AsyncConnection.connect(DSN, row_factory=dict_row) as c:
            return await (await c.execute(sql, params)).fetchall()

    async def row(self, sql, params=()):
        return (await self.rows(sql, params))[0]

    async def sql(self, sql, params=()):
        async with await self.psycopg.AsyncConnection.connect(DSN) as c:
            await c.execute(sql, params)

    async def new_source(self):
        source, version = str(uuid4()), str(uuid4())
        self.sources.append((source, version))
        async with await self.psycopg.AsyncConnection.connect(DSN) as c:
            await c.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'TASK092-synthetic',0)", (source,))
            await c.execute("INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'synthetic.txt','txt',%s,1)",
                            (version, source, "8" * 64))
            await c.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (version, source))
        return SourceSnapshot(source, version, 1)

    async def claim(self, activity=None):
        return await self.ledger.claim_lease(activity or self.activity, "executor092",
                                             lease_seconds=120, window_seconds=30)

    def context(self, lease, operation_id, activity=None):
        return CallContext(activity_id=activity or self.activity, operation_id=operation_id,
                           executor_id=lease.executor_id, execution_generation=lease.execution_generation,
                           scope_revision=lease.scope_revision)

    def tool_intent(self, lease, call, activity=None):
        return ToolIntent(context=self.context(lease, call.operation_id, activity), call=call)

    async def account(self, activity=None):
        return await self.row(
            "SELECT status,execution_generation,dispatch_closed,max_tool_calls,tools_reserved,"
            "requests_reserved,cost_reserved_microunits,running_reserved_seconds,running_settled_seconds "
            "FROM activities WHERE id=%s", (activity or self.activity,))

    async def op_rows(self, activity=None, operation_id=None):
        if operation_id is None:
            return await self.rows("SELECT * FROM activity_operations WHERE activity_id=%s ORDER BY operation_id",
                                   (activity or self.activity,))
        return await self.rows("SELECT * FROM activity_operations WHERE activity_id=%s AND operation_id=%s",
                               (activity or self.activity, operation_id))


class ToolPostgresTests(ToolPostgresBase):
    # -- C1 约束反例与重复迁移 ------------------------------------------------

    async def test_c1_tool_operation_conditional_constraints(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        permit = await self.ledger.admit_tool_operation(self.tool_intent(lease, call))
        self.assertEqual((await self.account())["tools_reserved"], 1)
        base = ("INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,"
                "execution_generation,scope_revision,kind,provider,tool_names,reserved_cost_microunits,"
                "arguments_sha256,tool_call_id) VALUES (%s,%s,%s,%s,1,1,'tool',%s,%s,%s,%s,%s)")
        rows = (
            ("tool-with-provider", base, (self.activity, "X1", str(uuid4()), "executor092", "p", ["finite_calculate"], 0, "a" * 64, "c")),
            ("tool-with-cost", base, (self.activity, "X2", str(uuid4()), "executor092", None, ["finite_calculate"], 5, "a" * 64, "c")),
            ("tool-wrong-tools", base, (self.activity, "X3", str(uuid4()), "executor092", None, ["other"], 0, "a" * 64, "c")),
            ("tool-missing-digest", base, (self.activity, "X4", str(uuid4()), "executor092", None, ["finite_calculate"], 0, None, "c")),
            ("tool-bad-digest", base, (self.activity, "X5", str(uuid4()), "executor092", None, ["finite_calculate"], 0, "Z" * 64, "c")),
            ("tool-missing-call", base, (self.activity, "X6", str(uuid4()), "executor092", None, ["finite_calculate"], 0, "a" * 64, None)),
        )
        for label, sql, params in rows:
            with self.subTest(label=label):
                with self.assertRaises(self.psycopg.Error):
                    await self.sql(sql, params)
        with self.assertRaises(self.psycopg.Error):
            await self.sql("INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,"
                           "execution_generation,scope_revision,provider,tool_names,reserved_cost_microunits) "
                           "VALUES (%s,'M1',%s,'executor092',1,1,NULL,'{}',0)",
                           (self.activity, str(uuid4())))
        # 工具行不允许任何模型元数据（触发器无、直接写 finish_reason）。
        with self.assertRaises(self.psycopg.Error):
            await self.sql("INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,"
                           "execution_generation,scope_revision,kind,tool_names,reserved_cost_microunits,"
                           "arguments_sha256,tool_call_id,finish_reason) VALUES "
                           "(%s,'X7',%s,'executor092',1,1,'tool',ARRAY['finite_calculate'],0,%s,'c','stop')",
                           (self.activity, str(uuid4()), "a" * 64))
        # 工具行标志与真实 admit 落行一致：kind/tool_names/摘要/call_id 且成本0。
        row = (await self.op_rows(operation_id="T1"))[0]
        self.assertEqual(row["kind"], "tool")
        self.assertEqual(list(row["tool_names"]), ["finite_calculate"])
        self.assertEqual(row["reserved_cost_microunits"], 0)
        self.assertEqual(row["arguments_sha256"], call.arguments_sha256)
        self.assertEqual(row["tool_call_id"], "calc.1")
        self.assertEqual((row["provider"], row["configured_model"], row["request_bytes"], row["max_output_tokens"]), (None, None, None, None))
        del permit

    async def test_c1_budget_check_rejections_and_repeat_008_rollback(self):
        # 已用1 时不能再被事后置 NULL（balance CHECK 拒绝）。
        lease = await self.claim()
        await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="T1")))
        with self.assertRaises(self.psycopg.Error):
            await self.sql("UPDATE activities SET max_tool_calls=NULL WHERE id=%s", (self.activity,))
        # 未使用的新活动：NULL 合法，回填上限同样合法。
        fresh = str(uuid4())
        self.ids.append(fresh)
        await self.create(fresh)
        await self.sql("UPDATE activities SET max_tool_calls=NULL WHERE id=%s", (fresh,))
        self.assertIsNone((await self.account(fresh))["max_tool_calls"])
        await self.sql("UPDATE activities SET max_tool_calls=4 WHERE id=%s", (fresh,))
        # 重复 008：整事务回滚，列与数据保持。
        migration = (MIGRATIONS / "008_activity_tool_budget.sql").read_text(encoding="utf-8")
        with self.assertRaises(self.psycopg.Error):
            await self.sql(migration)
        columns = await self.rows(
            "SELECT column_name FROM information_schema.columns WHERE table_name='activities' "
            "AND column_name IN ('max_tool_calls','tools_reserved')")
        self.assertEqual(len(columns), 2)
        self.assertEqual((await self.account())["max_tool_calls"], 4)
        self.assertEqual((await self.account())["tools_reserved"], 1)

    # -- C2 参数与凭证绑定 ----------------------------------------------------

    async def test_c2_mark_and_record_reject_wrong_identity(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        permit = await self.ledger.admit_tool_operation(self.tool_intent(lease, call))
        other = make_call(operation_id="T1", call_id="calc.2")
        with self.assertRaisesRegex(AdmissionDenied, "admission_permit_mismatch"):
            await self.ledger.mark_tool_started(permit, other)
        # 伪造摘要输入在规范重校验处即拒绝，且未进入事务（行保持 reserved）。
        forged = ToolExecutionInput("T1", "calc.1", "finite_calculate",
                                    '{"left":1,"operation":"add","right":2}', "b" * 64)
        with self.assertRaisesRegex(AdmissionDenied, "invalid_input"):
            await self.ledger.mark_tool_started(permit, forged)
        self.assertEqual((await self.op_rows(operation_id="T1"))[0]["state"], "reserved")
        with self.assertRaisesRegex(AdmissionDenied, "invalid_input"):
            await self.ledger.record_tool_outcome(permit, forged, LedgerOutcome(
                LedgerDisposition.UNKNOWN, error_code="diagnostic"))
        # 旧三字段模型凭证包装真实工具准入：拒绝。
        legacy = AdmissionPermit(permit.admission_id, permit.operation_id, permit.executor_id)
        with self.assertRaisesRegex(AdmissionDenied, "准入凭证"):
            await self.ledger.mark_dispatch_started(legacy)
        # 反向：工具凭证操作模型行拒绝（锁内kind复核，凭证与调用身份自洽）。
        model_lease = lease
        model_call = AdmissionIntent(self.context(model_lease, "M2"),
                                     Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model", 512, 40, ())
        model_permit = await self.ledger.admit(model_call)
        m2call = make_call(operation_id="M2", call_id="calc.9")
        tool_permit_for_model = ToolAdmissionPermit(
            model_permit.admission_id, model_permit.operation_id, model_permit.executor_id,
            self.activity, model_lease.execution_generation, model_lease.scope_revision,
            "finite_calculate", "calc.9", m2call.arguments_sha256)
        with self.assertRaisesRegex(AdmissionDenied, "admission_permit_mismatch"):
            await self.ledger.mark_tool_started(tool_permit_for_model, m2call)
        # 正确身份可 mark；第二次 mark 拒绝且不给执行资格。
        await self.ledger.mark_tool_started(permit, call)
        with self.assertRaisesRegex(AdmissionDenied, "start_qualification_consumed"):
            await self.ledger.mark_tool_started(permit, call)

    # -- C3 权限与有限计数 ----------------------------------------------------

    async def test_c3_whitelist_null_zero_and_exhaustion(self):
        lease = await self.claim()
        # 白名单缺名。
        await self.sql("UPDATE activities SET allowed_tools='{}' WHERE id=%s", (self.activity,))
        with self.assertRaisesRegex(AdmissionDenied, "tool_not_allowed"):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="T1")))
        await self.sql("UPDATE activities SET allowed_tools=ARRAY['finite_calculate']::VARCHAR(64)[] WHERE id=%s", (self.activity,))
        # NULL 未配置。
        await self.sql("UPDATE activities SET max_tool_calls=NULL WHERE id=%s", (self.activity,))
        with self.assertRaisesRegex(AdmissionDenied, "tool_limit_unconfigured"):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="T1")))
        # 零额度。
        await self.sql("UPDATE activities SET max_tool_calls=0 WHERE id=%s", (self.activity,))
        with self.assertRaisesRegex(AdmissionDenied, "tool_limit_exhausted"):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="T1")))
        # 正额 2 恰好两次；第三次拒绝；重连后不重置。
        await self.sql("UPDATE activities SET max_tool_calls=2 WHERE id=%s", (self.activity,))
        for key in ("A1", "A2"):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id=key)))
        ledger2 = PostgresAdmissionLedger(DSN)
        with self.assertRaisesRegex(AdmissionDenied, "tool_limit_exhausted"):
            await ledger2.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="A3")))
        account = await self.account()
        self.assertEqual(account["tools_reserved"], 2)
        self.assertEqual(account["requests_reserved"], 0)
        self.assertEqual(account["cost_reserved_microunits"], 0)
        self.assertEqual(len(await self.op_rows()), 2)
        # admit 无操作行残留：第三条没有新的 op。
        self.assertEqual([r["operation_id"] for r in await self.op_rows()], ["A1", "A2"])

    async def test_c3_rejected_admit_leaves_no_trace_and_no_refund_of_unknown(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        await self.ledger.admit_tool_operation(self.tool_intent(lease, call))
        # 已准入未 mark：工具额度已用，不退款；收敛 unknown 不改计数。
        await self.sql("UPDATE activities SET lease_expires_at=now()-interval '1 second' WHERE id=%s", (self.activity,))
        moved = await self.ledger.recover_unknown(self.activity)
        self.assertEqual(moved, 1)
        account = await self.account()
        self.assertEqual(account["tools_reserved"], 1)
        row = (await self.op_rows(operation_id="T1"))[0]
        self.assertEqual((row["state"], row["disposition"], row["error_code"]), ("unknown", "unknown", "executor_lost"))
        self.assertEqual(await self.rows("SELECT 1 FROM activity_operation_results WHERE activity_id=%s", (self.activity,)), [])

    # -- C4 同键竞争与实际执行 ------------------------------------------------

    async def test_c4_same_key_two_connections_single_permit_and_execution(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        ledger_a, ledger_b = self.ledger, PostgresAdmissionLedger(DSN)
        start = asyncio.Event()

        async def go(ledger):
            await start.wait()
            try:
                return await ledger.admit_tool_operation(self.tool_intent(lease, call))
            except AdmissionDenied as exc:
                return exc

        tasks = [asyncio.create_task(go(ledger_a)), asyncio.create_task(go(ledger_b))]
        start.set()
        results = await asyncio.gather(*tasks)
        permits = [x for x in results if isinstance(x, ToolAdmissionPermit)]
        denied = [x for x in results if isinstance(x, AdmissionDenied)]
        self.assertEqual(len(permits), 1)
        self.assertEqual(str(denied[0]), "operation_already_exists")
        self.assertEqual((await self.account())["tools_reserved"], 1)
        # 胜者 mark 后恰执行一次真实有限计算（从规范输入重建计划）；无第二份执行资格。
        tools = CountingToolRegistry()
        await self.ledger.mark_tool_started(permits[0], call)
        plan = ToolRegistry().plan(call.call_id, call.name, call.arguments_json, frozenset({call.name}))
        rendered = tools.execute(plan)
        self.assertEqual((rendered, tools.executions), ("3", 1))
        fmt, payload, sha = build_business_payload(text=rendered)
        recorded = await self.ledger.record_tool_outcome(permits[0], call, LedgerOutcome(
            LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        self.assertIs(recorded, RecordOutcome.RECORDED)
        # 同键同身份再次显式动作只读，无第二扣次。
        with self.assertRaisesRegex(AdmissionDenied, "operation_already_exists"):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, call))
        changed = make_call(operation_id="T1", call_id="calc.2")
        with self.assertRaisesRegex(AdmissionDenied, "tool_input_conflict"):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, changed))
        self.assertEqual((await self.account())["tools_reserved"], 1)

    async def test_c4_model_key_occupied_and_winner_crash_zero_execution(self):
        lease = await self.claim()
        model_permit = await self.ledger.admit(AdmissionIntent(
            self.context(lease, "K1"), Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model", 512, 40, ()))
        del model_permit
        with self.assertRaisesRegex(AdmissionDenied, "operation_key_conflict"):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="K1")))
        # 独立活动：胜者崩溃（无 mark）→ 实际执行 0，T=1 保留。
        crash_activity = str(uuid4())
        self.ids.append(crash_activity)
        await self.create(crash_activity)
        crash_lease = await self.claim(crash_activity)
        tools = CountingToolRegistry()
        permit = await self.ledger.admit_tool_operation(
            self.tool_intent(crash_lease, make_call(operation_id="T1"), activity=crash_activity))
        self.assertIsInstance(permit, ToolAdmissionPermit)
        await self.sql("UPDATE activities SET lease_expires_at=now()-interval '1 second' WHERE id=%s", (crash_activity,))
        await self.ledger.recover_unknown(crash_activity)
        self.assertEqual(tools.executions, 0)
        self.assertEqual((await self.account(crash_activity))["tools_reserved"], 1)
        self.assertEqual((await self.op_rows(crash_activity, "T1"))[0]["state"], "unknown")

    # -- C5 类型隔离 ----------------------------------------------------------

    async def test_c5_read_list_typed_and_parent_isolation(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        # 一次完整受控执行造出真实工具received正文（admit/mark/execute/record）。
        tools = CountingToolRegistry()
        result = await ControlledToolExecutor(self.ledger, tools=tools).call(self.context(lease, "T1"), call)
        self.assertIs(result.status, ToolCallStatus.SUCCEEDED)
        self.assertEqual(tools.executions, 1)
        snapshot = await self.ledger.read_committed_result(self.activity, "T1")
        self.assertEqual(snapshot.read_status, ResultReadStatus.COMMITTED_CURRENT)
        self.assertEqual(snapshot.kind, "tool")
        self.assertEqual(snapshot.tool_call_id, "calc.1")
        self.assertEqual(snapshot.arguments_sha256, call.arguments_sha256)
        self.assertEqual(tuple(snapshot.tool_names), ("finite_calculate",))
        self.assertEqual(snapshot.payload, '{"format":"text","value":"3"}')
        page = await self.ledger.list_committed_results(self.activity)
        self.assertEqual([x.kind for x in page], ["tool"])
        self.assertIsNone(page[0].payload)
        # 服务层：工具父拒绝且零监督。
        service = ActivityService(self.ledger)
        with patch("app.worker.one_call.run_one_call", side_effect=AssertionError("supervised")) as invoke:
            outcome = await service.continue_from_result(
                self.activity, "T1", "Q", "followup", _service(), SessionConfig(), "executor092", "run092")
        self.assertEqual(outcome.status, "result_kind_not_consumable")
        invoke.assert_not_called()
        # 仓储锁内：直接构造正确 scope/hash 引用、allowed_tools 为空也拒绝，无新模型行/预留。
        from app.capabilities.contracts import ResultConsumptionRef
        ref = ResultConsumptionRef(activity_id=self.activity, operation_id="T1",
                                   scope_revision=snapshot.scope_revision,
                                   payload_sha256=snapshot.payload_sha256)
        before = await self.account()
        intent = AdmissionIntent(self.context(lease, "Q"), Provider.DEEPSEEK_CHAT_COMPLETIONS,
                                 "synthetic-model", 512, 40, (), ref)
        with self.assertRaisesRegex(AdmissionDenied, "result_kind_not_consumable"):
            await self.ledger.admit(intent)
        self.assertEqual(before, await self.account())
        self.assertEqual(await self.op_rows(operation_id="Q"), [])
        # 对照：合法 model 父可正常续接准入。
        model_permit = await self.ledger.admit(AdmissionIntent(
            self.context(lease, "P"), Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model", 512, 40, ()))
        await self.ledger.mark_dispatch_started(model_permit)
        fmt, payload, sha = build_business_payload(text="model-answer")
        await self.ledger.record_outcome(model_permit, LedgerOutcome(
            LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        p_ref = ResultConsumptionRef(activity_id=self.activity, operation_id="P",
                                     scope_revision=snapshot.scope_revision, payload_sha256=sha)
        p_permit = await self.ledger.admit(AdmissionIntent(
            self.context(lease, "Q2"), Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model", 512, 40, (), p_ref))
        self.assertEqual(p_permit.operation_id, "Q2")

    # -- C6 admit/mark 边界故障 -----------------------------------------------

    async def test_c6_admit_and_mark_commit_boundaries(self):
        lease = await self.claim()
        # admit COMMIT 后丢响应：reserved/T1，不重新 admit。
        class LostAdmit(PostgresAdmissionLedger):
            async def admit_tool_operation(self, intent):
                await super().admit_tool_operation(intent)
                raise AdmissionUnavailable("synthetic response loss after commit")

        call = make_call(operation_id="T1")
        with self.assertRaises(AdmissionUnavailable):
            await LostAdmit(DSN).admit_tool_operation(self.tool_intent(lease, call))
        account = await self.account()
        self.assertEqual(account["tools_reserved"], 1)
        self.assertEqual((await self.op_rows(operation_id="T1"))[0]["state"], "reserved")
        # admit COMMIT 前失败（触发器）：无行/T0，整体回滚。
        await self._trigger("activity_operations", "BEFORE INSERT", "task092_fail_admit")
        try:
            with self.assertRaises(AdmissionUnavailable):
                await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="T2")))
        finally:
            await self._drop_trigger("activity_operations", "task092_fail_admit")
        self.assertEqual((await self.account())["tools_reserved"], 1)
        self.assertEqual(await self.op_rows(operation_id="T2"), [])
        # mark COMMIT 前失败：状态仍 reserved、T1、无执行资格。
        prepared = await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="T3")))
        await self._trigger("activity_operations", "BEFORE UPDATE", "task092_fail_mark")
        try:
            with self.assertRaises(AdmissionUnavailable):
                await self.ledger.mark_tool_started(prepared, make_call(operation_id="T3"))
        finally:
            await self._drop_trigger("activity_operations", "task092_fail_mark")
        row = (await self.op_rows(operation_id="T3"))[0]
        self.assertEqual(row["state"], "reserved")
        self.assertIsNone(row["dispatch_started_at"])
        # mark COMMIT 后丢响应：dispatched/T1，之后逐事务事实可只读核对。
        class LostMark(PostgresAdmissionLedger):
            async def mark_tool_started(self, permit, call):
                await super().mark_tool_started(permit, call)
                raise AdmissionUnavailable("synthetic response loss after commit")

        call_t4 = make_call(operation_id="T4")
        permit_t4 = await self.ledger.admit_tool_operation(self.tool_intent(lease, call_t4))
        with self.assertRaises(AdmissionUnavailable):
            await LostMark(DSN).mark_tool_started(permit_t4, call_t4)
        self.assertEqual((await self.op_rows(operation_id="T4"))[0]["state"], "dispatched")
        # 三个未决操作（T1/T3 reserved、T4 dispatched）收敛 unknown 均无成功正文；计数不退。
        await self.sql("UPDATE activities SET lease_expires_at=now()-interval '1 second' WHERE id=%s", (self.activity,))
        moved = await self.ledger.recover_unknown(self.activity)
        self.assertEqual(moved, 3)
        self.assertEqual((await self.account())["tools_reserved"], 3)
        self.assertEqual(await self.rows(
            "SELECT 1 FROM activity_operation_results WHERE activity_id=%s", (self.activity,)), [])

    async def _trigger(self, table, timing, name):
        async with await self.psycopg.AsyncConnection.connect(DSN) as c:
            await c.execute(
                f"""CREATE OR REPLACE FUNCTION {name}() RETURNS trigger LANGUAGE plpgsql AS $$
                     BEGIN RAISE EXCEPTION 'synthetic {name} failure'; END $$""")
            await c.execute(
                f"CREATE TRIGGER {name} {timing} ON {table} FOR EACH ROW EXECUTE FUNCTION {name}()")

    async def _drop_trigger(self, table, name):
        async with await self.psycopg.AsyncConnection.connect(DSN) as c:
            await c.execute(f"DROP TRIGGER IF EXISTS {name} ON {table}")
            await c.execute(f"DROP FUNCTION IF EXISTS {name}()")

    # -- C7 执行后未提交 ------------------------------------------------------

    async def permit_from_row(self, operation_id):
        row = (await self.op_rows(operation_id=operation_id))[0]
        return ToolAdmissionPermit(str(row["admission_id"]), row["operation_id"], row["executor_id"],
                                   str(row["activity_id"]), row["execution_generation"],
                                   row["scope_revision"], row["tool_names"][0], row["tool_call_id"],
                                   row["arguments_sha256"])

    async def test_c7_executed_but_record_uncommitted_stays_unknown_no_overwrite(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        # 实际计算发生（本地计数1）后 record 事务提交前失败：无 results、dispatched 保留。
        tools = CountingToolRegistry()
        await self._trigger("activity_operation_results", "BEFORE INSERT", "task092_fail_record")
        try:
            # 真实受控执行器但 record 命中触发器：未确认提交，不冒成功。
            result = await ControlledToolExecutor(self.ledger, tools=tools).call(self.context(lease, "T1"), call)
        finally:
            await self._drop_trigger("activity_operation_results", "task092_fail_record")
        self.assertEqual(tools.executions, 1)
        self.assertIs(result.status, ToolCallStatus.UNKNOWN)
        self.assertEqual(result.error_code, "record_unconfirmed")
        row = (await self.op_rows(operation_id="T1"))[0]
        self.assertEqual(row["state"], "dispatched")
        self.assertEqual((await self.account())["tools_reserved"], 1)
        self.assertEqual(await self.rows(
            "SELECT 1 FROM activity_operation_results WHERE activity_id=%s", (self.activity,)), [])
        # 恢复 unknown；同键成功正文不能覆盖 unknown、也不能 ALREADY_PRESENT。
        await self.sql("UPDATE activities SET lease_expires_at=now()-interval '1 second' WHERE id=%s", (self.activity,))
        await self.ledger.recover_unknown(self.activity)
        permit = await self.permit_from_row("T1")
        fmt, payload, sha = build_business_payload(text="3")
        with self.assertRaisesRegex(AdmissionDenied, "已终结调用不能覆盖为不同结果"):
            await self.ledger.record_tool_outcome(permit, call, LedgerOutcome(
                LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        snapshot = await self.ledger.read_committed_result(self.activity, "T1")
        self.assertEqual(snapshot.read_status, ResultReadStatus.UNRESOLVED)
        self.assertIsNone(snapshot.payload)
        # 确定计算失败：received + tool_execution_failed、无正文；窗口可独立结算。
        lease2 = await self.claim()  # 旧租约已过期：重领折叠一次 R 后开新窗。
        self.assertEqual((await self.account())["tools_reserved"], 1)
        call2 = make_call(operation_id="T2")
        permit2 = await self.ledger.admit_tool_operation(self.tool_intent(lease2, call2))
        await self.ledger.mark_tool_started(permit2, call2)
        await self.ledger.record_tool_outcome(permit2, call2, LedgerOutcome(
            LedgerDisposition.RECEIVED, error_code="tool_execution_failed"))
        row2 = (await self.op_rows(operation_id="T2"))[0]
        self.assertEqual((row2["state"], row2["disposition"], row2["error_code"]), ("received", "received", "tool_execution_failed"))
        self.assertEqual(await self.rows(
            "SELECT 1 FROM activity_operation_results WHERE activity_id=%s AND operation_id='T2'", (self.activity,)), [])
        await self.ledger.begin_window_close(self.activity, lease2.executor_id, lease2.execution_generation)
        settled = await self.ledger.settle_execution_window(
            self.activity, lease2.executor_id, lease2.execution_generation, window_seconds=30, elapsed_seconds=1)
        self.assertIs(settled, SettleResult.SETTLED)
        self.assertEqual((await self.account())["tools_reserved"], 2)

    # -- C8 record 已提交丢响应 ----------------------------------------------

    async def test_c8_committed_record_response_loss_and_write_free_confirmation(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        permit = await self.ledger.admit_tool_operation(self.tool_intent(lease, call))
        await self.ledger.mark_tool_started(permit, call)
        fmt, payload, sha = build_business_payload(text="3")
        outcome = LedgerOutcome(LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha)
        original = self.ledger._transaction

        async def lose(operation):
            await original(operation)
            raise AdmissionUnavailable("synthetic response loss after commit")

        with patch.object(self.ledger, "_transaction", lose):
            with self.assertRaises(AdmissionUnavailable):
                await self.ledger.record_tool_outcome(permit, call, outcome)
        # 持久事实：received+正文；只读确认正文与 typed hash。
        snapshot = await self.ledger.read_committed_result(self.activity, "T1")
        self.assertEqual(snapshot.read_status, ResultReadStatus.COMMITTED_CURRENT)
        self.assertEqual(snapshot.payload, payload)
        self.assertEqual(snapshot.payload_sha256, sha)
        self.assertEqual(snapshot.kind, "tool")
        # 直接同凭证/参数/完整终态等值确认：ALREADY_PRESENT、无新写。
        before = await self.rows(
            "SELECT xmin::text AS xmin, state FROM activity_operations WHERE activity_id=%s AND operation_id='T1'", (self.activity,))
        confirm = await self.ledger.record_tool_outcome(permit, call, outcome)
        self.assertIs(confirm, RecordOutcome.ALREADY_PRESENT)
        after = await self.rows(
            "SELECT xmin::text AS xmin, state FROM activity_operations WHERE activity_id=%s AND operation_id='T1'", (self.activity,))
        self.assertEqual(before, after)
        # 异文拒绝；received 无正文补写拒绝。
        fmt2, payload2, sha2 = build_business_payload(text="4")
        with self.assertRaisesRegex(AdmissionDenied, "已终结正文与提交不一致"):
            await self.ledger.record_tool_outcome(permit, call, LedgerOutcome(
                LedgerDisposition.RECEIVED, payload_format=fmt2, payload=payload2, payload_sha256=sha2))
        call3 = make_call(operation_id="T3")
        permit3 = await self.ledger.admit_tool_operation(self.tool_intent(lease, call3))
        await self.ledger.mark_tool_started(permit3, call3)
        await self.ledger.record_tool_outcome(permit3, call3, LedgerOutcome(LedgerDisposition.RECEIVED))
        with self.assertRaisesRegex(AdmissionDenied, "已终结无正文状态不能补写正文"):
            await self.ledger.record_tool_outcome(permit3, call3, LedgerOutcome(
                LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        # 非规范工具正文（json 或非原精度十进制）直接拒绝。
        bad = LedgerOutcome(LedgerDisposition.RECEIVED, payload_format="json",
                            payload='{"format":"json","value":{"a":1}}',
                            payload_sha256=payload_digest({"format": "json", "value": {"a": 1}}))
        call4 = make_call(operation_id="T4")
        permit4 = await self.ledger.admit_tool_operation(self.tool_intent(lease, call4))
        await self.ledger.mark_tool_started(permit4, call4)
        with self.assertRaisesRegex(AdmissionDenied, "invalid_tool_payload"):
            await self.ledger.record_tool_outcome(permit4, call4, bad)
        # 数值非原精度 50 规范串（"3.0"）同样拒绝，且未落任何行。
        text_payload = '{"format":"text","value":"3.0"}'
        bad2 = LedgerOutcome(LedgerDisposition.RECEIVED, payload_format="text",
                             payload=text_payload,
                             payload_sha256=payload_digest({"format": "text", "value": "3.0"}))
        with self.assertRaisesRegex(AdmissionDenied, "invalid_tool_payload"):
            await self.ledger.record_tool_outcome(permit4, call4, bad2)
        self.assertEqual((await self.op_rows(operation_id="T4"))[0]["state"], "dispatched")

    # -- C9 资格变更与取消 ----------------------------------------------------

    async def test_c9_scope_cas_variants_and_mark_gate(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        # 4a：CAS 完成 → admit 用旧 context 拒 scope_changed，T 不变。
        second = await self.new_source()
        await self.ledger.revise_scope(self.activity, 1, (second,))
        before = await self.account()
        with self.assertRaisesRegex(AdmissionDenied, "scope_changed"):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, call))
        self.assertEqual(before, await self.account())
        # 4b：读旧提示后暂停、CAS 提交不相交新集合、恢复事务抛 ScopeConflict 整事务回滚。
        fresh = str(uuid4())
        self.ids.append(fresh)
        await self.create(fresh)
        fresh_lease = await self.claim(fresh)
        ledger_a = PostgresAdmissionLedger(DSN)
        paused, resume = asyncio.Event(), asyncio.Event()
        real_lock = ledger_a._lock_sources

        async def barrier_lock(connection, snapshots):
            if not resume.is_set():
                paused.set()
                await resume.wait()
            return await real_lock(connection, snapshots)

        ledger_a._lock_sources = barrier_lock
        third = await self.new_source()
        task = asyncio.create_task(ledger_a.admit_tool_operation(
            self.tool_intent(fresh_lease, make_call(operation_id="B1"), activity=fresh)))
        try:
            # 屏障：旧事务已读提示但尚未加锁时暂停；另一连接提交不相交新集合。
            await asyncio.wait_for(paused.wait(), timeout=10)
            await self.ledger.revise_scope(fresh, 1, (third,))
        finally:
            resume.set()
        with self.assertRaises(AdmissionDenied) as caught:
            await asyncio.wait_for(task, timeout=10)
        self.assertEqual(str(caught.exception), "scope_conflict")
        self.assertEqual((await self.account(fresh))["tools_reserved"], 0)
        self.assertEqual(await self.op_rows(fresh), [])
        # 4c：admit 已提交后 CAS → mark 拒绝、资格失效；正文不新写、T 保留。
        # 4a 已把活动 scope 修订为 2：admit 需用当前 revision 的上下文（租约/G 未变）。
        call_t2 = make_call(operation_id="T2")
        context_t2 = CallContext(activity_id=self.activity, operation_id="T2",
                                 executor_id=lease.executor_id,
                                 execution_generation=lease.execution_generation,
                                 scope_revision=2)
        permit = await self.ledger.admit_tool_operation(ToolIntent(context=context_t2, call=call_t2))
        fourth = await self.new_source()
        await self.ledger.revise_scope(self.activity, 2, (fourth,))
        with self.assertRaisesRegex(AdmissionDenied, "qualification_invalid"):
            await self.ledger.mark_tool_started(permit, call_t2)
        self.assertEqual((await self.account())["tools_reserved"], 1)
        # cancel：首条留 reserved，cancel 全额折叠一次，重复 cancel 不重复折叠，工具计数不动。
        await self.ledger.cancel_activity(self.activity)
        account = await self.account()
        self.assertEqual(account["status"], "cancelled")
        self.assertEqual(account["running_reserved_seconds"], 0)
        self.assertEqual(account["tools_reserved"], 1)
        folded = account["running_settled_seconds"]
        self.assertGreaterEqual(folded, 1)
        await self.ledger.cancel_activity(self.activity)
        self.assertEqual((await self.account())["running_settled_seconds"], folded)
        with self.assertRaises(AdmissionDenied):
            await self.ledger.admit_tool_operation(self.tool_intent(lease, make_call(operation_id="T9")))
        # UNKNOWN 诊断仍可写；成功正文不能。
        await self.ledger.record_tool_outcome(permit, call_t2, LedgerOutcome(
            LedgerDisposition.UNKNOWN, error_code="scope_changed"))
        self.assertEqual((await self.op_rows(operation_id="T2"))[0]["state"], "unknown")
        fmt, payload, sha = build_business_payload(text="3")
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_tool_outcome(permit, call_t2, LedgerOutcome(
                LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))

    # -- C12 目标项：关门/结算与工具账独立 ------------------------------------

    async def test_c12_settle_and_close_facts_with_tool_budget(self):
        lease = await self.claim()
        call = make_call(operation_id="T1")
        permit = await self.ledger.admit_tool_operation(self.tool_intent(lease, call))
        await self.ledger.mark_tool_started(permit, call)
        fmt, payload, sha = build_business_payload(text="3")
        await self.ledger.record_tool_outcome(permit, call, LedgerOutcome(
            LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        # close 丢响应不先退款：同身份显式确认 ALREADY_CLOSED。
        class LostClose(PostgresAdmissionLedger):
            async def begin_window_close(self, activity_id, executor_id, execution_generation):
                await super().begin_window_close(activity_id, executor_id, execution_generation)
                raise AdmissionUnavailable("synthetic response loss after commit")

        with self.assertRaises(AdmissionUnavailable):
            await LostClose(DSN).begin_window_close(self.activity, lease.executor_id, lease.execution_generation)
        account = await self.account()
        self.assertTrue(account["dispatch_closed"])
        self.assertEqual(account["running_reserved_seconds"], 30)
        from app.activities import CloseResult, SettleResult
        self.assertIs(await self.ledger.begin_window_close(self.activity, lease.executor_id, lease.execution_generation),
                      CloseResult.ALREADY_CLOSED)
        # settle 提交后丢响应：同 G/W/C 有限一次 ALREADY_SETTLED，账只变一次。
        class LostSettle(PostgresAdmissionLedger):
            async def settle_execution_window(self, activity_id, executor_id, execution_generation, *, window_seconds, elapsed_seconds):
                await super().settle_execution_window(activity_id, executor_id, execution_generation,
                                                       window_seconds=window_seconds, elapsed_seconds=elapsed_seconds)
                raise AdmissionUnavailable("synthetic response loss after commit")

        with self.assertRaises(AdmissionUnavailable):
            await LostSettle(DSN).settle_execution_window(
                self.activity, lease.executor_id, lease.execution_generation, window_seconds=30, elapsed_seconds=2)
        again = await self.ledger.settle_execution_window(
            self.activity, lease.executor_id, lease.execution_generation, window_seconds=30, elapsed_seconds=2)
        self.assertIs(again, SettleResult.ALREADY_SETTLED)
        with self.assertRaises(ActivityLedgerConflict):
            await self.ledger.settle_execution_window(
                self.activity, lease.executor_id, lease.execution_generation, window_seconds=30, elapsed_seconds=3)
        account = await self.account()
        self.assertEqual(account["running_settled_seconds"], 2)
        self.assertEqual(account["running_reserved_seconds"], 0)
        self.assertEqual(account["tools_reserved"], 1)
        # 业务UNKNOWN但时间已结算可并存：独立事实。
        snapshot = await self.ledger.read_committed_result(self.activity, "T1")
        self.assertEqual(snapshot.read_status, ResultReadStatus.COMMITTED_CURRENT)


class ArgumentLengthBoundaryTests(unittest.TestCase):
    """E1（续作03）：2048字节边界的真实可达路径与阶段可分性；纯离线。

    区分两条真实路径：ToolRegistry.plan 收原始JSON字符串（长度按UTF8字节先行
    拒绝）；ToolExecutionInput.to_wire/from_wire 收严格规范字节，长度通过后
    仍要求逐字节规范等值。合法规范参数受Schema约束（三标量、|数值|<=1e12），
    最大长度远低于2048字节——2048规范参数不可达，其长度分支为纵深防御，
    以可达性依据作证，不伪造"2048规范参数成功"样本。
    """

    BASE = '{"operation":"add","left":1,"right":2}'
    CANONICAL = '{"left":1,"operation":"add","right":2}'
    DIGEST_PLACEHOLDER = "0" * 64

    def test_raw_json_plan_path_exact_2048_pass_and_2049_length_reject(self):
        raw2048 = self.BASE + " " * (2048 - len(self.BASE.encode("utf-8")))
        self.assertEqual(len(raw2048.encode("utf-8")), 2048)
        plan = ToolRegistry().plan("calc.1", "finite_calculate", raw2048, frozenset({"finite_calculate"}))
        self.assertEqual(plan.arguments, {"operation": "add", "left": 1, "right": 2})
        # 该路径不是规范wire：含合法JSON空白的原始串与紧凑规范字节（键序左/运算/右）不同。
        canonical, _ = canonical_tool_arguments({"operation": "add", "left": 1, "right": 2})
        self.assertEqual(canonical, self.CANONICAL)
        self.assertNotEqual(raw2048, canonical)
        raw2049 = raw2048 + " "
        self.assertEqual(len(raw2049.encode("utf-8")), 2049)
        with self.assertRaises(ToolValidationError) as caught:
            ToolRegistry().plan("calc.1", "finite_calculate", raw2049, frozenset({"finite_calculate"}))
        self.assertEqual(str(caught.exception), "工具参数不是有界 JSON 字符串")

    def test_canonical_wire_boundary_to_wire_and_from_wire_stages(self):
        short = make_call(operation_id="T1")
        wire = short.to_wire()
        self.assertEqual(ToolExecutionInput.from_wire(wire), short)
        # 2049字节：to_wire/from_wire 都在长度阶段拒绝（解析前）。
        raw2049 = self.BASE + " " * (2049 - len(self.BASE.encode("utf-8")))
        with self.assertRaises(ValueError) as caught:
            ToolExecutionInput("T1", "calc.1", "finite_calculate", raw2049, self.DIGEST_PLACEHOLDER).to_wire()
        self.assertEqual(str(caught.exception), "tool arguments exceed limit")
        wire2049 = dict(wire, arguments_json=raw2049, arguments_sha256=self.DIGEST_PLACEHOLDER)
        with self.assertRaises(ValueError) as caught:
            ToolExecutionInput.from_wire(wire2049)
        self.assertEqual(str(caught.exception), "tool arguments exceed limit")
        # 精确2048字节非规范（空白填充）：长度放行后在规范等值阶段拒绝。
        raw2048 = raw2049[:-1]
        self.assertEqual(len(raw2048.encode("utf-8")), 2048)
        with self.assertRaises(ValueError) as caught:
            ToolExecutionInput("T1", "calc.1", "finite_calculate", raw2048, self.DIGEST_PLACEHOLDER).to_wire()
        self.assertEqual(str(caught.exception), "tool arguments not canonical")
        wire2048 = dict(wire, arguments_json=raw2048, arguments_sha256=self.DIGEST_PLACEHOLDER)
        with self.assertRaises(ValueError) as caught:
            ToolExecutionInput.from_wire(wire2048)
        self.assertEqual(str(caught.exception), "tool arguments not canonical")

    def test_multibyte_byte_count_not_character_count_and_stages(self):
        prefix = '{"operation":"add","left":1,"right":2,"pad":"'
        suffix = '"}'
        # 字节超限而字符未超：长度阶段按UTF8字节拒绝，不混同字符数。
        filler = "中" * ((2049 - len((prefix + suffix).encode("utf-8"))) // 3 + 1)
        raw = prefix + filler + suffix
        self.assertGreater(len(raw.encode("utf-8")), 2048)
        self.assertLess(len(raw), 2048)
        with self.assertRaises(ToolValidationError) as caught:
            ToolRegistry().plan("calc.1", "finite_calculate", raw, frozenset({"finite_calculate"}))
        self.assertEqual(str(caught.exception), "工具参数不是有界 JSON 字符串")
        # 精确2048字节（含多字节）：长度放行，由Schema阶段拒绝额外字段，阶段可分。
        remaining = 2048 - len((prefix + suffix).encode("utf-8"))
        cjk, spaces = divmod(remaining, 3)
        raw2 = prefix + "中" * cjk + " " * spaces + suffix
        self.assertEqual(len(raw2.encode("utf-8")), 2048)
        self.assertLess(len(raw2), 2048)
        with self.assertRaises(ToolValidationError) as caught:
            ToolRegistry().plan("calc.1", "finite_calculate", raw2, frozenset({"finite_calculate"}))
        self.assertEqual(str(caught.exception), "工具参数未通过精确 Schema 校验")

    def test_canonical_2048_unreachable_basis_defense_only(self):
        # 可达性依据：枚举最坏合法参数，规范字节最大长度远低于2048。
        candidates = []
        for operation in ("add", "subtract", "multiply", "divide", "power"):
            for number in (1000000000000, -1000000000000, 999999999999.9999, -999999999999.9999,
                           0.1, -0.1, 0.0001, 123456789012.34567, 1e-05, 1e12):
                candidates.append({"operation": operation, "left": number, "right": 2})
        best = max(len(canonical_tool_arguments(args)[0].encode("utf-8")) for args in candidates)
        self.assertLess(best, 128)
        self.assertLess(best, MAX_TOOL_ARGUMENT_BYTES)
        # 规范等值剥离原始空白：2048字节空白填充输入的规范形式仍是紧凑规范串。
        raw2048 = self.BASE + " " * (2048 - len(self.BASE.encode("utf-8")))
        parsed = parse_tool_arguments(raw2048)
        canonical, digest = canonical_tool_arguments(parsed)
        self.assertEqual(canonical, self.CANONICAL)
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
