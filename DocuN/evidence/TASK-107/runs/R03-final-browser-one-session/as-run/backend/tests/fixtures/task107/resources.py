"""仅复用精确pg1；pg2/3只inspect，不取凭据或连接。"""
import json
import hashlib
import secrets
import socket
import subprocess
import time
from .common import ROOT, EVIDENCE, atomic_json, load, register_secret, reserve

CID = "dca7942c0b39c136fbdfd9f38dafdabd60571ad472539a8961fe0bc3f2fa34e4"
APP = "retrolume_task106_app"
BOOT = "retrolume_task106_bootstrap"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"


def docker(args):
    result = subprocess.run(["docker", *args], capture_output=True, text=True, encoding="utf-8",
                            timeout=25, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError("107精确Docker操作失败")
    return result.stdout


def spec(cid):
    data = load(EVIDENCE / "orchestration-setup-20261008/audit-input.json")
    return next(x for x in data["exact_resources"] if x["cid"] == cid)


def inspect(cid):
    expected = spec(cid); value = json.loads(docker(["inspect", cid]))[0]; host = value["HostConfig"]
    mount = value["Mounts"]
    assert value["Id"] == cid and value["Name"].lstrip("/") == expected["name"] and value["Image"] == IMAGE
    assert value["Config"]["Labels"] == expected["labels"] and expected["labels"]["retrolume.permit"] == "TASK-106-G10-20261008"
    assert len(mount) == 1 and mount[0]["Type"] == "volume" and mount[0]["Name"] == expected["name"] + "-data" and mount[0]["Destination"] == "/var/lib/postgresql/data"
    assert host["Memory"] == 536870912 and host["NanoCpus"] == 1000000000 and host["PidsLimit"] == 128
    assert not host["Privileged"] and not host.get("CapAdd") and host["RestartPolicy"]["Name"] == "no" and host["PortBindings"] == expected["ports"]
    return value


def public(value):
    return dict(cid=value["Id"], name=value["Name"], image=value["Image"], labels=value["Config"]["Labels"],
                running=value["State"]["Running"], pid=value["State"]["Pid"], status=value["State"]["Status"],
                mounts=value["Mounts"], ports=value["HostConfig"]["PortBindings"])


def port_free(port):
    with socket.socket() as connection:
        connection.settimeout(.1)
        return connection.connect_ex(("127.0.0.1", port)) != 0


def all_stopped():
    data = load(EVIDENCE / "orchestration-setup-20261008/audit-input.json")
    values = [public(inspect(x["cid"])) for x in data["exact_resources"]]
    assert all(not x["running"] and x["pid"] == 0 for x in values)
    assert all(port_free(p) for p in (18106, 18107, 55446, 55447, 55448))
    return values


def start():
    all_stopped()
    reserve("container_start", dict(cid=CID, only_existing=True))
    docker(["start", CID])
    import psycopg
    value = inspect(CID)
    password = next(x.split("=", 1)[1] for x in value["Config"]["Env"] if x.startswith("POSTGRES_PASSWORD="))
    register_secret(password)
    admin = psycopg.conninfo.make_conninfo(host="127.0.0.1", port=55446, dbname="retrolume_task106_main", user=BOOT, password=password, connect_timeout=3)
    register_secret(admin)
    until = time.monotonic() + 20
    while True:
        try:
            with psycopg.connect(admin, autocommit=True) as connection:
                connection.execute("SELECT 1")
            return admin
        except psycopg.Error:
            if time.monotonic() >= until:
                raise RuntimeError("107精确pg1就绪失败") from None
            time.sleep(.15)


def role_shape(connection):
    role = connection.execute("SELECT to_jsonb(r)-'rolpassword' AS role FROM pg_roles r WHERE rolname=%s", (APP,)).fetchone()["role"]
    memberships = list(connection.execute("SELECT roleid::regrole::text AS role,member::regrole::text AS member,admin_option,inherit_option,set_option FROM pg_auth_members WHERE member=%s::regrole ORDER BY roleid::regrole::text", (APP,)))
    tables = list(connection.execute("SELECT c.relname,r.rolname AS owner,c.relacl::text AS acl FROM pg_class c JOIN pg_roles r ON r.oid=c.relowner WHERE c.relnamespace='public'::regnamespace AND c.relkind IN ('r','v') ORDER BY c.relname"))
    columns = list(connection.execute("SELECT c.relname,a.attname,a.attacl::text AS acl FROM pg_class c JOIN pg_attribute a ON a.attrelid=c.oid WHERE c.relnamespace='public'::regnamespace AND a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum"))
    functions = list(connection.execute("SELECT p.proname,pg_get_function_identity_arguments(p.oid) AS args,r.rolname AS owner,p.proacl::text AS acl FROM pg_proc p JOIN pg_roles r ON r.oid=p.proowner WHERE p.pronamespace='public'::regnamespace ORDER BY p.proname,args"))
    return dict(role=role, memberships=memberships, tables=tables, columns=columns, functions=functions)


def ordinary_dsn(admin):
    import psycopg
    from psycopg import sql
    from psycopg.rows import dict_row
    assert inspect(CID)["State"]["Running"]
    password = hashlib.sha256((admin + "|TASK-107-G10-AUDIT-20261008|app-only").encode()).hexdigest()
    register_secret(password)
    enrolled = EVIDENCE / "ordinary-password-enrolled.json"
    with psycopg.connect(admin, autocommit=True, row_factory=dict_row) as connection:
        before = role_shape(connection); role = before["role"]
        assert role["rolcanlogin"] and not any(role[k] for k in ("rolsuper", "rolcreatedb", "rolcreaterole", "rolreplication", "rolbypassrls"))
        assert not any(x["role"] in ("retrolume_interview_owner", "retrolume_memory_owner", "retrolume_memory_purger") for x in before["memberships"])
        if not enrolled.exists():
            reserve("password_reset", dict(cid=CID, role=APP, only_password=True, old_services_stopped=True))
            connection.execute(sql.SQL("ALTER ROLE {} PASSWORD {}").format(sql.Identifier(APP), sql.Literal(password)))
        after = role_shape(connection); assert before == after
    atomic_json(EVIDENCE / "ordinary-role-before-after.json", dict(before=before, after=after, equal=True, password_saved=False, grants_or_owner_changes=False))
    atomic_json(enrolled, dict(cid=CID, role=APP, derivation="本许可bootstrap派生，只有RAM值", role_unchanged=True))
    values = psycopg.conninfo.conninfo_to_dict(admin)
    dsn = psycopg.conninfo.make_conninfo(**{**values, "user": APP, "password": password})
    register_secret(dsn)
    with psycopg.connect(dsn, row_factory=dict_row) as connection:
        assert connection.execute("SELECT current_user AS name").fetchone()["name"] == APP
    return dsn


def stop():
    value = inspect(CID)
    if value["State"]["Running"]:
        docker(["stop", "--time", "10", CID])
    value = inspect(CID)
    assert not value["State"]["Running"] and value["State"]["Pid"] == 0
    return public(value)
