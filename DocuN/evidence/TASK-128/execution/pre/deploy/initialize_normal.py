"""独立新集群空库首次安装；默认只显示帮助，计划不读取凭据。"""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid


ROOT = Path(__file__).absolute().parents[1]
PROFILE = "data_exit.v1.r03"
MANIFEST_SHA256 = "f2ed126daa1c5a982b490a9343d6c17053c0f385e7a2f55676ecf4132dd2abf0"
MIGRATIONS = (
    "001_materials.sql", "002_activities.sql", "003_pdf_review.sql",
    "004_activities_time_budget.sql", "005_activities_dispatch_closed.sql",
    "006_activities_running_owner_session.sql", "007_activity_operation_results.sql",
    "008_activity_tool_budget.sql", "009_teaching.sql", "010_learning_memory.sql",
    "011_text_interview.sql", "012_html_explanations.sql", "013_data_exit.sql",
    "014_step018_retrieval.sql", "015_activity_scope_delete_permission.sql",
)
BUSINESS_GROUPS = (
    "retrolume_data_app", "retrolume_memory_app", "retrolume_interview_app",
    "retrolume_html_app", "retrolume_retrieval_app",
)
SNAPSHOT_GROUPS = ("retrolume_data_snapshot",)
GLOBAL_ROLES = (
    "retrolume_memory_owner", "retrolume_memory_app", "retrolume_memory_purger",
    "retrolume_interview_owner", "retrolume_interview_app",
    "retrolume_html_owner", "retrolume_html_app", "retrolume_data_owner",
    "retrolume_data_app", "retrolume_data_snapshot", "retrolume_data_restore_loader",
    "retrolume_retrieval_owner", "retrolume_retrieval_app",
)
TEMPLATES = (
    "config/activity.example.json", "config/integration.example.json",
    "config/q-approval.example.json", "config/preview.example.json",
)
STAGES = tuple(name[:3] for name in MIGRATIONS[:13]) + (
    "normal_control", "014", "015", "login_roles",
)


class InstallError(Exception):
    """错误码固定，不携带驱动异常、路径输入或凭据。"""


def require(condition, code):
    if not condition:
        raise InstallError(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def safe_path(value, *, existing=True, directory=False):
    """逐级 lstat，不先 resolve 掩盖符号链接或 Windows junction。"""
    path = Path(value)
    require(path.is_absolute() and ".." not in path.parts and not str(path).startswith(("\\\\", "//")), "unsafe_path")
    for part in path.parts[1:]:
        require(":" not in part and part == part.rstrip(" .") and
                re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part) is None, "unsafe_path")
    for current in reversed((path,) + tuple(path.parents)):
        try:
            info = current.lstat()
        except FileNotFoundError:
            require(current == path and not existing, "path_missing")
            continue
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400, "unsafe_path")
        if current != path or directory:
            require(stat.S_ISDIR(info.st_mode), "unsafe_path")
        else:
            require(stat.S_ISREG(info.st_mode), "unsafe_path")
    return path


def read_json(path, limit=65536):
    path = safe_path(path)
    require(path.stat().st_size <= limit, "input_too_large")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "invalid_json")
            result[key] = value
        return result

    try:
        return json.loads(path.read_bytes().decode("utf-8-sig"), object_pairs_hook=unique,
                          parse_constant=lambda unused: (_ for _ in ()).throw(InstallError("invalid_json")))
    except (ValueError, UnicodeError):
        raise InstallError("invalid_json") from None


def fixed_path(root, relative):
    path = root / relative
    require(path.is_relative_to(root), "unsafe_path")
    return safe_path(path)


