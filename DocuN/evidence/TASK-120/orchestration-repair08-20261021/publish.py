"""主控核证与同号剩余修复签发，仅使用文件元数据。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,os,re

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
E=ROOT/'DocuN/evidence/TASK-120/execution'
A=ROOT/'DocuN/evidence/TASK-121/audit/review-01'
NOW=datetime.now(timezone(timedelta(hours=8)))
STAMP=NOW.isoformat(timespec='microseconds')
ID='TASK-120-Q-PREP-TARGETED-REPAIR-08-20261021'
def sha(x):return hashlib.sha256(x).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(p,x):
    p=p.resolve();assert p.is_relative_to(ROOT)
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.repair08.tmp')
    with tmp.open('xb') as s:s.write(x);s.flush();os.fsync(s.fileno())
    os.replace(tmp,p);assert p.read_bytes()==x
def js(p,x):put(p,(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def prefix(text,old):return (text.strip()+'\n\n').replace('\n','\r\n').encode('utf-8')+old

assert not (OUT/'save-proof.json').exists()
closing=load(A/'identity-closing.json');assert len(closing['rows'])==606
protected={}
for row in closing['rows']:
    p=Path(row['path']);actual=sha(p.read_bytes()) if p.is_file() else None
    assert actual==row['actual_sha256'],row['path']
    if actual:protected[p]=actual
rules=load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:assert sha(Path(row['absolute_path']).read_bytes())==row['sha256']
report=ROOT/'DocuN/results/TASK-121-result.md'
assert len(report.read_bytes())==55795 and sha(report.read_bytes())=='75d40d166010d29b28065327a8a911a859200d6da01cac080ab13b72748da595'
findings=load(A/'findings.json')
assert {r['id'] for r in findings['decisions'] if r['state']=='关闭'}=={'F01','F04','F05'}
receipt=load(A/'session-receipt.json')
budget_path=E/'budget.json';events_path=E/'events.jsonl'
budgetraw=budget_path.read_bytes();eventsha=sha(events_path.read_bytes());budget=load(budget_path)
assert budget['active_root'] is None and budget['active_command'] is None
assert budget['counts']['roots']==60 and budget['counts']['pg_starts']==61
assert len(budget['failures'])==141
assert abs(budget['command_wall_conservative_upper_seconds']-64525.559426)<.001
assert budget['command_wall_cap_seconds']==72000
business='2026-10-21T20:29:21.021710+08:00';finish='2026-10-21T20:59:21.021710+08:00'
assert NOW<datetime.fromisoformat(business),'本轮原业务窗已到，不能签新业务卡'
oldpermit=load(ROOT/'DocuN/evidence/TASK-120/orchestration-adopted07-20261021/permit.json')
contract=(OUT/'contract.md').read_bytes();ct=contract.decode('utf-8-sig')
for word in ('F02','F03','ADMIN','purge','20:29:21.021710','20:59:21.021710','7474.440574','unknown','已批准'):
    assert word in ct,word
assert '*' not in ct and '〈' not in ct
shared=['DocuN/results/TASK-120-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuN/tasks/TASK-120.md','DocuS/文档变更记录.MD']
before={n:(ROOT/n).read_bytes() for n in shared}
assert '文档v2.85' in before[shared[2]].decode('utf-8-sig')[:200]
assert '文档v1.57' in before[shared[1]].decode('utf-8-sig')[:200]
assert max(map(int,re.findall(r'CHG-(\d{4})',before[shared[4]].decode('utf-8-sig'))))==1579
for n,x in before.items():put(OUT/'before'/n,x)
put(OUT/'returned-ledger/budget.json',budgetraw)

js(OUT/'input-check.json',{
 'checked_at':STAMP,'audit_report':{'path':str(report),'bytes':55795,'sha256':sha(report.read_bytes())},
 'closing_identity_rows':606,'drift':[],'rules_match':len(rules),
 'review01_delivery':'accepted_complete','engineering_acceptance':'failed_pending_F02_F03',
 'adopted_closures':['TASK121-F01','TASK121-F04','TASK121-F05'],
 'remaining_P1':['TASK121-F02 ADMIN indirect capability closure','TASK121-F03 memory Q cleanup pending GET/reopen'],
 'scope_binding':'Original AP12007 object/permission/deletion scope; no new high-impact authorization requested or added',
 'O01_stop_qualification':'20 unknown/error5 process observations are not fresh exits; accept review01 exact alternative proofs for19 earlier exits and1 namedJob membership/tree_empty/absence. Preserve original records.',
 'audit_conservative_tool_total_retained':receipt['cumulative_conservative_charge_seconds'],
 'budget_counts':budget['counts'],'budget_caps':budget['caps'],'budget_sha256':sha(budgetraw),'events_sha256':eventsha,
 'wall_seconds_retained':budget['command_wall_conservative_upper_seconds'],'holding_seconds_retained':budget['runtime_holding_union_seconds'],
 'main_runtime':0,'product_writes':0,'engineering_ledger_writes':0,'live_resource_probe':False})
permit={
 'id':ID,'issued_at':STAMP,'task':'TASK-120','R':'R-114','STEP':'STEP018',
 'state':'SAVED_READABLE_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED_OR_STARTED',
 'parent_permit':oldpermit['id'],'user_adoption_inherited':'AP-120-07; original explicit 批准 binding retained',
 'scope':'Remaining TASK121 review01 F02/F03 only; no resource/privilege/delete/budget expansion',
 'receiver':'Same original A exclusive strongest-capable engineering window that returned07; old A+ stopped',
 'contract_path':str(OUT/'contract.md'),'contract_sha256':sha(contract),
 'old_counts_at_return':budget['counts'],'new_cumulative_caps':budget['caps'],'caps_increased':{},
 'command_wall_cap_seconds':72000,'old_conservative_wall_seconds':budget['command_wall_conservative_upper_seconds'],
 'remaining_wall_seconds_at_issue':72000-budget['command_wall_conservative_upper_seconds'],
 'runtime_holding_union_cap_seconds':21600,'old_holding_seconds':budget['runtime_holding_union_seconds'],
 'old_failure_records':141,'old_TASK117_failure_records':81,'older_unknown_reserves_retained':True,
 'business_deadline':business,'finish_deadline':finish,'old07_12hour_window_not_reset':True,
 'original_96h_deadline_utc':'2026-10-22T08:41:08.5687758Z',
 'first_read_clock_adoption_bootstrap_allowed_and_charged':True,
 'next_root_id':61,'command_ids':'Continue actual unique unused next id;999 is a prior final-save label, do not overwrite',
 'metadata_seconds':60,'offline_build_batch_seconds':300,'root_seconds':1800,'root_cleanup_reserve':120,
 'source_container':oldpermit['source_container'],
 'restore_target_must_remain_stopped':oldpermit['restore_target_must_remain_stopped'],
 'database_write_only':'retrolume_task120_audit07_main','new_logical_databases':0,'new_containers':0,'new_volumes':0,
 'other_existing_databases_readonly_history_only':True,
 'role_counterexamples':oldpermit['role_counterexamples'],
 'synthetic_cleanup':{**oldpermit['synthetic_cleanup'],
  'cumulative07_and08_maximum_new_body_files':16,'prior_registered_deleted_files_retained':6,
  'new_objects_manifest_required':True},
 'synthetic_admission_cumulative_cap':16,'synthetic_admission_used07':5,'no_old_grant_reactivation':True,
 'new_model_chain_replay_not_requested':True,'one_minimal_browser_flow_allowed_from_original_remaining2':True,
 'frontend_build_only_if_directly_changed':True,'memory_minimum_MiB':oldpermit['memory_minimum_MiB'],
 'memory_poll_seconds':1,'real_Q':'FROZEN','real_provider':0,'real_paid_fee':0,'preview':0,'Git':0,
 'independent_audit_after_stability':'Same original TASK121 audit window; remaining two boundaries and actual effects only',
 'main_did_not_execute_or_edit_engineering':True}
js(OUT/'permit.json',permit)

state=f'''# 执行动态文档

文档v2.86，2026-10-21，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.58、task_model/07。以下v2.85原字节保留。

## TASK121 review-01已返回；三项关闭，两P1合并交原120续作08

{STAMP}。主控回收原121 review-01，报告55795字节/hash75d40d16…da595及606条收尾身份核对无漂移。审计交付通过，采纳F01/F04/F05关闭；F02 ADMIN→中间角色→SET组合、F03记忆Q清理失败的GET/重开误报完成两P1保留，当前工程验收失败。源清理_CleanupAttempt及其限定恢复已获独审接受，旧正常链/C12/ACK/UI继续按适用性继承，不全面重审。

DISPATCH_STATUS

同TASK120/R114原A增强工程窗独占修两项及最小PG/记忆失败重开/浏览器对照；原A+停止，原121已返回不在途。沿用户批准AP12007精确库/角色事务/正文范围，不新增DB/容器/卷/权限类型/费用；许可{ID}、完整合同/身份核对/旧共享与返回账在DocuN/evidence/TASK-120/orchestration-repair08-20261021。无新TASK/R，完成后原121只核两项增量。

原root60/64、PG61/64、API63/96、Browser14/16、build5/8、Native69/128、HTTP1520/10000、容器卷2/2、141失败/原117的81、wall64525.559426/72000、holding2885.485295/21600全结转。只使用已建audit07_main，原6个实例不写不解冻；准入累计5/16、准确文件已用6/16不清零。原07保守业务门2026-10-21 20:29:21.021710+08、收尾20:59:21.021710+08和原96h均不延长，首次有限读卡采时登记照实，非新12h。

O01停止解释纠正同步采纳。原079的20条unknown/error5不得叫新鲜退出；19项旧准确退出加1项具名Job归属/树零/同名Job缺席组合支持当时精确清场。原件不改、主控没有实时服务探针；后续助手须保持unknown而非默认false即退出。历史控制不通过和未知投入保留，当前active_root/command空。Q、真实provider/费用/preview/Git冻结或0，STEP018整体/019/020/M1/项目未通过。CHG1580—1584，下一1585。

## 以下为v2.85及更早历史
'''
registered=prefix(state.replace('DISPATCH_STATUS','续作08已登记，完整卡正在保存；没有新转交/接收/启动事实。'),before[shared[2]])
put(ROOT/shared[2],registered);put(OUT/'registration-state.bytes',registered)
put(ROOT/shared[3],contract+b'\r\n\r\n---\r\n\r\n'+before[shared[3]])
assert (ROOT/shared[3]).read_bytes().startswith(contract)
put(ROOT/shared[2],prefix(state.replace('DISPATCH_STATUS','同号续作08完整可执行卡已保存读回，待人工转交原A窗口，尚无接收/启动事实。卡面明确沿原剩余时窗，20:29前停止新增业务，20:59前清场保存。'),before[shared[2]]))
put(ROOT/shared[0],prefix(f'''# TASK-120 / R-114 review-01回收与两P1同号续作08（当前有效）

{STAMP}。原TASK121增量审查已返回，主控核报告与606收尾身份零漂移、必要源码和GET/视图调用。采纳F01/F04/F05关闭，F02/F03仍各一P1，代码不通过、证据不足、历史控制不通过分别保持；当前工程不能关闭。审计任务交付通过，不能与被审工程状态混同。

两剩余问题合并回原A工程窗同TASK120/R114续作08。ADMIN组合能力闭包只补一准确PG事务反例及合法图对照；记忆清理只补文件删除失败→同键GET/列表详情/重开不误报→显式retry成功，核原007/费用/无关对象，不重刷旧样本。原源清理新attempt的限定关闭及旧充分证据继承。

仍在AP12007已批准的合成库/事务权限/新造准确文件范围，复用原源CID和audit07_main，无新增高影响动作，故直接签发{ID}，不再请求同项批准。原root60/PG61/Browser14等剩余及wall7474.440574秒可用；不重开12h，业务门20:29:21/收尾20:59:21当日+08保持。完整卡已保存待转交原工程，未虚记收到或开始；独审原121待稳定增量，不并行写源。

独审O01将原079中20个unknown观测与替代退出/Job证据分开，已同步更正停止解释，原停止报告不改；不能再以same_identity_running=false断言未知进程新鲜退出。主控只核原时点，未查当前Docker或进程。

所有原失败/预算/unknown/控制不通过不改，源码/工程报告/审计及唯一账本无主控写入。Q继续冻结，STEP018整体/M1/项目不关闭。以下原裁定完整保留。
''',before[shared[0]]))
put(ROOT/shared[1],prefix(f'''# 架构动态文档

文档v1.58，2026-10-21，Asia/Shanghai。需求v1.4、执行动态v2.86、task_model/07。以下v1.57原字节保留。

## Q三项修复获独立确认，两项组合边界尚待修正

{STAMP}。TASK121 review-01确认F01精确迁移前提与旧新链、F04联合时钟及不可逆失效、F05PG领取投影修复关闭；原记忆正常清理、源删除失败/重开私有cleanup attempt的限定路径亦有适用证据，不重推其协议。

F02仍漏ADMIN对空中间角色的可授予关系与其后SET/INHERIT组合能力；当前直接ACL/当前SET闭包不能证明潜在权限隔离。F03当前POST临时pending未进入GET及重开视图的组合投影，DB purge done与Q文件未确认必须保持两种事实，不将未确认显示完成或隐藏明确重试。两P1交原工程定向修复，尚未实施，不新增平台/DDL/公开请求类型。

原止损助手将unknown误并入退出的汇总缺陷为非阻断O01，精确旧退出/Job替代证据已由独审分级采纳。原字节不改，后续停止观察保留unknown。Q及STEP018整体仍未放行。

## 以下为v1.57及更早历史
''',before[shared[1]]))
entries=[(shared[0],'回收121 review01，采纳三关闭/两P1及停止证据限定，签同号定向08。'),
 (shared[1],'v1.58登记三已确认修复与ADMIN组合/记忆GET投影剩余边界，不扩大原方案。'),
 (shared[2],'v2.86登记原工程两项定向续作已保存待转交、剩余预算及原时间门保持。'),
 (shared[3],'置顶完整08合同，复用AP12007已批准范围，旧冻结与07合同历史保留。'),
 ('DocuN/evidence/TASK-120/orchestration-repair08-20261021','保存606身份核对、两项合同/精确许可、返回账与旧共享快照、保存读回；无工程执行。')]
ch='\n\n'+'\n\n'.join(f'- CHG-{1580+i:04d}，{STAMP}，Codex编排Agent，{n}。{why}' for i,(n,why) in enumerate(entries))+'\n'
put(ROOT/shared[4],before[shared[4]]+ch.encode('utf-8'))
for p,h in protected.items():assert sha(p.read_bytes())==h,str(p)
assert budget_path.read_bytes()==budgetraw and sha(events_path.read_bytes())==eventsha
for n in shared[:4]:assert (ROOT/n).read_bytes().endswith(before[n])
assert (ROOT/shared[4]).read_bytes().startswith(before[shared[4]])
js(OUT/'save-proof.json',{'state':'REPAIR08_SAVED_READABLE_AWAITING_MANUAL_HANDOFF','issued_at':STAMP,
 'task':'TASK-120','R':'R-114','contract_bytes':len(contract),'contract_sha256':sha(contract),
 'current_card_sha256':sha((ROOT/shared[3]).read_bytes()),'input_rows_match':606,'rules_match':len(rules),
 'runtime':0,'engineering_ledger_writes':0,'versions':['2.86','1.58'],'next_CHG':1585,
 'business_deadline':business,'finish_deadline':finish,'new_authorization_needed':False})
print(json.dumps({'state':'REPAIR08_SAVED_READABLE_AWAITING_HANDOFF','contract_bytes':len(contract),
 'identity_rows_match':606,'next_CHG':1585,'runtime':0},ensure_ascii=False))
