"""一个有界107根串行持有PG/API、RAM凭据与最后三组浏览器。"""
import asyncio
import collections
import hashlib
import json
import os
import pathlib
import secrets
import subprocess
import sys
import time
import traceback
import urllib.request
from uuid import uuid4
from .common import (ROOT, EVIDENCE, PERMIT, atomic_json, charge, checkpoint, checksum, initialize,
                     load, redact, register_secret, remaining, reserve, serial, state, utc)
from .resources import start, ordinary_dsn, stop, all_stopped, port_free
from .processes import state as process_state, descendants, terminate

TABLES = ("activities", "activity_allowed_models", "activity_memory_bindings", "activity_memory_choices",
          "activity_operation_results", "activity_operations", "activity_scope_sources", "interview_heads",
          "interview_commands", "interview_records", "learning_memories", "learning_memory_bodies",
          "learning_memory_commands", "learning_memory_dependencies", "learning_memory_revisions",
          "learning_memory_purge_receipts", "material_sources", "material_versions", "pdf_extracted_pages",
          "pdf_review_candidates", "pdf_review_pages", "pdf_user_supplements", "teaching_commands", "teaching_heads", "teaching_records")


def snapshot(dsn):
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(dsn, row_factory=dict_row) as connection:
        assert connection.execute("SELECT current_user AS name").fetchone()["name"] == "retrolume_task106_app"
        output = {}
        for table in TABLES:
            if not connection.execute("SELECT to_regclass(%s) AS name", ("public." + table,)).fetchone()["name"]:
                continue
            rows = [x["row"] for x in connection.execute("SELECT to_jsonb(t) AS row FROM public." + table + " t")]
            output[table] = rows
    return output


def bag(rows):
    return collections.Counter(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=serial) for x in rows)


async def shape(dsn):
    from app.activities.repository import PostgresAdmissionLedger
    ledger = PostgresAdmissionLedger(dsn, statement_timeout_ms=10000, lock_timeout_ms=5000)
    return await ledger._transaction(ledger._interview_shape)


def http_get(url, token=None):
    headers = {"X-RetroLume-Session": token, "Origin": "http://127.0.0.1:18106"} if token else {}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status, response.read()


def fixed_product():
    expected = load(EVIDENCE / "orchestration-setup-20261008/audit-input.json")["current_files"]
    bad = [p for p, sha in expected.items() if checksum(ROOT / p) != sha]
    if bad:
        raise RuntimeError("107输入/产品发生漂移：" + ",".join(bad))
    return expected


