"""Add pure fake-process launcher tests; no OS process is started."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "backend/tests/fixtures/task083/offline_unit.py"
data = path.read_text(encoding="utf-8")
old_import = "from app.activities import ActivityLease, CloseResult, SettleResult, WindowSnapshot\n"
new_import = "from app.activities import ActivityLease, CloseResult, PostgresAdmissionLedger, SettleResult, WindowSnapshot\nfrom app.worker.launcher import run_supervised_window\n"
assert data.count(old_import) == 1
data = data.replace(old_import, new_import)
old_end = '\n\nif __name__ == "__main__":\n'
extra = '''\n\nclass LauncherUnitTests(unittest.TestCase):
    def test_08_fake_process_timeout_terminates_exact_owner_without_charge_claim(self):
        class Pipe:
            def close(self): pass
            def poll(self, timeout): return False

        class Process:
            def __init__(self):
                self.alive = True
                self.calls = []
                self.exitcode = None

            def start(self): self.calls.append("start")
            def join(self, timeout): self.calls.append("join")
            def is_alive(self): return self.alive
            def terminate(self): self.calls.append("terminate"); self.alive = False
            def kill(self): self.calls.append("kill"); self.alive = False
            def close(self): self.calls.append("close")

        class Context:
            def __init__(self): self.process = Process()
            def Pipe(self, duplex): return Pipe(), Pipe()
            def Process(self, **kwargs): return self.process

        context = Context()
        with patch("app.worker.launcher.multiprocessing.get_context", return_value=context):
            result = run_supervised_window(
                PostgresAdmissionLedger("synthetic-not-connected"),
                SessionConfig(), str(uuid4()), "worker-1",
                WorkerCommand(sys._base_executable, ("-B", "-c", "pass"), str(BACKEND)),
                run_tag="offline-launcher",
            )
        self.assertEqual(result.state, "manager_timeout_unconfirmed")
        self.assertIsNone(result.reserved_seconds)
        self.assertIn("terminate", context.process.calls)
        self.assertNotIn("kill", context.process.calls)

'''
assert data.count(old_end) == 1
data = data.replace(old_end, extra + old_end)
path.write_text(data, encoding="utf-8", newline="")
