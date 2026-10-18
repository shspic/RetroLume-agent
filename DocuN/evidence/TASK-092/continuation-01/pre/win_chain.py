"""批次windows子进程：C10 正常工具链与旧 model 回归；C11 硬停止与恢复；混用探针。

场景（与 scenario-manifest.json 冻结一致）：
  tool_chain        C10：真实service→固定launcher/SUP/worker→真实finite_calculate→真实PG
  model_regression  C10配套：旧无工具model外2/内3形状端到端保持（合成transport）
  tool_stop         C11a：mark确认后执行边界不合作阻塞→SUP截止硬停止、全额预扣、T不退
  tool_recovery     C11b：同会话显式接续，旧R只折叠一次，旧操作unknown不重执行
  old_sup_reject    混用：旧SUP收到外3拒绝且无claim（真实Windows会话）
  old_worker_reject 混用：旧worker拒one_tool退出2；但新SUP已claim预扣保留
"""
from __future__ import annotations

import asyncio
import ctypes
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402
from app.activities import ActivitySpec, PostgresAdmissionLedger, ResultReadStatus, SourceSnapshot  # noqa: E402
from app.activities.service import ActivityService  # noqa: E402
from app.capabilities.contracts import (  # noqa: E402
    AdmissionIntent, CallContext, LedgerDisposition, LedgerOutcome, ModelCallRequest,
    ModelServiceConfig, Provider, ToolCallPlan, build_business_payload, canonical_tool_arguments,
)
from app.runtime import psycopg_compatible_loop_factory  # noqa: E402
from app.worker.command import _INTERPRETER  # noqa: E402
from app.worker.session import SessionConfig  # noqa: E402
from app.worker.windows_job import ERROR_FILE_NOT_FOUND, JobOpenError, NamedJob  # noqa: E402
import app.worker.launcher as launcher  # noqa: E402

EVIDENCE = Path(os.environ["TASK092_EVIDENCE"]).resolve()
DSN = os.environ.get("RETROLUME_TOOL_TEST_DATABASE_URL", "")
ROLE = "retrolume_task092_synth"
DBNAME = "retrolume_task092_tools"

SCENARIOS = ["tool_chain", "model_regression", "tool_stop", "tool_recovery", "old_sup_reject", "old_worker_reject"]

CONFIG = SessionConfig(window_seconds=10, request_timeout_seconds=2, stop_grace_seconds=1,
                       startup_limit_seconds=3, manager_db_timeout_seconds=2, cleanup_seconds=2,
                       mutex_wait_seconds=1, manager_overhead_seconds=12,
                       single_host_single_session_recovery=True)


def emit(**item):
    print(json.dumps(item, default=str), flush=True)


def check(condition, label):
    if not condition:
        raise AssertionError(label)


def run(coro):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
        return runner.run(coro)


def rows(query, params=()):
    with psycopg.connect(DSN, connect_timeout=2, row_factory=dict_row) as conn:
        return conn.execute(query, params).fetchall()


def row(query, params=()):
    return rows(query, params)[0]


def synthetic_supervisor(cls, mapping_name):
    """外层Job由launcher创建；此处只把固定SUP替换为测试自举/旧版探针进程。"""
    sup_mode = os.environ.get("TASK092_SUP_MODE", "bootstrap")
    if sup_mode == "legacy":
        argv = [str(sys._base_executable), "-B", str(HERE / "legacy_probe.py"),
                "old_sup", str(EVIDENCE), mapping_name]
    else:
        argv = [str(sys._base_executable), "-B", str(HERE / "bootstrap.py"),
                "sup", str(EVIDENCE), mapping_name]
    api = launcher._api()
    executable = str(sys._base_executable)
    command = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
    env = launcher._environment_block()
    startup = launcher._STARTUPINFOW()
    startup.cb = ctypes.sizeof(startup)
    info = launcher._PROCESS_INFORMATION()
    if not api.CreateProcessW(executable, command, None, None, False,
                              launcher.CREATE_SUSPENDED | launcher.CREATE_NO_WINDOW | launcher.CREATE_UNICODE_ENVIRONMENT,
                              ctypes.cast(env, ctypes.c_void_p), str(BACKEND),
                              ctypes.byref(startup), ctypes.byref(info)):
        raise launcher.ProcessCreationError(ctypes.get_last_error(),
                                            cls(api, info) if info.hProcess or info.hThread else None)
    return cls(api, info)


