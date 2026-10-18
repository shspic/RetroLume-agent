"""TASK-083 D3 bounded PG and Windows recovery sample; runner supplies only synthetic DSN."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row

from app.activities import ActivityLedgerConflict, ActivitySpec, PostgresAdmissionLedger, SourceSnapshot
from app.runtime import psycopg_compatible_loop_factory
from app.worker.command import WorkerCommand
from app.worker.launcher import run_supervised_window
from app.worker.session import SessionConfig
from app.worker.windows_job import (
    ERROR_FILE_NOT_FOUND, JobOpenError, NamedJob, current_process_session_id, job_name,
)

BASE_DSN = os.environ.pop("RETROLUME_TASK_083_D3_DATABASE_URL")
MIGRATIONS = [BACKEND / "migrations" / name for name in (
    "001_materials.sql", "002_activities.sql", "003_pdf_review.sql",
    "004_activities_time_budget.sql", "005_activities_dispatch_closed.sql",
    "006_activities_running_owner_session.sql",
)]
FIXTURE = Path(__file__).with_name("fixture.py")


def emit(record):
    record["event_utc"] = datetime.now(timezone.utc).isoformat()
    record["event_monotonic"] = time.monotonic()
    print(json.dumps(record, ensure_ascii=False, default=str), flush=True)


def make_schema(label, *, migrate=True):
    name = "task083_d3_" + label + "_" + uuid4().hex[:8]
    with psycopg.connect(BASE_DSN, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(name)))
    scoped = make_conninfo(BASE_DSN, options=f"-c search_path={name}")
    with psycopg.connect(scoped, autocommit=True) as conn:
        for path in MIGRATIONS[:6 if migrate else 5]:
            conn.execute(path.read_text(encoding="utf-8"))
    emit({"phase":"schema", "label":label, "schema":name, "migrated":migrate})
    return name, scoped


def row(scoped, query, params=()):
    with psycopg.connect(scoped, row_factory=dict_row) as conn:
        return conn.execute(query, params).fetchone()


def run_async(coro):
    return asyncio.run(coro, loop_factory=psycopg_compatible_loop_factory)


async def build(scoped, *, maximum):
    activity, source, version = (str(uuid4()) for _ in range(3))
    async with await psycopg.AsyncConnection.connect(scoped) as conn:
        async with conn.transaction():
            await conn.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'d3',0)", (source,))
            await conn.execute(
                "INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'d3.txt','txt',%s,1)",
                (version,source,"d"*64),
            )
            await conn.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s",
                               (version,source))
    ledger = PostgresAdmissionLedger(scoped)
    spec = ActivitySpec(
        activity_id=activity, sources=(SourceSnapshot(source,version,1),),
        deadline_at=datetime.now(timezone.utc)+timedelta(minutes=20),
        max_requests=8,max_cost_microunits=800,reserve_cost_microunits=100,
        max_request_bytes=4096,max_output_tokens=256,max_running_seconds=maximum,
        allowed_models=(("deepseek_chat_completions","synthetic-model"),),
    )
    await ledger.create_activity(spec)
    return ledger, activity


def expire(scoped, activity):
    with psycopg.connect(scoped, autocommit=True) as conn:
        conn.execute("UPDATE activities SET lease_expires_at=CURRENT_TIMESTAMP - interval '1 minute' WHERE id=%s",
                     (activity,))


def migration_cases():
    emit({"phase":"scenario_start","scenario":"migration_empty"})
    name, scoped = make_schema("empty", migrate=False)
    with psycopg.connect(scoped, autocommit=True) as conn:
        before={r[0] for r in conn.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name='activities'",(name,))}
        conn.execute(MIGRATIONS[5].read_text(encoding="utf-8"))
        added={r[0] for r in conn.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name='activities'",(name,))}-before
        assert added=={"running_owner_session_id"}, added
        activity=str(uuid4())
        conn.execute("""INSERT INTO activities(id,status,scope_revision,deadline_at,max_requests,
            max_cost_microunits,reserve_cost_microunits,max_request_bytes,max_output_tokens,
            max_running_seconds) VALUES (%s,'pending',1,CURRENT_TIMESTAMP + interval '1 hour',1,1,1,1,1,6)""",(activity,))
        assert conn.execute("SELECT running_owner_session_id FROM activities WHERE id=%s",(activity,)).fetchone()[0] is None
        for valid in (0,4294967295):
            conn.execute("UPDATE activities SET running_owner_session_id=%s WHERE id=%s",(valid,activity))
            assert conn.execute("SELECT running_owner_session_id FROM activities WHERE id=%s",(activity,)).fetchone()[0]==valid
        for invalid in (-1,4294967296):
            try:
                conn.execute("UPDATE activities SET running_owner_session_id=%s WHERE id=%s",(invalid,activity))
            except psycopg.errors.CheckViolation:
                pass
            else: raise AssertionError(f"accepted invalid session {invalid}")
        assert conn.execute("SELECT running_owner_session_id FROM activities WHERE id=%s",(activity,)).fetchone()[0]==4294967295
    emit({"phase":"migration_empty","schema":name,"added":sorted(added),"valid":[0,4294967295],"invalid":[-1,4294967296]})

    emit({"phase":"scenario_start","scenario":"migration_old"})
    name, scoped = make_schema("old", migrate=False)
    activity=str(uuid4())
    with psycopg.connect(scoped, autocommit=True) as conn:
        conn.execute("""INSERT INTO activities(id,status,scope_revision,executor_id,lease_expires_at,
            deadline_at,max_requests,max_cost_microunits,reserve_cost_microunits,
            max_request_bytes,max_output_tokens,max_running_seconds,running_reserved_seconds)
            VALUES (%s,'running',1,'legacy',CURRENT_TIMESTAMP - interval '1 minute',
            CURRENT_TIMESTAMP + interval '1 hour',1,1,1,1,1,6,6)""",(activity,))
        conn.execute(MIGRATIONS[5].read_text(encoding="utf-8"))
        old=conn.execute("SELECT status,running_reserved_seconds,running_owner_session_id FROM activities WHERE id=%s",(activity,)).fetchone()
        assert old==("running",6,None),old
    emit({"phase":"migration_old","schema":name,"activity":activity,"row":old})

    emit({"phase":"scenario_start","scenario":"migration_rollback"})
    name, scoped = make_schema("rollback", migrate=False)
    migration=MIGRATIONS[5].read_text(encoding="utf-8")
    broken=migration.replace("COMMIT;", "ALTER TABLE activities ADD CONSTRAINT deliberate_failure CHECK (missing_column = 1);\nCOMMIT;")
    assert broken!=migration
    with psycopg.connect(scoped, autocommit=True) as conn:
        try: conn.execute(broken)
        except psycopg.Error: conn.execute("ROLLBACK")
        else: raise AssertionError("failure injection did not fail")
        count=conn.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='activities' AND column_name='running_owner_session_id'",(name,)).fetchone()[0]
        assert count==0,count
    emit({"phase":"migration_rollback","schema":name,"column_count":count})


def ledger_cases():
    emit({"phase":"scenario_start","scenario":"ledger_active_lease_rejected"})
    name, scoped=make_schema("ledger")
    ledger,activity=run_async(build(scoped,maximum=12))
    for invalid in (True,-1,4294967296,1.5,"1"):
        try: run_async(ledger.claim_lease(activity,"bad",lease_seconds=6,window_seconds=6,running_owner_session_id=invalid))
        except ValueError: pass
        else: raise AssertionError(f"accepted {invalid!r}")
    first=run_async(ledger.claim_lease(activity,"old",lease_seconds=6,window_seconds=6,running_owner_session_id=0))
    assert first and first.running_owner_session_id==0
    before=row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds,running_owner_session_id FROM activities WHERE id=%s",(activity,))
    assert before["running_owner_session_id"]==0 and before["running_reserved_seconds"]==6
    snapshot=run_async(ledger.inspect_window(activity))
    assert snapshot.running_owner_session_id==0 and not snapshot.lease_recoverable
    try:
        run_async(ledger.claim_lease(activity,"too_early",lease_seconds=6,window_seconds=6,
                                     running_owner_session_id=0,expected_previous_generation=first.execution_generation))
    except ActivityLedgerConflict: pass
    else: raise AssertionError("active database lease was stolen")
    assert row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds,running_owner_session_id FROM activities WHERE id=%s",(activity,))==before
    emit({"phase":"ledger_active_lease_rejected","schema":name,"activity":activity,"row":before})
    emit({"phase":"scenario_start","scenario":"ledger_new_g"})
    expire(scoped,activity)
    try:
        run_async(ledger.claim_lease(activity,"wrong_owner",lease_seconds=6,window_seconds=6,
                                     running_owner_session_id=8,expected_previous_generation=first.execution_generation))
    except ActivityLedgerConflict: pass
    else: raise AssertionError("mismatched old session was accepted")
    second=run_async(ledger.claim_lease(activity,"new",lease_seconds=6,window_seconds=6,running_owner_session_id=0,expected_previous_generation=first.execution_generation))
    assert second and second.execution_generation==first.execution_generation+1
    after=row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds,running_owner_session_id,dispatch_closed FROM activities WHERE id=%s",(activity,))
    assert (after["running_reserved_seconds"],after["running_settled_seconds"],after["running_owner_session_id"])==(6,6,0),after
    assert after["dispatch_closed"] is False,after
    for attempt in (
        lambda: run_async(ledger.claim_lease(activity,"late",lease_seconds=6,window_seconds=6,running_owner_session_id=0,expected_previous_generation=first.execution_generation)),
        lambda: run_async(ledger.begin_window_close(activity,"old",first.execution_generation)),
        lambda: run_async(ledger.settle_execution_window(activity,"old",first.execution_generation,
                                                       window_seconds=6,elapsed_seconds=1)),
    ):
        try: attempt()
        except ActivityLedgerConflict: pass
        else: raise AssertionError("old generation was accepted")
    assert row(scoped,"SELECT running_owner_session_id,running_reserved_seconds,running_settled_seconds,dispatch_closed FROM activities WHERE id=%s",(activity,))=={
        k:after[k] for k in ("running_owner_session_id","running_reserved_seconds","running_settled_seconds","dispatch_closed")}
    upper_ledger,upper_activity=run_async(build(scoped,maximum=6))
    upper=run_async(upper_ledger.claim_lease(upper_activity,"upper",lease_seconds=6,window_seconds=6,running_owner_session_id=4294967295))
    upper_row=row(scoped,"SELECT status,execution_generation,running_owner_session_id FROM activities WHERE id=%s",(upper_activity,))
    assert upper and upper.running_owner_session_id==4294967295
    assert upper_row["status"]=="running" and upper_row["execution_generation"]==upper.execution_generation
    assert upper_row["running_owner_session_id"]==4294967295,upper_row
    emit({"phase":"ledger_new_g","schema":name,"activity":activity,"old":before,"new":after,"upper_pending_claim":upper_row,
          "old_retry_branches":["claim_previous_generation_mismatch","close_current_generation_mismatch","settle_current_window_mismatch"],
          "recent_settled_gc_idempotency_exercised":False})

    emit({"phase":"scenario_start","scenario":"ledger_exhausted"})
    name, scoped=make_schema("exhaust")
    ledger,activity=run_async(build(scoped,maximum=6))
    first=run_async(ledger.claim_lease(activity,"old",lease_seconds=6,window_seconds=6,running_owner_session_id=7))
    expire(scoped,activity)
    exhausted=run_async(ledger.claim_lease(activity,"new",lease_seconds=6,window_seconds=6,running_owner_session_id=7,expected_previous_generation=first.execution_generation))
    after=row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds,running_owner_session_id,dispatch_closed FROM activities WHERE id=%s",(activity,))
    assert exhausted is None and (after["status"],after["running_reserved_seconds"],after["running_settled_seconds"],after["running_owner_session_id"],after["dispatch_closed"])==("pending",0,6,None,True),after
    emit({"phase":"ledger_exhausted","schema":name,"activity":activity,"after":after})


def observe_source_lock_wait(scoped, application_name):
    until=time.monotonic()+.9
    with psycopg.connect(scoped,autocommit=True) as observer:
        while time.monotonic()<until:
            count=observer.execute("""SELECT count(*) FROM pg_stat_activity
                WHERE application_name=%s AND wait_event_type='Lock'
                  AND query LIKE '%%material_sources%%'""",(application_name,)).fetchone()[0]
            if count:
                return True
            time.sleep(.05)
    raise AssertionError("source row lock wait was not observed")

def lock_barrier_case():
    emit({"phase":"scenario_start","scenario":"ledger_lock_barrier"})
    started=time.monotonic()
    name,scoped=make_schema("lock_barrier")
    ledger,activity=run_async(build(scoped,maximum=12))
    source=row(scoped,"SELECT source_id FROM activity_scope_sources WHERE activity_id=%s",(activity,))["source_id"]
    deadline=datetime.now(timezone.utc)+timedelta(seconds=1.4)
    with psycopg.connect(scoped,autocommit=True) as conn:
        conn.execute("UPDATE activities SET deadline_at=%s WHERE id=%s",(deadline,activity))
    before=row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s",(activity,))
    claim_app="task083_claim_"+uuid4().hex[:8]
    barrier_ledger=PostgresAdmissionLedger(make_conninfo(scoped,application_name=claim_app))
    with psycopg.connect(scoped) as holder:
        holder.execute("SELECT id FROM material_sources WHERE id=%s FOR UPDATE",(source,)).fetchone()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(lambda: run_async(barrier_ledger.claim_lease(activity,"after_deadline",lease_seconds=6,window_seconds=6,running_owner_session_id=0)))
            claim_wait=observe_source_lock_wait(scoped,claim_app)
            claim_wait_at=datetime.now(timezone.utc)
            assert claim_wait_at<deadline,"claim wait was only observed after deadline"
            assert not future.done(),"source lock did not block claim"
            time.sleep(max(0,(deadline-datetime.now(timezone.utc)).total_seconds()+.2))
            holder.commit()
            try: future.result(timeout=4)
            except ActivityLedgerConflict: pass
            else: raise AssertionError("claim crossed deadline while source lock was held")
    after=row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s",(activity,))
    assert after==before,(before,after)

    lease_ledger,lease_activity=run_async(build(scoped,maximum=12))
    first=run_async(lease_ledger.claim_lease(lease_activity,"old",lease_seconds=6,window_seconds=6,running_owner_session_id=0))
    assert first
    lease_source=row(scoped,"SELECT source_id FROM activity_scope_sources WHERE activity_id=%s",(lease_activity,))["source_id"]
    expiry=datetime.now(timezone.utc)+timedelta(seconds=1.4)
    with psycopg.connect(scoped,autocommit=True) as conn:
        conn.execute("UPDATE activities SET lease_expires_at=%s WHERE id=%s",(expiry,lease_activity))
    inspect_app="task083_inspect_"+uuid4().hex[:8]
    inspect_ledger=PostgresAdmissionLedger(make_conninfo(scoped,application_name=inspect_app))
    with psycopg.connect(scoped) as holder:
        holder.execute("SELECT id FROM material_sources WHERE id=%s FOR UPDATE",(lease_source,)).fetchone()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(lambda: run_async(inspect_ledger.inspect_window(lease_activity)))
            inspect_wait=observe_source_lock_wait(scoped,inspect_app)
            inspect_wait_at=datetime.now(timezone.utc)
            assert inspect_wait_at<expiry,"inspect wait was only observed after expiry"
            assert not future.done(),"source lock did not block inspect"
            time.sleep(max(0,(expiry-datetime.now(timezone.utc)).total_seconds()+.2))
            holder.commit()
            snapshot=future.result(timeout=4)
    assert snapshot.status=="running" and snapshot.lease_recoverable,snapshot
    emit({"phase":"ledger_lock_barrier","schema":name,"deadline":deadline,"expiry":expiry,
          "claim_before":before,"claim_after":after,"claim_lock_wait_observed":claim_wait,
          "claim_wait_at":claim_wait_at,"inspect_wait_at":inspect_wait_at,
          "inspect_lock_wait_observed":inspect_wait,"snapshot_recoverable":snapshot.lease_recoverable,
          "elapsed_seconds":time.monotonic()-started})

def windows_case():
    emit({"phase":"scenario_start","scenario":"windows_recovery"})
    scene_started=time.monotonic()
    name, scoped=make_schema("windows")
    ledger,activity=run_async(build(scoped,maximum=12))
    session=current_process_session_id()
    first=run_async(ledger.claim_lease(activity,"old",lease_seconds=6,window_seconds=6,running_owner_session_id=session))
    old=NamedJob.create(activity,first.execution_generation,max_processes=1)
    old_record={"generation":first.execution_generation,"session":session,"name":old.name}
    try:
        old_record["pid"]=old.spawn_suspended([sys._base_executable,"-B",str(FIXTURE),"fast"],cwd=str(BACKEND))
        old_record["created_100ns"]=old.process_creation_time_100ns()
        assert old.active_processes()==1
        old.resume()
        assert old.wait_empty_until(time.monotonic_ns()+3_000_000_000)
        old_record["tree_zero"]=old.active_processes()
    finally:
        old.close()
    old_record["handles_closed"]=True
    try:
        NamedJob.open_existing(activity,first.execution_generation)
    except JobOpenError as exc:
        old_record["open_error_code"]=exc.code
        assert exc.code==ERROR_FILE_NOT_FOUND
    else: raise AssertionError("old Job still exists")
    pre=row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds,running_owner_session_id FROM activities WHERE id=%s",(activity,))
    expire(scoped,activity)
    config=SessionConfig(window_seconds=6,request_timeout_seconds=.5,stop_grace_seconds=1,
                         startup_limit_seconds=2,manager_db_timeout_seconds=1.5,
                         cleanup_seconds=2,mutex_wait_seconds=1,manager_overhead_seconds=10,
                         single_host_single_session_recovery=True)
    start=time.monotonic()
    outcome=run_supervised_window(ledger,config,activity,"new",WorkerCommand(),run_tag="d3-"+uuid4().hex[:8])
    elapsed=time.monotonic()-start
    final=row(scoped,"SELECT status,execution_generation,running_reserved_seconds,running_settled_seconds,running_owner_session_id,last_settled_generation,last_settled_seconds FROM activities WHERE id=%s",(activity,))
    assert outcome.state=="settled",asdict(outcome)
    assert outcome.active_processes_at_end==0 and not outcome.cleanup_incomplete and not outcome.cleanup_errors,asdict(outcome)
    assert outcome.running_owner_session_id==session and outcome.generation==first.execution_generation+1
    assert outcome.job_name==job_name(activity,outcome.generation)
    assert outcome.pid and outcome.worker_created_100ns and outcome.manager_pid and outcome.manager_created_100ns
    assert final["status"]=="pending" and final["running_reserved_seconds"]==0
    assert final["running_settled_seconds"]==6+outcome.settled_seconds
    assert final["last_settled_generation"]==outcome.generation and final["running_owner_session_id"] is None
    scene_elapsed=time.monotonic()-scene_started
    assert scene_elapsed<=30,scene_elapsed
    emit({"phase":"windows_recovery","schema":name,"activity":activity,"old":old_record,
          "pre":pre,"new_outcome":asdict(outcome),"final":final,"elapsed_seconds":elapsed,
          "transaction_committed":True,"scene_seconds":scene_elapsed})


def require_assertions(level):
    if level != 0:
        raise RuntimeError("D3 assertions require optimize=0")


def main():
    require_assertions(sys.flags.optimize)
    requested=os.environ.get("D3_PARTS","migration,ledger,windows").split(",")
    if len(set(requested)) != len(requested):
        raise ValueError("duplicate D3 part selection")
    parts=set(requested)
    if not parts or not parts <= {"migration","ledger","windows"}:
        raise ValueError("invalid D3 part selection")
    if "migration" in parts: migration_cases()
    if "ledger" in parts: ledger_cases(); lock_barrier_case()
    if "windows" in parts: windows_case()
    emit({"phase":"complete","all_pass":True,"parts":[p for p in ("migration","ledger","windows") if p in parts]})


if __name__=="__main__":
    main()