def load_bundle(root=ROOT):
    root = safe_path(root, directory=True)
    manifest_path = fixed_path(root, "deploy/normal_install_manifest.json")
    require(sha256(manifest_path.read_bytes()) == MANIFEST_SHA256, "manifest_mismatch")
    manifest = read_json(manifest_path)
    require(manifest["schema_profile"] == PROFILE, "profile_mismatch")
    require([row["path"] for row in manifest["migrations"]] ==
            ["backend/migrations/" + name for name in MIGRATIONS], "manifest_mismatch")
    migration_dir = safe_path(root / "backend/migrations", directory=True)
    require({p.name for p in migration_dir.iterdir() if p.suffix.lower() == ".sql"} == set(MIGRATIONS), "migration_set_mismatch")
    bodies = []
    for row in manifest["migrations"]:
        raw = fixed_path(root, row["path"]).read_bytes()
        require(len(raw) == row["bytes"] and sha256(raw) == row["sha256"], "migration_hash_mismatch")
        try:
            bodies.append(raw.decode("utf-8-sig"))
        except UnicodeError:
            raise InstallError("migration_encoding") from None
    require([r["path"] for r in manifest["closed_templates"]] == list(TEMPLATES), "manifest_mismatch")
    templates = []
    for row in manifest["closed_templates"]:
        path = fixed_path(root, row["path"])
        require(sha256(path.read_bytes()) == row["sha256"], "template_hash_mismatch")
        templates.append(read_json(path))
    activity, integration, approval, preview = templates
    require(activity["activity_defaults"]["max_requests"] == 0 and
            activity["activity_defaults"]["max_cost_microunits"] == 0 and
            integration["enabled"] is False and approval["enabled"] is False and
            preview["image_id"] == "REPLACE_WITH_VERIFIED_IMMUTABLE_IMAGE_ID", "runtime_not_closed")
    return {"root": root, "manifest": manifest, "bodies": tuple(bodies)}


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,62}", value) is not None
            and not value.startswith("pg_") and value not in GLOBAL_ROLES, "invalid_identifier")


def load_config(path):
    config = read_json(path)
    require(isinstance(config, dict) and set(config) == {
        "schema", "enabled", "schema_profile", "target", "identities", "roles", "credential_env", "runtime_configs"
    }, "config_shape")
    require(config["schema"] == "retrolume.normal-install.v1" and type(config["enabled"]) is bool, "config_shape")
    require(config["schema_profile"] == PROFILE, "profile_mismatch")
    target, identities, roles, env = (config[k] for k in ("target", "identities", "roles", "credential_env"))
    require(isinstance(target, dict) and set(target) == {
        "host", "port", "database", "system_identifier", "database_oid", "server_major", "installer_login"
    }, "config_shape")
    require(target["host"] == "127.0.0.1" and target["server_major"] == 17, "target_unsupported")
    require(target["port"] is None or type(target["port"]) is int and 1 <= target["port"] <= 65535, "target_unsupported")
    for key in ("database", "installer_login"):
        if target[key] is not None:
            identifier(target[key])
    require(target["database"] not in ("postgres", "template0", "template1"), "target_unsupported")
    require(target["system_identifier"] is None or isinstance(target["system_identifier"], str) and
            re.fullmatch(r"[1-9][0-9]{0,19}", target["system_identifier"]) is not None and
            int(target["system_identifier"]) < 2 ** 64, "target_unsupported")
    require(target["database_oid"] is None or type(target["database_oid"]) is int and
            0 < target["database_oid"] < 2 ** 32, "target_unsupported")
    require(isinstance(identities, dict) and set(identities) == {"dataset_id", "instance_id", "originals_root_id"}, "config_shape")
    for value in identities.values():
        if value is not None:
            try:
                require(isinstance(value, str) and str(uuid.UUID(value)) == value and uuid.UUID(value).int != 0, "invalid_identity")
            except (ValueError, AttributeError):
                raise InstallError("invalid_identity") from None
    require(isinstance(roles, dict) and set(roles) == {"business_login", "snapshot_login"}, "config_shape")
    for value in roles.values():
        if value is not None:
            identifier(value)
    supplied = [v for v in (*roles.values(), target["installer_login"]) if v is not None]
    require(len(supplied) == len(set(supplied)), "role_identity_overlap")
    require(isinstance(env, dict) and set(env) == {
        "installer_password", "business_password", "snapshot_password", "maintenance_key"
    }, "config_shape")
    require(all(isinstance(v, str) and re.fullmatch(r"RETROLUME_NORMAL_[A-Z0-9_]{1,80}", v) for v in env.values())
            and len(set(env.values())) == 4, "credential_reference_invalid")
    require(config["runtime_configs"] == {"activity": None, "integration": None, "q_approval": None, "preview": None}, "runtime_not_closed")
    return config


