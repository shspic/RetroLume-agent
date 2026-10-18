"""Adapt pre-existing synthetic tests; no tests or Job are run by this script."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "backend/tests/test_worker_session.py"
data = path.read_text(encoding="utf-8")


def once(old: str, new: str) -> None:
    global data
    assert data.count(old) == 1, (old, data.count(old))
    data = data.replace(old, new)


once("import ctypes\n", "import ctypes\nimport json\n")
once("from app.worker.gate import ClosingCallGate, GateClosed\n", "from app.worker.command import WorkerCommand\nfrom app.worker.gate import ClosingCallGate, GateClosed\n")
once("from app.worker.windows_job import JobUnknown, NamedJob\n", "from app.worker.windows_job import JobUnknown, NamedJob\n")
once(
    "    def config(self):\n        return SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1, startup_limit_seconds=2)\n\n    async def test_claim_response_lost_and_partial_window_never_spawn(self):",
    "    def config(self):\n        return SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1, startup_limit_seconds=2)\n\n    def command(self):\n        return WorkerCommand(sys._base_executable, (\"-B\", str(FIXTURE), \"fast\"), str(BACKEND))\n\n    async def test_claim_response_lost_and_partial_window_never_spawn(self):",
)
once("lambda _: [sys.executable], cwd=str(BACKEND), run_tag=\"unit-no-spawn\"", "self.command(), run_tag=\"unit-no-spawn\", manager_deadline_ns=time.monotonic_ns() + 20_000_000_000")
once("lambda _: [sys.executable], cwd=str(BACKEND), run_tag=\"unit-old-unknown\"", "self.command(), run_tag=\"unit-old-unknown\", manager_deadline_ns=time.monotonic_ns() + 20_000_000_000")
once("        return [sys._base_executable, \"-B\", str(FIXTURE), mode]\n", "        return WorkerCommand(sys._base_executable, (\"-B\", str(FIXTURE), mode), str(BACKEND))\n")
once("lambda _: self.command(\"fast\"), cwd=str(BACKEND), run_tag=\"job-normal\"", "self.command(\"fast\"), run_tag=\"job-normal\", manager_deadline_ns=time.monotonic_ns() + 20_000_000_000")
once("lambda _: self.command(\"hang\"), cwd=str(BACKEND), run_tag=\"job-hang\"", "self.command(\"hang\"), run_tag=\"job-hang\", manager_deadline_ns=time.monotonic_ns() + 20_000_000_000")
once("self.assertGreaterEqual(outcome.charged_seconds, 1)", "self.assertGreaterEqual(outcome.settled_seconds, 1)")
once("self.assertEqual(outcome.charged_seconds, 6)", "self.assertEqual(outcome.reserved_seconds, 6)\n        self.assertEqual(outcome.pending_fold_seconds, 6)\n        self.assertEqual(outcome.settled_seconds, 0)")
once("job.spawn_suspended(self.command(\"parent\"), cwd=str(BACKEND))", "job.spawn_suspended(self.command(\"parent\").argv(), cwd=str(BACKEND))")
start = data.index("    async def test_04_supervisor_death_closes_last_job_handle(self):\n")
end = data.index("    async def test_05_same_name_collision_fails_closed(self):\n", start)
data = data[:start] + (
    "    async def test_04_supervisor_death_closes_last_job_handle(self):\n"
    "        from fixtures.task083.job_control import verify_last_handle\n"
    "        result = await verify_last_handle(FIXTURE, BACKEND)\n"
    "        print(json.dumps(result))\n\n"
) + data[end:]
once("        self.assertEqual(ledger.events, [\"inspect\", \"claim\", \"close_db\", \"settle\"])\n", "        self.assertEqual(ledger.events, [\"inspect\", \"claim\", \"close_db\", \"settle\"])\n        print(json.dumps(outcome.__dict__))\n")
once("        self.assertNotIn(\"settle\", ledger.events)\n", "        self.assertNotIn(\"settle\", ledger.events)\n        print(json.dumps(outcome.__dict__))\n")
once("            self.assertEqual(job.active_processes(), 0)\n\n    async def test_04_", "            self.assertEqual(job.active_processes(), 0)\n            print(json.dumps({\"run_tag\": \"job-descendant\", \"activity_id\": activity_id, \"generation\": 1, \"job_name\": job.name, \"pid\": job.pid, \"created_100ns\": job.process_creation_time_100ns(), \"active_processes_at_end\": 0}))\n\n    async def test_04_")
once("            self.assertEqual(job.active_processes(), 0)\n\n\nif __name__", "            self.assertEqual(job.active_processes(), 0)\n            print(json.dumps({\"run_tag\": \"job-collision\", \"activity_id\": activity_id, \"generation\": 1, \"job_name\": job.name, \"active_processes_at_end\": 0}))\n\n\nif __name__")
path.write_text(data, encoding="utf-8", newline="")
