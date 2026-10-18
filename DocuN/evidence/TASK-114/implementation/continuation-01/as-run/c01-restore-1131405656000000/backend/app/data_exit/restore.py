"""只接受可信 host profile 的独立集群工厂和永久只读恢复。"""
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import time
from uuid import uuid4
from .codec import decode_row, lines, load_json, plain, TRANSFORMS
from .contracts import DataError, DataJobCommand, Limits, PROFILE, TABLES, canonical, digest, uuid
from .control import CredentialVault
from .files import safe_root, regular, RootLease
from .packages import PackageReader, hash_file
from .schema import MIGRATIONS


@dataclass(frozen=True)
class TargetRef:
    target_id: str
    job_id: str
    profile_id: str
    cid: str
    name: str
    volume: str
    port: int
    dataset_id: str
    instance_id: str
    root_id: str
    data_root: Path


def docker_call(arguments, *, environment=None, timeout=30):
    try:
        result = subprocess.run(["docker", *arguments], env=environment, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise DataError("restore_executor_missing", 503) from None
    if result.returncode:
        # Docker stderr 可能包含私有路径或配置值，公开面仅固定错误码。
        raise DataError("restore_resource_failed", 503)
    return result.stdout.decode("utf-8").strip()


def inspect_target(target, image_id):
    full = json.loads(docker_call(["inspect", target.cid]))
    if len(full) != 1: raise DataError("target_identity_unknown", 503)
    value = full[0]
    mount = value.get("Mounts", [])
    host = value["HostConfig"]
    ports = host.get("PortBindings", {})
    labels = value["Config"].get("Labels", {})
    if (value["Id"] != target.cid or value["Name"] != "/" + target.name or value["Image"] != image_id
        or host["Privileged"] or host["NetworkMode"] in ("host", "none") or host["RestartPolicy"]["Name"] != "no"
        or host["Memory"] != 512 * 1024**2 or host["NanoCpus"] != 10**9 or host["PidsLimit"] != 128
        or len(mount) != 1 or mount[0]["Type"] != "volume" or mount[0]["Name"] != target.volume
        or mount[0]["Destination"] != "/var/lib/postgresql/data" or not mount[0]["RW"]
        or ports != {"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(target.port)}]}
        or labels.get("retrolume.data.job") != target.job_id):
        raise DataError("target_identity_unknown", 503)
    return {"cid": target.cid, "name": target.name, "image_id": value["Image"], "volume": target.volume,
            "port": target.port, "running": value["State"]["Running"], "status": value["State"]["Status"],
            "labels": labels, "created": value["Created"]}


class TargetFactory:
    def __init__(self, hub, restore_root, profile, *, hooks=None, limits=None):
        self.hub, self.root, self.profile = hub, safe_root(restore_root), profile
        self.hooks, self.limits, self.vault = hooks, limits or Limits(), CredentialVault(hub)
        if (not isinstance(profile, dict) or re.fullmatch(r"sha256:[0-9a-f]{64}", profile.get("image_id", "")) is None
            or not re.fullmatch(r"[a-z][a-z0-9_]{1,40}", profile.get("login_prefix", ""))
            or not isinstance(profile.get("slots"), list) or not 1 <= len(profile["slots"]) <= 8):
            raise DataError("restore_executor_missing", 503)
        for slot in profile["slots"]:
            if (set(slot) != {"id", "name", "volume", "port", "database"} or not re.fullmatch(r"[a-z0-9-]{1,100}", slot["name"])
                or slot["volume"] != slot["name"] + "-data" or type(slot["port"]) is not int or not 1024 <= slot["port"] <= 65535):
                raise DataError("restore_executor_missing", 503)
        self._ephemeral = {}

    def _hook(self, name, *args):
        if self.hooks is not None: getattr(self.hooks, name)(*args)

    def allocate(self, job_id, accepted_profile_id):
        if accepted_profile_id != self.profile["id"]: raise DataError("restore_executor_missing", 503)
        state = self.hub.state()
        used = {v["slot_id"] for v in state["targets"].values()}
        slot = next((v for v in self.profile["slots"] if v["id"] not in used), None)
        if slot is None: raise DataError("capacity_exceeded", 413)
        target_id, dataset_id, instance_id, root_id = (str(uuid4()) for _ in range(4))
        intent = {"target_id": target_id, "job_id": uuid(job_id), "slot_id": slot["id"], "profile_id": accepted_profile_id,
                  "state": "allocating", "dataset_id": dataset_id, "instance_id": instance_id, "root_id": root_id}
        # 名字、卷、端口碰撞停止此 slot，不改名或清理旧对象绕过。
        if docker_call(["ps", "-aq", "--filter", "name=^/" + slot["name"] + "$"]): raise DataError("target_collision", 503)
        volumes = docker_call(["volume", "ls", "--format", "{{.Name}}"])
        if slot["volume"] in volumes.splitlines(): raise DataError("target_collision", 503)
        with socket.socket() as probe:
            try: probe.bind(("127.0.0.1", slot["port"]))
            except OSError: raise DataError("target_collision", 503) from None
        image = json.loads(docker_call(["image", "inspect", self.profile["image_id"]]))[0]
        if image["Id"] != self.profile["image_id"] or image["Os"] != "linux" or image["Architecture"] != "amd64":
            raise DataError("target_identity_unknown", 503)
        self._hook("before_create", slot)
        # 先完成host准入/内存门，再持久登记意图；仍先于实际资源创建。
        self.hub.commit("target.register", intent)
        prefix = self.profile["login_prefix"]
        credentials = {"admin_password": secrets.token_urlsafe(32), "loader_password": secrets.token_urlsafe(32),
                       "readonly_password": secrets.token_urlsafe(32), "snapshot_password": secrets.token_urlsafe(32),
                       "maintenance_key": secrets.token_hex(32)}
        environment = dict(os.environ)
        environment.update(POSTGRES_USER=prefix + "admin", POSTGRES_PASSWORD=credentials["admin_password"], POSTGRES_DB=slot["database"])
        cid = docker_call(["create", "--name", slot["name"], "--label", "retrolume.data.job=" + job_id,
                           "--label", "retrolume.data.profile=" + accepted_profile_id,
                           "--cpus", "1", "--memory", "512m", "--pids-limit", "128", "--restart", "no",
                           "--publish", f"127.0.0.1:{slot['port']}:5432", "--mount", f"type=volume,src={slot['volume']},dst=/var/lib/postgresql/data",
                           "--env", "POSTGRES_USER", "--env", "POSTGRES_PASSWORD", "--env", "POSTGRES_DB", self.profile["image_id"]], environment=environment)
        if re.fullmatch(r"[0-9a-f]{64}", cid) is None: raise DataError("target_identity_unknown", 503)
        data_root = self.root / job_id
        target = TargetRef(target_id, job_id, accepted_profile_id, cid, slot["name"], slot["volume"], slot["port"], dataset_id, instance_id, root_id, data_root)
        identity = inspect_target(target, self.profile["image_id"])
        self._hook("created", target, identity)
        self.hub.commit("target.register", {**intent, "state": "allocated", "cid": cid, "name": target.name,
                                          "volume": target.volume, "port": target.port, "database": slot["database"]})
        self._ephemeral[target_id] = credentials
        try:
            safe_root(self.root)
            data_root.mkdir()
            originals = data_root / "originals"; originals.mkdir()
            self.start(target)
            from psycopg.conninfo import make_conninfo
            credentials["admin_dsn"] = make_conninfo(host="127.0.0.1", port=target.port, dbname=slot["database"], user=prefix + "admin", password=credentials["admin_password"])
            self._wait_pg(credentials["admin_dsn"])
            self._initialize(target, credentials, slot)
            return target
        except BaseException:
            self.abandon(target)
            self.stop(target)
            raise

    def abandon(self,target):
        """失败目标失去临时加载身份；未知撤销仍记录失败，目标不再使用。"""
        credentials=self._ephemeral.pop(target.target_id,None)
        revoked=False
        if credentials and credentials.get('admin_dsn'):
            try:
                import psycopg
                from psycopg import sql
                with psycopg.connect(credentials['admin_dsn'],connect_timeout=3) as connection:
                    for suffix in ('loader','admin'):
                        connection.execute(sql.SQL('ALTER ROLE {} NOLOGIN PASSWORD NULL').format(sql.Identifier(self.profile['login_prefix']+suffix)))
                    connection.execute(sql.SQL('REVOKE retrolume_data_restore_loader FROM {}').format(sql.Identifier(self.profile['login_prefix']+'loader')))
                revoked=True
            except Exception:pass
        self.hub.commit('target.register',{'target_id':target.target_id,'state':'failed','temporary_credentials_revoked':revoked})

    def start(self, target):
        identity = inspect_target(target, self.profile["image_id"])
        if identity["running"]: return
        running = docker_call(["ps", "--format", "{{.Names}}"])
        own_names = {v["name"] for v in self.profile["slots"]} | {self.profile.get("source_name", "")}
        if len(set(running.splitlines()) & own_names) >= 2: raise DataError("resource_concurrency_exceeded", 503)
        self._hook("before_start", target)
        docker_call(["start", target.cid])
        identity = inspect_target(target, self.profile["image_id"])
        self._hook("started", target, identity)

    def stop(self, target):
        identity = inspect_target(target, self.profile["image_id"])
        if identity["running"]:
            docker_call(["stop", "--time", "10", target.cid], timeout=20)
        identity = inspect_target(target, self.profile["image_id"])
        if identity["running"] or identity["status"] not in ("exited", "created"): raise DataError("target_stop_unknown", 503)
        self._hook("stopped", target, identity)

    @staticmethod
    def _wait_pg(dsn):
        import psycopg
        end = time.monotonic() + 30
        while True:
            try:
                with psycopg.connect(dsn, connect_timeout=1): return
            except psycopg.Error:
                if time.monotonic() >= end: raise DataError("restore_resource_failed", 503) from None
                time.sleep(0.1)

    def _initialize(self, target, credentials, slot):
        import psycopg
        from psycopg import sql
        from psycopg.conninfo import make_conninfo
        prefix = self.profile["login_prefix"]
        with psycopg.connect(credentials["admin_dsn"], autocommit=True, connect_timeout=3) as connection:
            if connection.execute("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r'").fetchone()[0] != 0:
                raise DataError("target_not_empty", 503)
            directory = Path(__file__).resolve().parents[2] / "migrations"
            chain = {}
            for path in sorted(directory.glob("*.sql")):
                if not 1 <= int(path.name[:3]) <= 13: continue
                sha = digest(path.read_bytes()); chain[path.name] = sha
                from .schema import MIGRATION_013
                if sha != (MIGRATION_013 if int(path.name[:3])==13 else MIGRATIONS.get(path.name)): raise DataError("trusted_schema_changed", 503)
                connection.execute(path.read_text(encoding="utf-8-sig"))
            if len(chain) != 13: raise DataError("trusted_schema_changed", 503)
            version = int(connection.execute("SHOW server_version_num").fetchone()[0])
            if version // 10000 != self.profile.get("pg_major", 17): raise DataError("schema_profile_mismatch", 503)
            for name in ("loader", "readonly", "snapshot"):
                username = prefix + name
                connection.execute(sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}").format(sql.Identifier(username), sql.Literal(credentials[name + "_password"])))
                role = "retrolume_data_restore_loader" if name == "loader" else "retrolume_data_snapshot"
                connection.execute(sql.SQL("GRANT {} TO {}").format(sql.Identifier(role), sql.Identifier(username)))
                credentials[name + "_dsn"] = make_conninfo(host="127.0.0.1", port=target.port, dbname=slot["database"], user=username, password=credentials[name + "_password"])
            connection.execute("INSERT INTO public.data_control(dataset_id,instance_id,schema_profile,mode,source_snapshot_id,originals_root_id,loader_session_user,maintenance_key_sha256) VALUES(%s,%s,%s,'loading',%s,%s,%s,%s)",
                               (target.dataset_id, target.instance_id, PROFILE, target.job_id, target.root_id, prefix + "loader", digest(credentials["maintenance_key"])))
            identity = {"server_version_num": version, "migration_chain": chain, "target_id": target.target_id, "mode": "loading"}
            self.hub.commit("target.register", {"target_id": target.target_id, "schema_identity": identity})

    def loader_dsn(self, target): return self._ephemeral[target.target_id]["loader_dsn"]

    def seal_readonly(self, target, verification_sha, source_root_sha, restore_manifest_sha):
        import psycopg
        from psycopg import sql
        credentials = self._ephemeral[target.target_id]
        prefix = self.profile["login_prefix"]
        try:
            with psycopg.connect(credentials["admin_dsn"], connect_timeout=3) as connection:
                for table in TABLES:
                    # 目标内只存在失去执行权的归档占位，普通读取需要旧仓储的固定形状。
                    connection.execute(sql.SQL("GRANT SELECT ON public.{} TO retrolume_data_snapshot").format(sql.Identifier(table)))
                connection.execute("UPDATE public.data_control SET mode='restored_readonly',loader_session_user=NULL,source_root_sha256=%s,restore_manifest_sha256=%s WHERE dataset_id=%s AND instance_id=%s AND mode='loading'",
                                   (source_root_sha, restore_manifest_sha, target.dataset_id, target.instance_id))
                connection.execute(sql.SQL("REVOKE retrolume_data_restore_loader FROM {}").format(sql.Identifier(prefix + "loader")))
                connection.execute(sql.SQL("ALTER ROLE {} NOLOGIN PASSWORD NULL").format(sql.Identifier(prefix + "loader")))
                connection.execute(sql.SQL("ALTER ROLE {} NOLOGIN PASSWORD NULL").format(sql.Identifier(prefix + "admin")))
            readonly = self._probe_readonly(credentials["readonly_dsn"], target)
            binding=target.data_root/'originals/.reference.binding.json'
            with RootLease(target.data_root/'originals').acquire(True):
                with binding.open('xb') as stream:
                    stream.write(canonical({'profile':PROFILE,'dataset_id':target.dataset_id,'instance_id':target.instance_id,
                                            'root_id':target.root_id,'mode':'restored_readonly'}).encode('utf-8'))
                    stream.flush();os.fsync(stream.fileno())
            reference = self.vault.save({"readonly_dsn": credentials["readonly_dsn"], "snapshot_dsn": credentials["snapshot_dsn"]})
            receipt = {"target_id": target.target_id, "state": "sealed", "verification_sha256": verification_sha,
                       "restore_manifest_sha256": restore_manifest_sha, "credential_ref": reference,
                       "readonly_probe": readonly}
            self.hub.commit("target.seal", receipt)
            return {"target_id": target.target_id, "state": "sealed", "verification_sha256": verification_sha}
        finally:
            self._ephemeral.pop(target.target_id, None)

    @staticmethod
    def _probe_readonly(dsn, target):
        import psycopg
        with psycopg.connect(dsn, connect_timeout=3) as connection:
            state = connection.execute("SELECT dataset_id,source_instance_observed,mode_observed FROM public.data_export_control_v1").fetchone()
            if tuple(map(str, state)) != (target.dataset_id, target.instance_id, "restored_readonly"):
                raise DataError("target_seal_unconfirmed", 503)
            for table in TABLES: connection.execute("SELECT count(*) FROM public." + table).fetchone()
            for view in ("data_export_control_v1", "data_export_job_history_v1", "data_export_tombstones_v1"):
                connection.execute("SELECT count(*) FROM public." + view).fetchone()
        rejected = []
        for statement in ("DELETE FROM public.activities", "UPDATE public.material_sources SET current_version=NULL",
                          "SELECT public.html_update_preview('00000000-0000-0000-0000-000000000001','x','stopped',NULL,NULL,NULL,0)"):
            try:
                with psycopg.connect(dsn, connect_timeout=3) as connection: connection.execute(statement)
            except psycopg.Error as error:
                if error.sqlstate != "42501": raise DataError("target_seal_unconfirmed", 503) from None
                rejected.append(error.sqlstate)
            else: raise DataError("target_seal_unconfirmed", 503)
        return {"reads": 31, "writes_rejected": rejected}

    def target(self, target_id):
        value = self.hub.state()["targets"].get(uuid(target_id))
        if value is None or value.get("state") != "sealed": raise DataError("target_not_verified")
        return TargetRef(value["target_id"], value["job_id"], value["profile_id"], value["cid"], value["name"], value["volume"],
                         value["port"], value["dataset_id"], value["instance_id"], value["root_id"], self.root / value["job_id"])

    def readonly_credentials(self, target_id):
        value = self.hub.state()["targets"][uuid(target_id)]
        if value.get("state") != "sealed": raise DataError("target_not_verified")
        return self.vault.read(value["credential_ref"])


class RestoreController:
    def __init__(self, hub, incoming_root, factory, source, maintenance, *, rebind=None, limits=None):
        self.hub, self.incoming, self.factory = hub, safe_root(incoming_root), factory
        self.source, self.maintenance, self.rebind, self.limits = source, maintenance, rebind, limits or Limits()

    def prepare(self, upload_id, deletion_policy, origin_context):
        if deletion_policy not in ("respect_current_deletions", "snapshot_only_readonly"): raise DataError("invalid_input", 400)
        path = self.incoming / (uuid(upload_id) + ".rldata")
        with PackageReader(path, self.limits) as reader:
            if not reader.manifest["restore_eligible"]: raise DataError("restore_not_supported")
            package_sha, count = hash_file(path, self.limits.package_bytes)
            snapshot_tombs = list(lines(reader.archive.open("metadata/tombstones.jsonl"), self.limits))
            latest = self.source.latest() if self.source is not None else {"status": "unknown", "tombstones": []}
            registered=self.hub.state()['source']
            source_dataset=registered['dataset_id'] if registered is not None else origin_context.dataset_id
            same_lineage = reader.manifest["snapshot"]["source_dataset_id"] == source_dataset
            if latest['status']=='known' and (latest.get('source_control') is None or str(latest['source_control']['dataset_id'])!=source_dataset):
                latest={'status':'unknown','tombstones':[]}
            if not same_lineage: latest = {"status": "unknown", "tombstones": []}
            observed = list(self.hub.state()["deletions"].values()) if same_lineage else []
            overlay = snapshot_tombs + latest["tombstones"] + observed if deletion_policy == "respect_current_deletions" else snapshot_tombs
            plan_id = str(uuid4())
            plan = {"plan_id": plan_id, "upload_id": upload_id, "package_sha256": package_sha, "package_root_sha256": reader.manifest["root_sha256"],
                    "codec_profile": PROFILE, "scope": reader.manifest["scope"], "deletion_policy": deletion_policy,
                    "overlay": overlay, "latest_status": latest["status"], "origin": origin_context.public(),
                    "resource_profile_id": self.factory.profile["id"] if self.factory is not None else None,
                    "permanent_readonly": True, "bytes": str(count)}
            raw = canonical(plan).encode("utf-8")
            sha = self.hub.save_artifact("plans", plan_id, raw)
            public = {k: plan[k] for k in ("plan_id", "package_root_sha256", "codec_profile", "scope", "deletion_policy", "latest_status", "permanent_readonly", "bytes")}
            public.update(plan_sha256=sha, overlay_count=len(overlay), executor_configured=self.factory is not None)
            self.hub.commit("plan.create", {"plan_id": plan_id, "plan_sha256": sha, "public": public})
            return public

    def plan(self, plan_id, expected_sha):
        record = self.hub.state()["plans"].get(uuid(plan_id))
        if record is None: raise DataError("not_found", 404)
        if record["plan_sha256"] != expected_sha: raise DataError("plan_changed")
        return load_json(self.hub.read_artifact("plans", plan_id, expected_sha))

    def verify(self, job_id, expected_plan_sha):
        if self.factory is None: raise DataError("restore_executor_missing", 503)
        job = self.hub.state()["jobs"].get(uuid(job_id))
        if job is None or job["kind"] != "restore": raise DataError("not_found", 404)
        if job["state"] != "prepared": return self.hub.reconcile(job_id)
        plan = self.plan(job["scope"]["plan_id"], expected_plan_sha)
        target = None
        with self.hub.operation_lock.acquire(True, timeout=1):
            try:
                self.hub.update_job(job_id, job["revision"], state="running", stage="allocating", plan_id=plan["plan_id"], latest_status=plan["latest_status"])
                target = self.factory.allocate(job_id, plan["resource_profile_id"])
                path = self.incoming / (plan["upload_id"] + ".rldata")
                if hash_file(path, self.limits.package_bytes)[0] != plan["package_sha256"]: raise DataError("integrity_failed", 422)
                with PackageReader(path, self.limits) as reader:
                    proof = self._load(reader, target, plan)
                raw = canonical(proof).encode("utf-8")
                proof_sha = self.hub.save_artifact("receipts", job_id, raw)
                self.factory.seal_readonly(target, proof_sha, plan["package_root_sha256"], proof_sha)
                current = self.hub.get(job_id)
                return self.hub.update_job(job_id, current["revision"], state="verified", stage="verified",
                                           target_id=target.target_id, root_sha256=plan["package_root_sha256"], counts=proof["counts"])
            except BaseException as error:
                if target is not None:self.factory.abandon(target)
                current = self.hub.get(job_id)
                if current['state']!='cancelled':
                    self.hub.update_job(job_id, current["revision"], state="failed", stage="failed",
                                        error_code=error.code if isinstance(error, DataError) else "restore_failed")
                raise
            finally:
                if target is not None: self.factory.stop(target)

    def _load(self, reader, target, plan):
        import psycopg
        from psycopg import sql
        from psycopg.types.json import Jsonb
        from app.storage.originals import OriginalStore
        store = OriginalStore(target.data_root / "originals")
        lease = RootLease(store.root)
        from .spool import PackageRows
        started=time.monotonic()
        def bounded():
            if self.hub.get(target.job_id)['state']=='cancelled':raise DataError('operation_cancelled')
            if time.monotonic()-started>self.limits.operation_seconds:raise DataError('operation_timeout',504)
        rowset = {table:PackageRows(reader,table,bounded) for table in TABLES}
        deleted_sources = {r["entity_id"] for r in plan["overlay"] if r["entity_kind"] == "source"}
        deleted_memories = {r["entity_id"] for r in plan["overlay"] if r["entity_kind"] == "memory"}
        for head in rowset["learning_memories"]:
            if head["state"] == "revoked": deleted_memories.add(head["memory_id"])
        eligible_hashes = {r["sha256"] for r in rowset["material_versions"] if r["source_id"] not in deleted_sources}
        counts = {"files": 0, "rows": 0, "components": 0}
        with lease.acquire() as held:
            for entry in reader.manifest["contents"]:
                bounded()
                if entry["path"].startswith("originals/") and entry["path"].split("/")[1] in eligible_hashes:
                    from .reference import LoadingReferencePin,PreparedReference
                    version=next(r for r in rowset['material_versions'] if r['sha256']==entry['path'].split('/')[1] and r['source_id'] not in deleted_sources)
                    pin=LoadingReferencePin(self.factory,target,held,PreparedReference(version['source_id'],version['id'],None,version['sha256'],int(version['size'])))
                    with reader.archive.open(entry["path"]) as stream:
                        store.put(stream, max_bytes=self.limits.original_bytes,reference_pin=pin)
                    counts["files"] += 1
            for component in self._components(rowset):
                raw_bytes,count=0,0
                for values in component.values():
                    for row in values:
                        raw_bytes+=len(canonical(row).encode('utf-8'));count+=1
                        if raw_bytes>self.limits.component_bytes or count>self.limits.component_rows:raise DataError('capacity_exceeded',413)
                begin = time.monotonic()
                with psycopg.connect(self.factory.loader_dsn(target), connect_timeout=3) as connection:
                    connection.execute("SET LOCAL statement_timeout='30s'")
                    connection.execute("SET LOCAL lock_timeout='3s'")
                    connection.execute("SET CONSTRAINTS ALL DEFERRED")
                    pointers = []
                    for table in TABLES:
                        values = component.get(table, [])
                        if table in ("teaching_records", "interview_records"): values = sorted(values, key=lambda r: (r["activity_id"], r["seq"]))
                        if table in ("interview_commands", "html_commands"): values = sorted(values, key=lambda r: r["created_at"])
                        for row in values:
                            if self.hub.get(target.job_id)["state"] == "cancelled": raise DataError("operation_cancelled")
                            if table == "learning_memory_bodies" and row["memory_id"] in deleted_memories: continue
                            decoded = decode_row(table, row)
                            if table == "material_sources":
                                pointers.append((row["id"], row["current_version"]))
                                decoded["current_version"] = None
                            columns = list(decoded)
                            statement = sql.SQL("INSERT INTO public.{} ({}) VALUES ({})").format(sql.Identifier(table),
                                sql.SQL(",").join(map(sql.Identifier, columns)), sql.SQL(",").join(sql.Placeholder() for _ in columns))
                            connection.execute(statement, tuple(decoded[c] for c in columns))
                            counts["rows"] += 1
                            if time.monotonic() - begin > self.limits.component_seconds: raise DataError("operation_timeout", 504)
                    for sid, vid in pointers:
                        if vid is not None and sid not in deleted_sources:
                            connection.execute("UPDATE public.material_sources SET current_version=%s WHERE id=%s", (vid, sid))
                counts["components"] += 1
            with psycopg.connect(self.factory.loader_dsn(target), connect_timeout=3) as connection:
                for row in lines(reader.archive.open("metadata/operation_history.jsonl"), self.limits):
                    connection.execute("SELECT public.data_archive_history(%s)", (Jsonb(row),))
                for row in plan["overlay"]:
                    connection.execute("SELECT public.data_archive_tombstone(%s)", (Jsonb(row),))
        lease.close()
        with psycopg.connect(self.factory.loader_dsn(target), connect_timeout=3) as connection:
            actual = {table: connection.execute("SELECT count(*) FROM public." + table).fetchone()[0] for table in TABLES}
            for table, values in rowset.items():
                expected = len(values) if table != "learning_memory_bodies" else sum(r["memory_id"] not in deleted_memories for r in values)
                if actual[table] != expected: raise DataError("restore_rows_mismatch", 422)
            # 每个正文/额度列按 codec 回读逐字节核对，只有声明的指针和控制占位不同。
            from psycopg.rows import dict_row
            from .codec import encode_row
            from .schema import COLUMNS
            for table, values in rowset.items():
                columns = ",".join(COLUMNS[table])
                with connection.cursor(row_factory=dict_row) as cursor:
                    cursor.execute("SELECT " + columns + " FROM public." + table)
                    restored = [encode_row(table, row) for row in cursor.fetchall()]
                expected = [dict(row) for row in values if not (table == "learning_memory_bodies" and row["memory_id"] in deleted_memories)]
                if table == "material_sources":
                    for row in expected:
                        if row["id"] in deleted_sources: row["current_version"] = None
                if sorted(map(canonical, restored)) != sorted(map(canonical, expected)): raise DataError("restore_content_mismatch", 422)
        return {"profile": PROFILE, "target_id": target.target_id, "package_root_sha256": plan["package_root_sha256"],
                "counts": counts, "actual_rows": actual, "deletion_policy": plan["deletion_policy"], "latest_status": plan["latest_status"],
                "deleted_sources": sorted(deleted_sources), "deleted_memories": sorted(deleted_memories),
                "transformations": {**TRANSFORMS, "material_sources.current_version": "删除覆盖命中时 NULL；快照原值仍在包内"},
                "clock_origin": "archive_placeholder", "execution_authority": False}

    @staticmethod
    def _components(rows):
        from .spool import FilteredRows
        # 资料组件先提交；活动和记忆以真实依赖连通分量保持完整事务闭包。
        for source in rows["material_sources"]:
            sid = source["id"]
            versions = {r["id"] for r in rows["material_versions"] if r["source_id"] == sid}
            yield {"material_sources": [source], "material_versions": FilteredRows(rows['material_versions'],lambda r:r['source_id']==sid),
                   "pdf_review_candidates": FilteredRows(rows['pdf_review_candidates'],lambda r:r['source_id']==sid),
                   **{table:FilteredRows(rows[table],lambda r:r['version_id'] in versions) for table in ("pdf_extracted_pages", "pdf_review_pages", "pdf_user_supplements")}}
        parents = {}
        def find(key):
            parents.setdefault(key, key)
            root=key
            while parents[root]!=root:root=parents[root]
            while parents[key]!=key:
                previous=parents[key];parents[key]=root;key=previous
            return root
        def union(a, b): parents[find(a)] = find(b)
        for activity in rows["activities"]: find("a:" + activity["id"])
        for memory in rows["learning_memories"]: find("m:" + memory["memory_id"])
        for row in rows["activity_memory_choices"]: union("a:" + row["activity_id"], "m:" + row["memory_id"])
        for row in rows["learning_memory_dependencies"]:
            if row["origin_activity_id"]: union("m:" + row["memory_id"], "a:" + row["origin_activity_id"])
            if row["upstream_memory_id"]: union("m:" + row["memory_id"], "m:" + row["upstream_memory_id"])
        groups = {}
        for key in parents: groups.setdefault(find(key), set()).add(key)
        material_tables = {"material_sources", "material_versions", "pdf_review_candidates", "pdf_extracted_pages", "pdf_review_pages", "pdf_user_supplements"}
        for keys in groups.values():
            component = {}
            for table, values in rows.items():
                if table in material_tables: continue
                if not table.startswith('learning_memory') and table!='learning_memories':
                    component[table]=FilteredRows(values,lambda r,t=table:('a:'+(r['id'] if t=='activities' else r['activity_id'])) in keys)
                else:component[table]=FilteredRows(values,lambda r:('m:'+r['memory_id']) in keys)
            yield component

    async def activate_readonly(self, job_id, plan_sha, confirmation_key, expected_generation):
        with self.hub.operation_lock.acquire(True,timeout=1):
            return await self._activate_readonly(job_id,plan_sha,confirmation_key,expected_generation)

    async def _activate_readonly(self, job_id, plan_sha, confirmation_key, expected_generation):
        restore_job = self.hub.state()["jobs"].get(uuid(job_id))
        if restore_job is None or restore_job["state"] != "verified": raise DataError("target_not_verified")
        plan = self.plan(restore_job["scope"]["plan_id"], plan_sha)
        origin = self.maintenance.gate.context()
        command = DataJobCommand("activate", confirmation_key, {"restore_job_id": job_id, "plan_sha256": plan_sha, "expected_generation": expected_generation})
        activation = self.hub.create_or_get_job(command, origin)
        if activation["state"] != "prepared": return self.hub.reconcile(activation["job_id"])
        target = self.factory.target(restore_job["target_id"])
        lease = await self.maintenance.drain_for_readonly_switch(expected_generation, time.monotonic() + 30)
        try:
            latest = self.source.latest()
            if plan['deletion_policy']=='respect_current_deletions':
                if latest['status']!='known':raise DataError('deletion_history_unknown')
                covered={(r['entity_kind'],r['entity_id'],r['effective_revision']) for r in plan['overlay']}
                if any((r['entity_kind'],r['entity_id'],r['effective_revision']) not in covered for r in latest['tombstones']):
                    raise DataError('plan_changed')
            sidecar_id = str(uuid4())
            sha = self.hub.save_artifact("overlays", sidecar_id, canonical(latest).encode("utf-8"))
            self.factory.start(target)
            credentials = self.factory.readonly_credentials(target.target_id)
            self.factory._wait_pg(credentials["readonly_dsn"])
            self.factory._probe_readonly(credentials["readonly_dsn"], target)
            selection = {"generation": expected_generation + 1, "target_id": target.target_id, "dataset_id": target.dataset_id,
                         "instance_id": target.instance_id, "mode": "restored_readonly", "activation_job_id": activation["job_id"],
                         "latest_status": latest["status"], "latest_artifact_id": sidecar_id, "latest_sha256": sha}
            def check(state):
                current = state["selection"]
                if (current["generation"] if current else 0) != expected_generation or state["fence"] is None or state["fence"]["state"] != "frozen":
                    raise DataError("selection_changed")
            self.hub.commit("selector_commit", selection, validate=check)
            if self.rebind is not None: self.rebind(target, credentials, selection)
            current = self.hub.get(activation["job_id"])
            return self.hub.update_job(activation["job_id"], current["revision"], state="active_readonly", stage="active_readonly",
                                       target_id=target.target_id, selection_generation=selection["generation"], latest_status=latest["status"])
        finally:
            lease.close()
