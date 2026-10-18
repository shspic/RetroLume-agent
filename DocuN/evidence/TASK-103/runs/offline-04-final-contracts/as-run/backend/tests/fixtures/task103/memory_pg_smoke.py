"""新普通app的实际记忆CRUD、固定选择与撤销清理组合。"""
from __future__ import annotations
import asyncio
from datetime import datetime,timedelta,timezone
import io
import json
import secrets
import sys
import time
from urllib.parse import quote
from uuid import uuid4
import psycopg
from psycopg import sql
from .control import Control,ROOT,EVIDENCE,atomic_json,SECRET_VALUES,redact
from .resources import OwnedDocker


async def scenario(app_dsn):
    from app.activities import PostgresAdmissionLedger,ActivitySpec,SourceSnapshot
    from app.memory.contracts import MemoryCommandInput,MemorySelectionInput
    from app.memory.service import MemoryService
    ledger=PostgresAdmissionLedger(app_dsn);service=MemoryService(ledger)
    cap=await ledger.probe_memory();assert cap["write"] and cap["cleanup"],cap
    mid=str(uuid4())
    save=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=0,action="save",
        body={"kind":"self_report","title":"合成单位笔记","text":"我仍容易忘记分钟换算"})
    receipt=await service.submit_command(save);assert receipt["revision_after"]==1,receipt
    duplicate=await service.submit_command(save);assert duplicate["replayed"] and duplicate["revision_after"]==1
    view=await ledger.read_memory_snapshot(mid);assert view["body"]["text"]==save.body["text"]
    impact=await ledger.preview_memory_change(mid,1,"revise")
    revise=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=1,action="revise",
      body={"kind":"self_report","title":"更新合成笔记","text":"我需要继续练习单位",
            "base_body_sha256":view["body_sha256"],"impact_token":impact["impact_token"]})
    updated=await service.submit_command(revise);assert updated["version_after"]==2
    old=await ledger.read_memory_snapshot(mid,version=1);assert old["qualification"]=="superseded" and old["body"]["text"]==save.body["text"]
    now=await ledger.read_memory_snapshot(mid)
    impact=await ledger.preview_memory_change(mid,2,"revise")
    same=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=2,action="revise",
      body={"kind":"self_report","title":now["body"]["title"],"text":now["body"]["text"],
            "base_body_sha256":now["body_sha256"],"impact_token":impact["impact_token"]})
    no_effect=await service.submit_command(same);assert no_effect["version_after"]==2 and no_effect["revision_after"]==2
    later=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=2,action="revise",
      body={**same.body,"text":"不同正文仍可从同CAS修订"})
    third=await service.submit_command(later);assert third["version_after"]==3
    now=await ledger.read_memory_snapshot(mid)
    from app.materials.repository import PostgresMaterials
    from app.storage.originals import OriginalStore
    data_dir=EVIDENCE/"workspace"/"data";data_dir.mkdir(parents=True,exist_ok=True)
    originals=data_dir/"originals";originals.mkdir(exist_ok=True)
    raw="平均速度等于路程除以时间。120米除以120秒等于1米每秒。\n".encode()
    original=OriginalStore(originals).put(io.BytesIO(raw),max_bytes=5*1024*1024)
    source=PostgresMaterials(app_dsn).save(source_id=None,expected_version=None,filename="task103-synthetic-speed.md",
      format="md",sha256=original.sha256,size=original.size)
    aid=str(uuid4())
    spec=ActivitySpec(activity_id=aid,sources=(SourceSnapshot(source["id"],source["version_id"],source["revision"]),),
      deadline_at=datetime.now(timezone.utc)+timedelta(hours=1),max_requests=24,max_cost_microunits=1000000,
      reserve_cost_microunits=1000,max_request_bytes=65536,max_output_tokens=2048,max_running_seconds=240,
      allowed_models=(("deepseek_chat_completions","deepseek-v4-flash"),),allowed_tools=("finite_calculate",),max_tool_calls=4)
    selection=MemorySelectionInput(confirmed=True,entries=[{"memory_id":mid,"version":3,"revision":3,"body_sha256":now["body_sha256"]}])
    await ledger.create_activity(spec,memory_selection=selection)
    selected=await ledger.read_memory_selection(aid,include_bodies=True);assert selected["eligible"] and selected["entries"][0]["body"]["text"]==later.body["text"]
    await ledger.create_activity(spec,memory_selection=selection)
    facts=await ledger.read_activity_facts(aid);assert facts.memory_selection["eligible"]
    impact=await ledger.preview_memory_change(mid,3,"revoke")
    revoke=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=3,action="revoke",
      body={"impact_token":impact["impact_token"],"confirm_revoke":True,"purge_memory_content":True})
    deleted=await service.submit_command(revoke)
    assert deleted["purge_state_now"]=="done",deleted
    invalid=await ledger.read_memory_selection(aid,include_bodies=True);assert not invalid["eligible"] and invalid["entries"][0]["body"] is None
    tombstone=await ledger.read_memory_snapshot(mid);assert tombstone["body"] is None and tombstone["state"]=="revoked"
    with psycopg.connect(app_dsn) as connection:
        rows=connection.execute("SELECT (SELECT count(*) FROM learning_memory_bodies WHERE memory_id=%s),(SELECT count(*) FROM learning_memory_revisions WHERE memory_id=%s)",(mid,mid)).fetchone()
        assert rows==(0,3),rows
    return {"status":"PASS","executed":True,"memory_id":mid,"activity_id":aid,"source_id":source["id"],
            "versions_retained":3,"bodies_after_cleanup":0,"source_hash":original.sha256,"app_capabilities":cap,
            "properties":["V01","V02","V03","V06","V10","V12","V18"]}


