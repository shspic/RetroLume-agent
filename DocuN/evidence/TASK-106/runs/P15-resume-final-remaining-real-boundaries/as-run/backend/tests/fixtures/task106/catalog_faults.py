"""Fresh/old nonempty upgrade, ordinary privilege veto and restorable bad schemas."""
import asyncio,hashlib,json,sys,re
from uuid import uuid4
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import ROOT,batch,atomic_json
from .resources import start,stop,runtime,APP,DENIED
from .core import Harness
from .samples import T_NAME
from .directed import start_goal
from app.interview.contracts import InterviewRefusal
from app.learning.service import LearningService
from app.learning.teaching_contracts import TeachingCommandInput
from app.learning.teaching_service import TeachingService
from app.service_config import LayerState
from dataclasses import replace


def migrate(admin,last):
    with psycopg.connect(admin,autocommit=True) as conn:
        for p in sorted((ROOT/'backend/migrations').glob('*.sql')):
            if int(p.name[:3])<=last:conn.execute(p.read_text(encoding='utf-8-sig'),prepare=False)


def protected_rows(admin):
    tables=('material_sources','material_versions','activities','activity_scope_sources','activity_allowed_models','activity_operations','activity_operation_results','teaching_heads','teaching_commands','teaching_records')
    with psycopg.connect(admin,row_factory=dict_row) as conn:
        result={}
        for name in tables:
            rows=conn.execute(sql.SQL('SELECT row_to_json(t)::text AS value FROM public.{} t ORDER BY row_to_json(t)::text').format(sql.Identifier(name))).fetchall()
            # Contains only explicit synthetic material/facts; excludes role/password fields.
            result[name]=[r['value'] for r in rows]
        return result


async def old_upgrade(h):
    h.material(T_NAME);aid=await h.activity([T_NAME])
    learning=LearningService(h.ledger,h.materials,h.originals)
    config=replace(h.config,learning_layer=LayerState(True),learning_output_tokens=256,teaching_layer=LayerState(True),teaching_output_tokens=512)
    # Actual existing learning profile through native worker, before011.
    import app.learning.service as old_learning_module
    original_config=old_learning_module.SessionConfig
    old_learning_module.SessionConfig=lambda:h.session
    try:learned=await learning.execute(aid,str(uuid4()),'余额算法串行结果110',config,run_tag='task106-legacy-learning')
    finally:old_learning_module.SessionConfig=original_config
    atomic_json(h.out/'legacy-learning-return.json',dict(value=str(learned)))
    with psycopg.connect(h.dsn,row_factory=dict_row) as conn:
        result=conn.execute("SELECT r.payload::jsonb AS payload FROM activity_operation_results r WHERE r.activity_id=%s",(aid,)).fetchall()
    assert result and result[0]['payload']['value']['profile']=='learning.v1',result
    teach=await h.activity([T_NAME]);service=TeachingService(h.ledger,h.materials,h.originals,session_config=h.session)
    goal=TeachingCommandInput.model_validate(dict(business_key=str(uuid4()),action='goal',expected_revision=0,expected_goal_version=0,expected_scope_revision=1,body={'goal':'余额算法串行与覆盖'}))
    g=await service.submit_command(teach,goal,config,run_tag='task106-old-goal')
    snapshot=await h.ledger.read_teaching_workspace(teach)
    head=snapshot['head']
    plan=TeachingCommandInput.model_validate(dict(business_key=str(uuid4()),action='plan',expected_revision=head['revision'],expected_goal_version=head['goal_version'],expected_scope_revision=1,body={'confirmed':True}))
    receipt=await service.submit_command(teach,plan,config,run_tag='task106-old-plan')
    assert receipt.status=='committed',receipt
    atomic_json(h.out/'legacy-teaching-return.json',dict(status=receipt.status,activity_id=teach))
    before=protected_rows(h.admin)
    with psycopg.connect(h.admin,autocommit=True) as conn:conn.execute((ROOT/'backend/migrations/011_text_interview.sql').read_text(encoding='utf-8'),prepare=False)
    after=protected_rows(h.admin);assert before==after,{'changed':[k for k in before if before[k]!=after[k]]}
    atomic_json(h.out/'nonempty-upgrade-old-rows.json',dict(before=before,after=after,equal=True))
    app,denied=runtime(h.admin);h.dsn=app;h.ledger._dsn=app;h.materials.dsn=app
    shape=await h.ledger._transaction(h.ledger._interview_schema_info);assert shape=='ready',shape
    atomic_json(h.out/'upgrade-s1.json',dict(state=shape,old_learning=aid,old_teaching=teach))


