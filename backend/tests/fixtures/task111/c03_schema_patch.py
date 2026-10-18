"""仅应用本次确定预算缺陷的函数补丁，保留已应用原012和全部合成行。"""
import asyncio,hashlib,re,json
import psycopg
from .control import ROOT,CONTINUE_ROOT,atomic
from app.runtime import psycopg_compatible_loop_factory

def apply(resource,out):
    path=ROOT/"backend/migrations/012_html_explanations.sql";text=path.read_text(encoding="utf-8")
    body=re.search(r'CREATE FUNCTION public\.html_reserve_preview\([\s\S]*?\$body\$;',text).group(0).replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)
    with psycopg.connect(resource["admin"]) as conn:
        before=conn.execute("SELECT pg_get_userbyid(proowner),proacl::text FROM pg_proc WHERE oid='public.html_reserve_preview(uuid,uuid,uuid,uuid,text,uuid,text,text,uuid,text,text,integer,bigint,timestamptz,text)'::regprocedure").fetchone()
        conn.execute(body)
        after=conn.execute("SELECT pg_get_userbyid(proowner),proacl::text FROM pg_proc WHERE oid='public.html_reserve_preview(uuid,uuid,uuid,uuid,text,uuid,text,text,uuid,text,text,integer,bigint,timestamptz,text)'::regprocedure").fetchone()
        assert before==after and before[0]=='retrolume_html_owner'
    from app.activities.repository import PostgresAdmissionLedger
    from app.preview.description import digest
    ledger=PostgresAdmissionLedger(resource["app"])
    async def shape():return await ledger._transaction(ledger.html_schema_shape)
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:value=runner.run(shape())
    fingerprint={"schema":"retrolume.html.schema.v2","sha256":digest(value),"migration_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    atomic(ROOT/"backend/app/preview/schema-fingerprint.json",fingerprint)
    atomic(out/"schema-function-patch.json",{"status":"APPLIED_ONLY_IDENTIFIED_RESERVE_FUNCTION_PATCH","source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
      "function_patch_sha256":hashlib.sha256(body.encode()).hexdigest(),"before_owner_acl":before,"after_owner_acl":after,"fingerprint":fingerprint,"full012_rerun":False,"old_rows_deleted":False})
