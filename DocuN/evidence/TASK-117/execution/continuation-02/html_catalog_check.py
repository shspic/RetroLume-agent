"""只读核当前根16 source的HTML目录投影，不启资源或执行模型。"""
from batch_runtime import *
import asyncio,copy
import psycopg
from psycopg.rows import dict_row
from app.activities.repository import PostgresAdmissionLedger
from app.runtime import psycopg_compatible_loop_factory
from app.data_exit.schema_checks import legacy_business_shape,normalize_html_qualification
from app.data_exit.contracts import DataError

async def check():
    ledger=PostgresAdmissionLedger(rc.dsn('source'));ledger.data_enabled=True
    async with await psycopg.AsyncConnection.connect(rc.dsn('source'),connect_timeout=3,row_factory=dict_row) as db:
        await db.execute("BEGIN READ ONLY");await db.execute("SET LOCAL statement_timeout='3s'")
        shape=await ledger.html_schema_shape(db)
        c.write(C01/'HTML-actual-catalog.json',shape)
        await ledger._html_assert_schema(db)
        # 非批准写权必须仍失败，不把新授权自动学成基线。
        forged=copy.deepcopy(shape);row=forged['qualification_column_acls'][0]
        row['table_acl']=row['table_acl'][:-1]+',retrolume_interview_owner=w/unknown}'
        cursor=await db.execute("SELECT c.relname,r.rolname AS owner FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname='public' AND c.relname IN ('pdf_review_candidates','pdf_review_pages','pdf_extracted_pages')")
        owners={r['relname']:r['owner'] for r in await cursor.fetchall()}
        normalize_html_qualification(legacy_business_shape(shape),owners)
        try:normalize_html_qualification(legacy_business_shape(forged),owners)
        except DataError:closed=True
        else:raise AssertionError('未知ACL不能通过')
        c.write(C01/'HTML-catalog-real-PG-check.json',{'sample':c.sample(),'normal_app_role':True,'exact_trusted_HTML_fingerprint':True,'unknown_write_grant_rejected':closed,'new_R02_shape_unchanged':True,'HTTP_host':'NOT_RUN for this code; running API holds older module','resources_started':0})
        print('Actual PG HTML fingerprint passed; unknown ACL rejected; no execution resources started')
if __name__=='__main__':
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(check())
