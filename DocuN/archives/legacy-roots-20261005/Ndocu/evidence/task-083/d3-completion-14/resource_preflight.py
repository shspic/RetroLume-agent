"""完整14字段最小实测与精确资源只读预检，所有耗时记账。"""
import json
from pathlib import Path
import socket
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'Ndocu/evidence/task-083/d3-repair-11'))
import runner

if __name__=='__main__':
    started=time.monotonic()
    evidence=Path(__file__).parent
    runner.RESOURCE_LOG=evidence/'preflight-resource-commands.jsonl'
    if runner.RESOURCE_LOG.exists(): raise RuntimeError('preflight evidence already exists')
    state={'start_utc':runner.utc(),'pass':False}
    try:
        deadline=started+55
        value=runner.inspect((deadline,),reserve=0,limit=20)
        state['identity']=value
        if not runner.valid_identity(value) or value['running']: raise RuntimeError('exact stopped identity not confirmed')
        result=runner.docker(['ps','--filter','label=retrolume-task=083','--format','{{.ID}}'],(deadline,),reserve=0,limit=15)
        if result.returncode or result.stdout.strip(): raise RuntimeError('active task083 resource or unknown ownership')
        with socket.socket() as sock: sock.bind(('127.0.0.1',runner.PORT))
        state.update(pass_=True,port_free=True)
        state['pass']=True
    except BaseException as exc:
        state['error']=f'{type(exc).__name__}: {exc}'
    finally:
        state.update(end_utc=runner.utc(),seconds=time.monotonic()-started)
        (evidence/'preflight.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
    print(json.dumps(state,indent=2))
    sys.exit(not state['pass'])
