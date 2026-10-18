"""受控根入口：新合成PG基线/010及普通app权限，不启动应用。"""
from __future__ import annotations
import asyncio
import json
import os
from pathlib import Path
import sys
import time
import traceback
import psycopg
from psycopg import sql
from .control import Control,EVIDENCE,ROOT,atomic_json,redact
from .resources import OwnedDocker


def run(slot=1):
    control=Control();control.reserve("entry",{"name":"bootstrap-pg"+str(slot)})
    start=time.monotonic();resource=None;report={"executed":True,"status":"FAIL","slot":slot}
    docker=OwnedDocker(control)
    try:
        resource=docker.create(slot);docker.start(resource)
        dsn=docker.admin_dsn(resource)
        deadline=time.monotonic()+min(30,control.remaining("real",900))
        while True:
            try:conn=psycopg.connect(dsn,autocommit=True,connect_timeout=2);break
            except psycopg.Error:
                if time.monotonic()>=deadline:raise
                time.sleep(.1)
        with conn:
            conn.execute("SET statement_timeout='15s'")
            row=conn.execute("SELECT version(),current_setting('server_encoding'),encode(sha256(convert_to('abc','UTF8')),'hex')").fetchone()
            report.update(version=row[0],encoding=row[1],core_sha256=row[2])
            assert row[1]=="UTF8" and row[2]=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
            for path in sorted((ROOT/"backend/migrations").glob("*.sql")):
                report["current_migration"]=path.name
                conn.execute(path.read_text(encoding="utf-8-sig"),prepare=False)
            report["tables"]=conn.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename=ANY(%s)",
              (["learning_memories","learning_memory_revisions","learning_memory_bodies","learning_memory_dependencies",
                "learning_memory_commands","activity_memory_bindings","activity_memory_choices"],)).fetchone()[0]
            assert report["tables"]==7
            # 新普通登录仅映射本包app和原活动所需列；不给新正文DELETE/owner。
            conn.execute("CREATE ROLE retrolume_task103_app LOGIN")
            conn.execute("GRANT retrolume_memory_app TO retrolume_task103_app")
            for table in ("material_sources","material_versions","activities","activity_scope_sources","activity_allowed_models",
                          "activity_operations","activity_operation_results","teaching_heads","teaching_commands","teaching_records",
                          "pdf_review_candidates","pdf_extracted_pages","pdf_review_pages","pdf_user_supplements"):
                conn.execute(sql.SQL("GRANT SELECT,INSERT,UPDATE ON public.{} TO retrolume_task103_app").format(sql.Identifier(table)))
            conn.execute("GRANT DELETE ON public.activity_scope_sources TO retrolume_task103_app")
            conn.execute("CREATE ROLE retrolume_task103_denied LOGIN")
            conn.execute("SET ROLE retrolume_task103_app")
            app=conn.execute("""SELECT current_user,pg_has_role(current_user,'retrolume_memory_owner','MEMBER'),
              has_table_privilege(current_user,'public.learning_memory_bodies','DELETE'),
              has_function_privilege(current_user,'public.purge_learning_memory(uuid,text,uuid,text)','EXECUTE')""").fetchone()
            report["app_role"]={"name":app[0],"owner_member":app[1],"body_delete":app[2],"purge_execute":app[3]}
            assert app[0]=="retrolume_task103_app" and app[1] is False and app[2] is False and app[3] is True
            conn.execute("RESET ROLE")
        report.update(status="PASS",executed=True)
    except BaseException as exc:
        report.update(error_type=type(exc).__name__,message=redact(getattr(getattr(exc,"diag",None),"message_primary",None) or str(exc)),
                      sqlstate=getattr(exc,"sqlstate",None))
    finally:
        control.charge("real",time.monotonic()-start,{"name":"bootstrap-pg"+str(slot)})
        clean_start=time.monotonic()
        if resource:
            try:report["cleanup"]=docker.stop(resource)
            except BaseException as exc:report["cleanup_unconfirmed"]=type(exc).__name__;report["status"]="FAIL"
        control.charge("cleanup",time.monotonic()-clean_start,{"name":"bootstrap-pg"+str(slot)})
        atomic_json(EVIDENCE/"bootstrap-pg"+str(slot)+"-result.json",report)
    print(json.dumps(report,ensure_ascii=False))
    return 0 if report["status"]=="PASS" else 1


if __name__=="__main__":
    sys.exit(run(int(sys.argv[1]) if len(sys.argv)>1 else 1))

