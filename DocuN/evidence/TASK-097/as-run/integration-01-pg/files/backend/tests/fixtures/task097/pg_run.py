"""真实PG/HTTP合并阶段，原始输出由统一runner保存。"""
import json
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/"backend"));sys.path.insert(0,str(ROOT/"DocuN/evidence/TASK-097"))
from artifacts import write,imported_modules
from tests.fixtures.task097.network import install
install()
suite=unittest.defaultTestLoader.loadTestsFromNames(["tests.test_learning_pg","tests.test_learning_api"])
result=unittest.TextTestRunner(verbosity=2).run(suite)
write(Path(os.environ["RETROLUME_TASK097_OUT"])/"pg-summary.json",{"tests":result.testsRun,"skipped":result.skipped,
    "failures":len(result.failures),"errors":len(result.errors),"modules":imported_modules()})
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
