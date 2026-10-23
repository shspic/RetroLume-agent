"""Bounded filesystem-only delivery. Never starts any service or changes Q."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import copy,difflib,hashlib,json,time,zipfile
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4];started=time.monotonic()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def relative(p):return p.relative_to(ROOT).as_posix()
assert not (HERE/'final-review-index.json').exists(),'inspect any partial save before resuming'
b=read(EX/'budget.json');prior=read(HERE/'prior/budget.json');now=datetime.now(timezone.utc)
assert b['active_root'] is None and b['active_command'] is None and not b['needs_reconcile']
assert b['counts']['roots']==b['caps']['roots']==20
assert b['roots'][:len(prior['roots'])]==prior['roots'] and b['failures'][:len(prior['failures'])]==prior['failures']
assert (EX/'events.jsonl').read_bytes().startswith((HERE/'prior/events.jsonl').read_bytes())
assert all(b['counts'][k]==0 for k in ('provider_calls','actual_fee_microunits','preview_creates','preview_starts','Git_writes'))
stop=read(HERE/'final-stop-proof.json');own=read(HERE/'command-050.receipt.json')
assert stop['all_fresh_stop_dimensions_confirmed'] and own['tree_empty'] and own['exit_code']==0
assert read(HERE/'repair-tests-050.json')['successful']
old=(HERE/'prior/TASK-120-result.md').read_bytes();report=ROOT/'DocuN/results/TASK-120-result.md'
assert sha(report)==hashlib.sha256(old).hexdigest()==read(HERE/'adoption.json')['prior_result_sha256']
old_packages=[(EX/'final-review-files.zip',read(EX/'final-review-files-identity.json')['sha256']),
    (EX/'continuation-01/final-review-candidate.zip',read(EX/'continuation-01/candidate-package-identity.json')['sha256']),
    (EX/'continuation-02/final-review-candidate.zip',read(EX/'continuation-02/candidate-package-identity.json')['sha256'])]
for p,expected in old_packages:assert sha(p)==expected
rules=[]
for row in read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    observed=sha(row['absolute_path']);assert observed==row['sha256'];rules.append({'path':row['absolute_path'],'sha256':observed,'matches':True})
for asset in read(EX/'final-bundle-identities.json')['assets']:assert sha(ROOT/asset['path'])==asset['sha256']
verification=read(ROOT/'DocuN/evidence/TASK-120/orchestration-repair03-20261019/input-verification.json')
baseline={row['path']:row['sha256'] for row in verification['file_checks']}
for path in (ROOT/'backend/tests/fixtures/task120').glob('*.py'):baseline.setdefault(relative(path),None)
baseline.setdefault('backend/tests/test_task120_repair03.py',None)
product_allowed={'backend/app/data_exit/q_store.py','backend/app/capabilities/q_context.py','backend/app/capabilities/q_gateway.py','backend/app/interview/policy.py','backend/app/activities/interview_repository.py'}
identities=[];changes=[];new=[];source_diff=[];fixture_diff=[]
for rel,expected in sorted(baseline.items()):
    path=ROOT/rel;observed=sha(path) if path.is_file() else None
    identities.append({'path':rel,'sha256':observed})
    if observed==expected:continue
    assert observed is not None,rel
    assert rel in product_allowed or rel.startswith(('backend/tests/fixtures/task120/','backend/tests/test_task120','frontend/tests/task120-')),rel
    before=HERE/'preimage'/rel
    if expected is not None:assert before.exists() and sha(before)==expected,rel
    row={'path':rel,'before_sha256':expected,'after_sha256':observed};(new if expected is None else changes).append(row)
    left=before.read_text(encoding='utf-8-sig').splitlines(True) if before.exists() else []
    delta=difflib.unified_diff(left,path.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+rel if before.exists() else '/dev/null',tofile='after/'+rel)
    (source_diff if rel in product_allowed else fixture_diff).extend(delta)
(HERE/'source.diff').write_text(''.join(source_diff),encoding='utf-8')
(HERE/'fixture.diff').write_text(''.join(fixture_diff),encoding='utf-8')
write(HERE/'final-file-identities.json',{'baseline':'orchestration repair03 input-verification file_checks','all_current_paths':identities,'changed':changes,'new':new,
    'product_changed_files':sum(x['path'] in product_allowed for x in changes),'dist_four_files_unchanged':True,
    'final_product_delta_after_root20':'PathNode rationale scoped schema-field rule; final 11 offline checks pass, no final PG rerun',
    'post_root20_fixture_delta':'retrieval proof uses real business key/result sha, no nonexistent operation_id; safe nested HTTP codes; unrun UI fences retained as candidate'})
write(HERE/'final-rules-check.json',{'all_seven_match':True,'rules':rules})

# Preserve the earlier interrupted read-only lookup segment without charging
# its multi-hour interruption. Both envelopes are upper bounds, not CPU claims.
permit=read(ROOT/'DocuN/evidence/TASK-120/orchestration-repair03-20261019/permit.json')
early_start=datetime.fromisoformat(permit['issued_at']);early_end=datetime.fromisoformat('2026-10-19T06:52:56+00:00')
early_upper=max(0,(early_end-early_start).total_seconds())
active_anchor=datetime.fromisoformat('2026-10-19T09:55:30+00:00')
active_upper=(now-active_anchor).total_seconds()+60
measured_new=(b['controlled_command_wall_seconds']-prior['controlled_command_wall_seconds'])+(b['runtime_command_wall_seconds']-prior['runtime_command_wall_seconds'])
b['repair03_unwrapped_command_wall_upper_seconds']=max(300,early_upper+active_upper-measured_new)
b['repair03_metadata_time_note']='Actual interval envelopes, including unmeasured manual/read/edit time conservatively, less separately measured command/runtime receipts; not CPU. Earlier 06:52:56 to 09:55:30 interruption excluded. Final save has a 60s bounded reserve. Both old7200 reservations remain.'
b['repair03_time_intervals']=[{'start':early_start.isoformat(),'end':early_end.isoformat(),'upper_seconds':early_upper,'source':'permit issue to retained previous-window last clock sample; conservative readonly pre-adoption envelope'},
    {'start':active_anchor.isoformat(),'end_with_save_reserve':(now+timedelta(seconds=60)).isoformat(),'upper_seconds':active_upper,'source':'first present-turn clock09:56:01 minus31s tool margin to final save+60s; no intervening user pause'}]
b['repair03_manual_total']='UNKNOWN_NOT_ZERO; covered by interval upper envelopes, not fabricated measured CPU'
entry={'case':'repair03-readonly-metadata-lookup-diagnostics','classification':'metadata_only_not_independent_product_defects',
    'items':['Missing guessed backend/tests/test_task120_q_protocol.py; actual test paths found by rg','Missing guessed backend/app/interview/repository.py and activities/teaching_service.py; actual modules used','Literal backend/app/worker/*.py rg argument invalid on Windows; no runtime action','Final preflight/test authoring corrections preserved in candidate source and command042 FAIL log; no resource reset']}
b['failures'].append(entry)
b.update(engineering_status='REPAIR_03_PARTIAL_STOPPED_ROOT_CAP_20',real_Q='FROZEN',remaining_roots=0,
    final_stop_proof='repair-03/final-stop-proof.json',current_review_index='repair-03/final-review-index.json',runtime_resume_requires_new_explicit_permit=True,
    database02_status='Original third database/root/roster complete; creation-time selected memory, index/query/model/007 passed in root20; no recreation or grant extension')
keys=('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds','continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds')
b['command_wall_conservative_upper_seconds']=sum(b.get(k,0) for k in keys)
assert b['command_wall_conservative_upper_seconds']<=b['command_wall_cap_seconds']
assert b['runtime_holding_union_seconds']<=b['runtime_holding_union_cap_seconds']
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'kind':'repair03_final_return','utc':now.isoformat(),'mono_ns':time.monotonic_ns(),'roots_used':20,'roots_cap':20,'real_Q':'FROZEN','manual_total':'UNKNOWN_NOT_ZERO','command_wall_upper_seconds':b['command_wall_conservative_upper_seconds']})+'\n')

updates={
 'C01':('PARTIAL_ISOLATED_RETAINED_ACK_NOT_RUN','Original K1 checks retained; real ACK matrix not reached.'),
 'C02':('PARTIAL_REAL_MODELS_AND_MEMORY_FULL_REQUEST','Two real interview model/007 chains and exact selected memory in frozen full request verified; full PG negative matrix not run.'),
 'C03':('PASS_FOR_LISTED_INHERITED_WIRE_CHECKS','No wire contract change; original compatibility checks retained. No blanket new boundary pass.'),
 'C04':('PARTIAL_NEW_PERMISSION_COPY_READONLY_NOT_RUN','Original isolated gates retained; new live-PG copy/missing/tail/readonly suite not reached.'),
 'C05':('PASS_INHERITED_INERT_CONFIGURATION','Real Q remains frozen. Normal enabling conditions remain unknown; no user key/config change.'),
 'C06':('PASS_ORIGINAL_THREE_DATABASES_AND_CREATION_MEMORY','Original CID/volume/DBs retained; partial third DB resumed without recreate, original roster and creation-time memory selection completed.'),
 'C07':('PASS_LISTED_WAIT_APPROVE_UNKNOWN_LOCAL_END','Original exact unknown Q event sequences unchanged; A2 historical obsolete UNKNOWN locally abandoned, A3 abandoned_at set while UNKNOWN retained. No old-key resend.'),
 'C08':('PASS_FOR_LISTED_REAL_QUERY_AND_CACHE_CHAINS','Prior embeddings inherited; new original-instance queries received; cache_ready source indexes accepted only with full current cache proof.'),
 'C09':('PARTIAL_PLAN_COMMIT_EXERCISE_FINAL_FIX_OFFLINE_ONLY','Real teaching plan/007 passed; exercise accepted but prepare rejected rationale field. Scoped PathNode-field fix passes final offline tests, not PG rerun.'),
 'C10':('PASS_FOR_LISTED_INTERVIEW_LEGACY_HTML_MEMORY_MODELS','Original flow Interview and selected-memory Interview model/domain/007 passed; legacy followup and HTML description succeeded/current. Reconciled without new send after fixture KeyError.'),
 'C11':('NOT_RUN_REMAINING_ACK_K2_PERMISSION_MUTATION_RACES','Root20 finite dependency gates skipped fault/race suites. Existing unrelated evidence is not promoted.'),
 'C12':('PASS_INHERITED_ACTUAL_COMMON_PG_100_AND_REOPEN','Original99→100, dual-provider denial and stop/reopen100/25000000 inherited unchanged; no rerun/refund.'),
 'C13':('NOT_COMPLETE_FINAL_UI_BLOCKED_AT_MEMORY_GATE','Historical three FAIL browsers and valid asset hashes retained. Repair03 starts0 browser; final gate575877120<805306368. Five-entry success and head/scope/namespace/DataContext matrix not completed.'),
 'C14':('PASS_FRESH_EXACT_STOP_AND_OWN_COMMAND_EXIT','Final050:160 PID/birth,76 Jobs, original CID stopped/Pid0, both ports released; own050 Job tree_empty/exit0.'),
 'C15':('PASS_SAVED_REVIEWABLE_INCREMENT_NOT_ACCEPTANCE','Five product files, fixture deltas, preimages, as-run identities and old report/ZIPs retained; package is an incomplete engineering candidate, not independent audit acceptance.')}
case=read(HERE/'prior/case-index.json');case.setdefault('history',[]).append({'at_return':'continuation-02','cases':copy.deepcopy(case['cases'])})
for row in case['cases']:
    status,facts=updates[row['id']];row.update(status=status,repair03_facts=facts,repair03_evidence='repair-03/final-review-index.json')
case.update(status=b['engineering_status'],stable_audit_package_ready=False,real_Q='FROZEN',repair03_counts=b['counts'],repair03_failures_entries=len(b['failures']))
write(EX/'case-index.json',case)
missing=[
 'Final teaching exercise original accepted/unclaimed key needs normal PG/SUP verification of the scoped rationale-field fix; plan COMMIT is already valid and must not be rerun.',
 'Full actual PG whole-request permission/foreign-copy/missing-artifact/journal-tail/readonly and three ACK/K2/source-memory-scope race matrix remains unrun.',
 'Final five-entry real UI success and head/scope/namespace/DataContext late fences remain unverified; final Browser gate failed before any new browser start.',
 'Runtime root budget20/20 is exhausted. No root21/new resource or old-root reuse is authorized. Flow/budget02 original grant expiry2026-10-19T12:19:22.457756Z remains unchanged.',
 'Final business financial balance snapshot was not recollected after stop; Q journal is not used as a financial authority. Original C12 and actual per-operation COMMIT facts retain their exact scope.'
]
ready=read(HERE/'prior/remaining-readiness.json')
ready.update(engineering_stable=False,activated=False,real_Q='FROZEN',engineering_required=missing,
    current_block='Runtime roots20/20 exhausted; browser was independently blocked at its768MiB gate. No request to free user memory.',
    resource_block={'roots_used':20,'roots_cap':20,'current_counts':b['counts'],'new_runtime_permit_required':True},
    final_stop_proof='DocuN/evidence/TASK-120/execution/repair-03/final-stop-proof.json',user_keys_or_memory_release_requested=False,independent_audit_started=False,
    completed_increment=['Precise shared-policy teaching/interview/HTML read classifications and real pre-SQL write rejection','Historical obsolete Interview UNKNOWN local abandonment with claim/operation history retained','Real teaching plan007, normal Interview007, selected-memory Interview007, legacy followup and HTML description','Final11 offline checks, exact resource cleanup and retained original Q event sequences'])
write(EX/'remaining-readiness.json',ready)
write(HERE/'remaining-gaps.json',{'engineering_complete':False,'stable_for_independent_audit':False,'gaps':missing,'no_new_user_decision_requested':True})
counts='\n'.join(f"| {k} | {b['counts'][k]} | {b['caps'][k]} |" for k in b['counts'])
cases='\n'.join(f"| {cid} | {status} | {facts} |" for cid,(status,facts) in updates.items())
prefix=f'''# TASK-120 / R-114 — 集中修复03增量结果（未完整，Q继续冻结）

保存：{now.astimezone(timezone(timedelta(hours=8))).isoformat()}。接收/执行：原 A+ 工程窗口，单一执行者；未委派、未独审、未签项目或真实Q。

**本卡未达到稳定完整候选。** 已完成五个产品文件的精确修补、真实教学计划、面试、已选记忆、legacy续问与HTML description增量；原容器和全部自有执行均已停止，数据保留。累计根 **20/20**，不启动21、不重开旧根。教学练习最后字段修补仅离线通过，剩余权限/ACK/K2/竞态及最终UI未完成。后续应继承下列有效成果，只补缺口。

## 已确认成果与实际边界

- P1：`_teaching_read_snapshot`、`validate_interview_request`、`verify_html_request` 三个实际只读闭包精确归类；没有泛化私有方法，没有放开共享→排他升级。根17对原教学请求在正常PG读路径上复核：原分类触发 `q_policy_upgrade_forbidden`，修后返回None；原请求、财务及控制日志不变。最终真实写闭包仍在连接/SQL前拒绝。v2/v3无记忆/有记忆控制流有离线覆盖，替身不计PG。
- P2：原A2 `430a4e36-08e1-411f-a73e-097506a6278b` 经既有本地abandon结束，精确处理“obsolete UNKNOWN且head无其他pending”的原合同路径；原A3 `3b561488-07b7-4d6d-8b98-05e793c96749` 的本地abandon已落地，其原UNKNOWN状态按生产规则保留，以abandoned_at清pending。原A1 `1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e` 不变。三原键Q事件序列与续作02**逐项完全相同**；未重发、未释放semantic slot、未退款。
- P3：原日志明确HTML拒绝为 `q_unapproved_text` / `config_sha256`；legacy为 `q_unapproved_field` / history。现仅接纳原PG已接受命令的配置摘要、已核证当前同活动父007的完整规范history。原first父实际为answer、一段，schema/parent资格正常。根19新legacy续问和HTML description均真实提交，后者succeeded/current；preview创建/启动均0。九函数EOL修补直接继承，没有重做DDL或改001—014/profile。
- 根20真实教学plan与007已提交；练习在领取前prepare拒绝 `task/path_nodes/0/rationale`（字段JSON摘要43d257f56c2080147d25eecf7b7fb6091dd21336fa1fa446cfc0486f2e2181f4）。最终采用PathNode封闭schema字段，**仅限task.path_nodes整数项位置**；文字值仍须原父来源核证。该最终修补仅离线验证，不能算练习已通过。
- 根20原flow面试与budget02已选记忆面试均真实SUP提交、领域committed、007 committed_current。其后汇总夹具错误读取retrieval回执不存在的operation_id而FAIL；049只读复核已保存PG读证明、真实SUP回执、私有artifact多重hash及记忆绑定，单独归档成功事实，**原FAIL不改绿、不新发送**。flow007 `int18m.7305d1f04472479ba4bb268a6ff92b64`；记忆007 `int18m.e3ef75346c894927939956e3572d6ff1`。记忆全文与冻结输入、选中ID、selection/dependency摘要一致。
- 第三库沿原已迁移/绑定状态完成MemoryService保存和创建时选择，未重建、未重绑已有活动、未扩展期限。source_index终态实际允许cache_ready；仅在当前ready且缓存片段数完整时继承；query仍只接受received。最终夹具改用真实query业务键/result摘要。
- 最终050 **11项定向检查全通过**，Python/Node夹具语法通过。前端产品与四份dist字节未变，原typecheck/build和根16加载hash子事实直接继承；本轮没有重复build，也没有新浏览器成功。

## 运行、失败与清场

根17是唯一只读诊断根（实际约20秒）；根18、19、20为有限自动串行计划，均已finally清场。根18保留教学abandon断言错误和记忆model拒绝；根19保留cache_ready夹具错误；根20保留练习字段拒绝、两处汇总KeyError及UI门阻挡。原57条失败完整保留，当前 **{len(b['failures'])}条失败/诊断记录**，不是独立缺陷数；原TASK117的81历史不清零、不混算。

050在 {stop['utc']} 实核 **{len(stop['registered_processes'])}组PID/birth、{len(stop['registered_jobs'])}个Job** 全停，原CID Running=false/Pid0，PG55480与API18120均无监听；另有050自身tree_empty/exit0。保留唯一容器、卷和三个原库，无drop/truncate/prune/批删。根20Browser门实测575877120 bytes <805306368；动作未执行，累计Browser仍3。没有要求用户再释放内存。

| 累计项 | 已用 | cap |
|---|---:|---:|
{counts}

命令wall保守上界 **{b['command_wall_conservative_upper_seconds']:.6f}/{b['command_wall_cap_seconds']}秒**；运行持有并集 **{b['runtime_holding_union_seconds']:.6f}/{b['runtime_holding_union_cap_seconds']}秒**。两旧7200未知预留保留；新增按两个明确活跃区间上界、扣除另计真实命令/根wall计算，3小时中断空档未计CPU；人工总量UNKNOWN_NOT_ZERO，详见唯一budget.json。原首点/96h截止不延长，flow/budget02的12:19:22.457756Z期限不刷新。

## C01—C15实际口径

| 项 | 状态 | 限定事实 |
|---|---|---|
{cases}

## 仍须完成

{chr(10).join(str(i+1)+'. '+text for i,text in enumerate(missing))}

原C12共同99→100、双provider达限和原库重开100/25000000，旧R300核销、旧embedding、first、EOL及S有限验收完整继承，不重跑。真实Q启用事实继续UNKNOWN；真实provider、实际费用、preview、Git新增全部0。

## 结果包与复读

工程索引：`D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/repair-03/final-review-index.json`。
包：同目录 `final-review-candidate.zip`，身份在 `candidate-package-identity.json`。
关键证据：`readonly-diagnosis.json`、`retained-original-Q-witness.json`、`flow-interview-reconciled-positive.json`、`budget-02-interview-reconciled-positive.json`、`legacy-html-positive.json`、`repair-tests-050.json`、`final-stop-proof.json`、`command-050.receipt.json`、`source.diff`、`fixture.diff`、`final-file-identities.json`、原17—20 as-run/FAIL/StopProof。

原结果全文{len(old)}字节/SHA256 {hashlib.sha256(old).hexdigest()}作为下方原字节后缀保留；三旧ZIP、七规则、四dist指纹均复读一致。新增包不含.runtime、凭据或可用Q批准材料。此包可复核工程增量，**不标稳定完整、不替代集中独审**。

---

'''
report.write_bytes(prefix.encode('utf-8')+old);assert report.read_bytes().endswith(old)
write(HERE/'result-preservation.json',{'old_report_bytes':len(old),'old_report_sha256':hashlib.sha256(old).hexdigest(),'unchanged_original_suffix':True,'new_report_sha256':sha(report)})
index={'task':'TASK-120','R':'R-114','scope':'集中修复03','permit_id':b['current_permit_id'],'engineering_complete':False,'stable_for_independent_audit':False,'real_Q':'FROZEN',
    'report':str(report),'actual_new_roots':[17,18,19,20],'remaining_roots':0,'runtime_requires_new_explicit_permit':True,
    'case_index':'../case-index.json','remaining':'remaining-gaps.json','readiness':'../remaining-readiness.json','budget':'../budget.json',
    'diagnostic':'readonly-diagnosis.json','business_successes':['teaching-plan-reconciled-positive.json','flow-interview-reconciled-positive.json','budget-02-interview-reconciled-positive.json','legacy-html-positive.json'],
    'original_FAILs_retained':['../root-18-batch-01-failure.json','../root-18-batch-02-failure.json','root19-core-result.json','../root-20-batch-01-failure.json','../root-20-batch-02-failure.json','flow-tail-result.json'],
    'actual_UI_started_this_repair':0,'final_offline_tests':'repair-tests-050.json','stop':['final-stop-proof.json','command-050.receipt.json'],
    'final_source_not_same_as_root20_as_run':'final scoped rationale-field repair is offline tested only; fixture aggregate fields repaired after root20',
    'source_diff':'source.diff','fixture_diff':'fixture.diff','identities':'final-file-identities.json','rules':'final-rules-check.json',
    'old_packages_unchanged':[{'path':relative(p),'sha256':h} for p,h in old_packages],'package':'final-review-candidate.zip','no_private_configuration_or_usable_Q_material':True}
write(HERE/'final-review-index.json',index)
pack={report,EX/'budget.json',EX/'events.jsonl',EX/'case-index.json',EX/'remaining-readiness.json',EX/'final-bundle-identities.json'}
for p,h in old_packages:pack.add(p)
for row in changes+new:pack.add(ROOT/row['path'])
for p in HERE.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.zip','.pyc') and p.name not in ('candidate-package-identity.json','save-consistency.json'):pack.add(p)
for number in (17,18,19,20):pack.update(p for p in EX.glob(f'root-{number:02d}*') if p.is_file())
for name in ('budget-02-creation-memory-proof.json','budget-02-selected-memory-binding.json','budget-02-bootstrap.json','budget-02-source-identities.json','budget-02-q-binding.json'):
    if (EX/name).exists():pack.add(EX/name)
target=HERE/'final-review-candidate.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for p in sorted(pack):
        if time.monotonic()-started>55:raise RuntimeError('filesystem_finalize_55s_limit')
        rel=relative(p);assert not rel.startswith(('.runtime/','.git/'));z.write(p,rel)
with zipfile.ZipFile(target) as z:assert z.testzip() is None
identity={'path':relative(target),'bytes':target.stat().st_size,'sha256':sha(target),'files':len(pack),'engineering_complete':False,'real_Q':'FROZEN','includes_private_configuration':False,'includes_usable_Q_material':False}
write(HERE/'candidate-package-identity.json',identity)
assert time.monotonic()-started<60
write(HERE/'save-consistency.json',{'utc':datetime.now(timezone.utc).isoformat(),'old_report_suffix_preserved':True,'old_failure_root_event_prefixes_preserved':True,'old_three_ZIPs_unchanged':True,'seven_rules_unchanged':True,'four_dist_files_unchanged':True,'archive_CRC_ok':True,'final_report_sha256':sha(report),'roots_used':20,'failures_entries':len(b['failures']),'command_wall_upper_seconds':b['command_wall_conservative_upper_seconds'],'runtime_holding_union_seconds':b['runtime_holding_union_seconds'],'filesystem_finalize_seconds':time.monotonic()-started})
print(json.dumps({'report':str(report),'archive':identity,'engineering_complete':False,'roots':20,'failures':len(b['failures']),'wall_upper':b['command_wall_conservative_upper_seconds'],'holding_union':b['runtime_holding_union_seconds']}))
