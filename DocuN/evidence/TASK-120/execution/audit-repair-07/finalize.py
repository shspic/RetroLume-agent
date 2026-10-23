"""Final07 filesystem-only return. Exact old report suffix and original ledgers retained."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,os,time,zipfile

HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4]
started=time.monotonic()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def link(p,label=None):
    p=Path(p);return '['+(label or p.name)+']('+p.as_posix()+')'
def write(p,data):
    p=Path(p);tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)

assert not (HERE/'final-review-index.json').exists(),'Returned already; inspect rather than rewrite'
b=read(EX/'budget.json');prior=read(HERE/'budget.json.before.bytes');now=datetime.now(timezone.utc)
assert b['active_root'] is None and b['active_command']['manifest']=='command-999.json'
assert b['roots'][:51]==prior['roots'] and b['failures'][:125]==prior['failures']
assert (EX/'events.jsonl').read_bytes().startswith((HERE/'events.jsonl.before.bytes').read_bytes())
report=ROOT/'DocuN/results/TASK-120-result.md';old=(HERE/'result.before.bytes').read_bytes()
assert report.read_bytes()==old and len(old)==91351 and hashlib.sha256(old).hexdigest()=='3d044a788f7354e9a3b1fec0f75bab100f182469dea42613d3112078cda67b03'
assert read(HERE/'preparation-check.json')['engineering_targeted_checks_complete']
for number in (78,79,80):
    receipt=read(HERE/f'command-{number:03d}.receipt.json')
    assert receipt['exit_code']==0 and receipt['tree_empty']
identities=read(HERE/'final-file-identities.json')
for x in identities['registered_current_files']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
stop=read(HERE/'final-stop-proof.json');assert stop['all_fresh_stop_dimensions_confirmed']
assert read(HERE/'impact-matrix.json')['independent_audit']=='PENDING_ORIGINAL_TASK121_INCREMENTAL_REVIEW'
assert len(read(HERE/'old-packages-preserved.json')['eight_prior_packages'])==8
for x in read(HERE/'old-packages-preserved.json')['eight_prior_packages']:assert sha(ROOT/x['path'])==x['sha256']
assert b['counts']=={'roots':60,'pg_create_attempts':2,'pg_objects':2,'volume_create_attempts':2,'volumes':2,
    'pg_starts':61,'api_starts':63,'browser_starts':14,'frontend_builds':5,'native_business_sessions':69,'http':1520,
    'preview_creates':0,'preview_starts':0,'provider_calls':0,'actual_fee_microunits':0,'Git_writes':0}

# Read/search/path errors not issued as runtime/command receipts remain facts,
# grouped once as metadata diagnostics, never counted as independent defects.
b['failures'].append({'case':'audit07-metadata-read-and-fixture-diagnostics',
    'classification':'grouped_metadata_only_not_independent_product_defect_count',
    'items':['Several absent guessed paths/Windows literal-glob reads and an incorrect read-only interpreter workdir were corrected by exact rg paths.',
        'Early baseline/format reader assumptions corrected before relevant writes; byte snapshots and322 actual audit identities retained.',
        'Root57 fixture attempted JSON digest on bytes; original batch/root failures retained, corrected to raw_digest before any delete.',
        'Root55 binding body missing original_sha256 and root58 legacy GET Origin rejection were fixture errors; original receipts retained; exact unaccepted key/body and successful substeps reconciled.'],
    'same_runtime_failures_not_erased_or_reclassified_as_pass':True})
b['audit_repair07_synthetic_admissions']=5
b['audit_repair07_completion']={'utc':now.isoformat(),'engineering_complete':True,'targeted_F01_F05_checks_complete':True,
    'independent_audit':'PENDING_ORIGINAL_TASK121_DELTA_REVIEW','new_DB_admissions':{'audit07-r02':0,'audit07-main':5},
    'new_only_decisions_retired':8,'precise_delete_manifest_files_absent':6,'source_container_stopped':True,'target_never_started07':True}
# Entry envelope is updated by the owning controller. Reserve exactly60s for
# post-save metadata reread; the finite999 run is measured after this child exits.
b['audit_repair07_unwrapped_command_wall_upper_seconds']+=60
b['audit_repair07_timing']={'entry_clock_utc':b['audit_repair07']['first_tool_clock_observation_utc'],
    'save_utc':now.isoformat(),'actual_human_receipt_utc':'UNKNOWN','deadline_basis':'Conservative original issue time',
    'manual_total':'UNKNOWN_NOT_ZERO','post_save_metadata_reserve_seconds':60,
    'final999_actual_wall_added_by_controller_after_exit':True,
    'note':'Observed continuous interval is an uncertainty ceiling, not measured CPU/work. Approval/queue gaps not separately known; old uncertainty reserves retained. No new7200 reservation.'}
keys=('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds',
    'unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds',
    'continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds',
    'validation04_unwrapped_command_wall_upper_seconds','finalization05_unwrapped_command_wall_upper_seconds',
    'continuation06_unwrapped_command_wall_upper_seconds','audit_repair07_unwrapped_command_wall_upper_seconds')
b['command_wall_conservative_upper_seconds']=sum(b.get(k,0) for k in keys)
ceiling=b['command_wall_conservative_upper_seconds']+60
assert ceiling<72000 and b['runtime_holding_union_seconds']<21600
assert now<datetime.fromisoformat(b['audit_repair07']['finish_deadline_utc'])
b.update(engineering_status='AUDIT_REPAIR07_COMPLETE_STOPPED_READY_FOR_TASK121_DELTA_REVIEW',real_Q='FROZEN',
    current_review_index='audit-repair-07/final-review-index.json',final_stop_proof='audit-repair-07/final-stop-proof.json',
    runtime_resume_requires_new_explicit_permit=True,remaining_roots=b['caps']['roots']-b['counts']['roots'])
write(EX/'budget.json',b)
event={'kind':'audit07_complete_candidate_return','utc':now.isoformat(),'engineering_complete':True,
    'independent_audit':'PENDING_ORIGINAL_TASK121_DELTA_REVIEW','real_Q':'FROZEN','counts':b['counts'],
    'failures_entries':len(b['failures']),'wall_upper_with_final999_60second_reserve':ceiling,
    'holding_union_seconds':b['runtime_holding_union_seconds'],'manual_total':'UNKNOWN_NOT_ZERO'}
with (EX/'events.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(event,ensure_ascii=False)+'\n')
delta={k:b['counts'][k]-b['audit_repair07']['old_counts'][k] for k in b['counts']}
write(HERE/'budget-summary.json',{'counts':b['counts'],'caps':b['caps'],'new07_deltas':delta,
    'old_root_records':51,'old_failure_records':125,'failure_records':len(b['failures']),'new_failure_records':len(b['failures'])-125,
    'original_TASK117_failures_separate':81,'failure_records_are_not_distinct_defects':True,
    'old_wall_upper_retained':b['audit_repair07']['old_wall_ceiling'],'current_wall_upper_with_final999_60second_reserve':ceiling,
    'wall_cap':72000,'holding_union_seconds':b['runtime_holding_union_seconds'],'holding_cap':21600,
    'new_holding_seconds':b['runtime_holding_union_seconds']-b['audit_repair07']['old_holding'],
    'logical_DBs':b['audit_repair07_logical_databases'],'synthetic_admissions':5,'synthetic_admission_cap':16,
    'actual_first_human_receipt':'UNKNOWN','deadline_basis':'Conservative issue time, no extension of original96h',
    'old_manual_total_and_unknown_intervals':'UNKNOWN_NOT_ZERO','final999_receipt_and_latest_sole_ledger_external_to_archive':True})

base=HERE
prefix=f'''# TASK-120 / R-114 — 续作07结果：五项修复与定向验证完成，待原TASK-121增量复核

保存：{now.astimezone(timezone(timedelta(hours=8))).isoformat()}。原A独占工程窗口，Codex desktop；实际后台模型变体未暴露，A是资源标签。原A+保持停止，无子Agent或并行写入。依据已批准AP-120-07及精确permit TASK-120-Q-PREP-AUDIT-REPAIR-07-20261021继续，任务/R/STEP归属和累计账未清零。

工程定向检查完成，可交原TASK-121增量复核。五项最终工程状态均为PASS_TARGETED_ENGINEERING；独审、主控验收和真实Q启用均未签。未知缺陷没有被承诺为零。Q继续冻结，本轮收尾后工程停止，剩余次数不构成恢复许可。

统一入口：{link(base/'final-review-index.json')}；五项对应：{link(base/'impact-matrix.json')}；增量包：{link(base/'final-review-candidate.zip')}，精确包身份在{link(base/'candidate-package-identity.json')}。包不递归包含8个旧ZIP，不含.runtime、数据库凭据、Q正文或可用批准。唯一当前账仍为{link(EX/'budget.json')}和{link(EX/'events.jsonl')}；包内.before.bytes只作修前快照。

## TASK-121-F01：迁移前提及两个精确015身份

分别检查必需SELECT、INSERT、UPDATE并要求全部成立；原额外DELETE/TRUNCATE用于拒任一多权的语义保留。事务、锁和失败零部分DDL保持。新main库正常R02已有行暴露了CHECK转换顺序缺陷：首次修订015先加R03 CHECK时实际23514，根52整事务回滚；保存原FAIL和精确失败SQL。修为同事务DROP旧CHECK、ADD新CHECK NOT VALID、UPDATE原控制行到R03、VALIDATE后COMMIT。根54只在获批新main库应用最终015一次。

旧已应用015 SHA256=59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e；最终新015 SHA256=874d2a173f401ce923680d184eb5687c121fd70831d8b86cd9b6740a7c330915。失败中间版本1fbe278e19bd65f55d043159167e108563adcde8dae870a0bcf060b2f9c0a712不是兼容身份。001—014、R01/R02冻结常量、表列/金融及公开格式未改；旧库未重跑、回填或迁移，也不宣称旧安装通过了新前提。

正常reader只接受旧/新两个精确完整迁移链；codec保留包内精确历史链，新初始化仍取当前完整DDL链，不允许任意015范围或跳过hash。实际只读打开原06生产PG备份成功，其SHA256仍为3d43878f2ff9da2f8043fed02fbc8f2c61fb1ab02217f9282c0a7cdbf74f9611。旧/新codec和未知hash反例通过；未新做完整PG restore，原工厂/只读证据按原适用性继承。

真实PG三项缺权负例及正常安装：{link(base/'F01-select-only-PASS.json')}、{link(base/'F01-missing-insert-PASS.json')}、{link(base/'F01-missing-update-PASS.json')}、{link(base/'F01-normal-R03-install-PASS.json')}。缺权负例实际使用根52首修订SQL，最终修订的GRANT前前提字节一致；后续CHECK转换修正在根54验证，不把旧实跑冒称新字节实跑。兼容：{link(base/'F01-exact-codec-compatibility-PASS.json')}。

## TASK-121-F02：实际INHERIT、SET、ADMIN和管理能力

新增私有q_roles检查，在形状/ACL投影前读取PG17真实pg_roles、pg_auth_members三种选项及has_table_privilege，不以直接ACL或角色名称代替能力。按session主体沿SET链、再从每个可选角色沿INHERIT链求实际能力；检查4个用途组、可信owner及可达组的实际LOGIN主体。snapshot只读、loader导入、app正常scope权限分别约束；拒绝越权owner/SECURITY DEFINER所有权、可达ADMIN危险边和管理角色。合法的无继承/无SET普通成员关系可通过。

原8个角色能力负例覆盖直接/间接继承、SET-only、loader→app、app→pg_write_all_data、app→controller owner、可信owner→app及ADMIN无INHERIT/SET。后续增加control表、public schema/database CREATE及服务器文件/程序/信号/维护等管理能力检查，补实际snapshot SET-only→pg_execute_server_program负例与合法成员/正常快照读和写拒绝。未执行服务器程序。每次同一真实客户端事务内临时变化、测试、ROLLBACK，另开连接核图及权限与before一致，无API/worker并发、无永久角色或成员变更。只临时使用批准的2个NOLOGIN bridge。

PG语义参照[PG17角色成员](https://www.postgresql.org/docs/17/role-membership.html)、[权限查询函数](https://www.postgresql.org/docs/17/functions-info.html)、[预定义角色](https://www.postgresql.org/docs/17/predefined-roles.html)；实际能力结论来自本地PG实跑。全部原始F02案例见{link(base/'impact-matrix.json')}。根54 q_roles精确旧字节已按原as-run hash重建保存，原有图/用途检查未变；管理增量根57补证，最终根60正常schema检查通过，边界见{link(base/'as-run-final-mapping.json')}。

## TASK-121-F03：源/记忆Q正文清理、失败关闭与重开重试

prepare登记实际来源/历史/选中记忆和传递依赖摘要索引；源墓碑提交后、记忆revoke/purge正常路径接入Q准确清理。先持Q排他policy并记cleanup_pending，再验证准确普通文件、根目录、file identity/hash、单硬链接及无reparse，用Windows句柄删除，最后记cleanup_done。失败/待清理从artifact、operator查看、reference及实际gateway共同关闭，保留元数据/摘要/007历史/原费用。无任意目录扫描或递归删除，替换/重建文件不按旧身份误删。

本轮预登记6条准确合成文件，含5个Q正文文件和1个原始合成资料文件，均位于.runtime/task120-audit07，最终全不存在；无旧Q根、旧证据或用户资料删除。正常HTTP记忆撤销及自动purge、正文拒读/旧引用拒用、无关正文hash保留、金融/007保留通过，见{link(base/'F03-normal-memory-revoke-purge-PASS.json')}。

源N正常HTTP删除中对一个准确Q文件注入一次PermissionError：墓碑真实提交，其他准确目标已删，该文件保留pending、总receipt deleted_pending，正文/operator/引用/gateway关闭。根58后续夹具带Origin读取旧资料接口被403，原FAIL保留；根59只核已成功子事实及正常无Origin已认证GET，不重做墓碑或故障注入。源N404、无关R200、续问409 result_invalidated及零新增动作成立，见{link(base/'F03-source-cleanup-failure-closed-PASS.json')}及{link(base/'F03-root58-successful-substeps-reconciled.json')}。

根59重开后原retry-cleanup实际409 operation_authority_unknown，暴露原Operation每进程域使cleanup无法恢复。没有放宽旧Operation或续活其票据：只对source_delete待清理态新增私有、限时、CAS的cleanup attempt；必须用真实PG回读同source/business/impact/revision墓碑才准清理，不能重新admit/tombstone或恢复Q批准；原execution/admission和completion事实留存。完成证明单独记录，GET不把旧进程执行权重生。命令078实际journal负例覆盖缺墓碑/错墓碑、域变化、超时、被新尝试替代及重复完成，原Operation旧票据仍被拒。根60正常HTTP对原job 20a5b68a-3e4d-432b-b979-ff661855326c恢复清理，receipt deleted/unconfirmed=0，所有目标Q正文已删、无重发/新准入/新费用，见{link(base/'F03-exact-cleanup-replay-and-retry-PASS.json')}和{link(base/'command-078.receipt.json')}。

gateway负例调用实际ControlledModelGateway并在admission前拒绝，没有为此另做完整native外发；实际API/operator/native worker/SUP/PG正例另见F04。记忆K2旧缺少即时before-financial快照的限制不由本轮倒填。

## TASK-121-F04：批准的联合时钟和不可逆失效

私有批准证书绑定UTC和同boot可比较的monotonic上下界，monotonic最长900s且不越原grant/活动截止；批准ID覆盖证书。旧无证书批准关闭。过期、UTC回退、推导漂移、未知/改变域在同一journal CAS内记录不可逆invalidated，UTC恢复也不再有效；取样在锁内，避免合法并发读颠倒观察顺序。投影、reference/check_reference、领取前沿用同一判定；真实已claim不重发。只在正常未领取入口显式创建新决定，不恢复旧决定。

真实Windows boot GUID和本地Python3.12 GetTickCount64时钟实现已核；072先误假定QPC而失败，073修正后通过，旧失败保留。原先7个实际QAuthority/ControlHub/锁/准确私有文件时钟案例通过，仅注入q_clock.sample；真实系统时钟未改。证书的1s UTC漂移余量用于取样/NTP差异，不能声称能识别任意微小回调，但900s单调期限不延长。boot GUID native查询是平台专用能力，未知/不支持则关闭，不承诺跨平台恒可用。Python时钟定义参见[time.monotonic](https://docs.python.org/3/library/time.html#time.monotonic)，本地实现以实测为准。

{link(base/'F04-clock-authorization-PASS.json')}保留合法幂等、见过期后回退、未投影期间monotonic过期、域不明/切换、UTC回退、同boot重开、claim零重发。根55另通过实际API准备→operator批准→原键继续→真实native worker/SUP→PG received，正向时钟钩子只给API和worker一致+2s样本，无系统调时、无真实供应商。该生产组合仅一次合成准入250000，不因后续夹具失败重做；见{link(base/'F04-real-API-operator-worker-normal-combination-PASS.json')}。

## TASK-121-F05：PG已领取事实独立于冻结snapshot

新增只读PG命令事实查询，实际status/launch_claimed/时间/effect/terminal与不可变请求snapshot分开。public projection、operator查看/批准、claim前检查看PG是否已消费；不把这些易变状态纳入snapshot去制造不等，也不让worker正常已开始路径误拒。

根57正常A3检索/问答准备并批准，真实claim_interview_launch事务COMMIT返回后才注入ACK丢失：PG已claimed，Q launch_claim/worker claim/007 admission尚无，冻结snapshot仍完全相等。立即GET consumed/can_continue=false，立即与时钟+901s续批均准确q_approval_consumed；2次GET及2次重复POST无新批准、费用或dispatch。原UNKNOWN/已扣reservation不退，见{link(base/'F05-PG-claimed-before-Q-claim-PASS.json')}。

## 分账、累计投入与停止

只在原精确源CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f内建2个获批新逻辑库，各attempt=1/object=1；没有新容器、卷或镜像。retrolume_task120_audit07_r02 OID24351，0次/0预扣；retrolume_task120_audit07_main OID25874，5次/1250000微单位合成预扣，A1=1/250000、A2=2/500000、A3=2/500000，5个007均received，running_reserved_seconds全0。不是实际付费。原旧四库、06源和恢复副本沿用原各自金融快照，未启动目标或在旧库做本轮业务，不跨实例相加为新额度。8个新批准已显式revoke，旧批准/UNKNOWN未重发，见{link(base/'financial-summary.json')}与{link(base/'new-only-approvals-explicitly-retired.json')}。

累计roots60/64、PGstarts61/64、API63/96、Browser14/16、build5/8、Native69/128、HTTP1520/10000；相对06新增roots9、PGstarts9、API8、Native5、HTTP61，Browser/build增0。容器/卷create尝试及对象均保持2/2。真实provider、实际费用、preview、Git均0。旧125条失败前缀原样保留，现{len(b['failures'])}条、增{len(b['failures'])-125}条，是控制/批次/诊断记录数，不是独立缺陷数；TASK117旧81另列。根52/53/55/56/57/58/59和072的FAIL保留，不把整根FAIL改绿，已完成子事实按检查点复用。

holding累计{b['runtime_holding_union_seconds']:.6f}s/21600，新增{b['runtime_holding_union_seconds']-b['audit_repair07']['old_holding']:.6f}s；旧wall上界50243.003003s未抹去，本轮前向cap72000。保存时含999最多60s及另留post-save只读60s的保守上界为{ceiling:.6f}s，999实际wall由父控制器收尾追加至唯一账，不和包内快照冒充最终值。实际人工总投入及等待/工作精确拆分仍UNKNOWN_NOT_ZERO。原96h截止不变；07 actual human receipt未知，按更早签发时间保守取业务门2026-10-21T12:29:21.021710Z、收尾门12:59:21.021710Z，没有重开时窗。见{link(base/'budget-summary.json')}。

根56触发512MiB API启动前内存门后已准确清场；用户恢复内存后继续，不降门限、不重启Docker。每根有限stage、准确资源身份、512进入/连续低于256清理门保留。根60最终source stopped/Pid0，restore目标从未07启动。079只读最终核705组PID/birth、153个Job、两个精确CID stopped/Pid0及55480/55481/18120无监听；该命令自身tree_empty/exit0，080文件检查tree_empty/exit0，最终999只文件保存的回执在包外。见{link(base/'final-stop-proof.json')}、{link(base/'command-079.receipt.json')}、{link(base/'command-080.receipt.json')}；999退出后以{link(base/'command-999.receipt.json')}核最后消费者，不以报告保存中active_command冒称已空。

## 身份、兼容及历史控制限制

本轮15个产品文件和15个夹具/测试文件有实际变化，31条注册中未改文件仍登记，preimage/hash及{link(base/'source.diff')}、{link(base/'fixture.diff')}均已保存。322条原审计身份引用（含重复）除已登记变化和唯一账外无漂移，7锁定规则、001—014、前端源码/dist及8个旧证据ZIP原字节保持。最终根60产品与as-run零差异。原55/57检查使用其真实当时hash；后续只增加权限管理拒绝及清理重开/完成凭据路径，精确可用preimage、q_roles原字节重建和范围映射在{link(base/'as-run-final-mapping.json')}，不把未保留的全部中间夹具字节宣称已归档。最终身份：{link(base/'final-file-identities.json')}。

原C01—C15只按TASK121已接受的子事实和限制继承；不重跑共同99→100、三ACK、全部UI/K2或完整业务。当前C02/C04/C06/C07/C14的受影响点仅以本轮对应F证据补齐供复核，C15仍待独审与主控。旧memory窗口没有即时before-financial的限制、旧05/06 bootstrap/控制不通过均保留。07持久bootstrap前已有2个有界只读批次，登记为次序偏差，不倒签为首工具前完成；未因此授权业务，实际接收未知按更早边界计时。原报告91351字节在本前缀后逐字节保存，全部旧事件和51根/125失败前缀保持。

尚待：原TASK-121仅增量核F01—F05及受影响兼容/锁/清理/worker，再由主控裁定；真实Q账户/官方适用性/readiness、原首次启用决定和72h起点另待。没有签STEP018整体、019/020、M-1、项目或发布完成，也没有以剩余额度扩测。完整限制见{link(base/'remaining-gaps.json')}。

---

以下为续作06及更早统一结果原字节（91351字节；SHA256 3d044a788f7354e9a3b1fec0f75bab100f182469dea42613d3112078cda67b03）。

'''
tmp=report.with_suffix('.tmp');tmp.write_bytes(prefix.encode('utf-8')+old);os.replace(tmp,report)
saved=report.read_bytes();assert saved.endswith(old) and saved[-len(old):]==old
assert read(EX/'budget.json')['roots'][:51]==prior['roots']
index={'task':'TASK-120','R':'R-114','scope':'续作07 five audit findings','permit_id':b['current_permit_id'],
    'engineering_complete':True,'stable_for_independent_delta_audit':True,'independent_audit':'PENDING_ORIGINAL_TASK121',
    'real_Q':'FROZEN','report':rel(report),'impact_matrix':'impact-matrix.json','final_identities':'final-file-identities.json',
    'source_diff':'source.diff','fixture_diff':'fixture.diff','as_run_mapping':'as-run-final-mapping.json',
    'inheritance':'inherited-evidence.json','compatibility_and_limits':'remaining-gaps.json','budget':'budget-summary.json',
    'financials':'financial-summary.json','final_stop':'final-stop-proof.json','stop_command_receipt':'command-079.receipt.json',
    'preparation_receipt':'command-080.receipt.json','final_filesystem_receipt':'command-999.receipt.json',
    'unique_current_ledger':['../budget.json','../events.jsonl'],'package':'final-review-candidate.zip',
    'package_identity':'candidate-package-identity.json','save_proof':'save-consistency.json',
    'final999_receipt_latest_ledger_package_identity_and_save_proof_external_to_archive':True,
    'old_report_suffix_bytes':91351,'old_eight_packages':'old-packages-preserved.json',
    'no_private_credentials_Q_body_or_usable_approval':True,'unused_caps_do_not_authorize_further_runtime':True}
write(HERE/'final-review-index.json',index)
pack={report}
pack.update(ROOT/x['path'] for x in identities['changes'])
excluded={'command-999.log','candidate-package-identity.json','save-consistency.json'}
for p in HERE.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.zip','.pyc') and p.name not in excluded:pack.add(p)
target=HERE/'final-review-candidate.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
    for p in sorted(pack):
        assert time.monotonic()-started<45
        name=rel(p);assert not name.startswith(('.runtime/','.git/')) and p.suffix!='.zip'
        archive.write(p,name)
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    for name in archive.namelist():assert not name.startswith(('.runtime/','.git/')) and not name.endswith('.zip')
package={'path':rel(target),'bytes':target.stat().st_size,'sha256':sha(target),'files':len(pack),
    'engineering_complete':True,'stable_for_original_TASK121_delta_audit':True,'independent_audit':'PENDING',
    'old_ZIPs_nested':0,'private_credentials_body_or_usable_approvals':False,
    'entry_identities':[{'path':rel(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(pack)],
    'final999_receipt_and_current_ledger':'External referenced authority, not frozen duplicate current state'}
write(HERE/'candidate-package-identity.json',package)
write(HERE/'save-consistency.json',{'utc':datetime.now(timezone.utc).isoformat(),'old_report_suffix_exact':True,
    'old_report_bytes':len(old),'old_report_sha256':hashlib.sha256(old).hexdigest(),'new_report_sha256':sha(report),
    'old_roots_failures_events_prefixes_exact':True,'eight_old_ZIPs_unchanged':True,'archive_CRC_ok':True,
    'final_source_identities_match':True,'source_stop_proof':'final-stop-proof.json','engineering_complete':True,
    'independent_audit':'PENDING_ORIGINAL_TASK121','real_Q':'FROZEN','save_seconds':time.monotonic()-started,
    'final999_close_receipt':'External; own consumer still running at save time, parent confirms after exit'})
print(json.dumps({'saved':str(report),'engineering_complete':True,'independent_audit':'PENDING_ORIGINAL_TASK121',
    'files':len(pack),'ZIP_bytes':target.stat().st_size,'ZIP_sha256':package['sha256'],'failure_records':len(b['failures'])}))
