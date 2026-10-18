"""One owned preparation root: migrations, exact catalog and ordinary ACL."""
import asyncio,hashlib,json,sys
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from .control import ROOT,EVIDENCE,batch,atomic_json
from .resources import start,stop,runtime


async def catalog(dsn):
    from app.activities.repository import PostgresAdmissionLedger
    ledger=PostgresAdmissionLedger(dsn,statement_timeout_ms=10000,lock_timeout_ms=5000)
    return await ledger._transaction(ledger._interview_shape)


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with batch('P01-owned-main-migration-catalog') as out:
        try:
            dsn=start(1)
            with psycopg.connect(dsn,autocommit=True,row_factory=dict_row) as conn:
                existing=conn.execute("SELECT to_regclass('public.activities') AS present").fetchone()['present']
                if existing is not None:raise RuntimeError('preparation refuses to reapply existing migrations')
                applied=[]
                for p in sorted((ROOT/'backend/migrations').glob('*.sql')):
                    text=p.read_text(encoding='utf-8-sig');conn.execute(text,prepare=False)
                    applied.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
                atomic_json(out/'applied-migrations.json',applied)
            app,denied=runtime(dsn)
            shape=asyncio.run(catalog(dsn))
            from app.interview.contracts import canonical,sha
            fingerprint=sha(canonical(shape))
            atomic_json(out/'approved-011-catalog.json',dict(fingerprint=fingerprint,shape=shape,
                basis='exact approved011 applied to newly owned cluster; ordinary runtime ready verification in next root; no arbitrary schema adopted'))
            print(json.dumps(dict(prepared=True,fingerprint=fingerprint,tables=len(shape['table_acl']),functions=len(shape['functions']))))
        finally:stop(1)


if __name__=='__main__':main()
