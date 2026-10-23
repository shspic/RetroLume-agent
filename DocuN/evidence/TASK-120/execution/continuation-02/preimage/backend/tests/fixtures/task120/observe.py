"""Own immutable instances/deadlines and retained financials, actual PG only."""
import json
from datetime import datetime,timezone
from . import setup,resources as r
from .api_runtime import run,financials

def observe():
    import psycopg
    from psycopg.rows import dict_row
    from .budget import run_reopen
    run_reopen()
    values=[]
    for slot in ('flow','budget-01'):
        setup.environment(slot,include_admin=False)
        from app.main import create_app
        app=create_app()
        if not app.state.q_readiness['available']:raise RuntimeError('actual_q_root_unavailable')
        from app.data_exit.q_store import authority_for
        authority=authority_for(app.state.activities_ledger)
        with psycopg.connect(setup.dsn(slot),row_factory=dict_row) as connection:
            identity=connection.execute('SELECT current_database() AS database,public.data_state() AS control,(SELECT oid FROM pg_database WHERE datname=current_database()) AS database_oid').fetchone()
            rows=connection.execute('SELECT id::text,status,deadline_at,scope_revision,outbound_grant_sha256,execution_generation,running_reserved_seconds,running_settled_seconds FROM activities ORDER BY id').fetchall()
        if len(rows)!=3 or any(x['deadline_at']<=datetime.now(timezone.utc) or x['outbound_grant_sha256']!=authority.grant.sha256 for x in rows):raise RuntimeError('activity_expired_or_rebound')
        values.append({'slot':slot,'identity':identity,'activities':rows,'financials':financials(slot),'real_outbound_authorized':False})
    from app.data_exit.codec import plain
    r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-instance-observation.json",plain({'slots':values,'same_CID_reused':True,'old_reserves_retained':True}))
