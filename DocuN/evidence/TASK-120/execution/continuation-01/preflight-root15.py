"""Static closed-plan/source checks, cached JS syntax and actual memory only."""
import ast,hashlib,json,subprocess,shutil
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from tests.fixtures.task120.queued import read_plan
files=[]
for path in sorted((ROOT/'backend/tests/fixtures/task120').glob('*.py')):
    ast.parse(path.read_text(encoding='utf-8-sig'));files.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
script=ROOT/'frontend/tests/task120-ui-continuation.mjs'
subprocess.run([shutil.which('node'),'--check',str(script)],check=True,timeout=10)
plan=read_plan(Path(__file__).resolve().parent/'plan-root-15.json')
sample={'utc':r.utc(),'available_bytes':r.available_memory(),'kind':'actual_readonly_sample_not_a_future_start_permission'}
proof={'syntax':'PASS','plan':plan,'files':files,'browser_fixture_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'memory':sample,'PG_started':False,'browser_started':False}
r.write(Path(__file__).resolve().parent/'root15-offline-preflight.json',proof)
print(json.dumps({'syntax':'PASS','stage_seconds':sum(x['seconds'] for x in plan['stages']),'memory':sample}))
