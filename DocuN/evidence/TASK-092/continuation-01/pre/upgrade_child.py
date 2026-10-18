"""批次upgrade子进程：合法非空001—007→008、旧行不变、旧模型生命线与失败回滚。

s1 happy：真实旧行（received有/无正文、unknown、白名单非空、额度未配置）→008；
        旧行仅新增kind=model与预算默认；旧模型生命周期仍可用；未配置拒工具。
s2 rollback：成本约束被预先篡改→008识别失败→整事务回滚，旧schema原样。
s3 missing：空schema缺前置→008在ALTER前拒绝。
失败注入使用独立连接，失败后不复用其事务状态。
"""
from __future__ import annotations

from datetime import datetime, timezone
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


def emit(**item):
    print(json.dumps(item, default=str), flush=True)


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
    # 活动快照含 008 新增两列：008 前的库没有这两列，用 ->> 判缺失并显式标记。
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


def check_happy(conn, payload: tuple) -> dict:
    activity = str(uuid.uuid4())
    source, version = str(uuid.uuid4()), str(uuid.uuid4())
    for name in BASELINE:
        conn.execute(MIGS[name])
    emit(event="baseline_001_007_applied", schema=SCHEMAS["s1"])
    legacy_rows(conn, activity, source, version, payload)
    before = snapshot(conn, activity)
    constraints_before = conn.execute(
        "SELECT count(*) AS n FROM pg_constraint WHERE conrelid='activity_operations'::regclass AND contype='c'"
    ).fetchone()["n"]
    began = datetime.now(timezone.utc)
    conn.execute(MIGS["008_activity_tool_budget.sql"])
    committed = datetime.now(timezone.utc)
    after = snapshot(conn, activity)
    # 旧行字节不变：操作行仅新增三列（kind/arguments_sha256/tool_call_id），活动行仅新增两列默认。
    assert set(after["ops_columns"]) - set(before["ops_columns"]) == {"kind", "arguments_sha256", "tool_call_id"}
    assert set(after["activity"]) - set(before["activity"]) == {"max_tool_calls", "tools_reserved"}
    assert after["activity"]["max_tool_calls"] is None and after["activity"]["tools_reserved"] == 0
    for name, value in before["activity"].items():
        assert after["activity"][name] == value, name
    assert len(after["ops"]) == len(before["ops"]) == 3
    for old, new in zip(before["ops"], after["ops"]):
        assert new["kind"] == "model"
        assert {k: v for k, v in new.items() if k != "kind"} == old, new["operation_id"]
    assert after["results"] == before["results"]
    constraints_after = conn.execute(
        "SELECT count(*) AS n FROM pg_constraint WHERE conrelid='activity_operations'::regclass AND contype='c'"
    ).fetchone()["n"]
    assert constraints_after == constraints_before - 1 + 2
    emit(event="upgrade_happy_rows_intact", activity=activity, operations=len(after["ops"]),
         payload_sha256=after["results"][0]["payload_sha256"],
         applied_utc=began.isoformat(), committed_utc=committed.isoformat())
    # 旧模型生命周期在008 schema仍可用；未配置额度拒工具执行且零副作用（走真实仓储）。
    import asyncio
    from datetime import timedelta
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
        await ledger.begin_window_close(lifecycle_activity, lease.executor_id, lease.execution_generation)
        settled = await ledger.settle_execution_window(lifecycle_activity, lease.executor_id,
                                                       lease.execution_generation, window_seconds=10, elapsed_seconds=1)
        assert settled.name == "SETTLED"
        raw, digest = canonical_tool_arguments({"operation": "add", "left": 1, "right": 2})
        call = ToolExecutionInput("T1", "calc.1", "finite_calculate", raw, digest)
        try:
            await ledger.admit_tool_operation(ToolIntent(context=context, call=call))
        except AdmissionDenied as exc:
            assert str(exc) == "tool_limit_unconfigured", str(exc)
        else:
            raise AssertionError("unconfigured tool admission unexpectedly allowed")

    asyncio.Runner(loop_factory=psycopg_compatible_loop_factory).run(lifecycle())
    account = conn.execute(
        "SELECT max_tool_calls,tools_reserved,requests_reserved,cost_reserved_microunits AS cost "
        "FROM activities WHERE id=%s", (lifecycle_activity,)).fetchone()
    assert account == {"max_tool_calls": None, "tools_reserved": 0, "requests_reserved": 1, "cost": 100}, account
    ops = conn.execute("SELECT operation_id FROM activity_operations WHERE activity_id=%s ORDER BY operation_id",
                       (lifecycle_activity,)).fetchall()
    assert [x["operation_id"] for x in ops] == ["M1"], ops
    emit(event="legacy_lifecycle_ok", activity=lifecycle_activity)
    # 重复008：报错并整体回滚（独立连接，不复用其事务状态）。
    failing = connect(SCHEMAS["s1"])
    try:
        try:
            failing.execute(MIGS["008_activity_tool_budget.sql"])
        except Exception as exc:
            emit(event="repeat_008_rejected", type=type(exc).__name__, identification_failure="已有痕迹" in str(exc))
        else:
            raise AssertionError("repeat 008 unexpectedly succeeded")
    finally:
        failing.close()
    repeat_columns = conn.execute(
        "SELECT count(*) AS n FROM information_schema.columns WHERE table_schema=%s AND table_name='activities' "
        "AND column_name IN ('max_tool_calls','tools_reserved')", (SCHEMAS["s1"],)).fetchone()["n"]
    assert repeat_columns == 2
    return {"activity": activity, "lifecycle_activity": lifecycle_activity, "source": source, "version": version}


