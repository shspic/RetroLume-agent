"""本卡合成PG/Windows场景；被独立外层Job限制，零供应商网络。"""
from __future__ import annotations
import asyncio
import ctypes
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import secrets
import subprocess
import sys
import time
from unittest.mock import patch
from uuid import uuid4

BACKEND=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(BACKEND))
import psycopg
from psycopg.rows import dict_row
from app.activities import ActivitySpec, SourceSnapshot, PostgresAdmissionLedger
from app.capabilities.contracts import CallContext, ModelCallRequest, ModelServiceConfig
from app.worker.one_call import run_one_call
from app.worker.session import SessionConfig
from app.worker.command import _INTERPRETER
from app.worker.supervisor_ipc import NamedMapping
from app.worker.windows_job import NamedJob, JobOpenError, ERROR_FILE_NOT_FOUND
from app.runtime import psycopg_compatible_loop_factory
import app.worker.launcher as launcher

def emit(**item): print(json.dumps(item,default=str),flush=True)
def check(condition,label):
    if not condition: raise AssertionError(label)
def run(coro):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner: return runner.run(coro)

def synthetic_supervisor(cls,mapping_name):
    api=launcher._api()
    executable=str(sys._base_executable)
    argv=[executable,"-B",str(Path(__file__).with_name("bootstrap.py")),"sup",mapping_name]
    command=ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
    env=launcher._environment_block()
    startup=launcher._STARTUPINFOW();startup.cb=ctypes.sizeof(startup)
    info=launcher._PROCESS_INFORMATION()
    if not api.CreateProcessW(executable,command,None,None,False,
        launcher.CREATE_SUSPENDED|launcher.CREATE_NO_WINDOW|launcher.CREATE_UNICODE_ENVIRONMENT,
        ctypes.cast(env,ctypes.c_void_p),str(BACKEND),ctypes.byref(startup),ctypes.byref(info)):
        raise launcher.ProcessCreationError(ctypes.get_last_error(),cls(api,info) if info.hProcess or info.hThread else None)
    return cls(api,info)

def row(dsn,query,params=()):
    with psycopg.connect(dsn,connect_timeout=2,row_factory=dict_row) as conn:
        return conn.execute(query,params).fetchone()

async def build(dsn,maximum=30):
    activity,source,version=(str(uuid4()) for _ in range(3))
    async with await psycopg.AsyncConnection.connect(dsn,connect_timeout=2) as conn:
        await conn.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'task085',0)",(source,))
        await conn.execute("INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'synthetic.txt','txt',%s,1)",(version,source,"8"*64))
        await conn.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s",(version,source))
    ledger=PostgresAdmissionLedger(dsn,connect_timeout_seconds=1,statement_timeout_ms=500,lock_timeout_ms=200)
    await ledger.create_activity(ActivitySpec(activity,(SourceSnapshot(source,version,1),),
        datetime.now(timezone.utc)+timedelta(minutes=5),8,800,100,4096,256,maximum,
        (("deepseek_chat_completions","synthetic-model"),),("finite_calculate",)))
    return ledger,activity,source

CONFIG=SessionConfig(window_seconds=10,request_timeout_seconds=2,stop_grace_seconds=1,
    startup_limit_seconds=3,manager_db_timeout_seconds=2,cleanup_seconds=2,
    mutex_wait_seconds=1,manager_overhead_seconds=12)

def invoke(ledger,activity,label,*,model="synthetic-model",operation=None):
    service=ModelServiceConfig(provider="deepseek_chat_completions",base_url="https://api.deepseek.com",
        model=model,api_key=secrets.token_urlsafe(24),timeout_seconds=.5,max_request_bytes=4096,max_response_bytes=4096)
    request=ModelCallRequest(messages=[{"role":"user","content":label}],max_output_tokens=40,
        response_mode="json_object" if label=="json" else "text",
        allowed_tools={"finite_calculate"} if label=="tool" else set())
    return run_one_call(ledger,CONFIG,activity,"task085-executor",operation or ("op-"+label),request,service,run_tag="run-"+label)

def record(dsn,activity,label,outcome):
    data=asdict(outcome)
    receipt=data.pop("model_receipt")
    data["model_status"]=receipt["result"]["status"] if receipt else None
    data["business_commit"]=receipt["business_commit"] if receipt else None
    if receipt:
        data["receipt_context"]=receipt["context"]
    account=row(dsn,"SELECT status,execution_generation,scope_revision,running_reserved_seconds,running_settled_seconds,requests_reserved,dispatch_closed FROM activities WHERE id=%s",(activity,))
    operations=[]
    with psycopg.connect(dsn,connect_timeout=2,row_factory=dict_row) as conn:
        operations=conn.execute("SELECT operation_id,executor_id,execution_generation,scope_revision,state,disposition,error_code FROM activity_operations WHERE activity_id=%s",(activity,)).fetchall()
    # 精确业务Job在SUP释放全部句柄后必须已销毁。
    if outcome.job_name:
        try: job=NamedJob.open_existing(activity,outcome.generation)
        except JobOpenError as exc: check(exc.code==ERROR_FILE_NOT_FOUND,"job open unexpected")
        else:
            try: check(job.active_processes()==0,"business tree residual")
            finally: job.close()
            raise AssertionError("business job handle retained")
    emit(event="scenario_result",id=label,outcome=data,account=account,operations=operations)
    check(not outcome.cleanup_incomplete or label=="lease_conflict","cleanup incomplete")
    return receipt,account,operations

