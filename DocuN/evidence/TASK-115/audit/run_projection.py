"""只复核不依赖恢复/取消正确性的只读投影反例，沿用 A1 诊断根。"""
import json
import os
import subprocess
import time
from bootstrap import ROOT,AUDIT,save
from run_offline import event

arguments=[str(ROOT/'backend/.venv/Scripts/python.exe'),'-B','-X','utf8',str(AUDIT/'readonly_projection_case.py')]
event('root.resume',label='A1-offline-file-handler-boundaries',method='readonly-projection',arguments=arguments,timeout_seconds=60)
start=time.monotonic();code=None
try:
    with (AUDIT/'control/readonly-projection-02.log').open('xb') as stream:
        result=subprocess.run(arguments,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=60,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        code=result.returncode
finally:
    seconds=time.monotonic()-start
    receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
    receipt['new_counts']['offline_test_seconds']+=seconds;save('control/receipt.json',receipt)
    event('root.end',label='A1-offline-file-handler-boundaries',method='readonly-projection',seconds=seconds,exit_code=code)
print(json.dumps({'exit_code':code,'seconds':seconds}))
raise SystemExit(code)
