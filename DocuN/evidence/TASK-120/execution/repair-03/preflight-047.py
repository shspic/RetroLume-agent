from pathlib import Path
import ast,json,unittest,difflib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
from tests.fixtures.task120.queued import read_plan
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('tests.test_task120_repair03'))
(HERE/'repair-tests-047.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'PG_evidence':False}),encoding='utf-8')
if not result.wasSuccessful():raise SystemExit(1)
for p in (ROOT/'backend/tests/fixtures/task120').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
read_plan(HERE/'plan-root-19.json')
diff=[]
for rel in ['backend/app/data_exit/q_store.py','backend/app/capabilities/q_context.py','backend/app/capabilities/q_gateway.py','backend/app/interview/policy.py','backend/app/activities/interview_repository.py']:
    before=(HERE/'preimage'/rel).read_text(encoding='utf-8-sig');after=(ROOT/rel).read_text(encoding='utf-8-sig')
    diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before/'+rel,tofile='after/'+rel))
(HERE/'source-pre-root19.diff').write_text(''.join(diff),encoding='utf-8')
body=(HERE/'final-stop-check.py').read_text(encoding='utf-8').replace("'final-stop-proof.json'","'entry-root19-stop.json'")
exec(compile(body,str(HERE/'final-stop-check.py'),'exec'),{'__file__':str(HERE/'final-stop-check.py'),'__name__':'__main__'})
print(json.dumps({'closed_plan':19,'direct_read_closures':'teaching/interview/HTML','no_PG_started':True}))
