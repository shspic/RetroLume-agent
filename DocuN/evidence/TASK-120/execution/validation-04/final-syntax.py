from pathlib import Path
import py_compile,subprocess,json
root=Path.cwd()
for f in [root/'backend/app/activities/teaching_repository.py',*(root/'backend/tests/fixtures/task120').glob('*.py')]:py_compile.compile(str(f),doraise=True)
r=subprocess.run(['node','--check',str(root/'frontend/tests/task120-ui-continuation.mjs')],timeout=15)
(root/'DocuN/evidence/TASK-120/execution/validation-04/final-syntax-result.json').write_text(json.dumps({'exit_code':r.returncode,'PG_API_Browser':0}),encoding='utf-8')
raise SystemExit(r.returncode)
