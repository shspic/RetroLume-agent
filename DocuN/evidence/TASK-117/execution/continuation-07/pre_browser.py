"""首根前仅核当前脚本语法、闭合路由与正式字节身份。"""
import ast
import json
from control import N,ROOT,py,run,write,sample,sha,guard
guard();ast.parse((N/'runtime.py').read_text(encoding='utf-8'))
code=run(['C:/Program Files/nodejs/node.exe',str(ROOT/'frontend/tests/step018-s08.mjs'),'--contract-check'],'browser-contract-final',timeout=20)
paths=['frontend/tests/step018-s08.mjs','frontend/src/activities/TeachingWorkspace.tsx','frontend/src/activities/teachingIntents.ts','frontend/src/activities/teachingApi.ts',
 'frontend/src/activities/InterviewWorkspace.tsx','frontend/src/activities/ActivityWorkspace.tsx','frontend/src/activities/RetrievalPanel.tsx','frontend/src/activities/retrieval-api.ts']
write(N/'browser-as-run.json',{'sample':sample(),'contract_exit_code':code,'script_and_source':[{'path':p,'sha256':sha((ROOT/p).read_bytes())} for p in paths],
 'bundle':json.loads((N/'bundle-8.json').read_text(encoding='utf-8')),'root_watchdog_sha256':sha((N/'runtime.py').read_bytes()),
 'barrier':'真实IndexedDB commit后、native oncomplete回调前；同activity正常只读刷新，不替换产品guard',
 'lowest_transport':'合成HTTP，仅静态dist/有限fixture；无实际后端、PG、供应商或费用',
 'ownership':'CREATE_SUSPENDED→准确Job→resume；Job kill-on-close；双层截止/压力/父退出/stdin EOF；PID+birth全程采样'})
raise SystemExit(code)
