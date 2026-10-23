from pathlib import Path
import ast,json,unittest,subprocess,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('tests.test_task120_repair03'))
(HERE/'repair-tests-050.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'final_product_bytes_checked':True,'new_PG':False}),encoding='utf-8')
for p in (ROOT/'backend/tests/fixtures/task120').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
subprocess.run([shutil.which('node'),'--check',str(ROOT/'frontend/tests/task120-ui-continuation.mjs')],check=True,timeout=10)
body=(HERE/'final-stop-check.py').read_text(encoding='utf-8')
exec(compile(body,str(HERE/'final-stop-check.py'),'exec'),{'__file__':str(HERE/'final-stop-check.py'),'__name__':'__main__'})
if not result.wasSuccessful():raise SystemExit(1)
