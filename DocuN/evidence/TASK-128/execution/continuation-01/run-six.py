"""TASK127唯一串行控制器；只续尚未完成段，正式工具、原SQL与原生启动器不改。"""
import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import threading
import time
import uuid

ROOT = Path(__file__).absolute().parents[5]
E = Path(__file__).absolute().parent
PRIVATE = ROOT / ".runtime/normal-first-install"
IMAGE = "pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
IMAGE_ID = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
SLOTS = {
    "source": {"name": "retrolume-q-first-normal", "volume": "retrolume-q-first-normal-data", "database": "retrolume_q_first_normal",
               "project": "retrolume-first-install-source", "ports": [55482, 55484, 55486], "business": "retrolume_normal_app", "snapshot": "retrolume_normal_snapshot"},
    "interrupted": {"name": "retrolume-install-interrupted", "volume": "retrolume-install-interrupted-data", "database": "retrolume_install_interrupted",
                    "project": "retrolume-first-install-interrupted", "ports": [55483, 55485, 55487], "business": "retrolume_interrupt_app", "snapshot": "retrolume_interrupt_snapshot"},
}
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "backend/.venv/Lib/site-packages")]
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from app.data_exit.files import safe_root, private_file
from app.data_exit.schema_profiles import get_profile
from app.data_exit.schema_checks import assert_data_schema_sync
from app.data_exit.q_roles import ROLE_CAPABILITIES, MEMBERSHIPS, check_role_capabilities

spec = importlib.util.spec_from_file_location("task127_win_support", E / "win-support.py")
WIN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(WIN)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


