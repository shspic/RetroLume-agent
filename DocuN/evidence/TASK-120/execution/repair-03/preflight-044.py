from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
from tests.fixtures.task120.queued import read_plan
plan=read_plan(HERE/'plan-root-17.json')
for name in ('repair03.py','queued.py','run.py','api_runtime.py'):
    ast.parse((ROOT/'backend/tests/fixtures/task120'/name).read_text(encoding='utf-8-sig'))
for name in ('runtime_control.py','entry-stop-check.py','final-stop-check.py'):ast.parse((HERE/name).read_text(encoding='utf-8'))
print(json.dumps({'plan_root':plan['root_id'],'bounded_readonly':True,'syntax':'PASS','no_runtime':True}))
