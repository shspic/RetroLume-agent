"""本卡唯一专库、镜像和服务资源，凭据只在内存和限定子进程环境。"""
from __future__ import annotations
import asyncio
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import ROOT,EVIDENCE,PERMIT,reserve,run,atomic,event,state

DOCKER=r"C:\Users\28432\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe"
PG="retrolume-task-111-g11-v2-pg1";VOLUME=PG+"-data";PORT=55451
PG_IMAGE="pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
ADMIN="retrolume_task111_admin";APP="retrolume_task111_app";DENIED="retrolume_task111_denied"
DATABASES=("retrolume_task111_main","retrolume_task111_upgrade","retrolume_task111_fault")


def shell_env():
    names=("SystemRoot","WINDIR","PATH","TEMP","TMP","LOCALAPPDATA","USERPROFILE","PROGRAMFILES","PROGRAMFILES(X86)")
    return {key:os.environ[key] for key in names if key in os.environ}


def dsn(user,password,database):
    return psycopg.conninfo.make_conninfo(host="127.0.0.1",port=str(PORT),dbname=database,user=user,password=password,connect_timeout="3")


def pg_start(folder):
    password=secrets.token_urlsafe(32);app_password=secrets.token_urlsafe(32);denied_password=secrets.token_urlsafe(32)
    env=shell_env();env.update(RETROLUME_PG_NAME=PG,RETROLUME_PG_VOLUME=VOLUME,RETROLUME_PG_PORT=str(PORT),
     RETROLUME_PG_USER=ADMIN,RETROLUME_PG_PASSWORD=password,RETROLUME_PG_DATABASE=DATABASES[0])
    env.update(RETROLUME_RENDERER_TAG="retrolume-task-111-g11-renderer:v2-01",RETROLUME_RENDERER_CONTEXT=str(ROOT/"deploy/preview"),
      RETROLUME_RENDERER_BASE_OCI="oci-layout://"+(ROOT/"deploy/preview/task109-c01-cache/oci").as_posix()+"@sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac")
    # 第一个真实预检已经由外层root计数；只查本卡名字和安全白名单。
    value=run([DOCKER,"info","--format",'{"kernel":{{json .KernelVersion}},"os":{{json .OSType}},"version":{{json .ServerVersion}}}'],folder,maximum=10,name="platform")
    platform=json.loads(value.stdout);atomic(folder/"platform.json",platform)
    if platform["kernel"]!="6.6.114.1-microsoft-standard-WSL2" or platform["os"]!="linux":raise RuntimeError("TASK111 kernel/platform mechanism unconfirmed")
    existing=run([DOCKER,"ps","-a","--no-trunc","--filter","name=^/"+PG+"$","--format","{{.ID}}"],folder,maximum=10,name="pg-conflict")
    if existing.stdout.strip():raise RuntimeError("TASK111 fresh PG name collision")
    volume=run([DOCKER,"volume","ls","--filter","name=^"+VOLUME+"$","--format","{{.Name}}"],folder,maximum=10,name="volume-conflict")
    if volume.stdout.strip():raise RuntimeError("TASK111 fresh volume collision")
    reserve("PG_containers",{"name":PG});reserve("PG_volumes",{"name":VOLUME});reserve("PG_container_starts",{"name":PG})
    run([DOCKER,"compose","-f",str(ROOT/"deploy/compose.local.yml"),"-p","retrolume-task-111-g11-v2","up","-d","--no-build","--pull","never","pg"],
        folder,cwd=ROOT,env=env,maximum=120,name="compose-pg")
    admin=dsn(ADMIN,password,DATABASES[0]);until=time.monotonic()+30
    while True:
        try:
            with psycopg.connect(admin) as conn:conn.execute("SELECT 1")
            break
        except psycopg.Error:
            if time.monotonic()>until:raise RuntimeError("TASK111 synthetic PG not ready") from None
            time.sleep(.2)
    with psycopg.connect(admin,autocommit=True) as conn:
        for role,secret in ((APP,app_password),(DENIED,denied_password)):
            conn.execute(sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}").format(sql.Identifier(role),sql.Literal(secret)))
    return {"admin":admin,"app":dsn(APP,app_password,DATABASES[0]),"denied":dsn(DENIED,denied_password,DATABASES[0]),
            "passwords":(password,app_password,denied_password),"platform":platform,"pg_env":env}


