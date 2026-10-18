"""维护终审回收、缺陷与账段裁定，发布同TASK的合并修复合同。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from decimal import Decimal
import hashlib,json,re
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=sha(b))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def encoded(s):return s.replace('\n','\r\n').encode('utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
r=load(OUT/'received.json');gap=load(OUT/'PG-hold-disposition.json')
budget_path=ROOT/'DocuN/evidence/TASK-111/execution/budget.json';budget=load(budget_path)
assert budget['active_batch'] is None and budget['counts']==r['current_counts'] and budget['time_seconds']==r['current_time_seconds']
assert r['max_existing_DEF']==30
audit_report=ROOT/'DocuN/results/TASK-112-result.md';report111=ROOT/'DocuN/results/TASK-111-result.md'
assert info(audit_report)==r['audit_report_current']
assert info(report111)['sha256']=='fcee65ac816c59e364f26c23d0feaec023b28a97b170e78785d16af19d4be5f4'
sources=load(ROOT/'DocuN/evidence/TASK-111/execution/continuation-06/final/source-identity.json')
for row in sources:assert info(ROOT/row['path'])==dict(bytes=row['bytes'],sha256=row['sha256'])
raw_events=[json.loads(x) for x in (ROOT/'DocuN/evidence/TASK-111/execution/events.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
root6=next(e for e in raw_events if e['event']==109)
assert root6['kind']=='batch_end' and root6['data']['kind']=='real' and root6['data']['number']==6 and root6['at_ns']==gap['root6_end_ns']
assert load(ROOT/'DocuN/evidence/TASK-111/execution/cleanup-resume-20261010/pg-stop.json')['end_ns']==gap['stop_confirmation_ns']
save('defect-disposition.json',dict(at=at,audit_task='TASK-112',audit_R='R-106',audit_dispatch='已返回',audit_delivery_acceptance='通过只读集中审计交付',G11_final='不通过关闭条件',
  defects=[dict(id='DEF-031',finding='F112-01',priority='P1',status='开放',owner='TASK-111',issue='迟到ready被成功Event分支接受'),
           dict(id='DEF-032',finding='F112-03',priority='P1',status='开放',owner='TASK-111',issue='stderr线程提前退出冒充真实EOF与退款门'),
           dict(id='DEF-033',finding='F112-02',priority='P2',status='开放',owner='TASK-111',issue='Node实际constraints类型与BOM原字节域不一致')],
  execution_issue='E112-01保守核销2279.703，不追认626.566旧超限',input_record_erratum='21条=17真实成功ACK+4个422拒绝，43PNG保留',
  existing_evidence='按112限域接受；不取消有效原件或重跑全部G11',next='同111工程窗三缺陷/账调整/定向证据合并；之后原112限域增量复核',
  no_model_brand_reaudit=True,no_parent_release=True))
caps=dict(budget['continuation_caps']);caps.update(real_batches=20,image_builds=9,preview_creates=55,preview_starts=51,PG_container_starts=16)
conservative=Decimal(gap['conservative_real_seconds']);assert conservative+Decimal('2400')<=Decimal('20400')
assert caps['preview_creates']-budget['counts']['preview_creates']==10 and caps['preview_starts']-budget['counts']['preview_starts']==10
save('continuation-budget.json',dict(at=at,TASK='TASK-111',R='R-105',permit='TASK-111-G11-C07-20261012',base_product_permit='TASK-111-G11-P110-20261010',
  current_counts=budget['counts'],current_time_seconds=budget['time_seconds'],pending_unique_adjustment='E112-01',conservative_real_baseline=str(conservative),historical_excess_not_forgiven=gap['historical_excess_seconds'],
  prior_caps=budget['continuation_caps'],cumulative_caps=caps,new_roots=[19,20],per_root_seconds=1800,new_real_limit_seconds=2400,cumulative_real_limit_seconds=20400,
  integrated_seconds=14400,prior_authorized_work_seconds=129600,cumulative_authorized_work_seconds=144000,cleanup_reserved_seconds=600,cleanup_cumulative_limit_seconds=1800,
  preview_names=[f'retrolume-task-111-g11-preview-{n:02d}' for n in range(56,66)],planned_base_cases='六到七个定向真实反例/对照，可合法组合减少',related_repair_slots='其余三到四个，全部最多10',
  cached_image_builds_added=2,PG_starts_added=2,main_browser_API_frontend_model_OneCall_added_planned=0,
  same_control_root=str(ROOT/'DocuN/evidence/TASK-111/execution/continuation-04/synthetic/control'),execution_budget_not_yet_mutated=True,new_dispatch_or_actual_use=0))
paths=['DocuN/tasks/TASK-111.md','DocuN/results/TASK-111-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD']
before={p:(ROOT/p).read_bytes() for p in paths}
assert sha(before[paths[0]])=='8881dfea5f9194a384cf3ae66fe3689fbdf54bf9f845421cce944249eda2bbc1'
assert max(int(x) for x in re.findall(rb'CHG-(\d+)',before[paths[-1]]))==1239
pre=OUT/'before-documents';pre.mkdir(exist_ok=False)
for p,b in before.items():(pre/p.replace('/','__')).write_bytes(b)
(OUT/'prior-TASK-111.md').write_bytes(before[paths[0]])
audit_decision=ROOT/'DocuN/results/TASK-112-work-decision.md';assert not audit_decision.exists()
audit_prefix=f'''# TASK-112 / R-106 集中终审回收裁定

{at}，Codex编排Agent。审计实际交付36048字节/ea51e0f4…、同一105源/七规则和225审计对象匹配；已知审计时长3347.3488145秒≤10800，首采样前准备unknown如实保留，业务运行0。独立checkpoint先于已披露接触，没有实现参与或产品写入证据；验收通过审计交付，不等于被审G11通过。

代码与关闭条件不通过。F112-01/P1登记DEF-031，F112-03/P1登记DEF-032，F112-02/P2登记DEF-033，均开放归原111工程窗。主控对照冻结成功wait、stderr溢出break/最后谓词和实际Node入口，接受静态确定触发；尚无该分支真实修正证据，不声称已发生逃逸或退款事故。已证方法按112限域、不同bundle/variant继续成立；Panel旧方法静态继承成立，不扩大BFCache等Must。

E112-01原root6结束事件109/869276343000000与精确PG stop871556046000000原件已独立核，保守持有2279.703秒，旧14546.863→16826.566，旧16200超626.566。原始运行前仍Running=true/Pid945为事实，物理停机瞬时未采/连续段按单PG无中间stop/start记录保守核销，不伪精确全面观测。历史偏差不追认，不抹有效测试，运行账由工程追加唯一adjustment。

O112-01措辞更正为21输入记录=17个成功ACK+4个422拒绝；43PNG原件不变。旧首采样/时钟/入账/pre/离线未捕获秒数和13元保留。正式共享源由主控维护，审计原文和225冻结原件不改。

同TASK111/R105 C07合并三缺陷、账核销及定向运行，明确新缓存image/load与前向预算；不重发正常Native、不重跑全部矩阵、不改回109。修复稳定后本112原隔离窗口仅增量核三缺陷、账和实际传导，现不恢复其旧剩余时窗或业务许可。G11/SEC003/B01/STEP/M1/项目/发布仍未通过。
'''
prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK-111 / R-105 112终审阻断与C07合并修复许可

{at}，Codex编排Agent。112集中终审真实返回36048字节/ea51e0f4…，审计交付验收通过；当前111候选仍不具备G11关闭条件。原105源/七规则及225审计结束身份一致，40精确对象当前metadata停止，active_batch null。主控没有运行产品/PG/测试/构建。

三个确定缺陷定向接受并登记：DEF-031/F112-01/P1为ready成功wait分支漏原8秒边界复核；DEF-032/F112-03/P1为stderr超8192 break或读异常退出冒EOF，完整确认/退款门不足；DEF-033/F112-02/P2为Node显式null域及BOM原字节规范差异。都开放归本111，不用Python先拒解释Node无需修。现成正常/资格/前端/不同故障范围按112限域保持，原先稳定候选不等于最终通过。

E112-01经原事件109与PG前检/stop原输出核，2279.703未计持有段保守纳入14546.863为16826.566，对旧16200超626.566。物理瞬时未采/连续持有有推断成分明确保留，运行账尚未被主控改写；工程须一次追加adjustment、保旧数/失败/历史超限。21条输入记录更正为17成功ACK+4拒绝，不改43PNG或历史原文。

前向签TASK-111-G11-C07-20261012沿原C06 A+工程窗口，待人工转交。综合14400秒，旧授权129600→144000，末600清场；新real≤2400/累计20400，基线按16826.566投影19226.566，历史626.566不免责。根18→20各1800；image7→9允许缓存构建/加载最多2；create45→55/start41→51各新10，name56—65；PG start14→16最多2。API/主browser/model/OneCall/frontend不加且计划新0，权限/并发/资源安全门保持。

优先Node实际renderer-protocol集中修null/BOM、保四runtime与编译包/SQL，镜像内容变动必须新load身份，不沿旧v2-07签新入口。SUP修真实完整ready与双EOF/有界排空，相关反例/正常对照一次制齐后真实合并，不重复正常两Native/32例/六故障。全场景仍C04唯一registry，旧25UNKNOWN/R60/count1及根blocked不动，新未知完整同根恢复否则停。

新的运行许可包括明确工程准备、相关验证/普通修正和精确清场，不包括权限/持久模型/数学语言/用户库/provider/Git/删除或发布。修正后仍由原112隔离窗口只复核缺陷和变化传播，非再次完整终审。旧C06完整卡保存本receipt/prior-TASK-111.md，唯一新合同DocuN/tasks/TASK-111.md；旧许可/caps/剩余不能自动开跑。

## 以下为C06及此前裁定原字节

''',
'DocuS/架构动态文档.MD':'''# 架构动态文档

文档v1.20，2026-10-12，Asia/Shanghai。需求v1.2、执行动态v2.42、task_model/07。以下v1.19历史保留；G11集中终审阻断，当前代码尚未修正。

## ready时窗、真实双EOF与Node入口尚有确定缺陷

DEF-031/P1：完整ready接收/成功wait分支没有原单调边界核，逾8秒可进ready。DEF-032/P1：stderr溢出break/读异常不是EOF，原最终确认谓词仍能把线程结束视为完整管道事实。DEF-033/P2：Node nullish默认与Python显式null域不符，解码移除BOM使canonical文本对照不足以判原字节。保持8秒/原D/完整StopProof/保守退款门及Python第一防线，修正目标仍原有限合同，无新的安全豁免。

优先在私有SUP补真实接收时刻/成功后复核和双EOF标志/有界排空，在实际Node protocol入口加强类型/原字节；固定四runtime/数学与SQL不扩大。Node宿主镜像变动要新load/真实入口证据，当前旧v2-07仍是未修版本。独立终审未通过不等于既有数学/图形/资格/Panel实际原件无效，具体继承按112限域。

生产HTML仍默认关闭，B01/SEC003/G11及父STEP未放行。E112-01只属历史资源持有核销，不当成产品故障复演；旧25UNKNOWN保留。C07是同范围三缺陷的合并修复/验证，之后112只增量复核，不重新设计109或重复完整矩阵。

## 以下为v1.19及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.42，2026-10-12，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.20、task_model/07。以下v2.41原历史保留。

## TASK112已返回，TASK111三缺陷合并修复待转交

{at}。TASK112/R106集中审计已真实完成并返回36048字节/ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522。调度已返回、审计交付验收通过；被审G11最终关闭条件不通过。105当前源/七规则一致，225结束身份/必要原件可复核；审计业务0、已观测3347.3488145秒、前采样准备unknown保留，未按型号标签重审已完成工作。

共享缺陷新登记开放：DEF-031/F112-01/P1，ready完整接收和成功等待分支时窗；DEF-032/F112-03/P1，stderr真实EOF及停止/退款门；DEF-033/F112-02/P2，Node constraints显式null与BOM原字节域。主控依据源码/独立静态反例接受确定缺陷，不称异常分支已经实机发生。现成数学/资格/前端/不同故障证据按112限域继承，17成功ACK+4个422为21输入记录，原43PNG不变，旧错误措辞历史保留但不再沿用。

执行控制E112-01已原件核销：root6结束869276343000000至精确PG停止确认871556046000000，保守2279.703漏记段；旧账14546.863修正基线16826.566，对旧16200超626.566，连续持有/物理停机瞬时不确定性如实保留。主控只保存裁定，运行budget仍原值，工程开工追加一次唯一adjustment；新许可不追认历史超限。旧离线215.358/cleanup77.2837405、首采样/pre/漏秒/超限/迟记/失败及13元不清。

当前计数根18、image7、PG14、API12、browser11、create45/start41、frontend4、model/OneCall9、HTTP1611/PNG182/public68/internal26，active_batch null；40精确对象只读当前Stopped/Pid0/restart0，两端口18111/55451无监听。原C06工程已结束，112审计也已结束，旧许可/残余额度不可复活。

TASK111/R105 C07合并卡已保存待人工转交，接收原C06 A+工程窗口，无自动派发/新实际运行。许可TASK-111-G11-C07-20261012：综合14400/末600清场，旧129600授权账前向增144000；新real≤2400/累计20400按16826.566基线，根最多20已18/单根1800；image最多9已7(缓存构建2余量)、PG16已14(2余量)、create55/start51已45/41(各10)，name56—65。API/主browser/model/OneCall/frontend及HTTP/并发不增，计划不重启主工作区/模型。准备源/真实反例/新load/两EOF与持久结算一张卡连续完成，不另派准备卡、不重跑两Native或整矩阵。

C07仍原C04唯一registry，旧25UNKNOWN/R60/count1和旧根blocked不动；新未知同根精确恢复，否则停依赖。完整新源码/镜像候选后原112 A+独立窗口只复核三缺陷/E112-01/实际传播；不在本次提前恢复其旧审计时窗或自动派增量卡。G11/SEC003/B01/STEP/M1/项目/发布都未通过，公共原文和原始需求不改。

本次CHG1240—1252，下一1253。回收/缺陷/保守账/预算/合同在TASK111/orchestration-receipt-08，审计裁定DocuN/results/TASK-112-work-decision.md；唯一现行工程卡DocuN/tasks/TASK-111.md，旧C06原字节存prior-TASK-111.md。主控只有读取/hash/精确metadata与文档维护，产品/SQL/测试/构建0。

## 以下为v2.41及更早历史

'''}
draft=(OUT/'effective-contract.md').read_bytes();assert len(draft)>12000 and b'*' not in draft
(ROOT/'DocuS/执行动态文档.MD').write_bytes(encoded(f'# 执行动态文档\n\n{at}，TASK111/R105 C07已登记保存中，TASK112已回收，非新派发。\n\n')+before['DocuS/执行动态文档.MD'])
(ROOT/'DocuN/tasks/TASK-111.md').write_bytes(draft)
audit_decision.write_bytes(encoded(audit_prefix))
for rel,prefix in prefixes.items():(ROOT/rel).write_bytes(encoded(prefix)+before[rel])
save('window-assignment.json',dict(at=at,TASK='TASK-111',R='R-105',permit='TASK-111-G11-C07-20261012',resource='A+原续作06工程窗口',contract=str(ROOT/'DocuN/tasks/TASK-111.md'),contract_sha256=sha(draft),status='待人工转交',actual_dispatch=False,parallel=False,independent_auditor=False,followup_audit='原TASK112窗口缺陷/账/实际影响增量复核，当前未派发'))
entries=[
 ('DocuN/evidence/TASK-111/orchestration-receipt-08/receive.py','publish.py只核报告/冻结源/精确metadata/原事件及维护文档，零产品运行。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-08/received.json','112真实终审已回收，105源/七规则/225审计冻结匹配。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-08/PG-hold-disposition.json','E112-01保守补2279.703为16826.566，626.566历史超限不追认。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-08/resource-recheck.json','40精确metadata停止及ports-recheck.json无监听，非旧UNKNOWN补证。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-08/defect-disposition.json','DEF031/032/033开放归111、ACK措辞更正，G11关闭未过。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-08/continuation-budget.json','三缺陷合并/缓存镜像/定向真实链成套前向额度，原账只读保留。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-08/prior-TASK-111.md','C06旧完整卡原字节保存，window-assignment记录C07同窗待转交。'),
 ('DocuN/results/TASK-112-work-decision.md','审计交付通过、被审代码不通过及缺陷/预算裁定。'),
 ('DocuN/results/TASK-111-work-decision.md','C07合并修复许可及112限域后续复核，不重走完整终审。'),
 ('DocuN/tasks/TASK-111.md','现行完整C07工程合同，原111窗口连续修正验证。'),
 ('DocuS/架构动态文档.MD','v1.20确定ready/双EOF/Node入口缺陷开放，尚未修正。'),
 ('DocuS/执行动态文档.MD','v2.42唯一账：112已返回/111 C07待转交，DEF与历史账不清。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-08/delivery-proof.json','一次合同/历史/原源结果/预算保护与成套余量检查。')]
chgs=''.join(f'\n- CHG-{1240+i}，{at}，Codex编排Agent，{rel}。{note}\n' for i,(rel,note) in enumerate(entries))
(ROOT/'DocuS/文档变更记录.MD').write_bytes(before['DocuS/文档变更记录.MD']+encoded(chgs))
assert (ROOT/'DocuN/tasks/TASK-111.md').read_bytes()==draft and (OUT/'prior-TASK-111.md').read_bytes()==before[paths[0]]
for rel in prefixes:assert (ROOT/rel).read_bytes().endswith(before[rel])
for row in sources:assert info(ROOT/row['path'])==dict(bytes=row['bytes'],sha256=row['sha256'])
assert info(audit_report)==r['audit_report_current'] and info(report111)['sha256']=='fcee65ac816c59e364f26c23d0feaec023b28a97b170e78785d16af19d4be5f4'
assert load(budget_path)==budget
save('delivery-proof.json',dict(at=at,TASK='TASK-111',R='R-105',contract=info(ROOT/'DocuN/tasks/TASK-111.md'),old_contract_preserved=True,shared_old_suffixes_preserved=True,source111_unchanged=105,reports111_112_unchanged=True,execution_budget_unchanged=True,pending_ledger_adjustment='E112-01 once',caps_forward=caps,business_operations=0,actual_dispatch=False,CHG_first=1240,CHG_last=1252,next_CHG=1253))
print(json.dumps(dict(card_saved=True,TASK='TASK-111',R='R-105',bytes=len(draft),sha256=sha(draft),architecture='v1.20',execution='v2.42',DEF_open=['031','032','033'],conservative_real='16826.566',CHG='1240—1252',status='待人工转交',source_reports_budget_unchanged=True),ensure_ascii=False))
