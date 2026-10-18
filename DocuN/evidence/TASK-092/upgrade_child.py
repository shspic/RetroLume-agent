"""续作02 upgrade子进程：s1/s2/s3三个独立目标、独立连接与独立结果。

s1 happy：重建本卡happy schema并一次完整走通——001—007合法非空基线→008；
   旧行仅新增三列且其余逐字段不变；旧model生命线（含未配置额度拒工具、零副作用）；
   重复008命中008自身"已有痕迹"RAISE且schema与数据不变。此前行不变证据复用。
s2 rollback：成本约束被篡改→008"唯一识别"失败→整事务回滚；无五新列、无部分DDL、
   旧行不变、篡改约束仍在。独立基线与失败连接。
s3 missing：空schema缺前置→008在ALTER前"前置不存在"拒绝；明确零目标对象。

阴性纪律：不以任意Exception判通过；断言SQLSTATE=P0001且命中008自身的有限识别
文本（已有痕迹/唯一识别/前置不存在），排除DSN/权限/语法/夹具表缺失类错误。
每个场景独立连接、finally收连接；单场景失败（且清理确认）不阻塞其他隔离schema，
失败仍使整批非零；清理不确定则停止后续并标not_run。TASK092_UPGRADE_ONLY可定向
只重建/只测指定schema（real-06用），不抹掉其他通过证据。
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

UPGRADE_DB = "retrolume_task092_upgrade"
ROLE = "retrolume_task092_synth"
TOOLS_DB_FORBIDDEN = "retrolume_task092_tools"
MIGS = {
    "001_materials.sql": (BACKEND / "migrations" / "001_materials.sql").read_text(encoding="utf-8"),
    "002_activities.sql": (BACKEND / "migrations" / "002_activities.sql").read_text(encoding="utf-8"),
    "003_pdf_review.sql": (BACKEND / "migrations" / "003_pdf_review.sql").read_text(encoding="utf-8"),
    "004_activities_time_budget.sql": (BACKEND / "migrations" / "004_activities_time_budget.sql").read_text(encoding="utf-8"),
    "005_activities_dispatch_closed.sql": (BACKEND / "migrations" / "005_activities_dispatch_closed.sql").read_text(encoding="utf-8"),
    "006_activities_running_owner_session.sql": (BACKEND / "migrations" / "006_activities_running_owner_session.sql").read_text(encoding="utf-8"),
    "007_activity_operation_results.sql": (BACKEND / "migrations" / "007_activity_operation_results.sql").read_text(encoding="utf-8"),
    "008_activity_tool_budget.sql": (BACKEND / "migrations" / "008_activity_tool_budget.sql").read_text(encoding="utf-8"),
}
BASELINE = [name for name in MIGS if name < "008_"]
SCHEMAS = {"s1": "task092_upgrade_happy", "s2": "task092_upgrade_rollback", "s3": "task092_upgrade_missing"}
NEW_COLUMNS = {"max_tool_calls", "tools_reserved", "kind", "arguments_sha256", "tool_call_id"}
NEW_CONSTRAINTS = {"activities_tool_budget_limit", "activities_tool_budget_reserved",
                   "activities_tool_budget_balance", "activity_operations_kind_domain",
                   "activity_operations_kind_shape"}


def emit(**item):
    print(json.dumps(item, default=str), flush=True)


def sanitized_error(exc) -> dict:
    diag = getattr(exc, "diag", None)
    message = str(exc)
    return {"type": type(exc).__name__,
            "sqlstate": getattr(exc, "sqlstate", None),
            "constraint": getattr(diag, "constraint_name", None) if diag is not None else None,
            "message_head": message.splitlines()[0][:96] if message else ""}


def expect_migration_rejection(exc, marker: str) -> dict:
    """负例必须由008自身RAISE触发：P0001(raise_exception)且含唯一识别文本。"""
    import psycopg.errors
    info = sanitized_error(exc)
    assert info["sqlstate"] == "P0001", info
    assert isinstance(exc, psycopg.errors.RaiseException), info
    assert marker in str(exc), info
    return info


def scoped_dsn(schema: str) -> str:
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    parts = conninfo_to_dict(os.environ["RETROLUME_TOOL_UPGRADE_TEST_DATABASE_URL"])
    options = parts.get("options", "")
    parts["options"] = (options + f" -c search_path={schema}").strip()
    return make_conninfo(**parts)


def connect(schema: str, *, dict_rows: bool = True):
    import psycopg
    from psycopg.rows import dict_row
    return psycopg.connect(scoped_dsn(schema), autocommit=True,
                           row_factory=dict_row if dict_rows else None)


def schema_objects(conn, schema: str) -> dict:
    return {
        "tables": conn.execute("SELECT count(*) AS n FROM information_schema.tables WHERE table_schema=%s",
                               (schema,)).fetchone()["n"],
        "columns": conn.execute("SELECT count(*) AS n FROM information_schema.columns WHERE table_schema=%s",
                                (schema,)).fetchone()["n"],
        "constraints": conn.execute(
            "SELECT count(*) AS n FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
            "WHERE n.nspname=%s", (schema,)).fetchone()["n"],
        "sequences": conn.execute(
            "SELECT count(*) AS n FROM information_schema.sequences WHERE sequence_schema=%s",
            (schema,)).fetchone()["n"],
    }


def legacy_rows(conn, activity: str, source: str, version: str, payload: tuple) -> None:
    fmt, text, sha = payload
    conn.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'task092-upgrade',0)", (source,))
    conn.execute("INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'legacy.txt','txt',%s,1)",
                 (version, source, "8" * 64))
    conn.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (version, source))
    conn.execute(
        """INSERT INTO activities(id,status,scope_revision,execution_generation,deadline_at,
               max_requests,requests_reserved,max_cost_microunits,cost_reserved_microunits,reserve_cost_microunits,
               max_request_bytes,max_output_tokens,allowed_tools,
               max_running_seconds,running_reserved_seconds,running_settled_seconds,dispatch_closed)
           VALUES (%s,'pending',1,0,now()+interval '10 minutes',8,2,800,200,100,4096,256,
                   ARRAY['finite_calculate']::VARCHAR(64)[],300,0,0,FALSE)""", (activity,))
    conn.execute("INSERT INTO activity_allowed_models(activity_id,provider,model) VALUES (%s,'deepseek_chat_completions','synthetic-model')", (activity,))
    conn.execute("INSERT INTO activity_scope_sources(activity_id,source_id,version_id,source_revision) VALUES (%s,%s,%s,1)",
                 (activity, source, version))
    for key, state, disposition, error in (("P1", "received", "received", None),
                                           ("P2", "received", "received", None),
                                           ("P3", "unknown", "unknown", "executor_lost")):
        conn.execute(
            """INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,
                   execution_generation,scope_revision,provider,configured_model,request_bytes,max_output_tokens,
                   tool_names,reserved_cost_microunits,state,disposition,error_code,remote_request_id,
                   returned_model,finish_reason,prompt_tokens,completion_tokens,response_bytes,
                   reserved_at,dispatch_started_at,recorded_at)
               VALUES (%s,%s,gen_random_uuid(),'legacy092',1,1,'deepseek_chat_completions','synthetic-model',
                       512,40,'{}',100,%s,%s,%s,'req-legacy','synthetic-model','stop',10,4,200,
                       now()-interval '5 minutes',now()-interval '5 minutes',now()-interval '4 minutes')""",
            (activity, key, state, disposition, error))
    admission = conn.execute(
        "SELECT admission_id FROM activity_operations WHERE activity_id=%s AND operation_id='P1'",
        (activity,)).fetchone()["admission_id"]
    conn.execute(
        """INSERT INTO activity_operation_results(activity_id,operation_id,admission_id,
               execution_generation,scope_revision,payload_format,payload,payload_sha256)
           VALUES (%s,'P1',%s,1,1,%s,%s,%s)""", (activity, admission, fmt, text, sha))


def snapshot(conn, activity: str) -> dict:
    has_tool_columns = conn.execute(
        "SELECT count(*) AS n FROM information_schema.columns WHERE table_schema=current_schema() "
        "AND table_name='activities' AND column_name IN ('max_tool_calls','tools_reserved')").fetchone()["n"] == 2
    tool_columns = ",max_tool_calls,tools_reserved" if has_tool_columns else ""
    activity_row = conn.execute(
        f"""SELECT status,scope_revision,execution_generation,max_requests,requests_reserved,
                  max_cost_microunits,cost_reserved_microunits,reserve_cost_microunits,max_request_bytes,
                  max_output_tokens,allowed_tools,max_running_seconds,running_reserved_seconds,
                  running_settled_seconds,dispatch_closed,running_owner_session_id{tool_columns}
             FROM activities WHERE id=%s""", (activity,)).fetchone()
    ops = conn.execute(
        "SELECT * FROM activity_operations WHERE activity_id=%s ORDER BY operation_id", (activity,)).fetchall()
    results = conn.execute(
        "SELECT * FROM activity_operation_results WHERE activity_id=%s ORDER BY operation_id", (activity,)).fetchall()
    ops_columns = [d.name for d in conn.execute(
        "SELECT * FROM activity_operations WHERE activity_id=%s LIMIT 0", (activity,)).description]
    return {"activity": activity_row, "ops_columns": ops_columns, "ops": ops, "results": results}


def operation_check_count(conn) -> int:
    return conn.execute(
        "SELECT count(*) AS n FROM pg_constraint WHERE conrelid='activity_operations'::regclass AND contype='c'"
    ).fetchone()["n"]


def run_s1(conn, folder: Path) -> dict:
    activity = str(uuid.uuid4())
    source, version = str(uuid.uuid4()), str(uuid.uuid4())
    for name in BASELINE:
        conn.execute(MIGS[name])
    emit(event="baseline_001_007_applied", schema=SCHEMAS["s1"])
    from app.capabilities.contracts import build_business_payload
    legacy_rows(conn, activity, source, version, build_business_payload(json_object={"legacy": True}))
    before = snapshot(conn, activity)
    constraints_before = operation_check_count(conn)
    began = datetime.now(timezone.utc)
    conn.execute(MIGS["008_activity_tool_budget.sql"])
    committed = datetime.now(timezone.utc)
    after = snapshot(conn, activity)
    # F-U2：行级新增集合精确三列、kind=model、两元数据NULL，再排除三列后逐字段比较。
    new_op_columns = {"kind", "arguments_sha256", "tool_call_id"}
    assert set(after["ops_columns"]) - set(before["ops_columns"]) == new_op_columns
    assert set(after["activity"]) - set(before["activity"]) == {"max_tool_calls", "tools_reserved"}
    assert after["activity"]["max_tool_calls"] is None and after["activity"]["tools_reserved"] == 0
    for name, value in before["activity"].items():
        assert after["activity"][name] == value, name
    assert len(after["ops"]) == len(before["ops"]) == 3
    for old, new in zip(before["ops"], after["ops"]):
        assert set(new) - set(old) == new_op_columns, new["operation_id"]
        assert set(old) - set(new) == set(), new["operation_id"]
        assert new["kind"] == "model", new["operation_id"]
        assert new["arguments_sha256"] is None and new["tool_call_id"] is None, new["operation_id"]
        assert {k: v for k, v in new.items() if k not in new_op_columns} == old, new["operation_id"]
    assert after["results"] == before["results"]
    constraints_after = operation_check_count(conn)
    assert constraints_after == constraints_before - 1 + 2
    emit(event="upgrade_happy_rows_intact", activity=activity, operations=len(after["ops"]),
         payload_sha256=after["results"][0]["payload_sha256"],
         applied_utc=began.isoformat(), committed_utc=committed.isoformat())
    lifecycle_activity = run_lifecycle(conn, source, version)
    emit(event="legacy_lifecycle_ok", activity=lifecycle_activity)
    # 重复008：独立失败连接；阴性命中008自身"已有痕迹"；schema与数据不变。
    repeat_before = snapshot(conn, activity)
    repeat_constraints = operation_check_count(conn)
    repeat_info = None
    failing = connect(SCHEMAS["s1"])
    try:
        try:
            failing.execute(MIGS["008_activity_tool_budget.sql"])
        except BaseException as exc:
            repeat_info = expect_migration_rejection(exc, "已有痕迹")
            emit(event="repeat_008_rejected", **repeat_info)
        else:
            raise AssertionError("repeat 008 unexpectedly succeeded")
    finally:
        failing.close()
    repeat_after = snapshot(conn, activity)
    assert repeat_after == repeat_before, "schema or rows changed after rejected repeat 008"
    assert operation_check_count(conn) == repeat_constraints
    emit(event="repeat_008_state_intact", constraints=repeat_constraints)
    return {"activity": activity, "lifecycle_activity": lifecycle_activity,
            "repeat_008": repeat_info, "operations": len(after["ops"]),
            "payload_sha256": after["results"][0]["payload_sha256"]}


def run_lifecycle(conn, source: str, version: str) -> str:
    import asyncio
    from app.runtime import psycopg_compatible_loop_factory
    from app.activities import ActivitySpec, PostgresAdmissionLedger, SourceSnapshot
    from app.capabilities.contracts import (AdmissionDenied, AdmissionIntent, CallContext,
                                            LedgerDisposition, LedgerOutcome, Provider,
                                            ToolExecutionInput, ToolIntent,
                                            build_business_payload, canonical_tool_arguments)
    ledger = PostgresAdmissionLedger(scoped_dsn(SCHEMAS["s1"]))
    lifecycle_activity = str(uuid.uuid4())

    async def lifecycle():
        await ledger.create_activity(ActivitySpec(
            lifecycle_activity, (SourceSnapshot(source, version, 1),),
            datetime.now(timezone.utc) + timedelta(minutes=5), 4, 400, 100, 4096, 256, 120,
            (("deepseek_chat_completions", "synthetic-model"),),
            ("finite_calculate",), max_tool_calls=None))
        lease = await ledger.claim_lease(lifecycle_activity, "legacy092", lease_seconds=30, window_seconds=10)
        context = CallContext(activity_id=lifecycle_activity, operation_id="M1",
                              executor_id=lease.executor_id,
                              execution_generation=lease.execution_generation,
                              scope_revision=lease.scope_revision)
        permit = await ledger.admit(AdmissionIntent(context, Provider.DEEPSEEK_CHAT_COMPLETIONS,
                                                    "synthetic-model", 512, 40, ("finite_calculate",)))
        await ledger.mark_dispatch_started(permit)
        fmt, text, sha = build_business_payload(json_object={"legacy_plan": True})
        await ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.RECEIVED,
                                                          payload_format=fmt, payload=text, payload_sha256=sha))
        read = await ledger.read_committed_result(lifecycle_activity, "M1")
        assert read.read_status.value == "committed_current" and read.kind == "model"
        # 未配置额度拒工具：租约存活期内、以T1自身上下文配T1输入（否则先命中
        # 操作键绑定或lease_invalid而非tool_limit_unconfigured）。
        raw, digest = canonical_tool_arguments({"operation": "add", "left": 1, "right": 2})
        call = ToolExecutionInput("T1", "calc.1", "finite_calculate", raw, digest)
        tool_context = CallContext(activity_id=lifecycle_activity, operation_id="T1",
                                   executor_id=lease.executor_id,
                                   execution_generation=lease.execution_generation,
                                   scope_revision=lease.scope_revision)
        try:
            await ledger.admit_tool_operation(ToolIntent(context=tool_context, call=call))
        except AdmissionDenied as exc:
            assert str(exc) == "tool_limit_unconfigured", str(exc)
        else:
            raise AssertionError("unconfigured tool admission unexpectedly allowed")
        # 拒绝零副作用：键T1无操作行、额度仍0。
        denied_ops = conn.execute(
            "SELECT operation_id FROM activity_operations WHERE activity_id=%s AND operation_id='T1'",
            (lifecycle_activity,)).fetchall()
        assert denied_ops == [], denied_ops
        assert conn.execute("SELECT tools_reserved FROM activities WHERE id=%s",
                            (lifecycle_activity,)).fetchone()["tools_reserved"] == 0
        await ledger.begin_window_close(lifecycle_activity, lease.executor_id, lease.execution_generation)
        settled = await ledger.settle_execution_window(lifecycle_activity, lease.executor_id,
                                                       lease.execution_generation, window_seconds=10, elapsed_seconds=1)
        assert settled.name == "SETTLED"

    asyncio.Runner(loop_factory=psycopg_compatible_loop_factory).run(lifecycle())
    account = conn.execute(
        "SELECT max_tool_calls,tools_reserved,requests_reserved,cost_reserved_microunits AS cost "
        "FROM activities WHERE id=%s", (lifecycle_activity,)).fetchone()
    assert account == {"max_tool_calls": None, "tools_reserved": 0, "requests_reserved": 1, "cost": 100}, account
    ops = conn.execute("SELECT operation_id FROM activity_operations WHERE activity_id=%s ORDER BY operation_id",
                       (lifecycle_activity,)).fetchall()
    assert [x["operation_id"] for x in ops] == ["M1"], ops
    return lifecycle_activity


def run_s2(conn, folder: Path) -> dict:
    schema = SCHEMAS["s2"]
    source, version, activity = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    for name in BASELINE:
        conn.execute(MIGS[name])
    emit(event="baseline_001_007_applied", schema=schema)
    from app.capabilities.contracts import build_business_payload
    legacy_rows(conn, activity, source, version, build_business_payload(text="legacy-body"))
    row = conn.execute(
        "SELECT conname FROM pg_constraint WHERE conrelid='activity_operations'::regclass AND contype='c' "
        "AND pg_get_constraintdef(oid) IN ('CHECK ((reserved_cost_microunits > 0))','CHECK (reserved_cost_microunits > 0)')"
    ).fetchone()
    assert row is not None, "original cost check not found"
    conn.execute(f'ALTER TABLE activity_operations DROP CONSTRAINT "{row["conname"]}"')
    conn.execute("ALTER TABLE activity_operations ADD CONSTRAINT activity_operations_cost_tampered "
                 "CHECK (reserved_cost_microunits > 0 OR reserved_cost_microunits IS NULL)")
    before = snapshot(conn, activity)
    constraints_before = conn.execute(
        "SELECT count(*) AS n FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
        "WHERE n.nspname=%s", (schema,)).fetchone()["n"]
    info = None
    failing = connect(schema)
    try:
        try:
            failing.execute(MIGS["008_activity_tool_budget.sql"])
        except BaseException as exc:
            info = expect_migration_rejection(exc, "唯一识别")
            emit(event="rollback_008_rejected", **info)
        else:
            raise AssertionError("008 unexpectedly succeeded on tampered baseline")
    finally:
        failing.close()
    after = snapshot(conn, activity)
    assert after == before, "schema or rows changed after failed 008"
    constraints_after = conn.execute(
        "SELECT count(*) AS n FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
        "WHERE n.nspname=%s", (schema,)).fetchone()["n"]
    assert constraints_after == constraints_before
    new_columns = conn.execute(
        "SELECT count(*) AS n FROM information_schema.columns WHERE table_schema=%s "
        "AND table_name IN ('activities','activity_operations') AND column_name = ANY(%s)",
        (schema, list(NEW_COLUMNS))).fetchone()["n"]
    assert new_columns == 0, new_columns
    partial_constraints = conn.execute(
        "SELECT count(*) AS n FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
        "WHERE n.nspname=%s AND c.conname = ANY(%s)", (schema, list(NEW_CONSTRAINTS))).fetchone()["n"]
    assert partial_constraints == 0, partial_constraints
    tampered_present = conn.execute(
        "SELECT count(*) AS n FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
        "WHERE n.nspname=%s AND c.conname='activity_operations_cost_tampered'", (schema,)).fetchone()["n"]
    assert tampered_present == 1, tampered_present
    emit(event="rollback_intact", schema=schema, constraints=constraints_after,
         partial_ddl=partial_constraints, old_rows_unchanged=True)
    return {"activity": activity, "reject": info, "constraints": constraints_after}


def run_s3(conn, folder: Path) -> dict:
    schema = SCHEMAS["s3"]
    before_objects = schema_objects(conn, schema)
    assert all(value == 0 for value in before_objects.values()), before_objects
    info = None
    failing = connect(schema)
    try:
        try:
            failing.execute(MIGS["008_activity_tool_budget.sql"])
        except BaseException as exc:
            info = expect_migration_rejection(exc, "前置不存在")
            emit(event="missing_prereq_rejected", **info)
        else:
            raise AssertionError("008 unexpectedly succeeded on empty schema")
    finally:
        failing.close()
    after_objects = schema_objects(conn, schema)
    assert after_objects == before_objects, after_objects
    assert all(value == 0 for value in after_objects.values()), after_objects
    emit(event="missing_intact", schema=schema, objects=after_objects)
    return {"reject": info, "objects": after_objects}


SCENARIO_FUNCS = {"s1": run_s1, "s2": run_s2, "s3": run_s3}


def main(folder: Path) -> int:
    setup = connect("public", dict_rows=False)
    identity = setup.execute("SELECT current_database(), current_user").fetchone()
    assert identity == (UPGRADE_DB, ROLE), identity
    precheck = {}
    for key, schema in SCHEMAS.items():
        exists = setup.execute(
            "SELECT count(*) FROM information_schema.schemata WHERE schema_name=%s", (schema,)).fetchone()[0]
        tables = setup.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema=%s", (schema,)).fetchone()[0] if exists else 0
        precheck[key] = {"schema": schema, "exists": bool(exists), "tables": tables}
    emit(event="upgrade_schemas_precheck", **precheck)
    only = [x for x in (os.environ.get("TASK092_UPGRADE_ONLY") or "").split(",") if x]
    selected = [k for k in ("s1", "s2", "s3") if not only or k in only]
    for key in selected:
        # 仅本卡在专用升级库内自建的合成schema：先清后建保证幂等；定向重跑只重建所选schema。
        setup.execute(f'DROP SCHEMA IF EXISTS "{SCHEMAS[key]}" CASCADE')
        setup.execute(f'CREATE SCHEMA "{SCHEMAS[key]}"')
    setup.close()
    emit(event="schemas_reset", schemas=[SCHEMAS[k] for k in selected], only=only or None)
    results = {key: {"status": "not_run", "reason": "excluded_by_retry_scope"} for key in ("s1", "s2", "s3")}
    stop_after = None
    for key in selected:
        entry = {"status": "not_run"}
        results[key] = entry
        emit(event="upgrade_scenario_start", scenario=key)
        conn = None
        cleanup_error = None
        try:
            conn = connect(SCHEMAS[key])
            metrics = SCENARIO_FUNCS[key](conn, folder)
            entry.clear()
            entry.update({"status": "passed", **metrics})
        except BaseException as exc:
            entry.clear()
            entry.update({"status": "failure", "error": sanitized_error(exc),
                          "label": str(exc) if type(exc) is AssertionError else None})
            emit(event="upgrade_scenario_failed", scenario=key, **entry)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except BaseException as close_exc:
                    cleanup_error = type(close_exc).__name__
        if cleanup_error is not None:
            entry["cleanup_error"] = cleanup_error
            if entry["status"] == "passed":
                entry["status"] = "failure"
            stop_after = key
        emit(event="upgrade_scenario_result", scenario=key, status=entry["status"])
        if stop_after is not None:
            emit(event="upgrade_stopped", reason="scenario_cleanup_failed", after=stop_after)
            break
    summary = {"database": UPGRADE_DB, "role": ROLE, "schemas": SCHEMAS,
               "selected": selected, "results": results,
               "passed": [k for k, v in results.items() if v["status"] == "passed"],
               "failed": [k for k, v in results.items() if v["status"] == "failure"],
               "not_run": [k for k, v in results.items() if v["status"] == "not_run"]}
    (folder / "upgrade-summary.json").write_text(json.dumps(summary, default=str, ensure_ascii=False, indent=2),
                                                 encoding="utf-8")
    emit(event="upgrade_complete", passed=summary["passed"], failed=summary["failed"], not_run=summary["not_run"])
    return 0 if not summary["failed"] else 1


if __name__ == "__main__":
    assert sys.argv[1] == "--child"
    try:
        code = main(Path(sys.argv[2]))
    except BaseException as exc:
        emit(event="child_error", **sanitized_error(exc))
        code = 1
    raise SystemExit(code)
