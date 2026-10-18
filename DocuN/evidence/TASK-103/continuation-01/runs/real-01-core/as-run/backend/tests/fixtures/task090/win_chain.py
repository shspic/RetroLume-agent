"""TASK-089 最小真实 Windows 组合：复制task088，仅一例json及新库身份。

来源：控制流复制自 fixtures/task085/real_cases.py 的测试自举注入模式。
差异：迁移含 007；场景缩减为本卡成功链两例（json/text）；断言升级为
G3 协议3（business_commit=committed、回执无正文、payload_sha256）与
关门/settle 后 read_committed_result 合法读一致。被独立外层Job限制，
零供应商网络；替身 transport 仅替换发送边界，真实监督/身份/提交路径不绕过。
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
from unittest.mock import patch
from uuid import uuid4

BACKEND=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(BACKEND))
import psycopg
from psycopg.rows import dict_row
from app.activities import ActivitySpec, SourceSnapshot, PostgresAdmissionLedger, ResultReadStatus
from app.capabilities.contracts import (
    CallContext, ModelCallRequest, ModelServiceConfig, build_business_payload,
)
from app.worker.one_call import run_one_call
from app.activities.service import ActivityService
from app.capabilities.contracts import AdmissionIntent,Provider,LedgerOutcome,LedgerDisposition
from app.worker.session import SessionConfig
from app.worker.command import _INTERPRETER
from app.worker.supervisor_ipc import NamedMapping
from app.worker.windows_job import NamedJob, JobOpenError, ERROR_FILE_NOT_FOUND
from app.runtime import psycopg_compatible_loop_factory
import app.worker.launcher as launcher

EVIDENCE = Path(os.environ["TASK090_EVIDENCE"]).resolve()
DSN = os.environ.get("RETROLUME_SCOPE_TEST_DATABASE_URL", "")
ROLE = "retrolume_task090_synth"
DBNAME = "retrolume_task090_scope"

def emit(**item): print(json.dumps(item,default=str),flush=True)
def check(condition,label):
    if not condition: raise AssertionError(label)
def run(coro):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner: return runner.run(coro)

def synthetic_supervisor(cls,mapping_name):
    api=launcher._api()
    executable=str(sys._base_executable)
    argv=[executable,"-B",str(Path(__file__).with_name("bootstrap.py")),"sup",str(EVIDENCE),mapping_name]
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

def rows(dsn,query,params=()):
    with psycopg.connect(dsn,connect_timeout=2,row_factory=dict_row) as conn:
        return conn.execute(query,params).fetchall()

async def build(dsn):
    activity,source,version=(str(uuid4()) for _ in range(3))
    async with await psycopg.AsyncConnection.connect(dsn,connect_timeout=2) as conn:
        await conn.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'task088',0)",(source,))
        await conn.execute("INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'synthetic.txt','txt',%s,1)",(version,source,"8"*64))
        await conn.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s",(version,source))
    ledger=PostgresAdmissionLedger(dsn,connect_timeout_seconds=1,statement_timeout_ms=500,lock_timeout_ms=200)
    await ledger.create_activity(ActivitySpec(activity,(SourceSnapshot(source,version,1),),
        datetime.now(timezone.utc)+timedelta(minutes=5),8,800,100,4096,256,30,
        (("deepseek_chat_completions","synthetic-model"),),()))
    lease=await ledger.claim_lease(activity,"prepare090",lease_seconds=30,window_seconds=10)
    context=CallContext(activity_id=activity,executor_id=lease.executor_id,operation_id="P",execution_generation=lease.execution_generation,scope_revision=lease.scope_revision)
    permit=await ledger.admit(AdmissionIntent(context,Provider.DEEPSEEK_CHAT_COMPLETIONS,"synthetic-model",512,40,()))
    await ledger.mark_dispatch_started(permit)
    fmt,body,digest=build_business_payload(json_object={"parent":"低信任历史"})
    await ledger.record_outcome(permit,LedgerOutcome(LedgerDisposition.RECEIVED,payload_format=fmt,payload=body,payload_sha256=digest))
    await ledger.begin_window_close(activity,lease.executor_id,lease.execution_generation)
    await ledger.settle_execution_window(activity,lease.executor_id,lease.execution_generation,window_seconds=10,elapsed_seconds=1)
    emit(event="parent_prepared",activity=activity,operation="P",scope_revision=1,payload_sha256=digest)
    return ledger,activity,source,version

CONFIG=SessionConfig(window_seconds=10,request_timeout_seconds=2,stop_grace_seconds=1,
    startup_limit_seconds=3,manager_db_timeout_seconds=2,cleanup_seconds=2,
    mutex_wait_seconds=1,manager_overhead_seconds=12)

def invoke(ledger,activity,label):
    service=ModelServiceConfig(provider="deepseek_chat_completions",base_url="https://api.deepseek.com",
        model="synthetic-model",api_key=secrets.token_urlsafe(24),timeout_seconds=.5,max_request_bytes=4096,max_response_bytes=4096)
    request=ModelCallRequest(messages=[{"role":"user","content":label}],max_output_tokens=40,
        response_mode="json_object" if label=="json" else "text")
    result=run(ActivityService(ledger).continue_from_result(activity,"P","Q","explicit-followup-090",service,CONFIG,"executor090","run090"))
    check(result.status=="committed_current","service business current")
    check(result.business.snapshot.payload_sha256==result.supervision.model_receipt["result"]["payload_sha256"],"service business hash")
    emit(event="service_result",status=result.status,parent="P",child="Q",settlement=asdict(result.settlement))
    return result.supervision


def expected_payload(label):
    if label=="json":
        return build_business_payload(json_object={"synthetic": True})
    return build_business_payload(text="synthetic-response-088")

def cleanup(dsn,activity,source,version):
    with psycopg.connect(dsn,connect_timeout=2,autocommit=True) as conn:
        for sql in (
            "DELETE FROM activity_operation_results WHERE activity_id=%s",
            "DELETE FROM activity_operations WHERE activity_id=%s",
            "DELETE FROM activity_allowed_models WHERE activity_id=%s",
            "DELETE FROM activity_scope_sources WHERE activity_id=%s",
            "DELETE FROM activities WHERE id=%s",
        ):
            conn.execute(sql,(activity,))
        conn.execute("UPDATE material_sources SET current_version=NULL WHERE id=%s",(source,))
        conn.execute("DELETE FROM material_versions WHERE id=%s",(version,))
        conn.execute("DELETE FROM material_sources WHERE id=%s",(source,))

def main():
    if not DSN:
        emit(event="skip",reason="dedicated task089 DSN required");return 77
    identity=row(DSN,"SELECT current_database() AS db,current_user AS role")
    check(identity=={"db":DBNAME,"role":ROLE},"dedicated database identity mismatch")
    emit(event="database_identity",**identity)
    with patch.object(launcher._SuspendedSupervisor,"create",classmethod(synthetic_supervisor)):
        for label in ("json",):
            emit(event="scenario_start",id="chain-"+label)
            ledger,activity,source,version=run(build(DSN))
            try:
                outcome=invoke(ledger,activity,label)
                data=asdict(outcome)
                receipt=data.pop("model_receipt")
                # 树零/自有句柄关闭后：业务Job必须已销毁。
                if outcome.job_name:
                    try: job=NamedJob.open_existing(activity,outcome.generation)
                    except JobOpenError as exc: check(exc.code==ERROR_FILE_NOT_FOUND,"job open unexpected")
                    else:
                        try: check(job.active_processes()==0,"business tree residual")
                        finally: job.close()
                        raise AssertionError("business job handle retained")
                check(outcome.state=="settled","supervision settled")
                check(not outcome.cleanup_incomplete,"cleanup incomplete")
                # 协议3：committed、回执无正文、hash合法。
                check(receipt["protocol"]==3,"receipt protocol 3")
                check(receipt["business_commit"]=="committed","business_commit committed")
                result=receipt["result"]
                check(result["status"]=="succeeded","model succeeded")
                check(result["text"] is None and result["json_object"] is None,"receipt carries payload")
                digest=result["payload_sha256"]
                check(isinstance(digest,str) and len(digest)==64 and all(c in "0123456789abcdef" for c in digest),"payload digest shape")
                # 单次发送与持久事实：恰好一条 received 操作与一条 results 行。
                account=row(DSN,"SELECT status,running_reserved_seconds,running_settled_seconds,requests_reserved,dispatch_closed,execution_generation FROM activities WHERE id=%s",(activity,))
                ops=rows(DSN,"SELECT operation_id,state,execution_generation,scope_revision FROM activity_operations WHERE activity_id=%s AND operation_id='Q'",(activity,))
                results=rows(DSN,"SELECT payload_format,payload,payload_sha256,admission_id,execution_generation,scope_revision FROM activity_operation_results WHERE activity_id=%s AND operation_id='Q'",(activity,))
                check(len(ops)==1 and ops[0]["state"]=="received","exactly one received operation")
                check(account["requests_reserved"]==2 and account["dispatch_closed"],"one admission and door closed")
                check(account["running_reserved_seconds"]==0 and account["running_settled_seconds"]==1+outcome.settled_seconds,"settled accounting")
                check(len(results)==1,"single result row")
                check(account["execution_generation"]==ops[0]["execution_generation"]+1,"close generation increment")
                expected_format,expected_text,expected_sha=expected_payload(label)
                check(results[0]["payload_format"]==expected_format,"stored format")
                check(results[0]["payload"]==expected_text,"stored canonical payload")
                check(results[0]["payload_sha256"]==expected_sha==digest,"stored hash equals receipt hash")
                # 关门/settle 后合法 read：状态/hash/正文与持久事实一致。
                snapshot=run(ledger.read_committed_result(activity,"Q"))
                check(snapshot.read_status is ResultReadStatus.COMMITTED_CURRENT,"read committed current")
                check(snapshot.payload_sha256==digest and snapshot.payload==expected_text,"read payload consistent")
                check(str(snapshot.admission_id)==str(results[0]["admission_id"]),"read admission binding")
                list_page=run(ledger.list_committed_results(activity,limit=10))
                check(len(list_page)==2 and all(x.payload is None for x in list_page) and any(x.operation_id=="Q" and x.payload_sha256==digest for x in list_page),"list metadata only")
                emit(event="hash_binding", receipt=digest, database=results[0]["payload_sha256"], read=snapshot.payload_sha256, inner_protocol=receipt["protocol"])
                emit(event="scenario_result",id="chain-"+label,outcome={**data,"model_status":result["status"],"business_commit":receipt["business_commit"],"payload_sha256":digest},account=account,operations=ops)
                emit(event="scenario_complete",id="chain-"+label)
            finally:
                cleanup(DSN,activity,source,version)
                emit(event="case_cleanup",activity=activity,source=source,version=version)
    emit(event="complete",scenarios=1)
    return 0

if __name__=="__main__":
    try: code=main()
    except BaseException as exc:
        # 只保存类型与本夹具的固定断言标签；不打印驱动或数据异常文本。
        emit(event="error",type=type(exc).__name__,label=str(exc) if type(exc) is AssertionError else None)
        code=1
    raise SystemExit(code)
