"""回收稳定候选，串行登记TASK112独立终审；不改产品或执行预算。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
AUDIT=ROOT/'DocuN/evidence/TASK-112/orchestration-20261011'
C06=ROOT/'DocuN/evidence/TASK-111/execution/continuation-06'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=sha(b))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def encoded(s):return s.replace('\n','\r\n').encode('utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
received=load(OUT/'received.json');methods=load(OUT/'methods-byte-check.json')
assert info(ROOT/'DocuN/results/TASK-111-result.md')['sha256']==received['result']['result_sha256']
budget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
assert budget['active_batch'] is None and budget['counts']==received['counts'] and budget['time_seconds']==received['time_seconds']
for r in received['sources']:assert info(ROOT/r['path'])==dict(bytes=r['bytes'],sha256=r['sha256'])
assert not (ROOT/'DocuN/tasks/TASK-112.md').exists() and not (ROOT/'DocuN/results/TASK-112-result.md').exists()
assert len(received['sources'])==105 and received['runtime_originals_count']==81 and methods['source_changes']==11
save(OUT/'candidate-disposition.json',dict(at=at,TASK='TASK-111',R='R-105',dispatch_status='已返回',acceptance='部分通过；稳定有限候选待集中独立终审',
    implementation='完整候选已交付，不是父G11最终验收',evidence='C06五方法原件已补齐，原接受证据保持各自版本/限域',execution_control='C06本轮账已收口；旧偏差不清',
    engineering_pending_methods=[],raw_sources_verified=105,runtime_originals_verified=81,refresh_GETs=37,
    mixed_frontend_bundle_scope='旧hidden/unload/两Native是否继续适用于新增退出守卫，由TASK112独立判定，无默认全套重测',
    new_product_change='HtmlExplanationPanel.tsx文档退出守卫',old_unknown25_preserved=True,
    prior_111_engineering_may_not_restart_during_audit=True,independent_audit_task='TASK-112 / R-106',no_parent_release=True))
before_paths=['DocuN/results/TASK-111-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD']
before={p:(ROOT/p).read_bytes() for p in before_paths}
assert max(int(x) for x in re.findall(rb'CHG-(\d+)',before[before_paths[-1]]))==1227
draft=(OUT/'TASK-112-contract.md').read_bytes();assert len(draft)>12000 and b'*' not in draft
pre=OUT/'before-documents';pre.mkdir(exist_ok=False)
for p,b in before.items():(pre/p.replace('/','__')).write_bytes(b)
# 占号先于正式任务卡落盘；保存后再更新为待转交。
(ROOT/'DocuS/执行动态文档.MD').write_bytes(encoded(f'# 执行动态文档\n\n{at}，TASK112/R106独立终审已登记保存中；111稳定候选已返回，未派发新工程。\n\n')+before['DocuS/执行动态文档.MD'])
AUDIT.mkdir(parents=True,exist_ok=False)
sources=received['sources']
primary=['AGENTS.md','DocuS/最终需求文档.MD','DocuN/results/TASK-110-result.md','DocuN/results/TASK-110-work-decision.md','DocuN/evidence/v4-migration-20260930/rules-snapshot.json']
indexes=[
 'continuation-03/final/evidence-manifest.json','continuation-03/final/image-bindings.json','continuation-03/final/source-identity.json','continuation-03/root-11/step-15-faults/fault-results.json',
 'continuation-04/final/source-identity.json','continuation-04/final/source-differences.json','continuation-04/final/Native-and-normal-UI.json','continuation-04/final/pre-gap.json','continuation-04/root-14/step-10-faults/fault-results.json',
 'continuation-05/final/source-identity.json','continuation-05/final/source-changes.json','continuation-05/final/session-proof-index.json','continuation-05/root-15/step-03-tail/tail-attempt-2/tail-effects.json','continuation-05/root-15/step-04-faults/fault-results.json',
 'continuation-06/final/source-identity.json','continuation-06/final/source-changes.json','continuation-06/final/as-run-bindings.json','continuation-06/final/five-methods-final.json','continuation-06/final/active-refresh-complete-HTTP.json','continuation-06/final/session-proof-index.json','continuation-06/final/runtime-originals-index.json','continuation-06/final/execution-receipt.json','continuation-06/final/command-index.json','continuation-06/final/event-ledger-as-observed.jsonl','continuation-06/final/failures-and-reuse.json','continuation-06/final/exact-resources-final.json','continuation-06/final/ports-final.json']
originals=load(C06/'final/runtime-originals-index.json')
frozen=dict(at=at,TASK='TASK-112',R='R-106',purpose='对象/路径/身份导航，所有结论由独立审计者形成',project_root=str(ROOT),
    sources=[dict(path=str(ROOT/r['path']),relative_path=r['path'],bytes=r['bytes'],sha256=r['sha256']) for r in sources],
    primary_inputs=[dict(path=str(ROOT/p),**info(ROOT/p)) for p in primary],
    rule_sources=received['rules'],
    evidence_indexes=[dict(path=str(ROOT/'DocuN/evidence/TASK-111/execution'/p),**info(ROOT/'DocuN/evidence/TASK-111/execution'/p)) for p in indexes],
    C06_runtime_copies=[dict(path=r['evidence_copy'],original=r['runtime_source'],bytes=r['bytes'],sha256=r['sha256']) for r in originals],
    execution_budget_identity=info(ROOT/'DocuN/evidence/TASK-111/execution/budget.json'),
    omitted_implementation_self_evaluation=True,new_business_operations_authorized=0)
save(AUDIT/'frozen-inputs.json',frozen)
(ROOT/'DocuN/tasks/TASK-112.md').write_bytes(draft)
prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK-111 / R-105 C06稳定候选回收与TASK112集中终审

{at}，Codex编排Agent。真实回收146608字节/fcee65ac…；105当前文件和七锁定规则一致，原130797字节后缀原字节保留，81份runtime原件副本与原文件逐项同hash，40个登记Docker对象当前Stopped/Pid0/restart0，18111/55451无监听、active_batch null。TASK111已返回，工程五个剩余方法已交付，验收部分通过；批准的G11有限切片最终裁定仍待独立终审。

原生hidden/独立READY卸载和修正READY刷新有独立原件；修正刷新完整HTTP37条均GET、owner null、原D/starts不变。初次刷新实际两个stop尝试/ClientDisconnect反例保留，不冒请求根本未发。控制路径失联和hardD真实触发后的自然双EOF与同根满60持久恢复已核，验收者没有提前Docker kill，严格Job/Linux完整性由终审复核。旧25继续UNKNOWN/R60/count1，原两Native和已证子项按as-run版本继承，不重跑。

最后产品增量仅Panel文档退出守卫，11源变化包括夹具。最终Panel7c720469…及新bundle e76cacf4…，hidden/unload旧bundle和refresh新bundle分层，未把最终快照追认为全方法重跑。未变后台/SQL/镜像/角色域保留原范围；C03 renderer/browser忙死、C04 Node/Reaper、C05四故障与C06两故障均以各自原件交完整终审，不用六场景总标记替代不同故障。

C06实用根18/18、real14546.863/16200、offline215.358/cleanup77.2837405，create45/47/start41/43，PG14/API12/browser11到限，frontend4/5、image7/7、model/Windows9/10，HTTP1611/5000、PNG182/3000/public68/300/internal26/500。所有失败、旧超限/迟记/pre缺口/离线漏计批内秒数与13元保留；工程已返回不再消费未用56/57或旧到期入口。111窗冻结，不能并行写产品或重新跑旧runner。

正式登记TASK-112/R-106，一张完整只读增强终审卡，接收A+新真实隔离窗口，未参与110/111设计实施、不继承实现聊天，状态待人工转交。业务运行/PG/Docker/browser/模型/build额度0，10800秒一次完整读审，原始合同/105冻结源/版本差异/原件与执行账为输入；不读111结果自评或主控验收段先形成判断。工程普通修正不逐轮审计，此为既定完整稳定点集中门。

主控无产品执行/SQL/测试/构建，111源/结果/预算及历史不改。正式独立结果将存DocuN/results/TASK-112-result.md；此刻结果尚未产生，不能宣终审通过。候选与新卡/冻结索引已保存，用户人工转交即可，原111窗口不接该审计。

## 以下为C06及此前裁定原字节

''',
'DocuS/架构动态文档.MD':'''# 架构动态文档

文档v1.19，2026-10-11，Asia/Shanghai。需求v1.2、执行动态v2.41、task_model/07。以下v1.18历史保留；G11有限候选稳定返回，集中隔离终审待。

## 客户端文档退出与完整有限证据已交付

当前Panel新增beforeunload/pagehide撤销身份/引用版本与owner、abort旧请求，退出文档的visibility/组件清理及迟到分支不自动发送stop；pageshow只恢复退出标志，不恢复owner。同文档原生隐藏/组件卸载仍沿原停止路径。修正refresh新bundle真实GET-only证据与之前同文档两方法旧bundle分层交审，未统一追称最终版全部重跑。

余下原生隐藏、READY卸载/刷新与控制路径失联/hardD五方法有原件。私有Job严格销毁/自然EOF/Linux/持久恢复、M01—M12不同故障及版本继承仍由集中独立终审裁定。后台/012/角色域/四runtime/固定v2-07及其它图形/资格链未变；无新的自由HTML/JS、导航例外或用户库/provider/发布授权。

稳定候选不等于SEC003/B01/G11或所有STEP已放行。HTML生产默认关闭，旧25缺kernel/EOF的UNKNOWN不补造/不退款；当前控制根保持C04，产品未知门不绕过。TASK112只读独立审完整实际影响，完整候选期间工程冻结，不再派逐方法准备或重跑卡。

## 以下为v1.18及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.41，2026-10-11，Asia/Shanghai。唯一总进度与状态账；需求v1.2、架构v1.19、task_model/07。以下v2.40原历史保留。

## TASK111稳定候选已返回，TASK112集中独立终审待转交

{at}。TASK111/R105续作06真实回收146608字节/fcee65ac816c59e364f26c23d0feaec023b28a97b170e78785d16af19d4be5f4，105源/七规则和130797旧后缀一致，81原件副本与原runtime同hash。调度已返回；验收部分通过；实现完整稳定有限候选、五方法证据已补齐，父G11/SEC003/B01/STEP015016/M1及项目仍待终审，不宣全项目通过。

新hidden/独立READY卸载/修正refresh、control_path_lost/hardD原件接受为工程交付；最终Panel7c720469…文档退出guard与新bundle e76cacf4…，旧hidden/unload/正常两Native与新refresh的静态适用性留隔离审计判断。原首次严格刷新FAIL、两个stop尝试和ClientDisconnect未改；37个真实GET、owner null/不续D/不重置starts及两故障满60恢复有可核原件。C03 renderer/browser、C04 Node/Reaper、C05四故障均有独立目录，完整审计按不同方法归因，不仅看最新五项汇总。

实际累计根18/18(global96为入口非通过)、real14546.863/16200、offline215.358/cleanup77.2837405；create45/47/start41/43、name50—55使用/56—57未用；PG14/API12/browser11全到限；image7/7、frontend4/5、model/Windows9/10、HTTP1611/5000/PNG182/3000/public input68/300/internal26/500。active_batch null；40登记Docker对象当前Stopped/Pid0/restart0，18111/55451无监听。旧失败/超限/迟记/首采样及pre/漏计批内秒数和13元全部保留。旧25仍UNKNOWN/R60/count1，不借本次真实StopProof补旧缺口。

TASK111工程到回传终点，原A+窗口冻结，现无新工程运行许可。任务卡/旧时窗/剩余计数可读不恢复执行，不能与审计并行写产品/证据/资源。唯一C04 registry保持，资源仅精确拥有范围，无用户库、付费、安装/Git/删除/发布操作；主控产品执行0。

TASK112/R106已登记并完整保存，调度待人工转交、验收未裁定，实际dispatch/审计开始/审计结果均尚无。接收A+新隔离终审窗口，未参与110/111实现或继承聊天；一张卡完成代码/证据/执行控制三轴及M01—M12原合同判断，仅hash/diff/解析原件，业务/PG/Docker/Windows/browser/model/build额度0。一次综合10800秒，充分证据直接继承，真实缺口给最少差异，不新增BFCache/跨浏览器等未采用Must。终审通过后主控裁定G11有限切片关闭；有阻断再合并相关修复回原111窗，非逐轮全面重审。

新卡DocuN/tasks/TASK-112.md、冻结105源/原始输入和原件索引DocuN/evidence/TASK-112/orchestration-20261011/frozen-inputs.json。预期回传DocuN/results/TASK-112-result.md，此刻文件未产生。主控核证在TASK111/orchestration-receipt-07，CHG1228—1239，下一1240。公共规则与原始需求未动；唯一状态由本主控维护。

## 以下为v2.40及更早历史

'''}
for rel,prefix in prefixes.items():(ROOT/rel).write_bytes(encoded(prefix)+before[rel])
save(AUDIT/'window-assignment.json',dict(at=at,TASK='TASK-112',R='R-106',resource='A+用户最强且胜任的独立审计Agent',arrangement='全新真实隔离审计会话',reason='完整高风险候选的既定独立门；111工程窗不能兼审',status='待人工转交',actual_dispatch=False,parallel=False,independent=True,business_run_budget=0,integrated_seconds=10800,old_111_engineering_frozen=True))
entries=[
 ('DocuN/evidence/TASK-111/orchestration-receipt-07/receive.py','inspect_methods.py/publish.py只读证据与维护文档，不运行产品。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-07/received.json','105源/七规则/结果及81原件复制hash一致，真实五方法导航。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-07/methods-byte-check.json','两故障自然EOF/满R同根恢复及两版前端增量分层核证。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-07/resource-recheck.json','40精确metadata均停，ports-recheck.json两端口无监听，非旧UNKNOWN树证明。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-07/candidate-disposition.json','工程已返回/稳定候选待终审，111冻结；不签父放行。'),
 ('DocuN/evidence/TASK-112/orchestration-20261011/frozen-inputs.json','105对象及原始合同/各轮真实证据导航，不馈实现自评。'),
 ('DocuN/evidence/TASK-112/orchestration-20261011/window-assignment.json','新隔离A+集中终审，零业务运行，人工转交。'),
 ('DocuN/tasks/TASK-112.md','一张完整G11三轴终审卡，原111实现窗口不接审计。'),
 ('DocuN/results/TASK-111-work-decision.md','稳定候选限定回收和独立终审编排裁定。'),
 ('DocuS/架构动态文档.MD','v1.19客户端退出守卫及混合版本证据待独审，生产默认关闭。'),
 ('DocuS/执行动态文档.MD','v2.41唯一账：111已返回/112待转交，预算历史和UNKNOWN不清。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-07/delivery-proof.json','一次合同/身份/旧后缀/运行账/源结果保护的交付检查。')]
chgs=''.join(f'\n- CHG-{1228+i}，{at}，Codex编排Agent，{rel}。{note}\n' for i,(rel,note) in enumerate(entries))
(ROOT/'DocuS/文档变更记录.MD').write_bytes(before['DocuS/文档变更记录.MD']+encoded(chgs))
assert (ROOT/'DocuN/tasks/TASK-112.md').read_bytes()==draft
for rel in prefixes:assert (ROOT/rel).read_bytes().endswith(before[rel])
for r in received['sources']:assert info(ROOT/r['path'])==dict(bytes=r['bytes'],sha256=r['sha256'])
for r in received['rules']:assert info(Path(r['path']))['sha256']==r['sha256']
assert info(ROOT/'DocuN/results/TASK-111-result.md')['sha256']==received['result']['result_sha256']
assert load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')==budget
save(OUT/'delivery-proof.json',dict(at=at,TASK='TASK-112',R='R-106',contract=info(ROOT/'DocuN/tasks/TASK-112.md'),frozen_inputs=info(AUDIT/'frozen-inputs.json'),shared_history_preserved=True,source_unchanged=105,result111_unchanged=True,budget111_unchanged=True,actual_dispatch=False,audit_result_not_created=True,business_operations=0,CHG_first=1228,CHG_last=1239,next_CHG=1240))
print(json.dumps(dict(task='TASK-112',R='R-106',bytes=len(draft),contract_sha256=sha(draft),status='待人工转交',architecture='v1.19',execution='v2.41',CHG='1228—1239',source111_unchanged=105,result111_and_budget_unchanged=True),ensure_ascii=False))
