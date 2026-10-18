"""回收STEP017首轮设计，保存定向文档修正合同，未采用/未实施权限包。"""
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
at=datetime.now(timezone(timedelta(hours=8))).isoformat();r=load(OUT/'received.json')
report=ROOT/'DocuN/results/TASK-113-result.md';assert info(report)==dict(bytes=r['delivery']['bytes'],sha256=r['delivery']['sha256'])
for s in r['inputs']+r['additional_sources']:assert info(Path(s['path']))==dict(bytes=s['bytes'],sha256=s['sha256'])
facts=f'''# TASK113首轮设计定向核证

{at}，编排只读核证。首轮59137字节/1ca9cda0…，44输入/4补充/七规则/9设计证据匹配，运行0，原3261.109秒与准备unknown保留。当前产品还没有资料DELETE或data_exit模块；以下是未采用候选设计缺口，不称真实数据事故/产品DEF，也不要求运行证明设计文档。

K1：OriginalStore.put在发布/幂等验证原件后返回，PostgresMaterials.save另开事务提交新来源/版本引用，现资料API按此顺序调用，原代码无SourceFileLease。首轮拟租约只明确保护快照copy和清理。删除D取排他/查无他引用后，新来源B不拿该租约就复用同hash并提交引用，D再unlink会使成功B缺原件。A/B为不同来源，锁A不足。必须补所有新增引用与清理最后判据/实际unlink的共同围栏及事务未知/进程边界；不以双查hash省略。

K2：新data_control/data_operation_jobs/data_tombstones三表属提议，source snapshot仅授28表列SELECT的文字不足以支撑同T墓碑/谱系读取。需精确三表纳入/排除、源snapshot只读权限、包/codec载体、target由可信工厂生成的控制身份与受限墓碑加载/只读view。不要通过给snapshot写/删除成员资格补读。

K3：恢复job在原源，目标在新集群且selector换dataset/instance；需给持久控制权威/连接role和切换后by-key/收据/删除索引/最新账旁证路径，不能默认源一直可读。工厂/控制函数签名与受信凭据、停新写围栏和自有停线覆盖、selector半发布/丢响应行为需闭合。永久只读副本是原提议明示范围，并非要求现在改为执行恢复；但不能冒全部持续使用/执行恢复Must已过，采用代价/后续门一致保留。

源码事实依据：backend/app/storage/originals.py put/verify；materials/api.py上传链；materials/repository.py save/create_pdf_candidate；main.py连接/生命周期。已读010最终shape和002/006/012实际约束，未静态发现必须废弃原九加载分支/两FK思路的依据，不重复全仓研究。修正后的权限/格式/关系需整份A—D一致。
'''
(OUT/'design-gap-facts.md').write_bytes(encoded(facts))
used=Decimal(str(r['delivery']['observed_design_seconds']));new=Decimal('6000');cap=Decimal('10800');assert used+new<=cap
save('correction-budget.json',dict(at=at,TASK='TASK-113',R='R-107',permit='TASK-113-STEP017-DESIGN-R01-20261012',old_observed_seconds=str(used),total_observed_cap=str(cap),old_remaining=str(cap-used),new_window_seconds=str(new),max_observed_projection=str(used+new),old_prepare_unknown_preserved=True,official_pages_used=4,official_pages_cap=6,new_pages_if_critical_max=2,document_consistency_batches=1,product_operations=0,old_permit_not_resumed=True,actual_dispatch=False))
paths=['DocuN/tasks/TASK-113.md','DocuN/results/TASK-113-work-decision.md','DocuS/架构动态文档.MD','DocuS/执行动态文档.MD','DocuS/文档变更记录.MD']
before={p:(ROOT/p).read_bytes() for p in paths}
assert sha(before[paths[0]])=='7cdf64fb3d7448f37a19bbd9f188d2afa8c9c95cd3b440793bd1446c6f490f56'
assert max(int(x) for x in re.findall(rb'CHG-(\d+)',before[paths[-1]]))==1279
pre=OUT/'before-documents';pre.mkdir(exist_ok=False)
for p,b in before.items():(pre/p.replace('/','__')).write_bytes(b)
(OUT/'prior-TASK-113.md').write_bytes(before[paths[0]])
draft=(OUT/'effective-contract.md').read_bytes();assert len(draft)>7500 and b'*' not in draft
(ROOT/'DocuS/执行动态文档.MD').write_bytes(encoded(f'# 执行动态文档\n\n{at}，TASK113/R107修正轮01已登记保存中，首轮已回收，不派实施。\n\n')+before['DocuS/执行动态文档.MD'])
(ROOT/'DocuN/tasks/TASK-113.md').write_bytes(draft)
prefixes={
'DocuN/results/TASK-113-work-decision.md':f'''# TASK113/R107首轮回收与K1—K3定向合同修正

{at}，Codex编排Agent。首轮真实报告59137字节/1ca9cda00bcfb7f01bfd5630d909cea211f90e8951011159be984fb1925dff06、44输入/4补充/七规则/9设计证据匹配。调度已返回，设计验收部分通过，A—D/真实28表/格式和恢复边界有有效成果；产品未实施/未验证。必要STEP017-P1包尚未采用，不现在请求用户批准不完整合同。

K1原件共用hash清理与新引用提交缺统一围栏，静态并发反例可损坏刚成功的新导入；当前无DELETE，非已经出现产品事故。K2新增控制三表的同T读取/最小snapshot权限/包格式/target控制身份与墓碑加载需补齐。K3跨source/target/私有控制区和selector后的查询权威/工厂/停线接口需写实，并明确只读副本范围及后续执行恢复门。原readonly推荐不强改为付费续发，原需求持续使用Must不能无痕撤销或称已过。

上述均归同原113 A+设计窗，一次重写完整当前A—D、K对照/必要采用包/矩阵及图例，旧59137全文原字节保留；不让实施者拼旧冲突段。不重复已充分事实图或G11，不前置产品测试/独立审计、不读取用户私配/数据。新6000秒从实际接收UTC/mono固化，原3261.109/10800不清、观测投影9261.109，unknown与官方4/6页保留，所有产品操作0。

现行完整卡DocuN/tasks/TASK-113.md已保存待人工转交，旧首轮卡保存本receipt/prior-TASK-113.md。原新权限/013/加载guard/资料删除/切换仍未实施或授权采用，TASK114仅未来计划未占。修正闭合后主控再将具体唯一必要包给用户判断，无新关键决定的普通内容不人为追加审批。

## 以下为首轮设计许可原字节

''',
'DocuS/架构动态文档.MD':'''# 架构动态文档

文档v1.23，2026-10-12，Asia/Shanghai。需求v1.2、执行动态v2.45、task_model/07。以下v1.22历史保留，G11验收仍关闭。

## STEP017候选合同已有，租约与控制闭包尚待修正

113首轮提出同一严格数据包系列的可携导出和隔离只读恢复、MVCC T/文件清理租约、三控制表/四角色/十三版迁移及九加载分支/两FK属性等推荐。均只是设计、未采用/未实施，当前产品仍28业务表、backup_dir无消费者。永久只读验证副本及其代价不等于恢复后执行资格或全部NFR005已通过。

拟精确删除必须与普通上传/替换/PDF候选等新引用提交共用可执行的围栏，原只保护快照/清理不够。新控制三表的source同T权限、包/codec、target可信控制身份/墓碑view需闭合；source/target/私有注册器与selector后的读写主体、工厂/停线边界不能靠运行时猜。K1—K3归原113一次文档修正，不为当前无删除接口登记产品事故或重开G11。

只读恢复/资料删除/013权限模型的唯一采用包尚待完整主控核证，用户库/真实删除/迁移/覆盖/切换/新实例运行没有许可。现行原四账/UNKNOWN、只停止自有工作、原件身份/删除后不可用、配置秘密不出包等Must不降；所有当前源码和G11证明未被设计改变。

## 以下为v1.22及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.45，2026-10-12，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.23、task_model/07。以下v2.44历史原字节保留。

## TASK113首轮部分验收，K1—K3完整合同修正待转交

{at}。TASK113/R107首轮真实回收59137字节/1ca9cda00bcfb7f01bfd5630d909cea211f90e8951011159be984fb1925dff06，44输入/4补充/七规则及9设计原件匹配；已观测3261.109/10800秒、准备unknown、官方4/6页、一致性1批、产品/compile/test/build/SQL/PG/Docker/Job/browser/model/安装/费用/删除/Git写0。调度已返回、设计验收部分通过；STEP017设计进行中、产品未开始/未验证，不宣备份可恢复已通过。

A—D实读28表/关系和推荐格式、隔离只读恢复、预算/控制排除、删除影响、013权限包/矩阵已有有效文档。但K1新增引用与清理unlink缺共同围栏，K2新三表同T读取/格式/target控制元数据权限闭包不足，K3持久控制权威/切换后查询/工厂/停线及只读支持范围要写实，必须先修不完整合同，再提交唯一具体必要包。STEP017-P1仍recommended_pending，尚未询问/得到用户采用，不把新model/role/DELETE或loader计划当授权。

TASK113/R107修正轮01已保存，状态待人工转交，实际dispatch/接收/新操作0；接收原A+设计窗，无子Agent/并行/112审计窗参与。许可TASK-113-STEP017-DESIGN-R01-20261012，新只读6000秒从接收UTC/mono固化，原已观测3261.109与余额7538.891/总10800保留，最大投影9261.109；准备unknown不编造，官方页仅原剩2/总6。只改113结果置顶完整A—D及revision01证据，原59137全文保留；一次文档核对，产品操作仍全0，不生成真实数据包/SQL/容器。

G11/111112有限验收和DEF031—033关闭保持；旧unknown25/R60/count1、历史626.566/13元/原失败和全部账保留，不为了STEP017设计申请旧停止证明或重启资源。现有用户/合成库/私配/源码/权限均未改。只读副本是推荐有限支持，不替代项目所有持续恢复/真实provider/完整向量/STEP018—020/项目验收。

本轮主控只读源码/结果hash与共享文档维护，无产品运行。新卡DocuN/tasks/TASK-113.md，旧首轮卡原字节存TASK113/orchestration-receipt-01/prior-TASK-113.md，核证/静态设计反例/只读修正预算同目录；未来实施TASK114未占号，不能提前发。修正充分再处理必要采用，必要用户动作目前仅转同一设计修正卡，不要求数据/DSN/密钥。

CHG1280—1291，下一1292。唯一状态仍本文件，主控维护正式架构/Work/CHG，公共库与用户原始需求不改。

## 以下为v2.44及更早历史

'''}
for p,prefix in prefixes.items():(ROOT/p).write_bytes(encoded(prefix)+before[p])
save('window-assignment.json',dict(at=at,TASK='TASK-113',R='R-107',round='revision-01',permit='TASK-113-STEP017-DESIGN-R01-20261012',resource='A+原113设计窗口',status='待人工转交',actual_dispatch=False,parallel=False,independent_auditor=False,product_runs=0,adoption_pending_not_requested=True,contract=str(ROOT/'DocuN/tasks/TASK-113.md'),contract_sha256=sha(draft)))
entries=[
 ('DocuN/evidence/TASK-113/orchestration-receipt-01/receive.py','publish.py只核设计/输入及维护文档，零产品操作。'),
 ('DocuN/evidence/TASK-113/orchestration-receipt-01/received.json','59137首轮/44输入/4补充/七规则/9证据一致。'),
 ('DocuN/evidence/TASK-113/orchestration-receipt-01/design-gap-facts.md','K1共用hash新引用并发反例/K2K3闭包缺口，非实际产品事故。'),
 ('DocuN/evidence/TASK-113/orchestration-receipt-01/correction-budget.json','新6000只读/总10800不清，4/6页及unknown继承。'),
 ('DocuN/evidence/TASK-113/orchestration-receipt-01/effective-contract.md','一次完整A—D修正，不前置测试，不只贴补丁。'),
 ('DocuN/evidence/TASK-113/orchestration-receipt-01/prior-TASK-113.md','首轮完整任务卡原字节历史保全。'),
 ('DocuN/results/TASK-113-work-decision.md','首轮部分验收/必要包暂不提交/同窗文档修正裁定。'),
 ('DocuN/tasks/TASK-113.md','现行修正轮01完整合同，同TASK/R。'),
 ('DocuS/架构动态文档.MD','v1.23数据生命周期推荐及租约/控制闭包未定，未采用。'),
 ('DocuS/执行动态文档.MD','v2.45唯一账：113已回/修正待转交，产品未开始。'),
 ('DocuN/evidence/TASK-113/orchestration-receipt-01/window-assignment.json','A+原设计窗，只读接续，未实际派发。'),
 ('DocuN/evidence/TASK-113/orchestration-receipt-01/delivery-proof.json','一次合同/历史/非DocuS源/结果保护和预算核对。')]
