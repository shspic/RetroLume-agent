"""只复检受typed消息规范化夹具修正影响的模型用例。"""
from control import N,ROOT,py,run,write,sha,sample
paths=['backend/tests/test_step018_audit_repairs.py','backend/app/capabilities/gateway.py','backend/app/capabilities/embedding.py']
write(N/'model-v2-as-run.json',{'sample':sample(),'files':[{'path':p,'sha256':sha((ROOT/p).read_bytes())} for p in paths],
 'correction':'fixture消息摘要按真实adapter的typed Message规范化，补默认空tool_calls；未改网关实现或降低断言'})
code=run(py()+['-m','unittest','-v','test_step018_audit_repairs.AuditModelScopeTests'],'model-scope-v2',timeout=30)
write(N/'model-v2-result.json',{'sample':sample(),'exit_code':code})
raise SystemExit(code)
