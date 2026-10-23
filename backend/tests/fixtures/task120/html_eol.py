"""User-approved exact EOL-only correction in the original TESTONLY flow DB."""
import hashlib,json
from . import resources as r,setup
from .api_runtime import run,financials

def apply():
    folder=r.EVIDENCE/'continuation-01'
    permission=json.loads((folder/'html-eol-user-permission.json').read_text(encoding='utf-8'))
    raw=(folder/'proposed-html-eol-repair.sql').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=permission['patch_sha256']:raise RuntimeError('reviewed_DDL_patch_changed')
    before_shape=json.loads((r.EVIDENCE/'root-12-html-raw-shape.json').read_text(encoding='utf-8'))
    names={x['function'] for x in json.loads((folder/'proposed-html-eol-repair.json').read_text(encoding='utf-8'))['functions']}
    before_financials=financials('flow')
    setup.environment('flow',include_admin=False)
    from .transport import install
    install()
    from app.main import create_app
    app=create_app();ledger=app.state.activities_ledger
    import psycopg
    from psycopg.rows import dict_row
    from app.capabilities.q_protocol import digest
    async def go():
        async with await psycopg.AsyncConnection.connect(setup.dsn('flow',True),row_factory=dict_row) as db:
            async with db.transaction():
                await db.execute("SET LOCAL statement_timeout='5s'")
                if await ledger.html_schema_shape(db)!=before_shape:raise RuntimeError('DDL_preimage_changed')
                # Same reviewed bytes; transaction ownership remains here so a
                # failed strict fingerprint rolls back all nine replacements.
                text=raw.decode('utf-8')
                lines=text.splitlines(keepends=True)
                if not lines[0].startswith('-- REVIEW ONLY') or lines[1]!='BEGIN;\n' or lines[-1]!='COMMIT;\n':raise RuntimeError('DDL_closed_transaction')
                await db.execute(''.join(lines[2:-1]),prepare=False)
                await ledger._html_assert_schema(db)
                after=await ledger.html_schema_shape(db)
                for old,new in zip(before_shape['functions'],after['functions']):
                    expected=dict(old,prosrc=old['prosrc'].replace('\r\n','\n')) if old['proname'] in names else old
                    if expected!=new:raise RuntimeError('DDL_non_EOL_function_change')
                if any(before_shape[k]!=after[k] for k in before_shape if k!='functions'):raise RuntimeError('DDL_non_function_change')
            proof={'actual_admin_backend_pid':(await (await db.execute('SELECT pg_backend_pid() AS pid')).fetchone())['pid'],'preimage_sha256':digest(before_shape),'postimage_sha256':digest(after)}
        # Ordinary application principal checks the committed catalog too.
        await ledger._transaction(ledger._html_assert_schema)
        return proof
    proof=run(go())
    if financials('flow')!=before_financials:raise RuntimeError('DDL_financial_rows_changed')
    r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-html-eol-applied.json",{'status':'PASS','permission_file':'continuation-01/html-eol-user-permission.json','patch_sha256':permission['patch_sha256'],'nine_exact_functions':True,'owner_ACL_and_strict_fingerprint_verified':True,'normal_app_role_verified':True,'financial_rows_unchanged':True,'preview_creates':0,'preview_starts':0,**proof})
