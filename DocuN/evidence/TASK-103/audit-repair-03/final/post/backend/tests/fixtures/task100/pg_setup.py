"""本卡两库的保留式初始化；只由有限 runner 调用，不删旧资源。"""
from __future__ import annotations
import os
from pathlib import Path
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import MAIN_DB,FAULT_DB,ROLES,ControlRefusal,switched_dsn
BACKEND=Path(__file__).resolve().parents[3]
MIGRATIONS=["001_materials.sql","002_activities.sql","003_pdf_review.sql","004_activities_time_budget.sql",
    "005_activities_dispatch_closed.sql","006_activities_running_owner_session.sql","007_activity_operation_results.sql","008_activity_tool_budget.sql"]
TEACHING_MIGRATION="009_teaching.sql"
ADMIN_ROLE,APP_ROLE,DENIED_ROLE=ROLES
TEACHING_TABLES=("teaching_heads","teaching_commands","teaching_records")

DEADLINE=None

class BoundedConnection:
    def __init__(self,conn):self.conn=conn
    def execute(self,query,*args,**kwargs):
        import time
        deadline=DEADLINE
        remaining=deadline.timeout(5) if deadline is not None else min(5,max(.001,float(os.environ.get('RETROLUME_TASK100_DEADLINE',str(time.monotonic()+5)))-time.monotonic()))
        if remaining<=.001:raise ControlRefusal('pg_deadline')
        # 失败事务必须仍能回滚；在 ROLLBACK 前设置参数会被 25P02 拒绝。
        if isinstance(query,str) and query.strip().upper() in ('ROLLBACK','COMMIT'):
            return self.conn.execute(query,*args,**kwargs)
        self.conn.execute("SELECT set_config('statement_timeout',%s,false)",(str(max(1,int(remaining*1000))),))
        return self.conn.execute(query,*args,**kwargs)
    def __enter__(self):self.conn.__enter__();return self
    def __exit__(self,*args):return self.conn.__exit__(*args)
    def close(self):self.conn.close()

def connection(dsn,expected_db=None,expected_role=None,**kwargs):
    parsed=psycopg.conninfo.conninfo_to_dict(dsn)
    if parsed.get("host")!="127.0.0.1" or parsed.get("port")!="55442" or parsed.get("dbname") not in (MAIN_DB,FAULT_DB,"postgres"):
        raise ControlRefusal("database_identity")
    import time,math
    remaining=DEADLINE.timeout(5) if DEADLINE else max(.001,min(5,float(os.environ.get('RETROLUME_TASK100_DEADLINE',str(time.monotonic()+5)))-time.monotonic()))
    if remaining<=.001:raise ControlRefusal('pg_deadline')
    conn=psycopg.connect(dsn,row_factory=dict_row,connect_timeout=max(1,math.ceil(remaining)),**kwargs)
    try:
        fact=conn.execute("SELECT current_database() AS db,current_user AS role,inet_server_port() AS port").fetchone()
        if fact["db"]!=(expected_db or parsed["dbname"]) or expected_role and fact["role"]!=expected_role or fact["port"]!=5432:
            raise ControlRefusal("server_identity")
        return BoundedConnection(conn)
    except BaseException:
        conn.close(); raise

