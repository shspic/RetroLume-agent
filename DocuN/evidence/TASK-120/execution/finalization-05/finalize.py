"""Filesystem-only return. No runtime, SQL, provider, Git or shared-state write."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import ast, difflib, hashlib, json, os, struct, time, zipfile

HERE=Path(__file__).resolve().parent
EX=HERE.parent
ROOT=HERE.parents[4]
started=time.monotonic()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).relative_to(ROOT).as_posix()
def write(p,v):
    p=Path(p); tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(tmp,p)
def refs(*names): return [rel(HERE/n) for n in names]

assert not (HERE/'final-review-index.json').exists(), 'Already saved: inspect rather than rerun'
b=read(EX/'budget.json')
prior=read(EX.parent/'orchestration-final05-20261019/returned-snapshot/budget.json.bytes')
assert b['active_root'] is None and b['active_command']['manifest']=='command-059.json'
assert b['counts']['roots']==40 and len(b['failures'])==109
assert b['roots'][:24]==prior['roots'] and b['failures'][:88]==prior['failures']
old_events=(EX.parent/'orchestration-final05-20261019/returned-snapshot/events.jsonl.bytes').read_bytes()
assert (EX/'events.jsonl').read_bytes().startswith(old_events)
assert all(b['counts'][k]==0 for k in ('provider_calls','actual_fee_microunits','preview_creates','preview_starts','Git_writes'))
stop=read(HERE/'final-stop-proof.json'); own=read(HERE/'command-058.receipt.json')
assert stop['all_fresh_stop_dimensions_confirmed'] and own['exit_code']==0 and own['tree_empty']
assert read(HERE/'final-persistent-reconciliation-PASS.json')['status']=='PASS'
report=ROOT/'DocuN/results/TASK-120-result.md'; old=report.read_bytes()
assert len(old)==65338 and hashlib.sha256(old).hexdigest()=='85ed46c94bd38c8382a66112f9462e0e00e186715d364ec6790c24bc40d6430a'

# Exact round baseline and preimages; preserve inherited product evidence.
verification=read(EX.parent/'orchestration-final05-20261019/input-verification.json')
baseline={x['path']:x['sha256'] for x in verification['file_checks']}
for p in (ROOT/'backend/tests/fixtures/task120').glob('*.py'): baseline.setdefault(rel(p),None)
for n in ('frontend/tests/task120-final05-ui.mjs','frontend/tests/task120-final05-readonly.mjs'): baseline.setdefault(n,None)
identities=[]; changes=[]; source=[]; fixtures=[]
for name, expected in sorted(baseline.items()):
    p=ROOT/name; observed=sha(p) if p.is_file() else None
    identities.append({'path':name,'sha256':observed})
    if expected==observed: continue
    assert observed is not None, name
    assert name=='backend/app/activities/repository.py' or name.startswith(('backend/tests/fixtures/task120/','frontend/tests/task120-')),name
    before=HERE/'preimage'/name
    if expected is not None: assert before.is_file() and sha(before)==expected,name
    left=before.read_text(encoding='utf-8-sig').splitlines(True) if before.is_file() else []
    delta=list(difflib.unified_diff(left,p.read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+name if before.exists() else '/dev/null',tofile='after/'+name))
    (source if name.startswith('backend/app/') else fixtures).extend(delta)
    changes.append({'path':name,'before_sha256':expected,'after_sha256':observed})
assert [x['path'] for x in changes if x['path'].startswith('backend/app/')]==['backend/app/activities/repository.py']
(HERE/'source.diff').write_text(''.join(source),encoding='utf-8')
(HERE/'fixture.diff').write_text(''.join(fixtures),encoding='utf-8')
asrun=[]
for number in (34,40):
    p=EX/f'root-{number:02d}-batch-01-as-run.json'; j=read(p); checked=[]
    for x in j['files']:
        if x['path'].startswith(('backend/app/','frontend/src/','frontend/dist/')):
            assert sha(ROOT/x['path'])==x['sha256'],x['path']; checked.append(x['path'])
    asrun.append({'path':rel(p),'sha256':sha(p),'product_files_match':len(checked)})
write(HERE/'final-file-identities.json',{'round_baseline':'orchestration-final05-20261019/input-verification.json','all_current_paths':identities,'changed_or_new':changes,'product_changed_this_round':1,'as_run':asrun,'inherited_full_product_diffs':['../source.diff','../repair-03/source.diff','../validation-04/source.diff'],'fixture_warning':'Root33 head PASS and root34 scope PASS bind their own fixture hashes. Later collector corrections do not rewrite those as-run bytes.'})
rules=[]
for x in read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    assert sha(x['absolute_path'])==x['sha256']; rules.append({'path':x['absolute_path'],'sha256':x['sha256']})
for x in read(EX/'final-bundle-identities.json')['assets']: assert sha(ROOT/x['path'])==x['sha256']
write(HERE/'final-rules-and-bundle-check.json',{'all_seven_rules_unchanged':True,'rules':rules,'all_four_formal_dist_files_unchanged':True,'actual_JS_CSS_HTTP_binding':['UI-head-scope-root-33.json','UI-head-scope-root-34.json'],'no_new_build':True})
packages=read(EX/'validation-04/final-review-index.json')['old_packages_unchanged']
packages.append(read(EX/'validation-04/candidate-package-identity.json'))
for x in packages: assert sha(ROOT/x['path'])==x['sha256'],x['path']
write(HERE/'old-packages-preserved.json',{'six_old_packages':packages,'not_embedded_in_new_archive':True})

# Verify exact old UNKNOWN event subsequences and the committed journal chain.
wanted={x['prepared_id']:x for x in read(EX/'continuation-02/retained-unknown-witness.json')['requests']}
events_by={k:[] for k in wanted}; previous='0'*64; seq=0
canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
with (ROOT/'.runtime/TASK-120/flow/control/journal.bin').open('rb') as stream:
    while header:=stream.read(4):
        assert len(header)==4; size=struct.unpack('!I',header)[0]; assert 1<=size<=65536
        raw=stream.read(size); assert stream.read(73)==b'\nCOMMIT:'+hashlib.sha256(raw).hexdigest().encode()+b'\n'
        e=json.loads(raw); seq+=1
        assert e['seq']==seq and e['prev_hash']==previous and e['body_hash']==hashlib.sha256(canonical(e['payload']).encode()).hexdigest()
        previous=hashlib.sha256(raw).hexdigest(); pid=e['payload'].get('prepared_id')
        if pid in events_by: events_by[pid].append({'kind':e['kind'],'seq':seq})
for pid, events in events_by.items(): assert events==wanted[pid]['events'],pid
write(HERE/'retained-original-Q-witness.json',{'committed_frame_chain_verified':True,'original_three_exact_event_subsequences_unchanged':True,'requests':[{'business_key':x['business_key'],'prepared_id':pid,'events':events_by[pid]} for pid,x in wanted.items()],'no_resend':True,'no_refund_or_old_slot_release':True,'financial_authority':'Separate actual PG snapshots, not this journal'})

permission_files=sorted(HERE.glob('permission-*-PASS.json')); assert len(permission_files)==11
ui33=read(HERE/'UI-head-scope-root-33.json');ui34=read(HERE/'UI-head-scope-root-34.json')
head=next(x for x in ui33['cases'] if x['name']=='actual-head-late-approved-GET');scope=next(x for x in ui34['cases'] if x['name']=='actual-scope-late-approved-GET')
assert head['status']==scope['status']=='PASS'
memory=read(HERE/'K2-memory-persistent-reconciled.json'); assert memory['memory']['body_rows']==0
finance=read(HERE/'financial-final-separated.json'); assert finance['old_three_exactly_unchanged']
financial_summary={s:{'requests':v['requests'],'cost_reserved_microunits':v['cost'],'activities':v['activities'],'operations':len(v['operations'])} for s,v in finance['instances'].items()}
assert all(a['running_reserved_seconds']==0 for v in finance['instances'].values() for a in v['activities'])
write(HERE/'financial-summary.json',{'authority':'Fresh application-role PG connections in root38 after all mutations; root39/40 GET-only reconciliation preserves identical snapshots','raw':'financial-final-separated.json','instances':financial_summary,'do_not_sum_instances':True,'old_three_unchanged':True,'all_R_zero':True,'real_provider_calls':0,'actual_fee_microunits':0,'UNKNOWN_preserved':'Original three plus later claimed/unknown commands remain as recorded; no refunds or resend.'})

gaps=[{'id':'scope-removal','status':'BLOCKED_REQUIRES_ADOPTION','requirement':'Normal scope removal must work with the locked application profile','actual':'SQLSTATE42501; app role has no DELETE on activity_scope_sources; command absent, head/scope/fees unchanged','evidence':refs('scope-removal-blocker.json'),'boundary':'Current card forbids migrations001-014, schema/profile and permission changes.'}, {'id':'late-namespace-DataContext','status':'NOT_PASSED','requirement':'Actual delayed approved response across namespace and full DataContext switch must not affect current UI/eligibility/ledger','actual':'Head and scope have separate PASS. Root36 freeze COMMIT succeeded but cached Q snapshot failed at q_root_changed before client switch; UI remains FAIL. Matrix is permanently frozen and the one extra database allowance is consumed.','evidence':refs('UI-head-scope-root-33.json','UI-head-scope-root-34.json','UI-readonly-root-36.json','readonly-actual-PG-body-closed-reconciled.json'),'boundary':'No thaw, old grant renewal, replacement identity or fifth database is authorized.'}]
write(HERE/'remaining-gaps.json',{'engineering_complete':False,'stable_for_independent_audit':False,'gaps':gaps,'memory_evidence_limit':'Root35 did not immediately persist its pre-financial snapshot; original worker/actor/COMMIT/007 trace plus current PG reconciliation proves the listed invariants. Original FAIL and UNKNOWN remain.','not_a_runtime_cap_exhaustion':True,'no_user_key_SQL_or_memory_action_requested':True})
adoption='''# TASK-120 完整收尾05：最小采用包（未执行）

当前工程未达到完整稳定候选，Q 继续冻结。本文件供主控判断必要范围变更，不形成新授权或独审结论。

## 范围移除权限

实际角色 task120_flow_app 在 public.activity_scope_sources 上没有 DELETE。新增/版本更新已通过；真实移除返回 503，SQLSTATE42501，事务回滚，命令不存在且 head/scope/费用未变。精确原件是 scope-removal-blocker.json。源修补只避免无必要的全量删除，没有绕过权限门。

最小直接候选为在新的前向迁移中向 retrolume_data_app 授予这一张表的 DELETE；候选 SQL 为 GRANT DELETE ON public.activity_scope_sources TO retrolume_data_app。它会扩大该角色在此表的删除能力，不能按普通代码修正自动采用。另一候选为限定 activity、CAS、normal data mode 的可信范围替换函数，固定 search_path、撤销 PUBLIC EXECUTE、仅授应用角色 EXECUTE，配套 schema/profile 指纹与函数守卫审查。后者需要更多设计，但可缩小直接表权限。

主控应选择并明确采用权限/持久合同增量，再安排隔离安全审查；随后才可落新迁移、匹配 profile 和应用调用，并仅补真实移除、CAS/异活动/只读拒绝及受影响 K2。001—014 原字节不改。本包没有应用上述 SQL、创建函数或更改角色。

## namespace 与完整 DataContext 晚到

根33的 head 子例和根34的 scope 子例通过，正常五入口及 owner/view 证据直接继承。根36已将唯一新增矩阵库永久 frozen；界面切换前的缓存 Q 核证触发正确 q_root_changed，旧批准响应并未完整交付给新上下文，因此不得签 UI PASS。

续验需要明确授权一个可形成正常、当前、尚未 claim 的批准 GET 的独立有限测试目标及精确目标切换流程。原三库过期，不续 grant；matrix-final 不解冻、不重建、不重绑；不能复制批准或恢复旧响应冒充新的实测。现卡仅一个新逻辑库的额度已实际使用，不能自行新增第五库。采用时写清精确实例/根/期限/次数与清场上限，继续仅冻结合成输入、最低传输替身、单 Browser/context/page、真实 provider/费用/preview/Git 为零。

先形成合法正常响应并实际延迟，再通过生产 DataContext 机制切换 namespace/只读身份，记录真实路由、业务键、身份前后、当前内容/输入/可继续资格/新身份台账及零自动 POST；两个独立子例逐项 checkpoint。不得用标签切换、HTTP 只读拒绝或保存过的 JSON 替代此 UI 证明。

## 交回与终审

先完成上述采用及受影响工程验证，代码、证据稳定且无并行写后，再由主控按原118独立归属集中终审。本工程未启动或自签独审。建议主控在唯一执行动态账记录本轮局部完成、两个真实缺口和精确清场；本窗口未修改 DocuS、未新建 TASK、未分配 CHG。
'''
(HERE/'minimal-adoption-package.md').write_text(adoption,encoding='utf-8')

rows=[]
def row(i,status,facts,paths): rows.append({'id':i,'status':status,'facts':facts,'evidence':paths})
row('C01','PASS_LISTED_ACK_COMMIT_LOSS','Accepted, launch claim and result each committed before injected lost response; GET adds no action and claimed keys never resent.',refs('ACK-accepted-COMMIT-PASS.json','ACK-launch-claim-COMMIT-PASS.json','ACK-result-COMMIT-PASS.json'))
row('C02','PASS_LISTED_FULL_REQUEST_GATES','Eleven exact live-PG/full typed/provider request denials and idempotent approval; not a claim that all future unknown defects are absent.',[rel(p) for p in permission_files])
row('C03','PASS_INHERITED_WIRE_SCOPE','No public wire-contract delta this round. Original compatibility evidence retained.',['DocuN/evidence/TASK-120/execution/validation-04/acceptance-matrix.json','DocuN/evidence/TASK-120/execution/case-index.json'])
row('C04','PASS_LISTED_CLOSED_BODY_BOUNDARIES','Copied identity/tail inherited; missing original exact gate; revoked memory body0, deleted source tombstone/body closure and frozen-root rejection reconciled. This is not UI transition PASS.',refs('permission-missing-original-PASS.json','K2-memory-persistent-reconciled.json','deleted-source-body-reconciled.json','readonly-actual-PG-body-closed-reconciled.json')+['DocuN/evidence/TASK-120/execution/validation-04/copied-control-reconciliation.json'])
row('C05','PASS_FROZEN_ZERO_REAL_OUTBOUND','Q frozen; real provider, actual fees, preview and Git writes zero.',['DocuN/evidence/TASK-120/execution/budget.json'])
row('C06','PASS_EXACT_AUTHORIZED_RESOURCES','Same original CID/volume; one allowed matrix-final logical database, fixed activities and unmodified001-014/profile/old grants.',refs('matrix-bootstrap-PASS.json','final-stop-proof.json'))
row('C07','PASS_LISTED_NO_RESEND_AND_RECOVERY','Old unknown event sequences unchanged; exact old503 NOT_COMMITTED and old approved-unclaimed keys reconciled without sends.',refs('retained-original-Q-witness.json','old-scope-503-reconciliation.json','old-unclaimed-keys.json','ACK-matrix-PASS.json'))
row('C08','PASS_INHERITED_RETRIEVAL_SCOPE','Original real retrieval and listed normal query chains reused. No repeated99-call baseline.',['DocuN/evidence/TASK-120/execution/validation-04/positive-operation-map-root-24.json','DocuN/evidence/TASK-120/execution/root-23-batch-01-ui-all-proof.json'])
row('C09','PASS_INHERITED_ORIGINAL_EXERCISE','Original accepted/unclaimed exercise committed root21; final no-memory teaching display and selected-memory distinction passed root24.',['DocuN/evidence/TASK-120/execution/validation-04/original-exercise-positive.json','DocuN/evidence/TASK-120/execution/validation-04/memory-display-PG.json','DocuN/evidence/TASK-120/execution/root-24-batch-01-ui-remaining-proof.json'])
row('C10','PASS_INHERITED_LISTED_NORMAL_UI','Five normal entries and listed owner/view guards reuse actual root23/24 proofs; no new full-chain run.',['DocuN/evidence/TASK-120/execution/root-23-batch-01-ui-all-proof.json','DocuN/evidence/TASK-120/execution/root-24-batch-01-ui-remaining-proof.json'])
row('C11','PARTIAL_K2_PROVED_SCOPE_REMOVAL_OPEN','Head/revoke/scope/source release-window PASS; memory original trace and persistent reconciliation proves listed invariants with saved-before-financial limitation. Actual scope removal needs permission adoption.',refs('K2-head-PASS.json','K2-revoke-PASS.json','K2-scope-PASS.json','K2-source-PASS.json','K2-memory-persistent-reconciled.json','scope-removal-blocker.json'))
row('C12','PASS_INHERITED_REAL_COMMON100_GATE','Original99-to100, dual-provider limit rejection and original-db reopen100/25000000 retained; no rerun.',['DocuN/evidence/TASK-120/execution/validation-04/acceptance-matrix.json','DocuN/evidence/TASK-120/execution/case-index.json'])
row('C13','PARTIAL_HEAD_SCOPE_PASS_NAMESPACE_DATACONTEXT_OPEN','Root33 whole FAIL retains independently checkpointed head PASS; root34 scope PASS. Namespace and full DataContext remain unpassed; root36 actual freeze is separate from UI proof.',refs('UI-head-scope-root-33.json','UI-head-scope-root-34.json','UI-readonly-root-36.json','remaining-gaps.json'))
row('C14','PASS_FRESH_EXACT_STOP','058 confirms511 PID/birth identities,113 Jobs, exact CID stopped/Pid0 and both ports free; own058 exit0/tree_empty. Final059 is filesystem-only and has a separate exit receipt.',refs('final-stop-proof.json','command-058.receipt.json'))
row('C15','PASS_TRUTHFUL_PARTIAL_RETURN_NOT_AUDIT_READY','Differences, identities, as-run, financial snapshots, preserved failures/report/archives and minimal adoption package saved. Engineering complete=false and stable_for_independent_audit=false.',refs('final-file-identities.json','financial-summary.json','remaining-gaps.json','minimal-adoption-package.md'))
for x in rows:
    for p in x['evidence']: assert (ROOT/p).is_file(),p
write(HERE/'acceptance-matrix.json',{'C01_C15':rows,'engineering_complete':False,'stable_for_independent_audit':False,'original_FAILs_preserved':True,'head_and_scope_separate_checkpoints':{'head_root33':head['business_key'],'scope_root34':scope['business_key']},'memory_evidence_limit':memory['limits']})

# Keep old reservations. Known active envelopes and uncertainty are distinguished.
now=datetime.now(timezone.utc); command_start=datetime.fromisoformat(b['active_command']['start_utc'])
measured=(b['controlled_command_wall_seconds']-prior['controlled_command_wall_seconds'])+(b['runtime_command_wall_seconds']-prior['runtime_command_wall_seconds'])
first=(datetime.fromisoformat('2026-10-20T07:41:23.974632+00:00')-datetime.fromisoformat('2026-10-20T06:23:10+00:00')).total_seconds()
second=(datetime.fromisoformat('2026-10-20T08:17:21+00:00')-datetime.fromisoformat('2026-10-20T08:08:10+00:00')).total_seconds()
uncertain=(datetime.fromisoformat('2026-10-20T09:04:37+00:00')-datetime.fromisoformat('2026-10-20T08:17:21+00:00')).total_seconds()
uncertain+=(datetime.fromisoformat('2026-10-20T12:09:37+00:00')-datetime.fromisoformat('2026-10-20T09:04:37+00:00')).total_seconds()
third=(command_start-datetime.fromisoformat('2026-10-20T12:09:37+00:00')).total_seconds()
b['finalization05_unwrapped_command_wall_upper_seconds']=max(0,150+first+second+third+uncertain+60-measured)
b['finalization05_timing']={'known_active_envelopes_seconds':[first,second,third],'excluded_interrupt_UTC':['2026-10-20T07:41:23.974632Z','2026-10-20T08:08:10Z'],'unmeasured_read_edit_and_interruption_uncertainty_reserve_seconds':uncertain,'uncertainty_note':'08:17:21--12:09:37 has no reliable pause boundaries across repeated user continuations; reserved only as a conservative ceiling, NOT measured work/CPU or resource holding. No claim that the calendar gap was active.','initial_unwrapped_read_commands_upper_seconds':150,'final_post_save_metadata_reserve_seconds':60,'separately_measured_before059_seconds':measured,'manual_total':'UNKNOWN_NOT_ZERO','current059_wall':'Controller adds measured wall after its own exit; active interval ends at059 start to avoid overlap.','business_window_expired':True,'only_bounded_filesystem_return_after_expiry':True}
b['failures'].append({'case':'final05-filesystem-read-diagnostic','classification':'metadata_only_not_independent_product_defect','items':['One metadata read using the default Windows encoding failed; explicit UTF-8 used thereafter. No business action was repeated.']})
b['failures'].append({'case':'final05-final-save-prestart-deadline-denial','classification':'metadata_controller_gate_before_any_Job_or_resource','evidence':'finalization-05/command-059-prestart-denial.json','resolution':'Exact filesystem-only saving exception under the card; no business runtime extension.'})
keys=('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds','continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds','validation04_unwrapped_command_wall_upper_seconds','finalization05_unwrapped_command_wall_upper_seconds')
b['command_wall_conservative_upper_seconds']=sum(b.get(k,0) for k in keys)
wall_with_save=b['command_wall_conservative_upper_seconds']+60
assert wall_with_save<57600 and b['runtime_holding_union_seconds']<21600
b.update(engineering_status='FINALIZATION_05_PARTIAL_STOPPED_PERMISSION_AND_UI_GAPS',real_Q='FROZEN',remaining_roots=b['caps']['roots']-b['counts']['roots'],final_stop_proof='finalization-05/final-stop-proof.json',current_review_index='finalization-05/final-review-index.json',runtime_resume_requires_new_explicit_permit=True)
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as stream: stream.write(json.dumps({'kind':'finalization05_final_return','utc':now.isoformat(),'engineering_complete':False,'stable_for_independent_audit':False,'real_Q':'FROZEN','roots':40,'failures_entries':len(b['failures']),'command_wall_upper_with_final_save_reserve':wall_with_save,'holding_union_seconds':b['runtime_holding_union_seconds'],'gaps':['scope-removal','late-namespace-DataContext'],'manual_total':'UNKNOWN_NOT_ZERO'})+'\n')

matrix_text='\n'.join('- '+x['id']+'：'+x['status']+'。'+x['facts'] for x in rows)
prefix=f'''# TASK-120 / R-114 — 完整收尾05结果：局部修复与证据收口完成，整体未通过

保存：{now.astimezone(timezone(timedelta(hours=8))).isoformat()}。接收 A 独占工程窗口，Codex desktop；具体模型变体未暴露，不虚构型号。原 A+ 保持停止，无委派、无独审。

本卡尚未达到完整稳定候选：范围移除需要当前合同禁止的持久权限修订；namespace 与完整 DataContext 晚到 UI 尚无充分实证。已完成其余不受阻工程、逐项核证和清场。工程完整=false，稳定可集中独审=false，Q 冻结。没有把未知缺陷或缺失证据签成通过。

## 四组交付

- A 权限：11 项真实 PG/完整冻结请求反例及重复批准幂等性分别保存。未批准 answer/goal/memory/title/history、异活动父、真实不同实例、完整字节、endpoint、原件缺失分别命中准确边界；没有新增 claim/发送/预留。副本身份与损坏尾沿用原054原件。已撤销记忆 body_rows=0、资料墓碑与正文关闭、永久只读实际持久门另存核证；这些不替代 UI 转换证明。
- B ACK/K2：accepted COMMIT、launch claim COMMIT、result COMMIT 各自丢确认后按原键读持久事实，GET 无新增动作、0重复出站/预留，已 claim 键不重发。head/revoke/scope/source 均在实际 shared dispatch 释放后、重新取得 exclusive 前由不同 actor 提交，保存 worker/actor/锁窗口、007 与费用保留、head 不推进。memory 分支实际撤销/purge 已提交；原始 trace 与后续 PG 核证证明所列不变量，但根35未即时落盘 before-financial 快照，且在不必要 abandon 时失败，原 FAIL 与 UNKNOWN 均保留。
- C UI：继承根23/24五入口有限正常链和列明 owner/view，不重复 build。正式 bundle 的实际 JS/CSS 响应 hash 已绑定。根33独立 head 子例通过，整根因后继 scope 夹具失败仍为 FAIL；根34仅复检 scope 通过。namespace/DataContext 未通过，根36实际 frozen COMMIT 与 UI 未完成分开记录。
- D 完整性：C01—C15逐项链接、旧503持久结果、四实例金融分账、源/夹具差异、最终/as-run/dist身份、全部失败与精确 StopProof 已保存。统一入口是 finalization-05/final-review-index.json；最小采用方案在 minimal-adoption-package.md。未修改共享 DocuS 或分配新 TASK/CHG。

## 产品修复与原503

旧 budget02 范围变更键127091c0-c950-43a7-afdc-89b41f69165c：实际只读事务核得命令不存在、原 scope_revision=1 保持，因此 NOT_COMMITTED。原模型45b8d0b4-dd77-44d7-8cdd-370ef475c7b3 已 claim、领域 committed、007 received，摘要匹配，费用照留，未重发。两个旧批准未领取键也只读核证，没有过期重交或续 grant。

新独立 matrix-final 最小复现定位无条件 DELETE FROM activity_scope_sources 的 SQLSTATE42501。唯一产品增量 backend/app/activities/repository.py 的 _apply_scope_locked 读取既有 scope，仅删除实际移除的 source，再以 ON CONFLICT 更新版本/修订；保留事务、锁、CAS 与资格门。新增/版本更新路径实际 PG 通过，真实 scope 释放窗口和 UI scope 随后通过。

实际移除仍需 DELETE，而锁定应用 profile 未授此权。根31明确核得42501、命令不存在、scope/head/费用不变，未扩权、未改001—014/profile。新增成功不冒充移除成功。最小采用包给出单表 DELETE 与可信限定范围函数两种具体增量及安全审查点，均未执行。

## 新样本、费用与原未知

仅在原 CID/卷内创建一次 retrolume_task120_matrix_final，dataset=7ee0f885-de03-4e8b-9f92-b3f290ff5376，instance=0c00acec-176b-4a27-b718-aea0153c081c，OID21212。正常001—014、固定三活动与冻结8份合成输入；复用已核既有角色，无旧密码/角色权限修改，无新容器或卷。旧三库只读核对，期限、grant、金融与事件均不改。

金融权威为应用角色新连接读取的 PG，根38在所有变更后保存，根39/40仅 GET 核证并确认相同。各实例独立，不相加为共同额度：

- flow：25 次 / 6250000 合成费用微单位，原账完全未变。
- budget-01：100 次 / 25000000，原共同100门证据继承，未再刷99笔。
- budget-02：8 次 / 2000000，原账完全未变。
- matrix-final：23 次 / 5750000；A1=2/500000、A2=6/1500000、A3=15/3750000。所有活动 running reserve 为0；原件列出 settled seconds 和 operation。

真实 provider、实际费用、preview、Git 写入均0。原三个 UNKNOWN 的已提交 Q 事件子序列逐条未变；旧 A1 即使无 Q claim 仍是业务 UNKNOWN，永久不重发。所有后来已领取/UNKNOWN、007 received 和合成预扣照留，不退款、不释放旧 slot。

根35实际 memory 撤销/purge 完成后，夹具多余 abandon 正确触发 interview_memory_dependency_invalid；没有据此退款或重发。根36资料删除返回200、后续夹具 GET 的 Origin 错误造成403，删除并非失败；后续正常认证 GET 与墓碑核证完成，没有重复删除。根36永久只读已提交，缓存 authority 正确 q_root_changed；新 authority 正确 q_normal_root_required，不能接受任意错误码当通过。矩阵库保持 frozen，不解冻/重建/重绑。

## 失败、投入与停止

本轮从根25续至40，命令从056续号。原88条失败记录完整保留，新增23条阶段/整根/metadata记录，累计{len(b['failures'])}；同一失败可能同时有子阶段和整根条目，不是独立缺陷数。原TASK117的81历史另保留。根26复现权限失败；根31—33分别暴露刷新未完成、全局inflight等待和IDB随机键排序夹具问题，定向修正后 head/scope 各有实证。根35多余 abandon、根36冻结后错误采集以及根37—39的读取权限/准确枚举/legacy回执结构采集错误全部留档；根40仅只读持久收口通过，没有重复业务。末次文件保存曾被统一日历门在启动前拒绝，未创建Job/业务资源；只按卡面独立保存要求增加精确文件保存例外，不延长业务时窗。

累计 root40/64、PGstart39/64、API44/96、Browser11/16、build4/8、native59/128、HTTP1303/10000。容器/卷各1，新增逻辑库创建尝试1/1。上述剩余兜底次数不能绕过持久权限门或永久 frozen 的样本身份。

command wall 保守上界（含末次保存60秒预留）{wall_with_save:.6f}/57600秒；持有并集{b['runtime_holding_union_seconds']:.6f}/21600秒，本轮新增{b['runtime_holding_union_seconds']-prior['runtime_holding_union_seconds']:.6f}秒。旧投入与两个7200未知预留保留。已知活跃区间扣除另计实测命令/根wall，07:41:24—08:08:10中断排除；后续暂停边界不完整部分仅作为明确的保守不确定性预留，不称实际工作/CPU/资源持有。人工总量 UNKNOWN_NOT_ZERO。059退出后由控制器补精确wall，唯一账为 execution/budget.json。

本轮接收精确UTC在早次中断前未记齐，采用许可签发时点作为保守接收下界，收尾截止仍为2026-10-20 20:04:46.848938+08:00，不随继续消息重开24h；原首点与96h截止不变。该业务时窗已到期，最后仅保存既成材料，无业务验证再启动。

058于2026-10-20 15:41:23.916100+08:00核实511组PID/birth、113个Job、原CID Running=false/Pid0、55480/18120无监听；058自身exit0/tree_empty。之后无业务树/PG/API/Browser再启动，059为有限Job内文件保存并有独立退出回执。保留四库、数据、容器与卷，没有 drop/truncate/prune/批删。

## C01—C15

{matrix_text}

## 审阅与交回

统一入口：D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/finalization-05/final-review-index.json。

source.diff 是本轮唯一产品修补，fixture.diff 是本轮夹具增量；此前产品差异按索引直接引用原件。根34/40 product as-run 与最终产品一致，根33/34 UI 按各自实际 fixture hash 解释，后来的只读采集修正不回填旧运行身份。七锁定规则、四formal dist、六个旧包逐一复读一致；新包不递归嵌旧ZIP，不含.runtime、凭据或可用Q材料。最后059回执及唯一账作为包外权威附件在索引明确引用。

需主控采用的两个边界和最小验证方案已具体列出。尚不满足的 Must 不变，未启动原118集中独审，未签Q启用、STEP018整体/019/020/M1/项目。用户无需提供密钥、SQL或腾内存操作。

下面65338字节旧结果 SHA256 85ed46c94bd38c8382a66112f9462e0e00e186715d364ec6790c24bc40d6430a 原字节保留；旧轮“当前”字样只属于其历史时点。

---

'''
report.write_bytes(prefix.encode('utf-8')+old); assert report.read_bytes().endswith(old)
write(HERE/'result-preservation.json',{'old_report_bytes':len(old),'old_report_sha256':hashlib.sha256(old).hexdigest(),'unchanged_old_suffix':True,'new_report_sha256':sha(report)})
index={'task':'TASK-120','R':'R-114','scope':'完整收尾05','permit_id':b['current_permit_id'],'engineering_complete':False,'stable_for_independent_audit':False,'real_Q':'FROZEN','report':rel(report),'roots_added':list(range(25,41)),'four_groups':{'A':'acceptance-matrix.json C02/C04','B':'ACK-matrix-PASS.json and K2-* individually; memory limit explicit','C':'UI root33 head and root34 scope PASS; namespace/DataContext NOT_PASSED','D':'Exact preserved partial return; no stable acceptance'},'acceptance_matrix':'acceptance-matrix.json','remaining_gaps':'remaining-gaps.json','minimal_adoption':'minimal-adoption-package.md','source_diff':'source.diff','fixture_diff':'fixture.diff','final_identities':'final-file-identities.json','financial_summary':'financial-summary.json','actual_final_financials':'financial-final-separated.json','old_unknowns':'retained-original-Q-witness.json','final_stop':['final-stop-proof.json','command-058.receipt.json'],'final_filesystem_command_receipt':'command-059.receipt.json','live_authoritative_ledger':['../budget.json','../events.jsonl'],'ledger_and059_receipt_are_external_to_archive':True,'prior_product_diffs':['../source.diff','../repair-03/source.diff','../validation-04/source.diff'],'old_packages':'old-packages-preserved.json','all_historical_FAILUREs_preserved':True,'independent_audit_started':False,'runtime_resume_requires_explicit_adoption':True,'package':'final-review-candidate.zip','package_identity':'candidate-package-identity.json','no_private_configuration_or_usable_Q_material':True}
write(HERE/'final-review-index.json',index)
pack={report}
for p in HERE.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.zip','.pyc','.log') and p.name not in ('command-059.log','candidate-package-identity.json','save-consistency.json'): pack.add(p)
for x in changes: pack.add(ROOT/x['path'])
for n in range(25,41): pack.update(p for p in EX.glob(f'root-{n:02d}*') if p.is_file() and p.suffix in ('.json','.jsonl'))
for name in ('source.diff','repair-03/source.diff','validation-04/source.diff','final-bundle-identities.json'): pack.add(EX/name)
target=HERE/'final-review-candidate.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
    for p in sorted(pack):
        assert time.monotonic()-started<50
        name=rel(p); assert not name.startswith(('.runtime/','.git/')) and p.suffix!='.zip'
        archive.write(p,name)
with zipfile.ZipFile(target) as archive: assert archive.testzip() is None
write(HERE/'candidate-package-identity.json',{'path':rel(target),'bytes':target.stat().st_size,'sha256':sha(target),'files':len(pack),'engineering_complete':False,'old_ZIPs_embedded':0,'runtime_private_or_usable_Q_material_included':False,'final059_receipt_and_unique_ledger':'external, referenced in final-review-index.json'})
write(HERE/'save-consistency.json',{'utc':datetime.now(timezone.utc).isoformat(),'old_report_suffix_preserved':True,'old_roots_failures_events_prefixes_preserved':True,'old_six_packages_unchanged':True,'seven_rules_and_four_dist_unchanged':True,'archive_CRC_ok':True,'final_report_sha256':sha(report),'engineering_complete':False,'final_command_exit_receipt':'command-059.receipt.json, generated by parent after exit','save_wall_seconds':time.monotonic()-started})
print(json.dumps({'saved':str(report),'review_index':str(HERE/'final-review-index.json'),'engineering_complete':False,'failures_records':len(b['failures']),'package_bytes':target.stat().st_size}))
