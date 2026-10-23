"""累计批03；只运行已冻结名单，复用原空junction，禁止真实连接与运行时。"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
root = Path(sys.argv[1])
evidence = Path(__file__).absolute().parent
sys.path[:0] = [str(root / "backend"), str(root / "backend/.venv/Lib/site-packages")]
selection = json.loads((evidence / "batch-03-selection.json").read_text(encoding="utf-8"))
denied, mkdir_requests = [], []
scratch = root / "DocuN/evidence/TASK-125/execution/scratch"


def audit(event, args):
    if event in ("socket.__new__", "socket.connect", "socket.bind", "socket.getaddrinfo", "socket.gethostbyname",
                 "subprocess.Popen", "os.system", "os.startfile"):
        denied.append(event)
        raise RuntimeError("offline_effect_rejected")
    if event == "import" and args[0] in ("app.main", "app.data_exit.control", "app.data_exit.config", "app.q_authority"):
        denied.append("runtime_import")
        raise RuntimeError("offline_runtime_rejected")
    if event == "os.mkdir":
        path = Path(args[0]).absolute()
        if path.is_relative_to(scratch):
            mkdir_requests.append(str(path))


sys.addaudithook(audit)
import psycopg


def no_connection(*args, **kwargs):
    denied.append("psycopg_connection_entry")
    raise RuntimeError("offline_connection_rejected")


psycopg.connect = no_connection
psycopg.Connection.connect = classmethod(no_connection)
spec = importlib.util.spec_from_file_location("test_normal_install", root / "backend/tests/test_normal_install.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
records = []


class Result(unittest.TextTestResult):
    def startTest(self, test):
        self.started = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        records.append({"test": test.id(), "elapsed_seconds": time.perf_counter() - self.started, "case_directory": str(test.work)})
        super().stopTest(test)


started = time.perf_counter()
suite = unittest.TestSuite(module.NormalInstallTests(name) for name in selection["selected_methods"])
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
summary = {"cumulative_batch": 3, "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
           "skipped": len(result.skipped), "elapsed_seconds": time.perf_counter() - started, "denied_effect_attempts": denied,
           "selected_methods": selection["selected_methods"], "records": records, "driver_version": psycopg.__version__,
           "new_directories": [path for path in mkdir_requests if Path(path).is_dir()],
           "guards": ["Python socket/DNS/process audit", "psycopg.connect and Connection.connect blocked",
                      "only new hostaddr test replaces top driver alias with parameter recorder", "runtime imports blocked"],
           "observations": module.REPAIR_OBSERVATIONS,
           "scope": "参数及文件元数据/本地控制流；不证明实际TCP/认证、PG事务/权限或对手并发竞态"}
(evidence / "batch-03-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if result.wasSuccessful() else 1)
