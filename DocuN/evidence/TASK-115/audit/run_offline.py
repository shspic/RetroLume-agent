"""先计本卡尝试和真实时间，再运行一个有界离线诊断根。"""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from bootstrap import ROOT,AUDIT,save

def event(kind,**values):
    path=AUDIT/'control/events.jsonl'
    with path.open('a',encoding='utf-8') as stream:
        stream.write(json.dumps({'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'mono_ns':time.monotonic_ns(),
                                'kind':kind,**values},ensure_ascii=False)+'\n')
        stream.flush();os.fsync(stream.fileno())

def main():
    receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
    attempt=sys.argv[1] if len(sys.argv)>1 else '01'
    if attempt=='01':
        assert receipt['new_counts']['roots']<receipt['limits']['roots']
        receipt['new_counts']['roots']+=1
    save('control/receipt.json',receipt)
    arguments=[str(ROOT/'backend/.venv/Scripts/python.exe'),'-B','-X','utf8',str(AUDIT/'offline_cases.py'),attempt]
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    label='A1-offline-file-handler-boundaries'
    event('root.begin' if attempt=='01' else 'root.resume',label=label,attempt=attempt,arguments=arguments,timeout_seconds=60)
    begin=time.monotonic();code=None
    log=AUDIT/'control'/('offline-A1-'+attempt+'.log')
    try:
        with log.open('xb') as stream:
            result=subprocess.run(arguments,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=60,
                 creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            code=result.returncode
    finally:
        seconds=time.monotonic()-begin
        receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
        receipt['new_counts']['offline_test_seconds']+=seconds
        save('control/receipt.json',receipt)
        event('root.end',label=label,exit_code=code,seconds=seconds,log=str(log))
    print(json.dumps({'exit_code':code,'seconds':seconds,'log':str(log)}))
    raise SystemExit(code)

if __name__=='__main__':main()
