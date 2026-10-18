"""098唯一托管入口，预检前占入口，真期限及finally收尾。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

from probe_support import CID, HERE, ROOT, RUN, docker, event, free, identity, inspect_guard, load, publish, stop_exact


def freeze(command):
    entries = load(HERE / "input-snapshot.json")["current_objects"]
    entries += [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in HERE.glob("*.py")]
    root = RUN / "as-run/files"
    for entry in entries:
        source = ROOT / entry["path"]
        raw = source.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], "098_object_drift"
        target = root / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(raw)
    publish("as-run-manifest.json", {"command": command, "objects": entries, "at": time.time(),
            "expected": "双合法不同目标同时准备，真实仲裁首槽唯一，一send，原子正文，树零及有限账面"})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--permit", required=True)
    parser.add_argument("--business-seconds", type=int, required=True)
    parser.add_argument("--cleanup-seconds", type=int, required=True)
    parser.add_argument("--sup-limit", type=int, required=True)
    args = parser.parse_args()
    assert args.permit == "g7-audit-01" and os.environ.get("RETROLUME_TASK098_PERMIT") == args.permit
    assert (args.business_seconds, args.cleanup_seconds, args.sup_limit) == (300, 120, 2)
    started = time.monotonic()
    RUN.mkdir(parents=True, exist_ok=False)
    # 入口在托管运行预检前落账，任何abort仍为唯一入口已耗用。
    publish("entry-attempt-01.json", {"permit": args.permit, "at": time.time(), "entry": 1,
            "business_limit_seconds": 300, "cleanup_reserve_seconds": 120, "sup_attempt_limit": 2,
            "browser": 0, "driver": 0, "build": 0, "provider": 0})
    command = [str(ROOT / "backend/.venv/Scripts/python.exe"), "-B", str(Path(__file__).resolve()),
               "--permit", args.permit, "--business-seconds", "300", "--cleanup-seconds", "120", "--sup-limit", "2"]
    process = None
    child_id = None
    failure = None
    cleanup_errors = []
    process_cleanup = []
    child_exit = None
    try:
        freeze(command)
        # 托管入口只允许自身专用资源，无第二入口、无额外容器start。
        spec = {"task": "TASK-098", "permit": args.permit, "activity_id": str(uuid4()),
                "business_keys": [str(uuid4()), str(uuid4())],
                "goals": ["Explain atomicity basics in this document", "Explain atomicity detailed learning points"],
                "root": str(HERE / "runtime/data"), "http_port": 18098, "database_port": 55441}
        publish("case-spec.json", spec)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith("RETROLUME_")}
        env.update({"RETROLUME_TASK098_PERMIT": args.permit, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})
        process = subprocess.Popen([str(ROOT / "backend/.venv/Scripts/python.exe"), "-B", str(HERE / "case_run.py")],
                                   cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            child_id = identity(process.pid)
            assert child_id is not None
            publish("owned-case-runner.json", {**child_id, "kind": "case-runner"})
        except BaseException:
            process.kill()
            process.wait(timeout=10)
            raise
        # 准备及内层finally保守共用300秒；超时外层仍有独立120秒收尾。
        remaining = max(0.01, 300 - (time.monotonic() - started))
        child_exit = process.wait(timeout=remaining)
        if child_exit != 0:
            failure = "case_nonzero"
    except BaseException as exc:
        failure = type(exc).__name__
        event("entry-failure", {"type": failure, "at": time.time()})
    finally:
        outer_cleanup_started = time.monotonic()
        cleanup_deadline = min(started + 420, outer_cleanup_started + 120)

        def remaining_cleanup(cap):
            return max(0.01, min(cap, cleanup_deadline - time.monotonic()))

        if process is not None and process.poll() is None:
            try:
                if child_id is not None:
                    process_cleanup.append(stop_exact(child_id, max_seconds=remaining_cleanup(12)))
                else:
                    process.kill()
                process.wait(timeout=remaining_cleanup(10))
            except BaseException as exc:
                cleanup_errors.append("runner:" + type(exc).__name__)
        owned = []
        if (RUN / "owned-app.json").exists():
            owned.append(load(RUN / "owned-app.json"))
        owned += [load(p) | {"kind": "SUP"} for p in RUN.glob("sup-created-*.json")]
        for expected in owned:
            try:
                process_cleanup.append(stop_exact(expected, max_seconds=remaining_cleanup(12)))
            except BaseException as exc:
                cleanup_errors.append("process:" + type(exc).__name__)
        if any(not p["zero"] for p in process_cleanup):
            cleanup_errors.append("process_tree_nonzero")
        publish("process-cleanup.json", process_cleanup)
        try:
            free(18098)
        except BaseException as exc:
            cleanup_errors.append("http_port:" + type(exc).__name__)
        if (RUN / "container-start-attempt-01.json").exists():
            try:
                # 唯一已登记的精确容器，即使docker start回执丢失也核真实状态并收尾。
                before_stop = inspect_guard(timeout=remaining_cleanup(10))
                publish("container-before-stop.json", before_stop)
                if before_stop["running"]:
                    stopped = docker("stop", "--time", "10", CID, timeout=remaining_cleanup(20))
                    assert stopped.returncode == 0
                after = inspect_guard(timeout=remaining_cleanup(10))
                assert not after["running"] and after["pid"] == 0
                publish("container-after.json", after)
            except BaseException as exc:
                cleanup_errors.append("container:" + type(exc).__name__)
        try:
            free(55441)
        except BaseException as exc:
            cleanup_errors.append("database_port:" + type(exc).__name__)
        post_hashes = []
        for obj in load(HERE / "input-snapshot.json")["current_objects"]:
            actual = hashlib.sha256((ROOT / obj["path"]).read_bytes()).hexdigest()
            post_hashes.append({"path": obj["path"], "expected": obj["sha256"], "actual": actual, "match": actual == obj["sha256"]})
        publish("post-hashes.json", post_hashes)
        if any(not x["match"] for x in post_hashes):
            failure = "object_drift_after"
        case = load(RUN / "case-run-result.json") if (RUN / "case-run-result.json").exists() else None
        if case is None or not case["cleanup_ok"]:
            cleanup_errors.append("case_finally_missing_or_failed")
        if case and (case["business_seconds"] > 300 or case["cleanup_seconds"] > 120):
            failure = "case_budget_exceeded"
        elapsed = time.monotonic() - started
        if elapsed > 420 or time.monotonic() > cleanup_deadline:
            cleanup_errors.append("outer_deadline_exceeded")
        result = {"entry": 1, "container_starts": len(list(RUN.glob("container-start-attempt-*.json"))),
                  "sup_attempts": len(list(RUN.glob("sup-attempt-*.json"))),
                  "actual_sup_created": len(list(RUN.glob("sup-created-*.json"))),
                  "actual_sup_resumed": len(list(RUN.glob("sup-resumed-*.json"))),
                  "browser": 0, "driver": 0, "build": 0, "provider": 0, "paid": 0,
                  "child_exit_code": child_exit, "failure": failure, "case": case,
                  "outer_cleanup_seconds": time.monotonic() - outer_cleanup_started,
                  "total_seconds": elapsed, "cleanup_errors": cleanup_errors,
                  "cleanup_ok": not cleanup_errors, "entry_command": command,
                  "cross_task_upper_counts": {"entries": 12, "starts": 12, "sup": 25, "browser": 6, "driver": 7}}
        publish("entry-final.json", result)
        print(json.dumps(result, ensure_ascii=False))
    return 0 if not failure and not cleanup_errors and child_exit == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
