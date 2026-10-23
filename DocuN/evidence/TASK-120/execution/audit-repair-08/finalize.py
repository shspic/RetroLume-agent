"""08 bounded filesystem return at a genuine sample-scope blocker, never a pass."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,difflib,hashlib,json,os,time,zipfile
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4];start=time.monotonic()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def link(p):return '['+Path(p).name+']('+Path(p).as_posix()+')'
def write(p,data):
    p=Path(p);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)

assert not (HERE/'sample-method-user-adoption.json').exists(),'A new decision arrived; continue the dependent work before returning'
assert not (HERE/'final-review-index.json').exists()
b=read(EX/'budget.json');prior=read(HERE/'budget.json.before.bytes');now=datetime.now(timezone.utc)
assert b['active_root'] is None and b['active_command'] is not None
assert b['roots'][:60]==prior['roots'] and b['failures'][:141]==prior['failures']
assert (EX/'events.jsonl').read_bytes().startswith((HERE/'events.jsonl.before.bytes').read_bytes())
report=ROOT/'DocuN/results/TASK-120-result.md';old=(HERE/'result.before.bytes').read_bytes()
assert len(old)==109435 and hashlib.sha256(old).hexdigest()=='3772e95062f1f423b299ee6542364a5ce0ca8c4eae92717b35b41efca79a86a4'
assert report.read_bytes()==old
assert read(HERE/'command-1002.receipt.json')['exit_code']==0
assert read(HERE/'command-1003.receipt.json')['exit_code']==0
stop=read(HERE/'final-stop-proof.json');assert stop['08_stop_dimensions_confirmed']
assert read(HERE/'F02-ADMIN-delegation-SET-combination-PASS.json')['status']=='PASS'
facts=read(HERE/'memory-fixture-current-selection-readonly.json');assert facts['active_selected_memories']==0
assert b['counts']['roots']==62 and b['counts']['pg_starts']==62
assert all(b['counts'][k]==prior['counts'][k] for k in ('api_starts','browser_starts','frontend_builds','native_business_sessions','http','provider_calls','actual_fee_microunits','Git_writes'))
registry=read(HERE/'change-registry.json')['paths'];allowed={str((ROOT/x['path']).resolve()).casefold() for x in registry}
ledger={str((EX/x).resolve()).casefold() for x in ('budget.json','events.jsonl')};baseline=[]
for row in read(HERE/'baseline-identities.json')['checked']:
    p=Path(row['path']);got=sha(p) if p.is_file() else None
    status='UNCHANGED' if got==row['expected'] else 'REGISTERED08_CHANGE' if str(p.resolve()).casefold() in allowed else 'SOLE_LEDGER_UPDATED' if str(p.resolve()).casefold() in ledger else 'UNEXPECTED'
    assert status!='UNEXPECTED',str(p)
    baseline.append({'path':str(p),'before_sha256':row['expected'],'sha256':got,'status':status})
current=[];changes=[];source=[];fixture=[]
for row in registry:
    p=ROOT/row['path']
    if not p.is_file():continue
    raw=p.read_bytes()
    if p.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
    current.append({'path':row['path'],'sha256':sha(p),'bytes':len(raw)})
    if sha(p)==row['before_sha256']:continue
    pre=HERE/'preimage'/row['path']
    if row['existed']:assert sha(pre)==row['before_sha256']
    changes.append({'path':row['path'],'before_sha256':row['before_sha256'],'sha256':sha(p),'reason':row['reason']})
    delta=difflib.unified_diff(pre.read_text(encoding='utf-8-sig').splitlines(True) if pre.exists() else [],raw.decode('utf-8-sig').splitlines(True),
        fromfile='before/'+row['path'] if pre.exists() else '/dev/null',tofile='after/'+row['path'])
    (source if row['path'].startswith('backend/app/') else fixture).extend(delta)
(HERE/'source.diff').write_text(''.join(source),encoding='utf-8');(HERE/'fixture.diff').write_text(''.join(fixture),encoding='utf-8')
asrun=read(HERE/'root-62-batch-01-as-run.json')['files'];mismatches=[]
for row in asrun:
    if row['path'].startswith('backend/app/') and sha(ROOT/row['path'])!=row['sha256']:mismatches.append(row['path'])
assert not mismatches
write(HERE/'final-file-identities.json',{'baseline606_references':baseline,'current_registered':current,'changes':changes,
    'root62_product_asrun_mismatches':mismatches,'offline1002_tests_equal_current_bytes':True,
    'proposed_memory_and_browser_fixtures_not_executed':True,'source_diff':'source.diff','fixture_diff':'fixture.diff'})
packages=read(EX/'audit-repair-07/old-packages-preserved.json')['eight_prior_packages']+[read(EX/'audit-repair-07/candidate-package-identity.json')]
for row in packages:assert sha(ROOT/row['path'])==row['sha256']
assert len(packages)==9
write(HERE/'old-packages-preserved.json',{'nine_prior_packages':packages,'all_unchanged':True,'nested_ZIPs':0})
write(HERE/'remaining-gaps.json',{'F01_F04_F05':'Independent review01 CLOSED, inherited unchanged.',
    'F02':'Current bounded algorithm and real transactional ADMIN delegation/SET reproduction PASS; original TASK121 delta verdict pending.',
    'F03':'Code/direct offline projection checks PASS; required normal PG/API failure/readback/reopen/explicit retry/browser evidence NOT RUN.',
    'genuine_blocker':'All three fixed activities lack a live selected memory. The only stored selection is the already revoked07 memory; selection is written only when creating an activity. No normal selection-update interface exists. The card forbids rebinding activity/root/grant and restoring revoked memory.',
    'requested_smallest_method_adjustment':'One explicitly non-authorizing synthetic Q-body/dependency cleanup fixture, no accepted model command/approval/claim, same normal memory POST/GET/retry and same ControlHub; no activity/root/grant change. Not represented as normal model-chain evidence.',
    'answer':'PENDING. No elapsed time or preselected option treated as approval. No dependent body generation or deletion performed.',
    'proposal_fixture':'backend/tests/fixtures/task120/repair08_memory.py; explicit user adoption gate required before any runtime.',
    'business_deadline_utc':b['targeted_repair08']['business_deadline_utc'],'finish_deadline_utc':b['targeted_repair08']['finish_deadline_utc'],
    'unknown_defects':'Not certified absent. Whole08 task not passed or accepted; real Q remains frozen.'})
b['failures'].append({'case':'repair08-grouped-metadata-diagnostics','classification':'metadata records, not independent defects',
    'items':['First exact card read output was truncated; own new directory repair-08 was relocated to required audit-repair-08 with explicit forward path mapping. Old logs/receipts were not rewritten.',
        'A few nonexistent source paths/one malformed rg flag were corrected by exact reads.',
        '1000 local asyncio initialization timed out;1001 faulthandler located Windows fallback socketpair blocked by restricted execution.1002 scoped approved local execution passed all5 tests.',
        'Root61 memory sampler constructed evidence directory twice and failed before PG startup; original failure/zero holding retained, exact path correction proved by62.']})
b['engineering_status']='TARGETED_REPAIR08_F02_PASS_F03_DYNAMIC_BLOCKED_PENDING_SAMPLE_METHOD'
b['real_Q']='FROZEN';b['runtime_resume_requires_explicit_sample_method_adoption']=True
b['targeted_repair08_return']={'utc':now.isoformat(),'whole_task_complete':False,'F02_engineering':'PASS_TARGETED','F03_dynamic':'NOT_RUN_SCOPE_CONFLICT',
    'pending_user_decision':True,'old_60_roots_141_failures_events_report_suffix_preserved':True,'resources_stopped':True,
    'no_new_business_after_return_without_dependent_method_adoption':True,'deadline_not_extended':True}
keys=('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds',
    'continuation_metadata_uncertainty_reserved_seconds','continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds',
    'validation04_unwrapped_command_wall_upper_seconds','finalization05_unwrapped_command_wall_upper_seconds','continuation06_unwrapped_command_wall_upper_seconds',
    'audit_repair07_unwrapped_command_wall_upper_seconds','targeted_repair08_unwrapped_command_wall_upper_seconds')
b['command_wall_conservative_upper_seconds']=sum(b.get(k,0) for k in keys);assert b['command_wall_conservative_upper_seconds']+60<72000
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'kind':'repair08_scope_blocked_partial_return','utc':now.isoformat(),
    'F02_engineering':'PASS_TARGETED','F03_dynamic':'NOT_RUN_PENDING_SAMPLE_METHOD_ADOPTION','real_Q':'FROZEN','counts':b['counts'],'whole_task_complete':False},ensure_ascii=False)+'\n')
delta={k:b['counts'][k]-prior['counts'][k] for k in b['counts']}
write(HERE/'budget-summary.json',{'counts':b['counts'],'caps':b['caps'],'new08_delta':delta,'failure_records':len(b['failures']),
    'old141_failure_prefix':True,'original_TASK117_81_separate':True,'old_wall64525_retained':prior['command_wall_conservative_upper_seconds'],
    'old07_postsave60_and_unknown_reserves_untouched':True,'save_time_upper_with_final_command60':b['command_wall_conservative_upper_seconds']+60,
    'wall_cap':72000,'holding_seconds':b['runtime_holding_union_seconds'],'holding_cap':21600,
    'new_holding':b['runtime_holding_union_seconds']-prior['runtime_holding_union_seconds'],
    'no_calendar_reset':True,'exact_human_receipt':'UNKNOWN','manual_total':'UNKNOWN_NOT_ZERO',
    'unique_current_ledger':['../budget.json','../events.jsonl'],'final_command_close_and_postsave_reread_external_to_archive':True})
write(HERE/'financial-summary.json',{'new08_model_embedding_admissions':0,'new08_approval_claim_dispatch':0,'new08_fees':0,
    'new08_API_browser_starts':0,'normal_model_chain_replayed':False,'all_permanent_role_changes':0,
    'inherited_per_instance_actual_PG':'../audit-repair-07/final-new-instances-separated-PASS.json',
    'historical_main_requests':5,'historical_main_reserved_microunits':1250000,'historical_r02_requests':0,
    'fresh_financial_query08':'Not claimed. Sole PG episode executed role GRANT/SET in explicit transaction, fully rolled back; no business DML or new admission.',
    'no_cross_instance_credit_sum':True,'old_UNKNOWN_and_reservations_retained':True,'real_provider_actual_fee_preview_Git':0})
prefix=f'''# TASK-120 / R-114 — 续作08受阻收尾：F02定向实证完成，F03动态造样待范围裁定

保存：{now.astimezone(timezone(timedelta(hours=8))).isoformat()}。原A独占工程窗，Codex desktop，后台精确模型变体未暴露；无子Agent，旧A+停止。TASK-120/R-114/STEP018和原累计账不变。**本卡未整体完成、未通过验收。** 原独审关闭的F01/F04/F05保持，F02有新增修正及实际PG证据供原TASK121增量复核；F03代码及离线检查完成，必需的正常PG/API失败读回/重开/显式重试和浏览器证明尚未运行，不以离线通过替代。

真实阻塞：新库三活动唯一选中记忆是07已撤销对象3a3d2ec6-a821-48a3-9908-cc18755c96ed，active_selected_memories=0。活动记忆选择只由创建时的_memory_insert_selection写入，无现有正常修改接口；原绑定不改、旧记忆不恢复时，新memory无法进入这三活动的正常Q请求。增加query/index或消费剩余11笔并不能补出记忆选择。实际只读PG身份结果：{link(HERE/'memory-fixture-current-selection-readonly.json')}。

已提出最小方法调整：仅在获批新根生成一个明确不可授权的合成Q正文/依赖清理夹具，继续使用真实ControlHub和正常记忆POST、GET、重开与明确retry；不改活动/root/grant、不恢复旧批准、不引入模型准入，也不把它算作正常模型链证据。该答复仍待用户，未把预选或超时当批准。备用夹具和单页浏览器脚本已写好但未执行，运行入口在任何API或副本创建前检查显式采用门。若保持原合同，本项动态造样受阻；若批准且仍在原业务门内，可从此处续作，旧成功/失败不重跑。

统一索引：{link(HERE/'final-review-index.json')}；范围与缺口：{link(HERE/'remaining-gaps.json')}；本轮有限差异包：{link(HERE/'partial-review-candidate.zip')}，精确身份在{link(HERE/'candidate-package-identity.json')}。它是受阻时点材料，不是稳定完整通过候选。

## F02：ADMIN组合能力的有界闭包与实际复现

{link(ROOT/'backend/app/data_exit/q_roles.py')}现在分别追踪可SET角色和有效INHERIT角色；ADMIN可再授权其目标、改变其成员选项，故将目标加入潜在可SET集合，再继续SET/INHERIT/ADMIN传播。每角色每模式至多访问一次，每主体最多两次扫描每条边，保留1024角色/4096成员容量上界；多级链和环不会无限递归。用途判定沿原实际主体/组，随后核潜在能力，未将所有ADMIN或membership粗暴拒绝。原直接ACL、管理权、owner/definer及其他严格检查保留。

PG17角色再授权/选项语义依据[GRANT官方文档](https://www.postgresql.org/docs/17/sql-grant.html)、[Role Membership](https://www.postgresql.org/docs/17/role-membership.html)；本地真实PG实证独立核结论。根62在audit07_main、集群7697981369175429158、唯一测试连接，原快照主体task120_flow_snapshot当前DELETE=false/SET-app=false。事务内创建批准bridge1，bridge1以INHERIT FALSE/SET TRUE通app，S以ADMIN TRUE/INHERIT FALSE/SET FALSE通bridge1。产品检查在扩大前准确拒绝data_role_capability_mismatch。

随后同一事务SET SESSION AUTHORIZATION到实际S，由S执行GRANT bridge1 TO retrolume_data_snapshot WITH INHERIT FALSE, SET TRUE，实际pg_has_role(session_user,app,SET)=true，再SET ROLE app核实际DELETE=true；并非由superuser代执行这一步授权。finally ROLLBACK，正常前后检查通过，独立新连接全角色图/权限与before完全一致。期间没有API/worker，没有提交危险成员关系、改密码/LOGIN/角色管理属性或执行服务器程序。原始证据：{link(HERE/'F02-ADMIN-delegation-SET-combination-PASS.json')}及{link(HERE/'root-62-batch-01-as-run.json')}。旧11个角色场景/两快照对照未整批重跑。

## F03：组合状态只读修正及尚未验证的边界

新增{link(ROOT/'backend/app/memory/cleanup_projection.py')}，GET命令收据、详情、列表都通过同一组合投影：持共享Q policy后读取DB及准确当前记忆的传递依赖，再短锁读已验日志。匹配副本pending/unknown或done后路径重现时，沿用purge_state/purge_state_now=pending、cleanup_status_unconfirmed=true，不回写DB已COMMIT的done；无Q/确无相关副本可显示实际DB状态。控制残尾、依赖索引不明或不可访问不吞异常落回done。只检查文件存在，不读取正文、不删除、不追加Q事件，也不构造QAuthority。

锁序为shared Q policy→PG读事务→短journal读；写方已有exclusive Q policy→PG→清理，读方非阻塞等待policy以免阻塞持锁事件循环。sealed目标不拿旧正常源的Q副本索引冒充目标实体，沿原readonly仓储资格读真实DB事实。必要小依赖{link(ROOT/'backend/app/activities/repository.py')}仅让已持policy的纯读方法沿用其锁并跳过正常写QAuthority构造；写、claim、worker、007、金融和联合时钟协议未改。F03源删除/_CleanupAttempt不改，前端产品/dist不改，build=0。

命令1002运行实际算法和实际ControlHub/RootLease私有日志的5项离线检查：ADMIN→后续SET、多级ADMIN/有环收敛、无害ADMIN及INHERIT-only不误转SET、容量关闭，以及pending重放、准确done/路径重现、共享锁隔离、依赖未知/残尾关闭、无Q及sealed读兼容。通过见{link(HERE/'command-1002.log')}和{link(HERE/'command-1002.receipt.json')}。这些是离线直接检查，不是实际PG/HTTP失败清理或真实页面结果；后者因上述造样合同冲突未运行。{link(ROOT/'backend/tests/fixtures/task120/repair08_memory.py')}与{link(ROOT/'frontend/tests/task120-repair08-memory.mjs')}只属待采用方法，AST/JS语法已检查，没有启动浏览器，更无假造截图/PASS。

## 资源、账、停止和偏差

原源CID/卷/镜像/1CPU/512MiB/pids128/restart=no和loopback55480/API18120保持；恢复目标4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332未启动。新增2根（61、62），仅1次PG启动；根61在PG启动前因内存采样证据路径重复拼接而退出，holding=0，实际FileNotFoundError原件保留，修正后62成功。API、Browser、build、Native、HTTP、真实provider/费、preview、Git均增0，没有新库/容器/卷/LOGIN或业务删除。根62内存采样最小563052544字节，无降门限或Docker重启，不要求用户反复腾内存。

累计counts：{json.dumps(b['counts'],ensure_ascii=False)}。holding={b['runtime_holding_union_seconds']:.6f}/21600s，增{b['runtime_holding_union_seconds']-prior['runtime_holding_union_seconds']:.6f}s。原141失败前缀保留，现{len(b['failures'])}条，另列TASK117旧81；记录数不等于独立缺陷数。1000受限执行卡在Windows asyncio fallback socketpair而超时，1001定位trace，1002只对精确本地测试经平台审批后通过，原失败/清场保留，没有关闭全局sandbox或绕过拒绝。初读截断使新证据目录先误建repair-08，后来安全移动为卡定audit-repair-08；前向路径映射{link(HERE/'path-relocation.json')}保留，未改旧历史原件。

历史main5笔/1250000微单位合成预扣、r02=0/0按07实际PG逐实例记录继承，本轮没有业务DML/准入；未另作当前金融余额读回，不跨实例加成新额度。原UNKNOWN、007和预留不退/不重发。见{link(HERE/'financial-summary.json')}。

新08对象停止检查：{link(HERE/'final-stop-proof.json')}。本轮{len(stop['registered_processes'])}组PID/birth、{len(stop['registered_jobs'])}个具名Job、两精确CID stopped/Pid0和55480/55481/18120无监听，unresolved={len(stop['unresolved'])}。观察unknown仍保留unknown，必要时明确用准确Job成员+空树/缺席证明。原079的705组不是705次本轮新鲜退出：其中20条unknown及review01认可的19条旧退出、1条根22 Job组合证明原样继承，不改旧记录。1003自身exit0/tree_empty，最后文件保存命令也需包外回执确认。

原109435字节结果精确后缀、旧60根/141失败和events原字节前缀、606条审计引用中未授权改动之外的身份、7规则、001—015/profile/codec、worker/时钟/领取/金融及前端产物均保留，9个旧ZIP不变。差异及精确hash在{link(HERE/'final-file-identities.json')}、{link(HERE/'source.diff')}、{link(HERE/'fixture.diff')}；根62产品与最终字节零差异，新拟议夹具不冒充其已实跑。

旧wall64525.559426和旧post-save60/未知预留保留；本轮按实际首次采时2026-10-21T10:51:48Z起的观察区间保守入账，不将已收尾07至本轮交接空档再算工作。人工接收UNKNOWN，bootstrap前2批只读事实登记，不倒签首工具前登记。原业务门2026-10-21T12:29:21.021710Z（20:29）、收尾门12:59:21.021710Z（20:59）和96h不延长；上界及最终实耗以唯一{link(EX/'budget.json')}及{link(EX/'events.jsonl')}为准，包内时点上界见{link(HERE/'budget-summary.json')}。关闭历史控制不通过的责任不由技术修正替代。

下一步仅待上述最小造样方法决定；若批准，在原剩余时窗/次数内接续F03实证，不重做F02；若维持原合同或原业务门已到，F03保持证据缺口交回。原TASK121/主控裁定未填，Q继续冻结，STEP018整体/019/020/M-1/项目/发布均未签。

---

以下为续作07及更早统一结果原109435字节（SHA256 3772e95062f1f423b299ee6542364a5ce0ca8c4eae92717b35b41efca79a86a4）。

'''
tmp=report.with_suffix('.tmp');tmp.write_bytes(prefix.encode('utf-8')+old);os.replace(tmp,report);assert report.read_bytes().endswith(old)
index={'task':'TASK-120','R':'R-114','scope':'续作08 partial at genuine sample-method conflict','whole_task_complete':False,
    'F01_F04_F05':'CLOSED_REVIEW01_INHERITED','F02':'TARGETED_ENGINEERING_PASS_PENDING_DELTA_AUDIT',
    'F03':'IMPLEMENTED_OFFLINE_PASS_DYNAMIC_NOT_RUN_PENDING_USER_METHOD_DECISION','real_Q':'FROZEN',
    'report':rel(report),'product_and_fixture_diffs':['source.diff','fixture.diff'],'identities':'final-file-identities.json',
    'F02_evidence':'F02-ADMIN-delegation-SET-combination-PASS.json','F03_offline':'command-1002.receipt.json',
    'blocker':'remaining-gaps.json','stop':'final-stop-proof.json','stop_receipt':'command-1003.receipt.json',
    'unique_current_ledger':['../budget.json','../events.jsonl'],'final_command_receipt':b['active_command']['manifest'].replace('.json','.receipt.json'),
    'package':'partial-review-candidate.zip','package_identity_external':'candidate-package-identity.json',
    'proposed_runtime_gated_and_not_executed':True,'does_not_grant_new_window_or_business_authority':True}
write(HERE/'final-review-index.json',index)
pack={report};pack.update(ROOT/x['path'] for x in changes)
excluded={b['active_command']['manifest'].replace('.json','.log'),'candidate-package-identity.json','save-consistency.json'}
for p in HERE.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.zip','.pyc') and p.name not in excluded:pack.add(p)
target=HERE/'partial-review-candidate.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
    for p in sorted(pack):
        assert time.monotonic()-start<45;name=rel(p);assert not name.startswith(('.runtime/','.git/')) and p.suffix!='.zip';archive.write(p,name)
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None
write(HERE/'candidate-package-identity.json',{'path':rel(target),'bytes':target.stat().st_size,'sha256':sha(target),'files':len(pack),
    'whole_task_complete':False,'private_Q_body_credentials_or_usable_approval':False,'nested_ZIPs':0,
    'entry_identities':[{'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(pack)]})
write(HERE/'save-consistency.json',{'utc':datetime.now(timezone.utc).isoformat(),'old_result_suffix_exact':True,
    'new_report_sha256':sha(report),'old60_roots_141failures_events_prefixes_exact':True,'nine_old_ZIPs_unchanged':True,
    'CRC_ok':True,'whole_task_complete':False,'pending_user_sample_method_decision':True,'save_seconds':time.monotonic()-start})
print(json.dumps({'saved':str(report),'whole_task_complete':False,'F02':'PASS_TARGETED','F03_dynamic':'BLOCKED_SCOPE_CONFLICT','package_files':len(pack)}))
