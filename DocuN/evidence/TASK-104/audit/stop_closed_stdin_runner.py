import json,time
from pathlib import Path
from tests.fixtures.task104.common import EVIDENCE,Control,process_one,stop_witness,write,stamp
started=time.monotonic(); witnesses=[]
for pid in (42564,20508):
    value=process_one(pid)
    if value is not None:
        assert '-m tests.fixtures.task104.run_readonly' in value['command']
        assert value['created'].startswith('2026-10-07T10:05:31.')
        witnesses.append(value)
write(EVIDENCE/'audit/closed-stdin-runner-witnesses.json',{'at':stamp(),'witnesses':witnesses,'reason':'工具普通pipe stdin已关闭，root2资源已全部收尾且password_reset=0，仅停本卡等待输入的控制进程'})
out=[stop_witness(v) for v in witnesses]
control=Control();elapsed=time.monotonic()-started;control.state['used']['cleanup']+=elapsed;control.state['events'].append({'at':stamp(),'kind':'关闭stdin的自有runner收尾','elapsed':elapsed,'results':out});control.save()
write(EVIDENCE/'audit/closed-stdin-runner-stop.json',{'at':stamp(),'results':out,'seconds':elapsed})
print(json.dumps({'results':out,'seconds':elapsed,'counts':control.state['counts']},ensure_ascii=False))