async def build(dsn, *, max_tool_calls=4, window=30):
    activity, source, version = (str(uuid.uuid4()) for _ in range(3))
    async with await psycopg.AsyncConnection.connect(dsn, connect_timeout=2) as conn:
        await conn.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'task092',0)", (source,))
        await conn.execute("INSERT INTO material_versions(id,source_id,filename,format,sha256,size) "
                           "VALUES (%s,%s,'synthetic.txt','txt',%s,1)", (version, source, "8" * 64))
        await conn.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (version, source))
    ledger = PostgresAdmissionLedger(dsn, connect_timeout_seconds=1, statement_timeout_ms=500, lock_timeout_ms=200)
    await ledger.create_activity(ActivitySpec(
        activity, (SourceSnapshot(source, version, 1),),
        datetime.now(timezone.utc) + timedelta(minutes=10), 8, 800, 100, 4096, 256, 300,
        (("deepseek_chat_completions", "synthetic-model"),), ("finite_calculate",),
        max_tool_calls=max_tool_calls))
    return ledger, activity, source, version


def cleanup(activity, source, version):
    with psycopg.connect(DSN, connect_timeout=2, autocommit=True) as conn:
        for sql in ("DELETE FROM activity_operation_results WHERE activity_id=%s",
                    "DELETE FROM activity_operations WHERE activity_id=%s",
                    "DELETE FROM activity_allowed_models WHERE activity_id=%s",
                    "DELETE FROM activity_scope_sources WHERE activity_id=%s",
                    "DELETE FROM activities WHERE id=%s"):
            conn.execute(sql, (activity,))
        conn.execute("UPDATE material_sources SET current_version=NULL WHERE id=%s", (source,))
        conn.execute("DELETE FROM material_versions WHERE id=%s", (version,))
        conn.execute("DELETE FROM material_sources WHERE id=%s", (source,))


def account(activity):
    return row("SELECT status,execution_generation,dispatch_closed,max_tool_calls,tools_reserved,"
               "requests_reserved,cost_reserved_microunits,running_reserved_seconds,running_settled_seconds "
               "FROM activities WHERE id=%s", (activity,))


def ops(activity):
    return rows("SELECT operation_id,kind,state,disposition,execution_generation,scope_revision,"
                "tool_names,tool_call_id,arguments_sha256,dispatch_started_at FROM activity_operations "
                "WHERE activity_id=%s ORDER BY operation_id", (activity,))


def results(activity):
    return rows("SELECT operation_id,payload_format,payload,payload_sha256,admission_id,execution_generation,"
                "scope_revision FROM activity_operation_results WHERE activity_id=%s ORDER BY operation_id",
                (activity,))


def job_absent(activity, generation, label):
    try:
        job = NamedJob.open_existing(activity, generation)
    except JobOpenError as exc:
        check(exc.code == ERROR_FILE_NOT_FOUND, f"{label}: unexpected job open error {exc.code}")
        return {"job_present": False, "open_error": exc.code}
    else:
        active = job.active_processes()
        job.close()
        check(active == 0, f"{label}: job handle retained with active processes")
        return {"job_present": True, "active_processes": active}


def session_facts(supervision):
    data = asdict(supervision)
    data.pop("tool_receipt", None)
    data.pop("model_receipt", None)
    return data


def verify_bootstrap(mode: str, expect: dict) -> dict:
    records = [json.loads(p.read_text(encoding="utf-8")) for p in EVIDENCE.glob(f"bootstrap-{mode}-*.json")]
    check(len(records) >= 1, f"missing bootstrap capture {mode}")
    record = records[-1]
    as_run = json.loads((EVIDENCE / "as-run-hashes.json").read_text(encoding="utf-8"))["before"]
    for path, digest in record["loaded_source_bytes"].items():
        check(as_run.get(path) == digest, f"{mode}: loaded bytes mismatch {path}")
    for key, value in expect.items():
        check(record.get(key) == value, f"{mode}: {key}={record.get(key)} expected {value}")
    return {k: record.get(k) for k in ("mode", "pid", "worker_mode", "tool_execute_calls",
                                       "transport_sends", "message_roles")}