def run(forward_purge=False):
    control=Control();control.reserve("entry",{"name":"memory-pg-smoke"})
    docker=OwnedDocker(control);resource=control.load()["resources"][0]
    start=time.monotonic();report={"status":"FAIL","executed":True}
    try:
        assert control.load()["counts"]["listener_start"]==0 and control.load()["counts"]["sup"]==0
        docker.start(resource)
        admin=docker.admin_dsn(resource);password=secrets.token_urlsafe(32);SECRET_VALUES.add(password)
        with psycopg.connect(admin,autocommit=True,connect_timeout=2) as connection:
            if forward_purge:
                import hashlib
                before=connection.execute("SELECT pg_get_functiondef('public.purge_learning_memory(uuid,text,uuid,text)'::regprocedure)").fetchone()[0]
                (EVIDENCE/'forward-purge-before.sql').write_bytes(before.encode())
                migration=(ROOT/'backend/migrations/010_learning_memory.sql').read_text(encoding='utf-8')
                begin=migration.index('CREATE FUNCTION public.purge_learning_memory(')
                end=migration.index('$f$;',begin)+4
                statement=migration[begin:end].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)
                connection.execute(statement,prepare=False)
                after=connection.execute("SELECT pg_get_functiondef('public.purge_learning_memory(uuid,text,uuid,text)'::regprocedure)").fetchone()[0]
                (EVIDENCE/'forward-purge-after.sql').write_bytes(after.encode())
                report['forward_function']={'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'after_sha256':hashlib.sha256(after.encode()).hexdigest()}
            connection.execute(sql.SQL("ALTER ROLE retrolume_task103_app PASSWORD {}").format(sql.Literal(password)))
        app_dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
        from app.runtime import psycopg_compatible_loop_factory
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            report=runner.run(scenario(app_dsn))
    except BaseException as exc:
        report.update(error_type=type(exc).__name__,message=redact(str(exc)))
        traceback=__import__("traceback").format_exc();(EVIDENCE/"memory-pg-smoke-error.txt").write_bytes(redact(traceback).encode())
    finally:
        control.charge("real",time.monotonic()-start,{"name":"memory-pg-smoke"})
        clean=time.monotonic()
        try:report["cleanup"]=docker.stop(resource)
        except BaseException as exc:report["cleanup_unconfirmed"]=type(exc).__name__;report["status"]="FAIL"
        control.charge("cleanup",time.monotonic()-clean,{"name":"memory-pg-smoke"})
        atomic_json(EVIDENCE/"memory-pg-smoke-result.json",report)
    print(json.dumps(report,ensure_ascii=False))
    return 0 if report["status"]=="PASS" else 1

if __name__=="__main__":sys.exit(run(forward_purge='--forward-purge' in sys.argv))