def main():
    if len(sys.argv)!=2:
        emit(event="skip",reason="dedicated task085 mapping required");return 77
    mapping=NamedMapping.open_existing(sys.argv[1])
    try: data=mapping.read_request()
    finally: mapping.close()
    dsn=data["dsn"]
    identity=row(dsn,"SELECT current_database() AS db,current_user AS role")
    check(identity=={"db":"retrolume_task085_onecall","role":data["role"]},"dedicated database identity mismatch")
    emit(event="database_identity",**identity)
    with psycopg.connect(dsn,connect_timeout=2,autocommit=True) as conn:
        for path in sorted((BACKEND/"migrations").glob("00[1-6]_*.sql")): conn.execute(path.read_text(encoding="utf-8"))
    # 生产固定入口：合法配置但未获活动模型授权，真实gateway/PG必须拒绝出站。
    emit(event="scenario_start",id="production_rejected")
    ledger,activity,_=run(build(dsn))
    outcome=invoke(ledger,activity,"production_rejected",model="unauthorized-model")
    receipt,account,ops=record(dsn,activity,"production_rejected",outcome)
    check(outcome.state=="settled" and receipt["result"]["status"]=="rejected" and not ops,"fixed entry rejection")
    emit(event="scenario_complete",id="production_rejected")

    unknown_activity=None
    with patch.object(launcher._SuspendedSupervisor,"create",classmethod(synthetic_supervisor)):
        for label in ("success","json","tool","unknown","unknown_repeat","hard","no_balance","cancelled","source_invalid","lease_conflict","short"):
            emit(event="scenario_start",id=label)
            if label=="unknown_repeat":
                ledger,activity,_=unknown_activity
            else:
                ledger,activity,source=run(build(dsn,maximum=1 if label in ("short","no_balance") else 30))
            if label=="no_balance":
                with psycopg.connect(dsn,autocommit=True) as conn: conn.execute("UPDATE activities SET running_settled_seconds=max_running_seconds WHERE id=%s",(activity,))
            elif label=="cancelled": run(ledger.cancel_activity(activity))
            elif label=="source_invalid":
                with psycopg.connect(dsn,autocommit=True) as conn: conn.execute("UPDATE material_sources SET revision=revision+1 WHERE id=%s",(source,))
            elif label=="lease_conflict":
                # 当前真实会话由仓储写入，保持有效旧租约；不制造旧业务进程。
                from app.worker.windows_job import current_process_session_id
                run(ledger.claim_lease(activity,"other",lease_seconds=20,window_seconds=10,running_owner_session_id=current_process_session_id()))
            outcome=invoke(ledger,activity,label,operation="op-unknown" if label=="unknown_repeat" else None)
            receipt,account,ops=record(dsn,activity,label,outcome)
            if label in ("success","json","tool","unknown"):
                expected={"success":"succeeded","json":"succeeded","tool":"tool_plan","unknown":"unknown"}[label]
                check(outcome.state=="settled" and receipt["result"]["status"]==expected,"model/supervision status")
                check(len(ops)==1 and ops[0]["execution_generation"]==outcome.generation and ops[0]["scope_revision"]==receipt["context"]["scope_revision"],"claim operation binding")
                check(account["running_reserved_seconds"]==0 and account["running_settled_seconds"]==outcome.settled_seconds,"settled accounting")
                check(account["requests_reserved"]==1 and account["dispatch_closed"],"exactly one admission and close")
                check(ops[0]["state"]==("unknown" if label=="unknown" else "received"),"operation final state")
                if label=="unknown": unknown_activity=(ledger,activity,source)
            elif label=="unknown_repeat":
                check(receipt["result"]["status"]=="rejected" and len(ops)==1 and ops[0]["state"]=="unknown" and account["requests_reserved"]==1,"unknown operation resent")
            elif label=="hard":
                check(outcome.state=="stopped_at_deadline" and receipt is None and outcome.active_processes_at_end==0,"hard deadline result")
                check(account["running_reserved_seconds"]==10 and account["running_settled_seconds"]==0 and ops[0]["state"]=="dispatched","conservative hard deadline accounting")
            else:
                check(receipt is None and outcome.pid is None and not ops,"rejection spawned or dispatched")
            emit(event="scenario_complete",id=label)
    emit(event="complete",scenarios=12)
    return 0

if __name__=="__main__":
    try: code=main()
    except BaseException as exc:
        # 只保存类型与本夹具的固定断言标签；不打印驱动或数据异常文本。
        emit(event="error",type=type(exc).__name__,label=str(exc) if type(exc) is AssertionError else None)
        code=1
    raise SystemExit(code)
