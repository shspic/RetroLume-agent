"""TASK-092 定向离线批次：受影响套件清单、单命令截止、hash绑定与预算记录。

用法：python offline_runner.py offline-01 [额外target...]
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.machinery
import json
import os
from pathlib import Path
import queue
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BACKEND = ROOT / "backend"
EVIDENCE = HERE
sys.path.insert(0, str(BACKEND))

loaded_bytes = {}
_original_get_code = importlib.machinery.SourceFileLoader.get_code


def _capture_code(self, fullname):
    if fullname == "app" or fullname.startswith(("app.", "tests.")):
        path = Path(self.get_filename(fullname)).resolve()
        raw = self.get_data(str(path))
        loaded_bytes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
        return self.source_to_code(raw, str(path))
    return _original_get_code(self, fullname)


importlib.machinery.SourceFileLoader.get_code = _capture_code

from child_control import ControlledChild  # noqa: E402

TARGETS = [
    "tests.test_activity_tools",
    "tests.test_worker_one_tool",
    "tests.test_worker_one_call",
    "tests.test_worker_session",
    "tests.test_capabilities",
    "tests.test_activity_results",
    "tests.test_activity_continuation",
    "tests.test_activity_time_budget",
    "tests.test_activity_ledger",
    "tests.test_activity_recovery",
    "tests.test_activity_scope",
    "tests.test_activity_dispatch_close",
    "tests.test_d3_runner_control",
]


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def hashes() -> dict:
    paths = list((BACKEND / "app").rglob("*.py")) + list((BACKEND / "migrations").glob("*.sql"))
    paths += [BACKEND / "tests" / name for name in (
        "test_activity_tools.py", "test_worker_one_tool.py", "test_worker_one_call.py",
        "test_worker_session.py", "test_capabilities.py", "test_activity_results.py",
        "test_activity_continuation.py", "test_activity_time_budget.py", "test_activity_ledger.py",
        "test_activity_recovery.py", "test_activity_scope.py", "test_activity_dispatch_close.py",
        "test_d3_runner_control.py")]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def test_child(folder: Path, targets: list[str]) -> int:
    before = hashes()
    suite = unittest.defaultTestLoader.loadTestsFromNames(targets)
    loaded = {}
    for name, module in tuple(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename and name.startswith(("app.", "tests.")):
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT) and path.suffix == ".py":
                loaded[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    write(folder / "as-run-hashes.json", {"before": before, "loaded_modules": loaded})
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    write(folder / "loaded-source-bytes.json", loaded_bytes)
    write(folder / "post-hashes.json", hashes())
    write(folder / "case-summary.json", {
        "discovered": suite.countTestCases(), "run_including_skips": result.testsRun,
        "executed": result.testsRun - len(result.skipped), "skipped": len(result.skipped),
        "passed": result.testsRun - len(result.skipped) - len(result.errors) - len(result.failures),
        "failures": len(result.failures), "errors": len(result.errors),
        "source_unchanged": hashes() == before, "targets": targets})
    return 0 if result.wasSuccessful() and hashes() == before else 1


def main(tag: str, targets: list[str]) -> int:
    folder = EVIDENCE / tag
    folder.mkdir(exist_ok=False)
    budget_file = EVIDENCE / "budget-manifest.json"
    budget = json.loads(budget_file.read_text(encoding="utf-8-sig"))
    if budget["offline_used_seconds"] + 120 > budget["offline_limit_seconds"]:
        raise RuntimeError("offline budget exhausted")
    started = time.monotonic()
    deadline = started + 110
    child = ControlledChild()
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("RETROLUME_") and ("DSN" in k or "DATABASE" in k))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    command = [sys.executable, "-B", str(Path(__file__).resolve()), "--child", str(folder), *targets]
    state = {"command": command[:2] + ["offline_runner.py", "--child", tag, "..."],
             "utc": datetime.now(timezone.utc).isoformat(), "exit": None,
             "scenarios": targets, "deadline_seconds": 110}
    try:
        state["process"] = child.start(command, cwd=BACKEND, env=env, deadline=deadline - 5)
        budget["active_processes"] = [state["process"]]
        write(budget_file, budget)
        write(folder / "manifest.json", state)
        state["exit"] = child.wait_empty(deadline - 5)
    except BaseException as exc:
        state["error_type"] = type(exc).__name__
    finally:
        try:
            child.stop(deadline)
            state["tree_zero"] = child.active() == 0
        finally:
            child.close()
            state["handles_closed"] = True
        for reader in child.readers:
            reader.join(timeout=.5)
        logs = {"stdout": [], "stderr": []}
        while True:
            try:
                label, line = child.lines.get_nowait()
            except queue.Empty:
                break
            if line is not None:
                logs[label].append(line)
        for label, lines in logs.items():
            (folder / (label + ".log")).write_text("".join(lines), encoding="utf-8")
        state["events"] = child.events
        state["seconds"] = time.monotonic() - started
        write(folder / "manifest.json", state)
        budget["offline_used_seconds"] += state["seconds"]
        budget["offline_runs"].append({"path": folder.relative_to(ROOT).as_posix(),
                                       "seconds": state["seconds"], "exit": state["exit"]})
        budget["active_processes"] = [] if state.get("tree_zero") else budget["active_processes"]
        write(budget_file, budget)
    print(json.dumps({k: state.get(k) for k in ("exit", "seconds", "tree_zero", "handles_closed")}))
    summary = folder / "case-summary.json"
    if summary.exists():
        print(summary.read_text(encoding="utf-8"))
    return 0 if state["exit"] == 0 and state.get("tree_zero") else 1


if __name__ == "__main__":
    if sys.argv[1] == "--child":
        raise SystemExit(test_child(Path(sys.argv[2]), sys.argv[3:]))
    raise SystemExit(main(sys.argv[1], sys.argv[2:] or TARGETS))
