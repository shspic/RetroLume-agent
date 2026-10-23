"""Finite readonly original-PG diagnostics; no schema learning or repair."""
import json
from . import resources as r,setup
from .api_runtime import run

def diagnose():
    setup.environment('flow',include_admin=False)
    from .transport import install
    install()
    from app.main import create_app
    from app.capabilities.q_protocol import digest,canonical,ROSTER
    from app.data_exit.schema_checks import legacy_business_shape,html_qualification_profile
    from app.data_exit.q_store import authority_for
    import psycopg
    from psycopg.rows import dict_row
    app=create_app();ledger=app.state.activities_ledger;authority=authority_for(ledger)
    result={'readonly':True,'schema_modified':False}
    async def go():
        async with await psycopg.AsyncConnection.connect(setup.dsn('flow'),row_factory=dict_row) as db:
            await db.execute('BEGIN READ ONLY')
            await db.execute("SET LOCAL statement_timeout='4s'")
            result['backend_pid']=(await (await db.execute('SELECT pg_backend_pid() AS pid')).fetchone())['pid']
            shape=await ledger.html_schema_shape(db)
            r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-html-raw-shape.json",shape)
            normalized=await html_qualification_profile(db,legacy_business_shape(shape))
            r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-html-normalized-shape.json",normalized)
            expected=json.loads((r.ROOT/'backend/app/preview/schema-fingerprint.json').read_text(encoding='utf-8'))['data_exit_013_sha256']
            result['html_shape']={'expected':expected,'observed':digest(normalized),'matches':digest(normalized)==expected}
            baseline=json.loads((r.ROOT/'DocuN/evidence/TASK-114/implementation/control/html-shape-normalized-1088472437000000.json').read_text(encoding='utf-8-sig'))
            differences=[]
            for key in set(baseline)|set(normalized):
                if baseline.get(key)==normalized.get(key):continue
                old=baseline.get(key,[]);new=normalized.get(key,[])
                for index in range(max(len(old),len(new))):
                    left=old[index] if index<len(old) else None;right=new[index] if index<len(new) else None
                    if left!=right:differences.append({'section':key,'index':index,'before':left,'after':right})
            r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-html-shape-difference.json",{'baseline_sha256':digest(baseline),'expected_sha256':expected,'differences':differences})
            from app.interview.contracts import InterviewHybridContext
            schema=InterviewHybridContext.model_json_schema()
            fields=set()
            def collect(value):
                if isinstance(value,dict):
                    fields.update(value.get('properties',{}))
                    for child in value.values():collect(child)
                elif isinstance(value,list):
                    for child in value:collect(child)
            collect(schema)
            result['interview_schema_fields_missing_from_template_atoms']=sorted(fields-set(authority.bundle['template_atoms']))
            cursor=await db.execute('SELECT revision,goal_version,goal_record_id::text,pending_business_key::text FROM teaching_heads WHERE activity_id=%s',(ROSTER[0],))
            result['original_a1_head']=await cursor.fetchone()
            cursor=await db.execute("SELECT business_key::text,action,status,expected_revision,goal_version,slot_sha256,launch_claimed_at IS NOT NULL AS claimed,abandoned_at IS NOT NULL AS abandoned FROM teaching_commands WHERE activity_id=%s ORDER BY created_at",(ROSTER[0],))
            result['original_a1_commands']=await cursor.fetchall()
    run(go())
    r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-readonly-diagnosis.json",result)
