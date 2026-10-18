"""Prepare synthetic SUP->Job->controlled worker chain; no Job execution here."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def once(relative, old, new):
    path = ROOT / relative
    data = path.read_text(encoding="utf-8")
    assert data.count(old) == 1, (relative, data.count(old))
    path.write_text(data.replace(old, new), encoding="utf-8", newline="")


once(
    "backend/tests/fixtures/task083/fixture.py",
    '    if mode == "fast":\n        time.sleep(0.15)\n        return 0\n',
    '    if mode == "fast":\n        time.sleep(0.15)\n        return 0\n    if mode == "controlled_fast":\n        import asyncio\n        sys.path.insert(0, str(HERE.parents[3]))\n        from app.worker.worker_main import run_controlled_worker\n\n        class SyntheticGateway:\n            async def call(self, context, request):\n                await asyncio.sleep(0.05)\n                return "synthetic-received"\n\n        async def work(gate):\n            assert await gate.call(None, None) == "synthetic-received"\n\n        asyncio.run(run_controlled_worker(SyntheticGateway(), work, drain_timeout_seconds=1.0))\n        return 0\n',
)
once(
    "backend/tests/test_worker_session.py",
    '            str(uuid4()), "worker-1", self.command("fast"), run_tag="job-normal", manager_deadline_ns=time.monotonic_ns() + 20_000_000_000\n',
    '            str(uuid4()), "worker-1", WorkerCommand(sys.executable, ("-B", str(FIXTURE), "controlled_fast"), str(BACKEND)), run_tag="job-normal", manager_deadline_ns=time.monotonic_ns() + 20_000_000_000\n',
)
once(
    "backend/tests/fixtures/task083/job_control.py",
    'import json\nfrom pathlib import Path\n',
    'import json\nimport os\nfrom pathlib import Path\n',
)
once(
    "backend/tests/fixtures/task083/job_control.py",
    '    # 真正受控进程为 base Python；不再取会快速退出的 venv 转发器 PID。\n    proc = await asyncio.wait_for(asyncio.create_subprocess_exec(\n',
    '    # Python 3.12 Windows spawn同法绕过venv转发器，同时保留venv依赖路径。\n    child_env = os.environ.copy()\n    child_env["__PYVENV_LAUNCHER__"] = sys.executable\n    proc = await asyncio.wait_for(asyncio.create_subprocess_exec(\n',
)
once(
    "backend/tests/fixtures/task083/job_control.py",
    '        cwd=str(backend), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,\n',
    '        cwd=str(backend), env=child_env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,\n',
)
