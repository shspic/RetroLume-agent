from pathlib import Path
import ast,json,unittest,difflib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
from tests.fixtures.task120.queued import read_plan
suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_task120_repair03')
result=unittest.TextTestRunner(verbosity=2).run(suite)
(HERE/'repair-tests-045.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'PG_evidence':False}),encoding='utf-8')
if not result.wasSuccessful():raise SystemExit(1)
for p in (ROOT/'backend/tests/fixtures/task120').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
read_plan(HERE/'plan-root-18.json')
for name in ('creation-memory.json','identity.json','q-root.json'):
    json.loads((ROOT/'.runtime/TASK-120/budget-02'/name).read_text(encoding='utf-8'))
diff=[]
for rel in ['backend/app/data_exit/q_store.py','backend/app/capabilities/q_context.py','backend/app/interview/policy.py','backend/app/activities/interview_repository.py']:
    before=(HERE/'preimage'/rel).read_text(encoding='utf-8-sig');after=(ROOT/rel).read_text(encoding='utf-8-sig')
    diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before/'+rel,tofile='after/'+rel))
(HERE/'source-pre-root18.diff').write_text(''.join(diff),encoding='utf-8')
print(json.dumps({'closed_plan':18,'UTF8_saved_inputs':'PASS','finite_product_diff_saved':True,'no_PG':True}))
