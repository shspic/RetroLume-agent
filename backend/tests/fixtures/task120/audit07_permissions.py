"""F01/F02 real PG17 transactions; one client, exact rollback, no API/worker."""
import json
from pathlib import Path
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from . import resources as r,setup
from .audit07 import HERE,case
from app.data_exit.contracts import DataError
from app.data_exit.codec import plain
from app.data_exit.schema_checks import assert_data_schema_sync
from app.data_exit.schema_profiles import MIGRATION_015,SCOPE_ACL_QUERY
from app.data_exit.q_roles import ROLE_CAPABILITIES,MEMBERSHIPS


def image(c):
    return plain({'control':c.execute('SELECT dataset_id,instance_id,schema_profile,mode FROM public.data_control').fetchall(),
        'constraints':c.execute("SELECT conname,pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conrelid='public.data_control'::regclass ORDER BY conname").fetchall(),
        'scope_ACL':c.execute(SCOPE_ACL_QUERY).fetchall(),
        'objects':c.execute("SELECT c.relname,c.relkind,r.rolname AS owner,c.relacl::text FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname='public' ORDER BY c.relname").fetchall()})


def graph(c):return plain({'roles':c.execute(ROLE_CAPABILITIES).fetchall(),'members':c.execute(MEMBERSHIPS).fetchall()})


def single(c):
    clients=c.execute("SELECT pid,datname,usename,application_name FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid() ORDER BY pid").fetchall()
    assert not clients,clients
    return plain(c.execute('SELECT pg_backend_pid() AS backend_pid,current_database() AS database,(SELECT system_identifier::text FROM pg_control_system()) AS cluster_system_identifier').fetchone())


