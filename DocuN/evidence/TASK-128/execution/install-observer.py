"""正式安装器CLI的真实连接观察包装；仅预定interrupted/002隐藏一次提交确认。"""
from contextlib import contextmanager
import argparse
import datetime
import json
import os
from pathlib import Path
import runpy
import sys
import re
from urllib.parse import quote

def safe_diagnostic(error, values):
    message = str(error)
    for value in sorted((v for v in values if v), key=len, reverse=True):
        for form in (value, quote(value, safe=""), json.dumps(value)[1:-1], value.replace("'", "\\'")):
            message = message.replace(form, "[REDACTED]")
    message = re.sub(r"postgres(?:ql)?://\S+", "[DSN REDACTED]", message)
    return {"exception_module": type(error).__module__, "exception_class": type(error).__name__,
            "sqlstate": getattr(error, "sqlstate", None), "diagnostic": message[:700]}

ROOT = Path(__file__).absolute().parents[4]
EVIDENCE = Path(__file__).absolute().parent
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "backend/.venv/Lib/site-packages")]
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


class Observer:
    def __init__(self, path, bodies, *, inject=False):
        self.path, self.bodies, self.inject = path, bodies, inject
        self.injected, self.connections, self.writes = False, 0, 0
        self.stream = path.open("x", encoding="utf-8", newline="\n")

    def event(self, kind, **fields):
        self.stream.write(json.dumps({"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                      "kind": kind, **fields}, ensure_ascii=False, sort_keys=True) + "\n")
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def connect(self, real_connect, **kwargs):
        if kwargs.get("host") != "127.0.0.1" or kwargs.get("hostaddr") != "127.0.0.1":
            raise RuntimeError("observer_connection_boundary")
        self.connections += 1
        self.event("real_connect_requested", **{key: kwargs.get(key) for key in ("host", "hostaddr", "port", "dbname", "user")})
        try:
            inner = real_connect(**kwargs)
        except BaseException as error:
            values = [v for k,v in os.environ.items() if k.startswith("RETROLUME_NORMAL_")]
            values.append(kwargs.get("password", ""))
            self.event("real_connect_failed", **safe_diagnostic(error, values))
            raise
        self.event("real_connect_returned", backend_pid=inner.info.backend_pid)
        return Connection(inner, self)


class Connection:
    def __init__(self, inner, observer):
        self.inner, self.observer = inner, observer
        self.control_inserted = False

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def __enter__(self):
        self.inner.__enter__()
        return self

    def __exit__(self, *args):
        try:
            return self.inner.__exit__(*args)
        finally:
            self.observer.event("real_connection_closed", closed=self.inner.closed)

    def execute(self, statement, params=None, **kwargs):
        stage = self.observer.bodies.get(statement) if isinstance(statement, str) else None
        if stage:
            self.observer.writes += 1
            self.observer.event("original_migration_submitted", stage=stage)
        elif isinstance(statement, str):
            normalized = statement.lstrip().upper()
            if normalized.startswith("INSERT INTO PUBLIC.DATA_CONTROL"):
                self.control_inserted = True
                self.observer.writes += 1
                self.observer.event("control_insert_submitted")
            elif normalized.startswith(("SELECT", "SHOW", "BEGIN READ ONLY", "ROLLBACK")):
                self.observer.event("read_or_readonly_boundary", category=normalized.split()[0],
                                    read_only_begin=normalized.startswith("BEGIN READ ONLY"))
            else:
                self.observer.event("other_statement_category", category=normalized.split()[0])
        else:
            # 参数化标识符DDL可含真实密码Literal；绝不渲染、保存SQL或参数。
            self.observer.writes += 1
            self.observer.event("parameterized_login_statement")
        inner_cursor = self.inner.execute(statement, params, **kwargs)
        return Cursor(inner_cursor, self, stage=stage,
                      identity=isinstance(statement, str) and statement.startswith("SELECT current_database() AS database"))

    def state_after_boundary(self, boundary):
        row = self.inner.execute("SELECT to_regclass('public.data_control') IS NOT NULL AS present").fetchone()
        if row["present"]:
            control = self.inner.execute("SELECT dataset_id::text,instance_id::text,originals_root_id::text,schema_profile,mode FROM public.data_control").fetchone()
        else:
            control = None
        self.observer.event("control_observed_after_real_commit", boundary=boundary, control=control)

    @contextmanager
    def transaction(self, *args, **kwargs):
        with self.inner.transaction(*args, **kwargs):
            yield self
        self.observer.event("additional_transaction_commit_returned", transaction_status=int(self.inner.info.transaction_status))
        if self.control_inserted:
            self.state_after_boundary("normal_control")
            self.control_inserted = False


class Cursor:
    def __init__(self, inner, connection, *, stage=None, identity=False):
        self.inner, self.connection = inner, connection
        self.stage, self.identity = stage, identity

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def fetchone(self):
        row = self.inner.fetchone()
        if self.identity and row is not None:
            self.connection.observer.event("actual_database_identity", **{key: row[key] for key in (
                "database", "database_oid", "system_identifier", "installer_login", "session_login", "rolsuper",
                "version_num", "encoding", "server_address", "server_port")})
        return row

    def nextset(self):
        result = self.inner.nextset()
        if result is None and self.stage:
            connection, observer = self.connection, self.connection.observer
            committed = self.inner.statusmessage == "COMMIT" and int(connection.inner.info.transaction_status) == 0
            observer.event("all_real_migration_results_consumed", stage=self.stage, final_status=self.inner.statusmessage,
                           transaction_status=int(connection.inner.info.transaction_status), commit_observed=committed)
            if not committed:
                raise RuntimeError("observer_expected_real_commit")
            if self.stage in ("013", "014", "015"):
                connection.state_after_boundary(self.stage)
            if self.stage == "002" and observer.inject and not observer.injected:
                observer.injected = True
                observer.event("planned_confirmation_hidden_after_real_commit", stage="002")
                raise RuntimeError("planned_002_confirmation_loss")
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slot", choices=("source", "interrupted"), required=True)
    parser.add_argument("--action", choices=("apply", "verify"), required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--inject-002", action="store_true")
    args = parser.parse_args()
    private = ROOT / ".runtime/normal-first-install" / args.slot
    if (not args.config.is_absolute() or not args.config.is_relative_to(private)
            or not args.receipt.is_absolute() or not args.receipt.is_relative_to(private)
            or not args.trace.is_absolute() or not args.trace.is_relative_to(EVIDENCE)
            or args.inject_002 and (args.slot != "interrupted" or args.action != "apply")):
        raise SystemExit("observer_scope_rejected")
    names = json.loads((ROOT / "deploy/normal_install_manifest.json").read_text(encoding="utf-8"))["migrations"]
    bodies = {(ROOT / row["path"]).read_bytes().decode("utf-8-sig"): Path(row["path"]).name[:3] for row in names}
    observer = Observer(args.trace, bodies, inject=args.inject_002)
    import psycopg
    real_connect = psycopg.connect
    psycopg.connect = lambda **kwargs: observer.connect(real_connect, **kwargs)
    entry = ROOT / "deploy/initialize_normal.py"
    sys.argv = [str(entry), args.action, "--config", str(args.config), "--receipt", str(args.receipt)]
    observer.event("formal_cli_started", entry=str(entry), action=args.action, slot=args.slot,
                   planned_single_002_injection=args.inject_002)
    try:
        runpy.run_path(str(entry), run_name="__main__")
    finally:
        observer.event("formal_cli_finished", connections=observer.connections, write_requests=observer.writes,
                       planned_injection_exercised=observer.injected)
        observer.stream.close()
        psycopg.connect = real_connect


if __name__ == "__main__":
    main()