chgs=''.join(f'\n- CHG-{1280+i}，{at}，Codex编排Agent，{p}。{note}\n' for i,(p,note) in enumerate(entries))
(ROOT/'DocuS/文档变更记录.MD').write_bytes(before['DocuS/文档变更记录.MD']+encoded(chgs))
assert (ROOT/'DocuN/tasks/TASK-113.md').read_bytes()==draft and (OUT/'prior-TASK-113.md').read_bytes()==before[paths[0]]
for p in prefixes:assert (ROOT/p).read_bytes().endswith(before[p])
for s in r['inputs']+r['additional_sources']:
    if Path(s['path']).resolve() in {(ROOT/'DocuS/架构动态文档.MD').resolve(),(ROOT/'DocuS/执行动态文档.MD').resolve()}:continue
    assert info(Path(s['path']))==dict(bytes=s['bytes'],sha256=s['sha256'])
assert info(report)==dict(bytes=r['delivery']['bytes'],sha256=r['delivery']['sha256'])
save('delivery-proof.json',dict(at=at,TASK='TASK-113',R='R-107',contract=info(ROOT/'DocuN/tasks/TASK-113.md'),old_task_card_preserved=True,shared_history_preserved=True,old_design_result_unchanged=True,product_source_unchanged=True,new_adoption_granted=False,old_observed_seconds=str(used),new_window_seconds=str(new),total_observed_cap=str(cap),product_operations=0,actual_dispatch=False,CHG_first=1280,CHG_last=1291,next_CHG=1292))
print(json.dumps(dict(task='TASK-113',R='R-107',round='revision-01',bytes=len(draft),sha256=sha(draft),architecture='v1.23',execution='v2.45',CHG='1280—1291',status='待人工转交',adoption_not_granted=True,old_report_and_source_preserved=True),ensure_ascii=False))
