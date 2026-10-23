"""本卡集中离线批；隔离站点后只加入已安装项目依赖。"""
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

root = Path(sys.argv[1])
evidence = Path(__file__).absolute().parent
sys.path[:0] = [str(root / "backend"), str(root / "backend/.venv/Lib/site-packages")]
denied = []


def audit(event, args):
    if event in ("socket.__new__", "socket.connect", "socket.bind", "subprocess.Popen", "os.system", "os.startfile"):
        denied.append(event)
        raise RuntimeError("offline_effect_rejected")
    if event == "import" and args[0] in ("app.main", "app.data_exit.control", "app.data_exit.config", "app.q_authority"):
        denied.append("runtime_import")
        raise RuntimeError("offline_runtime_rejected")


sys.addaudithook(audit)
import psycopg


def no_connection(*args, **kwargs):
    denied.append("psycopg.connect")
    raise RuntimeError("offline_connection_rejected")


psycopg.connect = no_connection
spec = importlib.util.spec_from_file_location("test_normal_install", root / "backend/tests/test_normal_install.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
records = []


class Result(unittest.TextTestResult):
    def startTest(self, test):
        self.started = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        records.append({"test": test.id(), "elapsed_seconds": time.perf_counter() - self.started})
        super().stopTest(test)


started = time.perf_counter()
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromModule(module))
summary = {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
           "skipped": len(result.skipped), "elapsed_seconds": time.perf_counter() - started, "denied_effect_attempts": denied,
           "real_pg_connections": 0, "network_operations": 0, "records": records,
           "scope": "离线本地控制流、原件与现有纯核验样本；不证明真实 PG SQL、事务、ACL 或部署成功"}
(evidence / "batch-02-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if result.wasSuccessful() else 1)
