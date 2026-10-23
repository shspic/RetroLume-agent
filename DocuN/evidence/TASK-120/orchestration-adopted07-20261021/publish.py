"""登记用户批准并签发人工转交合同，仅文件核对与文档写入。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT/'DocuN/evidence/TASK-120/orchestration-audit07-20261021'
NOW = datetime.now(timezone(timedelta(hours=8)))
STAMP = NOW.isoformat(timespec='microseconds')
ID = 'TASK-120-Q-PREP-AUDIT-REPAIR-07-20261021'
ABSOUT = 'D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-adopted07-20261021'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def readj(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def put(path, data):
    path=path.resolve()
    assert path.is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_name(path.name+'.issue07.tmp')
    with tmp.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp,path)
    assert path.read_bytes()==data

def putj(path,value):
    put(path,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

def prepend(text,old):
    return (text.strip()+'\n\n').replace('\n','\r\n').encode('utf-8')+old

assert not (OUT/'save-proof.json').exists()
proof=readj(SOURCE/'save-proof.json')
assert proof['state']=='PROPOSAL_AND_COMPLETE_DRAFT_SAVED_READABLE_NOT_AUTHORIZED'
for row in proof['files']:
    assert sha(Path(row['path']).read_bytes())==row['sha256'],row['path']
closing=readj(ROOT/'DocuN/evidence/TASK-121/audit/identity-check-closing.json')
for row in closing['rows']:
    p=Path(row['path'])
    assert (sha(p.read_bytes()) if p.is_file() else None)==row['actual'],row['path']
rules=readj(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert sha(Path(row['absolute_path']).read_bytes())==row['sha256']
budget_path=ROOT/'DocuN/evidence/TASK-120/execution/budget.json'
events_path=ROOT/'DocuN/evidence/TASK-120/execution/events.jsonl'
budget_raw=budget_path.read_bytes()
events_hash=sha(events_path.read_bytes())
budget=readj(budget_path)
assert budget['active_root'] is None and budget['active_command'] is None
assert budget['engineering_status']=='CONTINUATION06_COMPLETE_STOPPED_READY_FOR_INDEPENDENT_AUDIT'
assert budget['counts']['roots']==51 and len(budget['failures'])==125
assert budget['command_wall_cap_seconds']==57600
assert abs(budget['command_wall_conservative_upper_seconds']-50243.003003)<0.001
deadline=datetime.fromisoformat('2026-10-22T08:41:08.568775+00:00')
assert NOW < deadline-timedelta(seconds=1800)
proposal=SOURCE/'adoption-proposal.md'
draft=SOURCE/'repair-contract-proposed.md'
assert sha(proposal.read_bytes())=='dc0e79bc8ae197233da1337b232c77b0420707c902303b530941c1cd07051bc0'
assert sha(draft.read_bytes())=='4674a04b6ba0f33003586ed60240f5a564decb1124978198e6638beb20b53a7f'

shared=['DocuN/results/TASK-120-work-decision.md','DocuS/架构动态文档.MD',
        'DocuS/执行动态文档.MD','DocuN/tasks/TASK-120.md','DocuS/文档变更记录.MD']
old={name:(ROOT/name).read_bytes() for name in shared}
assert '文档v2.83' in old[shared[2]].decode('utf-8-sig')[:200]
assert '文档v1.55' in old[shared[1]].decode('utf-8-sig')[:200]
assert max(map(int,re.findall(r'CHG-(\d{4})',old[shared[4]].decode('utf-8-sig'))))==1568
for name,data in old.items():
    put(OUT/'before'/name,data)
put(OUT/'returned-ledger/budget.json',budget_raw)

text=draft.read_text(encoding='utf-8')
replacements={
 '# TASK-120 / R-114 续作07 五项审计缺陷合并修复合同草案':
 '# TASK-120 / R-114 续作07 五项审计缺陷合并修复与定向验证（当前有效）',
 '状态为待采用，不是运行许可。AP-120-07 获得用户明确采用并由主控签发许可后，才将本完整正文置顶到原 TASK-120 卡。当前工程冻结照旧。不得凭草案、剩余次数或原06许可开始修改或运行。':
 f'用户已对AP-120-07明确回复“批准”。主控于{STAMP}登记采用并签发{ID}。本卡及下列精确permit是当前有效的前向续作合同，覆盖下方历史停止通知中与本轮范围冲突的部分。只解除本卡工程修复与定向验证的冻结，真实Q仍冻结。已保存待人工转交，未冒称执行者已接收或启动。',
 '需求 v1.4，架构 v1.55，执行动态 v2.83。':'需求 v1.4，架构 v1.56，执行动态 v2.84。',
 '4. DocuN/evidence/TASK-120/orchestration-audit07-20261021/bounded-review.json、adoption-proposal.md、后续真正签发的许可。草案没有后续许可，不能假定已存在。':
 f'4. DocuN/evidence/TASK-120/orchestration-audit07-20261021/bounded-review.json、adoption-proposal.md，以及 {ABSOUT}/adoption-receipt.json、permit.json、input-check.json、contract.md。原提案中的待批准措辞是历史，采用回执绑定其原hash；不是再次请求授权。',
 '## 待批准的真实资源和预算':'## 已批准的真实资源和预算',
 '以下为AP-120-07具体边界，尚未生效。批准后主控前向许可只准复用源容器':
 '以下为用户已批准AP-120-07的具体边界。本次前向许可只准复用源容器',
 '前向拟将工具wall累计上限57600提升72000秒':'本次许可将工具wall累计上限57600前向提升72000秒',
 '当前仅缺用户对AP-120-07的合并采用。批准后继续原工程窗，代码与验证不逐项再问；未批准前此草案不能启动任何部分。必要原因是原AP-120-06只批准一处表DELETE与两个既定资源，未覆盖本轮新增逻辑库、负例成员权限和精确正文删除。原有代码修复目标无需再次决定，真正缺的是这些高影响验证边界。':
 '用户已明确批准AP-120-07，卡内两个新合成逻辑库、未提交权限负例、准确新造正文删除和前向wall增量均已覆盖。必要人工只有将本完整卡转给原A工程窗口，之后带回统一结果路径；不再次逐项询问。首次接收bootstrap在原唯一工程账追加本许可、实际采时和保守接收边界后连续执行；主控没有代改工程账。旧证据、计数、旧失败和历史控制不通过保持，未在本卡内的权限、数据或运行依旧不得扩大。'
}
for before,after in replacements.items():
    assert text.count(before)==1,before
    text=text.replace(before,after)
for bad in ('尚未生效','当前仅缺','前向拟将','合同草案','需求 v1.4，架构 v1.55'):
    assert bad not in text,bad
assert '*' not in text and '〈' not in text
contract=text.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')
put(OUT/'contract.md',contract)
adoption={
 'adoption_id':'AP-120-07','user_reply_verbatim':'批准','recorded_by_orchestrator_at':STAMP,
 'exact_user_click_or_send_time':'unknown; recorded_at is observation/registration time',
 'approved_proposal_path':str(proposal),'approved_proposal_sha256':sha(proposal.read_bytes()),
 'approved_complete_draft_path':str(draft),'approved_draft_sha256':sha(draft.read_bytes()),
 'adopted_scope':'TASK121 F01-F05 repairs, two exact synthetic DBs, transactional privilege counterexamples, exact new synthetic body cleanup, forward wall budget increase',
 'real_Q_or_paid_provider_or_user_database_or_publication':False,
 'historical_proposal_and_draft_unchanged':True,
 'permit_id':ID,'actual_executor_receipt':'NOT_YET_REPORTED'}
putj(OUT/'adoption-receipt.json',adoption)
permit={
 'id':ID,'issued_at':STAMP,'task':'TASK-120','R':'R-114','STEP':'STEP018',
 'adoption_id':'AP-120-07','parent_permit':'TASK-120-Q-PREP-CONTINUATION-06-20261020',
 'state':'SAVED_READABLE_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED_OR_STARTED',
 'receiver':'Continue original A exclusive strongest-capable engineering window that returned continuation06; old A+ stopped',
 'contract_sha256':sha(contract),'contract_path':ABSOUT+'/contract.md',
 'adoption_receipt_path':ABSOUT+'/adoption-receipt.json',
 'approved_proposal_sha256':adoption['approved_proposal_sha256'],
 'old_counts_at_return':budget['counts'],'new_cumulative_caps':budget['caps'],
 'counter_caps_increased':{},
 'command_wall_cap_seconds':72000,'previous_command_wall_cap_seconds':57600,
 'old_conservative_wall_seconds_retained':budget['command_wall_conservative_upper_seconds'],
 'remaining_wall_seconds_at_issue':72000-budget['command_wall_conservative_upper_seconds'],
 'runtime_holding_union_cap_seconds':21600,'old_holding_seconds_retained':budget['runtime_holding_union_seconds'],
 'old_failures_retained':125,'TASK117_failures_retained':81,'all_older_unknown_reserves_retained':True,
 'calendar_deadline_utc_unchanged':'2026-10-22T08:41:08.5687758Z',
 'original_first_tool_utc_unchanged':budget['actual_first_tool_utc'],
 'maximum_finish_window_seconds_from_receipt':43200,'save_only_last_seconds':1800,
 'receipt_rule':'First <=60s non-business bootstrap may read card/ledger, sample UTC/QPC and record receipt; charge this tool. If exact receipt unknown use issued_at as conservative bound; do not claim pre-tool registration.',
 'finish_deadline_rule':'min(reliable_actual_receipt_or_conservative_issue_time + 43200s, original calendar deadline)',
 'business_deadline_rule':'finish deadline minus 1800s',
 'root_ids_begin_after':51,'command_ids_begin_after':71,
 'real_root_cap_seconds':1800,'root_cleanup_reserve_seconds':120,'metadata_batch_cap_seconds':60,'offline_build_batch_cap_seconds':300,
 'source_container':{
  'id':'b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f',
  'name':'retrolume-task120-qprep-pg1','volume':'retrolume-task120-qprep-data',
  'image_id':'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
  'original_permit_label_unchanged':'TASK-120-Q-PREP-IMPLEMENTATION-20261018',
  'cpu':1,'memory_bytes':536870912,'pids_limit':128,'restart':'no','host_bind_mounts':False,
  'host':'127.0.0.1','pg_port':55480,'api_port':18120},
 'restore_target_must_remain_stopped':{
  'id':'4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332',
  'name':'retrolume-task120-scopeui-ro1','volume':'retrolume-task120-scopeui-ro1-data','port':55481},
 'new_containers':0,'new_volumes':0,'new_logical_databases':[
  {'name':'retrolume_task120_audit07_r02','create_attempt_cap':1,'objects_cap':1},
  {'name':'retrolume_task120_audit07_main','create_attempt_cap':1,'objects_cap':1}],
 'existing_databases_no_write':['retrolume_task120_flow','retrolume_task120_budget_01','retrolume_task120_budget_02','retrolume_task120_matrix_final','retrolume_task120_scope_ui_final','retrolume_task120_scopeui_ro'],
 'role_counterexamples':{
  'explicit_uncommitted_transaction_only':True,'mandatory_rollback_and_new_connection_confirmation':True,
  'no_concurrent_clients_during_cluster_role_negative':True,
  'temporary_NOLOGIN_bridges':['retrolume_task120_audit07_bridge1','retrolume_task120_audit07_bridge2'],
  'commit_role_membership_or_dangerous_privileges':False,
  'new_LOGIN_or_password_reset_or_role_admin_attribute_change':False,
  'scope':'Only F01 required privilege deficit and F02 direct/indirect INHERIT/SET capability counterexamples on declared new synthetic fixture; never persist dangerous grants'},
 'migration':{'path':'backend/migrations/015_activity_scope_delete_permission.sql',
  'old_sha256':'59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e',
  'execute_revised_only_on_named_new_databases':True,'old_001_to014_unchanged':True,
  'old_R03_exact_hash_read_compatibility_only':True,'new_business_tables_or_columns':False},
 'synthetic_cleanup':{
  'root':'D:/shspic/project_NO3_RetroLume-agent/.runtime/task120-audit07',
  'maximum_new_body_files':16,'manifest_before_deletion':True,
  'path_identity_hash_regular_file_checks':True,'normal_source_delete_or_memory_purge_entry_only':True,
  'old_roots_evidence_personal_data_or_recursive_delete':False,
  'preserve_non_authorizing_hash_events_original_007_facts_and_reservations':True},
 'new_synthetic_admission_cap_across_both_databases':16,'per_call_synthetic_microunits':250000,
 'original_per_instance_global_limit':{'requests':100,'cost_microunits':25000000},
 'activity_roster':[{'id':'01800000-0000-4000-8000-000000000001','requests':48,'cost_microunits':12000000},
  {'id':'01800000-0000-4000-8000-000000000002','requests':28,'cost_microunits':7000000},
  {'id':'01800000-0000-4000-8000-000000000003','requests':24,'cost_microunits':6000000}],
 'only_original_frozen_eight_text_inputs':True,'new_TESTONLY_roots_only':True,
 'old_grants_or_frozen_instances_not_extended_thawed_rebound':True,
 'memory_minimum_MiB':{'PG_API':512,'browser_single_headless_page':512,'stop_below_two_samples':256},
 'memory_poll_seconds':1,'browser_build_only_on_direct_frontend_change':True,
 'real_Q':'FROZEN','real_provider_calls':0,'actual_paid_fee':0,'preview':0,'Git_writes':0,
 'no_install_pull_prune_drop_delete_old_resources':True,'no_platform_approval_bypass':True,
 'same_issue_two_evidence_based_repairs_still_failing_stop':True,
 'final_incremental_independent_audit':'Original TASK121 isolated audit window; no full re-audit by default',
 'main_did_not_change_engineering_ledger_or_run_product':True,
 'executor_append_only_adoption_on_first_receipt_bootstrap':True}
putj(OUT/'permit.json',permit)
putj(OUT/'input-check.json',{
 'checked_at':STAMP,'rules_checked':len(rules),'audit_closing_rows_rechecked':len(closing['rows']),
 'mismatches':[],'budget_sha256':sha(budget_raw),'events_sha256':events_hash,
 'engineering_state':budget['engineering_status'],'active_root':None,'active_command':None,
 'old_reports_and_snapshot_protected':True,'live_resource_probe':False,
 'stop_evidence':'Only previous saved stop receipts; executor must freshly verify identity/status before runtime',
 'draft_to_contract_changes':'Approval/status/path/version substitutions only; F01-F05 scope and resource boundaries retained',
 'main_runtime':0})

state_head=f'''# 执行动态文档

文档v2.84，2026-10-21，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.56、task_model/07。以下v2.83原字节保留。

## AP12007已批准，TASK120同号续作07已登记

{STAMP}。用户明确回复“批准”，绑定AP-120-07原提案hash dc0e79bc8ae197233da1337b232c77b0420707c902303b530941c1cd07051bc0；完整五项修复草案同范围转为当前执行合同。TASK120/R114沿原A最强工程窗口，旧A+停止；新TASK/R不占。TASK121已完成集中独审交付，后续待稳定修后候选才回原独审窗口增量复核。

DISPATCH_STATE_PLACEHOLDER

许可{ID}与采用回执/完整合同/输入核对在DocuN/evidence/TASK-120/orchestration-adopted07-20261021。一次完成F01—F05修复、定向PG/文件/时钟/领取证据及准确收尾，已有C12/ACK/正常链/K2/UI充分证据复用。仅前向解除卡内工程冻结，真实Q仍冻结。原权限、正文清理、时间与领取缺陷在修正验收前仍开放；工程上轮失败不改写。

新增两个精确合成逻辑库、仅未提交事务的权限/角色反例、新私有根内最多16个准确登记的新造正文文件清理已获批准；无新容器/卷，旧六实例不写不解冻。源CID b8952207…原镜像/limits/55480/18120保持，目标4eb5be54…停止。015修订只在新库验证，旧包/015hash保留为精确历史读取兼容，001—014不改。真实provider/费用/preview/Git0。

原账root51/64、PG52/64、API55/96、Browser14/16、build5/8、Native64/128、HTTP1459/10000、容器卷2/2与失败125/旧117的81保持。工具wall前向cap57600→72000，50243.003003旧保守投入原样结转，持有2667.078295/21600；新两逻辑库各尝试/对象1单列，最多16笔本轮合成admission。接收至多12h且不晚原96h终点2026-10-22T08:41:08.5687758Z，末1800只清场保存；首次有界读卡采时登记bootstrap获准且计账，未知接收按签发保守下界，不伪造先登记。

322条审计收尾身份/7规则/原预算无漂移，active_root/command空；主控未改产品/工程结果/唯一工程账、未启动服务，仅复用原停止时点。由执行者接收后前向追加许可与账并核当前资源，不能将待转交写成在途。历史控制不通过和unknown保持，Q/STEP018整体/019/020/M1/项目未放行。CHG1569—1573，下一1574。

## 以下为v2.83及更早历史
'''
registered=prepend(state_head.replace('DISPATCH_STATE_PLACEHOLDER','续作07已登记，正式卡正在保存；尚无实际转交、接收或启动事实。'),old[shared[2]])
put(ROOT/shared[2],registered)
put(OUT/'registration-state.bytes',registered)
put(ROOT/shared[3],contract+b'\r\n\r\n---\r\n\r\n'+old[shared[3]])
assert (ROOT/shared[3]).read_bytes().startswith(contract)
final_state=prepend(state_head.replace('DISPATCH_STATE_PLACEHOLDER','续作07完整卡已真实保存读回，状态为待人工转交；尚无实际接收或启动事实。原A按DocuN/tasks/TASK-120.md置顶当前卡接续，无需再问卡内已批准事项。'),old[shared[2]])
put(ROOT/shared[2],final_state)
put(ROOT/shared[0],prepend(f'''# TASK-120 / R-114 AP-120-07批准与续作07签发（当前有效）

{STAMP}。用户对已准备的AP-120-07完整包明确回复“批准”。主控核原提案、草案、322条审计收尾身份、7锁定规则和原预算均未漂移，记录采用并签发{ID}，不重新索取同项授权。

原A独占最强工程窗一次合并修F01—F05及定向验证。新增精确两个合成库、未提交事务权限/角色反例、新私有根准确合成正文删除和wall前向cap72000已获采用；其他次数/容器/卷cap不变，旧投入与失败未知全保留。旧实例/旧批准不延不解冻，修订015只用于新库，旧精确hash及包保留兼容。真实Q、真实付费/preview/Git不授权。

完整同号续作07卡已保存到DocuN/tasks/TASK-120.md置顶，合同快照/采用回执/permit/输入核对/旧共享与返回账快照在DocuN/evidence/TASK-120/orchestration-adopted07-20261021；待人工转交，不声称工程已接收或启动。下方历史停止通知仅在本卡范围内前向覆盖，旧事实不改。工程原结果/源码/审计/唯一预算均未写入，主控运行0。

完成后原TASK121增量复核，不重做充分正常链/共同100门等。当前五缺陷仍开放，修复成功不能自签；历史控制不通过不被新许可追认，原S有限关闭保持，STEP018整体/M1/项目未通过。

以下为原裁定，原字节保留。
''',old[shared[0]]))
put(ROOT/shared[1],prepend(f'''# 架构动态文档

文档v1.56，2026-10-21，Asia/Shanghai。需求v1.4、执行动态v2.84、task_model/07。以下v1.55原字节保留。

## AP12007修复与精确验证边界已采用，实施待原窗执行

{STAMP}。用户已批准修正原Q合同的F01—F05。迁移015补全必需权限，新安装用修订hash、旧R03按原精确hash兼容读取；profile核实际INHERIT/SET及危险能力；源/记忆精确清理覆盖Q正文，失败关相关资格；批准采用可解释单调/UTC时限及不可逆失效；PG已领取事实单独封闭投影/续批，合法worker不误拒。均为待实施修复，不登记已验证。

仅两个新合成库、既有精确源容器内的事务权限反例和新根最多16正文精确清理获准，旧库/旧根/旧凭证/001—014及业务表结构不变。批准内部必要Q时钟见证，不增加provider消息/公开wire/费用账。旧R03样本不追认为经过新迁移前提，新兼容必须逐项证据绑定。真实Q启用条件与原独审增量复核仍保留；原正常链/ACK/C12等有效结论按影响继承。

## 以下为v1.55及更早历史
''',old[shared[1]]))
changes=[
 (shared[0],'记录用户批准AP12007、同号续作07签发与旧判定不改。'),
 (shared[1],'v1.56登记五项修复与严格新旧迁移身份/合成验证边界已采用、实施待执行。'),
 (shared[2],'v2.84登记原A同窗续作07保存待转交、前向许可与旧账保留。'),
 (shared[3],'置顶已批准完整五项修复合同，旧停止与合同原字节保留，按当前卡优先。'),
 ('DocuN/evidence/TASK-120/orchestration-adopted07-20261021','保存批准绑定、精确permit、完整合同、322身份核对、返回账/旧共享快照和保存读回；未执行业务。')]
entries='\n\n'+'\n\n'.join(f'- CHG-{1569+i:04d}，{STAMP}，Codex编排Agent，{path}。{why}' for i,(path,why) in enumerate(changes))+'\n'
put(ROOT/shared[4],old[shared[4]]+entries.encode('utf-8'))

for row in closing['rows']:
    p=Path(row['path'])
    assert (sha(p.read_bytes()) if p.is_file() else None)==row['actual'],row['path']
assert budget_path.read_bytes()==budget_raw and sha(events_path.read_bytes())==events_hash
for name in shared[:4]:
    assert (ROOT/name).read_bytes().endswith(old[name])
assert (ROOT/shared[4]).read_bytes().startswith(old[shared[4]])
assert sha(draft.read_bytes())==adoption['approved_draft_sha256']
assert sha(proposal.read_bytes())==adoption['approved_proposal_sha256']
assert (ROOT/'DocuN/tasks/TASK-120.md').read_bytes().startswith((OUT/'contract.md').read_bytes())
putj(OUT/'save-proof.json',{
 'state':'ADOPTED_CONTRACT_SAVED_READABLE_AWAITING_MANUAL_HANDOFF',
 'issued_at':STAMP,'permit_id':ID,'task':'TASK-120','R':'R-114','contract_bytes':len(contract),
 'contract_sha256':sha(contract),'canonical_card_sha256':sha((ROOT/shared[3]).read_bytes()),
 'input_rows_match':len(closing['rows']),'rules_match':len(rules),'versions':['2.84','1.56'],
 'next_CHG':1574,'product_runtime':0,'engineering_ledger_writes':0,
 'actual_executor_receipt':'NOT_YET_REPORTED','previous_bytes_preserved':True})
print(json.dumps({'state':'ADOPTED_SAVED_READABLE_AWAITING_HANDOFF','task':'TASK-120','R':'R-114',
 'contract_bytes':len(contract),'identity_rows_match':len(closing['rows']),'next_CHG':1574,'runtime':0},ensure_ascii=False))