def create_roles(dsn,passwords):
    with connection(dsn,"postgres",autocommit=True) as conn:
        if not conn.execute("SELECT rolsuper FROM pg_roles WHERE rolname=current_user").fetchone()["rolsuper"]:
            raise ControlRefusal("cluster_admin_required")
        for role in ROLES:
            old=conn.execute("SELECT rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname=%s",(role,)).fetchone()
            if old and any(old.values()): raise ControlRefusal("existing_role_privilege_changed")
            memberships=conn.execute("SELECT count(*) AS n FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=%s)",(role,)).fetchone()["n"]
            if memberships: raise ControlRefusal("existing_role_membership_changed")
            verb="ALTER" if old else "CREATE"
            conn.execute(sql.SQL(verb+" ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(role),sql.Literal(passwords[role])))
            print("role_verified",role,"existing",bool(old))

def create_database(dsn,name):
    if name not in (MAIN_DB,FAULT_DB): raise ControlRefusal("database_not_allowed")
    with connection(dsn,"postgres",autocommit=True) as conn:
        old=conn.execute("SELECT pg_get_userbyid(datdba) AS owner FROM pg_database WHERE datname=%s",(name,)).fetchone()
        if old:
            if old["owner"]!=ADMIN_ROLE: raise ControlRefusal("existing_database_owner")
        else: conn.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(sql.Identifier(name),sql.Identifier(ADMIN_ROLE)))
        print("database_verified",name,"existing",bool(old))

def apply_migrations(dsn):
    with connection(dsn,MAIN_DB,ADMIN_ROLE,autocommit=True) as conn:
        existing=conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename").fetchall()
        names={r["tablename"] for r in existing}
        if not names:
            for name in MIGRATIONS:
                conn.execute((BACKEND/"migrations"/name).read_text(encoding="utf-8")); print("applied",name)
        else:
            required={"activities","activity_operations","activity_operation_results","material_sources","material_versions","activity_scope_sources","activity_allowed_models","pdf_review_candidates","pdf_review_pages","pdf_extracted_pages","pdf_user_supplements"}
            if not required.issubset(names): raise ControlRefusal("partial_baseline_preserved")
            cols=conn.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='activities'").fetchall()
            if "max_tool_calls" not in {r['column_name'] for r in cols}: raise ControlRefusal("partial_baseline_preserved")
            print("baseline_001_008_reused")
        present=names.intersection(TEACHING_TABLES)
        if present:
            if present!=set(TEACHING_TABLES): raise ControlRefusal("partial_teaching_preserved")
            expected=(BACKEND/"migrations"/TEACHING_MIGRATION).read_text(encoding="utf-8")
            import re
            normalize=lambda text:re.sub(r'\s+','',text).lower()
            for name in ('teaching_records_immutable','teaching_command_identity_guard'):
                function=conn.execute("SELECT prosrc AS body FROM pg_proc WHERE proname=%s AND pronamespace='public'::regnamespace",(name,)).fetchone()
                source=re.search(r'CREATE FUNCTION '+name+r'\(\).*?AS \$\$(.*?)\$\$;',expected,re.S).group(1)
                if function is None or normalize(function['body'])!=normalize(source):
                    # 已有本卡对象仅向前收紧这两个保护函数；全表数据哈希前后等值。
                    before=conn.execute("SELECT md5(COALESCE(string_agg(to_jsonb(r)::text,'' ORDER BY activity_id,record_id),'')) AS h FROM teaching_records r").fetchone()['h']
                    conn.execute(sql.SQL('CREATE OR REPLACE FUNCTION {}() RETURNS trigger LANGUAGE plpgsql AS {}').format(sql.Identifier(name),sql.Literal(source)))
                    after=conn.execute("SELECT md5(COALESCE(string_agg(to_jsonb(r)::text,'' ORDER BY activity_id,record_id),'')) AS h FROM teaching_records r").fetchone()['h']
                    if before!=after:raise ControlRefusal('forward_guard_changed_data')
                    print('forward_guard_verified',name,'record_fingerprint',before)
            trigger_names={r['tgname'] for r in conn.execute("SELECT tgname FROM pg_trigger WHERE tgrelid IN ('teaching_records'::regclass,'teaching_commands'::regclass) AND NOT tgisinternal").fetchall()}
            if not {'teaching_records_immutable','teaching_command_identity_guard'}.issubset(trigger_names):raise ControlRefusal('existing_teaching_trigger_missing')
            print("teaching_complete_reused")
        else:
            conn.execute((BACKEND/"migrations"/TEACHING_MIGRATION).read_text(encoding="utf-8"));print("applied",TEACHING_MIGRATION)

def grant_table_privileges(dsn):
    old=("activities","activity_scope_sources","activity_allowed_models","activity_operations","activity_operation_results","material_sources","material_versions","pdf_review_candidates","pdf_extracted_pages","pdf_review_pages","pdf_user_supplements")
    head="revision,goal_version,last_seq,phase,goal_record_id,path_record_id,node_id,exercise_record_id,answer_record_id,feedback_record_id,reason_record_id,pending_business_key,projection,updated_at"
    command="status,launch_claimed_at,obsolete_at,abandoned_at,result_record_id,error_code,updated_at"
    with connection(dsn,MAIN_DB,ADMIN_ROLE,autocommit=True) as conn:
        for table in old:
            # 原运行表保留既有 DML 范围，合成验证不使用 DELETE。
            conn.execute(sql.SQL("GRANT SELECT,INSERT,UPDATE ON {} TO {}").format(sql.Identifier(table),sql.Identifier(APP_ROLE)))
        for table in TEACHING_TABLES:
            conn.execute(sql.SQL("REVOKE ALL ON {} FROM PUBLIC,{},{}").format(sql.Identifier(table),sql.Identifier(APP_ROLE),sql.Identifier(DENIED_ROLE)))
            conn.execute(sql.SQL("GRANT SELECT,INSERT ON {} TO {}").format(sql.Identifier(table),sql.Identifier(APP_ROLE)))
        conn.execute(sql.SQL("GRANT UPDATE ("+head+") ON teaching_heads TO {}").format(sql.Identifier(APP_ROLE)))
        conn.execute(sql.SQL("GRANT UPDATE ("+command+") ON teaching_commands TO {}").format(sql.Identifier(APP_ROLE)))
        invalid=conn.execute("SELECT has_table_privilege(%s,'teaching_records','UPDATE') OR has_table_privilege(%s,'teaching_records','DELETE') OR has_any_column_privilege(%s,'teaching_records','UPDATE') AS bad",(APP_ROLE,APP_ROLE,APP_ROLE)).fetchone()['bad']
        if invalid: raise ControlRefusal("records_privilege_not_minimal")
        if conn.execute("SELECT has_table_privilege(%s,'teaching_records','SELECT') AS bad",(DENIED_ROLE,)).fetchone()['bad']:
            raise ControlRefusal("denied_role_leak")
        print("privilege_verified records=SELECT,INSERT commands=head_state_columns_only")