def check_rollback(conn) -> None:
    schema = SCHEMAS["s2"]
    for name in BASELINE:
        conn.execute(MIGS[name])
    source, version, activity = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
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
        "SELECT count(*) AS n FROM pg_constraint WHERE conrelid='activity_operations'::regclass").fetchone()["n"]
    failing = connect(schema)
    try:
        try:
            failing.execute(MIGS["008_activity_tool_budget.sql"])
        except Exception as exc:
            emit(event="rollback_008_rejected", type=type(exc).__name__, identification_failure="唯一识别" in str(exc))
        else:
            raise AssertionError("008 unexpectedly succeeded on tampered baseline")
    finally:
        failing.close()
    after = snapshot(conn, activity)
    assert after == before, "schema or rows changed after failed 008"
    constraints_after = conn.execute(
        "SELECT count(*) AS n FROM pg_constraint WHERE conrelid='activity_operations'::regclass").fetchone()["n"]
    assert constraints_after == constraints_before
    new_columns = conn.execute(
        "SELECT count(*) AS n FROM information_schema.columns WHERE table_schema=%s "
        "AND table_name IN ('activities','activity_operations') "
        "AND column_name IN ('max_tool_calls','tools_reserved','kind','arguments_sha256','tool_call_id')",
        (schema,)).fetchone()["n"]
    assert new_columns == 0, new_columns
    emit(event="rollback_intact", schema=schema, constraints=constraints_after)


def check_missing(conn) -> None:
    schema = SCHEMAS["s3"]
    failing = connect(schema)
    try:
        try:
            failing.execute(MIGS["008_activity_tool_budget.sql"])
        except Exception as exc:
            emit(event="missing_prereq_rejected", type=type(exc).__name__,
                 identification_failure="前置" in str(exc))
        else:
            raise AssertionError("008 unexpectedly succeeded on empty schema")
    finally:
        failing.close()
    tables = conn.execute(
        "SELECT count(*) AS n FROM information_schema.tables WHERE table_schema=%s", (schema,)).fetchone()["n"]
    assert tables == 0, tables
    emit(event="missing_intact", schema=schema)


def main(folder: Path) -> int:
    setup = connect("public", dict_rows=False)
    identity = setup.execute("SELECT current_database(), current_user").fetchone()
    assert identity == (UPGRADE_DB, ROLE), identity
    for schema in SCHEMAS.values():
        # 仅本卡在专用升级库内自建的合成schema：先清后建，保证跨批幂等重跑。
        setup.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        setup.execute(f'CREATE SCHEMA "{schema}"')
    setup.close()
    emit(event="schemas_reset", schemas=list(SCHEMAS.values()))
    conns = {key: connect(schema) for key, schema in SCHEMAS.items()}
    from app.capabilities.contracts import build_business_payload
    result = check_happy(conns["s1"], build_business_payload(json_object={"legacy": True}))
    check_rollback(conns["s2"])
    check_missing(conns["s3"])
    (folder / "upgrade-summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    emit(event="upgrade_complete", schemas=list(SCHEMAS.values()))
    return 0


if __name__ == "__main__":
    assert sys.argv[1] == "--child"
    try:
        code = main(Path(sys.argv[2]))
    except BaseException as exc:
        emit(event="child_error", type=type(exc).__name__,
             label=str(exc) if type(exc) is AssertionError else None)
        code = 1
    raise SystemExit(code)
