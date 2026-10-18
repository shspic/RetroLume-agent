"""正式关闭G11有限成果并登记STEP017只读设计卡，保全旧报告/源/账。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
NEXT=ROOT/'DocuN/evidence/TASK-113/orchestration-20261012'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=sha(b))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def encoded(s):return s.replace('\n','\r\n').encode('utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat();r=load(OUT/'received.json')
budget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json');assert budget['active_batch'] is None
assert budget['counts']==r['current_counts'] and budget['time_seconds']==r['current_time_seconds']
assert info(ROOT/'DocuN/results/TASK-111-result.md')==r['engineering_report']
assert info(ROOT/'DocuN/results/TASK-112-result.md')==dict(bytes=r['audit_receipt']['report']['bytes'],sha256=r['audit_receipt']['report']['sha256'])
for s in r['sources']:assert info(ROOT/s['path'])==dict(bytes=s['bytes'],sha256=s['sha256'])
assert not (ROOT/'DocuN/tasks/TASK-113.md').exists() and not (ROOT/'DocuN/results/TASK-113-result.md').exists()
paths=['DocuN/results/TASK-111-work-decision.md','DocuN/results/TASK-112-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD']
before={p:(ROOT/p).read_bytes() for p in paths};assert max(int(x) for x in re.findall(rb'CHG-(\d+)',before[paths[-1]]))==1265
pre=OUT/'before-documents';pre.mkdir(exist_ok=False)
for p,b in before.items():(pre/p.replace('/','__')).write_bytes(b)
final=ROOT/'DocuN/results/TASK-111-G11-final-acceptance.md';assert not final.exists()
acceptance=f'''# TASK-111 / TASK-112 — G11已采用有限切片最终验收

{at}，Codex编排Agent。验收依据为用户已采用G11-P110、当前工程C07、112首轮集中终审及review01独立增量原件。正式裁定TASK111/R105工程交付与TASK112/R106审计交付通过，批准的G11有限切片验收关闭。STEP015/016更新为已采用Windows有限切片已完成/限域已验证；B01在该已采用方案下的宿主阻断解除，SEC003对应有限宿主验收门已通过，不签完整MVP/项目/发布。

终审结果53403字节/SHA1dab1126aa72e335288d037baed5bc13b7cfdc1e4a386b6c04553e630f871571，旧36048字节原后缀保留。379审计结束对象、12份关键审计原件、当前112源和七锁定规则相符；原工程164196字节/51b4311e…与对应255份原件索引保持。主控只读/hash/精确metadata，不执行产品/SQL/测试/构建。

DEF031/F11201、DEF032/F11203、DEF033/F11202按独立代码与对应反例/对照关闭。完整ready接受与收到事实分开、原8秒/D-10/stop时窗保持；stdout/stderr真实EOF和读异常不被线程退出替代，未确认先保R/禁start、独立真实EOF后同根满R恢复；Node实际constraints类型/原UTF8 canonical入口收紧，Python和固定四runtime不变。新v2-08 image sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789，load8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f，651资源由独审逐项核；实际新宿主/管道/正常78.4与PNG对照成立。

原两Native/UI、数学/图形、描述/协议/预算/事务/资格、不同忙死与监督故障、Panel两版的限定继承按首轮及增量结论接受，不追称全在最终版重跑。21条公开输入记录为17个成功ACK+4个422，43PNG原件保留。自由HTML/JS执行后所有导航事前原生同步否决不是现采用合同；旧109 hash反证仍FAIL，不改成通过。固定有限数据/程序及其限定真实输入不因此成为任意脚本或所有浏览器安全保证。

E11201漏记2279.703秒已唯一核销，14546.863→16826.566，旧16200超626.566保留、不追认。C07新增168.657，当前real16995.223/前向20400；旧首读/pre/迟记/漏秒/失败/13元及历史整体控制偏差始终保留。接受有效产品证据和本次前向账/计数/清场，不签历史整体合规为通过。

当前47登记容器精确metadata已停止/Pid0/restart0，active_batch null；七新持久终态及真正流/Job/Linux证明由独审核，主控metadata不替代StopProof。旧25/542b0750-6e02-418a-b216-5dfbd3b93047仍UNKNOWN/R60/count1、旧根blocked，不能凭本次关闭补旧kernel/EOF或退款。111/112执行许可到此结束，任何未用秒数/构建/名字/模型额度不恢复运行。

通过范围为已采用G11-P110、本Windows单人本地目标、合成资料与受控服务替身、固定有限描述/程序/输入及现有故障模型。真实provider质量/本人开放任务、全部Must/完整向量/数据退出恢复/整链Compose/权限预算综合验收/自用交接/完整Linux部署仍有对应后续门。生产能力实际配置、用户库/资料/真实付费/安装/发布未因验收自动启用或授权；未知与运行限制继续失败关闭。

下一项按原路线是STEP017数据退出、备份恢复与删除一致性。TASK113/R107只读交唯一完整实施合同，原件/关系/记录可独立解读、恢复保账/不重发及删除影响必须先收敛。设计后由主控据具体变化判断必要采用/权限门并另卡实施，不复跑G11、不重新设计109、不把设计交付说成备份已验证。
'''
final.write_bytes(encoded(acceptance))
draft=(NEXT/'effective-contract.md').read_bytes();assert len(draft)>10000 and b'*' not in draft
# 先占新编号，再落正式卡与完整待转交状态。
(ROOT/'DocuS/执行动态文档.MD').write_bytes(encoded(f'# 执行动态文档\n\n{at}，G11有限验收已关闭，TASK113/R107设计已登记保存中，尚未实际派发。\n\n')+before['DocuS/执行动态文档.MD'])
(ROOT/'DocuN/tasks/TASK-113.md').write_bytes(draft)
next_decision=ROOT/'DocuN/results/TASK-113-work-decision.md';assert not next_decision.exists()
next_decision.write_bytes(encoded(f'''# TASK-113 / R-107 STEP017设计许可

{at}，Codex编排Agent。G11已采用有限切片经111/112当前独立原件正式验收关闭，沿原执行路线进入STEP017/MOD008/FLOW007/API005。授权终点为数据退出/备份恢复/删除一致性唯一完整A—D合同及一次文档核对，非当前实现/新数据权限。

接收A+，优先原111已结束工程窗口，真实仓储/预算恢复上下文可复用，112审计窗保持隔离；容量/可用性不足可换新A+设计窗按最小输入恢复，不要求用户重述，不派子Agent。当前TASK113待人工转交，未自动dispatch/接收/开始；只读10800秒从实际接收工具采钟固定，产品/SQL/PG/Docker/浏览器/model/build/费用/删除/Git写全0，原111/112失败/预算/unknown不清也不恢复。

合同须给当前表/文件/权限关系、可独立解读导出与可恢复备份的区分、一致快照/安全发布/隔离副本恢复、原账/UNKNOWN/owner不复活、删除及旧备份影响、实际拟文件/签名/格式和未来最小真实矩阵。没有的向量/Redis/恢复模块不冒已存在，不为角色/模型变动先运行实验。真实必要采用变化收敛成具体推荐包，无新关键决定则不得人为新增审批。

结果将存DocuN/results/TASK-113-result.md，当前尚未产生。共享状态、正式文档/必要采用与下一实施许可由主控维护；设计不自签STEP017已实现/项目完成。用户库/数据/私有配置/凭据不读取，公共库与原始需求不改。
'''))
prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK111/R105及G11有限切片正式验收关闭

{at}，Codex编排Agent。依据112首轮+review01、C07真实修正与版本原件，验收通过并关闭TASK111工程、TASK112审计交付及已采用G11有限切片；DEF031/032/033关闭，E11201一次核销关闭其缺口但保626.566历史超限。正式裁定在TASK-111-G11-final-acceptance.md，原111/112结果不改。

当前112源/七规则相符、审计379对象/12关键文件可复核、47精确metadata停止。新v2-08/load及固定四runtime真实绑定，及时/迟到、超限/未EOF、null/BOM原件与首轮限域继承充分；没有新阻断。旧unknown25/R60/count1不解封/不退款，不改109反证或历史Fail，历史整体执行合规不签通过。所有111运行和112审计许可已结束，余量不恢复。

STEP015/016在已采用Windows有限范围已完成/限域已验证，B01在该方案下障碍解除/SEC003对应门通过；不签全部STEP/M1/项目/provider或部署。生产默认配置不由本主控启用。下一TASK113/R107沿STEP017只读设计完整数据退出/备份恢复与删除一致性合同，待人工转交A+原工程窗，0产品操作；不是再做HTML或抢执行层任务。

## 以下为增量接续及此前裁定原字节

''',
'DocuN/results/TASK-112-work-decision.md':f'''# TASK112/R106 review01回收与G11关闭裁定

{at}，Codex编排Agent。review01结果53403字节/1dab1126…、旧36048后缀保留，379结束对象/当前112源/七规则及12关键原件吻合。审计交付验收通过，代码/对应证据三缺陷关闭、E11201唯一核销成立，当前G11有限切片具备正式关闭条件，主控已据原件签TASK-111-G11-final-acceptance.md。

本轮已观测2305.839869秒、累计5653.1886835/10800，0业务运行，未知准备不编造；同原窗口未参与修复、checkpoint与原件顺序/触面披露成立，不按型号重审。所有审计许可结束，旧剩余额度不复活。当前没有再派完整或增量审计的阻断理由，历史控制偏差/626.566及旧unknown照常保留，不冒历史整体合规。

STEP017是下一独立数据生命周期成果，其稳定点审计归后续实际影响，不把112窗混用成新设计/实施者。该窗口无需继续G11核查，若后续已验收对象真有新缺陷另按新范围关联，不造重复门。

## 以下为review01接续及首轮裁定原字节

''',
'DocuS/架构动态文档.MD':'''# 架构动态文档

文档v1.22，2026-10-12，Asia/Shanghai。需求v1.2、执行动态v2.44、task_model/07。以下v1.21历史保留；G11已采用有限切片通过关闭。

## G11有限宿主/完整接线及独立门已闭合

严格有限描述/数据编译和固定程序、来源/父/记忆资格、同COMMIT产物/旧账、持久preview预算、可信UI/画面/有限输入与外部精确停止已完成当前范围验收。SUP ready时刻/原8秒门、实际双EOF/异常不退款、Node constraints/null/BOM实际入口修正经112增量确认，DEF031—033关闭。当前生产候选image sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789/load8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f；四runtime集合6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597保持。

STEP015/016按已采用Windows有限切片已完成/限域已验证，B01具体宿主障碍解除、SEC003相应有限验收门通过。固定程序能力边界不是任意已执行脚本全导航事前同步否决，109旧hash反证不改。真实provider/跨浏览器/用户开放任务及完整Must/M1/项目/发布不外推；实际启用仍需要有效配置，本主控不启能力。

旧unknown25保R60/一次使用与根blocked，E11201保守2279.703已入账/历史626.566超限不追认，StopProof不凭当前metadata或跨部署拷贝授权。已成立的不同版本/variant与数学/界面/事务原件直接继承，无新全面重测。

下一STEP017只读收敛MOD008/FLOW007/API005的数据退出/备份恢复/删除一致性实际合同。当前backup_dir配置存在不代表产品导出恢复已实现；当前schema和文件权威/未知/删除状态要先映射。可携导出需独立解读，恢复副本验证及旧运行资格不复活均原Must，无新资料/权限授权。Compose仍STEP018集成，Windows既定目标与Linux/Nginx条件阶段保留；不因为G11关闭提前改变其适用边界。

## 以下为v1.21及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.44，2026-10-12，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.22、task_model/07。以下v2.43原历史保留。

## G11正式关闭，STEP017完整设计TASK113待转交

{at}。TASK112/R106 review01真实结果53403字节/1dab1126aa72e335288d037baed5bc13b7cfdc1e4a386b6c04553e630f871571、379结束身份/12关键原件、当前112源/七规则及旧后缀相符。调度已返回/审计交付验收通过；主控正式通过关闭TASK111/R105工程、TASK112/R106审计及已采用G11有限切片。DEF031/F11201、DEF032/F11203、DEF033/F11202关闭，E11201漏计缺口一次核销关闭；历史整体控制合规不签通过。裁定DocuN/results/TASK-111-G11-final-acceptance.md。

STEP015/016执行已完成、验证已验证，适用范围为G11-P110/Windows单人本地目标/合成资料与受控服务替身/固定有限描述及既有故障模型；B01对该方案的宿主阻断解除、SEC003对应门通过。原109强化合同被已采用方案替换而其hash FAIL不改写。真实provider/全部Must/完整向量/本人开放任务/M1/整体验收/发布未通过，不能以有限关闭充当项目完成。旧HTML默认配置不由主控自动启用。

新v2-08 image ec3c70c7…/load8a047050…、四runtime6cc30016…绑定和三修正原件独审充分；其余业务/数学/资格/不同故障与Panel版本继承限域成立，不再出G11重复审计/准备/重跑卡。21输入记录=17真实成功ACK+4个422，43PNG原件不变。原111工程结果164196/51b4311e…、112首轮36048/ea51e0f4…全文保存。

执行账保守累计real16995.223，含E11201新增2279.703并保旧626.566超限；offline216.451/cleanup81.7987405。根20/20/global98入口非通过、PG16/16、image8/9、create52/55/start48/51、API12/12/browser11/11、model/OneCall9/10、frontend4/5、HTTP1611/5000/PNG182/3000/public68/300/internal30/500，所有失败/迟记/pre/时钟缺口/旧13元保留。审计本轮2305.839869、累计已观测5653.1886835/10800、未知准备单列。111和112全部执行/审计许可到终点，余秒/名字/模型额度不恢复运行。

预算active_batch null；47登记容器只读当前Stopped/Pid0/restart0，七新真实终态与准确自有树证明经独审，旧25UNKNOWN/R60/count1及旧root blocked不动，metadata不补旧kernel/EOF。主控产品/SQL/测试/build0，公共库/用户原始需求/111112原件及运行账未改。

按原路线转STEP017/MOD008/FLOW007/API005：执行进行中（设计）、产品开发未开始、验证未验证。TASK113/R107已登记并完整保存待人工转交，验收未裁定、实际dispatch/接收/开始均尚无。接收A+优先原111已结束工程窗，112窗保持独立；容量/可用性不足可新A+设计窗按最小卡恢复。10800秒只读设计从实采接收起，运行/compile/test/build/SQL/PG/Docker/Job/browser/model/安装/费用/删除/Git写全0，不消费旧余量。交当前关系/权限/格式/一致快照/隔离副本/保账未知/删除影响的唯一A—D实施合同；真正新关键决定才提具体采用包，无变化不人为增审批。

STEP018整链含Compose和真实检索/provider剩余、STEP019风险权限预算一致性独立验收、STEP020本人自用与运行交接继续原门。Linux完整应用部署属未来条件批次，Nginx按实际入口需要确定；不把Windows Job等同Linux监督，也不提前公开发布。旧DEF001/002禁用、既有G3—G10验收和非阻断观察不重开；范围改变或新反证按真实关联处理。

新卡DocuN/tasks/TASK-113.md，输入/窗口/只读预算在DocuN/evidence/TASK-113/orchestration-20261012；预期结果DocuN/results/TASK-113-result.md尚未产生。共享维护仍本主控。CHG1266—1279，下一1280；关闭核证在TASK111/orchestration-closure-20261012，当前不再派TASK112。

## 以下为v2.43及更早历史

'''}
for rel,prefix in prefixes.items():(ROOT/rel).write_bytes(encoded(prefix)+before[rel])
inputs=['AGENTS.md','DocuS/最终需求文档.MD','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','README.md','DocuN/results/TASK-111-G11-final-acceptance.md',
 'backend/app/main.py','backend/app/local_session.py','backend/app/runtime.py','backend/app/storage/originals.py','backend/app/materials/repository.py','backend/app/materials/api.py',
 'backend/app/activities/repository.py','backend/app/activities/teaching_repository.py','backend/app/activities/interview_repository.py','backend/app/memory/repository.py','backend/app/memory/api.py','backend/app/preview/repository.py','backend/app/preview/production_supervisor.py','backend/app/worker/launcher.py','backend/app/worker/gate.py',
 'frontend/src/main.tsx','frontend/src/activities/pendingIntents.ts','frontend/src/activities/teachingIntents.ts','frontend/src/activities/interviewIntents.ts','frontend/src/activities/teachingDrafts.ts','frontend/src/activities/interviewDrafts.ts','frontend/src/activities/MemoryWorkspace.tsx','config/local.env.example','deploy/start_local.py','deploy/compose.local.yml','backend/requirements.lock']
inputs.extend(str(p.relative_to(ROOT)).replace('\\','/') for p in sorted((ROOT/'backend/migrations').glob('*.sql')))
save(NEXT/'input-manifest.json',dict(at=at,TASK='TASK-113',R='R-107',purpose='最小源码/数据关系设计导航，不代表已实现出口或读取真实数据',files=[dict(path=str(ROOT/p),relative_path=p,**info(ROOT/p)) for p in inputs],rules=r['rules'],no_user_configuration_or_data_read=True))
save(NEXT/'window-assignment.json',dict(at=at,TASK='TASK-113',R='R-107',resource='A+增强设计执行者',window='优先原111已结束工程窗口；不可用/容量不足可新A+设计窗',reason='实际持久状态/预算及存储关系可复用；112独审窗口保持隔离',status='待人工转交',actual_dispatch=False,parallel=False,independent_auditor=False,contract=str(ROOT/'DocuN/tasks/TASK-113.md'),contract_sha256=sha(draft)))
save(NEXT/'plan-budget.json',dict(at=at,TASK='TASK-113',R='R-107',design_integrated_seconds=10800,kickoff='首个实际接收工具UTC/mono采样，准备unknown单列',product_or_compile_or_test_or_build_or_SQL_or_PG_or_Docker_or_Job_or_browser_or_model_or_fee_or_delete_or_git_write=0,official_primary_pages_max=6,document_consistency_batches=1,old_TASK111_112_permits_closed=True,no_budget_failure_unknown_reset=True,new_actual_dispatch_or_use=0))
entries=[
 ('DocuN/evidence/TASK-111/orchestration-closure-20261012/receive.py','publish.py只核增量终审原件/身份/精确metadata与维护文档。'),
 ('DocuN/evidence/TASK-111/orchestration-closure-20261012/received.json','53403终审/旧后缀/379对象及当前112源/七规则核证。'),
 ('DocuN/evidence/TASK-111/orchestration-closure-20261012/resource-recheck.json','47精确对象当前停止metadata，非旧UNKNOWN补证。'),
 ('DocuN/results/TASK-111-G11-final-acceptance.md','已采用有限G11、111112交付与DEF031—033正式关闭，历史626.566保留。'),
 ('DocuN/results/TASK-111-work-decision.md','工程验收关闭，许可结束，不复跑G11或恢复旧余量。'),
 ('DocuN/results/TASK-112-work-decision.md','增量审计交付通过及独立门闭合，无继续审计阻断。'),
 ('DocuN/evidence/TASK-113/orchestration-20261012/input-manifest.json','STEP017真实表/文件/关系的只读最小上下文，排真实配置数据。'),
 ('DocuN/evidence/TASK-113/orchestration-20261012/window-assignment.json','A+优先原工程窗只读设计，审计窗保持隔离，人工转交。'),
 ('DocuN/tasks/TASK-113.md','数据退出/备份恢复/删除一致性完整A—D合同任务，零产品操作。'),
 ('DocuN/results/TASK-113-work-decision.md','原STEP017只读设计许可，必要真实采用门不人为追加。'),
 ('DocuS/架构动态文档.MD','v1.22G11有限验收关闭、数据生命周期合同下一项。'),
 ('DocuS/执行动态文档.MD','v2.44唯一账：G11闭/113待转交，015016限定完成、017设计。'),
 ('DocuN/evidence/TASK-113/orchestration-20261012/plan-budget.json','10800秒设计/1次文档核对/运行0，旧投入与unknown不清。'),
 ('DocuN/evidence/TASK-111/orchestration-closure-20261012/delivery-proof.json','一次原文/源结果/执行账保护与闭合及新卡交付核对。')]
chgs=''.join(f'\n- CHG-{1266+i}，{at}，Codex编排Agent，{rel}。{note}\n' for i,(rel,note) in enumerate(entries))
(ROOT/'DocuS/文档变更记录.MD').write_bytes(before['DocuS/文档变更记录.MD']+encoded(chgs))
assert (ROOT/'DocuN/tasks/TASK-113.md').read_bytes()==draft
for rel in prefixes:assert (ROOT/rel).read_bytes().endswith(before[rel])
for s in r['sources']:assert info(ROOT/s['path'])==dict(bytes=s['bytes'],sha256=s['sha256'])
assert info(ROOT/'DocuN/results/TASK-111-result.md')==r['engineering_report']
assert info(ROOT/'DocuN/results/TASK-112-result.md')==dict(bytes=r['audit_receipt']['report']['bytes'],sha256=r['audit_receipt']['report']['sha256'])
assert load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')==budget
save(OUT/'delivery-proof.json',dict(at=at,G11_limited_accepted_and_closed=True,DEF031_032_033_closed=True,historical626_566_not_forgiven=True,task113_contract=info(ROOT/'DocuN/tasks/TASK-113.md'),final_acceptance=info(final),shared_old_history_preserved=True,source_unchanged=112,reports111112_unchanged=True,execution_budget_unchanged=True,actual_dispatch=False,new_business_operations=0,CHG_first=1266,CHG_last=1279,next_CHG=1280))
print(json.dumps(dict(G11_limited_closed=True,DEF_closed=['031','032','033'],next_task='TASK-113 / R-107',card_bytes=len(draft),card_sha256=sha(draft),architecture='v1.22',execution='v2.44',CHG='1266—1279',status='待人工转交',source_reports_budget_unchanged=True),ensure_ascii=False))
