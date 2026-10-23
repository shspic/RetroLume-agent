"""主控有限核证与原独审增量转卡；只读产品/原证据，只写编排材料。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,os,re,zipfile

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
A=ROOT/'DocuN/evidence/TASK-121/orchestration-review02-20261021'
E=ROOT/'DocuN/evidence/TASK-120/execution'
B=E/'audit-repair-08'
NOW=datetime.now(timezone(timedelta(hours=8)))
STAMP=NOW.isoformat(timespec='microseconds')
def sha(x):return hashlib.sha256(x).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(p,x):
    p=p.resolve();assert p.is_relative_to(ROOT)
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.review02.tmp')
    with tmp.open('xb') as s:s.write(x);s.flush();os.fsync(s.fileno())
    os.replace(tmp,p);assert p.read_bytes()==x
def js(p,x):put(p,(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def prefix(text,old):return (text.strip()+'\n\n').replace('\n','\r\n').encode('utf-8')+old
def item(p):return {'path':str(p.relative_to(ROOT)).replace('\\','/') if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes()) if p.is_file() else None,'bytes':p.stat().st_size if p.is_file() else None}

assert not (OUT/'save-proof.json').exists()
rules=load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for x in rules:assert sha(Path(x['absolute_path']).read_bytes())==x['sha256']
f=load(B/'final-file-identities-completed.json')
assert len(f['baseline606_references'])==606 and len(f['changed_product_paths'])==5
assert len(f['registered_current_files'])==18 and len(f['changes'])==15
current={};protected={}
for row in f['baseline606_references']:
    p=Path(row['path'])
    if row['status']=='AUTHORIZED_LEDGER_OR_RESULT_PREFIX':continue
    h=sha(p.read_bytes()) if p.is_file() else None
    assert h==row['sha256'],row['path']
    current[str(p).lower()]=item(p)
    if h:protected[p]=h
for row in f['registered_current_files']:
    p=ROOT/row['path'];assert sha(p.read_bytes())==row['sha256'],row['path']
    current[str(p).lower()]=item(p);protected[p]=row['sha256']
for row in f['changes']:assert sha((ROOT/row['path']).read_bytes())==row['sha256'],row['path']
report=ROOT/'DocuN/results/TASK-120-result.md';raw=report.read_bytes()
post=load(B/'post-save-verification-completed.json')
assert sha(raw)==post['report_sha256']=='c9db53c3d86819a8b0658b2f0c7c23a331ca43dc760ef23e03a3adc602d1cc62'
assert len(raw)==134777
assert sha(raw[-109435:])=='3772e95062f1f423b299ee6542364a5ce0ca8c4eae92717b35b41efca79a86a4'
protected[report]=sha(raw)
budget_path=E/'budget.json';events_path=E/'events.jsonl'
budgetraw=budget_path.read_bytes();eventsha=sha(events_path.read_bytes());budget=load(budget_path)
assert budget['active_root'] is None and budget['active_command'] is None
assert budget['counts']['roots']==64 and budget['counts']['pg_starts']==64
assert budget['engineering_status']=='TARGETED_REPAIR08_COMPLETE_STOPPED_READY_FOR_TASK121_DELTA_REVIEW'
assert len(budget['failures'])==149 and abs(budget['command_wall_conservative_upper_seconds']-69357.418110)<.001
oldbudget=load(ROOT/'DocuN/evidence/TASK-120/orchestration-repair08-20261021/returned-ledger/budget.json')
assert budget['roots'][:60]==oldbudget['roots']
assert budget['failures'][:141]==oldbudget['failures']
protected[budget_path]=sha(budgetraw);protected[events_path]=eventsha
approval=load(B/'sample-method-user-adoption.json')
assert approval['explicitly_approved'] is True
assert approval['user_answer']=='允许这个最小清理夹具调整'
assert approval['no_window_or_caps_extended'] is True
package=load(B/'completed-candidate-package-identity.json');zp=ROOT/package['path']
assert sha(zp.read_bytes())==package['sha256']=='15ec6b364ca9d16e2020a2c17640a655f5074bc9464f57a6747ac239e5e62ae4'
assert zp.stat().st_size==1341581
with zipfile.ZipFile(zp) as z:
    assert len(z.infolist())==147
    assert not any(x.filename.lower().endswith('.zip') for x in z.infolist())
oldpackages=load(B/'old-packages-preserved-completed.json')['ten_prior_ZIPs_including_blocked08_snapshot']
assert len(oldpackages)==10
for row in oldpackages:assert sha((ROOT/row['path']).read_bytes())==row['sha256'],row['path']
stop=load(B/'final-stop-proof-completed.json')
assert stop['unresolved']==[] and stop['08_stop_dimensions_confirmed'] is True
assert stop['source_container']['state']['Running'] is False and stop['source_container']['state']['Pid']==0
assert stop['restore_target']['running'] is False and stop['restore_target']['Pid']==0
assert all(not x['listening'] for x in stop['ports'].values())
receipts={}
for n in ('1005','1006'):
    r=load(B/f'command-{n}.receipt.json');assert r['exit_code']==0 and r['tree_empty'] is True
    receipts[n]={k:r[k] for k in ('start_utc','end_utc','wall_seconds','exit_code','tree_empty')}
prior_audit=ROOT/'DocuN/results/TASK-121-result.md'
assert len(prior_audit.read_bytes())==55795
assert sha(prior_audit.read_bytes())=='75d40d166010d29b28065327a8a911a859200d6da01cac080ab13b72748da595'
protected[prior_audit]=sha(prior_audit.read_bytes())
prior_receipt=load(ROOT/'DocuN/evidence/TASK-121/audit/review-01/session-receipt.json')
assert abs(prior_receipt['cumulative_conservative_charge_seconds']-1459.2202126)<.001
deadline='2026-10-22T00:51:52.291692+08:00'
assert NOW<datetime.fromisoformat(deadline)
contract=(A/'contract.md').read_bytes();ct=contract.decode('utf-8-sig')
for x in ('F02','F03','不可授权','最小夹具','1459.2202126','1200','00:51:52.291692','全部0','shared Q policy'):
    assert x in ct,x
assert '*' not in ct and '〈' not in ct
shared=['DocuN/results/TASK-120-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuN/tasks/TASK-120.md','DocuN/tasks/TASK-121.md','DocuS/文档变更记录.MD']
old={n:(ROOT/n).read_bytes() for n in shared}
assert '文档v2.86' in old[shared[2]].decode('utf-8-sig')[:200]
assert '文档v1.58' in old[shared[1]].decode('utf-8-sig')[:200]
assert max(map(int,re.findall(r'CHG-(\d{4})',old[shared[5]].decode('utf-8-sig'))))==1584
raw_entries=[item(p) for p in sorted(B.rglob('*')) if p.is_file()]
for n,x in old.items():put(OUT/'before'/n,x)
put(OUT/'returned-ledger/budget.json',budgetraw)
inputs={
 'frozen_at':STAMP,'rules':rules,'current_frozen_files':list(current.values()),
 'registered_current_files':f['registered_current_files'],'changes':f['changes'],
 'raw_engineering_evidence':raw_entries,'unique_latest_ledger':[item(budget_path),item(events_path)],
 'opaque_engineering_result':item(report),'prior_audit_result':item(prior_audit),
 'prior_audit_receipt':item(ROOT/'DocuN/evidence/TASK-121/audit/review-01/session-receipt.json'),
 'completed_archive':item(zp),'archive_entries':147,
 'engineering08_contract':item(ROOT/'DocuN/evidence/TASK-120/orchestration-repair08-20261021/contract.md'),
 'engineering08_permit':item(ROOT/'DocuN/evidence/TASK-120/orchestration-repair08-20261021/permit.json'),
 'sample_method_adoption':item(B/'sample-method-user-adoption.json')}
js(A/'audit-inputs.json',inputs)
js(A/'scope-index.json',{
 'scope':'Original F02 ADMIN combination and F03 memory pending projection, all five08 products and direct effects only',
 'product_paths_changed':f['changed_product_paths'],'changes':f['changes'],
 'source_diff':item(B/'source.diff'),'fixture_diff':item(B/'fixture-completed.diff'),
 'preimage_directory':str(B/'preimage'),
 'exact_fixture_directories':[str(B/'asrun-root063'),str(B/'asrun-root064')],
 'asrun_map':item(B/'as-run-final-completed.json'),
 'evidence_index':item(B/'final-review-index-completed.json'),
 'impact_matrix':item(B/'impact-matrix-completed.json'),
 'method_adoption':item(B/'sample-method-user-adoption.json'),
 'index_engineering_PASS_values_are_navigation_not_independent_judgment':True,
 'specific_direct_effects':['shared read policy inheritance and lock order','server-only read classification and authority skip versus write guard',
    'no-Q and sealed-target compatibility','non-authorizing Q-body fixture efficacy and exact normal cleanup/projection entry',
    'real API restart plus browser reload/explicit retry and DB idempotence']})
permit={
 'id':'TASK-121-READONLY-INCREMENTAL-REVIEW-02-20261021','issued_at':STAMP,
 'task':'TASK-121','R':'R-115','review':'review-02','STEP':'STEP018',
 'state':'SAVED_READABLE_AWAITING_MANUAL_HANDOFF_NOT_RECEIVED_OR_STARTED',
 'receiver':'Same original TASK121 A+ independent audit window',
 'contract_sha256':sha(contract),'input_manifest_sha256':sha((A/'audit-inputs.json').read_bytes()),
 'scope_index_sha256':sha((A/'scope-index.json').read_bytes()),
 'runtime_counts':{k:0 for k in ('compile','unittest','product_or_test_import','PG','Docker','API','Windows_Job','Browser','build','model','business_network','Git')},
 'metadata_only_stdlib_hash_diff_zip_saved_record_comparison':True,
 'audit_cumulative_tool_cap_seconds':3600,'prior_conservative_audit_seconds_retained':1459.2202126,
 'this_increment_tool_cap_seconds':1200,'single_metadata_command_cap_seconds':60,
 'calendar_deadline_inherited':deadline,'old_review01_window_not_reset':True,
 'first_finite_read_clock_bootstrap_allowed_and_charged':True,
 'existing_official_reference_limit_retained':True,
 'writes':['DocuN/evidence/TASK-121/audit/review-02/','DocuN/results/TASK-121-result.md'],
 'prior_result_exact_suffix_bytes':55795,'prior_result_sha256':sha(prior_audit.read_bytes()),
 'forbidden_decode':['TASK-120-result.md','TASK-120-work-decision.md','engineering result archive entries and implementation thinking/context'],
 'read_private_runtime_or_vault_credentials':False,'engineering_frozen':True,'real_Q':'FROZEN',
 'main_runtime':0}
js(A/'audit-permit.json',permit)
js(OUT/'bounded-review.json',{
 'checked_at':STAMP,'baseline_reference_rows_checked':606,'unique_current_identity_count':len(current),
 'registered_current_files':18,'registered_changes':15,'product_changes':5,
 'raw_engineering_files':len(raw_entries),'rules_match':len(rules),'mismatches':[],
 'report_identity':item(report),'old109435byte_suffix_exact':True,
 'sample_method_approval':approval,
 'approval_interpretation':'本轮工程记录明确答复且用户当前回传确认已批准方法；不倒签精确人工时刻，不将清理夹具当业务授权',
 'archive_identity':item(zp),'archive_entries':147,'old_ten_zip_hashes_match':True,
 'root_and_failure_prefix_match':True,'current_failures':149,'package_save_time_failures':148,'original_TASK117_failures':81,
 'latest_budget_counts':budget['counts'],'latest_wall':budget['command_wall_conservative_upper_seconds'],
 'latest_holding':budget['runtime_holding_union_seconds'],'active_root':None,'active_command':None,
 'accounting_limit':'1006 reserve replacement plus later finite metadata/readback envelope; latest sole ledger149/69357.418110, not only save snapshot148/69322.102513',
 'stop_record_original_utc':stop['utc'],'this_round_registered_processes':len(stop['registered_processes']),
 'this_round_registered_jobs':len(stop['registered_jobs']),'unresolved':stop['unresolved'],'close_receipts':receipts,
 'old_unknown20_preserved_with_prior_accepted_alternatives':True,
 'screenshots_read':['memory08-page-reopened-pending.png','memory08-page-reopened-done.png'],
 'main_runtime':0,'live_resource_probe':False,'independent_technical_closure':'pending original TASK121 review02'})
state=f'''# 执行动态文档

文档v2.87，2026-10-21，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.59、task_model/07。以下v2.86原字节保留。

## TASK120续作08完整候选已返回冻结，原TASK121 review-02增量复核已登记

{STAMP}。工程08原受阻样本问题由用户明确允许“这个最小清理夹具调整”后接续，新完成结果已返回。主控核606引用、五产品/18注册15变化、原始ADMIN组合PG、夹具批准/正常memory清理POST-三GET/API重开/浏览器原件及两截图、准确文件/金融/包/1005-1006停止和最新账；仅有限文件与记录核对，没有业务运行或独审。前三关闭保持，F02/F03关闭仍待独立结论，工程候选不得自签通过。

DISPATCH_STATUS

工程原A/旧A+停止，产品/fixture/dist/工程报告/账冻结；root与PG启动均64/64到门，余量不恢复业务。原121同窗口只审两项和五文件直接影响，真实运行0。原累计审计cap3600、已用保守1459.2202126/unknown保持，本轮增量至多1200s，单命令60s，原审计截止2026-10-22 00:51:52.291692+08不延长。

本轮方法只生成不可授权Q副本依赖清理夹具，真实HTTP新memory/ControlHub及准确文件故障→GET→API重开→原bundle明确retry→页面reload/新Hub回放为补证；不赋模型链/来源资格/合法外发。活动/root/grant不改，新准入/批准/claim/dispatch增0，准确新文件1，总7/16；main仍5/1250000，旧实例不加总，旧UNKNOWN/007保留。

累计root64/64、PG64/64、API65/96、Browser15/16、build5/8、Native69/128、HTTP1572/10000，容器卷创建及对象2/2。唯一账149失败（完成包时148、停后元数据读已缺席旧JS错误再记1），旧141前缀/117的81保留；wall69357.418110/72000，holding2943.704295/21600，active空。保存时69322.102513含1006预留，后续只读核证区间前向入账，旧预留不重复扣/抹零。原业务/收尾/96h时窗均未重开。

1005于2026-10-21T12:01:58.174181Z核本轮28组PID/birth、8Job、unresolved0、两精确CID stopped/Pid0、三端口无监听，1005/1006 exit0/tree_empty；旧079 unknown20与独审替代证明原样限定。主控未查实时服务。Q/provider/实际费用/preview/Git继续冻结或0，STEP018整体/019/020/M1/项目未通过。CHG1585—1590，下一1591。

## 以下为v2.86及更早历史
'''
registered=prefix(state.replace('DISPATCH_STATUS','同TASK121/R115 review-02已登记，完整增量卡正在保存，未声称已接收或开始。'),old[shared[2]])
put(ROOT/shared[2],registered);put(OUT/'registration-state.bytes',registered)
put(ROOT/shared[4],contract+b'\r\n\r\n---\r\n\r\n'+old[shared[4]])
assert (ROOT/shared[4]).read_bytes().startswith(contract)
put(ROOT/shared[2],prefix(state.replace('DISPATCH_STATUS','原TASK121/R115 review-02完整卡已保存读回，待人工转交原独立A+窗口，未声明已接收或启动。输入/范围/只读permit在DocuN/evidence/TASK-121/orchestration-review02-20261021；卡DocuN/tasks/TASK-121.md当前置顶。'),old[shared[2]]))
put(ROOT/shared[0],prefix(f'''# TASK-120 / R-114 续作08完成候选回收与原121 review-02安排（当前有效）

{STAMP}。收到工程完整结果，原受阻报告和失败保留。用户当前确认F03采用已批准最小清理夹具，工程原件保存明确答复“允许这个最小清理夹具调整”及原范围/不延窗。主控核606引用、五产品变化/18注册/15变化、原BEGIN-ROLLBACK权限记录、清理/GET/API重开/浏览器原件、截图、10旧包和147条目新包、1005/1006及唯一账。仅有限核证，不执行产品或独审。

收存F02/F03修复候选，原F01/F04/F05已关闭保持；当前两项技术关闭待原TASK121独立增量结论，不把工程PASS当验收。清理样本明确不可授权、不证明正常请求装配；其效力是否覆盖准确副本故障读回/重开/重试目标交独审判断，不重复原正常模型/来源资格全链。

原A/旧A+工程冻结，源码/测试/dist/结果/唯一账只读。root/PGstart64/64均耗尽，无后续业务许可。原121 review02完整卡同号已保存待人工转交，运行0、原3600累计审计cap/1459.2202126旧投入/unknown保留，增量1200、原截止00:51:52+08不延长。不新开全面审计或TASK/R。

唯一账149失败/旧141及117的81保留，完成包148与停后元数据错误区分；wall69357.418110/72000、holding2943.704295/21600，当前active空。main5/1250000不变，新收费/批准/claim/dispatch0，新准确删1累计7；旧实例不相加。1005只核其原时间本轮28PID/8Job与精确容器/端口，不重解释原079 unknown为新鲜退出。主控无实时探针。

Q保持冻结，STEP018整体/M1/项目未通过。工程报告/原预算/源/审计未由主控改写。以下原裁定字节保留。
''',old[shared[0]]))
put(ROOT/shared[1],prefix(f'''# 架构动态文档

文档v1.59，2026-10-21，Asia/Shanghai。需求v1.4、执行动态v2.87、task_model/07。以下v1.58原字节保留。

## 两剩余边界已有修复候选与定向实证，独审待确认

{STAMP}。q_roles将ADMIN可再授权后的SET/INHERIT/后续ADMIN潜在能力纳入有界检查；实际原快照主体完成组合GRANT/SET能力演示并事务回滚，正常图保持。memory新增cleanup_projection为原GET收据/详情/列表统一组合状态；shared policy→PG→短journal锁，pending/unknown/重现不回退done，原DB已提交清理不回写。activities.repository只读持policy小依赖及memory service/api接线共五产品变化，写/费用/007/worker/联合时钟与015/profile/codec未改。

F03用户采用不可授权最小副本依赖夹具，仅补正常HTTP清理文件失败、三GET、API重开、原正式bundle明确retry及页面重开/新Hub确认；它不是正常模型来源/请求装配证明。前端产品/dist未改，实际网络hash绑定旧正式bundle，旧充分链按review01继承。两项修复尚待原121 review02独立确认，原三项关闭、source-delete attempt限定结论保持，Q及STEP018整体不放行。

## 以下为v1.58及更早历史
''',old[shared[1]]))
put(ROOT/shared[3],prefix(f'''# TASK-120 当前工程冻结通知——08完成候选已返回，待原121 review-02

{STAMP}。工程08在明确批准最小清理夹具后补齐并返回，原部分/受阻/FAIL均保留。当前产品/测试/dist/工程结果/原件及唯一预算事件冻结，原A/旧A+停止。root64/64、PGstart64/64均到累计门，原08合同不再提供业务入口；Browser等剩余不授权自动重启。

原TASK121独立窗口按 D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-121.md 当前review-02只读增量卡接续。Q继续冻结。以下旧08及历史合同完整保留，只作授权/尝试历史。
''',old[shared[3]]))
entries=[(shared[0],'收存08完成候选和夹具采用/原证据，交原121只读增量，不预签两项关闭。'),
 (shared[1],'v1.59登记ADMIN闭包和记忆清理组合投影五文件修复候选/方法限定，独审待决。'),
 (shared[2],'v2.87登记工程已返回冻结、原121 review02保存待转交、最新149/69357.418110账。'),
 (shared[3],'置顶root/PG耗尽及08完成后的工程冻结通知，旧许可/历史原字节保留。'),
 (shared[4],'置顶原121同号review02完整只读增量合同，只审两边界和真实影响，原时窗/累计工具额度不重置。'),
 ('DocuN/evidence/TASK-120/orchestration-return08-20261021及TASK-121/orchestration-review02-20261021','保存有限核证、当前身份/原始材料索引、许可、旧共享/返回账和读回，不执行产品。')]
changes='\n\n'+'\n\n'.join(f'- CHG-{1585+i:04d}，{STAMP}，Codex编排Agent，{n}。{why}' for i,(n,why) in enumerate(entries))+'\n'
put(ROOT/shared[5],old[shared[5]]+changes.encode('utf-8'))
for p,h in protected.items():assert sha(p.read_bytes())==h,str(p)
assert budget_path.read_bytes()==budgetraw and sha(events_path.read_bytes())==eventsha
for n in shared[:5]:assert (ROOT/n).read_bytes().endswith(old[n])
assert (ROOT/shared[5]).read_bytes().startswith(old[shared[5]])
assert (ROOT/shared[4]).read_bytes().startswith(contract)
js(A/'dispatch-readback.json',{'state':'SAVED_READABLE_NOT_DISPATCHED','issued_at':STAMP,
 'card':str(ROOT/shared[4]),'card_sha256':sha((ROOT/shared[4]).read_bytes()),
 'contract_sha256':sha(contract),'permit_sha256':sha((A/'audit-permit.json').read_bytes())})
js(OUT/'save-proof.json',{'state':'REVIEW02_SAVED_READABLE_AWAITING_MANUAL_HANDOFF','issued_at':STAMP,
 'task':'TASK-121','R':'R-115','review':'review-02','contract_bytes':len(contract),
 'current_files_frozen':len(current),'raw_evidence_files_frozen':len(raw_entries),'runtime':0,
 'versions':['2.87','1.59'],'next_CHG':1591,'engineering_ledger_writes':0})
print(json.dumps({'state':'REVIEW02_SAVED_READABLE_AWAITING_HANDOFF','task':'TASK-121','R':'R-115',
 'contract_bytes':len(contract),'frozen_current_files':len(current),'raw_evidence_files':len(raw_entries),
 'runtime':0,'next_CHG':1591},ensure_ascii=False))
