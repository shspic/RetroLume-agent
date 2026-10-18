"""同一精确专簇的非空升级与坏结构拒绝，不重建或删除任何旧数据。"""
import hashlib,json,re,subprocess
from pathlib import Path
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import ROOT,atomic,event
from .resources import DOCKER,ADMIN,shell_env
from app.materials.repository import PostgresMaterials


def snapshot(conn):
    tables=conn.execute("SELECT c.relname,c.relacl::text,r.rolname AS owner FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname='public' AND c.relkind='r' AND c.relname NOT LIKE 'html_%' ORDER BY c.relname").fetchall()
    rows=conn.execute("SELECT s.id::text,s.title,s.current_version::text,s.revision,v.id::text AS version_id,v.filename,v.format,v.sha256,v.size FROM material_sources s JOIN material_versions v ON v.source_id=s.id ORDER BY s.id,v.id").fetchall()
    columns=conn.execute("SELECT table_name,column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='public' AND table_name NOT LIKE 'html_%' ORDER BY table_name,ordinal_position").fetchall()
    return {"tables":tables,"material_rows":rows,"columns":columns}


def baseline(conn):
    for path in sorted((ROOT/"backend/migrations").glob("*.sql")):
        if not path.name[:3].isdigit() or not 1<=int(path.name[:3])<=11:continue
        conn.execute(path.read_text(encoding="utf-8"))


