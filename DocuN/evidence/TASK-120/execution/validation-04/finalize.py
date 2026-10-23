"""Bounded filesystem-only final save; never starts or mutates runtime."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import copy,difflib,hashlib,json,time,zipfile,struct
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4];started=time.monotonic()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
assert not (HERE/'final-review-index.json').exists(),'inspect saved result; do not overwrite'
b=read(EX/'budget.json');prior=read(HERE/'prior/budget.json');now=datetime.now(timezone.utc)
assert b['active_root'] is None and b['active_command'] is None and not b['needs_reconcile']
assert b['counts']['roots']==b['caps']['roots']==24 and b['counts']['api_starts']==b['caps']['api_starts']==24
assert b['roots'][:len(prior['roots'])]==prior['roots'] and b['failures'][:len(prior['failures'])]==prior['failures']
assert (EX/'events.jsonl').read_bytes().startswith((HERE/'prior/events.jsonl').read_bytes())
assert all(b['counts'][k]==0 for k in ('provider_calls','actual_fee_microunits','preview_creates','preview_starts','Git_writes'))
stop=read(HERE/'final-stop-proof.json');own=read(HERE/'command-055.receipt.json')
assert stop['all_fresh_stop_dimensions_confirmed'] and own['tree_empty'] and own['exit_code']==0
assert read(HERE/'preflight-result.json')['successful'] and read(HERE/'offline-final-checks.json')['success']
old=(HERE/'prior/TASK-120-result.md').read_bytes();report=ROOT/'DocuN/results/TASK-120-result.md'
assert sha(report)==hashlib.sha256(old).hexdigest()==read(HERE/'adoption.json')['prior_result_sha256']
verification=read(ROOT/'DocuN/evidence/TASK-120/orchestration-validation04-20261019/input-verification.json')
baseline={x['path']:x['sha256'] for x in verification['file_checks']}
for f in (ROOT/'backend/tests/fixtures/task120').glob('*.py'):baseline.setdefault(rel(f),None)
identities=[];changes=[];new=[];source=[];fixtures=[]
for name,expected in sorted(baseline.items()):
    p=ROOT/name;observed=sha(p) if p.is_file() else None;identities.append({'path':name,'sha256':observed})
    if observed==expected:continue
    assert observed is not None and (name=='backend/app/activities/teaching_repository.py' or name.startswith(('backend/tests/fixtures/task120/','frontend/tests/task120-'))),name
    before=HERE/'preimage'/name
    if expected is not None:assert before.is_file() and sha(before)==expected,name
    row={'path':name,'before_sha256':expected,'after_sha256':observed};(new if expected is None else changes).append(row)
    left=before.read_text(encoding='utf-8-sig').splitlines(True) if before.exists() else []
    delta=difflib.unified_diff(left,p.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+name if before.exists() else '/dev/null',tofile='after/'+name)
    (source if name.startswith('backend/app/') else fixtures).extend(delta)
(HERE/'source.diff').write_text(''.join(source),encoding='utf-8');(HERE/'fixture.diff').write_text(''.join(fixtures),encoding='utf-8')
assert {x['path'] for x in new}=={'backend/tests/fixtures/task120/validation04.py','backend/tests/fixtures/task120/validation_memory.py'}
asrun=read(EX/'root-24-batch-01-as-run.json')['files'];product_checked=[]
for item in asrun:
    if item['path'].startswith(('backend/app/','frontend/src/','frontend/dist/')):
        assert sha(ROOT/item['path'])==item['sha256'],item['path'];product_checked.append(item)
write(HERE/'final-file-identities.json',{'baseline':'validation04 input-verification exact file_checks; 23 existing fixtures preserved as existing','all_current_paths':identities,'changed':changes,'new':new,'product_changed_files':1,'final_product_matches_root24_as_run':True,'product_as_run_files_checked':len(product_checked),'root24_batch01_as_run_sha256':sha(EX/'root-24-batch-01-as-run.json'),'final_fixture_deltas_after_root24':['control_tail_unconfirmed is an expected tail denial; save individual gate checkpoints','explicit readonly RetrievalPanel list refresh before original-key reconciliation','SQLSTATE-only transaction exception-chain observer; no error messages'],'these_final_fixture_deltas_not_PG_UI_rerun':True})
rules=[]
for row in read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    assert sha(row['absolute_path'])==row['sha256'];rules.append({'path':row['absolute_path'],'sha256':row['sha256'],'match':True})
write(HERE/'final-rules-check.json',{'all_seven_match':True,'rules':rules})
for asset in read(EX/'final-bundle-identities.json')['assets']:assert sha(ROOT/asset['path'])==asset['sha256']
old_packages=[]
for name in ['final-review-files.zip','continuation-01/final-review-candidate.zip','continuation-02/final-review-candidate.zip','repair-03/final-review-candidate.zip','repair-03/final-review-candidate-before-identity-reconciliation.zip']:
    p=EX/name
    if name.startswith('repair-03/'):
        record=next(x for x in verification['inputs'] if x['path']==rel(p)) if any(x['path']==rel(p) for x in verification['inputs']) else None
        expected=record['sha256'] if record else ('b91e94ea0b6c853600fa3f2e89a84961f2ed30c945a3747e97ab5e84bcfd3916' if name.endswith('/final-review-candidate.zip') else '2ae451189d0169835fde441d1a21514479d5cf27d89622057d85aa0c515d6d8b')
    else:expected=read(EX/(name.replace('final-review-files.zip','final-review-files-identity.json').replace('final-review-candidate.zip','candidate-package-identity.json')))['sha256']
    assert sha(p)==expected,name;old_packages.append({'path':rel(p),'bytes':p.stat().st_size,'sha256':expected})

# Compare the exact committed old-key event subsequences, not just booleans.
old_unknown=read(EX/'continuation-02/retained-unknown-witness.json')['requests'];wanted={x['prepared_id']:x for x in old_unknown};events_by={k:[] for k in wanted}
canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
path=ROOT/'.runtime/TASK-120/flow/control/journal.bin';previous='0'*64;seq=0
with path.open('rb') as stream:
    while header:=stream.read(4):
        assert len(header)==4;size=struct.unpack('!I',header)[0];assert 1<=size<=65536
        raw=stream.read(size);tail=stream.read(73);assert tail==b'\nCOMMIT:'+hashlib.sha256(raw).hexdigest().encode()+b'\n'
        e=json.loads(raw);seq+=1;assert e['seq']==seq and e['prev_hash']==previous and e['body_hash']==hashlib.sha256(canonical(e['payload']).encode()).hexdigest();previous=hashlib.sha256(raw).hexdigest()
        pid=e['payload'].get('prepared_id')
        if pid in events_by:events_by[pid].append({'kind':e['kind'],'seq':seq})
for pid,items in events_by.items():assert items==wanted[pid]['events'],pid
write(HERE/'retained-original-Q-witness.json',{'committed_frame_chain_verified':True,'exact_old_three_event_sequences_unchanged':True,'old_keys':[{'business_key':x['prepared']['business_key'] if 'prepared' in x else x.get('business_key'),'prepared_id':pid,'events':len(events_by[pid]),'new_send':0} for pid,x in wanted.items()],'note':'Original A1 is business UNKNOWN even though Q claim is absent; never resend it. Q journal is not financial authority.'})

ui23=read(EX/'root-23-batch-01-ui-all-proof.json');ui24=read(EX/'root-24-batch-01-ui-remaining-proof.json');normal=ui23['cases']+ui24['cases']
assert len(normal)==4 and all(x['status']=='PASS' for x in normal)
copy_proof=read(HERE/'copied-control-reconciliation.json');assert len(copy_proof['copies'])==2
finance=read(HERE/'financial-final-new-connection-root-24.json');base=read(HERE/'financial-baseline.json')
assert all(x['running_reserved_seconds']==0 for slot in ('flow','budget-02') for x in finance[slot]['activities'])
write(HERE/'financial-summary.json',{'authority':'actual original PG fresh connections, not Q journal','baseline':base,'final':finance,'flow_delta':{'requests':finance['flow']['requests']-base['flow']['requests'],'cost':finance['flow']['cost']-base['flow']['cost']},'budget02_delta':{'requests':finance['budget-02']['requests']-base['budget-02']['requests'],'cost':finance['budget-02']['cost']-base['budget-02']['cost']},'C12_budget01':'inherited only; not rerun','all_final_R_zero':True})
missing=[
 'ACK/K2 real COMMIT-loss matrix not reached: root24 negative-copy callback stopped at expected control_tail_unconfirmed before arming its result-ACK fault. Final collector correction is offline only.',
 'Whole-request negative gates reached the copied-tail guard, but individual gate receipts were not saved before failure. Two saved-copy denials are independently verified; do not sign the full live-PG permissions matrix.',
 'New-v2 head/scope/namespace/DataContext late fences remain incomplete. Head-case query9d478f34-cfef-4753-8b73-fb8a4d5f7631 is approved/unclaimed; a missing same-document panel refresh stopped before its explicit continuation. Final refresh fix is not Browser rerun.',
 'budget02 scope mutation returned503/database_unavailable at the real released dispatch gap. Its COMMIT status/head/scope were not read after that error; do not assume rollback or resend. Scope model45b8d0b4-dd77-44d7-8cdd-370ef475c7b3 was claimed and its operation is received in final PG; preserve its result and charge.',
 'Source/memory mutation races and readonly/deleted-body branches were not reached. No source freeze/unfreeze, new target, source delete or memory revoke is claimed. Final typed SQLSTATE diagnostic is offline tested, not a diagnosis of the original503.',
 'Runtime roots24/24 and APIstarts24/24 are exhausted. Original grant/activity expiry2026-10-19T12:19:22.457756Z is unchanged. No root25, old-root reopen or expiry refresh is authorized.'
]
write(HERE/'remaining-gaps.json',{'engineering_complete':False,'stable_for_independent_audit':False,'gaps':missing,'no_new_user_decision_requested':True})
updates={
 'C01':('PARTIAL_ACK_NOT_REACHED','Old K1 checks retained; new real ACK matrix was not armed.'),
 'C02':('PARTIAL_FULL_REQUEST_GATES_WITNESSES_INCOMPLETE','Actual snapshot/full-request checks reached the copy-tail guard; no blanket matrix pass. Exact selected memory and normal chains retained.'),
 'C03':('PASS_FOR_INHERITED_WIRE_SCOPE','Original compatibility checks reused; no wire-contract delta.'),
 'C04':('PARTIAL_TWO_SAVED_COPY_DENIALS_PASS','Actual saved copy q_instance_identity and damaged-tail control_tail_unconfirmed verified in054; readonly/deleted-body branches not reached.'),
 'C05':('PASS_FROZEN_ZERO_REAL_OUTBOUND','Q remains frozen; provider/fee/preview/Git all0. No enabling authority created.'),
 'C06':('PASS_ORIGINAL_RESOURCES_REUSED','Same CID/volume/three DBs/fixed activities; no create, DDL or grant extension.'),
 'C07':('PASS_LISTED_WAIT_APPROVE_CURRENTNESS','Original UNKNOWN keys never resent. New normal UI waits, readonly refresh, local approval and explicit same-key continue observed.'),
 'C08':('PASS_LISTED_REAL_RETRIEVAL_SCOPE','Old successes inherited; UI query chains and actual received/cache-qualified requests kept.'),
 'C09':('PASS_ORIGINAL_EXERCISE_AND_NORMAL_UI','Original accepted/unclaimed exercise cd632dfd-8a25-465b-895e-375b0ce1d48e committed in21; final no-memory display projection and normal teaching UI passed in24.'),
 'C10':('PASS_LISTED_FIVE_ENTRY_NORMAL_UI','Interview, retrieval, legacy and HTML normal UI passed23; teaching normal UI passed24; received original model/domain/007 proofs inherited.'),
 'C11':('PARTIAL_SCOPE_MUTATION_503_OTHER_RACES_NOT_RUN','Real release gap reached; scope mutation503 has unconfirmed COMMIT status. Model charge/result preserved; source/memory/ACK/K2 not passed.'),
 'C12':('PASS_INHERITED_REAL_COMMON_100_GATE','Original99→100, dual provider denial and original-db reopen100/25000000 reused; no 99-call rerun.'),
 'C13':('PARTIAL_NORMAL_UI_PASS_LATE_MATRIX_OPEN','Final bundle hashes/one page confirmed. Owner/view late guards passed listed normal modes; head/scope/namespace/DataContext incomplete.'),
 'C14':('PASS_FRESH_EXACT_STOP','055 confirms193 PID/birth,89 Jobs, exact CID Running=false/Pid0, both ports free; own055 tree_empty/exit0.'),
 'C15':('PASS_SAVED_PARTIAL_REVIEW_PACKAGE','Final differences, identities, as-run, financial snapshot, failures, old report and all old ZIPs retained; no stable/independent acceptance.')}
case=read(EX/'case-index.json');case.setdefault('history',[]).append({'at_return':'repair-03','cases':copy.deepcopy(case['cases'])})
for row in case['cases']:
    status,facts=updates[row['id']];row.update(status=status,validation04_facts=facts,validation04_evidence='validation-04/final-review-index.json')
b['failures'].append({'case':'validation04-filesystem-authoring-and-read-diagnostics','classification':'metadata_only_not_independent_product_defects','items':['Two intermediate JS syntax checks failed during fixture editing; corrected before053 and root24, no service action from these checks','One default-encoding read failed and was repeated with explicit UTF-8','Targeted guessed read paths and literal Windows glob searches were absent/invalid; rg directory searches used instead']})
measured=(b['controlled_command_wall_seconds']-prior['controlled_command_wall_seconds'])+(b['runtime_command_wall_seconds']-prior['runtime_command_wall_seconds'])
entry=datetime.fromisoformat(b['validation04_timing']['entry_utc']);envelope=(now-entry).total_seconds()+60
b['validation04_unwrapped_command_wall_upper_seconds']=max(0,envelope-measured)
b['validation04_timing'].update(end_with_save_reserve=(now+timedelta(seconds=60)).isoformat(),active_interval_upper_seconds=envelope,separately_measured_new_command_and_runtime_seconds=measured,unwrapped_upper_seconds=b['validation04_unwrapped_command_wall_upper_seconds'],manual_total='UNKNOWN_NOT_ZERO; included in active interval upper bound, not CPU')
keys=('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds','continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds','validation04_unwrapped_command_wall_upper_seconds')
b['command_wall_conservative_upper_seconds']=sum(b.get(k,0) for k in keys)
assert b['command_wall_conservative_upper_seconds']<=28800 and b['runtime_holding_union_seconds']<=14400
b.update(engineering_status='VALIDATION_04_PARTIAL_STOPPED_ROOT_AND_API_CAP_24',real_Q='FROZEN',remaining_roots=0,final_stop_proof='validation-04/final-stop-proof.json',current_review_index='validation-04/final-review-index.json',runtime_resume_requires_new_explicit_permit=True)
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'kind':'validation04_final_return','utc':now.isoformat(),'real_Q':'FROZEN','roots':24,'APIstarts':24,'command_wall_upper_seconds':b['command_wall_conservative_upper_seconds'],'holding_union_seconds':b['runtime_holding_union_seconds'],'manual_total':'UNKNOWN_NOT_ZERO'})+'\n')
case.update(status=b['engineering_status'],stable_audit_package_ready=False,real_Q='FROZEN',validation04_counts=b['counts'],validation04_failures_entries=len(b['failures']));write(EX/'case-index.json',case)
ready=read(EX/'remaining-readiness.json');ready.update(status=b['engineering_status'],engineering_stable=False,activated=False,real_Q='FROZEN',engineering_required=missing,current_block='Authorized runtime roots and API starts exhausted; no user memory/key/SQL action requested.',resource_block={'roots_used':24,'roots_cap':24,'current_counts':b['counts'],'new_runtime_permit_required':True},final_stop_proof=rel(HERE/'final-stop-proof.json'),independent_audit_started=False,user_keys_or_memory_release_requested=False,validation04_completed=['Original accepted/unclaimed exercise domain/007 plus exact before/after PG financials','Listed normal five-entry UI and actual final JS/CSS hashes, one context/page','Precise no-memory teaching-v3 display projection proved on real PG and normal UI','Final fresh-PG financial snapshots, retained Q unknown sequences and exact stopped ownership']);write(EX/'remaining-readiness.json',ready)
write(HERE/'acceptance-matrix.json',{'C01_C15':[{ 'id':cid,'status':status,'facts':facts} for cid,(status,facts) in updates.items()],'normal_UI_actual_cases':normal,'late_owner_view':'PASS for listed actual new-v2 teaching/interview and legacy activity/view tests','late_head_scope_namespace_DataContext':'NOT_COMPLETE','copy_cases':copy_proof,'scope_mutation_status':'503; COMMIT/head status not independently reconciled','original_FAILs_preserved':True})
counts='\n'.join(f"| {k} | {b['counts'][k]} | {b['caps'][k]} |" for k in b['counts'])
cases='\n'.join(f'| {cid} | {status} | {facts} |' for cid,(status,facts) in updates.items())
prefix=f'''# TASK-120 / R-114 — 续验04结果（有限正常链通过；仍未完整，Q冻结）

保存：{now.astimezone(timezone(timedelta(hours=8))).isoformat()}。原 A+ 工程窗口、单一执行者，无委派、无独审。原许可未延期，flow/budget02 截止仍为今天20:19:22+08。

**已完成原教学练习、五入口有限正常UI、最终真实PG金融快照及精确清场；本卡仍未达到稳定完整候选。** 四个新增根21—24已经用尽，API启动24/24；没有重开旧根、追加运行根、创建新库或刷新权利。ACK/K2、剩余权限与失效竞态、晚到围栏缺项如实保留，不能签Q启用或集中终审通过。

## 本轮有效成果

- 原练习 `cd632dfd-8a25-465b-895e-375b0ce1d48e`：先核原accepted/unclaimed、原请求与上下文摘要、父/范围，再对完整冻结请求执行无发送资格校验；随后prepare、本机批准、原键显式继续。根21领域committed、007 committed_current，原件SHA256 `f1a72a2c87622f82c14f41bd4f8af4305a892f04416cbde5255e5fd8f1644b1b`，真实SUP结果及树零可追。单次实际合成预扣+1/+250000；没有重做原plan或更换练习键。
- 已成两条面试、legacy、HTML和原教学计划按实际键/operation/query摘要/原件/真实PG/SUP读取映射；旧成功随新目标转历史时，正常资格读取会抑制正文，额外真实只读PG核原007摘要，明确区分历史成功与当前可用，不因旧汇总文件名缺失重发。
- 正式bundle五入口正常链：根23面试与检索、legacy续问、HTML description通过等待/GET/重开不自动POST、本机批准、同键显式继续；根24教学与检索正常链通过，列明owner/view迟到检查。实际响应JS/CSS摘要与正式dist一致，HTML preview始终0。没有重复已成原业务键；新UI动作仅对应合法的新等待意图。
- 教学UI发现无记忆teaching.v3被旧保守版本回退误标为“已选记忆”而禁用按钮。仅修改允许范围 `backend/app/activities/teaching_repository.py` 的读取显示投影：只有显式null-memory冻结上下文判为未选；有实际binding、v2或未知/不完整上下文继续保守。没有修改memory仓储、资格/正文守卫、DDL、schema/profile、SUP/Job/时钟或前端产品。根24真实PG证明flow教学未选、资格有效，同时budget02仍真实已选；正常教学UI随后提交通过。
- 一个Browser/context/page串行，根24通过路由在真实已批准POST发出前计native尝试；未发POST的围栏准备不新增native，旧保守计数不改。约1秒可用内存与自有Job进程工作集样本已保存；仅前向512MiB启动门，连续两次低于256MiB清场规则保留。根21曾有一次低样本，未出现连续两低；四根均自动清场。
- 两个已保存私有控制副本在054离线只读复核：复制身份拒绝q_instance_identity；尾增一字节拒绝control_tail_unconfirmed。原root24 FAIL不改绿，原控制日志不损坏。末次两项诊断脱敏测试及3项新门检查通过，旧050的11项检查复用；这些离线检查不冒充PG/UI补验。

## 真实失败、已保存修补与断点

根22在教学查询按钮等待时超时；Node未处理等待promise导致第一版UI细节未保存，正常控制器已清场。修正观察与逐模式失败保存后，根23确认教学按钮因上述显示误分类而禁用，其余正常模式通过。根24显示修补及教学UI通过。

根24权限回调已走到第二个损坏副本，但夹具只接受control_tail/control_corrupt，误拒了正确的control_tail_unconfirmed；**尚未设置结果ACK故障，更未执行三种ACK/K2**。此前各门断言虽经控制流走到此处，未逐项保存回执，不据此签完整权限矩阵。最终夹具补精确码与逐门checkpoint，只有保存副本拒绝已被054实际复核。

根24头围栏在同文档prepare后未刷新RetrievalPanel已保存列表，找不到“按原键只读核对”；最终补显式只读刷新，尚未Browser复跑。该检索键 `9d478f34-cfef-4753-8b73-fb8a4d5f7631` 已批准但未claim。模型键 `fa4d574c-e47b-4db6-832b-56ae55289582` 在权限回调中也已prepare/批准、未claim；当前资格可能因后续新goal失效，不能盲重交。head/scope/namespace/DataContext围栏及readonly分支均未完成。

budget02先只读复核原已选记忆面试仍committed_current，再进入真实scope释放锁窗口；变更POST返回503/database_unavailable，**变更的COMMIT/head/scope状态没有后续PG快照核证，不宣称回滚，也不得盲重试**。模型键 `45b8d0b4-dd77-44d7-8cdd-370ef475c7b3` 已claim，其007操作在最终PG为received，费用及SUP树零保留。source/memory/deleted-body分支未到达。最终增加只记录异常类型/SQLSTATE的事务诊断，脱敏测试通过；没有据此猜测503根因或声称已修复。

旧三个UNKNOWN键的提交事件链与原续作02逐项一致，未重发、不退款、不清slot。其中旧A1虽Q claim为空，业务仍UNKNOWN，继续永久禁止重发。全部旧报告/FAIL/as-run和五份旧ZIP原字节保留。

## 金融权威与停止

金融权威为原PG的新连接；Q日志只说明协议状态。基线→最终：flow **17/4250000→25/6250000**；budget02 **5/1250000→8/2000000**（次数/合成费用微单位）。最终各活动R均0；flow S依原固定活动顺序为9/33/55秒，budget02为0/28/10秒。每根后新连接原件及原练习前后数在financial-*.json；budget01的真实100门和重开证据直接继承，没有再积累99笔。合成预扣不是真实账单，真实provider/实际费用仍0。

055在 {stop['utc']} 实核 **{len(stop['registered_processes'])}组PID/birth、{len(stop['registered_jobs'])}个Job** 停止，原CID Running=false/Pid0，55480/18120无监听；另有055自身tree_empty/exit0。保留原容器、卷、三库和数据，没有drop/truncate/prune/批删；readonly冻结/删除分支并未到达，不伪称执行。

| 累计项 | 已用 | cap |
|---|---:|---:|
{counts}

累计 **{len(b['failures'])}条失败/诊断记录**（旧77原样保留；不是独立缺陷数），原TASK117的81历史另保留。command wall保守上界 **{b['command_wall_conservative_upper_seconds']:.6f}/28800秒**，持有并集 **{b['runtime_holding_union_seconds']:.6f}/14400秒**；两旧7200未知预留未清零。本轮以11:01:53Z至保存+60秒活跃区间上界扣除另计实测命令/根wall，不重叠计时；人工总量UNKNOWN_NOT_ZERO，不冒充CPU。

## C01—C15与剩余门

| 项 | 实际状态 | 限定事实 |
|---|---|---|
{cases}

{chr(10).join(str(i+1)+'. '+item for i,item in enumerate(missing))}

## 交付与复读

索引：`D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/validation-04/final-review-index.json`。
候选包：同目录 `final-review-candidate.zip`；hash、字节数及文件数在candidate-package-identity.json。源/夹具diff、最终身份、真实as-run、五入口原件映射、金融快照、所有FAIL和StopProof集中可查。最终产品与根24实测字节相同；尾码/面板刷新/事务诊断属于之后的夹具增量，仅离线检查，不回填成运行成功。

原结果{len(old)}字节/SHA256 {hashlib.sha256(old).hexdigest()}完整保留为下方后缀。七规则、四dist及五旧ZIP复读一致。包不包含.runtime、凭据或可用Q批准材料。未启动独审，未签STEP018整体/019/020/M1/项目；Q继续冻结。

---

'''
report.write_bytes(prefix.encode('utf-8')+old);assert report.read_bytes().endswith(old)
write(HERE/'result-preservation.json',{'old_report_bytes':len(old),'old_report_sha256':hashlib.sha256(old).hexdigest(),'unchanged_original_suffix':True,'new_report_sha256':sha(report)})
index={'task':'TASK-120','R':'R-114','scope':'续验04','permit_id':b['current_permit_id'],'engineering_complete':False,'stable_for_independent_audit':False,'real_Q':'FROZEN','report':str(report),'new_roots':[21,22,23,24],'remaining_roots':0,'runtime_requires_new_explicit_permit':True,'normal_five_entry_UI':{'teaching':'../root-24-batch-01-ui-remaining-proof.json','interview_retrieval_legacy_HTML':'../root-23-batch-01-ui-all-proof.json','scope':'only listed normal chains and owner/view; remaining late matrix is open'},'original_exercise':'original-exercise-positive.json','positive_mapping':'positive-operation-map-root-24.json','memory_display':'memory-display-PG.json','copy_reconciliation':'copied-control-reconciliation.json','financials':'financial-summary.json','matrix':'acceptance-matrix.json','gaps':'remaining-gaps.json','budget':'../budget.json','events':'../events.jsonl','case_index':'../case-index.json','stop':['final-stop-proof.json','command-055.receipt.json'],'source_diff':'source.diff','fixture_diff':'fixture.diff','identities':'final-file-identities.json','old_packages_unchanged':old_packages,'package':'final-review-candidate.zip','no_private_configuration_or_usable_Q_material':True}
write(HERE/'final-review-index.json',index)
pack={report,EX/'budget.json',EX/'events.jsonl',EX/'case-index.json',EX/'remaining-readiness.json',EX/'final-bundle-identities.json'}
pack.update(ROOT/x['path'] for x in changes+new)
pack.update(ROOT/x['path'] for x in old_packages)
for folder in (HERE,EX/'repair-03'):
    for p in folder.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.zip','.pyc') and p.name not in ('candidate-package-identity.json','save-consistency.json'):pack.add(p)
for number in (21,22,23,24):pack.update(p for p in EX.glob(f'root-{number:02d}*') if p.is_file())
target=HERE/'final-review-candidate.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
    for p in sorted(pack):
        assert time.monotonic()-started<55;name=rel(p);assert not name.startswith(('.runtime/','.git/'));archive.write(p,name)
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None
identity={'path':rel(target),'bytes':target.stat().st_size,'sha256':sha(target),'files':len(pack),'engineering_complete':False,'real_Q':'FROZEN','includes_private_configuration':False,'includes_usable_Q_material':False}
write(HERE/'candidate-package-identity.json',identity)
assert time.monotonic()-started<60
write(HERE/'save-consistency.json',{'utc':datetime.now(timezone.utc).isoformat(),'old_report_suffix_preserved':True,'old_failure_root_event_prefixes_preserved':True,'old_five_ZIPs_unchanged':True,'seven_rules_unchanged':True,'four_dist_files_unchanged':True,'archive_CRC_ok':True,'final_report_sha256':sha(report),'roots_used':24,'failures_entries':len(b['failures']),'command_wall_upper_seconds':b['command_wall_conservative_upper_seconds'],'runtime_holding_union_seconds':b['runtime_holding_union_seconds'],'filesystem_finalize_seconds':time.monotonic()-started})
print(json.dumps({'report':str(report),'archive':identity,'engineering_complete':False,'failures':len(b['failures']),'wall_upper':b['command_wall_conservative_upper_seconds'],'holding_union':b['runtime_holding_union_seconds']}))
