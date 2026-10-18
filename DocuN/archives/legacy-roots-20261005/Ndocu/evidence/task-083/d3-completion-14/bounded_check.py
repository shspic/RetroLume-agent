"""离线命令统一60秒上限，保留原始输出和累计时长。"""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

root=Path(__file__).resolve().parents[4]
out=Path(__file__).parent
label=sys.argv[1]
script=out/'offline_checks.py'
command=[str(root/'backend/.venv/Scripts/python.exe'),'-B',str(script)]
if (out/(label+'.json')).exists(): raise RuntimeError('no overwrite')
record={'command':command,'cwd':str(root),'start_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest()}
start=time.monotonic()
try:
    result=subprocess.run(command,cwd=root,capture_output=True,timeout=60)
    (out/(label+'.stdout.log')).write_bytes(result.stdout)
    (out/(label+'.stderr.log')).write_bytes(result.stderr)
    record['exit']=result.returncode
except subprocess.TimeoutExpired as exc:
    (out/(label+'.stdout.log')).write_bytes(exc.stdout or b'')
    (out/(label+'.stderr.log')).write_bytes(exc.stderr or b'')
    record.update(exit=1,timeout=True)
record.update(seconds=time.monotonic()-start,end_utc=datetime.now(timezone.utc).isoformat())
(out/(label+'.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
sys.exit(record['exit'])