def permissions():
    risk=json.loads((HERE/'permission-risk-final-before-PG.json').read_text(encoding='utf-8'))
    assert risk['status']=='PASS' and risk['revised015_sha256']==MIGRATION_015
    for slot in ('audit07-r02','audit07-main'):setup.initial_files(slot);setup.migrate(slot)
    migration=(r.ROOT/'backend/migrations/015_activity_scope_delete_permission.sql').read_text(encoding='utf-8')
    for title,missing in [('missing-insert',['INSERT']),('missing-update',['UPDATE']),('select-only',['INSERT','UPDATE'])]:
        def negative(missing=missing):
            with psycopg.connect(setup.dsn('audit07-r02',True),autocommit=True,row_factory=dict_row) as c:
                endpoint=single(c);before=image(c);assert_data_schema_sync(c)
                c.execute('BEGIN');error=None
                try:
                    for privilege in missing:c.execute('REVOKE '+privilege+' ON public.activity_scope_sources FROM retrolume_data_app')
                    observed={p:c.execute('SELECT has_table_privilege(%s,%s,%s) AS ok',('retrolume_data_app','public.activity_scope_sources',p)).fetchone()['ok'] for p in ('SELECT','INSERT','UPDATE')}
                    try:c.execute(migration,prepare=False)
                    except psycopg.Error as exc:error={'sqlstate':exc.sqlstate,'message':exc.diag.message_primary}
                    assert error=={'sqlstate':'P0001','message':'scope_delete_migration_requires_exact_quiescent_r02'},error
                finally:c.execute('ROLLBACK')
                after=image(c);assert after==before
            with psycopg.connect(setup.dsn('audit07-r02',True),autocommit=True,row_factory=dict_row) as verify:
                assert image(verify)==before
            return {'missing':missing,'actual_preconditions':observed,'error':error,'endpoint':endpoint,
                    'before':before,'after':after,'new_connection_equal':True,'DDL_ACL_profile_metadata_unchanged':True}
        case('F01-'+title,negative)
    def positive():
        with psycopg.connect(setup.dsn('audit07-main',True),autocommit=True,row_factory=dict_row) as c:
            endpoint=single(c);before=image(c);assert before['control'][0]['schema_profile']=='data_exit.v1.r02'
            r.write(HERE/('F01-normal-R02-before015-root-'+str(r.state()['active_root'])+'.json'),before)
            c.execute(migration,prepare=False)
            after=image(c);assert after['control'][0]['schema_profile']=='data_exit.v1.r03'
            assert_data_schema_sync(c)
            progress_path=r.PRIVATE/'audit07-main/bootstrap-progress.json';progress=json.loads(progress_path.read_text(encoding='utf-8'))
            progress['migrations'].append({'name':'015_activity_scope_delete_permission.sql','sha256':MIGRATION_015});r.write(progress_path,progress,private=True)
            return {'endpoint':endpoint,'before':before,'after':after,'revised015_sha256':MIGRATION_015,'normal_R02_row_present_before_apply':True,'actual_COMMIT':True}
    case('F01-normal-R03-install',positive)
    actual_login=setup.info('audit07-main')['snapshot_user']
    app=setup.info('audit07-main')['app_user']
    cases=[('direct-inherit-snapshot',[
        'GRANT retrolume_data_app TO retrolume_data_snapshot WITH INHERIT TRUE, SET FALSE'],True,False,'retrolume_data_snapshot'),
      ('indirect-inherit-snapshot',[
        'CREATE ROLE retrolume_task120_audit07_bridge1 NOLOGIN',
        'GRANT retrolume_data_app TO retrolume_task120_audit07_bridge1 WITH INHERIT TRUE, SET FALSE',
        'GRANT retrolume_task120_audit07_bridge1 TO retrolume_data_snapshot WITH INHERIT TRUE, SET FALSE'],True,False,'retrolume_data_snapshot'),
      ('set-only-indirect-snapshot',[
        'CREATE ROLE retrolume_task120_audit07_bridge1 NOLOGIN',
        'CREATE ROLE retrolume_task120_audit07_bridge2 NOLOGIN',
        'GRANT retrolume_data_app TO retrolume_task120_audit07_bridge2 WITH INHERIT FALSE, SET TRUE',
        'GRANT retrolume_task120_audit07_bridge2 TO retrolume_task120_audit07_bridge1 WITH INHERIT FALSE, SET TRUE',
        'GRANT retrolume_task120_audit07_bridge1 TO retrolume_data_snapshot WITH INHERIT FALSE, SET TRUE'],False,True,'retrolume_data_snapshot'),
      ('loader-inherit-app',['GRANT retrolume_data_app TO retrolume_data_restore_loader WITH INHERIT TRUE, SET FALSE'],True,False,'retrolume_data_restore_loader'),
      ('trusted-owner-inherit-app',['GRANT retrolume_data_app TO retrolume_interview_owner WITH INHERIT TRUE, SET FALSE'],True,False,'retrolume_interview_owner'),
      ('application-inherit-controller-owner',['GRANT retrolume_data_owner TO retrolume_data_app WITH INHERIT TRUE, SET FALSE'],True,False,'retrolume_data_app'),
      ('admin-without-inherit-or-set',['GRANT retrolume_data_app TO retrolume_data_snapshot WITH ADMIN TRUE, INHERIT FALSE, SET FALSE'],False,False,'retrolume_data_snapshot'),
      ('legal-harmless-membership',['CREATE ROLE retrolume_task120_audit07_bridge1 NOLOGIN',
        'GRANT retrolume_task120_audit07_bridge1 TO retrolume_data_snapshot WITH INHERIT TRUE, SET FALSE'],False,False,'retrolume_data_snapshot'),
      ('application-inherit-write-all-data',['GRANT pg_write_all_data TO retrolume_data_app WITH INHERIT TRUE, SET FALSE'],True,False,'retrolume_data_app'),
      ('snapshot-SET-only-server-program',['CREATE ROLE retrolume_task120_audit07_bridge1 NOLOGIN',
        'GRANT pg_execute_server_program TO retrolume_task120_audit07_bridge1 WITH INHERIT FALSE, SET TRUE',
        'GRANT retrolume_task120_audit07_bridge1 TO retrolume_data_snapshot WITH INHERIT FALSE, SET TRUE'],False,False,'retrolume_data_snapshot'),
      ('legal-harmless-membership-current-management',['CREATE ROLE retrolume_task120_audit07_bridge1 NOLOGIN',
        'GRANT retrolume_task120_audit07_bridge1 TO retrolume_data_snapshot WITH INHERIT TRUE, SET FALSE'],False,False,'retrolume_data_snapshot')]
    for name,statements,inherit,can_set,subject in cases:
        def role_case(name=name,statements=statements,inherit=inherit,can_set=can_set,subject=subject):
            with psycopg.connect(setup.dsn('audit07-main',True),autocommit=True,row_factory=dict_row) as c:
                endpoint=single(c);before=graph(c);assert_data_schema_sync(c);c.execute('BEGIN')
                try:
                    for statement in statements:c.execute(statement)
                    capability=c.execute("SELECT has_table_privilege(%s,'public.activity_scope_sources','DELETE') AS actual_delete,pg_has_role(%s,'retrolume_data_app','SET') AS can_set_app",(subject,subject)).fetchone()
                    # App already has DELETE by design; the owner leak is a
                    # management failure, not a newly missing table privilege.
                    if subject!='retrolume_data_app':assert capability=={'actual_delete':inherit,'can_set_app':can_set},capability
                    observed_graph=graph(c);denial=None
                    management=c.execute("SELECT has_table_privilege(%s,'public.data_control','UPDATE') AS actual_control_update,pg_has_role(%s,'pg_execute_server_program','SET') AS can_set_server_program",(subject,subject)).fetchone()
                    try:assert_data_schema_sync(c)
                    except DataError as exc:denial=exc.code
                    if name.startswith('legal-harmless-membership'):assert denial is None
                    else:assert denial=='data_role_capability_mismatch',denial
                    actual_write=None
                    if subject=='retrolume_data_snapshot' and (inherit or can_set):
                        c.execute(sql.SQL('SET LOCAL SESSION AUTHORIZATION {}').format(sql.Identifier(actual_login)))
                        if can_set:c.execute('SET LOCAL ROLE retrolume_data_app')
                        actual_write=c.execute('DELETE FROM public.activity_scope_sources WHERE false').rowcount
                        c.execute('RESET ROLE');c.execute('RESET SESSION AUTHORIZATION')
                    return_value={'name':name,'endpoint':endpoint,'subject':subject,'exact_uncommitted_statements':statements,
                        'actual_PG_capability':capability,'actual_management_capability':management,'actual_snapshot_login':actual_login if actual_write is not None else None,
                        'actual_DELETE_false_rows':actual_write,'schema_check_error':denial,'baseline_graph':before,'uncommitted_graph':observed_graph}
                finally:c.execute('ROLLBACK')
                assert graph(c)==before
            with psycopg.connect(setup.dsn('audit07-main',True),autocommit=True,row_factory=dict_row) as verify:
                assert graph(verify)==before;assert_data_schema_sync(verify)
            return {**return_value,'ROLLBACK_confirmed':True,'new_connection_graph_exact':True,'temporary_bridges_retained':False}
        case('F02-'+name,role_case)
    def normal_snapshot_denied():
        with psycopg.connect(setup.dsn('audit07-main',snapshot=True),autocommit=True,row_factory=dict_row) as c:
            assert_data_schema_sync(c)
            try:c.execute('DELETE FROM public.activity_scope_sources WHERE false')
            except psycopg.Error as exc:assert exc.sqlstate=='42501';error=exc.sqlstate
            else:raise AssertionError('snapshot gained delete')
            return {'actual_login':actual_login,'normal_configuration_passed':True,'write_error':error,'old_sealed_reader_guard':'continuation06 inherited, target not started'}
    case('F02-normal-snapshot-read-and-write-denial-current-management',normal_snapshot_denied)
    return {'F01':'PASS','F02':'PASS','all_role_changes':'ROLLBACK only','API_and_worker_during_role_negatives':0}
