"""白名单环境、隔离子进程、单批至多120秒，仅选择直接相关离线方法。"""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "child":
    sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "backend/tests")]
    import asyncio
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    import unittest
    import faulthandler
    from contextlib import ExitStack
    from importlib.metadata import version
    from unittest.mock import patch
    methods = ["test_q_readiness",
        "test_activity_workspace_config.ConfigLoaderTests.test_missing_file_is_config_missing",
        "test_activity_workspace_config.ConfigLoaderTests.test_bad_json_and_non_dict_are_invalid",
        "test_activity_workspace_config.ConfigLoaderTests.test_l1_without_key_and_l2_with_key",
        "test_activity_workspace_config.ConfigLoaderTests.test_service_mapping_incompatibilities",
        "test_activity_workspace_api.OfflineApiTests.test_guard_rejections",
        "test_activity_workspace_api.OfflineApiTests.test_own_origin_allowed_for_same_site_page"]
    if len(sys.argv) > 3 and sys.argv[3] == "diagnostic":
        methods = ["test_q_readiness.ReadinessTests.test_auth_context_readonly_and_error_redaction"]
        faulthandler.dump_traceback_later(20, exit=True)
    guards = ("app.data_exit.control.ControlHub.__init__", "app.data_exit.q_store.QAuthority.bind",
              "app.data_exit.q_store.QAuthority.approve", "app.operator.q_request.configure_application",
              "app.operator.q_request.operator_ledger", "app.main.PostgresMaterials",
              "app.main.PostgresAdmissionLedger", "psycopg.connect", "psycopg.AsyncConnection.connect",
              "app.capabilities.transport.HttpxModelTransport.__init__", "httpx.AsyncClient.send")
    started = time.monotonic()
    with ExitStack() as stack:
        calls = {name: stack.enter_context(patch(name, side_effect=AssertionError("禁止离线外执行 " + name))) for name in guards}
        suite = unittest.TestLoader().loadTestsFromNames(methods)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        counts = {name: mock.call_count for name, mock in calls.items()}
    summary = {"selected": methods, "tests_run": result.testsRun, "failures": len(result.failures),
               "errors": len(result.errors), "skipped": len(result.skipped),
               "forbidden_call_counts": counts, "successful": result.wasSuccessful() and not any(counts.values()),
               "elapsed_seconds": time.monotonic() - started,
               "packages": {name: version(name) for name in ("fastapi", "pydantic", "httpx", "psycopg")}}
    save(Path(sys.argv[2]), summary)
    raise SystemExit(0 if summary["successful"] else 1)

if __name__ == "__main__":
    batch = sys.argv[1]
    assert batch in ("batch1", "batch2", "batch3")
    folder = HERE / batch
    folder.mkdir(exist_ok=False)
    work = folder / "temporary-configs"
    work.mkdir()
    # 只显式提供系统运行所需路径，不继承任何用户provider key、DSN或配置。
    env = {"SYSTEMROOT": "C:\\Windows", "WINDIR": "C:\\Windows", "TEMP": str(work), "TMP": str(work)}
    command = [str(ROOT / "backend/.venv/Scripts/python.exe"), "-I", "-B", str(Path(__file__).resolve()),
               "child", str(folder / "summary.json")]
    if batch == "batch2":
        command.append("diagnostic")
    paths = ["backend/app/main.py", "backend/app/activities/api.py", "backend/app/q_readiness.py",
             "backend/tests/test_q_readiness.py", "backend/tests/test_activity_workspace_config.py",
             "backend/tests/test_activity_workspace_api.py"]
    snapshot = [{"path": name, "bytes": len((ROOT / name).read_bytes()),
                 "sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest()} for name in paths]
    start = datetime.datetime.now(datetime.timezone.utc)
    timer = time.monotonic()
    save(folder / "command.json", {"command": command, "cwd": str(ROOT / "backend"), "env": env,
         "timeout_seconds": 120, "started_at": start.isoformat(), "input_bytes": snapshot,
         "purpose": "新只读投影、关闭、脱敏、装载次数、认证/上下文及原GET probe保持；不重跑旧Q矩阵"})
    try:
        result = subprocess.run(command, cwd=ROOT / "backend", env=env, timeout=120, capture_output=True)
        (folder / "stdout.bin").write_bytes(result.stdout)
        (folder / "stderr.bin").write_bytes(result.stderr)
        exit_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        (folder / "stdout.bin").write_bytes(exc.stdout or b"")
        (folder / "stderr.bin").write_bytes(exc.stderr or b"")
        exit_code = 124
    record = {"exit_code": exit_code, "elapsed_seconds": time.monotonic() - timer,
              "ended_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "logs": [{"path": name, "bytes": len((folder / name).read_bytes()),
                        "sha256": hashlib.sha256((folder / name).read_bytes()).hexdigest()}
                       for name in ("stdout.bin", "stderr.bin")]}
    save(folder / "completion.json", record)
    print(json.dumps(record, ensure_ascii=False))
    sys.stdout.flush()
    # 原始stderr另存字节，屏幕用UTF8/替换解码只供快速定位。
    print((folder / "stderr.bin").read_bytes().decode("utf-8", errors="replace"))
    raise SystemExit(exit_code)