async def fault_tests(h,denied):
    h.material(T_NAME);aid=await start_goal(h,[T_NAME],'余额算法权限验证',{T_NAME:'reference'})
    # Zero-cost local records provide the actual immutable target, no need for a model just to test ACL.
    state=h.snapshot(aid);rid=state['records'][0]['record_id'];v=await h.ledger.read_interview_workspace(aid)
    refusals=[]
    for name,statement,params in (
        ('record-update','UPDATE interview_records SET body_sha256=%s WHERE activity_id=%s AND record_id=%s',('0'*64,aid,rid)),
        ('record-delete','DELETE FROM interview_records WHERE activity_id=%s',(aid,)),
        ('truncate','TRUNCATE interview_records',()),('owner','SET ROLE retrolume_interview_owner',()),
        ('old007-update','UPDATE activity_operation_results SET payload_sha256=%s',('0'*64,)),
        ('old009-update','UPDATE teaching_records SET body_sha256=%s',('0'*64,)),
    ):
        with psycopg.connect(h.dsn) as conn:
            try:conn.execute(statement,params)
            except psycopg.Error as exc:refusals.append(dict(name=name,sqlstate=exc.sqlstate,message=exc.diag.message_primary))
            else:raise AssertionError('ordinary forbidden operation succeeded: '+name)
    atomic_json(h.out/'ordinary-acl-refusals.json',refusals)
    with psycopg.connect(denied) as conn:
        try:conn.execute('SELECT * FROM interview_heads')
        except psycopg.Error as exc:assert exc.sqlstate=='42501',exc.sqlstate
        else:raise AssertionError('denied role read new tables')
    # Corrupt only an011 function, restore exact approved definition, no DROP/DELETE/old trigger edits.
    text=(ROOT/'backend/migrations/011_text_interview.sql').read_text(encoding='utf-8')
    definition=re.search(r'CREATE FUNCTION public\.interview_result_eligible\(.*?\$body\$;',text,re.S).group(0)
    with psycopg.connect(h.admin,autocommit=True) as conn:
        conn.execute("CREATE OR REPLACE FUNCTION public.interview_result_eligible(aid uuid,op text) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public AS $$ SELECT true $$")
    try:
        shape=await h.ledger._transaction(h.ledger._interview_schema_info);assert shape=='damaged',shape
        try:await h.ledger.read_interview_workspace(aid)
        except InterviewRefusal as exc:assert exc.code=='interview_schema_not_ready',exc.code
        else:raise AssertionError('tampered function adopted')
        atomic_json(h.out/'tampered-definition-fail-closed.json',dict(S1=shape,body_returned=False))
    finally:
        with psycopg.connect(h.admin,autocommit=True) as conn:conn.execute(definition.replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1))
    assert await h.ledger._transaction(h.ledger._interview_schema_info)=='ready'
    # Missing head table name is a partial-schema failure, not a legacy TRUE fallback.
    with psycopg.connect(h.admin,autocommit=True) as conn:conn.execute('ALTER TABLE interview_heads RENAME TO task106_saved_interview_heads')
    try:
        assert await h.ledger._transaction(h.ledger._interview_schema_info)=='damaged'
        try:await h.ledger.read_interview_workspace(aid)
        except InterviewRefusal as exc:assert exc.code=='interview_schema_not_ready'
        else:raise AssertionError('partial schema adopted')
        atomic_json(h.out/'missing-head-fail-closed.json',dict(table_renamed=True,body_returned=False,drop=False))
    finally:
        with psycopg.connect(h.admin,autocommit=True) as conn:conn.execute('ALTER TABLE task106_saved_interview_heads RENAME TO interview_heads')
    assert await h.ledger._transaction(h.ledger._interview_schema_info)=='ready'
    atomic_json(h.out/'fault-restored-state.json',h.snapshot(aid))


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with batch('P08-nonempty-upgrade-ordinary-acl-fault-restore') as out:
        try:
            admin=start(2);migrate(admin,10);app,denied=runtime(admin);h=Harness(admin,app,out)
            asyncio.run(old_upgrade(h))
        finally:stop(2)
        try:
            admin=start(3);migrate(admin,11);app,denied=runtime(admin);h=Harness(admin,app,out)
            asyncio.run(fault_tests(h,denied))
        finally:stop(3)
        print(json.dumps(dict(nonempty_upgrade=True,old_profiles=True,ordinary_acl=True,S1_definition_and_missing_fail_closed=True,faults_restored=True)))


if __name__=='__main__':main()