def scenario_tool_chain():
    ledger, activity, source, version = run(build(DSN))
    try:
        os.environ["TASK092_WORKER_MODE"] = "one_tool"
        os.environ["TASK092_SUP_MODE"] = "bootstrap"
        plan = ToolCallPlan("calc.1", "finite_calculate", {"operation": "add", "left": 1, "right": 2})
        _, digest = canonical_tool_arguments({"operation": "add", "left": 1, "right": 2})
        before = account(activity)
        emit(event="windows_session_attempt", scenario="tool_chain")
        with launcher_patch():
            outcome = run(ActivityService(ledger).execute_tool_action(
                activity, "T1", plan, CONFIG, "executor092", "run092-tool"))
        check(outcome.status == "committed_current", f"tool status {outcome.status}")
        sup = outcome.supervision
        check(sup.state == "settled" and not sup.cleanup_incomplete, f"tool supervision {sup.state}")
        receipt = sup.tool_receipt
        check(receipt["protocol"] == 4 and receipt["business_commit"] == "committed", "tool receipt shape")
        check(receipt["result"]["status"] == "succeeded", "tool receipt status")
        check(receipt["result"]["arguments_sha256"] == digest and receipt["result"]["call_id"] == "calc.1",
              "tool receipt identity")
        payload_sha = receipt["result"]["payload_sha256"]
        stored = results(activity)
        check(len(stored) == 1 and stored[0]["operation_id"] == "T1", "single tool result")
        check(stored[0]["payload"] == '{"format":"text","value":"3"}', "tool payload value")
        check(stored[0]["payload_sha256"] == payload_sha, "receipt/database hash")
        row_op = ops(activity)
        check(len(row_op) == 1 and row_op[0]["kind"] == "tool" and row_op[0]["state"] == "received",
              "tool operation row")
        check(row_op[0]["tool_call_id"] == "calc.1" and row_op[0]["arguments_sha256"] == digest,
              "tool row identity")
        after = account(activity)
        check(after["tools_reserved"] == 1 and after["requests_reserved"] == 0
              and after["cost_reserved_microunits"] == 0, "tool budget alone")
        check(after["running_reserved_seconds"] == 0 and after["dispatch_closed"], "window closed")
        check(after["execution_generation"] == row_op[0]["execution_generation"] + 1, "close generation")
        check(after["running_settled_seconds"] == sup.settled_seconds, "settled once")
        read = run(ledger.read_committed_result(activity, "T1"))
        check(read.read_status is ResultReadStatus.COMMITTED_CURRENT and read.kind == "tool", "typed read")
        check(read.payload == '{"format":"text","value":"3"}' and read.payload_sha256 == payload_sha, "read payload")
        page = run(ledger.list_committed_results(activity))
        check(len(page) == 1 and page[0].kind == "tool" and page[0].payload is None, "typed list metadata")
        job = job_absent(activity, sup.generation, "tool_chain")
        sup_record = verify_bootstrap("sup", {"worker_mode": "one_tool"})
        worker_record = verify_bootstrap("worker-one_tool", {"tool_execute_calls": 1, "transport_sends": 0})
        emit(event="scenario_result", scenario="tool_chain", status=outcome.status,
             supervision=session_facts(sup), account_before=before, account_after=after,
             operations=row_op, results=stored, job=job, sup=sup_record, worker=worker_record)
    finally:
        cleanup(activity, source, version)


