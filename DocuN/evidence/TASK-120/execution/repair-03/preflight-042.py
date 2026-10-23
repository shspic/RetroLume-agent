from pathlib import Path
import unittest, runpy, json, py_compile
ROOT=Path(__file__).resolve().parents[5];HERE=Path(__file__).resolve().parent
suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_task120_repair03')
result=unittest.TextTestRunner(verbosity=2).run(suite)
(HERE/'lock-control-flow-tests.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'PG_evidence':False}),encoding='utf-8')
if not result.wasSuccessful():raise SystemExit(1)
runpy.run_path(str(HERE/'entry-stop-check.py'),run_name='__main__')
