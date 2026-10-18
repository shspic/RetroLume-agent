"""一个有界真实根；失败后的新根复用本进程RAM口令，最多三根。"""
from __future__ import annotations
import json, os, secrets, socket, subprocess, sys, threading, time, queue, traceback
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import psycopg
from psycopg import sql
from .common import ROOT, EVIDENCE, CIDS, DATABASE, APP_ROLE, PERMIT, SECRETS, Control, clean, command, inspect_owned, process_tree, process_one, stop_witness, stamp, sha_bytes, write

APP_PASSWORD = None
ADMIN_PASSWORD = None

def ports_available():
    result = {}
    for port in (18103, 18104, 55443, 55444, 55445):
        with socket.socket() as sock:
            result[str(port)] = sock.connect_ex(("127.0.0.1", port)) != 0
    return result

def role_acl(conn):
    roles = conn.execute("""SELECT jsonb_agg(jsonb_build_object('name',rolname,'super',rolsuper,'inherit',rolinherit,
      'create_role',rolcreaterole,'create_db',rolcreatedb,'login',rolcanlogin,'replication',rolreplication,
      'bypassrls',rolbypassrls,'connections',rolconnlimit,'valid_until',rolvaliduntil) ORDER BY rolname)
      FROM pg_roles WHERE rolname=ANY(%s)""", ([APP_ROLE, "retrolume_memory_app", "retrolume_memory_owner", "retrolume_memory_purger"],)).fetchone()[0]
    memberships = conn.execute("""SELECT jsonb_agg(jsonb_build_object('role',r.rolname,'member',u.rolname,'admin',m.admin_option,
       'inherit',m.inherit_option,'set',m.set_option) ORDER BY r.rolname,u.rolname)
       FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.roleid JOIN pg_roles u ON u.oid=m.member
       WHERE r.rolname LIKE 'retrolume_memory_%%' OR u.rolname=%s""", (APP_ROLE,)).fetchone()[0]
    tables = conn.execute("""SELECT jsonb_agg(jsonb_build_object('name',c.relname,'owner',pg_get_userbyid(c.relowner),
       'acl',c.relacl::text) ORDER BY c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
       WHERE n.nspname='public' AND c.relkind='r'""").fetchone()[0]
    functions = conn.execute("""SELECT jsonb_agg(jsonb_build_object('name',p.proname,'owner',pg_get_userbyid(p.proowner),
       'definer',p.prosecdef,'volatility',p.provolatile,'search_path',p.proconfig,'acl',p.proacl::text,
       'source',p.prosrc) ORDER BY p.proname) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
       WHERE n.nspname='public' AND(p.proname LIKE 'memory_%' OR p.proname IN('activity_memory_eligible','purge_learning_memory'))""").fetchone()[0]
    return {"roles": roles, "memberships": memberships, "tables": tables, "functions": functions}

def snapshot(conn):
    conn.execute("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")
    try:
        conn.execute("SET LOCAL statement_timeout='5000ms'")
        names = [r[0] for r in conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")]
        tables = {}
        for name in names:
            rows = conn.execute(sql.SQL("SELECT COALESCE(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text),'[]'::jsonb) FROM public.{} t").format(sql.Identifier(name))).fetchone()[0]
            tables[name] = rows
        conn.execute("COMMIT")
        return tables
    except Exception:
        conn.execute("ROLLBACK")
        raise

def fingerprint(value):
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())