def scenario_model_regression():
    ledger, activity, source, version = run(build(DSN))
    try:
        async def prepare():
            lease = await ledger.claim_lease(activity, "prepare092", lease_seconds=30, window_seconds=10)
            context = CallContext(activity_id=activity, executor_id=lease.executor_id, operation_id="P",
                                  execution_generation=lease.execution_generation,
                                  scope_revision=lease.scope_revision)
            permit = await ledger.admit(AdmissionIntent(context, Provider.DEEPSEEK_CHAT_COMPLETIONS,
                                                        "synthetic-model", 512, 40, ()))
            await ledger.mark_dispatch_started(permit)
            fmt, text, sha = build_business_payload(json_object={"parent": "低信任历史"})
            await ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.RECEIVED,
                                                              payload_format=fmt, payload=text, payload_sha256=sha))
            await ledger.begin_window_close(activity, lease.executor_id, lease.execution_generation)
            await ledger.settle_execution_window(activity, lease.executor_id, lease.execution_generation,
                                                 window_seconds=10, elapsed_seconds=1)
            return sha
        parent_sha = run(prepare())
        os.environ["TASK092_WORKER_MODE"] = "one_call"
        os.environ["TASK092_SUP_MODE"] = "bootstrap"
        os.environ["TASK092_MODEL_ANSWER"] = '{"synthetic":true}'
        service = ModelServiceConfig(provider="deepseek_chat_completions", base_url="https://api.deepseek.com",
                                     model="synthetic-model", api_key=secrets.token_urlsafe(24),
                                     timeout_seconds=0.5, max_request_bytes=4096, max_response_bytes=4096)
        emit(event="windows_session_attempt", scenario="model_regression")
        with launcher_patch():
            outcome = run(ActivityService(ledger).continue_from_result(
                activity, "P", "Q", "explicit-followup-092", service, CONFIG, "executor092", "run092-model"))
        check(outcome.status == "committed_current", f"model status {outcome.status}")
        sup = outcome.supervision
        check(sup.state == "settled" and not sup.cleanup_incomplete, f"model supervision {sup.state}")
        receipt = sup.model_receipt
        check(receipt["protocol"] == 3 and receipt["business_commit"] == "committed", "model receipt frame")
        check(receipt["result"]["status"] == "succeeded", "model receipt status")
        stored = results(activity)
        check(len(stored) == 2, "parent and child results")
        child = [x for x in stored if x["operation_id"] == "Q"][0]
        check(child["payload"] == '{"format":"json","value":{"synthetic":true}}', "child payload")
        check(child["payload_sha256"] == receipt["result"]["payload_sha256"], "model hash binding")
        check(parent_sha == [x for x in stored if x["operation_id"] == "P"][0]["payload_sha256"], "parent intact")
        job = job_absent(activity, sup.generation, "model_regression")
        sup_record = verify_bootstrap("sup", {"worker_mode": "one_call"})
        worker_record = verify_bootstrap("worker-one_call", {"transport_sends": 1,
                                                             "message_roles": ["assistant", "user"]})
        emit(event="scenario_result", scenario="model_regression", status=outcome.status,
             supervision=session_facts(sup), operations=ops(activity), results=stored,
             job=job, sup=sup_record, worker=worker_record)
    finally:
        cleanup(activity, source, version)


