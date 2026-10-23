"""One real transactional ADMIN combination; no API/worker during the graph change."""
import psycopg
from psycopg.rows import dict_row
from psycopg import sql
from . import setup,resources as r
from .audit07 import case
from .audit07_permissions import graph,single
from app.data_exit.schema_checks import assert_data_schema_sync
from app.data_exit.contracts import DataError


def exercise():
    login=setup.info('audit07-main')['snapshot_user'];bridge='retrolume_task120_audit07_bridge1'
    def action():
        with psycopg.connect(setup.dsn('audit07-main',True),autocommit=True,row_factory=dict_row) as c:
            endpoint=single(c);before=graph(c);assert_data_schema_sync(c)
            statements=['CREATE ROLE '+bridge+' NOLOGIN',
                'GRANT retrolume_data_app TO '+bridge+' WITH INHERIT FALSE, SET TRUE',
                sql.SQL('GRANT {} TO {} WITH ADMIN TRUE, INHERIT FALSE, SET FALSE').format(sql.Identifier(bridge),sql.Identifier(login)).as_string(c)]
            c.execute('BEGIN')
            try:
                for statement in statements:c.execute(statement)
                observed=graph(c)
                pre=c.execute("SELECT has_table_privilege(%s,'public.activity_scope_sources','DELETE') AS delete,pg_has_role(%s,'retrolume_data_app','SET') AS can_set_app",(login,login)).fetchone()
                assert pre=={'delete':False,'can_set_app':False},pre
                denial=None
                try:assert_data_schema_sync(c)
                except DataError as exc:denial=exc.code
                assert denial=='data_role_capability_mismatch',denial
                c.execute(sql.SQL('SET SESSION AUTHORIZATION {}').format(sql.Identifier(login)))
                assert c.execute('SELECT session_user::text AS s').fetchone()['s']==login
                # This GRANT is executed by the actual existing snapshot
                # principal, not by the setup superuser.
                delegated='GRANT '+bridge+' TO retrolume_data_snapshot WITH INHERIT FALSE, SET TRUE'
                c.execute(delegated)
                after_grant=c.execute("SELECT current_user::text AS actor,pg_has_role(session_user,'retrolume_data_app','SET') AS can_set_app").fetchone()
                assert after_grant['actor']==login and after_grant['can_set_app']
                c.execute('SET ROLE retrolume_data_app')
                after_set=c.execute("SELECT current_user::text AS actor,has_table_privilege(current_user,'public.activity_scope_sources','DELETE') AS delete").fetchone()
                assert after_set=={'actor':'retrolume_data_app','delete':True}
            finally:
                c.execute('ROLLBACK')
                c.execute('SET SESSION AUTHORIZATION DEFAULT')
            after=graph(c);assert after==before;assert_data_schema_sync(c)
        with psycopg.connect(setup.dsn('audit07-main',True),autocommit=True,row_factory=dict_row) as verify:
            assert graph(verify)==before;assert_data_schema_sync(verify)
            choices=verify.execute('''SELECT c.activity_id::text,c.memory_id::text,h.state,h.revision
                FROM activity_memory_choices c JOIN learning_memories h USING(memory_id)
                ORDER BY c.activity_id,c.memory_id''').fetchall()
            r.write(r.EVIDENCE/'memory-fixture-current-selection-readonly.json',{
                'existing_activity_memory_choices':choices,'active_selected_memories':sum(x['state']=='active' for x in choices),
                'body_read':False,'activity_bindings_modified':False})
        return {'endpoint':endpoint,'subject':login,'exact_uncommitted_statements':statements,
            'before_capability':pre,'strict_check_before_delegation':denial,'actual_subject_GRANT':delegated,
            'actual_after_GRANT':after_grant,'actual_SET_ROLE':after_set,'observed_graph':observed,
            'before':before,'after':after,'ROLLBACK_and_new_connection_equal':True,'normal_before_and_after_pass':True,
            'role_changes_committed':False,'password_LOGIN_admin_attributes_changed':False,'server_program_executed':False}
    return case('F02-ADMIN-delegation-SET-combination',action)
