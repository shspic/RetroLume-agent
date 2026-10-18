"""维护同TASK的C05部分验收/C06合同与共享状态，保护现成产品/结果/历史。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
C05 = ROOT / 'DocuN/evidence/TASK-111/execution/continuation-05'

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(data): return hashlib.sha256(data).hexdigest()
def info(p):
    data=p.read_bytes()
    return dict(bytes=len(data), sha256=sha(data))
def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def encoded(text): return text.replace('\n', '\r\n').encode('utf-8')

at=datetime.now(timezone(timedelta(hours=8))).isoformat()
received=load(OUT/'received.json')
budget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
assert budget['active_batch'] is None and budget['counts']==received['counts'] and budget['time_seconds']==received['time_seconds']
assert info(ROOT/'DocuN/results/TASK-111-result.md')['sha256']==received['result']['result_sha256']
for row in received['sources']:
    assert info(ROOT/row['path'])['sha256']==row['sha256'], row['path']
pending=['real_hidden','READY_unload','READY_active_refresh','control_path_lost','hard_deadline']
save('accepted-and-pending.json',dict(at=at, TASK='TASK-111', R='R-105', received_status='已返回', acceptance='部分通过，完整G11未关闭',
    new_accepted=['真实Response读取完成及实际bitmap尾组合/原生close0/旧图不draw限定组合','owner_control_lost最终首因','pipe_corrupt实际匿名管道反例','supervisor_death实际Reaper/自然EOF/严格Job销毁/同根满R恢复','both_supervisors_death实际结果/外部救援分层/同根满R恢复'],
    inherited='两Native/UI、DEF027—030及未变资格/数学/协议/预算/SQL/镜像/四runtime原范围证据',pending=pending,
    private_Job_recovery='真实premise/准确实例结束/准确error2销毁与Linux/EOF的限定证明，完整成果终审仍待',
    controls='C05内部600/650秒及陈旧换根偏差原样保留；当前coordinator900秒/旧C05选择器须在真实动作前与C06统一',
    old_preview25_UNKNOWN_preserved=True,new_evidence_not_general_dual_supervision_guarantee=True,full_audit_ready=False))
caps=dict(budget['continuation_caps'])
caps.update(real_batches=18,preview_creates=47,preview_starts=43,PG_container_starts=14,API_listener_starts=12,main_browser_starts=11)
assert caps['preview_creates']-received['counts']['preview_creates']==8 and caps['preview_starts']-received['counts']['preview_starts']==8
assert received['time_seconds']['real']+1800<=16200
save('continuation-budget.json',dict(at=at,TASK='TASK-111',R='R-105',permit='TASK-111-G11-C06-20261011',base_product_permit='TASK-111-G11-P110-20261010',
    prior_used=received['counts'],prior_time_seconds=received['time_seconds'],prior_count_caps=budget['continuation_caps'],cumulative_caps=caps,
    new_real_roots=[17,18],per_root_seconds=1800,new_real_limit_seconds=1800,cumulative_real_limit_seconds=16200,
    integrated_work_seconds=10800,prior_authorized_work_seconds=118800,cumulative_authorized_work_seconds=129600,
    kickoff='首个实际许可接收UTC+monotonic采样；准备段真实有据或unknown，不倒推',cleanup_reserved_seconds=600,cleanup_cumulative_limit_seconds=1800,
    planned_base=dict(UI_lifecycles=3,remaining_stop_scenarios=2),related_repair_slots=3,
    preview_names=[f'retrolume-task-111-g11-preview-{n:02d}' for n in range(50,58)],
    same_control_root=str(ROOT/'DocuN/evidence/TASK-111/execution/continuation-04/synthetic/control'),
    new_model_or_OneCall_planned=0,new_image_builds=0,actual_new_dispatch_or_use=0,not_written_into_execution_budget_yet=True))
paths=['DocuN/tasks/TASK-111.md','DocuN/results/TASK-111-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD']
before={rel:(ROOT/rel).read_bytes() for rel in paths}
assert sha(before[paths[0]])=='0d540620da8df04ef81e13a6f3e103adb29bb15c0e2130d18695e298b57b30ee', '旧合同漂移'
chgs=[int(x) for x in re.findall(rb'CHG-(\d+)',before[paths[-1]])]
assert max(chgs)==1215 and b'CHG-1216' not in before[paths[-1]]
pre=OUT/'before-documents'
pre.mkdir(exist_ok=False)
for rel,data in before.items(): (pre/rel.replace('/','__')).write_bytes(data)
(OUT/'prior-TASK-111.md').write_bytes(before[paths[0]])
prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK-111 / R-105 C05部分验收与C06五方法收口

{at}，Codex编排Agent。续作05已真实返回130797字节/cc115a6f…；99项交回源、七锁定规则、117106字节旧后缀及实际预算匹配，34登记对象只读metadata均停，18111/55451当前无监听，active_batch null。调度已返回，验收部分通过。完整G11未关闭，未派独立终审。

原正常两Native/UI与资格/启动/四准确屏障等有效事实继承，不重复。新增实际读取Response和已解码bitmap尾组合/原生close归零/旧图不draw，owner最终control_lost首因、真实pipe、SUP及双死亡四场景按原件限定范围接受。私有Job严格销毁前提、自然EOF和同根满reserve恢复有实际证明；双死亡不因此签通用自主停止，完整私有proof增量仍归集中终审。旧25缺kernel/EOF继续UNKNOWN/R60/count1，不用新证据替填。

只剩real_hidden、READY_unload、READY_active_refresh、control_path_lost、hard_deadline五方法。PW默认focus emulation/旧目录guard已有实读依据；旧600/650秒短窗、陈旧换根命令造成提前截断，current协调者900秒及C05自动选择也需与新许可统一。均在同一开发边界内，先制齐再运行，不换方案/权限/镜像或把普通修正切成准备卡。

前向签TASK-111-G11-C06-20261011，沿原C05 A+工程窗口待人工转交。新10800综合秒/末600清场，旧118800授权账变129600；real当前13951.425，新≤1800、累计上限16200，根16→18/每根1800；create39→47/start35→43，各新8及name50—57为五基线+三修正。PG/API/browser分别12→14/10→12/9→11，各两余量；image7/7、model/Windows9/10、frontend3/5及HTTP/输入/PNG/并发不增。旧失败/13元/迟记/pre缺口保留，C05旧到期许可不恢复。

仍唯一C04 control根，C06仅新证据目录。三UI专用入口不得找不到同目录旧组合而又重放；先无preview验证原生visibility，再独立READY隐藏/卸载/刷新，二故障实际注入、非干预取证、同根恢复。coordinator按当前根/总余时、expected_root和实际结果决策，禁止预排stop及另一套整组短时限。完整稳定后一次隔离增强审计仍保留。

主控只读文件/hash/精确metadata及维护文档，产品/SQL/build/业务执行0。原C05完整合同保存orchestration-receipt-06/prior-TASK-111.md，新卡DocuN/tasks/TASK-111.md；执行者接收后才合并运行账，不自动dispatch或占TASK112。

## 以下保留C05及此前裁定原字节

''',
'DocuS/架构动态文档.MD':'''# 架构动态文档

文档v1.18，2026-10-11，Asia/Shanghai。需求v1.2、执行动态v2.40、task_model/07。以下v1.17历史保留；G11五方法尚待，生产HTML默认关闭。

## 实际客户端尾组合与四停止已证，五方法收口

未变正常两Native/UI、计算图形、资格/启动与四准确屏障继承。续作05实际Response读取完成后迟到/真实解码bitmap释放、原生close归零和新视图未复活有有效原件；owner最终首因和真实pipe、SUP/双监督死亡限定场景已证。没有新Native、产品前端/image/四runtime/SQL/角色域变化。

HostJob新增实测limit_flags/成员/私有句柄/准确birth的premise；私有结束支持实际Query零或完整前提+准确实例已结束+准确Open error2的job_destroyed，不伪ActiveProcesses0。私有recover采用触发前只读进程与匿名管道读副本观测，原Linux/kernel/自然EOF/事件门不省。额外Job句柄/写端/验收者提前Terminate不能用于自主主张，双死亡该次结果不承诺任意双挂死自动停止。完整增量终审仍待。

原生hidden、独立READY卸载、READY活跃刷新及control_path_lost/hard_deadline缺证。PW focus模拟/旧目录guard与协调短窗属于已定界开发缺口，本次不再改技术方案或持久模型。原产品3次180秒、ready8/D-10/soft2/诊断15、默认关闭和用户库/provider/发布边界不变。旧25UNKNOWN保留，所有新场景仍原C04控制根。

## 以下为v1.17及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.40，2026-10-11，Asia/Shanghai。唯一总进度账；需求v1.2、架构v1.18、task_model/07。以下v2.39及原历史保留。

## 111续作05已部分验收，续作06仅五方法待转交

{at}。原C05 A+工程窗口已返回130797字节/cc115a6fe90d25e61d802a4df56bac5cefb1c8477b9eac09fc1a8dc29840a35d；99源/七规则和旧后缀一致。TASK111/R105调度已返回，验收部分通过，完整候选尚未稳定。真实Response/bitmap尾组合及owner/pipe/SUP/双死亡四场景限定接受，未变正常两Native/UI与其它已证部分继承；不派集中终审、不占TASK112，不签父G11/M1/项目。

仅剩real_hidden、READY_unload、READY_active_refresh、control_path_lost、hard_deadline。夹具最终关闭focus emulation/修原C04路径未跑，coordinator短窗/陈旧next_root和当前900秒/旧C05选择器需一致接续。旧FAIL_RECORDED、历史超限/迟记/pre缺口及旧25UNKNOWN/R60/count1仍保留，不换方案或重跑已证四停止/两Native。

C05真实根16/16(global94为入口非通过)，real13951.425/offline206.186/cleanup64.9397405；PG12/12、API10/10、browser9/9、preview create39/43/start35/41，已分配40—49；model/Windows9/10、frontend3/5、image7/7、HTTP1290/5000、PNG171/3000、public input66/300/internal26/500。预算active_batch null，34登记容器只读当前Stopped/Pid0/restart0，18111/55451当前无监听；无主控启动/业务执行。

签C06同TASK/R沿原C05 A+窗口，状态待人工转交，实际dispatch/新运行0。新10800综合秒从实际接收UTC/mono固化，旧授权118800→129600，末600清场。新real≤1800且累计上限14400→16200，根16→18各1800；create上限43→47/start41→43，按实际39/35各可新8，name50—57(五基线+三有据修正)。PG/API/browser上限14/12/11，各新增可用2；image/model/Windows/frontend/并发等不加。Unused不必消费，不恢复旧到期许可。

当前唯一control根仍continuation-04/synthetic/control；C06证据只入continuation-06。先把许可/路径/余时/五方法选择器一次核齐；无preview的原生visibility成立再消费预览；UI三方法与二故障连续，保留同browser上下文修正和一个修正根，不重复旧组合。未解决新UNKNOWN先完整本对象同根恢复，否则停止依赖部分并清场。完整稳定后另隔离A+集中终审。

本次CHG1216—1227，下一1228。回收/部分裁定/资源/预算/合同在DocuN/evidence/TASK-111/orchestration-receipt-06/；唯一新卡DocuN/tasks/TASK-111.md，旧C05卡原字节已保存。执行者接收后才能并入运行账，主控仅维护共享状态，不接管工程层；公共库/原始需求未动。

## 以下为v2.39及更早历史

'''}
draft=(OUT/'effective-contract.md').read_bytes()
assert b'*' not in draft and len(draft)>9000
# 先登记保存中，再落完整卡，最后写待转交状态。
(ROOT/'DocuS/执行动态文档.MD').write_bytes(encoded(f'# 执行动态文档\n\n{at}，TASK111/R105 C06已登记保存中，未实际派发。\n\n')+before['DocuS/执行动态文档.MD'])
(ROOT/'DocuN/tasks/TASK-111.md').write_bytes(draft)
for rel,prefix in prefixes.items(): (ROOT/rel).write_bytes(encoded(prefix)+before[rel])
save('window-assignment.json',dict(at=at,TASK='TASK-111',R='R-105',resource='A+原续作05工程窗口',contract=str(ROOT/'DocuN/tasks/TASK-111.md'),contract_sha256=sha(draft),status='待人工转交',actual_dispatch=False,parallel=False,audit=False))
entries=[
 ('DocuN/evidence/TASK-111/orchestration-receipt-06/receive.py','publish.py只维护编排文档；99源/七规则/结果及34精确metadata核证。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-06/received.json','续作05真实返回/原历史保存/有效限定证据，不签全G11。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-06/resource-recheck.json','34登记对象当前Stopped/Pid0，不补旧25完整停止证明。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-06/accepted-and-pending.json','新增尾组合/四停止接受，剩五方法和控制问题一次收口。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-06/continuation-budget.json','五基线+三修正及根/real/启动成套前向许可，旧账不清。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-06/effective-contract.md','C06只选五方法，不重跑正常/迟到组合/四停止。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-06/prior-TASK-111.md','C05旧完整合同原字节历史；新窗口安排待人工转交。'),
 ('DocuN/results/TASK-111-work-decision.md','C05部分验收/C06同范围接续裁定，集中终审仍待。'),
 ('DocuN/tasks/TASK-111.md','唯一完整现行C06任务卡，原工程窗口连续修正执行。'),
 ('DocuS/架构动态文档.MD','v1.18私有严格Job/EOF/限定动态结果及剩五项。'),
 ('DocuS/执行动态文档.MD','v2.40唯一进度账，C05已回收/C06待转交，所有实际预算保留。'),
 ('DocuN/evidence/TASK-111/orchestration-receipt-06/delivery-proof.json','一次文档路径/预算/旧后缀/源和结果未变检查，主控零产品执行。')]
change_text=''.join(f'\n- CHG-{1216+i}，{at}，Codex编排Agent，{rel}。{note}\n' for i,(rel,note) in enumerate(entries))
(ROOT/'DocuS/文档变更记录.MD').write_bytes(before['DocuS/文档变更记录.MD']+encoded(change_text))
assert info(ROOT/'DocuN/results/TASK-111-result.md')['sha256']==received['result']['result_sha256']
assert (OUT/'prior-TASK-111.md').read_bytes()==before[paths[0]]
assert (ROOT/'DocuN/tasks/TASK-111.md').read_bytes()==draft
for rel in prefixes: assert (ROOT/rel).read_bytes().endswith(before[rel])
for row in received['sources']: assert info(ROOT/row['path'])['sha256']==row['sha256']
for row in received['rules']: assert info(Path(row['path']))['sha256']==row['sha256']
assert load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')==budget
save('delivery-proof.json',dict(at=at,contract=info(ROOT/'DocuN/tasks/TASK-111.md'),old_card_preserved=True,shared_document_old_suffixes_preserved=True,report_unchanged=True,sources_unchanged=len(received['sources']),rules_unchanged=len(received['rules']),execution_budget_unchanged=True,counts_prior=received['counts'],caps_forward=caps,task_number_unchanged=True,next_TASK112_not_dispatched=True,CHG_first=1216,CHG_last=1227,next_CHG=1228,implementation_or_test_or_build_or_SQL_runs=0,actual_dispatch=False))
print(json.dumps(dict(contract_saved=True,bytes=len(draft),sha256=sha(draft),architecture='v1.18',execution='v2.40',CHG='1216—1227',status='待人工转交',source_unchanged=len(received['sources']),result_unchanged=True,budget_unchanged=True),ensure_ascii=False))