def scenario_tool_stop_recovery():
    ledger, activity, source, version = run(build(DSN))
    try:
        os.environ["TASK092_SUP_MODE"] = "bootstrap"
        os.environ["TASK092_WORKER_MODE"] = "one_tool_block"
        plan = ToolCallPlan("calc.1", "finite_calculate", {"operation": "add", "left": 1, "right": 2})
        emit(event="windows_session_attempt", scenario="tool_stop")
        before = account(activity)
        started = time.monotonic()
        with launcher_patch():
            outcome = run(ActivityService(ledger).execute_tool_action(
                activity, "T1", plan, CONFIG, "executor092", "run092-stop"))
        elapsed = time.monotonic() - started
        sup = outcome.supervision
        check(sup.state == "stopped_at_deadline", f"stop state {sup.state}")
        check(sup.active_processes_at_end == 0 and not sup.cleanup_incomplete, "tree zero after hard stop")
        check(sup.job_name and sup.pid and sup.worker_created_100ns, "worker identity recorded")
        check(elapsed >= 8, f"stop earlier than deadline window: {elapsed}")
        stopped = ops(activity)
        check(len(stopped) == 1 and stopped[0]["state"] == "dispatched", "mark committed before block")
        check(stopped[0]["dispatch_started_at"] is not None, "dispatch boundary persisted")
        check(results(activity) == [], "no fake success body")
        after = account(activity)
        check(after["tools_reserved"] == 1, "tool attempt retained, no refund")
        check(after["running_reserved_seconds"] == 10 and after["running_settled_seconds"] == 0,
              "full reservation retained, no partial settle")
        check(not after["dispatch_closed"], "no close after hard stop")
        job = job_absent(activity, sup.generation, "tool_stop")
        check(outcome.status == "supervision_unknown", f"business unknown {outcome.status}")
        # 恢复会话：等待持久租约到期后同会话显式接续新键。
        deadline = time.monotonic() + 20
        while row("SELECT lease_expires_at <= now() AS expired FROM activities WHERE id=%s",
                  (activity,))["expired"] is not True:
            check(time.monotonic() < deadline, "lease did not expire for recovery")
            time.sleep(0.2)
        os.environ["TASK092_WORKER_MODE"] = "one_tool"
        plan2 = ToolCallPlan("calc.2", "finite_calculate", {"operation": "add", "left": 5, "right": 7})
        emit(event="windows_session_attempt", scenario="tool_recovery")
        with launcher_patch():
            outcome2 = run(ActivityService(ledger).execute_tool_action(
                activity, "T2", plan2, CONFIG, "executor092", "run092-recover"))
        check(outcome2.status == "committed_current", f"recovery status {outcome2.status}")
        sup2 = outcome2.supervision
        check(sup2.state == "settled" and not sup2.cleanup_incomplete, f"recovery supervision {sup2.state}")
        settled_seconds = sup2.settled_seconds
        recovered = account(activity)
        check(recovered["tools_reserved"] == 2, "both attempts retained")
        check(recovered["running_settled_seconds"] == 10 + settled_seconds,
              f"old R folded exactly once: {recovered['running_settled_seconds']}")
        check(recovered["running_reserved_seconds"] == 0, "window released after settle")
        stored = results(activity)
        check(len(stored) == 1 and stored[0]["operation_id"] == "T2", "only new key produced a result")
        check(stored[0]["payload"] == '{"format":"text","value":"12"}', "recovery computation")
        folded = run(ledger.recover_obsolete_operations(activity))
        check(folded == 1, f"one obsolete operation converged: {folded}")
        final_ops = ops(activity)
        check(final_ops[0]["state"] == "unknown" and final_ops[0]["operation_id"] == "T1",
              "old tool operation unknown, never re-executed")
        check(final_ops[1]["state"] == "received" and final_ops[1]["operation_id"] == "T2", "new op intact")
        check(results(activity) == stored, "no body added to unknown")
        check(account(activity)["tools_reserved"] == 2, "convergence changes no tool budget")
        job = job_absent(activity, sup2.generation, "tool_recovery")
        worker2 = verify_bootstrap("worker-one_tool", {"tool_execute_calls": 1})
        emit(event="scenario_result", scenario="tool_stop_recovery", stop={"state": sup.state,
             "supervision": session_facts(sup), "account": before, "account_after_stop": after,
             "operations": stopped, "job": job_absent(activity, sup.generation, "tool_stop-recheck")},
             recovery={"status": outcome2.status, "supervision": session_facts(sup2),
                       "account": recovered, "operations": final_ops, "results": stored,
                       "job": job, "worker": worker2})
    finally:
        cleanup(activity, source, version)


def scenario_old_sup_reject():
    ledger, activity, source, version = run(build(DSN))
    try:
        # 正反照：旧版校验对 2 帧成功、对 3 帧拒绝（证明副本为旧逻辑而非一律拒绝）。
        from legacy_probe import legacy_validated_request
        from app.worker.one_call import OneCallInput
        from app.worker.launcher import _request
        from app.worker.command import WorkerCommand
        model_request = ModelCallRequest(messages=[{"role": "user", "content": "synthetic"}],
                                         max_output_tokens=40, response_mode="text")
        service = ModelServiceConfig(provider="deepseek_chat_completions", base_url="https://api.deepseek.com",
                                     model="synthetic-model", api_key=secrets.token_urlsafe(24),
                                     timeout_seconds=0.5, max_request_bytes=4096, max_response_bytes=4096)
        name = "Local\\RetroLume.SUP." + secrets.token_hex(16)
        frame2 = _request(ledger, CONFIG, activity, "executor092", WorkerCommand("one_call"), "run092",
                          name, time.monotonic_ns() + 60_000_000_000,
                          OneCallInput("probe", model_request, service))
        frame3 = _request(ledger, CONFIG, activity, "executor092", WorkerCommand("one_tool"), "run092",
                          name, time.monotonic_ns() + 60_000_000_000, None,
                          make_probe_call())
        check(len(legacy_validated_request(frame2, name)) == 8, "legacy accepts protocol 2")
        try:
            legacy_validated_request(frame3, name)
        except ValueError:
            pass
        else:
            raise AssertionError("legacy validator unexpectedly accepted protocol 3")
        os.environ["TASK092_SUP_MODE"] = "legacy"
        os.environ["TASK092_WORKER_MODE"] = "one_tool"
        plan = ToolCallPlan("calc.1", "finite_calculate", {"operation": "add", "left": 1, "right": 2})
        emit(event="windows_session_attempt", scenario="old_sup_reject")
        with launcher_patch():
            outcome = run(ActivityService(ledger).execute_tool_action(
                activity, "T1", plan, CONFIG, "executor092", "run092-oldsup"))
        sup = outcome.supervision
        check(sup.state == "supervisor_lost_unconfirmed", f"legacy sup state {sup.state}")
        after = account(activity)
        check(after["status"] == "pending" and after["running_reserved_seconds"] == 0, "no claim")
        check(after["tools_reserved"] == 0 and ops(activity) == [] and results(activity) == [], "no side effects")
        check(outcome.status == "supervision_unknown", outcome.status)
        probes = [json.loads(p.read_text(encoding="utf-8")) for p in EVIDENCE.glob("legacy-sup-*.json")]
        check(len(probes) == 1 and probes[0]["rejected"] and probes[0]["protocol_seen"] == 3, "legacy sup probe")
        emit(event="scenario_result", scenario="old_sup_reject", status=outcome.status,
             supervision=session_facts(sup), account=after, probe=probes[0])
    finally:
        cleanup(activity, source, version)


