"""Bounded filesystem-only complete candidate return. No runtime start."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,copy,difflib,hashlib,json,os,time,zipfile
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4];started=time.monotonic()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def write(p,v):
 p=Path(p);temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p)
assert not (HERE/'final-review-index.json').exists(),'Already returned; inspect rather than rewrite'
b=read(EX/'budget.json');prior=read(HERE/'budget.json.before.bytes');adoption=read(HERE/'adoption.json')
assert b['active_root'] is None and b['active_command']['manifest']=='command-071.json'
assert b['roots'][:40]==prior['roots'] and b['failures'][:111]==prior['failures']
assert (EX/'events.jsonl').read_bytes().startswith((HERE/'events.jsonl.before.bytes').read_bytes())
assert b['counts']['roots']==51 and all(b['counts'][k]==0 for k in ('provider_calls','actual_fee_microunits','preview_creates','preview_starts','Git_writes'))
stop=read(HERE/'final-stop-proof-after-readonly.json');own=read(HERE/'command-070.receipt.json')
assert stop['all_fresh_stop_dimensions_confirmed'] and own['tree_empty'] and own['exit_code']==0
required=['new-R03-bootstrap-PASS.json','real-profile-ACL-and-guard-PASS.json','actual-scope-shrink-PASS.json','scope-targeted-negatives-PASS.json','K2-scope-shrink-PASS.json','late-context-UI-PASS.json','readonly-listing-PASS.json','readonly-listing-UI-PASS.json','old-R02-and-final-readonly-reconciliation-PASS.json']
for name in required:assert read(HERE/name)['status']=='PASS',name
assert read(HERE/'old-new-package-compatibility.json')['status']=='PASS_OFFLINE_FILE_CODEC_ONLY'
report=ROOT/'DocuN/results/TASK-120-result.md';old=(HERE/'result.before.bytes').read_bytes();assert report.read_bytes()==old and hashlib.sha256(old).hexdigest()==adoption['old_result_sha256']

baseline={x['path']:x['sha256'] for x in read(HERE/'baseline-identities.json')['verified_05_paths']}
new_paths=['backend/migrations/015_activity_scope_delete_permission.sql','backend/tests/test_scope_delete_profile.py','backend/tests/fixtures/task120/continuation06.py','backend/tests/fixtures/task120/restore06.py','frontend/tests/task120-continuation06-ui.mjs','frontend/tests/task120-continuation06-readonly-view.mjs']
for p in (HERE/'preimage').rglob('*'):
 if p.is_file():baseline.setdefault(p.relative_to(HERE/'preimage').as_posix(),sha(p))
for name in new_paths:baseline.setdefault(name,None)
changes=[];identities=[];source=[];fixture=[];dist=[]
for name,expected in sorted(baseline.items()):
 p=ROOT/name;actual=sha(p) if p.is_file() else None;identities.append({'path':name,'sha256':actual})
 if actual==expected:continue
 item={'path':name,'before_sha256':expected,'after_sha256':actual};changes.append(item)
 if name.startswith('frontend/dist/'):dist.append(item);continue
 assert actual is not None,name
 before=HERE/'preimage'/name
 if expected is not None:assert before.is_file() and sha(before)==expected,name
 left=before.read_text(encoding='utf-8-sig').splitlines(True) if before.exists() else []
 delta=list(difflib.unified_diff(left,p.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+name if before.exists() else '/dev/null',tofile='after/'+name))
 if name.startswith(('backend/app/','backend/migrations/','frontend/src/')):source.extend(delta)
 else:
  assert name.startswith(('backend/tests/','frontend/tests/')),name
  fixture.extend(delta)
for p in (ROOT/'frontend/dist').rglob('*'):
 if p.is_file() and rel(p) not in baseline:dist.append({'path':rel(p),'before_sha256':None,'after_sha256':sha(p)});identities.append({'path':rel(p),'sha256':sha(p)})
(HERE/'source.diff').write_text(''.join(source),encoding='utf-8');(HERE/'fixture.diff').write_text(''.join(fixture),encoding='utf-8')
product_paths=[x['path'] for x in changes if x['path'].startswith(('backend/app/','backend/migrations/','frontend/src/'))]
assert len(product_paths)==8,product_paths
asrun=[]
for number in (46,51):
 path=EX/f'root-{number:02d}-batch-01-as-run.json';rows=read(path)['files'];mismatch=[];checked=0
 for x in rows:
  if x['path'].startswith(('backend/app/','frontend/src/','frontend/dist/')):
   checked+=1
   if sha(ROOT/x['path'])!=x['sha256']:mismatch.append(x['path'])
 assert mismatch==(['backend/app/activities/repository.py'] if number==46 else []),mismatch
 asrun.append({'path':rel(path),'sha256':sha(path),'product_files_checked':checked,'final_mismatches':mismatch})
write(HERE/'final-file-identities.json',{'baseline':'baseline-identities.json;202 paths verified including explicit absent identities','current':identities,'changes':changes,'new_generated_dist':dist,'product_paths_changed':product_paths,'as_run':asrun,'root46_to_final_product_delta':'Only sealed-reader pure-read Q construction order; normal source reads/write/claim and captured normal GETs retain old branch. Final readonly projection proved by real API50 and UI51.','frontend_bundle_for_both_late_guards_and_final_readonly_view':'formal build063; actual JS/CSS hashes in roots46/51','later_fixture_delta':'Readonly-only diagnostic/observation helpers and old-profile reconciliation; original as-run files never rewritten'})
for x in read(HERE/'formal-bundle-identities.json')['assets']:assert sha(ROOT/x['path'])==x['sha256']
old_packages=read(EX/'finalization-05/old-packages-preserved.json')['six_old_packages']+[read(EX/'finalization-05/candidate-package-identity.json')]
for x in old_packages:assert sha(ROOT/x['path'])==x['sha256'],x['path']
write(HERE/'old-packages-preserved.json',{'seven_prior_packages':old_packages,'nested_ZIPs_in_new_package':0})
finance=read(HERE/'final-fresh-financials-separated.json');target_finance=read(HERE/'restore-target-final-after-readonly-UI.json')
assert finance['old_four_exactly_unchanged'] and target_finance['requests']==5 and target_finance['cost']==1250000
write(HERE/'financial-summary.json',{'authority':'Actual application-role readonly PG connections for old four/source in47; target fresh production saved-records PG read in51 after rejected cancellation','instances':{s:{'requests':v['requests'],'cost_reserved_microunits':v['cost'],'activities':v['activities']} for s,v in finance['instances'].items()},'restored_copy':target_finance,'raw_source_and_old_four':'final-fresh-financials-separated.json','raw_target':'restore-target-final-after-readonly-UI.json','no_sum_of_instances_or_restore_copy':True,'actual_provider_calls':0,'actual_fee_microunits':0})

inherited=read(EX/'finalization-05/acceptance-matrix.json')['C01_C15'];matrix=copy.deepcopy(inherited)
updates={
 'C04':('PASS_LISTED_BODY_AND_READONLY_BOUNDARIES','Original missing/copy/tail/delete/memory proofs inherited; new exact R03 readonly ACL/guard plus actual frozen/selected context. Normal Q remains denied.', ['real-profile-ACL-and-guard-PASS.json','readonly-cancel-mutation-denied.json']),
 'C06':('PASS_EXACT_ADOPTED_SOURCE_AND_FACTORY_TARGET','Original CID/volume plus one authorized new logical source and one production factory target/volume; exact labels, port55481 and two-object caps retained.',['new-R03-bootstrap-PASS.json','actual-restore-target-created.json','factory-preflight.json']),
 'C07':('PASS_LISTED_NO_RESEND_AND_CURRENTNESS','All original UNKNOWN event sequences unchanged; new claimed/UNKNOWN and three approved-unclaimed intents retained, source frozen/selected target never restores continuation rights.',['retained-original-Q-witness.json','final-protocol-currentness-witness.json']),
 'C11':('PASS_LISTED_K2_INCLUDING_TRUE_SCOPE_SHRINK_WITH_INHERITED_MEMORY_LIMIT','Original head/revoke/source/scope-add and bounded memory traces reused. New actual removal and scope-shrink K2 close prior permission gap; memory original missing before-financial limitation remains for independent audit.',['actual-scope-shrink-PASS.json','K2-scope-shrink-PASS.json','scope-targeted-negatives-PASS.json']),
 'C13':('PASS_LISTED_LATE_FENCES_AND_FINAL_READONLY_VIEW','Original owner/view/head/scope inherited. Root46 proves full DataContext and namespace with two real captured normal approved GETs; final pure-read projection API50/UI51 closes final-view defect.',['UI-complete-DataContext-PASS-root-46.json','UI-namespace-PASS-root-46.json','readonly-listing-PASS.json','readonly-listing-UI-PASS.json']),
 'C14':('PASS_FINAL_EXACT_BOTH_CID_STOP','Final070 exact PID/birth/Jobs, both CID stopped/Pid0 and55480/55481/18120 free;070 own exit0/tree_empty. Final071 saves files only.',['final-stop-proof-after-readonly.json','command-070.receipt.json']),
 'C15':('PASS_ENGINEERING_CANDIDATE_READY_FOR_INDEPENDENT_AUDIT','A-D complete for approved bounded scope; final source/fixture/dist/as-run, financials, full failures and preserved history. Independent audit/acceptance/Q activation are not signed.',['final-file-identities.json','financial-summary.json','remaining-gaps.json'])}
for x in matrix:
 if x['id'] in updates:
  status,facts,paths=updates[x['id']];x.update(status=status,facts=facts,evidence=[rel(HERE/p) for p in paths])
 else:x['inherited_from']='DocuN/evidence/TASK-120/execution/finalization-05/acceptance-matrix.json'
write(HERE/'acceptance-matrix.json',{'C01_C15':matrix,'card06_groups':{'A':'PASS_EXACT015_R03_AND_OLD_COMPATIBILITY','B':'PASS_REAL_SHRINK_AND_ITS_K2','C':'PASS_BOTH_ACTUAL_LATE_UI','D':'PASS_COMPLETE_CANDIDATE_EVIDENCE_AND_STOP'},'inherited_evidence_not_rerun':True,'memory_before_financial_limit_retained':True,'engineering_complete':True,'stable_for_independent_audit':True,'independent_audit_started':False})
write(HERE/'remaining-gaps.json',{'engineering_complete_for_approved_card06':True,'stable_for_independent_audit':True,'known_required_engineering_gaps':[],'limits':['Original root35 memory-before-financial snapshot was not immediately saved; existing bounded reconciliation inherited as accepted by card06, not rewritten as stronger evidence.','R01 compatibility is immutable constants and a real ZIP reader test; no claim of a new live R01 database restore. R02 actual normal/frozen PG reads and R03 actual backup/restore were tested.','Late proof captures normal responses before freeze and delivers them to native fetch; the business guard intentionally rejects before JSON consumption. No claim that stale bodies were consumed by business handlers.','Namespace capabilities uses one actual authenticated request crossing selector/rebind. Original response header and new production caps body are retained; no setter/token/body injection.','A complete candidate is not independent-audit, project-release or real-Q approval; unknown future defects are not promised absent.'],'independent_audit_required':True,'new_runtime_not_requested':True})

for x in matrix:
 for p in x['evidence']:assert (ROOT/p).is_file(),p
b['failures'].append({'case':'continuation06-metadata-read-and-baseline-diagnostics','classification':'metadata_only_not_independent_product_defects','items':['Windows literal path glob and several guessed source paths were absent; targeted directory rg reads used instead.','Baseline first reader attempted a retained absent asset identity; corrected to honor the original null hash before any preimage/product mutation.']})
now=datetime.now(timezone.utc);end=datetime.fromisoformat(b['active_command']['start_utc']);entry=datetime.fromisoformat(adoption['actual_receipt_observed_utc'])
measured=(b['controlled_command_wall_seconds']-prior['controlled_command_wall_seconds'])+(b['runtime_command_wall_seconds']-prior['runtime_command_wall_seconds'])
envelope=(end-entry).total_seconds()+3
b['continuation06_unwrapped_command_wall_upper_seconds']=max(0,envelope-measured)+60
b['continuation06_timing']={'entry_utc':entry.isoformat(),'end_before_final071':end.isoformat(),'observed_interval_upper_seconds':envelope,'separately_measured_new_roots_and_commands_before071_seconds':measured,'post_save_metadata_reserve_seconds':60,'initial_read_clock_resolution_reserve_seconds':3,'manual_total':'UNKNOWN_NOT_ZERO','note':'Continuous work envelope used only as conservative unmeasured/read-edit uncertainty ceiling. Approval/queue gaps are not claimed as measured work/CPU; their exact split is unknown. No new7200 reservation and no overlap with measured runtime/command receipts.071 adds actual measured wall after exit.'}
keys=('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds','continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds','validation04_unwrapped_command_wall_upper_seconds','finalization05_unwrapped_command_wall_upper_seconds','continuation06_unwrapped_command_wall_upper_seconds')
b['command_wall_conservative_upper_seconds']=sum(b.get(k,0) for k in keys);ceiling=b['command_wall_conservative_upper_seconds']+60
assert ceiling<57600 and b['runtime_holding_union_seconds']<21600
b.update(engineering_status='CONTINUATION06_COMPLETE_STOPPED_READY_FOR_INDEPENDENT_AUDIT',real_Q='FROZEN',current_review_index='continuation-06/final-review-index.json',final_stop_proof='continuation-06/final-stop-proof-after-readonly.json',runtime_resume_requires_new_explicit_permit=True,remaining_roots=b['caps']['roots']-b['counts']['roots'])
b['continuation06']['verified_baseline_evidence']='continuation-06/baseline-identities.json (202 paths incl retained null identities); original adoption format found no file_checks array'
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'kind':'continuation06_complete_candidate_return','utc':now.isoformat(),'engineering_complete':True,'stable_for_independent_audit':True,'real_Q':'FROZEN','counts':b['counts'],'failures_entries':len(b['failures']),'wall_ceiling_with_final071_reserve':ceiling,'holding_union_seconds':b['runtime_holding_union_seconds'],'manual_total':'UNKNOWN_NOT_ZERO'})+'\n')
write(HERE/'budget-summary.json',{'counts':b['counts'],'caps':b['caps'],'failures_records':len(b['failures']),'original_TASK117_failures_separate':81,'old_command_wall_ceiling_retained':prior['command_wall_conservative_upper_seconds'],'current_ceiling_with_final071_60second_reserve':ceiling,'command_cap':57600,'holding_union_seconds':b['runtime_holding_union_seconds'],'holding_cap':21600,'new_holding_seconds':b['runtime_holding_union_seconds']-prior['runtime_holding_union_seconds'],'new_logical_source_create_attempts':b['continuation06_database_create_attempts'],'old_matrix_database_create_attempts_retained':b['matrix_database_create_attempts'],'manual_total':'UNKNOWN_NOT_ZERO','unique_ledger':'../budget.json','final071_receipt_is_external_to_archive':True})
counts='、'.join(k+'='+str(v) for k,v in b['counts'].items())
cases='\n'.join('- '+x['id']+'：'+x['status']+'。'+x['facts'] for x in matrix)
prefix=f'''# TASK-120 / R-114 — 续作06结果：工程候选完成，可交集中独审

保存：{now.astimezone(timezone(timedelta(hours=8))).isoformat()}。本轮为继续完整收尾05的原 A 独占工程窗口，Codex desktop，具体模型变体未暴露；原 A+ 保持停止，无委派、无并行独审。

A—D在已批准AP-120-06边界内完成，已有两个缺口闭合，并处理了实际发现的普通缺陷。建议工程候选可交原118独立归属集中终审。工程完整=true、稳定可交独审=true，不等于主控验收、发布或独审通过；Q保持冻结，不签STEP018整体、019/020、M1或项目，也不承诺未知缺陷为零。

## A：015单表权限、R03严格版本及旧兼容

新增015_activity_scope_delete_permission.sql，SHA256={read(HERE/'final-rules-migrations-bundle-check.json')['015_sha256']}。事务锁住data_control和scope绑定表，核旧R02/静默状态、既有NOLOGIN组、运行guard及原权限，再只向retrolume_data_app授public.activity_scope_sources DELETE，并写入精确data_exit.v1.r03标识。001—014原字节、R01/R02冻结常量、业务列、金融、公开HTTP和备份格式/编码不改；旧四库没有迁移或扩权。

这是表级DELETE，可信应用若绕仓储裸SQL可删除本库其他活动绑定；并非数据库行级CAS。原来源锁→活动锁→CAS/资格及data_runtime_write guard保留。snapshot/readonly/restore-loader没有获得正常DELETE、TRUNCATE或管理权。没有新建登录角色、重置旧密码或更改成员关系；本轮复用已核既有应用/快照角色，只在新库增加表ACL。

先行工程风险检查在真实015执行前保存，062通过，后续清单/readonly seal兼容修正各有064/065复检与原件。R03与R02表列/codec形状相同，单独精确迁移链/权限和metadata约束；未知profile、错误迁移hash、缺失DELETE、额外TRUNCATE/readonly DELETE和不符版本约束准确关闭。权限反例用实际隔离PG事务并回滚，没有把异常权限提交为新能力。frozen/restored_readonly DELETE均真实42501/data_runtime_readonly；工厂既有seal的snapshot SELECT只在restored_readonly版本形态接受。

旧R01真实ZIP读取测试、旧R02 ZIP读取及错误profile/迁移hash拒绝已核；原067整体FAIL保留，其先完成的R01子例直接复用，068修正上下文管理器进入后补完反例。根47用应用角色只读核旧四库实际R02 normal/frozen兼容及金融完全不变。新R03初始化、实际backup→restore→verify→seal→activate_readonly全部生产路径通过。没有冒称新做了R01数据库恢复。

## B：实际移除、准确拒绝与收缩K2

保留05差集DELETE/upsert；新库正常HTTP实际将A3的N/R范围收缩为N，只删除目标绑定，scope_revision恰增1，其他活动绑定/费用不变；用户显式变更head与模型旧结果推进分开核证。stale CAS→interview_head_conflict、无效来源→source_invalid、未知活动→not_found，均按精确码核无部分写入/金融变化。

发现失效source_revision在共享scope方法抛ActivityLedgerConflict，面试入口未映射而返回500。仅在bind_scope现有校验处先核锁定来源current_version/revision，以既有InterviewRefusal(source_invalid)准确返回409，原写事务/锁/错误码合同不放宽。根43原500留档，根44定向验证通过；已过scope正例与旧11项权限矩阵没有重跑。

新K2只做真实scope收缩：不同actor在shared dispatch释放、结果exclusive重新获取前提交移除。worker/actor、释放窗口、PG COMMIT及before/after金融立即保存；不可变007 received/原件摘要及单笔250000预扣保留、one dispatch、GET零新动作，迟到模型不推进变更后的head。原head/revoke/source/scope新增及memory限定证据直接继承，没有重发旧claim/UNKNOWN或清退费用。

## C：完整DataContext与namespace真实迟到闭合

根46先在新源normal时通过生产UI形成两个待批准续问，本机批准后，两个独立实际GET200均完整取到原headers/body且can_continue=true，再只暂停浏览器交付；每个路由、业务键、六字段身份及SHA256立即checkpoint。之后正常备份/冻结/恢复，未在冻结后重取正常Q响应，没有改响应字节、签名、权限或客户端setter。

- 完整DataContext：control/dataset/instance/generation与namespace不变，生产维护和capabilities使mode=normal→frozen、read_only=false→true。确认UI观察后释放响应1，真实native fetch完成，dataFetch完整上下文守卫在业务JSON消费前拒绝；当前内容/输入/台账不变，零自动POST。
- namespace：正常文件上传、restore-plan、verified工厂目标及activate_readonly/selector提交。一次真实已认证capabilities请求跨越选择提交，由生产caps构造新状态；原header/新body按实保存，既有bootstrap接纳新身份，没有注入token/body或伪造选择器。UI实际dataset/instance/generation/storage namespace改变后释放响应2，native fetch完成而业务不消费旧JSON，当前内容/输入/台账不变，零自动POST。随后正常bootstrap及新namespace存储读取均有原件。

本轮frontend只将dataFetch普通响应的守卫从namespace扩展为完整DataContext；hubRead/hubCancel/bootstrap既有例外保持。正式build063通过，实际JS/CSS响应与dist绑定，之后没有前端产品修改或重复build。两例均非静态取消标签，也没有声称旧正文被业务handler消费。

最终截图另发现恢复目标普通活动列表不可用。根49定位为只读查询前无条件构造normal QAuthority，正常只读记录接口其实可返回3项。仅在服务器已绑定的data_readonly仓储且方法属于既有纯读分类时跳过该构造；仍走原PG readonly连接守卫。写入/claim/外发分支、金融SQL及Q根门不变。根50实际普通列表/专用记录均3项，normal Q初始化和cancel_activity写入仍精确拒绝；根51真实只读UI复验3项/3项、零自动POST。只读副本不因此恢复普通执行资格，最小fixture未配置的Memory能力不签正常放行。

## D：对象、金融、投入、停止与身份

原源CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f及原卷精确复用，只新建一次retrolume_task120_scope_ui_final。新源dataset=6eac474d-3a6d-4668-89a0-eb4061cd5604，instance=187ec042-8b08-4944-88cb-682f0625b287；固定3活动、冻结8份输入和100/25合成上限不改，grant/活动截止不晚于本轮业务门，最后源永久frozen，未复制旧批准或解冻旧matrix。

唯一生产工厂目标CID=4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332，name=retrolume-task120-scopeui-ro1，卷同名-data，数据库retrolume_task120_scopeui_ro，固化55481（先实际核55481/55482）。dataset=83877e63-ca07-40b1-a58d-841a791c75d9，instance=70bb08f5-785d-4844-be62-d0c2e5afbb02，generation=1。正常工厂标签/job/target/profile及随机身份照实登记，不冒充源；create/start先计数，CID返回即登记。两容器均同原完整镜像、1CPU/512MiB/pids128/restart=no、named volume、loopback，无host bind。额外只读诊断仅串行启动既有目标，源保持停止。

金融为实际PG，不以Q日志当余额。旧四库经根47新只读连接逐字段完全不变，之后源没有再启动：flow25/6250000、budget01 100/25000000、budget02 8/2000000、matrix-final23/5750000。新scope-ui-final共5/1250000：A1=1/250000、A2=0/0、A3=4/1000000，全部R=0。恢复副本同样5/1250000，是备份时点历史，根51实际只读记录GET又核一致；不与源相加，不构成新额度。真实provider/实际费用/preview/Git均0。

旧三个UNKNOWN事件子序列及完整journal提交链再次核证未变；原A1即使无Q claim仍是业务UNKNOWN，永久不重发。新收缩K2的claim/UNKNOWN/007/费用及3个批准未领取续问均保留，当前资格因source frozen/selector变化关闭；没有退款、释放旧slot或把目标当正常Q。

累计：{counts}。各cap、余量、尝试与原账见budget-summary.json；只把实际容器/卷对象cap1→2，创建尝试cap仍2且已用2，新逻辑源创建1/1，旧matrix创建1/1保留。原111条失败记录/旧TASK117的81历史均留存；本轮累计失败记录{len(b['failures'])}条，不等于独立缺陷数。根41清单角色名、根42嵌套错误码采集、根43实际来源500、根45transport结算、067未进入PackageReader上下文、根48观察helper误用关闭API以及根49实际只读列表缺陷均保留；修后成功独立checkpoint，不改旧FAIL。

command wall保守上界（包含最后071保存60秒预留）{ceiling:.6f}/57600秒，持有并集{b['runtime_holding_union_seconds']:.6f}/21600秒，本轮新增{b['runtime_holding_union_seconds']-prior['runtime_holding_union_seconds']:.6f}秒；旧43917.209199及全部未知预留保持。新连续处理区间仅作未测read/edit时间的保守边界，扣除另计实测根/命令，不将审批排队称为实测工作/CPU；人工总量UNKNOWN_NOT_ZERO，没有机械另加7200或把未知记0。071退出后唯一账补实际命令wall，本段不是新的精确CPU声明。

实际接收观测为2026-10-20T13:36:43Z，登记早于产品修改/新运行；首次只读读卡工具先于持久登记的顺序及3秒时钟边界如实记录，不冒称主控签发就是接收。finish=2026-10-21T01:36:43Z，末1800保存，business=01:06:43Z；原首点/96h截止不变，不随继续消息重开。初次Docker引擎管道不存在时没有启动资源，用户恢复后061重新实核，再运行；没有自行重启Docker或绕过审批。

070于{stop['utc']}精核{len(stop['registered_processes'])}组PID/birth、{len(stop['registered_jobs'])}个命名Job，源及实际目标均Running=false/Pid0，55480/55481/18120无监听；070自身exit0/tree_empty。之后仅071有限文件保存有独立退出回执。所有库、目标、容器、卷、数据及旧证据保留，无drop/truncate/prune/批删。

本轮8项产品/迁移文件差异在source.diff；fixture.diff、最终文件身份/生成dist、原as-run与复用映射一并保存。根46与最终产品只差后续sealed-reader纯读投影修补，已按直接影响用根50/51验证；正常源分支仍走原路径，C被延迟的正常响应及前端守卫字节未改变，不假称整轮都跑过最终字节。根51 product as-run与最终逐项一致。七规则、001—014、旧R01/R02常量和七个旧包复读一致；新包不递归套旧ZIP，不含.runtime、凭据、DSN、私钥或可用Q票据。最后071回执与唯一budget/events为包外权威附件，索引明确引用。

## C01—C15和集中审阅

{cases}

唯一审阅入口：D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/continuation-06/final-review-index.json。候选ZIP及SHA256/文件数在candidate-package-identity.json；已知本卡必需工程缺口为空，限制逐项在remaining-gaps.json。原memory缺即时before-financial快照的限定不增强、不隐藏；R01仅文件codec识别与冻结合同，不冒称重做PG恢复。

建议主控同步唯一执行动态与架构：015/R03严格兼容、两个真实迟到UI已闭合、scope来源错误投影及sealed-reader只读投影修正、精确资源/金融与停止状态；本窗口未修改DocuS/公共库或占用新TASK/CHG。由主控在稳定包上安排原118隔离集中终审，再作正式验收；用户无需再提供密钥、SQL或内存操作。工程已完整即停止，未复跑五入口/完整ACK权限K2/99→100基线。

以下原{len(old)}字节结果SHA256={hashlib.sha256(old).hexdigest()}完整保留为原字节后缀；旧“当前”仅属于历史时点。

---

'''
report.write_bytes(prefix.encode('utf-8')+old);assert report.read_bytes().endswith(old)
write(HERE/'result-preservation.json',{'old_report_bytes':len(old),'old_report_sha256':hashlib.sha256(old).hexdigest(),'old_suffix_unchanged':True,'new_report_sha256':sha(report)})
index={'task':'TASK-120','R':'R-114','scope':'续作06','permit_id':b['current_permit_id'],'engineering_complete':True,'stable_for_independent_audit':True,'independent_audit_started':False,'real_Q':'FROZEN','report':rel(report),'groups':{'A':['permission-risk-check.json','real-profile-ACL-and-guard-PASS.json','old-new-package-compatibility.json','old-R02-and-final-readonly-reconciliation-PASS.json'],'B':['actual-scope-shrink-PASS.json','scope-targeted-negatives-PASS.json','K2-scope-shrink-PASS.json'],'C':['UI-order-preflight.md','UI-normal-GET-1-root-46.json','UI-normal-GET-2-root-46.json','UI-complete-DataContext-PASS-root-46.json','UI-namespace-PASS-root-46.json','normal-restore-verified-checkpoint.json','normal-selector-activation-COMMIT.json'],'D':['final-file-identities.json','financial-summary.json','budget-summary.json','readonly-listing-PASS.json','readonly-listing-UI-PASS.json','final-stop-proof-after-readonly.json']},'matrix':'acceptance-matrix.json','limits_and_gaps':'remaining-gaps.json','source_diff':'source.diff','fixture_diff':'fixture.diff','old_inherited_matrix':'../finalization-05/acceptance-matrix.json','as_run':'final-file-identities.json','unique_current_ledger':['../budget.json','../events.jsonl'],'final_stop_receipt':'command-070.receipt.json','final_filesystem_receipt':'command-071.receipt.json','final071_and_current_ledger_are_external_to_archive':True,'package':'final-review-candidate.zip','package_identity':'candidate-package-identity.json','history_preserved':'old-packages-preserved.json','no_private_or_usable_Q_material':True,'no_further_runtime_justified_by_unused_caps':True}
for paths in index['groups'].values():
 for p in paths:assert (HERE/p).is_file(),p
write(HERE/'final-review-index.json',index)
pack={report};pack.update(ROOT/x['path'] for x in changes if (ROOT/x['path']).is_file())
for p in (ROOT/'frontend/dist').rglob('*'):
 if p.is_file():pack.add(p)
for p in HERE.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.zip','.pyc') and p.name not in ('command-071.log','candidate-package-identity.json','save-consistency.json'):pack.add(p)
for n in range(41,52):pack.update(p for p in EX.glob(f'root-{n:02d}*') if p.is_file() and p.suffix in ('.json','.jsonl','.log'))
target=HERE/'final-review-candidate.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for p in sorted(pack):
  assert time.monotonic()-started<50;name=rel(p);assert not name.startswith(('.runtime/','.git/')) and p.suffix!='.zip';z.write(p,name)
with zipfile.ZipFile(target) as z:assert z.testzip() is None
write(HERE/'candidate-package-identity.json',{'path':rel(target),'bytes':target.stat().st_size,'sha256':sha(target),'files':len(pack),'engineering_complete':True,'stable_for_independent_audit':True,'nested_old_ZIPs':0,'private_runtime_credentials_or_usable_Q_material':False,'final071_receipt_and_current_ledger':'external referenced authority'})
write(HERE/'save-consistency.json',{'utc':datetime.now(timezone.utc).isoformat(),'old_report_suffix_exact':True,'old_roots_failures_events_prefixes_exact':True,'seven_old_packages_unchanged':True,'all_required_checkpoint_paths_exist':True,'archive_CRC_ok':True,'report_sha256':sha(report),'engineering_complete':True,'stable_for_independent_audit':True,'filesystem_save_seconds':time.monotonic()-started})
print(json.dumps({'saved':str(report),'engineering_complete':True,'stable_for_independent_audit':True,'counts':b['counts'],'failures_records':len(b['failures']),'candidate_bytes':target.stat().st_size}))