def missing_inputs(config):
    missing = [section + "." + key for section in ("target", "identities", "roles")
               for key, value in config[section].items() if value is None]
    if not config["enabled"]:
        missing.insert(0, "enabled")
    return missing


def binding(config):
    return sha256(canonical({k: v for k, v in config.items() if k != "enabled"}))


def plan(bundle, config):
    return {
        "status": "plan_only", "schema_profile": PROFILE, "manifest_sha256": MANIFEST_SHA256,
        "migrations": bundle["manifest"]["migrations"], "missing": missing_inputs(config),
        "local_inputs_complete": not missing_inputs(config), "installed": False, "verified": False,
        "database_observed": False, "credentials_read": False, "runtime_closed": True,
        "observed": {k: None for k in ("container_id", "system_identifier", "database_oid", "source_snapshot_id",
                                        "dataset_id", "instance_id", "originals_root_id", "control_root", "data_root", "backup_root", "restore_root")},
        "next_gate": "独立风险审查及另行精确正常部署许可；计划不证明可执行或允许真实调用",
    }


def new_output(path, root=ROOT):
    path = safe_path(path, existing=False)
    require(not path.exists(), "output_exists")
    # 先检查原拼写的全部祖先，再取实际目录身份；严格模式不回退短别名字面比较。
    try:
        parent = safe_path(path.parent, directory=True).resolve(strict=True)
        project = safe_path(root, directory=True).resolve(strict=True)
    except (OSError, RuntimeError):
        raise InstallError("output_identity_unavailable") from None
    path = safe_path(parent, directory=True) / path.name
    project = safe_path(project, directory=True)
    # 产品目录只读；输出只落显式本机目录，不允许覆盖产品或配置。
    for protected in (project / "backend", project / "deploy", project / "config", project / ".git", project / ".agents", project / ".codex"):
        require(not path.is_relative_to(protected), "unsafe_output")
    require(path != project / "README.md" and path != project / "AGENTS.md", "unsafe_output")
    return path


class Journal:
    """排他新建、逐行 fsync；提交前先记 submitted，断线后不重放。"""
    def __init__(self, path, header):
        self.file = new_output(path).open("x", encoding="utf-8", newline="\n")
        try:
            self.append(header)
        except BaseException:
            self.file.close()
            raise

    def append(self, value):
        self.file.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        self.file.flush()
        os.fsync(self.file.fileno())

    def close(self):
        self.file.close()


IDENTITY_QUERY = """SELECT current_database() AS database,d.oid::bigint AS database_oid,
 (SELECT system_identifier::text FROM pg_control_system()) AS system_identifier,
 current_setting('server_version_num')::integer AS version_num,pg_encoding_to_char(d.encoding) AS encoding,
 current_user AS installer_login,session_user AS session_login,r.rolsuper,
 inet_server_addr()::text AS server_address,inet_server_port() AS server_port
 FROM pg_database d JOIN pg_roles r ON r.rolname=current_user WHERE d.datname=current_database()"""
