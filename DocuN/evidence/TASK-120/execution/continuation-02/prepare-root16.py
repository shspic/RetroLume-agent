"""Filesystem-only save last-root plan and new preflight identities."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
plan=json.loads((HERE/'plan-root-15.json').read_text());plan['root_id']=16
(HERE/'plan-root-16.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
body=(HERE/'check-stop.py').read_text().replace("HERE/'entry-stop-proof.json'","HERE/'stop-before-root16.json'")
(HERE/'check-stop-16.py').write_text(body,encoding='utf-8')
body=(HERE/'preflight-039.py').read_text().replace('plan-root-15.json','plan-root-16.json').replace('check-stop.py','check-stop-16.py').replace('preflight-039-result.json','preflight-040-result.json')
(HERE/'preflight-040.py').write_text(body,encoding='utf-8')
(HERE/'command-040.json').write_text(json.dumps({'label':'scope02-corrected-observer-final-preflight','seconds':60,'cwd':'backend','argv':[str(HERE.parents[4]/'backend/.venv/Scripts/python.exe'),str(HERE/'preflight-040.py')]}),encoding='utf-8')
print('Saved independent last-root plan and preflight040; no runtime.')
