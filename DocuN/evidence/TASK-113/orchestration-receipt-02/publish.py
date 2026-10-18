"""发布主控文档核证；保留旧文档原字节，不执行产品。"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent


def info(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


received = json.loads((OUT / 'received.json').read_text(encoding='utf-8'))
inputs = received['inputs_before_main_publication'] + received['additional_inputs_before_main_publication']
for entry in inputs:
    assert info(Path(entry['path'])) == {'bytes': entry['bytes'], 'sha256': entry['sha256']}, entry['path']
assert info(ROOT / 'DocuN/results/TASK-113-result.md') == received['result_identity']
assert not (ROOT / 'DocuN/tasks/TASK-114.md').exists()

at = datetime.now(timezone(timedelta(hours=8))).isoformat()
work = ROOT / 'DocuN/results/TASK-113-work-decision.md'
arch = ROOT / 'DocuS/架构动态文档.MD'
state = ROOT / 'DocuS/执行动态文档.MD'
changes = ROOT / 'DocuS/文档变更记录.MD'
old = {path: path.read_bytes() for path in (work, arch, state, changes)}
assert '文档v1.23' in old[arch].decode('utf-8-sig').splitlines()[2]
assert '文档v2.45' in old[state].decode('utf-8-sig').splitlines()[2]
assert 'CHG-1291' in old[changes].decode('utf-8-sig')
assert 'CHG-1292' not in old[changes].decode('utf-8-sig')

backups = OUT / 'before-documents'
backups.mkdir(exist_ok=False)
for path, raw in old.items():
    (backups / path.name).write_bytes(raw)

verdict = f'''# TASK-113 / R-107 修正轮01文档核证与设计验收

{at}，Codex编排Agent，task_model/07，V4.0/公共AGENTS CHG-0003。

结论：设计交付通过，K1—K3按完整当前A—D合同闭合；TASK113设计任务验收关闭。STEP017-P1仅为待用户采用的具体推荐包，产品未实施、未动态验证，不签STEP017完成或全部NFR005。

## 身份与读取证据

当前结果140950字节，SHA-256 37ba578fa653f778ab60f38b008c3c570e1e106a9237d55829cd21b5f47e19d0；81813字节当前合同前缀与revision-01/current-contract.md逐字节相同。首轮59137字节/1ca9cda00bcfb7f01bfd5630d909cea211f90e8951011159be984fb1925dff06作为原字节后缀完整保留。

主控核44份输入及4份必要补充、七份锁定规则、首轮9份及本轮15份证据，全部当前hash匹配。重读完整修正的引用/快照、权限、工厂/切换、删除、采用、矩阵和手工轨迹；没有用K闭合自评代替正文。逐文件结果见received.json，所有产品运行为0。

## K1—K3文档裁定

- K1：全部原件发布、幂等复用及新引用COMMIT与清理unlink采用共同RootLease；PG事务共享/排他锁、持久ticket/epoch、未知提交核对及先确认取消后最终新语句查询已明确。锁序、upload/save/PDF/直接元数据/目标加载入口、已墓碑源和共享历史引用均纳入，取消与unlink不得处于同一可回滚事务。V04/V14/V29及轨迹二覆盖未来实证门。关闭的是未实施方案的并发缺口，不登记为当前产品事故。
- K2：同一REPEATABLE READ只读T覆盖28业务及3控制安全投影，metadata/checkpoint载体、snapshot最小SELECT及秘密排除明确；target身份由可信工厂新建，历史转archive_history，墓碑按受限codec装载及只读view读取，活票据不迁权。V08/V09/V27覆盖未来权限与闭包实证。
- K3：独立私有ControlHub是长期job/selector唯一权威，源PG进度只是T观察；参考票据仍是源侧引用事实。工厂allocate/prepare/verify/seal、DPAPI凭据生命周期、MutationPermit及自有收尾、模式frozen、selector提交点与跨切换GET/丢响应核对已具体化。V12/V22/V24/V28/V29覆盖未来故障和切换；缺私有权威/未知停止不凭缓存或旧包放行。

三个修正已同时进入A—D、权限、格式例、图及29条未来矩阵。没有新的确定文档阻断；算法、ACL、LockFileEx、PG竞态、真实恢复和清理仍必须在实施后的定向验证中证实，本核证不代替产品测试或独立审计。

## 范围、账目及后续

有限切片为可携导出、备份、隔离新PG副本验证/永久只读核对、源资料墓碑与准确清理、控制与恢复权限。恢复后的旧任务/付费/tool/preview/持续学习执行不包含，完整恢复并继续使用Must仍须STEP018—020收口；不改最终需求、不减少Must。

修正轮观测2995.156/6000秒，累计6256.265/10800秒，旧准备unknown；官方6/6页。余时不延长已结束设计许可，产品/PG/Docker/browser/model/费用/Git写仍0。原G11验收、旧unknown25/R60/count1、历史超限及13元等原账保留，不取得新运行许可。

唯一必要用户决定为采用STEP017-P1；具体四项、代价和授权终点在TASK-113-work-decision.md当前置顶段。确认后主控按同一完整成果组织TASK114合成实施/定向验证，优先原A+工程窗口，具体资源与预算在卡面冻结；稳定成果另隔离A+集中审计一次。不前置重复G11研究，不占TASK114或提前运行。
'''

work_prefix = f'''# TASK-113 / R-107 设计验收与STEP017-P1待采用包

{at}，Codex编排Agent。修正轮01完整A—D文档核证通过，K1—K3设计缺口关闭，TASK113设计交付验收关闭。当前采用状态recommended_pending；未得到本包采用决定，未实现/动态验证。当前结果SHA-256 37ba578fa653f778ab60f38b008c3c570e1e106a9237d55829cd21b5f47e19d0，精确核证见DocuN/evidence/TASK-113/orchestration-receipt-02/design-acceptance.md与received.json。

## 唯一采用包STEP017-P1

请用户一次决定以下完整包。必要决定来自新增持久模型、角色/加载例外、准确删除和恢复切换语义，属于主要接口/关键数据模型变化；并非再批已有G11或普通实现细节。

1. 可携导出与checkpoint共用严格data_exit.v1.r01包，保全部业务关系、原件、正文和快照账；同一T包含28业务表和3安全控制投影。只导数据、受限历史和必要摘要，不带私配/凭据/活控制权，不执行包内代码/SQL。
2. 新增013_data_exit.sql、data_control/data_operation_jobs/data_tombstones及四NOLOGIN角色；九个严格绑定新目标loading的INSERT分支、两条教学FK可延迟默认IMMEDIATE、材料引用guard及frozen/restored_readonly模式门。001—012原件不改，普通不可变UPDATE/DELETE和账面守恒不放宽。代价是新增迁移/角色、schema指纹和跨模块定向验证。
3. 原件RootLease、PG事务围栏、持久引用ticket/epoch覆盖全部上传/替换/PDF/元数据提交及精确清理；资料墓碑后仅按准确hash清单删除本条不再共享的原件，历史元数据/旧备份/WAL不擦除。未知COMMIT/取消/锁/来源时不删。代价是导入/清理调用点的必要联动与真实竞态验证。
4. 私有ControlHub持久job/收据/selector与可信目标工厂，DPAPI保护本机凭据；完整停新写和自有收尾后才选择已验证的隔离目标。新目标永久只读，旧owner/nonce/StopProof/UNKNOWN不迁执行权、不重置额度或重发。默认尊重当前删除覆盖，旧备份仍可能含已删内容，按备份时点只读查看须另一次明确动作。代价是独立私有控制根、失败关闭和只读恢复能力范围。

## 采用后的授权终点

若批准，本主控可按该合同生成一张完整合成实施与定向验证卡，覆盖必要源码/013/配置样例/前端/README及真实合成PG、文件、HTTP、浏览器和有限故障验证，允许准确合成数据清理与只读副本切换；卡面必须先冻结精确新集群/卷/目录/角色/端口和有限预算，保留失败与证据。只批准技术包及该合成实施，不自动启用真实用户环境。

实现优先原A+设计/工程窗口；复杂角色、事务、恢复和跨模块控制继续增强执行。完整稳定成果后安排一次隔离A+集中独立审计，由主控据真实原件裁定有限STEP017，不逐修正重复全审。旧版本不变的G3—G11证据按hash及边界复用，实际影响处补验。

真实用户库迁移、真实数据删除/覆盖/切换、付费provider和任意旧资源运行不在本决定内，需另有对应实际授权。永久只读副本不完成恢复后持续执行/完整NFR005，也不完成STEP018—020/M-1/项目；这些Must继续保留并在后续完整链收口。原源普通本机重开维持原合同，不把只读范围变成对既有功能的暗中删除。

## 当前状态与证据

48输入/7规则、原9和本15证据全部hash匹配，首轮59137字节完整保留。修正轮2995.156/6000秒，累计6256.265/10800秒，准备unknown/官方6/6保留，全部产品操作0。设计许可已收口，余额不能复活；TASK114尚未生成或占号。架构v1.24、执行动态v2.46维护当前待采用状态，源/结果/旧证据/需求/公共库不改。

## 以下为首轮回收及原设计许可历史原字节

'''

arch_prefix = f'''# 架构动态文档

文档v1.24，2026-10-12，Asia/Shanghai。需求v1.2、执行动态v2.46、task_model/07。以下v1.23历史原字节保留，G11验收仍关闭。

## STEP017完整设计通过，唯一采用包待决定

{at}。TASK113/R107修正轮01完整A—D文档核证通过；K1—K3在引用/快照/权限/格式/工厂/停线/切换及未来矩阵闭合。新013、三控制表、四角色、九loading INSERT分支及两教学FK属性等均仍recommended_pending，当前产品仍28业务表，数据退出/备份恢复/资料删除尚未实施或动态验证。

推荐同一T读取28业务及3控制安全域，以严格数据包保关系/原件/正文/原账。全部新引用/元数据COMMIT与准确unlink共用RootLease、PG根事务围栏及持久ticket/epoch；提交未知不能删除。source控制安全投影不授target loading，target身份由可信工厂生成，历史和墓碑受限装载。ControlHub是私有长期job/selector权威，源PG只是进度T观察及实际引用准入事实，切换后的原key与收据查询不依赖旧source可连。

源停新写、自有工作按原证明收尾、frozen与selector一致后，才可选择经撤权验证的隔离目标；只读目标不加载旧控制者/执行/退款资格，不把备份时点余额当最新可用余额。永久只读恢复只支持此有限退出切片，旧活动/持续付费/tool/preview/学习执行恢复及完整NFR005仍留STEP018—020；最终需求Must不降。

具体唯一采用包与代价见DocuN/results/TASK-113-work-decision.md。用户采用后另卡精确合成实现/验证，稳定后一次隔离集中审计；当前无用户库迁移、真实删除/切换或资源启动授权。G11未知/预算/失败和既有有限验收不改，Compose/整体链/Windows自用及Linux/Nginx条件阶段维持。

## 以下为v1.23及更早历史

'''

state_prefix = f'''# 执行动态文档

文档v2.46，2026-10-12，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.24、task_model/07。以下v2.45历史原字节保留。

## TASK113修正轮01设计验收关闭，STEP017-P1待用户采用

{at}。用户回传的TASK113/R107修正轮01已实际保存，140950字节/37ba578fa653f778ab60f38b008c3c570e1e106a9237d55829cd21b5f47e19d0；当前完整合同81813字节与前缀相同，首轮59137字节/1ca9cda0…f06原后缀字节不改。主控48输入/7规则/首轮9和本轮15证据匹配，完整A—D与29条未来矩阵、四条手工轨迹已核读，K1—K3设计层关闭。TASK113设计交付验收通过并关闭，STEP017设计已完成/实施未开始/动态未验证；不是产品或独审PASS。

STEP017-P1仍recommended_pending，具体合并包在TASK-113-work-decision.md当前段：013三控制表/四角色/加载例外与FK、同T全域数据包、全引用与准确删除围栏、私有ControlHub/可信工厂和永久只读目标。现在向用户提交唯一必要采用决定，不再转设计修正卡。批准后主控出TASK114完整合成实施/定向验证，优先原A+设计工程窗口；稳定后隔离A+集中审计一次。当前TASK114未占号/未生成/未派，无产品运行授权。

修正轮真实接收06:13:28.613848Z至完成07:03:23.811855Z，观测2995.156/6000秒；累计6256.265/10800、余额4543.735，旧准备unknown，官方6/6页。产品import/compile/test/build/SQL/PG/Docker/Job/browser/model/安装/费用/删除/Git写全0；已结束设计余额不转作实现许可。主控此轮仅文件读取/hash/文档维护，不启动资源或执行产品层任务。

G11/111112有限关闭、DEF031—033、unknown25/R60/count1、历史626.566/13元和全部尝试/预算保留；不重复G11运行或审计。恢复副本永久只读不是完整NFR005持续使用或执行恢复，STEP018整体链/检索Embedding/Compose/真实服务、019总验、020自用运维仍未完成，最终需求Must不降。真实用户库/数据/凭据/删除/覆盖/切换不由本设计默许。

核证/历史保护见DocuN/evidence/TASK-113/orchestration-receipt-02/received.json、design-acceptance.md、delivery-proof.json。共享状态唯一仍本文件，正式架构/Work/CHG由主控维护；结果报告、旧证据、原始需求和公共库原件不改。CHG1292—1298，下一1299。

## 以下为v2.45及更早历史

'''

verdict_path = OUT / 'design-acceptance.md'
assert not verdict_path.exists()
verdict_path.write_text(verdict, encoding='utf-8')
for path, prefix in ((work, work_prefix), (arch, arch_prefix), (state, state_prefix)):
    path.write_bytes(prefix.replace('\n', '\r\n').encode('utf-8') + old[path])

entries = [
    (1292, 'DocuN/evidence/TASK-113/orchestration-receipt-02/receive.py', '修正轮01结果/当前合同/首轮后缀/48输入/7规则/原9及本15证据和计时核证。'),
    (1293, 'DocuN/evidence/TASK-113/orchestration-receipt-02/received.json', '当前真实读入身份和预算证据；无产品运行。'),
    (1294, 'DocuN/evidence/TASK-113/orchestration-receipt-02/design-acceptance.md', 'K1—K3完整合同闭合，113设计交付验收关闭，不签产品动态或完整NFR005。'),
    (1295, 'DocuN/results/TASK-113-work-decision.md', '具体STEP017-P1唯一待采用包，合成实施终点/永久只读范围/必要模型权限决定，历史保留。'),
    (1296, 'DocuS/架构动态文档.MD', 'v1.24完整数据出口设计通过但尚未采用/实施，保全部Must及后续持续使用门。'),
    (1297, 'DocuS/执行动态文档.MD', 'v2.46唯一账：113设计已收口/采用待用户/TASK114未派，旧计数和证据不重置。'),
    (1298, 'DocuN/evidence/TASK-113/orchestration-receipt-02/delivery-proof.json', '本轮保存复读/共享旧字节后缀与CHG连续性/非编排输入和结果保护。'),
]
addition = ''.join(f'\r\n- CHG-{number}，{at}，Codex编排Agent，{path}。{description}\r\n' for number, path, description in entries)
changes.write_bytes(old[changes] + addition.encode('utf-8'))

for path in (work, arch, state):
    assert path.read_bytes().endswith(old[path]), path
assert changes.read_bytes().startswith(old[changes])
for entry in inputs:
    path = Path(entry['path'])
    if path not in (arch, state):
        assert info(path) == {'bytes': entry['bytes'], 'sha256': entry['sha256']}, str(path)
assert info(ROOT / 'DocuN/results/TASK-113-result.md') == received['result_identity']
assert not (ROOT / 'DocuN/tasks/TASK-114.md').exists()
for number, _, _ in entries:
    assert changes.read_text(encoding='utf-8-sig').count(f'CHG-{number}，') == 1

proof = {
    'at': at, 'TASK': 'TASK-113', 'R': 'R-107',
    'design_acceptance': '通过，设计交付关闭，非产品动态/独立审计',
    'adoption': 'STEP017-P1 recommended_pending，等用户真实决定',
    'result_unchanged': True, 'prior_shared_documents_byte_exact': True,
    'non_shared_inputs_unchanged': True, 'rules_locked': 'V4.0/CHG-0003/task_model',
    'TASK114_generated_or_dispatched': False,
    'CHG_range': [1292, 1298], 'next_CHG': 1299,
    'product_runs': 0,
    'files': [{'path': str(path), **info(path)} for path in (verdict_path, work, arch, state, changes)],
    'backups': [{'path': str(backups / path.name), **info(backups / path.name)} for path in old],
    'consistency_check': '一次文档发布与保存复读：状态/版本/必要采用终点/输入/结果/历史/CHG核对',
}
save_json(OUT / 'delivery-proof.json', proof)
print(json.dumps({'design_accepted': True, 'adoption_pending': True, 'architecture': 'v1.24', 'execution': 'v2.46', 'CHG': [1292, 1298], 'TASK114_exists': False, 'result_unchanged': True, 'history_preserved': True, 'product_runs': 0}, ensure_ascii=False))
