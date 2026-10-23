"""有限工程交付裁定及下一前置任务签发，仅元数据和项目文档。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,os,re,zipfile

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
N=ROOT/'DocuN/evidence/TASK-122/orchestration-20261021'
A=ROOT/'DocuN/evidence/TASK-121/audit/review-02'
E=ROOT/'DocuN/evidence/TASK-120/execution'
STAMP=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='microseconds')
def sha(x):return hashlib.sha256(x).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(p,x):
    p=p.resolve();assert p.is_relative_to(ROOT)
    p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.closure.tmp')
    with temp.open('xb') as s:s.write(x);s.flush();os.fsync(s.fileno())
    os.replace(temp,p);assert p.read_bytes()==x
def js(p,x):put(p,(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def prefix(text,old):return (text.strip()+'\n\n').replace('\n','\r\n').encode('utf-8')+old
def item(p):return {'path':str(p.relative_to(ROOT)).replace('\\','/') if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}

assert not (OUT/'save-proof.json').exists()
assert not (ROOT/'DocuN/tasks/TASK-122.md').exists()
assert not (ROOT/'DocuN/results/TASK-122-result.md').exists()
rows=load(A/'identity-closing.json')['rows'];assert len(rows)==750
protected={}
for row in rows:
    p=Path(row['path']);actual=sha(p.read_bytes()) if p.is_file() else None
    assert actual==row['actual_sha256'],row['path']
    if actual:protected[p]=actual
rules=load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for x in rules:assert sha(Path(x['absolute_path']).read_bytes())==x['sha256']
audit=ROOT/'DocuN/results/TASK-121-result.md'
assert audit.stat().st_size==78165 and sha(audit.read_bytes())=='ffbd03ce3d5ce34ca22570aeaaafbf72c295fc09a88a1f1c2b4fdac79dc1c12f'
assert sha(audit.read_bytes()[-55795:])=='75d40d166010d29b28065327a8a911a859200d6da01cac080ab13b72748da595'
receipt=load(A/'session-receipt.json');decisions=receipt['scope_conclusion']
assert decisions['F02']=='关闭' and decisions['F03']=='关闭'
assert decisions['F01']=='保留关闭' and decisions['F04']=='保留关闭' and decisions['F05']=='保留关闭'
assert decisions['eligible_for_main_finite_slice_closure'] is True
budget_path=E/'budget.json';events_path=E/'events.jsonl'
budgetraw=budget_path.read_bytes();eventsha=sha(events_path.read_bytes());budget=load(budget_path)
assert budget['active_root'] is None and budget['active_command'] is None
assert budget['counts']['roots']==64 and budget['counts']['pg_starts']==64 and len(budget['failures'])==149
assert abs(budget['command_wall_conservative_upper_seconds']-69357.418110)<.001
assert budget['engineering_status']=='TARGETED_REPAIR08_COMPLETE_STOPPED_READY_FOR_TASK121_DELTA_REVIEW'
protected[budget_path]=sha(budgetraw);protected[events_path]=eventsha
package=E/'audit-repair-08/completed-review-candidate.zip'
assert package.stat().st_size==1341581 and sha(package.read_bytes())=='15ec6b364ca9d16e2020a2c17640a655f5074bc9464f57a6747ac239e5e62ae4'
with zipfile.ZipFile(package) as z:assert len(z.infolist())==147
stop=load(E/'audit-repair-08/final-stop-proof-completed.json')
assert stop['unresolved']==[] and len(stop['registered_processes'])==28 and len(stop['registered_jobs'])==8
adoption=load(ROOT/'DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json')
assert adoption['adopted']==['zero_DDL_Q_v2_exact_local_operator_approval_and_original_key_continue','candidate_deepseek_flash_thinking_disabled_same_endpoint_and_caps','one_future_conditional_Q_100_requests_25_CNY_roster_48_28_24']
assert adoption['global_max_requests']==100 and adoption['global_max_cost_microunits']==25000000
assert sum(r['max_requests'] for r in adoption['roster'])==100
shared=['DocuN/results/TASK-120-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuN/tasks/TASK-120.md','DocuN/tasks/TASK-121.md','DocuS/文档变更记录.MD']
old={n:(ROOT/n).read_bytes() for n in shared}
assert '文档v2.87' in old[shared[2]].decode('utf-8-sig')[:200]
assert '文档v1.59' in old[shared[1]].decode('utf-8-sig')[:200]
assert max(map(int,re.findall(r'CHG-(\d{4})',old[shared[5]].decode('utf-8-sig'))))==1590
for n,x in old.items():put(OUT/'before'/n,x)
put(OUT/'returned-ledger/budget.json',budgetraw)
js(OUT/'closure-receipt.json',{
 'recorded_at':STAMP,'task':'TASK-120','R':'R-114','STEP':'STEP018','dispatch_status':'已返回',
 'overall_task_acceptance':'部分通过，历史执行控制不通过保留',
 'finite_engineering_delivery':'通过并关闭','finite_code_axis':'通过','finite_targeted_evidence':'充分，限批准范围与独审继承边界',
 'historical_execution_control':'不通过，不追认','closed_findings':['TASK121-F01','TASK121-F02','TASK121-F03','TASK121-F04','TASK121-F05'],
 'audit_delivery_acceptance':'TASK121/R115集中独审及两轮增量交付通过并结束',
 'audit_result':item(audit),'frozen_identity_rows_rechecked':750,'rules_match':len(rules),'identity_mismatches':[],
 'sample_limit':'Explicitly adopted non-authorizing Q-body dependency fixture proves cleanup projection and recovery only; not request assembly/provenance/legal outbound',
 'inheritance':'Unchanged S, original ACK/C12/K2/UI and closed fixes stay within independently accepted scopes; no reruns',
 'stop_evidence_scope':'Original1005/1006 registered28 PID-birth,8Job,twoCID/ports and prior qualified alternatives; no live probe',
 'old_uncertain_evidence_and_failures_retained':True,'budget_counts':budget['counts'],'failures':149,'TASK117_failures':81,
 'conservative_wall_seconds':budget['command_wall_conservative_upper_seconds'],'holding_seconds':budget['runtime_holding_union_seconds'],
 'audit_conservative_tools_cumulative':receipt['cumulative_conservative_tool_charge'],
 'real_Q':'FROZEN','real_provider_and_paid_fee':0,'Q_activation_T0':None,'main_runtime':0,'product_writes':0,
 'parent_STEP018':'进行中，验证部分','STEP019_STEP020_M1_project_release':'未通过',
 'next_unit':'TASK122/R116 current official/account-metering/readiness and one operation package; no product runtime'})

contract=(N/'contract.md').read_bytes();ct=contract.decode('utf-8-sig')
for x in ('TASK-122 / R-116','100次/25元','48/28/24','token','正常','2400','24h','根README.md'):
    assert x in ct,x
assert '*' not in ct and '〈' not in ct
paths=[
 'AGENTS.md','DocuS/最终需求文档.MD','DocuN/results/TASK-119-result.md','DocuN/results/TASK-119-work-decision.md',
 'DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json',
 'DocuN/evidence/TASK-119/design/call-matrix.json',
 'DocuN/evidence/TASK-116/design/sample-inputs.json','DocuN/evidence/TASK-116/design/acceptance-contract.md',
 'DocuN/evidence/TASK-116/design/integration-contract.md','DocuN/results/TASK-121-result.md','DocuN/results/TASK-120-result.md',
 'backend/app/capabilities/embedding.py','backend/app/capabilities/q_protocol.py','backend/app/capabilities/q_context.py',
 'backend/app/capabilities/q_gateway.py','backend/app/capabilities/gateway.py','backend/app/capabilities/transport.py',
 'backend/app/service_config.py','backend/app/retrieval/service.py','backend/app/operator/q_request.py',
 'config/activity.example.json','config/integration.example.json','config/q-approval.example.json','README.md']
for p in paths:assert (ROOT/p).is_file(),p
js(N/'input-manifest.json',{'frozen_at':STAMP,'rules':rules,'inputs':[item(ROOT/p) for p in paths],
 'main_finite_closure':item(OUT/'closure-receipt.json'),'shared_versions':{'state':'2.88','architecture':'1.60','requirements':'1.4'},
 'no_claim_all_old_external_facts_current':True,'README_may_be_minimally_updated_under_contract':True})
js(N/'handoff-facts.json',{
 'task120_finite_delivery_closed':True,'task120_overall_partial_historical_control_failed':True,
 'task121_findings_all_closed':True,'audit_result_sha256':sha(audit.read_bytes()),
 'adopted_provider_candidate':'deepseek-flash, thinking disabled; current capabilities/account/price still to verify',
 'effective_future_conditional_budget':{'requests':100,'CNY_microunits':25000000,'per_reservation':250000,'roster':adoption['roster']},
 'original80_20_superseded_not_added':True,'old13_CNY_not_restored':True,'actual_Q_activated':False,
 'T0':None,'paid_Q_calls':0,'paid_Q_fee':0,'engineering_TESTONLY_budget_not_paid_Q_usage':True,
 'current_normal_loader_runtime_account_readiness':'not established by finite engineering acceptance',
 'remaining_original_musts':'TASK116 acceptance plus TASK119 call matrix, updated effective budget; static/TESTONLY not real semantic completion',
 'new_task_purpose':'Complete external facts/operation package and minimal missing user/account decisions; never repeat protocol design',
 'old_history_retained':{'engineering_counts':budget['counts'],'engineering_failures':149,'TASK117_failures':81,
  'engineering_wall_upper':budget['command_wall_conservative_upper_seconds'],'engineering_holding':budget['runtime_holding_union_seconds'],
  'audit_tools_upper':receipt['cumulative_conservative_tool_charge']},
 'all_old_runtime_resources_frozen':True,'old_investment_or_failure_counts_not_reset_by_new_readonly_unit':True})
permit={
 'id':'TASK-122-Q-READINESS-AND-OPERATION-PREPARATION-20261021','issued_at':STAMP,
 'task':'TASK-122','R':'R-116','STEP':'STEP018','state':'SAVED_READABLE_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED_OR_STARTED',
 'receiver':'A+ new preparation/research window; no implementation or audit role',
 'contract_sha256':sha(contract),'input_manifest_sha256':sha((N/'input-manifest.json').read_bytes()),
 'mode':'task_model','rules':'V4.0 CHG-0003','stage':'07 preactivation preparation',
 'allowed_writes':['DocuN/evidence/TASK-122/preparation/','DocuN/results/TASK-122-result.md','README.md only verified Q preparation/operator/closed limitations'],
 'official_search_themes_cap':12,'official_original_documents_cap':24,
 'tool_wall_seconds':2400,'metadata_batch_seconds':60,'calendar_seconds':86400,
 'receipt_rule':'First bounded read/clock bootstrap allowed and charged; unknown receipt uses issued_at as conservative bound; no interruption reset',
 'runtime_caps':{k:0 for k in ('product_import','compile','unittest','build','PG','Docker','API','browser','Windows_Job','model_or_embedding_api','paid_api','Git')},
 'allowed_local_work':'stdlib filesystem/hash/JSON/arithmetic, declared env-variable existence only; no value/hash output',
 'read_secret_values_vault_runtime_or_user_database':False,'read_private_account_console_or_use_API_key':False,
 'old_runtime_permits_not_reactivated_or_extended':True,'valid_grant_approval_activation_or_enabled_config_writes':False,
 'real_Q':'FROZEN','real_fee':0,'same_problem_two_evidence_based_searches_still_missing_stop_expansion':True,
 'independent_audit_required_for_this_document_only_unit':False,
 'reason':'Existing high-risk engineering/audit closed; this unit changes no executable behavior, needs document and provenance consistency only',
 'all_old_accounts_budgets_failures_retained':True}
js(N/'permit.json',permit)

state=f'''# 执行动态文档

文档v2.88，2026-10-21，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.60、task_model/07。以下v2.87原字节保留。

## TASK120有限工程交付通过并关闭；TASK121独审交付通过，下一TASK122启用前置准备

{STAMP}。主控回收原121 review02，78165字节/hashffbd03ce…c1c12f、750收尾引用/7规则重算零漂移，五项原缺陷全部关闭。采纳有限代码通过/定向证据充分，TASK120有限工程功能及有效证据交付通过并关闭，停止原修复循环；TASK120总验收部分通过，历史控制轴不通过与所有旧违规/unknown保留。TASK121/R115集中及两增量审计交付通过并结束，不把审计回传当主控签字。

最小清理夹具只证明清理投影/恢复，非来源资格或合法外发；原已接受S/ACK/C12/K2/UI和normal协议证据按原范围继承。原28PID/8Job/两CID/三端口及1005/1006只证明原停止时点，旧unknown替代证据保持，主控无实时探针或业务运行。工程root/PG64/64、149失败/117旧81、wall69357.418110/72000、holding2943.704295/21600及审计保守2113.8359792/3600留档，账active空，旧资源/根/票据都不恢复许可。

TASK122/R116已登记，父STEP018，A+新前置核查窗口，领域转为当前官方/计量/账号非敏感readiness/操作包，不使用旧工程或审计运行许可。DISPATCH_STATUS

新卡是已有100次/25元、48/28/24及12/7/6元条件采用下的准备，不重新索取同预算/候选，不执行Q。完成A—D当前官方证据、计价/token/framing/reasoning上界与适用性、配置/环境presence分层、全部剩余语义Must矩阵、一次操作包和最少集中缺口。运行/真实provider/费用/Git均0，只可写准备证据/结果和README已验Q操作限制；24h日历/工具2400秒、官方12主题24文档，文档一致性检查一次，不新增末尾独审门。

Q仍冻结，T0/72h及实际normal首次启用未建立。需真实官方/账户/计量/严格返回身份、normal loader readiness、实际新normal绑定及可容纳Must/精确资源/主控首次启用回执后才进入付费语义验证；TASK122只准备，不造可用grant。STEP018仍进行中/部分验证，STEP019/020/M1/项目/发布未通过。CHG1591—1597，下一1598。

## 以下为v2.87及更早历史
'''
registered=prefix(state.replace('DISPATCH_STATUS','完整卡正在保存，未声明转交/接收/开始。'),old[shared[2]])
put(ROOT/shared[2],registered);put(OUT/'registration-state.bytes',registered)
put(ROOT/'DocuN/tasks/TASK-122.md',contract)
assert (ROOT/'DocuN/tasks/TASK-122.md').read_bytes()==contract
put(ROOT/shared[2],prefix(state.replace('DISPATCH_STATUS','完整TASK122/R116卡已真实保存读回，待用户人工转交，未声明已接收/开始。路径DocuN/tasks/TASK-122.md，输入/事实交接/permit在DocuN/evidence/TASK-122/orchestration-20261021。'),old[shared[2]]))
put(ROOT/shared[0],prefix(f'''# TASK-120 / R-114 有限工程交付关闭裁定（当前有效）

{STAMP}。主控核原TASK121 review02完整报告及750收尾引用、原后缀、五项关闭与方法限定，零身份漂移；当前代码通过、定向证据充分。按原批准的有限工程范围，功能及有效证据交付验收通过并关闭；TASK120总验收保留部分通过，历史全过程执行控制不通过不追认。原S和未变已验事实继承，五项F01—F05无开放阻断项，不再在本有限切片重复修复/测试/全面审计。

独审TASK121/R115交付通过并结束。F03不可授权依赖副本夹具仅证明准确清理投影和恢复，不证正常请求来源/合法外发；normal协议/模型/来源原有证据各守边界，当前真实Q不能由有限工程验收自动放行。原R01仅包读取、旧memory快照限制、个别fixture字节时间/原unknown停止替代证明全部保留。

工程root64/64、PG64/64、API65/96、Browser15/16、build5/8、Native69/128、HTTP1572/10000，149失败/原117的81，wall69357.418110/72000、holding2943.704295/21600、audit保守2113.8359792秒原样结转/封存。原1005/1006停止及后续只读事实按其时点接受，主控未实时查服务，没有产品/测试/Git/付费运行或改工程账。全部旧对象只读留档，余量和旧卡不可恢复执行。

下一独立可执行准备成果为新TASK122/R116，A+新核查窗口，当前外部事实/计量/readiness和一次操作包，运行费用0，完整卡保存待转交。已批准deepseek-flash候选与100/25条件许可不再索权，但当前供应商/账号/计量/价格税/返回身份、完整语义矩阵和首次启用回执未核齐前Q继续冻结，T0不设。STEP018整体/019/020/M1/项目未通过。

详细主控关闭与冻结对象在DocuN/evidence/TASK-120/orchestration-closure-20261021/closure-receipt.json。以下历史裁定原字节保留。
''',old[shared[0]]))
put(ROOT/shared[1],prefix(f'''# 架构动态文档

文档v1.60，2026-10-21，Asia/Shanghai。需求v1.4、执行动态v2.88、task_model/07。以下v1.59原字节保留。

## Q v2有限工程验收关闭，正式Q启用仍待前置事实与运行合同

{STAMP}。TASK121两轮增量确认F01—F05关闭，主控接受当前有限代码/定向证据并关闭TASK120该工程交付；历史控制不通过保持。精确逐请求批准/原键恢复、共同PG账门、015严格新旧迁移链、实际角色潜在ADMIN能力、源/记忆Q副本清理与组合只读投影、联合时钟/领取门、正式UI隔离在各自原证据范围实现并已验证，不作无限域保证。

F03最小样本仅证清理投影/恢复，normal来源与合法外发不由该样本代证；原已审正常协议和未变S/业务证据继承。纯读POLICY标记不是写资格，未来新增方法仍须守无写/无逃逸任务和旧guard。旧profile/备份层级、unknown替代停止及历史控制限制照留。

正式Q未启、T0/72h未起，用户已采用的候选与未来唯一100/25/48-28-24边界保持。新TASK122只核当前官方/账号/计量/readiness及剩余语义/一次操作包，不变架构或启用参数，不新造权限平台/账本。实际部署/付费语义/最终安全与本人交付仍是后续阶段门。

## 以下为v1.59及更早历史
''',old[shared[1]]))
put(ROOT/shared[3],prefix(f'''# TASK-120 当前终点——有限工程交付已验收关闭，旧许可停止

{STAMP}。主控已回收TASK121 review02并采纳F01—F05关闭。有限工程功能及有效定向证据交付通过并关闭；总TASK验收保留部分通过，历史执行控制不通过照留。工程原A/旧A+停止，产品/证据/统一账封存，root/PG64/64不可再启动，旧时窗或Browser余量不恢复运行。

下一前置核查为独立TASK122/R116，不是120续作，不从此卡获得Q启用权。Q继续冻结。以下旧停止通知/合同只作真实授权/尝试历史，原字节保留。
''',old[shared[3]]))
put(ROOT/shared[4],prefix(f'''# TASK-121 当前终点——集中独审及review-01/review-02交付已验收结束

{STAMP}。主控已核review02及冻结身份，采纳五项关闭，有限工程代码/证据可关闭。历史执行控制轴不通过、最小夹具与原证据限制保留。当前审计任务调度已返回，审计交付验收通过并结束，不代签Q/STEP018整体或项目。

旧review-02窗口及工具余量不自动形成新审计/运行许可。未来真实新增变化若需审计，由主控另给明确范围；本卡下方原合同只作历史。当前没有要求该窗口继续操作。
''',old[shared[4]]))
changes=[(shared[0],'采纳121五项关闭，有限工程交付通过并关闭，总任务部分通过/历史控制失败保留。'),
 (shared[1],'v1.60登记已验Q有限实现与正式启用前置分界，不把合成夹具扩大为正常外发证明。'),
 (shared[2],'v2.88登记120有限关闭/121结束、新122R116前置准备保存待转交与Q冻结。'),
 (shared[3],'置顶工程有限交付关闭及旧运行许可停止终点，历史原字节保留。'),
 (shared[4],'置顶独审交付结束通知，旧审计余量不自动续审，历史原字节保留。'),
 ('DocuN/tasks/TASK-122.md','保存A+新核查窗口的官方/计量/readiness/剩余Must/一次操作包完整任务，运行费0。'),
 ('DocuN/evidence/TASK-120/orchestration-closure-20261021及TASK-122/orchestration-20261021','保存750身份核证/有限关闭回执、旧共享/返回账、新输入/事实/permit与读回；主控无工程运行。')]
ch='\n\n'+'\n\n'.join(f'- CHG-{1591+i:04d}，{STAMP}，Codex编排Agent，{n}。{why}' for i,(n,why) in enumerate(changes))+'\n'
put(ROOT/shared[5],old[shared[5]]+ch.encode('utf-8'))
allowed={ROOT/n for n in shared}
for p,h in protected.items():
    if p not in allowed:assert sha(p.read_bytes())==h,str(p)
assert budget_path.read_bytes()==budgetraw and sha(events_path.read_bytes())==eventsha
for n in shared[:5]:assert (ROOT/n).read_bytes().endswith(old[n])
assert (ROOT/shared[5]).read_bytes().startswith(old[shared[5]])
assert (ROOT/'DocuN/tasks/TASK-122.md').read_bytes()==contract
js(N/'dispatch-readback.json',{'state':'SAVED_READABLE_NOT_DISPATCHED','issued_at':STAMP,
 'task':'TASK-122','R':'R-116','card':str(ROOT/'DocuN/tasks/TASK-122.md'),
 'contract_sha256':sha(contract),'permit_sha256':sha((N/'permit.json').read_bytes()),'runtime':0})
js(OUT/'save-proof.json',{'state':'FINITE_DELIVERY_CLOSED_NEXT122_SAVED_READABLE_AWAITING_HANDOFF','recorded_at':STAMP,
 'identity_rows_match':750,'closed_findings':['F01','F02','F03','F04','F05'],
 'task120_finite_delivery':'通过并关闭','task120_overall':'部分通过，历史控制不通过',
 'next_task':'TASK-122','next_R':'R-116','contract_bytes':len(contract),'new_runtime':0,
 'versions':['2.88','1.60'],'next_CHG':1598,'engineering_ledger_writes':0})
print(json.dumps({'state':'FINITE_DELIVERY_CLOSED_NEXT122_READY_FOR_MANUAL_HANDOFF','identities':750,
 'task122_contract_bytes':len(contract),'next_CHG':1598,'runtime':0},ensure_ascii=False))