EMPTY_QUERY = """SELECT
 EXISTS(SELECT 1 FROM pg_database WHERE NOT datistemplate AND datname NOT IN ('postgres',current_database())) AS other_databases,
 EXISTS(SELECT 1 FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()) AS other_clients,
 EXISTS(SELECT 1 FROM pg_namespace WHERE nspname NOT IN('public','information_schema') AND nspname !~ '^pg_') AS extra_schemas,
 EXISTS(SELECT 1 FROM pg_extension WHERE extname<>'plpgsql') AS extra_extensions,
 EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public') AS relations,
 EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public') AS functions,
 EXISTS(SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='public') AS types,
 EXISTS(SELECT 1 FROM pg_operator o JOIN pg_namespace n ON n.oid=o.oprnamespace WHERE n.nspname='public') AS operators,
 EXISTS(SELECT 1 FROM pg_opclass o JOIN pg_namespace n ON n.oid=o.opcnamespace WHERE n.nspname='public') AS opclasses,
 EXISTS(SELECT 1 FROM pg_opfamily o JOIN pg_namespace n ON n.oid=o.opfnamespace WHERE n.nspname='public') AS opfamilies,
 EXISTS(SELECT 1 FROM pg_collation c JOIN pg_namespace n ON n.oid=c.collnamespace WHERE n.nspname='public') AS collations,
 EXISTS(SELECT 1 FROM pg_conversion c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname='public') AS conversions,
 EXISTS(SELECT 1 FROM pg_ts_config c JOIN pg_namespace n ON n.oid=c.cfgnamespace WHERE n.nspname='public') AS text_configs,
 EXISTS(SELECT 1 FROM pg_ts_dict c JOIN pg_namespace n ON n.oid=c.dictnamespace WHERE n.nspname='public') AS text_dicts,
 EXISTS(SELECT 1 FROM pg_ts_parser c JOIN pg_namespace n ON n.oid=c.prsnamespace WHERE n.nspname='public') AS text_parsers,
 EXISTS(SELECT 1 FROM pg_ts_template c JOIN pg_namespace n ON n.oid=c.tmplnamespace WHERE n.nspname='public') AS text_templates,
 EXISTS(SELECT 1 FROM pg_event_trigger) AS event_triggers,EXISTS(SELECT 1 FROM pg_default_acl) AS default_acls,
 EXISTS(SELECT 1 FROM pg_largeobject_metadata) AS large_objects,EXISTS(SELECT 1 FROM pg_foreign_server) AS foreign_servers,
 EXISTS(SELECT 1 FROM pg_foreign_data_wrapper) AS foreign_wrappers,EXISTS(SELECT 1 FROM pg_publication) AS publications,
 EXISTS(SELECT 1 FROM pg_subscription) AS subscriptions,
 EXISTS(SELECT 1 FROM pg_cast WHERE oid>=16384) AS custom_casts,
 EXISTS(SELECT 1 FROM pg_roles WHERE rolname !~ '^pg_' AND rolname<>current_user) AS extra_cluster_roles,
 EXISTS(SELECT 1 FROM pg_namespace n CROSS JOIN LATERAL aclexplode(COALESCE(n.nspacl,acldefault('n',n.nspowner))) a
        WHERE n.nspname='public' AND a.grantee=0 AND a.privilege_type='CREATE') AS public_schema_create,
 EXISTS(SELECT 1 FROM pg_database d CROSS JOIN LATERAL aclexplode(COALESCE(d.datacl,acldefault('d',d.datdba))) a
        WHERE d.datname=current_database() AND a.grantee=0 AND a.privilege_type='CREATE') AS public_database_create,
 EXISTS(SELECT 1 FROM pg_language WHERE lanname NOT IN('internal','c','sql','plpgsql')) AS extra_languages"""


def observe_identity(connection, config):
    row = connection.execute(IDENTITY_QUERY).fetchone()
    expected = config["target"]
    require(row is not None and all(row[k] == expected[k] for k in
            ("database", "database_oid", "system_identifier", "installer_login")) and
            row["session_login"] == expected["installer_login"] and row["rolsuper"] is True and
            170000 <= row["version_num"] < 180000 and row["encoding"] == "UTF8" and
            isinstance(row["server_address"], str) and type(row["server_port"]) is int and
            0 < row["server_port"] <= 65535, "target_identity_mismatch")
    try:
        ipaddress.ip_address(row["server_address"])
    except ValueError:
        raise InstallError("target_identity_mismatch") from None
    return {k: row[k] for k in ("database", "database_oid", "system_identifier", "installer_login",
                               "server_address", "server_port", "version_num", "encoding")}