class Controller:
    def __init__(self, reason):
        self.path = E / "checkpoint.json"
        self.permit = json.loads((E.parents[1] / "orchestration-continuation01-20261023/permit.json").read_text(encoding="utf-8-sig"))
        if self.path.exists():self.state = json.loads(self.path.read_bytes())
        else:
            self.state = json.loads((E.parent / "checkpoint.json").read_bytes())
            self.state["previous_checks"] = self.state["checks"]
            self.state["checks"] = {}
        require(self.state["entries"] < 7, "combined_entry_cap")
        self.state["entries"] += 1
        self.entry = self.state["entries"]
        self.entry_clock = time.monotonic()
        self.preparation_conservative_seconds = 7800
        self.run = E / ("entry-" + str(self.entry).zfill(2))
        self.run.mkdir(exist_ok=False)
        self.redactions, self.credentials = [], {}
        self.active_api, self.api_refs = None, []
        self.pressure, self.done = threading.Event(), threading.Event()
        self.lock = threading.RLock()
        self.docker = Path(os.environ["LOCALAPPDATA"]) / "Programs/DockerDesktop/resources/bin/docker.exe"
        self.env = {k: os.environ[k] for k in ("SystemRoot", "WINDIR", "TEMP", "TMP", "ComSpec", "USERPROFILE", "APPDATA", "LOCALAPPDATA") if k in os.environ}
        self.env["PATH"] = str(ROOT / "backend/.venv/Scripts") + os.pathsep + str(self.docker.parent) + os.pathsep + str(Path(self.env["SystemRoot"]) / "System32")
        self.state["last_entry"] = {"entry": self.entry, "reason": reason, "started": utc(), "status": "preparing"}
        self.save()
        self.freeze()

    def clean(self, value):
        text = json.dumps(value, ensure_ascii=False, default=str)
        for secret in self.redactions:
            text = text.replace(secret, "[REDACTED]")
        return json.loads(text)

    def evidence(self, name, value):
        path = self.run / name
        raw = (json.dumps(self.clean(value), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        with path.open("xb") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())

    def save(self):
        with self.lock:
            raw = (json.dumps(self.state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            temporary = self.path.with_suffix(".next")
            with temporary.open("wb") as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            os.replace(temporary, self.path)

    def freeze(self):
        rows = []
        for path in (E / "run-six.py", E / "install-observer.py", E / "win-support.py"):
            raw = path.read_bytes()
            (self.run / path.name).write_bytes(raw)
            rows.append({"path": str(path), "bytes": len(raw), "sha256": digest(raw)})
        inputs = json.loads((E / "final-run-inputs.json").read_bytes())
        for row in inputs:
            require(digest(Path(row["path"]).read_bytes()) == row["sha256"], "frozen_input_drift")
        self.evidence("as-run.json", {"helpers": rows, "inputs": inputs, "observed": utc()})

    def guard(self, *, startup=False):
        require(dt.datetime.now(dt.timezone.utc) < dt.datetime.fromisoformat(self.permit["valid_until"]), "calendar_limit")
        require(not self.pressure.is_set(), "pressure_or_holding_stop")
        require(self.preparation_conservative_seconds + time.monotonic() - self.entry_clock < 9900, "tool_cleanup_reserve")
        if startup:
            require(WIN.available_mib() >= 512, "startup_memory_below512")
        pg = sum(x.get("seconds", time.time() - x["start_epoch"]) for x in self.state["pg_intervals"])
        api = sum(x.get("seconds", time.time() - x["start_epoch"]) for x in self.state["api_intervals"])
        require(pg < 1800 and api < 900, "holding_cap")
        if startup:
            require(pg < 1400 and api < 650, "insufficient_cleanup_holding_reserve")

    def command(self, args, *, env=None, timeout=30, allow_failure=False, stdin=None):
        self.state["commands"] += 1
        number = self.state["commands"]
        started = time.perf_counter()
        record = {"argv": args, "started": utc(), "timeout": timeout, "environment_names": sorted((env or self.env).keys())}
        try:
            result = subprocess.run(args, cwd=ROOT, env=env or self.env, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            record.update(exit_code=result.returncode, stdout=result.stdout.decode("utf-8", errors="replace"), stderr=result.stderr.decode("utf-8", errors="replace"))
        except subprocess.TimeoutExpired:
            record.update(exit_code=124, stdout="", stderr="bounded_command_timeout")
        record["wall_seconds"] = time.perf_counter() - started
        self.evidence("command-" + str(number).zfill(3) + ".json", record)
        self.save()
        require(allow_failure or record["exit_code"] == 0, "command_failed_" + str(number))
        return record

    def docker_json(self, args, *, absent_ok=False):
        result = self.command([str(self.docker)] + args, allow_failure=absent_ok)
        if result["exit_code"]:
            require(absent_ok and ("No such" in result["stderr"] or "not found" in result["stderr"]), "docker_read_failed")
            return None
        return json.loads(result["stdout"])

    def inspect(self, slot):
        # inspect完整JSON只留内存，command不能记录Env。
        target = self.state["slots"][slot]
        start = time.perf_counter()
        result = subprocess.run([str(self.docker), "inspect", target["cid"]], env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        require(result.returncode == 0, "owned_container_inspect_failed")
        raw = json.loads(result.stdout)[0]
        require(raw["Id"] == target["cid"] and raw["Image"] == IMAGE_ID, "container_identity_changed")
        require(raw["Name"].lstrip("/") == SLOTS[slot]["name"], "container_name_changed")
        if target.get("network_id"):
            network_ids = [value["NetworkID"] for value in raw["NetworkSettings"]["Networks"].values()]
            require(len(network_ids) == 1 and (network_ids[0] == target["network_id"] or not raw["State"]["Running"] and network_ids[0] == ""), "container_network_identity_changed")
        return {"cid": raw["Id"], "image_id": raw["Image"], "created": raw["Created"], "state": raw["State"],
                "mounts": raw["Mounts"], "network_ids": {k: v["NetworkID"] for k, v in raw["NetworkSettings"]["Networks"].items()},
                "limits": {k: raw["HostConfig"].get(k) for k in ("NanoCpus", "Memory", "PidsLimit", "RestartPolicy", "NetworkMode", "PortBindings")},
                "inspect_wall_seconds": time.perf_counter() - start}

    def memory_watch(self):
        low = 0
        with (self.run / "memory.jsonl").open("a", encoding="utf-8") as out:
            while not self.done.is_set():
                value = WIN.available_mib()
                out.write(json.dumps({"utc": utc(), "available_mib": value}) + "\n"); out.flush()
                low = low + 1 if value < 256 else 0
                pg = sum(x.get("seconds", time.time() - x["start_epoch"]) for x in self.state["pg_intervals"])
                api = sum(x.get("seconds", time.time() - x["start_epoch"]) for x in self.state["api_intervals"])
                remaining = (dt.datetime.fromisoformat(self.permit["valid_until"]) - dt.datetime.now(dt.timezone.utc)).total_seconds()
                if low >= 2 or pg >= 1500 or api >= 650 or remaining < 300:
                    self.state["forced_stop_trigger"] = {"low_samples": low, "pg_seconds": pg, "api_seconds": api, "calendar_remaining": remaining}
                    self.pressure.set()
                    if self.active_api and self.active_api.poll() is None:
                        try:self.active_api.stdin.write(b"stop\n"); self.active_api.stdin.flush()
                        except (OSError, ValueError):pass
                    for slot in tuple(self.state["slots"]):
                        if self.state["slots"][slot].get("holding"):
                            try:self.stop_pg(slot)
                            except Exception:self.state["pressure_stop_unknown"] = True
                    self.save()
                    return
                self.done.wait(2)

    def choose_port(self, candidates, purpose):
        owners = WIN.port_owners(set(candidates))
        attempts = []
        for port in candidates:
            if any(row["port"] == port for row in owners):
                attempts.append({"port": port, "occupied": True}); continue
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
                try:probe.bind(("127.0.0.1", port))
                except OSError as error:
                    attempts.append({"port": port, "bind_winerror": error.winerror}); continue
            self.evidence(purpose + "-port.json", {"owners": owners, "attempts": attempts, "chosen": port, "short_exclusive_bind_succeeded": True})
            return port
        raise RuntimeError("approved_ports_unavailable")

    def secrets_for(self, slot):
        if slot not in self.credentials:
            path = PRIVATE / slot / "credentials.dpapi"
            values = WIN.protect_secret(path.read_bytes(), decrypt=True).decode("ascii").split("\0")
            require(len(values) == 4 and len(set(values)) == 4, "private_secret_shape")
            self.credentials[slot] = dict(zip(("installer_password", "business_password", "snapshot_password", "maintenance_key"), values))
            self.redactions.extend(values)
        return self.credentials[slot]

    def configure_slot(self, slot):
        if slot in self.state["slots"]:
            self.secrets_for(slot)
            require(self.state["slots"][slot].get("cid"), "created_slot_identity_incomplete_no_recreate")
            self.inspect(slot)
            return
        raise RuntimeError("TASK128_creation_prohibited")

    def pg_kwargs(self, slot, purpose="installer"):
        target, secret = self.state["slots"][slot], self.secrets_for(slot)
        user = target["bootstrap"] if purpose == "installer" else SLOTS[slot][purpose]
        return {"host": "127.0.0.1", "hostaddr": "127.0.0.1", "port": target["port"], "dbname": SLOTS[slot]["database"], "user": user,
                "password": secret[purpose + "_password"], "connect_timeout": 3, "sslmode": "disable", "autocommit": True, "row_factory": dict_row}

    @contextmanager
    def connection(self, slot, purpose="installer"):
        with psycopg.connect(**self.pg_kwargs(slot, purpose)) as connection:
            yield connection

    def start_pg(self, slot):
        self.guard(startup=True)
        require(not any(self.inspect(other)["state"]["Running"] for other in self.state["slots"] if other != slot), "second_pg_refused")
        target = self.state["slots"][slot]
        require(target["starts"] < (5 if slot == "source" else 2), "pg_start_cap")
        require(not self.inspect(slot)["state"]["Running"], "unaccounted_running_pg")
        target["starts"] += 1
        interval = {"slot": slot, "cid": target["cid"], "start_epoch": time.time(), "start_requested": utc()}
        self.state["pg_intervals"].append(interval); target["holding"] = len(self.state["pg_intervals"]); self.save()
        self.command([str(self.docker), "start", target["cid"]], timeout=30)
        deadline = time.monotonic() + 30
        while True:
            self.guard()
            try:
                with self.connection(slot) as connection:
                    row = connection.execute("SELECT current_database() AS database,d.oid::bigint AS database_oid,(SELECT system_identifier::text FROM pg_control_system()) AS system_identifier,current_setting('server_version_num')::int AS version_num,current_user AS installer_login FROM pg_database d WHERE datname=current_database()").fetchone()
                    version = connection.execute("SELECT default_version FROM pg_available_extensions WHERE name='vector'").fetchone()
                require(170000 <= row["version_num"] < 180000 and version["default_version"] == "0.8.6", "pg_or_vector_version_mismatch")
                if target.get("database_identity"):require(row == target["database_identity"], "database_identity_changed")
                target["database_identity"] = row
                self.write_install_config(slot); self.save()
                self.evidence(slot + "-running-identity-" + str(target["starts"]) + ".json", {"container": self.inspect(slot), "database": row, "vector": version})
                break
            except psycopg.Error:
                require(time.monotonic() < deadline, "pg_not_ready")
                time.sleep(.3)

    def stop_pg(self, slot):
        target = self.state["slots"][slot]
        observed = self.inspect(slot)
        if observed["state"]["Running"]:self.command([str(self.docker), "stop", "--time", "5", target["cid"]], timeout=30)
        after = self.inspect(slot)
        require(not after["state"]["Running"], "pg_stop_unconfirmed")
        if target.get("holding"):
            interval = self.state["pg_intervals"][target["holding"] - 1]
            interval.update(seconds=time.time() - interval["start_epoch"], stopped=utc(), docker_state=after["state"])
            target["holding"] = None
        target["stop_observations"] = target.get("stop_observations", 0) + 1
        self.save(); self.evidence(slot + "-stop-observation-" + str(target["stop_observations"]) + ".json", after)

    def write_install_config(self, slot):
        target, home = self.state["slots"][slot], PRIVATE / slot
        config = json.loads((ROOT / "config/normal-install.example.json").read_text(encoding="utf-8"))
        config.update(enabled=True, identities=target["identities"], roles={"business_login": SLOTS[slot]["business"], "snapshot_login": SLOTS[slot]["snapshot"]})
        config["target"].update(port=target["port"], database=SLOTS[slot]["database"], installer_login=target["bootstrap"],
            system_identifier=target["database_identity"]["system_identifier"], database_oid=target["database_identity"]["database_oid"])
        path = home / "config/install.json"
        raw = (json.dumps(config, indent=2) + "\n").encode()
        if path.exists():require(path.read_bytes() == raw, "install_config_drift")
        else:path.write_bytes(raw)

    def installer(self, slot, name, *, action="apply", config=None, receipt=None, inject=False, expected=0, only_admin=False):
        self.guard()
        home = PRIVATE / slot
        config = config or home / "config/install.json"
        receipt = receipt or home / "receipts" / ("task128-c01-" + name + ".jsonl")
        trace = self.run / (slot + "-" + name + "-trace.jsonl")
        native = json.loads(config.read_text(encoding="utf-8"))
        environment = dict(self.env)
        for key, value in self.secrets_for(slot).items():
            if not only_admin or key == "installer_password":environment[native["credential_env"][key]] = value
        args = [str(ROOT / "backend/.venv/Scripts/python.exe"), "-I", "-S", "-B", str(E / "install-observer.py"),
                "--slot", slot, "--action", action, "--config", str(config), "--receipt", str(receipt), "--trace", str(trace)]
        if inject:args.append("--inject-002")
        result = self.command(args, env=environment, timeout=120, allow_failure=True)
        require(result["exit_code"] == expected, "unexpected_install_cli_status_" + name)
        rows = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
        output = json.loads(result["stdout"].strip())
        require(any(row["kind"] == "formal_cli_finished" for row in rows), "installer_trace_incomplete")
        if receipt.exists():(self.run / (slot + "-" + name + "-receipt.jsonl")).write_bytes(receipt.read_bytes())
        return output, rows, receipt

    def database_facts(self, slot):
        with self.connection(slot) as connection:
            tables = connection.execute("SELECT c.relname,c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' ORDER BY c.relname").fetchall()
            counts = {row["relname"]: connection.execute(sql.SQL("SELECT count(*) AS n FROM public.{}").format(sql.Identifier(row["relname"]))).fetchone()["n"] for row in tables if row["relname"] != "data_control"}
        return {"tables": tables, "counts_excluding_control": counts}

    def check1(self):
        slot, home = "source", PRIVATE / "source"
        original = json.loads((home / "config/install.json").read_text())
        observations = []
        for key in ("database_oid", "system_identifier"):
            config = json.loads(json.dumps(original))
            value = int(config["target"][key]) + 1
            config["target"][key] = str(value) if key == "system_identifier" else value
            path = home / "config" / ("task128-c01-wrong-" + key + ".json"); path.write_text(json.dumps(config), encoding="utf-8")
            output, trace, receipt = self.installer(slot, "wrong-" + key, config=path, expected=2)
            require(output["reason"] == "target_identity_mismatch" and trace[-1]["write_requests"] == 0, "wrong_identity_not_distinguished")
            observations.append({"case": key, "output": output, "writes": trace[-1]["write_requests"]})
        with self.connection(slot) as connection:
            require(connection.execute("SELECT to_regclass('public.retrolume_install_probe_nonempty') AS t").fetchone()["t"] is None, "probe_already_exists")
            connection.execute("CREATE TABLE public.retrolume_install_probe_nonempty(id integer)")
            oid = connection.execute("SELECT 'public.retrolume_install_probe_nonempty'::regclass::oid AS oid").fetchone()["oid"]
        output, trace, receipt = self.installer(slot, "nonempty", expected=2)
        require(output["reason"] == "target_not_empty_or_exclusive" and trace[-1]["write_requests"] == 0, "nonempty_probe_not_distinguished")
        with self.connection(slot) as connection:
            with connection.transaction():
                connection.execute("LOCK TABLE public.retrolume_install_probe_nonempty IN ACCESS EXCLUSIVE MODE")
                require(connection.execute("SELECT 'public.retrolume_install_probe_nonempty'::regclass::oid AS oid").fetchone()["oid"] == oid, "probe_oid_changed")
                connection.execute("DROP TABLE public.retrolume_install_probe_nonempty")
        observations.append({"case": "nonempty", "created_and_dropped_exact_oid": oid, "output": output})
        with self.connection(slot) as connection:
            require(not connection.execute("SELECT oid FROM pg_roles WHERE rolname='retrolume_data_app'").fetchall(), "collision_probe_already_exists")
            connection.execute("CREATE ROLE retrolume_data_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS")
            oid = connection.execute("SELECT oid FROM pg_roles WHERE rolname='retrolume_data_app'").fetchone()["oid"]
        output, trace, receipt = self.installer(slot, "role-collision", expected=2)
        require(output["reason"] == "global_role_collision" and trace[-1]["write_requests"] == 0, "role_collision_not_distinguished")
        with self.connection(slot) as connection:
            with connection.transaction():
                require(connection.execute("SELECT oid FROM pg_roles WHERE rolname='retrolume_data_app'").fetchone()["oid"] == oid, "collision_probe_oid_changed")
                connection.execute("DROP ROLE retrolume_data_app")
        observations.append({"case": "role_collision", "created_and_dropped_exact_oid": oid, "output": output})
        require(not self.database_facts(slot)["tables"], "source_not_empty_after_exact_probe_cleanup")
        self.evidence("check1.json", observations)

    def check2(self):
        require(not self.state["slots"]["source"].get("install_attempted"), "source_install_no_replay")
        self.state["slots"]["source"]["install_attempted"] = True; self.save()
        output, trace, receipt = self.installer("source", "success")
        rows = [json.loads(line) for line in receipt.read_text().splitlines()]
        require(len(rows) == 37 and rows[-1]["event"] == "complete" and output["status"] == "installed", "source_receipt_not_complete")
        boundaries = [row for row in trace if row["kind"] == "control_observed_after_real_commit"]
        for boundary, profile in (("normal_control", "data_exit.v1.r01"), ("014", "data_exit.v1.r02"), ("015", "data_exit.v1.r03")):
            require(any(row["boundary"] == boundary and row["control"] and row["control"]["schema_profile"] == profile and row["control"]["mode"] == "normal" for row in boundaries), "missing_real_profile_boundary")
        self.state["slots"]["source"]["successful_receipt"] = str(receipt)
        self.state["slots"]["source"]["successful_receipt_sha256"] = digest(receipt.read_bytes())
        self.evidence("check2.json", {"output": output, "receipt_lines": len(rows), "profile_boundaries": boundaries})

    def check3(self):
        observations = []
        for purpose in ("business", "snapshot"):
            with self.connection("source", purpose) as connection:
                roles = connection.execute(ROLE_CAPABILITIES).fetchall()
                members = connection.execute(MEMBERSHIPS).fetchall()
                audited = check_role_capabilities(roles, members, "data_exit.v1.r03")
                actual = connection.execute("SELECT current_user,session_user,pg_backend_pid() AS pid,has_column_privilege(current_user,'public.data_control','maintenance_key_sha256','SELECT') AS reads_maintenance,has_table_privilege(current_user,'public.activities','INSERT') AS inserts_activity").fetchone()
                require(actual["current_user"] == actual["session_user"] == SLOTS["source"][purpose] and not actual["reads_maintenance"], "login_or_maintenance_privilege_mismatch")
                if purpose == "snapshot":require(not actual["inserts_activity"], "snapshot_has_write")
                control = connection.execute("SELECT * FROM public.data_export_control_v1").fetchone()
                refusals = []
                statements = ["SET ROLE retrolume_data_owner"]
                if purpose == "snapshot":statements += ["SET ROLE retrolume_data_app", "SELECT maintenance_key_sha256 FROM public.data_control", "INSERT INTO public.activities DEFAULT VALUES"]
                for statement in statements:
                    connection.execute("BEGIN")
                    try:
                        connection.execute(statement)
                        raise RuntimeError("expected_permission_rejection_missing")
                    except psycopg.Error as error:
                        require(error.sqlstate == "42501", "unexpected_permission_error")
                        refusals.append({"operation": statement.split()[0], "sqlstate": error.sqlstate})
                    finally:connection.execute("ROLLBACK")
                project_roles = [row for row in roles if row["rolname"].startswith("retrolume_")]
                ids = {row["oid"] for row in project_roles}
                observations.append({"purpose": purpose, "actual_login": actual, "control": dict(control), "roles": project_roles,
                    "memberships": [row for row in members if row["member"] in ids or row["roleid"] in ids], "audited": audited, "actual_refusals": refusals})
        self.evidence("check3.json", observations)

    def api_environment(self):
        target, home = self.state["slots"]["source"], PRIVATE / "source"
        secret = self.secrets_for("source")
        for name in ("activity", "integration", "q-approval"):
            destination = home / "config" / (name + ".json")
            raw = (ROOT / "config" / (name + ".example.json")).read_bytes()
            if destination.exists():require(destination.read_bytes() == raw, "closed_config_drift")
            else:destination.write_bytes(raw)
        data_profile = {"enabled": True, "snapshot_url_env": "RETROLUME_NORMAL_SNAPSHOT_URL", "maintenance_key_env": "RETROLUME_NORMAL_MAINTENANCE_KEY", "factory": None}
        (home / "config/data-exit.json").write_text(json.dumps(data_profile), encoding="utf-8")
        environment = dict(self.env, RETROLUME_DATA_DIR=str(home / "data"), RETROLUME_BACKUP_DIR=str(home / "backup"),
            RETROLUME_CONTROL_ROOT=str(home / "control"), RETROLUME_RESTORE_ROOT=str(home / "restore"),
            RETROLUME_ACTIVITY_CONFIG=str(home / "config/activity.json"), RETROLUME_INTEGRATION_CONFIG=str(home / "config/integration.json"),
            RETROLUME_Q_APPROVAL_CONFIG=str(home / "config/q-approval.json"), RETROLUME_DATA_EXIT_CONFIG=str(home / "config/data-exit.json"),
            RETROLUME_NORMAL_MAINTENANCE_KEY=secret["maintenance_key"])
        for purpose, key in (("business", "RETROLUME_DATABASE_URL"), ("snapshot", "RETROLUME_NORMAL_SNAPSHOT_URL")):
            kwargs = self.pg_kwargs("source", purpose); kwargs.pop("row_factory"); kwargs.pop("autocommit")
            kwargs["application_name"] = "retrolume-task127-api" if purpose == "business" else "retrolume-task127-snapshot"
            value = make_conninfo(**kwargs); self.redactions.append(value); environment[key] = value
        return environment

    def http_json(self, path, token=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.state["api_port"], timeout=10)
        try:
            connection.request("GET", path, headers={"x-retrolume-session": token} if token else {})
            response = connection.getresponse(); raw = response.read(1048577)
            require(response.status == 200 and len(raw) <= 1048576, "native_api_response_not_ready")
            return json.loads(raw)
        finally:connection.close()

    def api_once(self, index):
        self.guard(startup=True)
        require(self.state["api_starts"] < 3, "api_start_cap")
        target = self.state["slots"]["source"]
        before = self.database_facts("source")
        if not self.state.get("api_port"):self.state["api_port"] = self.choose_port([18122, 18124, 18126], "api")
        self.state["api_starts"] += 1
        self.save()
        args = [str(ROOT / "backend/.venv/Scripts/python.exe"), "-B", str(ROOT / "deploy/start_local.py"),
                "--container", SLOTS["source"]["name"], "--port", str(self.state["api_port"]), "--shutdown-stdin"]
        interval = {"start_epoch": time.time(), "start_requested": utc(), "args": args}
        self.state["api_intervals"].append(interval); self.save()
        login_stop, login_observations = threading.Event(), []
        def observe_login():
            try:
                with self.connection("source") as observer:
                    while not login_stop.is_set():
                        rows = observer.execute("SELECT pid,usename,application_name,client_addr::text,datname FROM pg_stat_activity WHERE application_name='retrolume-task127-api' AND datname=current_database()").fetchall()
                        for row in rows:
                            if row not in login_observations:login_observations.append(row)
                        login_stop.wait(.025)
            except Exception:
                login_observations.append({"observation_error": True})
        login_thread = threading.Thread(target=observe_login, daemon=True); login_thread.start()
        process = subprocess.Popen(args, cwd=ROOT, env=self.api_environment(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
        self.active_api = process
        parent_ref = WIN.ProcessRef(process.pid)
        self.api_refs = [parent_ref]
        interval.update(pid=process.pid, birth=parent_ref.birth)
        self.save()
        output = bytearray()
        def drain():
            while True:
                chunk = process.stdout.read(4096)
                if not chunk:break
                if len(output) < 2097152:output.extend(chunk[:2097152 - len(output)])
        drain_thread = threading.Thread(target=drain, daemon=True); drain_thread.start()
        try:
            deadline = time.monotonic() + 45
            while True:
                self.guard()
                require(process.poll() is None, "native_launcher_exited_early")
                try:
                    session = self.http_json("/api/session")
                    break
                except (OSError, RuntimeError):
                    require(time.monotonic() < deadline, "native_api_ready_timeout")
                    time.sleep(.3)
            self.redactions.append(session["token"])
            child_pids = WIN.descendants(process.pid)
            require(child_pids, "native_api_child_not_observed")
            self.api_refs += [WIN.ProcessRef(pid) for pid in child_pids]
            interval["processes"] = [{"pid": ref.pid, "birth": ref.birth} for ref in self.api_refs]; self.save()
            listeners = WIN.port_owners({self.state["api_port"]})
            require(any(row["state"] == 2 and row["pid"] in child_pids for row in listeners), "api_listener_not_owned")
            activities = self.http_json("/api/activities/capabilities", session["token"])
            data = self.http_json("/api/data/capabilities", session["token"])
            require(activities["storage_ready"] and not activities["continue"]["available"], "native_storage_or_outbound_gate")
            require(not activities["q_approval"]["available"] and not activities["q_approval"]["real_outbound_authorized"], "q_not_closed")
            require(data["current_mode"] == "normal" and data["dataset_id"] == target["identities"]["dataset_id"] and data["instance_id"] == target["identities"]["instance_id"], "native_normal_binding_mismatch")
            from app.data_exit.control import ControlHub
            hub = ControlHub(PRIVATE / "source/control")
            hub_state = hub.state()
            require(hub_state["selection"] is None and hub_state["source"]["originals_root_id"] == target["identities"]["originals_root_id"], "native_control_binding_mismatch")
            if target.get("control_id"):require(target["control_id"] == hub.control_id, "control_identity_changed")
            target["control_id"] = hub.control_id
            binding = json.loads((PRIVATE / "source/data/originals/.reference.binding.json").read_text())
            require(binding["root_id"] == target["identities"]["originals_root_id"], "native_originals_binding_mismatch")
            require(any(row.get("usename") == SLOTS["source"]["business"] for row in login_observations), "native_business_login_not_actually_observed")
            require([WIN.file_identity(Path(row["path"])) for row in target["roots"]] == target["roots"], "native_roots_changed")
            self.evidence("api-" + str(index) + "-observations.json", {"capabilities": activities, "data": data, "control_id": hub.control_id,
                "source": hub_state["source"], "binding": binding, "listener": listeners, "processes": [{"pid": ref.pid, "birth": ref.birth} for ref in self.api_refs],
                "actual_pg_stat_activity": login_observations, "pg_already_started_by_controller": True, "admin_environment_inherited": False})
        finally:
            if process.poll() is None:
                try:process.stdin.write(b"stop\n"); process.stdin.flush()
                except (OSError, ValueError):pass
            try:process.wait(timeout=220)
            except subprocess.TimeoutExpired:
                for ref in reversed(self.api_refs):ref.stop()
                process.wait(timeout=10)
            drain_thread.join(timeout=3)
            login_stop.set(); login_thread.join(timeout=5)
            interval.update(seconds=time.time() - interval["start_epoch"], stopped=utc(), exit_code=process.returncode)
            status = [{"pid": ref.pid, "birth": ref.birth, "exited": not ref.alive()} for ref in self.api_refs]
            require(all(ref["exited"] for ref in status), "api_tree_stop_unconfirmed")
            for ref in self.api_refs:ref.close()
            self.api_refs = []; self.active_api = None
            listeners_after = WIN.port_owners({self.state["api_port"]})
            self.evidence("api-" + str(index) + "-output.json", {"output": output.decode("utf-8", errors="replace"), "stop_proof": status,
                "listener_after": listeners_after, "interval": interval, "login_observations": login_observations})
            self.save()
            require(not any(row["state"] == 2 for row in listeners_after), "api_listener_stop_unconfirmed")
            require(process.returncode == 0, "native_shutdown_not_clean")
        require(self.database_facts("source") == before, "business_data_changed_by_native_reopen")
        self.state.setdefault("api_completed", []).append(index); self.save()

    def check4(self):
        for index in (1, 2):
            if index in self.state.get("api_completed", []):continue
            if not self.inspect("source")["state"]["Running"]:self.start_pg("source")
            self.api_once(index)
        self.stop_pg("source")

    def check5(self):
        self.configure_slot("interrupted"); self.start_pg("interrupted")
        require(not self.state["slots"]["interrupted"].get("install_attempted"), "interrupted_injection_no_replay")
        self.state["slots"]["interrupted"]["install_attempted"] = True; self.save()
        output, trace, receipt = self.installer("interrupted", "expected-unknown", inject=True, expected=2)
        require(output["reason"] == "commit_unknown", "planned_unknown_not_observed")
        rows = [json.loads(line) for line in receipt.read_text().splitlines()]
        require(rows[-1]["confirmed_stages"] == ["001"] and rows[-1]["unknown_stage"] == "002", "planned_unknown_receipt_mismatch")
        require(sum(row["kind"] == "planned_confirmation_hidden_after_real_commit" for row in trace) == 1, "expected_single_real_commit_injection_missing")
        facts = self.database_facts("interrupted")
        names = {row["relname"] for row in facts["tables"]}
        require("activities" in names and "pdf_review_candidates" not in names and "data_control" not in names, "interrupted_real_boundary_mismatch")
        for action, reason in (("apply", "output_exists"), ("verify", "receipt_incomplete")):
            value, observed, unused = self.installer("interrupted", "same-partial-" + action, action=action, receipt=receipt, expected=2, only_admin=action == "verify")
            require(value["reason"] == reason and observed[-1]["connections"] == 0, "partial_reuse_not_local_rejection")
        value, observed, unused = self.installer("interrupted", "new-receipt-partial", expected=2)
        require(value["reason"] == "target_not_empty_or_exclusive" and observed[-1]["write_requests"] == 0, "partial_database_not_rejected")
        require(self.database_facts("interrupted") == facts, "partial_state_changed")
        self.evidence("check5.json", {"expected_unknown": output, "real_database_facts": facts, "preserved_receipt_sha256": digest(receipt.read_bytes()), "not_resumed": True})
        self.stop_pg("interrupted")

    def check6(self):
        if not self.inspect("source")["state"]["Running"]:self.start_pg("source")
        target = self.state["slots"]["source"]
        receipt = Path(target["successful_receipt"])
        before = receipt.read_bytes()
        output, trace, unused = self.installer("source", "readonly-verify", action="verify", receipt=receipt, only_admin=True)
        require(output["status"] == "readonly_rechecked" and trace[-1]["write_requests"] == 0 and receipt.read_bytes() == before, "verify_wrote_or_changed_receipt")
        config = json.loads((PRIVATE / "source/config/install.json").read_text()); config["roles"]["business_login"] = "retrolume_mismatched_receipt"
        wrong = PRIVATE / "source/config/wrong-binding.json"; wrong.write_text(json.dumps(config), encoding="utf-8")
        output2, trace2, unused = self.installer("source", "wrong-binding", action="verify", config=wrong, receipt=receipt, expected=2, only_admin=True)
        require(output2["reason"] == "receipt_mismatch" and trace2[-1]["connections"] == 0, "wrong_receipt_binding_not_local")
        self.evidence("check6.json", {"output": output, "wrong_binding": output2, "receipt_sha256_unchanged": digest(before)})
        self.stop_pg("source")

    def run_all(self):
        thread = threading.Thread(target=self.memory_watch, daemon=True); thread.start()
        def stage(key, action):
            if self.state["checks"].get(key, {}).get("status") == "passed":return True
            self.state["checks"][key] = {"status":"started", "utc":utc()};self.save()
            try:
                action()
                self.state["checks"][key] = {"status":"passed", "utc":utc()};self.save();return True
            except BaseException as error:
                self.state["checks"][key] = {"status":"failed", "error_type":type(error).__name__, "reason":str(error) if isinstance(error, RuntimeError) else "redacted_nonruntime", "utc":utc()}
                self.evidence("stage-"+key+"-failure.json",self.state["checks"][key]);self.save();return False
        def initial_preflight():
            spec = importlib.util.spec_from_file_location("real_c01_install",ROOT / "deploy/initialize_normal.py")
            install = importlib.util.module_from_spec(spec);spec.loader.exec_module(install)
            config=json.loads((PRIVATE / "source/config/install.json").read_bytes())
            with install.connect(config,self.secrets_for("source")) as connection:
                observed=install.preflight(connection,config)
            self.evidence("correct-empty-preflight.json",{"passed":True,"observed":observed})
        try:
            self.guard()
            for slot in self.state["slots"]:
                self.configure_slot(slot)
                projected=self.inspect(slot)
                require(not projected["state"]["Running"], "preexisting_running_resource")
                require(projected["created"]==self.state["slots"][slot]["created_projection"]["created"],"creation_changed")
                require(projected["mounts"]==self.state["slots"][slot]["created_projection"]["mounts"] and projected["limits"]==self.state["slots"][slot]["created_projection"]["limits"],"limits_or_mount_changed")
                require([WIN.file_identity(Path(r["path"])) for r in self.state["slots"][slot]["roots"]]==self.state["slots"][slot]["roots"],"root_entity_changed")
                for kind,identity,expected,keys in (("volume",SLOTS[slot]["volume"],self.state["slots"][slot]["volume"],("Name","CreatedAt","Driver","Labels")),("network",self.state["slots"][slot]["network_id"],self.state["slots"][slot]["network"],("Name","Id","Created","Driver","Labels"))):
                    actual=self.docker_json([kind,"inspect",identity])[0]
                    require(all(actual.get(k)==expected.get(k) for k in keys),"volume_or_network_changed")
                self.evidence(slot+"-pre-reuse-identity.json",projected)
            # A：正确预检、四拒绝、成功安装、角色、首API，同一源启动。
            self.start_pg("source")
            okay=stage("preflight",initial_preflight)
            for key,action in (("1",self.check1),("2",self.check2),("3",self.check3),("api1",lambda:self.api_once(1))):
                if okay:okay=stage(key,action)
            if okay:
                self.state["source_after_A"]={"database":self.database_facts("source"),"identity":self.state["slots"]["source"]["database_identity"],"control_id":self.state["slots"]["source"].get("control_id")};self.save()
            self.stop_pg("source")
            # B：独立唯一注入；A的失败不伪造此项结果。
            stage("5",self.check5)
            if self.state["slots"]["interrupted"].get("holding"):self.stop_pg("interrupted")
            # C：真实PG重开后第二API及只读verify；成功安装不重放。
            if okay:
                self.start_pg("source")
                require(self.database_facts("source")==self.state["source_after_A"]["database"],"source_changed_across_pg_restart")
                if stage("api2",lambda:self.api_once(2)):
                    self.state["checks"]["4"]={"status":"passed","utc":utc(),"two_api_cycles_across_pg_restart":True};self.save()
                stage("6",self.check6)
        finally:
            self.done.set()
            for slot in self.state["slots"]:
                try:self.stop_pg(slot)
                except Exception as error:self.state["stop_unknown"] = type(error).__name__
            thread.join(timeout=5)
            self.state["last_entry"].update(status="returned",finished=utc(),controller_wall_seconds=time.monotonic()-self.entry_clock)
            self.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--reason", default="本机Docker引擎恢复后续尚未开始的六项")
    args = parser.parse_args()
    if not args.execute:
        print("未执行；必须先核Docker恢复及当前原许可，再显式--execute。")
        return
    controller = Controller(args.reason)
    controller.run_all()
    print(json.dumps({"entry": controller.entry, "checks": controller.state["checks"], "starts": {key: value["starts"] for key, value in controller.state["slots"].items()}, "api_starts": controller.state["api_starts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
