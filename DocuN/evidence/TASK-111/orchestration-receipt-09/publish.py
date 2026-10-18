"""保存C07限定回收与112同窗增量合同；不改产品/执行账/结果原文。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from decimal import Decimal
import hashlib,json,re
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
REVIEW=ROOT/'DocuN/evidence/TASK-112/orchestration-review01-20261012'
C07=ROOT/'DocuN/evidence/TASK-111/execution/continuation-07'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=sha(b))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def encoded(s):return s.replace('\n','\r\n').encode('utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat();r=load(OUT/'received.json')
budget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
assert budget['active_batch'] is None and budget['counts']==r['counts'] and budget['time_seconds']==r['time_seconds']
assert info(ROOT/'DocuN/results/TASK-111-result.md')['sha256']==r['result']['sha256']
assert info(ROOT/'DocuN/results/TASK-112-result.md')==r['audit112_report_unchanged']
sources=r['sources']
for s in sources:assert info(ROOT/s['path'])==dict(bytes=s['bytes'],sha256=s['sha256'])
prior_audit=load(ROOT/'DocuN/evidence/TASK-112/audit-20261011/delivery-receipt.json')
used=Decimal(str(prior_audit['observed_seconds_since_first_clock']));cap=Decimal('10800');window=Decimal('7200')
assert used+window<=cap
save(OUT/'candidate-disposition.json',dict(at=at,TASK='TASK-111',R='R-105',dispatch='已返回',acceptance='部分通过，三缺陷候选修复及必要证据已回收，最终关闭待112增量独审',
  DEF_031='候选修复/离线6样本/真实迟到及及时对照待复核',DEF_032='候选真实双EOF/异常保R及同根恢复待复核',DEF_033='候选Node实际入口/新load与真实wire待复核',E112_01='唯一2279.703已入账；历史626.566保留，待独立核销确认',
  sources_matched=112,evidence_files_matched=255,new_lifecycles=7,selected_methods=6,new_real_seconds='168.657',new_image='sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789',
  old112_scope_preserved=True,old_unknown25_kept=True,no_parent_release=True,engineering_frozen=True,main_business_runs=0))
paths=['DocuN/tasks/TASK-112.md','DocuN/results/TASK-111-work-decision.md','DocuN/results/TASK-112-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD']
before={p:(ROOT/p).read_bytes() for p in paths}
assert sha(before[paths[0]])=='fc341b4225e8353687b78de7118f9763899dcccb901fdee93d9637321d6a2fdf'
assert max(int(x) for x in re.findall(rb'CHG-(\d+)',before[paths[-1]]))==1252
pre=OUT/'before-documents';pre.mkdir(exist_ok=False)
for p,b in before.items():(pre/p.replace('/','__')).write_bytes(b)
(OUT/'prior-TASK-112.md').write_bytes(before[paths[0]])
draft=(OUT/'TASK-112-review-01-contract.md').read_bytes();assert len(draft)>8500 and b'*' not in draft
# 先登记接续保存中，再写现行合同，完成后标待转交。
(ROOT/'DocuS/执行动态文档.MD').write_bytes(encoded(f'# 执行动态文档\n\n{at}，TASK112/R106 review01已登记保存中，111 C07已返回，尚未派发增量审计。\n\n')+before['DocuS/执行动态文档.MD'])
REVIEW.mkdir(parents=True,exist_ok=False)
primary=['DocuN/results/TASK-112-result.md','DocuN/evidence/TASK-112/audit-20261011/static-counterexamples.json','DocuN/evidence/TASK-112/audit-20261011/execution-budget-independent.json','DocuN/evidence/TASK-112/orchestration-20261011/frozen-inputs.json','DocuN/evidence/v4-migration-20260930/rules-snapshot.json']
indexes=['final/source-identity.json','final/change-index.json','final/case-index.json','final/stop-index.json','final/sessions-final.json','final/load-manifest-verification.json','final/budget-final.json','final/exact-resources-final.json','final/old-unknown-kept.json','final/ports-final.json','E112-01-adjustment.json','timing.json','accepted.json','offline-01/ready/ready-offline-result.json','offline-01/stderr/stderr-offline-result.json','offline-02-node/node/node-host-result.json','offline-02-node/node/python-domain-result.json']
evidence=load(C07/'final/evidence-manifest.json')['entries']
freeze=dict(at=at,TASK='TASK-112',R='R-106',review='review-01',purpose='原始差异/身份/原件导航，判断由原独立窗口形成',
  sources=[dict(path=str(ROOT/s['path']),relative_path=s['path'],bytes=s['bytes'],sha256=s['sha256']) for s in sources],
  primary_inputs=[dict(path=str(ROOT/p),**info(ROOT/p)) for p in primary],rule_sources=r['rules'],
  evidence_indexes=[dict(path=str(C07/p),**info(C07/p)) for p in indexes],C07_evidence=evidence,
  omitted_implementation_self_eval=True,new_business_operations_authorized=0)
save(REVIEW/'frozen-inputs.json',freeze)
save(REVIEW/'review-budget.json',dict(at=at,permit='TASK-112-G11-REVIEW01-20261012',prior_observed_seconds=str(used),prior_preclock_unknown_preserved=True,observed_total_cap=str(cap),observed_remaining=str(cap-used),new_window_seconds=str(window),max_observed_projection=str(used+window),new_clock_anchor_required=True,business_runs=0,new_audit_NOT_started=True,old_window_not_restored=True))
(ROOT/'DocuN/tasks/TASK-112.md').write_bytes(draft)
prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK-111 / R-105 C07回收与112限域增量复核

{at}，Codex编排Agent。C07真实交回164196字节/51b4311e…，原146608字节后缀完整；112当前源/七规则及255工程证据逐项字节一致，六采用方法/七生命周期有原件，47精确对象当前Stopped/Pid0/restart0，active_batch null。工程已返回，验收部分通过；三个DEF尚不由主控按自评关闭，交原112独立窗口复核。

产品实际仅SUP/pipe/Node protocol三处，差异对应完整ready时刻与成功后门、真实双EOF/异常/退款门、constraints显式类型及原UTF8 canonical字节。新v2-08 image ec3c70c7…/load8a047050…，四runtime/数学/SQL/前端不变。真实迟到8.063拒ready/输入，正常78.4 ACK/PNG与BOM拒绝合用；stderr12289只捕获8192且真实排空，未EOF先R60/禁start后被动真实EOF同根满R恢复。首个closed夹具失败保留，root20只修该接口复验，不能把旧五方法原件追成新版重新跑。

E112-01已唯一事件3508和预算execution_time_adjustments生效一次，2279.703使14546.863→16826.566，旧626.566超限仍保留；新增168.657使累计16995.223。工程根20/PG16到限，image8、create52/start48、internal30，其余费用/模型/公开HTTP/主browser/前端没有新增。旧unknown25、失败/pre/时钟/13元不清；C07自减300秒及首采样缺口留给真实控制判断，不冒精确首读。

原111工程到回传终点，当前冻结，无新工程许可。签TASK112/R106 review01，同原A+独立窗口，限三缺陷/E112-01/新image与真实变化传导，不完整终审第二轮。零业务运行；新实际接收固化7200秒，原已观测3347.3488145/10800不清，原观测余额7452.6511855、最大投影10547.3488145，原准备unknown仍单列。当前待人工转交，未自动派发/开始。

旧112原完整卡已保存本receipt/prior-TASK-112.md，完整新卡DocuN/tasks/TASK-112.md；原112结果ea51e0f4…及原111报告/运行账/112源都不改。独立通过才可由主控裁定G11有限关闭，B01/SEC003/STEP/M1/项目发布仍不预签。主控产品/SQL/测试/构建0。

## 以下为C07及更早裁定原字节

''',
'DocuN/results/TASK-112-work-decision.md':f'''# TASK-112 / R-106 review01接续许可

{at}，Codex编排Agent。111 C07已真实回收/冻结，112原集中审计结果36048字节/ea51e0f4…未改，其三缺陷与账段关闭结论仍未更新。三个产品修正与原112冻结基线可用pre/diff/post核，六定向方法及七生命周期真实原件已保存；候选不直接签缺陷关闭。

正式复用原112 A+独立审计窗口，不沿111实施窗，不重新完整审计。只review DEF031/F11201、DEF032/F11203、DEF033/F11202、E11201和新镜像/私有pipe/真实传导；原112的Panel版本继承、其它M项限域和旧观察保留。候选资料为原始diff/hash/流/Job/DB/计时原件，不以111结果自评或主控核证作独立通过依据。

许可TASK-112-G11-REVIEW01-20261012，本轮7200秒从首个实际接收工具UTC/mono固定，旧已观测3347.3488145/10800保留，观测累计最多10547.3488145，未知准备不编造。旧审计时窗已结束不恢复；任何产品运行/PG/Job/Docker/browser/模型/test/build额度0。结果在原112路径置顶review01保留旧36048字节，新证据review-01-20261012。

现行合同已保存/复读待人工转交，原窗口身份/独立性由执行者如实披露；不能据主控“原窗口”安排声称已用工具核chat ID。没有自动dispatch或审计开始事实。复核通过后主控验收关闭有限G11；未通过给具体剩余和实际影响，不机械再跑整链。旧历史超限/13元/未知全部保持。

## 以下为首轮终审裁定原字节

''',
'DocuS/架构动态文档.MD':'''# 架构动态文档

文档v1.21，2026-10-12，Asia/Shanghai。需求v1.2、执行动态v2.43、task_model/07。以下v1.20历史保留；三缺陷候选修正已交付，独立增量复核待。

## 完整ready门、双EOF门与Node入口候选已补

当前SUP记录完整ready单调接收与接受时刻，成功wait后复核原8秒/D-10/stop；迟到仍留kernel供物理清场。stdout与stderr实际EOF和读异常分开，stderr超8192有限保留并排空，实际双EOF/无读异常及原StopProof才能持久结算。PipeReadError区分IO失败，私有证据不授公开退款。DEF031/032只为候选修正，尚待原112关闭判断。

Node实际protocol入口要求存在constraints为数组并对原UTF8 canonical字节一致性核验，显式null/BOM拒绝，内部U+FEFF不删除；Python、固定四runtime/数学/编译包/SQL不变。新v2-08 image sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789/load8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f有实际加载与管道原件。DEF033独立增量待审，不沿v2-07身份追签新程序。

其余前端、资格/预算、012/ACL/角色、旧四账/worker与隔离规范未改，旧充分证据按112限域继承。E11201历史核销不更改产品合同，旧25UNKNOWN/R60不补造。生产HTML仍默认关闭，G11/SEC003/B01/父STEP未最终放行；只做问题及真实传导增量复核，无新Must/自由脚本/用户库/provider/发布权限。

## 以下为v1.20及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.43，2026-10-12，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.21、task_model/07。以下v2.42原历史保留。

## 111 C07已返回，112 review01待人工转交

{at}。TASK111/R105续作07真实交回164196字节/51b4311ec743876bae0f16cc71427cc17e093dcb4db50ae009170865366684cf，112源/七规则和255证据字节匹配，146608旧后缀原样。调度已返回、验收部分通过；实现三缺陷修正候选和必要证据已完成，DEF031/032/033保持“候选修复待独立关闭”，不能用工程自评签G11。原TASK112/R106首轮结果ea51e0f4…未改。

真实迟到8.063拒ready/输入，及时ready/78.4实际ACK及PNG与新BOM header拒绝合用；stderr12289捕获8192且真实排空，未EOF真实异常先cleanup_unconfirmed/R60/禁start，独立双EOF后同根满R恢复；null/BOM body实际Node拒绝。六采用方法包括一个预期UNKNOWN/恢复方法，七生命周期含首closed接口失败及复验，不把阴性反例叫正常成功。旧正常/数学/资格/前端和不同故障按112已有范围继承，未全量重跑。

E11201唯一事件3508/预算一次核销2279.703：14546.863→16826.566，旧16200超626.566保留；本C07新增real168.657，累计16995.223/20400、offline216.451/cleanup81.7987405。根20/20、PG16/16到限，image8/9、create52/55/start48/51，name56—62用/63—65未用；API12/browser11、model/OneCall9、frontend4、HTTP1611/PNG182/public68不增，internal30，offline分组34。旧所有失败/超限/迟记/pre/首采样/离线漏秒和13元不清，300秒收紧不冒精确首读。

预算active_batch null，47登记Docker对象当前Stopped/Pid0/restart0，两端口18111/55451无监听，七新持久行均stopped，未EOF两行满R60；旧25UNKNOWN/R60/count1及旧根blocked不动。111工程到回传终点重新冻结，当前无新root/PG/build/preview运行许可，剩秒/计数可读不恢复执行。主控产品/PG/测试/build0。

TASK112/R106 review01正式登记并保存，状态待人工转交、验收未裁定、实际dispatch/开始0。接收原A+独立112集中审计窗口，未参与111修复，不用新完整终审替代增量；范围仅三缺陷/E11201/新image与实际pipe/夹具传导。零业务/PG/Docker/browser/model/test/build，7200秒前向窗口用原已观测审计余额7452.6511855，原3347.3488145/10800不清，最大投影10547.3488145；未知准备继续单列，旧已结束时窗不恢复。

完整卡DocuN/tasks/TASK-112.md，旧首轮卡原字节存TASK111/orchestration-receipt-09/prior-TASK-112.md。新冻结输入/预算DocuN/evidence/TASK-112/orchestration-review01-20261012，预期原112结果置顶review01、新证据review-01-20261012。旧112独立结论与观察直接复用，真正缺陷/证据判定由该窗口形成。增量通过后主控裁定批准有限G11，不预签STEP/M1/项目/发布。

本批CHG1253—1265，下一1266。回收/精确metadata/候选裁定在TASK111/orchestration-receipt-09；正式共享状态只由主控维护，公共规则/原始需求及111/112结果原件和运行预算未改。

## 以下为v2.42及更早历史

'''}
for rel,prefix in prefixes.items():(ROOT/rel).write_bytes(encoded(prefix)+before[rel])
save(REVIEW/'window-assignment.json',dict(at=at,TASK='TASK-112',R='R-106',review='review-01',permit='TASK-112-G11-REVIEW01-20261012',resource='A+原集中终审独立窗口',status='待人工转交',actual_dispatch=False,parallel=False,independent=True,business_runs=0,old_engineering_frozen=True,contract=str(ROOT/'DocuN/tasks/TASK-112.md'),contract_sha256=sha(draft)))
entries=[
 ('DocuN/evidence/TASK-111/orchestration-receipt-09/receive.py','publish.py只核原件/hash/精确metadata及维护文档，不执行产品。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-09/received.json','112当前源/七规则/255原件及六方法/七生命周期和唯一账事件核证。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-09/resource-recheck.json','47精确metadata停止，ports-recheck两端口无监听，非旧UNKNOWN补证。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-09/candidate-disposition.json','三缺陷候选及E11201一次核销已回收，独立关闭待。'),
 ('DocuN/evidence/TASK-112/orchestration-review01-20261012/frozen-inputs.json','新112对象/255证据身份导航，不先馈工程自评。'),
 ('DocuN/evidence/TASK-112/orchestration-review01-20261012/review-budget.json','已观测旧3347.3488145/10800保留，新7200只读窗口，unknown不编造。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-09/prior-TASK-112.md','旧首轮独审卡原字节保存，新同窗增量安排待人工转交。'),
 ('DocuN/results/TASK-112-work-decision.md','原112窗口三缺陷/账/实际影响增量许可，不重新完整终审。'),
 ('DocuN/results/TASK-111-work-decision.md','C07限定工程回收/冻结，原112复核前不签父关闭。'),
 ('DocuN/tasks/TASK-112.md','现行review01完整合同，零业务运行，同原独立窗口。'),
 ('DocuS/架构动态文档.MD','v1.21候选ready/双EOF/Node门与新v2-08身份，待独审。'),
 ('DocuS/执行动态文档.MD','v2.43唯一账，111已回/112增量待转交，历史用量不清。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-09/delivery-proof.json','一次文档/路径/旧字节/源结果/预算及增量时限检查。')]
changes=''.join(f'\n- CHG-{1253+i}，{at}，Codex编排Agent，{rel}。{note}\n' for i,(rel,note) in enumerate(entries))
(ROOT/'DocuS/文档变更记录.MD').write_bytes(before['DocuS/文档变更记录.MD']+encoded(changes))
assert (ROOT/'DocuN/tasks/TASK-112.md').read_bytes()==draft and (OUT/'prior-TASK-112.md').read_bytes()==before[paths[0]]
for rel in prefixes:assert (ROOT/rel).read_bytes().endswith(before[rel])
for s in sources:assert info(ROOT/s['path'])==dict(bytes=s['bytes'],sha256=s['sha256'])
assert info(ROOT/'DocuN/results/TASK-111-result.md')['sha256']==r['result']['sha256']
assert info(ROOT/'DocuN/results/TASK-112-result.md')==r['audit112_report_unchanged']
assert load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')==budget
save(OUT/'delivery-proof.json',dict(at=at,contract=info(ROOT/'DocuN/tasks/TASK-112.md'),old112_card_preserved=True,shared_history_preserved=True,sources_unchanged=112,reports111_112_unchanged=True,execution_budget_unchanged=True,observed_audit_projection=str(used+window),audit_total_cap=str(cap),main_business_runs=0,actual_dispatch=False,CHG_first=1253,CHG_last=1265,next_CHG=1266))
print(json.dumps(dict(task='TASK-112',R='R-106',review='review-01',contract_bytes=len(draft),contract_sha256=sha(draft),architecture='v1.21',execution='v2.43',CHG='1253—1265',status='待人工转交',source_reports_budget_unchanged=True),ensure_ascii=False))