def preflight(connection, config):
    connection.execute("BEGIN READ ONLY")
    try:
        observed = observe_identity(connection, config)
        collisions = connection.execute("SELECT rolname FROM pg_roles WHERE rolname=ANY(%s)",
            (list(GLOBAL_ROLES) + list(config["roles"].values()),)).fetchall()
        require(not collisions, "global_role_collision")
        empty = connection.execute(EMPTY_QUERY).fetchone()
        require(empty is not None and not any(empty.values()), "target_not_empty_or_exclusive")
        version = connection.execute("SELECT default_version FROM pg_available_extensions WHERE name='vector'").fetchone()
        require(version is not None and version["default_version"] == "0.8.6", "vector_version_mismatch")
        return observed
    finally:
        connection.execute("ROLLBACK")


def connect(config, credentials):
    # 本函数仅在显式 apply 或完整收据 verify 的本地校验通过后调用。
    import psycopg
    from psycopg.rows import dict_row
    target = config["target"]
    return psycopg.connect(host=target["host"], hostaddr=target["host"], port=target["port"], dbname=target["database"],
        user=target["installer_login"], password=credentials["installer_password"],
        connect_timeout=3, autocommit=True, row_factory=dict_row, sslmode="disable", service="",
        options="-c search_path=public,pg_catalog -c statement_timeout=60000 -c lock_timeout=3000 -c idle_in_transaction_session_timeout=60000")


def read_credentials(config, *, readonly=False):
    keys = ("installer_password",) if readonly else tuple(config["credential_env"])
    values = {}
    for key in keys:
        value = os.environ.get(config["credential_env"][key])
        require(isinstance(value, str) and 16 <= len(value.encode("utf-8")) <= 1024 and "\x00" not in value, "credential_missing_or_invalid")
        values[key] = value
    if not readonly:
        require(len(set(values.values())) == len(values), "credential_identity_overlap")
    return values


def committed_sql(connection, body):
    cursor = connection.execute(body, prepare=False)
    status = cursor.statusmessage
    while cursor.nextset():
        status = cursor.statusmessage
    require(status == "COMMIT" and int(connection.info.transaction_status) == 0, "commit_unknown")


def create_control(connection, config, credentials):
    with connection.transaction():
        connection.execute("""INSERT INTO public.data_control
            (dataset_id,instance_id,originals_root_id,schema_profile,mode,maintenance_key_sha256)
            VALUES(%s,%s,%s,'data_exit.v1.r01','normal',%s)""",
            tuple(config["identities"][k] for k in ("dataset_id", "instance_id", "originals_root_id")) +
            (sha256(credentials["maintenance_key"].encode("utf-8")),))


def create_logins(connection, config, credentials):
    from psycopg import sql
    with connection.transaction():
        for purpose, groups in (("business", BUSINESS_GROUPS), ("snapshot", SNAPSHOT_GROUPS)):
            login = config["roles"][purpose + "_login"]
            connection.execute(sql.SQL("CREATE ROLE {} LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}").format(
                sql.Identifier(login), sql.Literal(credentials[purpose + "_password"])))
            for group in groups:
                connection.execute(sql.SQL("GRANT {} TO {} WITH INHERIT TRUE, SET FALSE, ADMIN FALSE").format(
                    sql.Identifier(group), sql.Identifier(login)))
            connection.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(config["target"]["database"]), sql.Identifier(login)))


