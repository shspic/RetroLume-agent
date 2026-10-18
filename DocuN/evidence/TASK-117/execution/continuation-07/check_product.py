"""实现收齐后的受影响检查批，不开PG或浏览器根。"""
from control import N,ROOT,py,run,write,sample
checks=[('backend-targeted',py()+['-m','unittest','-v','test_step018_control_snapshot','test_step018_flows','test_step018_embedding_contracts','test_step018_audit_repairs']),
        ('typecheck',['C:/Program Files/nodejs/node.exe',str(ROOT/'frontend/node_modules/typescript/bin/tsc'),'--noEmit','-p',str(ROOT/'frontend/tsconfig.json')])]
rows=[]
for label,command in checks:
    code=run(command,label,timeout=120);rows.append({'label':label,'command':command,'exit_code':code})
write(N/'product-checks.json',{'sample':sample(),'checks':rows})
raise SystemExit(any(row['exit_code'] for row in rows))
