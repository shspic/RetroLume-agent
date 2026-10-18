from metadata import *
ledger_path=ROOT/'DocuN/evidence/TASK-104/runtime-ledger.json';ledger=load(ledger_path)
extra=load(OWN/'closed-stdin-runner-stop-powershell.json')
if not any(x.get('kind')=='补记已停止的闭stdin辅助进程' for x in ledger['events']):
    ledger['used']['cleanup']+=extra['elapsed_seconds']
    ledger['events'].append({'at':stamp(),'kind':'补记已停止的闭stdin辅助进程','elapsed':extra['elapsed_seconds'],'source':str(OWN/'closed-stdin-runner-stop-powershell.json'),'actual_remaining_old_pids':[x for x in extra['remaining_old_pids'] if x is not None]})
    ledger_path.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert ledger['counts']['entry']==ledger['counts']['fixture_offline']==3
assert ledger['counts']['browser']==ledger['counts']['driver']==0
assert ledger['used']['real']<600 and ledger['used']['cleanup']<300 and ledger['used']['fixture_offline']<300
save('runtime-stop-diagnosis.json',{'at':stamp(),'root1':'命名卷Binds误判，启动0，原异常栈未保存；已留实际字段诊断','root2':'fixture参数SQL百分号未转义，普通DB只读前置失败，口令/监听/浏览器0','root3':'actual_get给/api/session带18103 Origin，当前local_request不默认允许该Origin；实际非200，原HTTP状态正文未保存，403为B级确定推导','last_citation':'NOT_RUN；没有浏览器引用GET、DOM、截图和DB末后快照，不能补签','permit_remaining_root':0,'all_business_POST':0,'password_reset_once':1,'business_db_write':0,'infrastructure_exception':'允许的retrolume_task103_app RAM口令一次重置，非秘密属性/ACL由同根前后核不变','control_counts':ledger['counts'],'known_seconds':ledger['used'],'metadata_failures_retained':['wrong TASK102 decision directory rg','missing C02 runtime-configs path read','backend cwd rg frontend path','write_stdin closed','cleanup helper ModuleNotFoundError before action; native known-pid cleanup succeeded']})
finish('all-runtime-attempts-stopped-and-accounted',{'counts':ledger['counts'],'seconds':ledger['used'],'citation':'NOT_RUN','business_write':0})