def environment():
    keys = ("PATH", "SystemRoot", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA", "APPDATA", "ProgramFiles", "ProgramFiles(x86)")
    return {k: os.environ[k] for k in keys if k in os.environ}

def actual_get(path, token, control):
    headers = {"Origin": "http://127.0.0.1:18103"}
    if token:
        headers["X-RetroLume-Session"] = token
    try:
        with urlopen(Request("http://127.0.0.1:18103" + path, headers=headers, method="GET"), timeout=control.remaining(10)) as response:
            return response.status, json.load(response), dict(response.headers)
    except HTTPError as exc:
        return exc.code, json.load(exc), dict(exc.headers)

def source_freeze():
    data = json.loads((EVIDENCE / "orchestration-setup-20261007/audit-input.json").read_text("utf-8"))
    actual = {p: sha_bytes((ROOT / p).read_bytes()) for p in data["current_files"]}
    assert actual == data["current_files"], "冻结产品字节漂移"
    return actual

def run_root(control):
    global APP_PASSWORD, ADMIN_PASSWORD
    number = control.begin_root()
    directory = EVIDENCE / ("read-only-" + str(number).zfill(2))
    directory.mkdir(parents=True, exist_ok=True)
    report = {"permit": PERMIT, "number": number, "started_at": stamp(), "status": "FAIL", "business_POST": 0, "business_SQL_writes": 0}
    server = node = None
    witnesses = []
    pg_started = False
    try:
        write(directory / "source-before.json", source_freeze())
        harness = sorted((ROOT / "backend/tests/fixtures/task104").glob("*.py")) + [ROOT / "frontend/tests/task104-citation-audit.cjs"]
        for path in harness:
            target = directory / "as-run-harness" / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
        before_ports = ports_available()
        assert all(before_ports.values()), "前置端口仍被占用"
        public = []
        raw1 = None
        for slot in (1, 2, 3):
            info, raw = inspect_owned(slot)
            assert not info["running"] and info["pid"] == 0, "旧服务尚未全停"
            public.append(info)
            if slot == 1:
                raw1 = raw
        write(directory / "resources-before.json", {"containers": public, "ports_available": before_ports})
        if ADMIN_PASSWORD is None:
            ADMIN_PASSWORD = next(x.split("=", 1)[1] for x in raw1["Config"]["Env"] if x.startswith("POSTGRES_PASSWORD="))
            SECRETS.add(ADMIN_PASSWORD)
            SECRETS.add(quote(ADMIN_PASSWORD, safe=""))
        control.reserve("container_start", {"cid": CIDS[0]})
        started = command(["docker", "start", CIDS[0]], timeout=control.remaining(20))
        assert started.returncode == 0, "精确pg1启动失败"
        pg_started = True
        admin = "postgresql://postgres:" + quote(ADMIN_PASSWORD, safe="") + "@127.0.0.1:55443/" + DATABASE
        ready_deadline = time.monotonic() + control.remaining(20)
        while True:
            try:
                with psycopg.connect(admin, connect_timeout=2, autocommit=True) as conn:
                    assert conn.execute("SELECT current_database()").fetchone()[0] == DATABASE
                break
            except psycopg.Error:
                if time.monotonic() >= ready_deadline:
                    raise
                time.sleep(0.1)
        with psycopg.connect(admin, connect_timeout=2, autocommit=True) as conn:
            before = snapshot(conn)
            attrs = role_acl(conn)
            write(directory / "business-before.json", before)
            write(directory / "catalog-role-before.json", attrs)
            if APP_PASSWORD is None:
                control.reserve("password_reset", {"role": APP_ROLE, "scope": "仅RAM随机口令，旧服务全停"})
                APP_PASSWORD = secrets.token_urlsafe(32)
                SECRETS.add(APP_PASSWORD)
                conn.execute(sql.SQL("ALTER ROLE {} PASSWORD {}").format(sql.Identifier(APP_ROLE), sql.Literal(APP_PASSWORD)))
            assert attrs == role_acl(conn), "角色属性或ACL改变"
        dsn = "postgresql://" + APP_ROLE + ":" + quote(APP_PASSWORD, safe="") + "@127.0.0.1:55443/" + DATABASE
        with psycopg.connect(dsn, connect_timeout=2, autocommit=True) as conn:
            actor = conn.execute("SELECT current_user,session_user,(SELECT rolsuper FROM pg_roles WHERE rolname=current_user),pg_has_role(current_user,'retrolume_memory_owner','MEMBER'),pg_has_role(current_user,'retrolume_memory_purger','MEMBER')").fetchone()
            assert actor[0] == actor[1] == APP_ROLE and not any(actor[2:]), "实际app身份不满足普通最小角色"
            write(directory / "ordinary-app-identity.json", {"current_user": actor[0], "session_user": actor[1], "superuser": actor[2], "owner_member": actor[3], "purger_member": actor[4], "password_ram_only": True})
        data = directory / "workspace/data"
        originals = data / "originals"
        backup = directory / "workspace/backup"
        originals.mkdir(parents=True, exist_ok=True)
        backup.mkdir(parents=True, exist_ok=True)
        config_source = EVIDENCE.parent / "TASK-103/continuation-02/workspace/activity-config.json"
        config_path = directory / "workspace/activity-config.json"
        config_path.write_bytes(config_source.read_bytes())
        assert config_path.read_bytes() == config_source.read_bytes()
        original_root = EVIDENCE.parent / "TASK-103/continuation-01/workspace/data/originals"
        original_hash = "2cf6d42095064095a7c82760eee133b1ef3f69b1abb7f7a766b154e654e50d80"
        content = (original_root / original_hash).read_bytes()
        assert sha_bytes(content) == original_hash
        (originals / original_hash).write_bytes(content)
        write(directory / "configuration-and-copy.json", {"same_c02_config_bytes": True, "config_sha256": sha_bytes(config_path.read_bytes()), "original_sha256": original_hash, "original_bytes": len(content), "source_readonly": str(original_root / original_hash), "data": str(data), "backup": str(backup)})
        api_env = environment()
        synthetic = secrets.token_urlsafe(24)
        SECRETS.add(synthetic)
        api_env.update(RETROLUME_DATA_DIR=str(data), RETROLUME_BACKUP_DIR=str(backup), RETROLUME_DATABASE_URL=dsn,
                       RETROLUME_ACTIVITY_CONFIG=str(config_path), RETROLUME_TASK103_SYNTHETIC_KEY=synthetic,
                       PYTHONPATH=str(ROOT / "backend"))
        control.reserve("listener_start", {"module": "tests.fixtures.task104.server", "port": 18103})
        server = subprocess.Popen([sys.executable, "-X", "utf8", "-B", "-m", "tests.fixtures.task104.server", "--run-dir", str(directory)], cwd=ROOT / "backend", env=api_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        server_witness = process_one(server.pid)
        assert server_witness and "tests.fixtures.task104.server" in server_witness["command"]
        witnesses.append(server_witness)
        write(directory / "server-identity.json", server_witness)
        ready_deadline = time.monotonic() + control.remaining(20)
        while True:
            try:
                status, health, _ = actual_get("/health", None, control)
                assert status == 200 and health["status"] == "ok"
                break
            except Exception:
                if server.poll() is not None or time.monotonic() >= ready_deadline:
                    raise
                time.sleep(0.1)
        status, session, _ = actual_get("/api/session", None, control)
        assert status == 200
        token = session["token"]
        SECRETS.add(token)
        target = {"activity_id": "a29a945b-a58f-4798-b4b3-93cc1e736aed", "record_id": "e6964ce9-7686-45c3-b8b2-8e247cd25dcf", "citation_id": "lc_c0655a9aed2099f2e0d9f328", "switch_activity_id": "0643576f-0c29-46ce-aff8-2e0653a03b6f"}
        target["citation_path"] = "/api/activities/" + target["activity_id"] + "/teaching/records/" + target["record_id"] + "/citations/" + target["citation_id"]
        status, workspace, _ = actual_get("/api/activities/" + target["activity_id"] + "/teaching/workspace", token, control)
        assert status == 200 and not workspace["memory_invalid"], "现有目标工作区不可读"
        status, citation, headers = actual_get(target["citation_path"], token, control)
        assert status == 200 and citation["citation"]["citation_id"] == target["citation_id"], "现有目标引用不可读；不补建"
        target.update(view_token=workspace["view_token"], workspace=workspace, citation_precheck=citation)
        write(directory / "target-fresh-read.json", {"target": target, "status": status, "cache_control": headers.get("Cache-Control"), "no_new_execution_qualification": True})
        write(directory / "browser-target.json", target)
        script = ROOT / "frontend/tests/task104-citation-audit.cjs"
        control.reserve("driver", {"script": str(script)})
        control.reserve("browser", {"profile": str(directory / "browser-profile")})
        node_env = environment()
        node_env["TASK104_RUN_DIR"] = str(directory)
        node = subprocess.Popen(["node", str(script)], cwd=ROOT / "frontend", env=node_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        driver_tree = process_tree(node.pid)
        witnesses.extend(driver_tree)
        write(directory / "driver-identity.json", {"root_pid": node.pid, "tree": driver_tree})
        stdout, stderr = node.communicate(timeout=max(0.1, control.remaining(210) - 5))
        write(directory / "driver-output.json", {"exit_code": node.returncode, "stdout": clean(stdout.decode("utf-8", "replace")), "stderr": clean(stderr.decode("utf-8", "replace"))})
        browser = json.loads((directory / "browser/result.json").read_text("utf-8"))
        report["browser"] = browser
        assert node.returncode == 0 and browser["status"] == "PASS", "只读引用补证未全部成立"
        with psycopg.connect(admin, connect_timeout=2, autocommit=True) as conn:
            after = snapshot(conn)
            write(directory / "business-after.json", after)
            assert before == after, "GET/SELECT补证业务表发生变化"
            assert attrs == role_acl(conn), "非口令角色属性/ACL发生变化"
        assert not (directory / "forbidden-http.json").exists() and not (directory / "network-denied.json").exists()
        write(directory / "source-after.json", source_freeze())
        report.update(status="PASS", before_sha256=fingerprint(before), after_sha256=fingerprint(after), tables=len(before), ordinary_app=True, source_drift=False, password_resets=control.state["counts"]["password_reset"])
    except Exception as exc:
        report.update(error_type=type(exc).__name__, error=clean(str(exc)), traceback=clean(traceback.format_exc()))
    finally:
        control.begin_cleanup()
        cleanup = {"at": stamp(), "stopped": []}
        if node is not None and node.poll() is None:
            try:
                witnesses.extend(process_tree(node.pid))
            except Exception as observed:
                report["tree_observation_error"] = type(observed).__name__
        if server is not None:
            write(directory / "stop-api.json", {"stop": True})
            try:
                out, err = server.communicate(timeout=control.remaining(6))
                write(directory / "server-output.json", {"exit_code": server.returncode, "stdout": clean(out.decode("utf-8", "replace")), "stderr": clean(err.decode("utf-8", "replace"))})
            except Exception:
                pass
        identity_file = directory / "browser/process-identities.json"
        if identity_file.exists():
            value = json.loads(identity_file.read_text("utf-8"))
            witnesses.extend(value if isinstance(value, list) else [value])
        known = {w["pid"]: w for w in witnesses if w is not None}
        for witness in sorted(known.values(), key=lambda x: x["pid"], reverse=True):
            try:
                cleanup["stopped"].append(stop_witness(witness))
            except Exception as exc:
                cleanup["stopped"].append({"pid": witness["pid"], "state": "unconfirmed", "error_type": type(exc).__name__})
        try:
            if pg_started:
                command(["docker", "stop", "--time", "10", CIDS[0]], timeout=control.remaining(20))
            cleanup["containers"] = [inspect_owned(slot)[0] for slot in (1, 2, 3)]
            cleanup["ports_available"] = ports_available()
            cleanup["complete"] = all(not r["running"] and r["pid"] == 0 for r in cleanup["containers"]) and all(cleanup["ports_available"].values()) and all(x["state"] in ("absent", "stopped") for x in cleanup["stopped"])
        except Exception as exc:
            cleanup.update(complete=False, error_type=type(exc).__name__, error=clean(str(exc)))
        control.end_cleanup()
        report.update(ended_at=stamp(), cleanup_complete=cleanup.get("complete", False), data_roles_profiles_volumes_retained=True)
        write(directory / "resources-after.json", cleanup)
        write(directory / "root-result.json", report)
        print(json.dumps({"root": number, "status": report["status"], "error": report.get("error"), "cleanup": report["cleanup_complete"], "counts": control.state["counts"], "seconds": control.state["used"], "result": str(directory / "root-result.json")}, ensure_ascii=False), flush=True)
    return report

def main():
    control = Control()
    incoming = queue.Queue()
    def read_commands():
        for line in sys.stdin:
            incoming.put(line.strip())
    threading.Thread(target=read_commands, daemon=True).start()
    while True:
        report = run_root(control)
        if report["status"] == "PASS" or not report["cleanup_complete"] or control.state["counts"]["entry"] >= 3:
            return 0 if report["status"] == "PASS" and report["cleanup_complete"] else 1
        print("本根已收尾。仅在有据fixture修正后输入retry；输入stop保留退出。RAM口令不落盘。", flush=True)
        while time.monotonic() < control.state["fixed_active_deadline"]:
            try:
                action = incoming.get(timeout=10)
                break
            except queue.Empty:
                continue
        else:
            return 1
        if action != "retry":
            return 1
        control.state = json.loads(control.path.read_text("utf-8"))

if __name__ == "__main__":
    sys.exit(main())
