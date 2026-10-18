"""登记本卡补充合同和精确已验关闭身份，不生成认证key。"""
from control import ROOT,HERE,event,sha,write,guard
guard()
notice=ROOT/'DocuN/evidence/TASK-117/orchestration-preview-config-20261014/notice.md'
expected={'DocuN/results/TASK-112-result.md':'1dab1126aa72e335288d037baed5bc13b7cfdc1e4a386b6c04553e630f871571',
 'backend/app/preview/host_policy.py':'7c54c0d4574ecfd9edd2b2a70821a731d3f219df3c7abf5bd14e17d8acb90b83',
 'backend/app/preview/pipe.py':'db2a742a559d7905012273e9fd9acaec441a549e12d71fa8ac77a3f486d3f974',
 'backend/app/preview/production_supervisor.py':'d6870137371caf003412fc4089bfc1e0dcf6ecf859ee05633fd5024d894c6d58'}
rows=[]
for path,value in expected.items():
    actual=sha((ROOT/path).read_bytes())
    if actual!=value:raise RuntimeError('冻结身份不符：'+path)
    rows.append({'path':path,'sha256':actual,'same':True})
value={'notice_path':str(notice),'notice_sha256':sha(notice.read_bytes()),'identities':rows,'operator_handoff':'新合成配置的受托operator认证已授权；沿原loader，不自签新独审','runtime_checked':False}
write(HERE/'preview-notice.json',value);event('contract_addendum_received',**value)
print('Preview operator handoff recorded; four frozen identities match; budget unchanged')
