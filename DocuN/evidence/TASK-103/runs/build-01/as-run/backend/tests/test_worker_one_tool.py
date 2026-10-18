"""TASK-092 受控 one_tool 工具链离线合同：编解码、回执与版本兼容。

不访问网络/数据库/Job；工具执行使用真实 ToolRegistry 于内存替身之上。
外2/外3与内3/内4的严格帧形状、身份绑定与三值提交确认逐项核对。
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.activities import ActivityLease
from app.capabilities.contracts import (
    CallContext,
    ToolCallResult,
    ToolCallStatus,
    ToolExecutionInput,
    canonical_tool_arguments,
)
from app.worker.command import WorkerCommand, _INTERPRETER
from app.worker.launcher import (
    ManagerControlError,
    _OUTER2_OUTCOME_FIELDS,
    _OUTER3_OUTCOME_FIELDS,
    _decode_outcome,
    _request,
)
from app.worker.one_call import OneCallInput, decode_worker_request, worker_request as model_worker_request
from app.worker.one_tool import (
    decode_tool_receipt,
    decode_tool_worker_request,
    run_one_tool,
    tool_receipt,
    worker_request_tool,
)
from app.worker.session import SessionConfig, SessionOutcome, SingleWindowSupervisor
from app.worker.supervisor_ipc import SLOT_SIZE, pack_frame, unpack_frame
from app.worker.supervisor_main import _validated_request
from app.worker.worker_main import execute_one_tool, main as worker_main
from app.worker.worker_main import run_internal_task
from app.activities import PostgresAdmissionLedger
from tests.test_worker_one_call import request as _model_request, service as _model_service


def make_call(operation_id="T1", call_id="calc.1", arguments=None):
    arguments = {"operation": "add", "left": 1, "right": 2} if arguments is None else arguments
    arguments_json, sha = canonical_tool_arguments(dict(arguments))
    return ToolExecutionInput(operation_id, call_id, "finite_calculate", arguments_json, sha)


def tool_frame(**overrides):
    lease = ActivityLease(str(uuid4()), "executor", 7, 3, None, 12, 1)
    frame = worker_request_tool(
        make_call(), dict(dsn="synthetic-dsn", connect_timeout_seconds=1,
                          statement_timeout_ms=500, lock_timeout_ms=100),
        lease, "run-092", time.monotonic_ns() + 10_000_000_000, 0.5)
    frame.update(overrides)
    return frame, lease


class OneToolCodecTests(unittest.IsolatedAsyncioTestCase):
    def test_fixed_worker_command_and_idle(self):
        argv = WorkerCommand("one_tool").argv("Local\\RetroLume.SUP." + "a" * 32)
        self.assertEqual(argv[:5], [str(_INTERPRETER), "-B", "-m", "app.worker.worker_main", "one_tool"])
        with self.assertRaises(ValueError):
            WorkerCommand("one_tool").argv()
        with self.assertRaises(ValueError):
            WorkerCommand("run_anything")
        with self.assertRaises(ValueError):
            WorkerCommand("idle").argv("Local\\RetroLume.SUP." + "a" * 32)
        self.assertEqual(WorkerCommand("idle").argv(), [str(_INTERPRETER), "-B", "-m", "app.worker.worker_main", "idle"])

    def test_worker_main_dispatch_rejects_unknown_and_missing_mapping(self):
        for argv, code in ((["worker_main"], 2), (["worker_main", "one_tool"], 2),
                           (["worker_main", "other", "Local\\RetroLume.SUP." + "a" * 32], 2)):
            with self.subTest(argv=argv):
                with patch.object(sys, "argv", argv):
                    self.assertEqual(worker_main(), 2)
        with patch.object(sys, "argv", ["worker_main", "idle"]):
            self.assertEqual(worker_main(), 0)

    def test_tool_request_frame_exact_fields_and_strict_decode(self):
        frame, lease = tool_frame()
        self.assertEqual(frame["protocol"], 4)
        call, context = decode_tool_worker_request(frame)
        self.assertEqual(call.operation_id, "T1")
        self.assertEqual(context.activity_id, lease.activity_id)
        self.assertEqual((context.execution_generation, context.scope_revision), (7, 3))
        # 参数只以不可变规范字节传输；对象 repr 不泄漏（帧本身是受控映射数据）。
        self.assertNotIn("left", repr(call))
        self.assertEqual(call.arguments_json, '{"left":1,"operation":"add","right":2}')
        mutators = (
            lambda x: x.update(protocol=3),
            lambda x: x.update(protocol=5),
            lambda x: x.update(extra=1),
            lambda x: x.pop("call_seconds"),
            lambda x: x["call"].update(arguments_sha256="0" * 64),
            lambda x: x["context"].update(operation_id="other"),
            lambda x: x["context"].update(execution_generation=0),
            lambda x: x["context"].update(execution_generation=True),
            lambda x: x["ledger"].update(extra=1),
            lambda x: x.update(call_seconds=121),
            lambda x: x.update(stop_ns=time.monotonic_ns() + 100_000),
            lambda x: x.update(run_tag="bad tag!"),
        )
        for mutate in mutators:
            item = json.loads(json.dumps(frame))
            mutate(item)
            with self.subTest(item=item), self.assertRaises(ValueError):
                decode_tool_worker_request(item)

    def test_tool_receipt_truth_table(self):
        context = CallContext(activity_id=str(uuid4()), operation_id="T1", executor_id="executor",
                              execution_generation=7, scope_revision=3)
        call = make_call()
        digest = "a" * 64
        good = ToolCallResult(ToolCallStatus.SUCCEEDED, "finite_calculate", "calc.1", call.arguments_sha256,
                              None, digest)
        frame = tool_receipt(good, context, "run-092")
        self.assertEqual(frame["protocol"], 4)
        self.assertEqual(set(frame), {"protocol", "context", "run_tag", "business_commit", "result"})
        self.assertEqual(frame["business_commit"], "committed")
        self.assertEqual(set(frame["result"]),
                         {"kind", "name", "call_id", "arguments_sha256", "status", "error_code", "payload_sha256"})
        decoded = decode_tool_receipt(json.loads(json.dumps(frame)), context, "run-092", call)
        self.assertEqual(decoded.payload_sha256, digest)
        self.assertEqual(decoded.arguments_sha256, call.arguments_sha256)
        # 成功缺 hash 属内部错误；非成功不得夹带 hash；unconfirmed 仅限 record 不确定且必须 unknown。
        for bad, exc in (
            (ToolCallResult(ToolCallStatus.SUCCEEDED, "finite_calculate", "calc.1", call.arguments_sha256), ValueError),
            (ToolCallResult(ToolCallStatus.FAILED, "finite_calculate", "calc.1", call.arguments_sha256,
                            "tool_execution_failed", digest), ValueError),
            (ToolCallResult(ToolCallStatus.UNKNOWN, "finite_calculate", "calc.1", call.arguments_sha256,
                            "record_denied", digest), ValueError),
        ):
            with self.assertRaises(exc):
                tool_receipt(bad, context, "run-092")
        for status, code, commit, digest_v in (
            (ToolCallStatus.UNKNOWN, "record_denied", "unconfirmed", None),
            (ToolCallStatus.UNKNOWN, "record_unconfirmed", "unconfirmed", None),
            (ToolCallStatus.UNKNOWN, "delivery_x", "not_committed", None),
            (ToolCallStatus.REJECTED, "tool_limit_exhausted", "not_committed", None),
            (ToolCallStatus.FAILED, "tool_execution_failed", "not_committed", None),
        ):
            with self.subTest(code=code):
                result = ToolCallResult(status, "finite_calculate", "calc.1", call.arguments_sha256, code, digest_v)
                frame = tool_receipt(result, context, "run-092")
                self.assertEqual(frame["business_commit"], commit)
                decoded = decode_tool_receipt(json.loads(json.dumps(frame)), context, "run-092", call)
                self.assertIs(decoded.status, status)

    def test_tool_receipt_mutations_rejected(self):
        context = CallContext(activity_id=str(uuid4()), operation_id="T1", executor_id="executor",
                              execution_generation=7, scope_revision=3)
        call = make_call()
        frame = tool_receipt(ToolCallResult(ToolCallStatus.SUCCEEDED, "finite_calculate", "calc.1",
                                            call.arguments_sha256, None, "a" * 64), context, "run-092")
        for mutate in (
            lambda x: x.update(protocol=3),
            lambda x: x["result"].update(kind="model"),
            lambda x: x["result"].update(call_id="calc.2"),
            lambda x: x["result"].update(name="other"),
            lambda x: x["result"].update(arguments_sha256="b" * 64),
            lambda x: x["result"].update(status="tool_plan"),
            lambda x: x["result"].update(extra=1),
            lambda x: x["result"].update(payload_sha256=None),
            lambda x: x.update(business_commit="not_committed"),
            lambda x: x["context"].update(execution_generation=6),
            lambda x: x.update(run_tag="other"),
            lambda x: x.update(extra=1),
        ):
            item = json.loads(json.dumps(frame))
            mutate(item)
            with self.subTest(item=item), self.assertRaises(ValueError):
                decode_tool_receipt(item, context, "run-092", call)
        # 帧经真实封套往返后仍可解。
        raw = pack_frame(frame).ljust(SLOT_SIZE, b"\0")
        decoded = decode_tool_receipt(unpack_frame(raw), context, "run-092", call)
        self.assertEqual(decoded.payload_sha256, "a" * 64)

    async def test_run_internal_task_one_tool_wraps_gate_and_timeout(self):
        events = []
        class Executor:
            async def call(self, context, call):
                events.append("execute")
                return ToolCallResult(ToolCallStatus.FAILED, call.name, call.call_id,
                                      call.arguments_sha256, "tool_execution_failed")
        result = await run_internal_task(Executor(), "one_tool", CallContext(
            activity_id=str(uuid4()), operation_id="T1", executor_id="executor",
            execution_generation=1, scope_revision=1), tool_call=make_call(), call_seconds=0.5)
        self.assertEqual(events, ["execute"])
        self.assertIs(result.status, ToolCallStatus.FAILED)
        with self.assertRaises(ValueError):
            await run_internal_task(Executor(), "one_tool")
        # 超时由闭包截止终止，不无限等待不合作的执行体。
        class Blocking:
            async def call(self, context, call):
                await asyncio.sleep(5)
        with self.assertRaises(TimeoutError):
            await run_internal_task(Blocking(), "one_tool", CallContext(
                activity_id=str(uuid4()), operation_id="T1", executor_id="executor",
                execution_generation=1, scope_revision=1), tool_call=make_call(), call_seconds=0.05)

    async def test_execute_one_tool_single_call_and_receipt(self):
        frame, lease = tool_frame()
        seen = {}
        class SyncExecutor:
            calls = 0
            async def call(self, context, call):
                SyncExecutor.calls += 1
                seen["context"] = context
                return ToolCallResult(ToolCallStatus.SUCCEEDED, call.name, call.call_id,
                                      call.arguments_sha256, None, "c" * 64)
        with patch("app.worker.worker_main.PostgresAdmissionLedger", return_value=object()), \
             patch("app.worker.worker_main.ControlledToolExecutor", return_value=SyncExecutor()):
            result = await execute_one_tool(frame)
        self.assertEqual(SyncExecutor.calls, 1)
        self.assertEqual(result["protocol"], 4)
        self.assertEqual(result["business_commit"], "committed")
        self.assertEqual(result["context"]["operation_id"], "T1")
        self.assertEqual(seen["context"].execution_generation, 7)
        # 窗口不足在构造ledger之前拒绝。
        short = json.loads(json.dumps(frame))
        short["stop_ns"] = time.monotonic_ns() + 100_000_000
        with patch("app.worker.worker_main.PostgresAdmissionLedger", side_effect=AssertionError("constructed")):
            with self.assertRaises(ValueError):
                await execute_one_tool(short)

    def test_run_one_tool_early_rejects_before_launcher(self):
        ledger = PostgresAdmissionLedger("synthetic-dsn")
        with patch("app.worker.launcher.run_supervised_window", side_effect=AssertionError("launched")):
            with self.assertRaises(ValueError):
                run_one_tool(ledger, SessionConfig(window_seconds=200, request_timeout_seconds=121),
                             str(uuid4()), "executor", make_call(), run_tag="run")
            with self.assertRaises(TypeError):
                run_one_tool(ledger, SessionConfig(), str(uuid4()), "executor", "not typed", run_tag="run")
            with self.assertRaises(ValueError):
                run_one_tool(ledger, SessionConfig(), "not-a-uuid", "executor", make_call(), run_tag="run")

    async def test_sup_one_tool_old_unknown_job_fails_before_claim(self):
        # 未变停止主体：旧Job不可判时工具分支必须在claim前失败关闭，不获得新资格。
        from app.worker.windows_job import JobUnknown
        from tests.test_worker_session import FakeLedger

        class Owner:
            def __init__(self, *args, **kwargs):
                pass

            def close(self):
                pass

        ledger = FakeLedger(old_running=True)
        config = SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1,
                               startup_limit_seconds=2, single_host_single_session_recovery=True)
        with patch("app.worker.session.current_process_session_id", return_value=1), \
             patch("app.worker.session.ActivityMutex", Owner), \
             patch("app.worker.session.NamedJob.open_existing", side_effect=JobUnknown("unknown")):
            outcome = await SingleWindowSupervisor(ledger, config).run_once(
                str(uuid4()), "worker-1", WorkerCommand("one_tool"), run_tag="unit-tool-old",
                manager_deadline_ns=time.monotonic_ns() + 20_000_000_000, tool_action=make_call())
        self.assertEqual(outcome.state, "failed_closed")
        self.assertEqual(ledger.events, ["inspect"])

    async def test_sup_one_tool_early_rejections_before_claim(self):
        activity = str(uuid4())
        ledger = PostgresAdmissionLedger("synthetic-dsn")
        config = SessionConfig(window_seconds=10, request_timeout_seconds=1, stop_grace_seconds=1,
                               startup_limit_seconds=3, manager_db_timeout_seconds=2, cleanup_seconds=2,
                               mutex_wait_seconds=1, manager_overhead_seconds=12)
        supervisor = SingleWindowSupervisor(ledger, config)
        with patch.object(ledger, "claim_lease") as claim:
            with self.assertRaises(ValueError):
                await supervisor.run_once(activity, "executor", WorkerCommand("one_tool"),
                                          run_tag="run-092", manager_deadline_ns=time.monotonic_ns() + 60_000_000_000)
            with self.assertRaises(ValueError):
                await supervisor.run_once(activity, "executor", WorkerCommand("one_tool"),
                                          run_tag="run-092", manager_deadline_ns=time.monotonic_ns() + 60_000_000_000,
                                          one_call=OneCallInput("op", _model_request(), _model_service()))
            claim.assert_not_called()
        # 模型路径混入工具数据同样拒绝。
        with self.assertRaises(ValueError):
            await supervisor.run_once(activity, "executor", WorkerCommand("one_call"),
                                      run_tag="run-092", manager_deadline_ns=time.monotonic_ns() + 60_000_000_000,
                                      one_call=OneCallInput("op", _model_request(), _model_service()),
                                      tool_action=make_call())


class OuterProtocolCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    def test_outer_request_shapes_strict_by_protocol(self):
        ledger = PostgresAdmissionLedger("synthetic-dsn")
        config = SessionConfig()
        name = "Local\\RetroLume.SUP." + "a" * 32
        activity = str(uuid4())
        tool_frame_dict = _request(ledger, config, activity, "executor", WorkerCommand("one_tool"),
                                   "run", name, time.monotonic_ns() + 10 ** 10, None, make_call())
        self.assertEqual(tool_frame_dict["protocol"], 3)
        self.assertEqual(set(tool_frame_dict), {"protocol", "mapping_name", "activity_id", "executor_id",
                                                "run_tag", "deadline_ns", "command", "config", "ledger", "tool_action"})
        self.assertNotIn("one_call", tool_frame_dict)
        decoded = _validated_request(tool_frame_dict, name)
        self.assertEqual(decoded[7], None)
        self.assertEqual(decoded[8].operation_id, "T1")
        # 协议与command不匹配、额外字段、伪身份全部拒绝且不声称可降级。
        for mutate in (
            lambda x: x.update(command={"task": "one_call"}),
            lambda x: x.update(protocol=2),
            lambda x: x.update(one_call=None),
            lambda x: x.update(extra=1),
            lambda x: x["config"].update(extra=1),
        ):
            item = json.loads(json.dumps(tool_frame_dict))
            mutate(item)
            with self.subTest(item=item), self.assertRaises(ValueError):
                _validated_request(item, name)
        model_frame = _request(ledger, config, activity, "executor", WorkerCommand("one_call"),
                               "run", name, time.monotonic_ns() + 10 ** 10,
                               OneCallInput("op", _model_request(), _model_service()))
        self.assertEqual(model_frame["protocol"], 2)
        with self.assertRaises(ValueError):
            _validated_request(dict(model_frame, protocol=3), name)
        with self.assertRaises(ValueError):
            _validated_request(dict(model_frame, tool_action=make_call().to_wire()), name)

    def test_outer_outcome_v2_v3_frozen_field_sets(self):
        activity = str(uuid4())
        context = CallContext(activity_id=activity, operation_id="T1", executor_id="executor",
                              execution_generation=2, scope_revision=1)
        receipt = tool_receipt(ToolCallResult(ToolCallStatus.SUCCEEDED, "finite_calculate", "calc.1",
                                              make_call().arguments_sha256, None, "d" * 64), context, "run")
        outcome = SessionOutcome("run", "settled", activity, generation=2, tool_receipt=receipt)
        frame3 = {"protocol": 3, "run_tag": "run", "activity_id": activity, "outcome": asdict(outcome)}
        recovered = _decode_outcome(json.loads(json.dumps(frame3)), "run", activity)
        self.assertEqual(recovered.tool_receipt, receipt)
        self.assertEqual(set(asdict(outcome)), set(_OUTER3_OUTCOME_FIELDS))
        # 旧2字段集不携带新tool_receipt；外2若带tool_receipt（21字段）拒绝，不回退兼容。
        with self.assertRaises(ManagerControlError):
            _decode_outcome(json.loads(json.dumps({"protocol": 2, "run_tag": "run", "activity_id": activity,
                                                   "outcome": asdict(outcome)})), "run", activity)
        old = asdict(SessionOutcome("run", "settled", activity, generation=2, model_receipt=None))
        old.pop("tool_receipt")
        self.assertEqual(set(old), set(_OUTER2_OUTCOME_FIELDS))
        recovered2 = _decode_outcome(json.loads(json.dumps({"protocol": 2, "run_tag": "run",
                                                            "activity_id": activity, "outcome": old})), "run", activity)
        self.assertIsNone(recovered2.tool_receipt)
        # 缺字段的外3同样拒绝。
        short = dict(frame3, outcome={k: v for k, v in asdict(outcome).items() if k != "tool_receipt"})
        with self.assertRaises(ManagerControlError):
            _decode_outcome(json.loads(json.dumps(short)), "run", activity)

    def test_model_inner_protocol_unchanged(self):
        # 旧模型路径内3帧与回执形状保持（回归由 test_worker_one_call 全量承担）。
        value = dict(dsn="synthetic-dsn", connect_timeout_seconds=1, statement_timeout_ms=500, lock_timeout_ms=100)
        lease = ActivityLease(str(uuid4()), "executor", 7, 3, None, 12, 1)
        call = OneCallInput("op-092", _model_request(), _model_service())
        frame = model_worker_request(call, value, lease, "run", time.monotonic_ns() + 10 ** 10, 0.5)
        self.assertEqual(frame["protocol"], 3)
        decoded_call, context = decode_worker_request(frame)
        self.assertEqual(decoded_call.operation_id, "op-092")
        self.assertEqual(context.execution_generation, 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