def pg_resume(folder):
    """同卡自有专库恢复，仅重置这三个已授权角色的内存口令，不重建数据。"""
    previous=json.loads((EVIDENCE/"real-01/pg-final.stdout.bin").read_text(encoding="utf-8"))
    current=run([DOCKER,"inspect","--format",'{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"running":{{json .State.Running}},"pid":{{json .State.Pid}}}',PG],folder,maximum=10,name="pg-resume-identity")
    actual=json.loads(current.stdout)
    if actual["id"]!=previous["id"] or actual["image"]!=previous["image"] or actual["name"]!="/"+PG:raise RuntimeError("TASK111 PG ownership drift")
    if not actual["running"]:
        reserve("PG_container_starts",{"cid":actual["id"]});run([DOCKER,"start",actual["id"]],folder,maximum=15,name="pg-resume-start")
    passwords=tuple(secrets.token_urlsafe(32) for _ in range(3))
    statements="\n".join(sql.SQL("ALTER ROLE {} PASSWORD {};").format(sql.Identifier(role),sql.Literal(password)).as_string() for role,password in zip((ADMIN,APP,DENIED),passwords))
    result=subprocess.run([DOCKER,"exec","-i",actual["id"],"psql","-U",ADMIN,"-d",DATABASES[0],"-v","ON_ERROR_STOP=1"],
                         input=statements.encode("utf-8"),capture_output=True,timeout=10,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
    # 口令只走stdin和内存；即使错误也不保存未脱敏psql原文。
    stdout=result.stdout.decode("utf-8","replace");stderr=result.stderr.decode("utf-8","replace")
    for password in passwords:stdout=stdout.replace(password,"[redacted]");stderr=stderr.replace(password,"[redacted]")
    atomic(folder/"credential-recovery.json",{"cid":actual["id"],"roles":[ADMIN,APP,DENIED],"code":result.returncode,"stdout":stdout,"stderr":stderr,"stdin_saved":False})
    if result.returncode:raise RuntimeError("TASK111 own-role password recovery failed")
    platform=json.loads((EVIDENCE/"real-01/platform.json").read_text(encoding="utf-8"))
    return {"admin":dsn(ADMIN,passwords[0],DATABASES[0]),"app":dsn(APP,passwords[1],DATABASES[0]),"denied":dsn(DENIED,passwords[2],DATABASES[0]),"passwords":passwords,"platform":platform}


def migrate_baseline(runtime,folder):
    with psycopg.connect(runtime["admin"],autocommit=True) as conn:
        for path in sorted((ROOT/"backend/migrations").glob("0[01][0-9]_*.sql")):
            if int(path.name[:3])>11:continue
            conn.execute(path.read_text(encoding="utf-8"));event("migration",{"file":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})


def build_renderer(folder):
    spec=importlib.util.spec_from_file_location("task111_build_renderer",ROOT/"deploy/preview/build_renderer.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    number=reserve("image_builds",{"purpose":"production-v2"});tag="retrolume-task-111-g11-renderer:v2-"+str(number).zfill(2)
    context=ROOT/"deploy/preview/build-contexts"/("v2-"+str(number).zfill(2))
    prepared=module.prepare(context,base_oci=ROOT/"deploy/preview/task109-c01-cache/oci");atomic(folder/"build-input.json",prepared)
    run([DOCKER,*module.build_args(context,prepared["base_oci"],tag,folder/"build-metadata.json")],folder,cwd=ROOT,maximum=600,name="renderer-build")
    result=run([DOCKER,"image","inspect","--format",'{"id":{{json .Id}},"descriptor":{{json .Descriptor}},"digests":{{json .RepoDigests}},"os":{{json .Os}},"architecture":{{json .Architecture}}}',tag],folder,maximum=10,name="renderer-image")
    image=json.loads(result.stdout);atomic(folder/"renderer-image.json",image)
    # manifest/config区分依实际Docker投影，不猜build-metadata字段。
    prepared.update({"image":image,"tag":tag});atomic(folder/"production-build.json",prepared)
    shutil.copy2(context/"load-manifest.json",ROOT/"deploy/preview/load-manifest.json")
    return prepared


async def install_html(runtime,folder):
    from app.preview.compiler import runtime_identity,runtime_html
    from app.preview.description import digest
    from app.activities.repository import PostgresAdmissionLedger
    renderer=runtime_identity()["renderer_sha256"];html_hash=hashlib.sha256(runtime_html().encode()).hexdigest()
    path=ROOT/"backend/migrations/012_html_explanations.sql";body=path.read_text(encoding="utf-8")
    body=body.replace("__RENDERER_SHA256__",renderer).replace("__HTML_SHA256__",html_hash);path.write_text(body,encoding="utf-8")
    with psycopg.connect(runtime["admin"],autocommit=True) as conn:
        conn.execute(body)
        # 旧域只给原服务真正需要的读/写，不给DELETE/TRUNCATE或新表直接DML。
        old_tables=[r[0] for r in conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename NOT LIKE 'html_%' AND tablename NOT LIKE 'interview_%' AND tablename NOT LIKE 'learning_memory_%' AND tablename NOT IN ('learning_memories','activity_memory_bindings','activity_memory_choices')").fetchall()]
        for table in old_tables:conn.execute(sql.SQL("GRANT SELECT,INSERT,UPDATE ON public.{} TO {}").format(sql.Identifier(table),sql.Identifier(APP)))
        conn.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(APP)))
        for role in ("retrolume_memory_app","retrolume_interview_app","retrolume_html_app"):
            conn.execute(sql.SQL("GRANT {} TO {}").format(sql.Identifier(role),sql.Identifier(APP)))
    ledger=PostgresAdmissionLedger(runtime["admin"])
    shape=await ledger._transaction(ledger.html_schema_shape)
    atomic(ROOT/"backend/app/preview/schema-fingerprint.json",{"schema":"retrolume.html.schema.v2","sha256":digest(shape),"migration_sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    atomic(folder/"schema-shape.json",shape)
    atomic(folder/"schema-identity.json",{"sha256":digest(shape),"renderer_sha256":renderer,"html_sha256":html_hash})


def restore_fixture_acl(runtime,folder):
    """撤销本夹具误加的直属授权，保留原受保护域的原ACL和角色授权。"""
    with psycopg.connect(runtime["admin"],autocommit=True) as conn:
        protected=[r[0] for r in conn.execute("""SELECT tablename FROM pg_tables WHERE schemaname='public' AND
            (tablename LIKE 'interview_%' OR tablename LIKE 'learning_memory_%' OR tablename IN ('learning_memories','activity_memory_bindings','activity_memory_choices'))""").fetchall()]
        for table in protected:conn.execute(sql.SQL("REVOKE ALL ON public.{} FROM {}").format(sql.Identifier(table),sql.Identifier(APP)))
    atomic(folder/"fixture-acl-restoration.json",{"role":APP,"tables":protected,"reason":"only undo TASK111 fixture direct grants; original owner/app roles and privileges retained"})


def stop_pg(folder):
    try:run([DOCKER,"stop","--time","5",PG],folder,maximum=15,name="pg-stop")
    finally:
        run([DOCKER,"inspect","--format",'{"id":{{json .Id}},"image":{{json .Image}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"name":{{json .Name}}}',PG],folder,maximum=10,name="pg-final")
