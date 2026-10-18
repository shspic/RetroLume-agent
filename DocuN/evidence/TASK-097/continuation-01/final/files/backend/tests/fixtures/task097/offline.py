"""离线检查入口，记录实际导入模块hash，不启动监督或连接PG。"""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "DocuN/evidence/TASK-097"))
from artifacts import imported_modules, write

suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[2:])
result = unittest.TextTestRunner(verbosity=2).run(suite)
write(Path(sys.argv[1]), {"modules": imported_modules(), "tests":result.testsRun, "skipped":result.skipped,
    "failure_count":len(result.failures), "error_count":len(result.errors)})
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