def scenario_old_worker_reject():
    ledger, activity, source, version = run(build(DSN))
    try:
        os.environ["TASK092_SUP_MODE"] = "bootstrap"
        os.environ["TASK092_WORKER_MODE"] = "legacy_worker"
        plan = ToolCallPlan("calc.1", "finite_calculate", {"operation": "add", "left": 1, "right": 2})
        emit(event="windows_session_attempt", scenario="old_worker_reject")
        with launcher_patch():
            outcome = run(ActivityService(ledger).execute_tool_action(
                activity, "T1", plan, CONFIG, "executor092", "run092-oldworker"))
        sup = outcome.supervision
        check(sup.state == "worker_failed_full_reservation", f"old worker state {sup.state}")
        check(sup.active_processes_at_end == 0 and not sup.cleanup_incomplete, "tree zero")
        after = account(activity)
        check(after["tools_reserved"] == 0 and ops(activity) == [], "old worker never admitted a tool action")
        check(after["running_reserved_seconds"] == 10 and after["running_settled_seconds"] == 0,
              "claim pre-charge exists though tool was rejected")
        worker = verify_bootstrap("worker-legacy", {"worker_mode": "legacy_worker"})
        emit(event="scenario_result", scenario="old_worker_reject", status=outcome.status,
             supervision=session_facts(sup), account=after, worker=worker)
    finally:
        cleanup(activity, source, version)


def make_probe_call():
    from app.capabilities.contracts import ToolExecutionInput
    raw, digest = canonical_tool_arguments({"operation": "add", "left": 1, "right": 2})
    return ToolExecutionInput("probe", "calc.1", "finite_calculate", raw, digest)


def launcher_patch():
    from unittest.mock import patch
    return patch.object(launcher._SuspendedSupervisor, "create",
                        classmethod(synthetic_supervisor))


def main(folder: Path) -> int:
    if not DSN:
        emit(event="skip", reason="dedicated task092 tools DSN required")
        return 77
    identity = row("SELECT current_database() AS db, current_user AS role")
    check(identity == {"db": DBNAME, "role": ROLE}, "dedicated database identity mismatch")
    emit(event="database_identity", **identity)
    failures = []
    for scenario in SCENARIOS:
        emit(event="scenario_start", scenario=scenario)
        try:
            globals()[f"scenario_{scenario}"]()
        except Exception as exc:
            # 冻结场景清单连续运行：单场景失败不吞掉其余场景，也不重试该场景。
            failures.append({"scenario": scenario, "type": type(exc).__name__,
                             "label": str(exc) if type(exc) is AssertionError else None})
            emit(event="scenario_error", scenario=scenario, type=type(exc).__name__,
                 label=str(exc) if type(exc) is AssertionError else None)
            continue
        emit(event="scenario_complete", scenario=scenario)
    emit(event="complete", scenarios=len(SCENARIOS), failed=failures)
    return 0 if not failures else 1


if __name__ == "__main__":
    assert sys.argv[1] == "--child"
    try:
        code = main(Path(sys.argv[2]))
    except BaseException as exc:
        emit(event="error", type=type(exc).__name__,
             label=str(exc) if type(exc) is AssertionError else None)
        code = 1
    raise SystemExit(code)