def restore_missing_baseline(folder):
    """同簇现有角色由原main持有：只恢复已核main的010/011 schema对象，不改迁移守卫。"""
    cid="1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51"
    args=[DOCKER,"exec",cid,"pg_dump","-U",ADMIN,"-d","retrolume_task111_main","--schema-only","--format=custom","--schema=public","--exclude-table=public.html_*"]
    result=subprocess.run(args,capture_output=True,timeout=20,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise RuntimeError("authorized main schema dump failed")
    archive=result.stdout;(folder/"old-baseline-schema.cdump").write_bytes(archive)
    listing=subprocess.run([DOCKER,"exec","-i",cid,"pg_restore","--list"],input=archive,capture_output=True,timeout=10,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
    if listing.returncode:raise RuntimeError("schema archive list failed")
    texts=[(ROOT/"backend/migrations"/name).read_text(encoding="utf-8") for name in ("010_learning_memory.sql","011_text_interview.sql")]
    names=set()
    for body in texts:
        names.update(re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:FUNCTION|TABLE|TRIGGER|(?:UNIQUE\s+)?INDEX)\s+(?:public\.)?([a-zA-Z0-9_]+)",body,re.I))
    selected=[]
    for line in listing.stdout.decode("utf-8").splitlines():
        if line.startswith(';'):selected.append(line);continue
        words=set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*",line))
        if names & words:selected.append(line)
    if len([l for l in selected if not l.startswith(';')])<10:raise RuntimeError("010011 archive selection incomplete")
    toc='\n'.join(selected)+'\n';(folder/"selected-010011.toc").write_text(toc,encoding="utf-8")
    location="/tmp/retrolume-task111-010011.toc"
    put=subprocess.run([DOCKER,"exec","-i",cid,"tee",location],input=toc.encode(),capture_output=True,timeout=10,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
    if put.returncode:raise RuntimeError("task-owned TOC write failed")
    restored=subprocess.run([DOCKER,"exec","-i",cid,"pg_restore","-U",ADMIN,"-d","retrolume_task111_upgrade","--exit-on-error","--single-transaction","--use-list",location],input=archive,capture_output=True,timeout=30,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
    (folder/"baseline-restore.stderr.txt").write_bytes(restored.stderr)
    atomic(folder/"baseline-restore.json",{"method":"exact_schema_only_010011_restore_from_authorized_main","archive_sha256":hashlib.sha256(archive).hexdigest(),"source_migration_files_unchanged":True,"existing_cluster_roles_not_changed":True,"code":restored.returncode})
    if restored.returncode:raise RuntimeError("baseline schema-only restore refused")


def verify(resource,folder):
    raw=(ROOT/"backend/migrations/012_html_explanations.sql").read_text(encoding="utf-8");identities=[]
    with psycopg.connect(resource["admin"],autocommit=True) as main:
        for name in ("retrolume_task111_upgrade","retrolume_task111_fault"):
            exists=main.execute("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=%s)",(name,)).fetchone()[0]
            if not exists:main.execute(sql.SQL("CREATE DATABASE {} OWNER retrolume_task111_admin").format(sql.Identifier(name)))
            identities.append({"name":name,"created_now":not exists,"retained":exists})
    upgrade=psycopg.conninfo.make_conninfo(resource["admin"],dbname="retrolume_task111_upgrade")
    fault=psycopg.conninfo.make_conninfo(resource["admin"],dbname="retrolume_task111_fault")
    with psycopg.connect(upgrade,autocommit=True,row_factory=dict_row) as conn:
        existing=conn.execute("SELECT to_regclass('public.html_artifacts') AS html").fetchone()["html"]
        if existing is not None:
            prior=ROOT/"DocuN/evidence/TASK-111/execution/continuation-02/root-08/attempt-18"
            before=json.loads((prior/"upgrade-before.json").read_text(encoding="utf-8"));after=json.loads((prior/"upgrade-after.json").read_text(encoding="utf-8"))
            if before["columns"]!=after["columns"] or before["material_rows"]!=after["material_rows"]:raise RuntimeError("old fields or rows changed")
            deltas=[]
            for left,right in zip(before["tables"],after["tables"]):
                if left["relname"]!=right["relname"] or left["owner"]!=right["owner"]:raise RuntimeError("old table owner changed")
                if left==right:continue
                def normalized(row):
                    cursor=conn.execute("""SELECT role.rolname AS grantee,a.privilege_type,a.is_grantable FROM pg_roles owner
                      CROSS JOIN LATERAL aclexplode(COALESCE(%s::aclitem[],acldefault('r',owner.oid))) a
                      LEFT JOIN pg_roles role ON role.oid=a.grantee WHERE owner.rolname=%s ORDER BY role.rolname,a.privilege_type""",(row["relacl"],row["owner"]))
                    return cursor.fetchall()
                old_acl=normalized(left);new_acl=normalized(right);added=[r for r in new_acl if r not in old_acl]
                if any(r not in new_acl for r in old_acl) or any(r["grantee"]!="retrolume_html_owner" or r["privilege_type"]!="SELECT" or r["is_grantable"] for r in added):raise RuntimeError("unexpected old principal ACL delta")
                deltas.append({"table":left["relname"],"new_role_read_only":added})
            atomic(folder/"upgrade-result.json",{"status":"PASS_NONEMPTY_ROWS_COLUMNS_EXISTING_PRINCIPALS_ACL","raw_ACL_byte_equal":False,"authorized_new_HTML_owner_SELECT_delta":deltas,"before_after_source":str(prior),"reapplied_012":False})
        else:
            prepare_upgrade(resource,folder,conn,raw)
    rejections=[]
    with psycopg.connect(fault,autocommit=True,row_factory=dict_row) as conn:
        try:conn.execute(raw);raise RuntimeError("missing baseline accepted")
        except psycopg.errors.RaiseException as error:
            conn.execute("ROLLBACK");rejections.append({"case":"missing_baseline","sqlstate":error.sqlstate,"message":error.diag.message_primary})
        none=conn.execute("SELECT count(*) AS n FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'html_%'").fetchone()["n"]
        if none!=0:raise RuntimeError("partial DDL after absent baseline")
        conn.execute("CREATE TABLE public.activities (scope_revision text,dispatch_closed boolean)")
        conn.execute("CREATE TABLE public.activity_operations (kind text)")
        conn.execute("CREATE TABLE public.activity_operation_results (payload text)")
        conn.execute("CREATE TABLE public.teaching_records (source_refs text)")
        conn.execute("CREATE TABLE public.activity_memory_bindings (known_bad_shape integer)")
        conn.execute("CREATE TABLE public.interview_heads (known_bad_shape integer)")
        try:conn.execute(raw);raise RuntimeError("bad existing domain accepted")
        except psycopg.errors.RaiseException as error:
            conn.execute("ROLLBACK");rejections.append({"case":"bad_prerequisite_types","sqlstate":error.sqlstate,"message":error.diag.message_primary})
        present=conn.execute("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name LIKE 'html_%' ORDER BY table_name,ordinal_position").fetchall()
        if present:raise RuntimeError("partial DDL added on bad prerequisite rejection")
        atomic(folder/"fault-result.json",{"status":"PASS_TRANSACTIONAL_REJECTION","rejections":rejections,"no_HTML_DDL_after_each_failure":True})
    atomic(folder/"migration-databases.json",identities)


def prepare_upgrade(resource,folder,conn,raw):
        old=conn.execute("SELECT to_regclass('public.activities') AS old,to_regclass('public.learning_memories') AS memory,to_regclass('public.interview_heads') AS interview").fetchone()
        if old["old"] is None:baseline(conn)
        elif old["memory"] is None and old["interview"] is None:restore_missing_baseline(folder)
        content=b"TASK111 nonempty pre-012 synthetic material retained"
        row=PostgresMaterials(upgrade).save(source_id=None,expected_version=None,filename="task111-upgrade.md",format="md",sha256=hashlib.sha256(content).hexdigest(),size=len(content))
        before=snapshot(conn);atomic(folder/"upgrade-before.json",before)
        conn.execute(raw)
        after=snapshot(conn);atomic(folder/"upgrade-after.json",after)
        if before!=after or not before["material_rows"]:raise RuntimeError("nonempty old fields/ACL changed")
        new=conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'html_%' ORDER BY tablename").fetchall()
        if len(new)!=4:raise RuntimeError("four domain tables not complete")
        atomic(folder/"upgrade-result.json",{"status":"PASS_NONEMPTY_FIELDS_ACL_RETENTION","seed":row,"new_tables":new,"migration_sha256":hashlib.sha256(raw.encode()).hexdigest()})
