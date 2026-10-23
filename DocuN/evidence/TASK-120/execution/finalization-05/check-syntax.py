from pathlib import Path
import ast,json,sys
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'backend'))
HERE=Path(__file__).resolve().parent
files=[*HERE.glob('*.py'),*(ROOT/'backend/tests/fixtures/task120').glob('*.py')]
for p in files:ast.parse(p.read_text(encoding='utf-8-sig'),str(p))
from tests.fixtures.task120.queued import read_plan
plan=read_plan(HERE/'plan-25.json');assert plan['root_id']==25
(HERE/'syntax-check.json').write_text(json.dumps({'status':'PASS','parsed_files':len(files),'closed_finalization_plan':True}),encoding='utf-8')
print('syntax and closed finalization plan PASS')
