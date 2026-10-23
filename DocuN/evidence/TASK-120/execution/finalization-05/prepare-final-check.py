from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4]
body=(HERE/'initial-stop-check.py').read_text(encoding='utf-8')
body=body.replace("HERE/'initial-stop-proof.json'","HERE/'final-stop-proof.json'")
body=body.replace("for slot in ('flow','budget-01','budget-02'):","for slot in ('flow','budget-01','budget-02','matrix-final'):")
body=body.replace("*(EX/'repair-03').glob('command-*.receipt.json'),*HERE.glob", "*(EX/'repair-03').glob('command-*.receipt.json'),*(EX/'validation-04').glob('command-*.receipt.json'),*HERE.glob")
body=body.replace("            if type(pid) is int and pid>0", "            if isinstance(stamp,dict):stamp=stamp.get('birth')\n            if type(pid) is int and pid>0")
body=body.replace("# Read only these two registered private control files.","for directory in (EX/'validation-04',HERE):\n    for sample in directory.glob('root-*-memory-samples.jsonl'):\n        for line in sample.read_text(encoding='utf-8').splitlines():\n            if line.strip():collect(json.loads(line),'exact-owned-memory-sample:'+sample.name)\n# Read only these registered private control files.")
(HERE/'final-stop-check.py').write_text(body,encoding='utf-8')
manifest={'label':'final05-exact-final-stop','seconds':60,'argv':[str(ROOT/'backend/.venv/Scripts/python.exe'),str(HERE/'final-stop-check.py')],'cwd':'.'}
(HERE/'command-058.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('已准备精确只读最终StopProof，不启动资源。')
