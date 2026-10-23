"""Necessary syntax/finite-plan/readonly-stop preflight, no service startup."""
import ast,hashlib,json,runpy,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from tests.fixtures.task120.queued import read_plan
from app.interview.contracts import SourceBinding
from app.memory.contracts import MemorySelectionInput
assert set(SourceBinding.model_fields)=={'source_id','version_id','source_revision','original_sha256'}
files=[]
for folder in (ROOT/'backend/tests/fixtures/task120',HERE):
    for path in sorted(folder.glob('*.py')):
        ast.parse(path.read_text(encoding='utf-8-sig'));files.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
for path in (ROOT/'backend/app/capabilities/q_context.py',ROOT/'backend/app/capabilities/q_protocol.py'):
    ast.parse(path.read_text(encoding='utf-8-sig'))
node=shutil.which('node');assert node and shutil.which('npx')
script=ROOT/'frontend/tests/task120-ui-continuation.mjs'
subprocess.run([node,'--check',str(script)],check=True,timeout=10)
plan=read_plan(HERE/'plan-root-15.json')
assert sum(s['seconds'] for s in plan['stages'])<=1680
runpy.run_path(str(HERE/'check-stop.py'))
proof={'syntax':'PASS','plan':plan,'files':files,'browser_fixture_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'available_bytes':r.available_memory(),'PG_started':False,'API_started':False,'Browser_started':False,'old_command038_not_executed':True}
r.write(HERE/'preflight-039-result.json',proof)
print(json.dumps({'syntax':'PASS','finite_plan_seconds':sum(s['seconds'] for s in plan['stages']),'available_bytes':proof['available_bytes'],'no_runtime_started':True}))
