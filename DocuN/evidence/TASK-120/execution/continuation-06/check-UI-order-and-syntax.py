from pathlib import Path
import ast,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[5];HERE=Path(__file__).resolve().parent
for p in [*HERE.glob('*.py'),*(ROOT/'backend/tests/fixtures/task120').glob('*.py')]:ast.parse(p.read_text(encoding='utf-8-sig'),str(p))
assert shutil.which('npx') and shutil.which('node')
result=subprocess.run(['node','--check',str(ROOT/'frontend/tests/task120-continuation06-ui.mjs')],capture_output=True,timeout=10)
assert result.returncode==0,result.stderr.decode('utf-8')
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120.queued import read_plan
plan=read_plan(HERE/'plan-45.json');assert plan['root_id']==45
assert (HERE/'UI-order-preflight.md').is_file()
assets=[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()]
(HERE/'formal-bundle-identities.json').write_text(json.dumps({'build_receipt':'command-063.receipt.json','assets':assets,'actual_JS_CSS_binding':'to be recorded by real browser responses'},indent=2),encoding='utf-8')
(HERE/'UI-prestart-check.json').write_text(json.dumps({'status':'PASS_OFFLINE_ONLY','finite_plan':plan,'node_syntax':True,'npx_available':True,'factory_not_created_by_this_check':True,'response_order':'two normal actual approved GETs before backup/freeze; separate full-context and namespace checkpoints'},indent=2),encoding='utf-8')
print('UI order, finite ownership cleanup, AST, JS syntax and formal bundle identity saved; no runtime started')