def main():
    initialize(); reserve("root", dict(name="R01-final-browser-one-session")); start_ns = time.monotonic_ns()
    folder = EVIDENCE / "runs/R01-final-browser-one-session"; folder.mkdir(parents=True, exist_ok=False)
    report = dict(status="FAIL", actual_new_root=True, started_at=utc(), start_ns=start_ns,
                  root_deadline_ns=state()["root_deadline_ns"], cases=[], prior_roots=67)
    server = node = None; server_id = node_id = None; admin = dsn = None; pg_started = False; known_tree = []
    try:
        before_files = fixed_product(); atomic_json(folder / "product-before.json", before_files)
        fixture_sources = {}
        source_paths = list((ROOT / "backend/tests/fixtures/task107").rglob("*.py")) + [ROOT / "frontend/tests/task107-g10-final.mjs"]
        for source in source_paths:
            relative = source.relative_to(ROOT)
            target = folder / "as-run" / relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(source.read_bytes())
            fixture_sources[str(relative)] = checksum(source)
        atomic_json(folder / "own-as-run-source.json", fixture_sources)
        admin = start(); pg_started = True; dsn = ordinary_dsn(admin)
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        actual_shape = asyncio.run(shape(dsn))
        canonical = json.dumps(actual_shape, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
        atomic_json(folder / "ordinary-S1-catalog.json", dict(shape=actual_shape, fingerprint=fingerprint, ordinary_role=True))
        if fingerprint != "13e3d8d9d78d7f6e119a226be6f4d6f3163b9bf5eaeeb1b8d66e5d44351f850b":
            raise RuntimeError("107源码/真实S1目录指纹不符，停止真实动作")
        before = snapshot(dsn); atomic_json(folder / "pg-before.json", before)
        work = EVIDENCE / "workspace/R01"; data = work / "data"; originals = data / "originals"; backup = work / "backup"
        originals.mkdir(parents=True, exist_ok=True); backup.mkdir(parents=True, exist_ok=True)
        original_root = ROOT / "DocuN/evidence/TASK-106/continuation-01/synthetic/data/originals"
        copied = []
        for source in original_root.iterdir():
            if source.is_file():
                content = source.read_bytes()
                if hashlib.sha256(content).hexdigest() != source.name:
                    raise RuntimeError("107旧合成原件文件名/hash不一致")
                (originals / source.name).write_bytes(content); copied.append(dict(sha256=source.name, bytes=len(content)))
        atomic_json(folder / "original-copies.json", copied)
        config = load(ROOT / "DocuN/evidence/TASK-106/continuation-01/synthetic/activity-normal.json")
        config["api_key_env"] = "RETROLUME_TASK107_MODEL_KEY"
        configfile = EVIDENCE / "runtime-config.json"; atomic_json(configfile, config)
        key = secrets.token_urlsafe(32); register_secret(key)
        env = dict(os.environ, RETROLUME_TASK107_FIXTURE=PERMIT, PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=os.pathsep.join((str(ROOT / "backend/tests/fixtures/task107/bootstrap"), str(ROOT / "backend"))),
                   RETROLUME_DATA_DIR=str(data), RETROLUME_BACKUP_DIR=str(backup), RETROLUME_DATABASE_URL=dsn,
                   RETROLUME_ACTIVITY_CONFIG=str(configfile), RETROLUME_TASK107_MODEL_KEY=key)
        if not port_free(18106):
            raise RuntimeError("107 API端口已被占用")
        reserve("listener_start", dict(port=18106, module="tests.fixtures.task107.server"))
        server = subprocess.Popen([sys.executable, "-X", "utf8", "-B", "-m", "tests.fixtures.task107.server"], cwd=ROOT / "backend", env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        server_id = dict(process_state(server.pid), module="tests.fixtures.task107.server"); atomic_json(folder / "owned-api.json", server_id)
        until = time.monotonic() + 20
        while True:
            try:
                if http_get("http://127.0.0.1:18106/health")[0] == 200:
                    break
            except Exception:
                if time.monotonic() >= until or server.poll() is not None:
                    raise RuntimeError("107自己的API bootstrap就绪失败") from None
                time.sleep(.1)
        _, session_body = http_get("http://127.0.0.1:18106/api/session")
        token = json.loads(session_body)["token"]; register_secret(token)
        old_seed = load(ROOT / "DocuN/evidence/TASK-106/continuation-01/runs/P04-resume-real-cancel-and-config/browser-seed.json")
        old_views = {}
        for label in ("technical", "lost", "accepted"):
            aid = old_seed[label]
            _, body = http_get("http://127.0.0.1:18106/api/activities/" + aid + "/interview/workspace", token)
            old_views[label] = json.loads(body)
        _, old_receipt = http_get("http://127.0.0.1:18106/api/activities/" + old_seed["accepted"] + "/interview/commands/" + old_seed["acceptedCommand"]["business_key"], token)
        atomic_json(folder / "old-seeds-current-readonly.json", dict(workspaces=old_views, accepted_receipt=json.loads(old_receipt), old_POST=0))
        material = old_seed["materials"][old_seed["technicalTitle"]]
        prepared = load(EVIDENCE / "validation-plan.json")
        plan = dict(B1=prepared["B1"], B2=prepared["B2"], material=material,
                    target="TASK107合成余额算法：串行110及先读100后写120、90的覆盖风险",
                    answer_v1=old_seed["Tanswer"],
                    answer_v2="🧭修订说明：给定算法串行得到110；两个操作都先读100后写120和90，后写90覆盖一次写回。只针对给定合成算法。",
                    native_call_plan=dict(B1=4, B2=1, B3=0, total=5, hard_limit=8),
                    old_seed_explanation="旧场次保留；真实GET已核期限/状态，不修改旧期限或重发旧模型键",
                    B2_method="调用真实accept得到持久回执后仅延迟它的完成通知，再真实取消HTTP调用者，使原键accepted/unclaimed；原POST后续显式同键完整native链COMMIT，浏览器丢其真实响应",
                    B3_method="真实WebLock完成释放、真实digest完成后延迟完成通知；真实goal/API/GET产生新view；一个直接摘要hash变化代表；不改React状态/服务资格")
        atomic_json(EVIDENCE / "runtime-plan.json", plan); checkpoint("planned_aids", [plan["B1"], plan["B2"]])
        _, index = http_get("http://127.0.0.1:18106", None)
        (folder / "actual-index.html").write_bytes(index)
        browser_out = folder / "browser"; browser_out.mkdir()
        env["TASK107_BROWSER_OUTPUT"] = str(browser_out)
        reserve("driver", dict(script="frontend/tests/task107-g10-final.mjs")); reserve("browser", dict(profile=str(browser_out / "chrome-profile")))
        node = subprocess.Popen(["node", str(ROOT / "frontend/tests/task107-g10-final.mjs")], cwd=ROOT / "frontend", env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        node_id = dict(process_state(node.pid), module="frontend/tests/task107-g10-final.mjs"); atomic_json(folder / "owned-browser-driver.json", node_id)
        print(json.dumps(dict(stage="107真实会话启动", api_pid=server.pid, browser_driver_pid=node.pid, native_planned=5)), flush=True)
        last = None
        while node.poll() is None:
            if time.monotonic_ns() >= state()["root_deadline_ns"]:
                raise RuntimeError("107真实根900秒截止已到")
            checkpoint_file = browser_out / "checkpoint.json"
            if checkpoint_file.exists():
                try:
                    progress = [x["method"] for x in load(checkpoint_file)["cases"]]
                    if progress != last:
                        print(json.dumps(dict(stage="107浏览器检查点", methods=progress)), flush=True); last = progress
                except (ValueError, KeyError):
                    pass
            time.sleep(.2)
        stdout, stderr = node.communicate(timeout=5)
        (folder / "browser-stdout.txt").write_text(redact(stdout.decode("utf-8", "replace")), encoding="utf-8")
        (folder / "browser-stderr.txt").write_text(redact(stderr.decode("utf-8", "replace")), encoding="utf-8")
        browser = load(browser_out / "result.json"); report["browser"] = browser; report["driver_exit_code"] = node.returncode
        after = snapshot(dsn); atomic_json(folder / "pg-after.json", after)
        missing = {table: dict(bag(rows) - bag(after[table])) for table, rows in before.items() if bag(rows) - bag(after[table])}
        atomic_json(folder / "old-all-rows-preserved.json", dict(before_tables=len(before), old_rows_missing=missing,
                                                                old_immutable_and_UNKNOWN_preserved=not missing, old_seeds_no_write=True))
        if missing:
            raise RuntimeError("107旧合成业务行发生未授权改变")
        fixed_product(); atomic_json(folder / "product-after.json", before_files)
        actual_shape_after = asyncio.run(shape(dsn)); assert actual_shape == actual_shape_after
        report["new_counts"] = state()["counts"]
        if node.returncode or browser["status"] != "PASS":
            raise RuntimeError("107自己的浏览器夹具未完成；先据检查点核实际COMMIT，不重放")
        report["status"] = "PASS"
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=redact(str(error)))
        (folder / "failure-stack.txt").write_text(redact(traceback.format_exc()), encoding="utf-8")
    finally:
        cleanup_begin = time.monotonic(); stop_reports = {}
        try:
            live_roots = []
            for owned in (server_id, node_id):
                if owned and process_state(owned["pid"]).get("created_100ns") == owned["created_100ns"]:
                    live_roots.append(owned["pid"])
            known_tree = descendants(live_roots) if live_roots else []
            atomic_json(folder / "owned-tree-before-cleanup.json", known_tree)
            if node and node.poll() is None:
                stop_reports["driver"] = terminate(node_id)
            atomic_json(EVIDENCE / "stop-api.json", dict(at=utc(), only_owned=True))
            if server:
                try:
                    stdout, stderr = server.communicate(timeout=min(70, remaining("cleanup", 70)))
                except subprocess.TimeoutExpired:
                    stop_reports["api_forced"] = terminate(server_id); stdout, stderr = server.communicate(timeout=5)
                (folder / "api-stdout.txt").write_text(redact(stdout.decode("utf-8", "replace")), encoding="utf-8")
                (folder / "api-stderr.txt").write_text(redact(stderr.decode("utf-8", "replace")), encoding="utf-8")
            for owned in reversed(known_tree):
                current = process_state(owned["pid"])
                if current.get("running") and current.get("created_100ns") == owned.get("created_100ns"):
                    stop_reports[str(owned["pid"])] = terminate(owned)
            if pg_started or state()["counts"]["container_start"]:
                stop_reports["pg1"] = stop()
            elif admin:
                stop_reports["pg1"] = stop()
            stop_reports["containers"] = all_stopped()
            stop_reports["ports_free"] = {str(p): port_free(p) for p in (18106,18107,55446,55447,55448)}
            stop_reports["owned_births"] = [dict(expected=x, final=process_state(x["pid"])) for x in known_tree]
            atomic_json(folder / "cleanup.json", stop_reports)
        except BaseException as error:
            report["status"] = "FAIL"; report["cleanup_unconfirmed"] = redact(str(error))
            atomic_json(folder / "cleanup-unconfirmed.json", dict(error_type=type(error).__name__, message=redact(str(error)), stops=stop_reports))
        cleanup_seconds = time.monotonic() - cleanup_begin
        charge("cleanup", cleanup_seconds, dict(name=report.get("name", "R01")))
        report.update(ended_at=utc(), elapsed_seconds=(time.monotonic_ns()-start_ns)/1e9, cleanup_seconds=cleanup_seconds,
                      new_counts=state()["counts"], data_volume_role_profile_retained=True)
        charge("real", report["elapsed_seconds"], dict(name="R01-final-browser-one-session", includes_cleanup=True))
        atomic_json(folder / "result.json", report)
        checkpoint("R01-result", dict(status=report["status"], path=str(folder / "result.json")))
    print(json.dumps(dict(status=report["status"], error=report.get("error"), counts=state()["counts"])), flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