def product_checks(root=ROOT):
    # 只装载原有纯核验模块；不装载应用、配置运行时或控制权威。
    backend = str(root / "backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)
    from app.data_exit.schema_checks import assert_data_schema_sync
    from app.data_exit.q_roles import ROLE_CAPABILITIES, MEMBERSHIPS, check_role_capabilities
    from app.data_exit.schema_profiles import get_profile
    return assert_data_schema_sync, ROLE_CAPABILITIES, MEMBERSHIPS, check_role_capabilities, get_profile


def verify_installed(connection, bundle, config):
    check_schema, role_query, member_query, check_roles, get_profile = product_checks(bundle["root"])
    require(get_profile(PROFILE).migration_chain == {
        Path(row["path"]).name: row["sha256"] for row in bundle["manifest"]["migrations"]
    }, "profile_migration_mismatch")
    check_schema(connection, PROFILE)
    roles = connection.execute(role_query).fetchall()
    memberships = connection.execute(member_query).fetchall()
    check_roles(roles, memberships, PROFILE)
    by_name = {r["rolname"]: r for r in roles}
    for key, groups in (("business_login", BUSINESS_GROUPS), ("snapshot_login", SNAPSHOT_GROUPS)):
        role = by_name.get(config["roles"][key])
        require(role is not None and role["rolcanlogin"] is True and not any(role[k] for k in (
            "rolsuper", "rolcreatedb", "rolcreaterole", "rolreplication", "rolbypassrls", "owns_objects", "owns_definers", "schema_create", "database_create"
        )), "login_role_unsafe")
        edges = [r for r in memberships if r["member"] == role["oid"]]
        require(len(edges) == len(groups) and {r["roleid"] for r in edges} == {by_name[g]["oid"] for g in groups}
                and all(r["inherit_option"] and not r["set_option"] and not r["admin_option"] for r in edges), "login_membership_mismatch")
    row = connection.execute("SELECT dataset_id::text,instance_id::text,originals_root_id::text,schema_profile,mode FROM public.data_control").fetchone()
    require(row is not None and all(row[k] == value for k, value in config["identities"].items())
            and row["schema_profile"] == PROFILE and row["mode"] == "normal", "normal_control_mismatch")


def check_product_profile(bundle):
    get_profile = product_checks(bundle["root"])[-1]
    require(get_profile(PROFILE).migration_chain == {
        Path(row["path"]).name: row["sha256"] for row in bundle["manifest"]["migrations"]
    }, "profile_migration_mismatch")


def apply(bundle, config, receipt, *, connector=connect, verifier=verify_installed):
    require(not missing_inputs(config), "apply_inputs_incomplete")
    receipt = new_output(receipt)
    check_product_profile(bundle)
    credentials = read_credentials(config)
    journal = Journal(receipt, {"schema": "retrolume.normal-install-receipt.v1", "event": "intent",
        "manifest_sha256": MANIFEST_SHA256, "config_binding": binding(config), "target": config["target"],
        "identities": config["identities"], "roles": config["roles"], "migrations": bundle["manifest"]["migrations"]})
    confirmed = []
    pending = None
    try:
        with connector(config, credentials) as connection:
            observed = preflight(connection, config)
            journal.append({"event": "preflight", "observed": observed})

            def stage(name, action):
                nonlocal pending
                journal.append({"event": "submitted", "stage": name})
                pending = name
                action()
                journal.append({"event": "confirmed", "stage": name})
                confirmed.append(name)
                pending = None

            for index, body in enumerate(bundle["bodies"]):
                stage(MIGRATIONS[index][:3], lambda body=body: committed_sql(connection, body))
                if index == 12:
                    stage("normal_control", lambda: create_control(connection, config, credentials))
            stage("login_roles", lambda: create_logins(connection, config, credentials))
            connection.execute("BEGIN READ ONLY")
            try:
                observe_identity(connection, config)
                verifier(connection, bundle, config)
            finally:
                connection.execute("ROLLBACK")
            journal.append({"event": "complete", "confirmed_stages": confirmed, "schema_profile": PROFILE})
        return {"status": "installed", "schema_profile": PROFILE, "confirmed_stages": confirmed, "runtime_closed": True}
    except BaseException as error:
        # 断线或应答丢失不能据异常文本推断回滚；submitted 保守保留为未知。
        code = "commit_unknown" if pending else (error.args[0] if isinstance(error, InstallError) else "installation_stopped")
        try:
            journal.append({"event": "stopped", "reason": code, "confirmed_stages": confirmed, "unknown_stage": pending})
        except (OSError, ValueError):
            pass
        raise InstallError(code) from None
    finally:
        journal.close()


def complete_receipt(path, bundle, config):
    path = safe_path(path)
    require(path.stat().st_size <= 131072, "receipt_invalid")
    try:
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    except (ValueError, UnicodeError):
        raise InstallError("receipt_invalid") from None
    require(len(records) == 3 + 2 * len(STAGES), "receipt_incomplete")
    header = records[0]
    require(header == {"schema": "retrolume.normal-install-receipt.v1", "event": "intent",
        "manifest_sha256": MANIFEST_SHA256, "config_binding": binding(config), "target": config["target"],
        "identities": config["identities"], "roles": config["roles"], "migrations": bundle["manifest"]["migrations"]}, "receipt_mismatch")
    require(records[1].get("event") == "preflight" and isinstance(records[1].get("observed"), dict), "receipt_invalid")
    for index, name in enumerate(STAGES):
        require(records[2 + index * 2] == {"event": "submitted", "stage": name} and
                records[3 + index * 2] == {"event": "confirmed", "stage": name}, "receipt_incomplete")
    require(records[-1] == {"event": "complete", "confirmed_stages": list(STAGES), "schema_profile": PROFILE}, "receipt_incomplete")
    return records


def verify(bundle, config, receipt, *, connector=connect, verifier=verify_installed):
    require(not [m for m in missing_inputs(config) if m != "enabled"], "verify_inputs_incomplete")
    records = complete_receipt(receipt, bundle, config)
    check_product_profile(bundle)
    credentials = read_credentials(config, readonly=True)
    try:
        with connector(config, credentials) as connection:
            connection.execute("BEGIN READ ONLY")
            try:
                observed = observe_identity(connection, config)
                require(observed == records[1]["observed"], "receipt_target_mismatch")
                verifier(connection, bundle, config)
            finally:
                connection.execute("ROLLBACK")
        return {"status": "readonly_rechecked", "schema_profile": PROFILE, "observed": observed, "runtime_closed": True}
    except Exception:
        raise InstallError("readonly_recheck_failed") from None


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InstallError("invalid_arguments")


def main(argv=None):
    parser = Parser(description=__doc__)
    commands = parser.add_subparsers(dest="action", parser_class=Parser)
    for action, help_text in (("plan", "仅核本地固定文件与非敏感输入"),
                              ("apply", "仅供另行获准的独立新集群空库首次安装"),
                              ("verify", "仅凭完整成功收据作只读复核")):
        command = commands.add_parser(action, help=help_text)
        command.add_argument("--config", type=Path, required=True, help="绝对路径，安装器自己的非敏感 JSON")
        if action == "plan":
            command.add_argument("--output", type=Path, help="可选绝对路径，仅排他新建计划文件")
        else:
            command.add_argument("--receipt", type=Path, required=True, help="绝对路径；apply 排他新建，verify 仅读完整成功收据")
    try:
        args = parser.parse_args(argv)
        if args.action is None:
            parser.print_help()
            return 0
        config = load_config(args.config)
        bundle = load_bundle()
        if args.action == "plan":
            result = plan(bundle, config)
            if args.output:
                with new_output(args.output).open("x", encoding="utf-8", newline="\n") as output:
                    output.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        elif args.action == "apply":
            result = apply(bundle, config, args.receipt)
        else:
            result = verify(bundle, config, args.receipt)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except InstallError as error:
        print(json.dumps({"status": "rejected", "reason": error.args[0]}, ensure_ascii=False))
        return 2
    except Exception:
        print(json.dumps({"status": "rejected", "reason": "local_or_driver_failure"}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
