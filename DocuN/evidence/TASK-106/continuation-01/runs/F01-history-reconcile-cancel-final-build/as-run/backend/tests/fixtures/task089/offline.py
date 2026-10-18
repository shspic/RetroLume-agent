"""TASK089定向离线验证；单命令60秒、外层Job、原始日志和加载文件指纹。"""
from pathlib import Path
import hashlib
import json
import os
import queue
import sys
import time
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
BACKEND = ROOT / "backend"
EVIDENCE = ROOT / "Ndocu/evidence/task-089"
sys.path.insert(0, str(BACKEND))
from controlled_child import ControlledChild


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def hashes():
    paths = list((BACKEND / "app").rglob("*.py"))
    paths += list((BACKEND / "migrations").glob("*.sql"))
    paths += list((BACKEND / "tests/fixtures/task089").glob("*.py"))
    paths += [BACKEND / "tests" / name for name in (
        "test_activity_results.py", "test_capabilities.py", "test_worker_one_call.py",
        "test_worker_session.py", "test_activity_ledger.py", "test_activity_recovery.py",
        "test_activity_time_budget.py")]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def test_child(folder, targets):
    # 导入前固定输入；禁用pyc，保存实际导入模块的路径/hash。
    before = hashes()
    suite = unittest.defaultTestLoader.loadTestsFromNames(targets)
    discovered = suite.countTestCases()
    loaded = {}
    for name, module in tuple(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename and name.startswith(("app.", "tests.")):
            p = Path(filename).resolve()
            if p.is_relative_to(ROOT) and p.suffix == ".py":
                loaded[p.relative_to(ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    write(folder / "as-run-hashes.json", {"before": before, "loaded_modules": loaded})
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    write(folder / "case-summary.json", {
        "discovered": discovered, "run_including_skips": result.testsRun,
        "executed": result.testsRun - len(result.skipped), "skipped": len(result.skipped),
        "passed": result.testsRun - len(result.skipped) - len(result.errors) - len(result.failures),
        "failures": len(result.failures), "errors": len(result.errors),
        "source_unchanged": hashes() == before,
    })
    return 0 if result.wasSuccessful() and hashes() == before else 1


def main(tag, targets):
    folder = EVIDENCE / tag
    folder.mkdir(exist_ok=False)
    budget_file = EVIDENCE / "budget-manifest.json"
    budget = json.loads(budget_file.read_text(encoding="utf-8-sig"))
    if budget["offline_used_seconds"] + 60 > budget["offline_limit_seconds"]:
        raise RuntimeError("offline budget exhausted")
    started = time.monotonic()
    deadline = started + 58
    child = ControlledChild()
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("RETROLUME_") and ("DSN" in k or "DATABASE" in k))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    command = [sys.executable, "-B", str(Path(__file__).resolve()), "--child", str(folder), *targets]
    state = {"command": command, "utc": datetime.now(timezone.utc).isoformat(), "exit": None}
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
            try: label, line = child.lines.get_nowait()
            except queue.Empty: break
            if line is not None: logs[label].append(line)
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
    if summary.exists(): print(summary.read_text(encoding="utf-8"))
    return 0 if state["exit"] == 0 and state.get("tree_zero") else 1


if __name__ == "__main__":
    if sys.argv[1] == "--child":
        raise SystemExit(test_child(Path(sys.argv[2]), sys.argv[3:]))
    raise SystemExit(main(sys.argv[1], sys.argv[2:]))
