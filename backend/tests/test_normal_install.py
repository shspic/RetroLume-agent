"""首次安装器的离线边界；记录器不证明真实 PG 的 SQL、事务或权限。"""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import copy
import ctypes
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).absolute().parents[2]
SPEC = importlib.util.spec_from_file_location("normal_install_under_test", ROOT / "deploy/initialize_normal.py")
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)
EXAMPLE = ROOT / "config/normal-install.example.json"
REPAIR_OBSERVATIONS = {}


def role_samples(config):
    names = list(INSTALL.GLOBAL_ROLES) + list(config["roles"].values()) + ["bridge", "danger"]
    roles = []
    for oid, name in enumerate(names, 100):
        values = dict.fromkeys(("rolsuper", "rolcreatedb", "rolcreaterole", "rolreplication", "rolbypassrls",
                                "schema_create", "database_create", "owns_objects", "owns_definers"), False)
        privilege = []
        if name in ("retrolume_data_app", config["roles"]["business_login"]):
            privilege = ["SELECT", "INSERT", "UPDATE", "DELETE"]
        elif name in ("retrolume_data_snapshot", config["roles"]["snapshot_login"], "retrolume_data_owner"):
            privilege = ["SELECT"]
        elif name == "retrolume_data_restore_loader":
            privilege = ["SELECT", "INSERT"]
        if name.endswith("_owner"):
            values.update(owns_objects=True, owns_definers=True)
        roles.append(dict(values, oid=oid, rolname=name, rolcanlogin=name in config["roles"].values(),
                          privileges=privilege, control_privileges=["SELECT"] if name == "retrolume_data_owner" else []))
    by_name = {r["rolname"]: r for r in roles}

    def edge(member, target, inherit=True, setting=False, admin=False):
        return dict(member=by_name[member]["oid"], roleid=by_name[target]["oid"], grantor=1,
                    inherit_option=inherit, set_option=setting, admin_option=admin)

    members = [edge(config["roles"]["business_login"], group) for group in INSTALL.BUSINESS_GROUPS]
    members += [edge(config["roles"]["snapshot_login"], "retrolume_data_snapshot")]
    return roles, members, by_name, edge


class Cursor:
    statusmessage = "COMMIT"

    def __init__(self, one=None, many=None):
        self.one, self.many = one, many or []

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.many

    def nextset(self):
        return None


class Recorder:
    """仅记录调用类别，绝不记录密码 SQL、维护摘要或 DSN。"""
    info = type("Info", (), {"transaction_status": 0})()

    def __init__(self, config, bundle, *, mismatch=False, nonempty=False, collision=False, vector="0.8.6", fail_stage=None, server_address="127.0.0.1"):
        self.config, self.bundle = config, bundle
        self.mismatch, self.nonempty, self.collision, self.vector, self.fail_stage = mismatch, nonempty, collision, vector, fail_stage
        self.server_address = server_address
        self.calls, self.readonly = [], False

    def __enter__(self):
        self.calls.append("connect")
        return self

    def __exit__(self, *unused):
        self.calls.append("close")

    @contextmanager
    def transaction(self):
        self.calls.append("transaction_begin")
        yield
        self.calls.append("transaction_ack")

    def execute(self, statement, params=None, **kwargs):
        if statement == "BEGIN READ ONLY":
            self.readonly = True
            self.calls.append("read_only_begin")
        elif statement == "ROLLBACK":
            self.readonly = False
            self.calls.append("read_only_end")
        elif statement == INSTALL.IDENTITY_QUERY:
            if not self.readonly:
                raise AssertionError("preflight_not_readonly")
            self.calls.append("identity_read")
            target = self.config["target"]
            return Cursor(one=dict(target, database_oid=target["database_oid"] + int(self.mismatch), session_login=target["installer_login"],
                                   version_num=170007, encoding="UTF8", rolsuper=True, server_address=self.server_address, server_port=5432))
        elif statement == INSTALL.EMPTY_QUERY:
            self.calls.append("empty_read")
            return Cursor(one={"nonempty": self.nonempty})
        elif isinstance(statement, str) and statement.startswith("SELECT default_version"):
            self.calls.append("version_read")
            return Cursor(one={"default_version": self.vector})
        elif isinstance(statement, str) and statement.startswith("SELECT rolname FROM pg_roles"):
            self.calls.append("collision_read")
            return Cursor(many=[{"rolname": INSTALL.GLOBAL_ROLES[0]}] if self.collision else [])
        elif statement in self.bundle["bodies"]:
            name = INSTALL.MIGRATIONS[self.bundle["bodies"].index(statement)][:3]
            self.calls.append("write:" + name)
            if self.readonly:
                raise AssertionError("write_in_readonly")
            if name == self.fail_stage:
                raise RuntimeError("driver detail " + "sentinel_" + "dsn_secret")
        elif isinstance(statement, str) and statement.startswith("INSERT INTO public.data_control"):
            self.calls.append("write:normal_control")
        else:
            from psycopg.sql import Composable
            if not isinstance(statement, Composable):
                raise AssertionError("unexpected_call")
            rendered = statement.as_string()
            self.calls.append("write:login_ddl" if rendered.startswith("CREATE ROLE") else "write:login_grant")
        return Cursor()


class NormalInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = INSTALL.load_bundle()
        parent = os.environ.get("RETROLUME_NORMAL_TEST_SCRATCH", tempfile.gettempdir())
        cls.scratch = Path(tempfile.mkdtemp(prefix="normal-install-", dir=parent)).absolute()

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="case-", dir=self.scratch))
        self.example = INSTALL.load_config(EXAMPLE)

    def complete_config(self):
        config = copy.deepcopy(self.example)
        config["enabled"] = True
        config["target"].update(port=55464, database="normal_empty", system_identifier="1234567890123456789", database_oid=16400,
                                installer_login="bootstrap_admin")
        config["roles"].update(business_login="normal_business", snapshot_login="normal_snapshot")
        config["identities"].update(dataset_id="00000000-0000-4000-8000-000000000001",
                                    instance_id="00000000-0000-4000-8000-000000000002",
                                    originals_root_id="00000000-0000-4000-8000-000000000003")
        return config

    def credentials(self, config):
        return {name: "synthetic_" + str(index) + "_credential_sentinel" for index, name in enumerate(config["credential_env"].values())}

    def write_config(self, value):
        path = self.work / "input.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def cli(self, argv):
        output, error = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            try:
                code = INSTALL.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, output.getvalue() + error.getvalue()

    def copy_bundle(self):
        root = self.work / "product"
        for rel in ("deploy/normal_install_manifest.json",) + tuple("backend/migrations/" + n for n in INSTALL.MIGRATIONS) + INSTALL.TEMPLATES:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, path)
        return root

    def test_01_default_help_bad_arguments_and_plan_have_no_runtime_effect(self):
        import builtins
        real_import = builtins.__import__
        forbidden = ("app.main", "app.data_exit.control", "app.data_exit.config", "app.q_authority")

        def restricted_import(name, *args, **kwargs):
            if name.startswith(forbidden):
                raise AssertionError("runtime_import")
            return real_import(name, *args, **kwargs)

        def deny(*unused, **kwargs):
            raise AssertionError("forbidden_effect")

        environment_get = os.environ.get

        def guarded_environment(name, *args):
            if name.startswith(("RETROLUME_", "PG", "OPENAI_", "DEEPSEEK_", "ZHIPU_")):
                raise AssertionError("credential_environment_read")
            return environment_get(name, *args)

        with patch.object(INSTALL.os.environ, "get", side_effect=guarded_environment), patch.object(subprocess, "Popen", side_effect=deny), \
                patch.object(INSTALL, "connect", side_effect=deny), patch.object(builtins, "__import__", side_effect=restricted_import):
            for argv in ([], ["--help"], ["plan", "--help"], ["apply", "--help"], ["verify", "--help"],
                         ["plan", "--config", str(EXAMPLE)]):
                with self.subTest(argv=argv[:1]):
                    code, unused = self.cli(argv)
                    self.assertEqual(code, 0)
            code, output = self.cli(["--unknown", "sentinel_" + "dsn_secret"])
            self.assertEqual(code, 2)
            self.assertTrue("sentinel_" + "dsn_secret" not in output, "argument_exposed")

    def test_02_plan_is_repeatable_closed_and_does_not_make_identities(self):
        before = set(self.work.iterdir())
        first = INSTALL.plan(self.bundle, self.example)
        second = INSTALL.plan(self.bundle, self.example)
        self.assertEqual(first, second)
        self.assertEqual(before, set(self.work.iterdir()))
        self.assertFalse(first["local_inputs_complete"])
        self.assertFalse(first["installed"])
        self.assertFalse(first["verified"])
        self.assertTrue(all(v is None for v in first["observed"].values()))
        self.assertTrue(all(v is None for v in self.example["runtime_configs"].values()))

    def test_03_missing_and_extra_sql_are_rejected(self):
        root = self.copy_bundle()
        path = root / "backend/migrations" / INSTALL.MIGRATIONS[0]
        raw = path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(INSTALL.InstallError, "migration_set_mismatch"):
            INSTALL.load_bundle(root)
        path.write_bytes(raw)
        (path.parent / "016_unadopted.sql").write_text("SELECT 1", encoding="utf-8")
        with self.assertRaisesRegex(INSTALL.InstallError, "migration_set_mismatch"):
            INSTALL.load_bundle(root)

    def test_04_manifest_order_extra_and_hash_edits_are_rejected(self):
        root = self.copy_bundle()
        path = root / "deploy/normal_install_manifest.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        for change in ("order", "extra", "hash"):
            value = copy.deepcopy(original)
            if change == "order":
                value["migrations"].reverse()
            elif change == "extra":
                value["migrations"].append(value["migrations"][-1])
            else:
                value["migrations"][0]["sha256"] = "0" * 64
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.subTest(change=change), self.assertRaisesRegex(INSTALL.InstallError, "manifest_mismatch"):
                INSTALL.load_bundle(root)

    def test_05_original_sql_byte_drift_is_rejected(self):
        root = self.copy_bundle()
        path = root / "backend/migrations" / INSTALL.MIGRATIONS[0]
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(INSTALL.InstallError, "migration_hash_mismatch"):
            INSTALL.load_bundle(root)

    def test_06_profile_identifiers_and_runtime_enablement_are_rejected(self):
        for change in ("profile", "identifier", "runtime", "overlap"):
            value = self.complete_config()
            if change == "profile":
                value["schema_profile"] = "data_exit.v1.r02"
            elif change == "identifier":
                value["roles"]["business_login"] = 'bad";role'
            elif change == "runtime":
                value["runtime_configs"]["integration"] = "enabled.json"
            else:
                value["roles"]["snapshot_login"] = value["roles"]["business_login"]
            with self.subTest(change=change), self.assertRaises(INSTALL.InstallError):
                INSTALL.load_config(self.write_config(value))

    def test_07_plan_entry_rejects_output_conflicts_and_path_escape(self):
        output = self.work / "plan.json"
        args = ["plan", "--config", str(EXAMPLE), "--output", str(output)]
        self.assertEqual(self.cli(args)[0], 0)
        raw = output.read_bytes()
        self.assertEqual(self.cli(args)[0], 2)
        self.assertEqual(output.read_bytes(), raw)
        for path in (self.work / ".." / "escape.json", ROOT / "deploy/new-output.json", self.work / "file:stream", self.work / "NUL"):
            self.assertEqual(self.cli(args[:-1] + [str(path)])[0], 2)

    def test_08_real_junction_or_symlink_is_rejected(self):
        provided = os.environ.get("RETROLUME_NORMAL_TEST_JUNCTION")
        target, junction = self.work / "target", self.work / "junction"
        target.mkdir()
        if provided:
            # 受限沙箱允许读 reparse 元数据；夹具由测试操作者预建在同一 scratch。
            junction = Path(provided)
            self.assertTrue(junction.is_absolute() and junction.parent.is_relative_to(self.scratch.parent))
            self.assertTrue(getattr(junction.lstat(), "st_file_attributes", 0) & 0x400)
            self.assertTrue(junction.resolve().is_relative_to(self.scratch.parent))
        elif os.name == "nt":
            junction.mkdir()
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
                                          ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
            kernel.CreateFileW.restype = ctypes.c_void_p
            kernel.DeviceIoControl.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32,
                                              ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            substitute = ("\\??\\" + str(target)).encode("utf-16-le")
            printable = str(target).encode("utf-16-le")
            paths = substitute + b"\0\0" + printable + b"\0\0"
            data = struct.pack("<LHHHHHH", 0xA0000003, 8 + len(paths), 0, 0, len(substitute), len(substitute) + 2, len(printable)) + paths
            handle = kernel.CreateFileW(str(junction), 0x40000000, 0, None, 3, 0x02200000, None)
            self.assertTrue(handle not in (None, ctypes.c_void_p(-1).value), "junction_handle_failed")
            try:
                buffer, returned = ctypes.create_string_buffer(data), ctypes.c_uint32()
                self.assertTrue(kernel.DeviceIoControl(handle, 0x900A4, buffer, len(data), None, 0, ctypes.byref(returned), None), "junction_create_failed")
            finally:
                kernel.CloseHandle(handle)
        else:
            junction.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(INSTALL.InstallError, "unsafe_path"):
            INSTALL.safe_path(junction / "plan.json", existing=False)
        self.assertEqual(self.cli(["plan", "--config", str(EXAMPLE), "--output", str(junction / "plan.json")])[0], 2)

    def test_09_disabled_apply_does_not_read_credentials_or_connect(self):
        with patch.object(INSTALL.os.environ, "get", side_effect=AssertionError("env_read")):
            with self.assertRaisesRegex(INSTALL.InstallError, "apply_inputs_incomplete"):
                INSTALL.apply(self.bundle, self.example, self.work / "receipt.jsonl", connector=lambda *unused: self.fail("connected"))
        self.assertFalse((self.work / "receipt.jsonl").exists())

    def test_10_preflight_refusals_have_zero_write_requests(self):
        config = self.complete_config()
        for number, option in enumerate(({"mismatch": True}, {"nonempty": True}, {"collision": True}, {"vector": "0.8.5"})):
            recorder = Recorder(config, self.bundle, **option)
            with self.subTest(option=number), patch.dict(os.environ, self.credentials(config), clear=True):
                with self.assertRaises(INSTALL.InstallError):
                    INSTALL.apply(self.bundle, config, self.work / (str(number) + ".jsonl"), connector=lambda *unused: recorder)
            self.assertFalse(any(c.startswith("write:") for c in recorder.calls))
            self.assertIn("read_only_end", recorder.calls)

    def test_11_apply_order_raw_chain_control_and_role_separation(self):
        config = self.complete_config()
        recorder, receipt = Recorder(config, self.bundle, server_address="172.18.0.2"), self.work / "receipt.jsonl"

        def verify(connection, bundle, current):
            self.assertTrue(connection.readonly)
            connection.calls.append("role_schema_check")

        with patch.dict(os.environ, self.credentials(config), clear=True):
            result = INSTALL.apply(self.bundle, config, receipt, connector=lambda *unused: recorder, verifier=verify)
        self.assertEqual(result["confirmed_stages"], list(INSTALL.STAGES))
        self.assertLess(recorder.calls.index("version_read"), recorder.calls.index("write:001"))
        self.assertLess(recorder.calls.index("write:013"), recorder.calls.index("write:normal_control"))
        self.assertLess(recorder.calls.index("write:normal_control"), recorder.calls.index("write:014"))
        self.assertLess(recorder.calls.index("write:015"), recorder.calls.index("write:login_ddl"))
        self.assertEqual(recorder.calls.count("write:login_ddl"), 2)
        INSTALL.complete_receipt(receipt, self.bundle, config)
        text = receipt.read_text(encoding="utf-8")
        self.assertTrue(all(value not in text and INSTALL.sha256(value.encode()) not in text for value in self.credentials(config).values()), "receipt_secret_exposed")

    def test_12_unknown_commit_preserves_prior_stage_and_blocks_replay(self):
        config, receipt = self.complete_config(), self.work / "partial.jsonl"
        recorder = Recorder(config, self.bundle, fail_stage="002")
        with patch.dict(os.environ, self.credentials(config), clear=True):
            with self.assertRaisesRegex(INSTALL.InstallError, "commit_unknown"):
                INSTALL.apply(self.bundle, config, receipt, connector=lambda *unused: recorder)
            before = list(recorder.calls)
            with self.assertRaisesRegex(INSTALL.InstallError, "output_exists"):
                INSTALL.apply(self.bundle, config, receipt, connector=lambda *unused: recorder)
        self.assertEqual(recorder.calls, before)
        rows = [json.loads(line) for line in receipt.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rows[-1]["confirmed_stages"], ["001"])
        self.assertEqual(rows[-1]["unknown_stage"], "002")
        self.assertNotIn("write:003", recorder.calls)
        self.assertTrue("sentinel_" + "dsn_secret" not in receipt.read_text(encoding="utf-8"), "driver_detail_exposed")
        with self.assertRaisesRegex(INSTALL.InstallError, "receipt_incomplete"):
            INSTALL.verify(self.bundle, config, receipt, connector=lambda *unused: self.fail("connected"))

    def test_13_complete_receipt_allows_only_readonly_recheck(self):
        config, receipt = self.complete_config(), self.work / "complete.jsonl"
        first = Recorder(config, self.bundle)
        with patch.dict(os.environ, self.credentials(config), clear=True):
            INSTALL.apply(self.bundle, config, receipt, connector=lambda *unused: first, verifier=lambda *unused: None)
        original = receipt.read_bytes()
        second = Recorder(config, self.bundle)
        only = {config["credential_env"]["installer_password"]: next(iter(self.credentials(config).values()))}
        with patch.dict(os.environ, only, clear=True):
            result = INSTALL.verify(self.bundle, config, receipt, connector=lambda *unused: second, verifier=lambda *unused: None)
        self.assertEqual(result["status"], "readonly_rechecked")
        self.assertEqual(receipt.read_bytes(), original)
        self.assertFalse(any(c.startswith("write:") for c in second.calls))
        bad = self.complete_config()
        bad["target"]["database_oid"] += 1
        with self.assertRaises(INSTALL.InstallError):
            INSTALL.verify(self.bundle, bad, receipt, connector=lambda *unused: self.fail("connected"))

    def test_14_existing_pure_role_checker_accepts_intended_separate_logins(self):
        from app.data_exit.q_roles import check_role_capabilities
        config = self.complete_config()
        roles, members, unused, unused_edge = role_samples(config)
        result = check_role_capabilities(roles, members, INSTALL.PROFILE)
        audited = {r["role"]: r for r in result}
        self.assertIn(config["roles"]["business_login"], audited)
        self.assertEqual(audited[config["roles"]["snapshot_login"]]["purpose"], ["retrolume_data_snapshot"])

    def test_15_existing_checker_rejects_transitive_set_inherit_admin_and_cross_purpose(self):
        from app.data_exit.contracts import DataError
        from app.data_exit.q_roles import check_role_capabilities
        config = self.complete_config()
        for mode in ("set", "inherit", "admin", "owner", "snapshot_write", "management"):
            roles, members, by_name, edge = role_samples(config)
            business = config["roles"]["business_login"]
            if mode in ("set", "management"):
                by_name["danger"]["rolsuper"] = True
                members.extend((edge(business, "bridge", inherit=False, setting=True), edge("bridge", "danger", inherit=False, setting=True)))
            elif mode == "inherit":
                by_name["danger"]["database_create"] = True
                members.extend((edge(business, "bridge"), edge("bridge", "danger")))
            elif mode == "admin":
                by_name["danger"]["rolcreaterole"] = True
                members.extend((edge(business, "bridge"), edge("bridge", "danger", inherit=False, admin=True)))
            elif mode == "owner":
                members.append(edge(business, "retrolume_memory_owner"))
            else:
                members.append(edge(config["roles"]["snapshot_login"], "retrolume_data_app"))
            with self.subTest(mode=mode), self.assertRaises(DataError):
                check_role_capabilities(roles, members, INSTALL.PROFILE)

    def test_16_production_verifier_reuses_schema_and_capability_checks(self):
        config = self.complete_config()
        from app.data_exit.q_roles import ROLE_CAPABILITIES, MEMBERSHIPS, check_role_capabilities
        from app.data_exit.schema_profiles import get_profile
        roles, members, unused, unused_edge = role_samples(config)
        schema_calls = []

        class CheckRecorder:
            def execute(self, query):
                if query == ROLE_CAPABILITIES:
                    return Cursor(many=roles)
                if query == MEMBERSHIPS:
                    return Cursor(many=members)
                return Cursor(one=dict(config["identities"], schema_profile=INSTALL.PROFILE, mode="normal"))

        with patch.object(INSTALL, "product_checks", return_value=(lambda conn, profile: schema_calls.append(profile),
                           ROLE_CAPABILITIES, MEMBERSHIPS, check_role_capabilities, get_profile)):
            INSTALL.verify_installed(CheckRecorder(), self.bundle, config)
        self.assertEqual(schema_calls, [INSTALL.PROFILE])

    def test_17_redacted_cli_failure_and_runtime_dependency_boundary(self):
        config = self.complete_config()
        path = self.write_config(config)
        secret = "sentinel_" + "dsn_secret"
        with patch.object(INSTALL, "apply", side_effect=RuntimeError(secret)):
            code, output = self.cli(["apply", "--config", str(path), "--receipt", str(self.work / "out.jsonl")])
        self.assertEqual(code, 2)
        self.assertTrue(secret not in output, "driver_detail_exposed")
        source = (ROOT / "deploy/initialize_normal.py").read_text(encoding="utf-8")
        for forbidden in ("DocuN", "fixtures", "tests/", "project_NO3_", "项目开发提示词", "sitecustomize", "TESTONLY"):
            self.assertNotIn(forbidden, source)

    def test_18_help_documentation_and_original_startup_arguments_agree(self):
        for action in ("plan", "apply", "verify"):
            code, output = self.cli([action, "--help"])
            self.assertEqual(code, 0)
            self.assertIn("--config", output)
            self.assertIn("--output" if action == "plan" else "--receipt", output)
        import ast
        tree = ast.parse((ROOT / "deploy/start_local.py").read_text(encoding="utf-8-sig"))
        options = {arg.value for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and n.func.attr == "add_argument" for arg in n.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)}
        self.assertTrue({"--container", "--port", "--shutdown-stdin"} <= options)
        self.assertFalse({"--profile", "--migrate", "--initialize"} & options)
        doc = (ROOT / "deploy/normal-install.md").read_text(encoding="utf-8")
        self.assertTrue(all(option in doc for option in ("--config", "--output", "--receipt", "--shutdown-stdin")))

    def test_19_connect_pins_driver_address_for_direct_apply_and_verify(self):
        import psycopg
        from psycopg._conninfo_utils import get_param
        from psycopg.rows import dict_row
        config = self.complete_config()
        environment = self.credentials(config)
        environment.update(PGHOSTADDR="203.0.113.77", PGHOST="synthetic.invalid")
        credentials = {"installer_password": environment[config["credential_env"]["installer_password"]]}
        captured, recorders = [], []
        purpose = "direct"

        def driver_entry(**kwargs):
            self.assertTrue(kwargs.get("host") == kwargs.get("hostaddr") == "127.0.0.1", "connection_address_not_pinned")
            self.assertTrue(get_param(kwargs, "hostaddr") == "127.0.0.1", "driver_environment_override")
            self.assertEqual(kwargs["port"], config["target"]["port"])
            self.assertEqual(kwargs["dbname"], config["target"]["database"])
            self.assertEqual(kwargs["user"], config["target"]["installer_login"])
            self.assertTrue(kwargs["password"] == credentials["installer_password"], "credential_parameter_mismatch")
            self.assertEqual(kwargs["connect_timeout"], 3)
            self.assertIs(kwargs["autocommit"], True)
            self.assertIs(kwargs["row_factory"], dict_row)
            self.assertEqual(kwargs["sslmode"], "disable")
            self.assertNotIn("service", kwargs)
            self.assertIn("search_path=public,pg_catalog", kwargs["options"])
            captured.append({"purpose": purpose, **{key: kwargs[key] for key in ("host", "hostaddr", "port", "dbname", "user")}})
            recorder = Recorder(config, self.bundle, server_address="172.18.0.2")
            recorders.append(recorder)
            return recorder

        receipt = self.work / "shared-connect.jsonl"
        # 先替换唯一驱动入口，再设置合成环境；不调用真实 TCP、DNS 或认证。
        with patch.object(psycopg, "connect", side_effect=driver_entry), patch.dict(os.environ, environment, clear=True):
            INSTALL.connect(config, credentials)
            purpose = "apply"
            INSTALL.apply(self.bundle, config, receipt, verifier=lambda *unused: None)
            original = receipt.read_bytes()
            purpose = "verify"
            INSTALL.verify(self.bundle, config, receipt, verifier=lambda *unused: None)
            self.assertEqual((os.environ["PGHOSTADDR"], os.environ["PGHOST"]), ("203.0.113.77", "synthetic.invalid"))
        self.assertEqual([item["purpose"] for item in captured], ["direct", "apply", "verify"])
        self.assertEqual(receipt.read_bytes(), original)
        self.assertFalse(any(call.startswith("write:") for call in recorders[-1].calls))
        REPAIR_OBSERVATIONS["F126-01"] = {"driver_kwargs": captured, "real_authentication_exercised": False,
                                          "synthetic_environment_preserved": True, "server_address": "172.18.0.2", "server_port": 5432}

    def test_22_ambient_service_is_rejected_before_driver_without_environment_changes(self):
        import psycopg
        config = self.complete_config()
        environment = self.credentials(config)
        credentials = {"installer_password": environment[config["credential_env"]["installer_password"]]}
        for key in ("PGSERVICE", "PGSERVICEFILE"):
            for value in ("", "synthetic-untrusted-service"):
                with self.subTest(key=key, value=value), patch.dict(os.environ, {**environment, key:value}, clear=True), patch.object(psycopg, "connect") as driver:
                    before = dict(os.environ)
                    with self.assertRaises(INSTALL.InstallError) as raised:
                        INSTALL.connect(config, credentials)
                    self.assertEqual(raised.exception.args[0], "ambient_service_rejected")
                    driver.assert_not_called()
                    self.assertEqual(dict(os.environ), before)

    def test_23_identity_accepts_only_host_addresses_and_preserves_other_checks(self):
        config = self.complete_config()
        row = dict(config["target"], session_login=config["target"]["installer_login"],
                   version_num=170011, encoding="UTF8", rolsuper=True, server_address="172.19.0.2/32", server_port=5432)
        class IdentityRow:
            def execute(self, statement):
                assert statement == INSTALL.IDENTITY_QUERY
                return self
            def fetchone(self):return row
        for value in ("172.19.0.2/32", "172.18.0.2", "::1", "2001:db8::2/128"):
            row["server_address"] = value
            observed = INSTALL.observe_identity(IdentityRow(), config)
            self.assertEqual(observed["server_address"], value)
            self.assertEqual(observed["server_port"], 5432)
        for value in ("invalid", "172.19.0.2/24", "2001:db8::2/64", "172.19.0.2/33", ""):
            row["server_address"] = value
            with self.subTest(address=value), self.assertRaises(INSTALL.InstallError):
                INSTALL.observe_identity(IdentityRow(), config)
        row["server_address"] = "172.19.0.2/32"
        for key, wrong in (("database_oid", 1), ("system_identifier", "wrong"), ("installer_login", "wrong"),
                           ("session_login", "wrong"), ("rolsuper", False), ("version_num", 160000),
                           ("encoding", "LATIN1"), ("server_port", 0)):
            saved = row[key]; row[key] = wrong
            with self.subTest(field=key), self.assertRaises(INSTALL.InstallError):
                INSTALL.observe_identity(IdentityRow(), config)
            row[key] = saved

    def test_20_real_short_alias_is_rejected_before_plan_or_receipt_write(self):
        self.assertEqual(os.name, "nt", "actual_windows_short_alias_required")
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)

        def converted(name, path):
            function = getattr(kernel, name)
            function.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
            function.restype = ctypes.c_uint32
            size = function(str(path), None, 0)
            self.assertGreater(size, 0, "actual_alias_metadata_unavailable")
            buffer = ctypes.create_unicode_buffer(size + 1)
            count = function(str(path), buffer, len(buffer))
            self.assertTrue(0 < count < len(buffer), "actual_alias_metadata_unavailable")
            return Path(buffer.value)

        short_root = converted("GetShortPathNameW", ROOT)
        long_root = converted("GetLongPathNameW", short_root)
        self.assertNotEqual(short_root, ROOT, "actual_short_alias_unavailable")
        self.assertTrue(os.path.samefile(short_root, ROOT) and os.path.samefile(long_root, ROOT))
        actual_open, write_probes, observed = Path.open, [], []

        def no_write(path, mode="r", *args, **kwargs):
            if any(flag in mode for flag in "wax+"):
                write_probes.append({"path": str(path), "mode": mode})
                raise AssertionError("protected_output_write_probe")
            return actual_open(path, mode, *args, **kwargs)

        for name in ("backend", "deploy", "config"):
            directory = short_root / name
            INSTALL.safe_path(directory, directory=True)
            self.assertTrue(os.path.samefile(directory, ROOT / name))
            output = directory / ("repair01-" + self.work.name + ".json")
            self.assertFalse(output.exists())
            with self.subTest(directory=name), patch.object(Path, "open", no_write), \
                    patch.object(INSTALL, "read_credentials", side_effect=AssertionError("unexpected_credential_read")):
                with self.assertRaisesRegex(INSTALL.InstallError, "unsafe_output"):
                    INSTALL.new_output(output)
                code, text = self.cli(["plan", "--config", str(EXAMPLE), "--output", str(output)])
                self.assertEqual(code, 2)
                self.assertEqual(json.loads(text)["reason"], "unsafe_output")
                with self.assertRaisesRegex(INSTALL.InstallError, "unsafe_output"):
                    INSTALL.Journal(output, {"event": "offline_probe"})
                with self.assertRaisesRegex(INSTALL.InstallError, "unsafe_output"):
                    INSTALL.apply(self.bundle, self.complete_config(), output)
            self.assertFalse(output.exists())
            observed.append({"short_directory": str(directory), "long_directory": str(converted("GetLongPathNameW", directory)),
                             "same_directory": True, "new_output_plan_journal_apply_rejected": True, "file_created": False})
        self.assertEqual(write_probes, [])
        REPAIR_OBSERVATIONS["F126-02"] = {"short_root": str(short_root), "long_root": str(long_root),
                                          "directories": observed, "blocked_write_probe_calls": write_probes}

    def test_21_directory_identity_failure_is_closed_before_open(self):
        output = self.work / "identity-unavailable.json"
        with patch.object(Path, "resolve", side_effect=OSError("synthetic_identity_failure")), \
                patch.object(Path, "open", side_effect=AssertionError("unexpected_file_open")):
            with self.assertRaisesRegex(INSTALL.InstallError, "output_identity_unavailable"):
                INSTALL.new_output(output)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
