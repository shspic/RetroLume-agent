"""登记采用和真实委派合同；只处理项目文档及文件身份，无产品运行。"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
RULES = ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def info(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def json_save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


at = datetime.now(timezone(timedelta(hours=8))).isoformat()
root_contract = OUT / 'effective-contract.md'
task_path = ROOT / 'DocuN/tasks/TASK-114.md'
work_path = ROOT / 'DocuN/results/TASK-114-work-decision.md'
parent_work = ROOT / 'DocuN/results/TASK-113-work-decision.md'
arch = ROOT / 'DocuS/架构动态文档.MD'
state = ROOT / 'DocuS/执行动态文档.MD'
changes = ROOT / 'DocuS/文档变更记录.MD'
assert not task_path.exists() and not work_path.exists()
received113 = load(ROOT / 'DocuN/evidence/TASK-113/orchestration-receipt-02/received.json')
for entry in received113['inputs_before_main_publication'] + received113['additional_inputs_before_main_publication']:
    path = Path(entry['path'])
    if path not in (arch, state):
        assert info(path) == {'bytes': entry['bytes'], 'sha256': entry['sha256']}, str(path)
assert info(ROOT / 'DocuN/results/TASK-113-result.md') == received113['result_identity']
for rule in load(RULES):
    assert info(Path(rule['absolute_path']))['sha256'] == rule['sha256'], rule['absolute_path']
observation = load(OUT / 'resource-observation.json')
assert observation['new_task_namespace_existing_names'] == []
assert observation['new_task_listening_ports'] == []
assert observation['prior_owned_pg_untouched']['Running'] is False

old = {path: path.read_bytes() for path in (parent_work, arch, state, changes)}
assert '文档v1.24' in old[arch].decode('utf-8-sig').splitlines()[2]
assert '文档v2.46' in old[state].decode('utf-8-sig').splitlines()[2]
assert 'CHG-1298' in old[changes].decode('utf-8-sig')
assert 'CHG-1299' not in old[changes].decode('utf-8-sig')
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items():
    (backup / path.name).write_bytes(raw)

product_paths = set()
for directory in ('backend/app', 'backend/migrations', 'frontend/src', 'frontend/dist'):
    for path in (ROOT / directory).rglob('*'):
        if path.is_file() and path.suffix in ('.py', '.sql', '.ts', '.tsx', '.css', '.json', '.js', '.html'):
            product_paths.add(path)
for relative in ('AGENTS.md', 'README.md', '.gitignore', 'deploy/start_local.py', 'deploy/preview/load-manifest.json', 'backend/pyproject.toml', 'frontend/package.json', 'frontend/package-lock.json'):
    path = ROOT / relative
    if path.is_file():
        product_paths.add(path)
for path in (ROOT / 'config').glob('*.example.json'):
    product_paths.add(path)
product_baseline = [{'relative_path': path.relative_to(ROOT).as_posix(), 'path': str(path), **info(path)} for path in sorted(product_paths)]

git_status = subprocess.run(['git', 'status', '--short', '--untracked-files=no', '--', 'backend/app', 'frontend/src', 'backend/migrations', 'deploy/start_local.py', 'README.md', '.gitignore'], cwd=ROOT, capture_output=True, check=True)
(OUT / 'git-product-status-before.txt').write_bytes(git_status.stdout)
head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, check=True).stdout.decode().strip()

allocation = {
    'TASK': 'TASK-114', 'R': 'R-108', 'permit': 'TASK-114-STEP017-IMPLEMENT-20261012',
    'allocated_at': at, 'actual_execution_started': False,
    'approval': {'source': '用户2026-10-12明确回复确认采用', 'package': 'STEP017-P1', 'scope': '完整合成实施与定向验证，永久只读目标；不含真实用户库/删除/覆盖/切换/费用'},
    'pg_image': observation['pg_image'], 'preview_image': observation['preview_image'],
    'maximum_running_containers': 2,
    'pg_slots': [
        {'slot': 'source', 'name': 'retrolume-task-114-data-source', 'volume': 'retrolume-task-114-data-source-data', 'port': 55461, 'database': 'retrolume_task114_source'}
    ] + [
        {'slot': f'target{number:02d}', 'name': f'retrolume-task-114-data-target{number:02d}', 'volume': f'retrolume-task-114-data-target{number:02d}-data', 'port': 55461 + number, 'database': 'retrolume_task114_target'} for number in range(1, 9)
    ],
    'pg_limits': {'cpus': 1, 'memory_bytes': 536870912, 'pids': 128, 'restart': 'no', 'host_ip': '127.0.0.1', 'host_binds': 0, 'docker_socket': False, 'privileged': False},
    'login_prefix': 'retrolume_task114_',
    'roles': ['admin', 'app', 'snapshot', 'loader', 'readonly', 'denied'],
    'restore_profiles': '可信host有限slot，创建后绑定完整CID/image/name/volume/job_id；包不可配置',
    'preview_namespace': 'retrolume-task-114-data-preview-',
    'api_port': 18114, 'vite_port': 15114,
    'roots': {name: str(ROOT / f'DocuN/evidence/TASK-114/synthetic/{name}') for name in ('source-root', 'backup-root', 'restore-root', 'control-root', 'scratch', 'sentinel-root')},
    'execution_control': str(ROOT / 'DocuN/evidence/TASK-114/implementation/control'),
    'limits': {'work_seconds': 28800, 'offline_process_seconds': 7200, 'real_hold_seconds': 10800, 'real_business_hold_seconds': 9600, 'cleanup_reserved_seconds': 1200, 'real_roots': 12, 'pg_create_attempts': 12, 'pg_slots': 9, 'pg_start_attempts': 32, 'preview_create_attempts': 2, 'preview_start_attempts': 2, 'api_starts': 8, 'vite_starts': 8, 'browser_starts': 6, 'windows_sessions': 12, 'frontend_builds': 6, 'new_fee': 0, 'real_provider_calls': 0, 'public_network': 0},
    'counts_at_dispatch_preparation': '全部新许可执行计数0；旧失败/投入/UNKNOWN/费用账保留，未实际派发',
    'resource_recheck_required_before_real_start': True,
    'host_memory_observation': observation['host'],
    'end_policy': '精确停止/证明并保留全部新容器卷数据证据，不drop/remove；未知不得授退款',
    'prior_resources_not_authorized': True,
}
json_save('resource-allocation.json', allocation)

parent_prefix = f'''# STEP017-P1用户明确采用（2026-10-12，当前有效）

{at}为主控登记时刻，不冒用户发言精确时间。用户在本编排聊天明确回复“确认采用”，批准上一主控提交的完整STEP017-P1包，采用状态adopted。TASK113修正轮01设计已验收关闭，113原结果与证据不改，其recommended_pending段仅保历史；执行必须按当前采用与TASK114精确新许可。

采用包括严格可携/恢复包、013三控制表/四角色/九加载INSERT分支/两FK和模式门、全新引用/准确清理围栏、私有ControlHub/可信工厂/全应用停线和永久只读目标。许可终点为完整合成实现及PG/文件/HTTP/UI定向验证，具体新资源/预算见TASK-114-work-decision.md及TASK114卡。不包括真实用户库迁移/真实数据删除覆盖切换/费用，也不以永久只读副本代全部NFR005持续业务恢复。

下一TASK114/R108已前置满足，A+原113设计工程窗口，一张完整成果卡内连续执行、普通修复/实际影响复验，稳定后隔离集中独审。旧G11/预算/失败/unknown25不复活；原设计余时不转实施额度。

## 以下为待采用包及此前历史原字节

'''
parent_work.write_bytes(parent_prefix.replace('\n', '\r\n').encode('utf-8') + old[parent_work])

work_text = f'''# TASK-114 / R-108 实施许可与编排裁定

{at}，Codex编排Agent。用户2026-10-12明确“确认采用”STEP017-P1，TASK113设计通过且K1—K3闭合。正式占用TASK114/R108，当前登记准备并保存完整卡，核对后待人工转交；实际派发/接收/执行均未发生。

本卡是一份完整数据退出、备份、隔离只读恢复、准确资料删除及HTTP/工作区接线成果，源码/迁移/配置/相关验证和范围内修复在原113 A+窗口连续完成。已采用合同为revision-01/current-contract.md精确81813字节/SHA-256 8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa；旧113结果140950字节和首轮全文只读保留。

允许卡面精确新source/最多8隔离target slot、必要最多2新的preview及本卡本地API/Browser/Job验证，OCI只复用实核本地固定镜像。新计数0、整体28800秒、offline7200、真实持有10800含最后1200清场、业务门9600/12真实根及其他有限次数，以实际接收首工具固化。新配置/凭据仅本卡新资源，角色及命名/端口/目录/并发条件在resource-allocation.json；旧库/容器/角色/预算不借。当前内存观察不足组合验证建议值，执行时复核，先推进源码/离线，不停用户软件或开启旧资源。

完整013/model/ACL、RootLease/PG ticket-epoch引用竞态、同T31安全域、可信factory/ControlHub/seal、源写fence/只读selector、包/原件/删除覆盖/四账与UNKNOWN、完整界面及V01—V29真实方法均在授权终点。scope永久只读，不授旧执行/退款或签完整NFR005；source原普通重开不变，剩余持续使用在STEP018—020。真实用户库/资料/私配/费用/外网/安装/pull/build/任意删除/Git写不许可。

一张卡内完成普通兼容/夹具/产品修复及必要复验，保全真实失败和as-run；同因两次有证据修正仍失败、上限或真实关键风险停依赖部分并交回，不每个普通失败即暗加新卡。旧充分证据按hash/实际影响继承，不复验G11全链/旧25。完整稳定后新隔离A+集中独审另卡（未来TASK115/R109未占）；本卡不是审计且不能自签。

全部产品/迁移/容器/测试执行由接收者，本主控只读核证、占号和维护共享文档。当前架构v1.25/执行动态v2.47，CHG由主控串行维护。人工只需转本卡，结果回传TASK-114-result.md路径；没有追加用户密钥或重复采用决定。
'''
work_path.write_text(work_text, encoding='utf-8')

register_prefix = f'''# 执行动态文档

文档v2.47，2026-10-12，Asia/Shanghai。需求v1.2、架构v1.25、task_model/07。

{at} 用户已明确采用STEP017-P1。TASK114/R108已占号登记准备；完整卡尚待保存复读，不能当已派发/接收。A+原113窗口，合成完整实现/验证；当前产品运行0。

## 以下为v2.46历史原字节

'''
state.write_bytes(register_prefix.replace('\n', '\r\n').encode('utf-8') + old[state])
# 模板要求先占号，再保存正式任务卡并改待转交。
task_path.write_bytes(root_contract.read_bytes())
assert task_path.read_bytes() == root_contract.read_bytes()
assert not (ROOT / 'DocuN/results/TASK-114-result.md').exists()

arch_prefix = f'''# 架构动态文档

文档v1.25，2026-10-12，Asia/Shanghai。需求v1.2、执行动态v2.47、task_model/07。以下v1.24历史原字节保留，G11仍有限验收关闭。

## STEP017-P1已采用，完整合成实施TASK114待转交

{at}登记。用户明确“确认采用”TASK113修正轮01及主控完整包：同T28业务/3控制安全域的严格包、013三表/四角色/九隔离loading INSERT分支及两教学FK、跨线程进程RootLease/PG引用ticket-epoch及准确unlink、独立私有ControlHub/工厂/全应用停线/只读选择。方案采用状态adopted，不等于产品已实现或动态通过；当前源码和001—012未由主控改动。

精确实施接线/角色/codec/原件/快照/清理/恢复/前端范围与V01—V29在TASK114完整合同，受控资源为新独立source/有限target/必要新合成preview，本地固定镜像实核复用，无真实provider或用户库。原28表与正常不可变/账守恒/StopProof规则保持，改动传播需要定向真实验证；稳定一次隔离集中独审，不逐修补全面重审。

只读目标的原账/unknown/历史资格保存，不迁活owner/nonce/StopProof、不退款或复活旧执行。永久只读副本不能替完整恢复后持续学习/付费tool/preview使用Must；这些仍STEP018—020/整体M1未闭合。原源普通本机重开与G3—G11已验边界保持，Compose/真实服务/Embedding/自用、Linux/Nginx条件阶段不被该包外推完成。

当前无真实用户库迁移/数据删除覆盖切换/生产启能力许可。主控只维护正式模型方案采用和任务状态，必要实际源码/013/指纹/角色将由执行者交候选后据证据更新。

## 以下为v1.24及更早历史

'''
arch.write_bytes(arch_prefix.replace('\n', '\r\n').encode('utf-8') + old[arch])

state_prefix = f'''# 执行动态文档

文档v2.47，2026-10-12，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.25、task_model/07。以下v2.46历史原字节保留。

## STEP017-P1已明确采用，TASK114完整实施/验证待人工转交

{at}为主控登记时刻。用户在本聊天明确回复“确认采用”，批准TASK113已核完整STEP017-P1，采用adopted。113/R107设计交付仍验收关闭，原修正报告/首轮/规则/证据不改；设计累计6256.265/10800、准备unknown/官方6/6与产品0保历史，不延设计余额。

TASK114/R108先占号登记，再保存DocuN/tasks/TASK-114.md并复读，状态待人工转交。接收A+原113设计工程窗口，真实可用性/不可核窗口ID不冒确认；无并行/子Agent，112审计窗隔离，实际派发/接收/运行尚0。目标是013/角色、导出/备份、引用-清理竞态、隔离只读恢复/私有控制/全写fence与HTTP/工作区、相关测试及普通修复的完整候选成果。TASK115/R109仅稳定后独审计划未占号，不能提前派或自签。

新许可TASK-114-STEP017-IMPLEMENT-20261012，从实际首工具固化UTC/mono计28800秒，offline7200、真实资源合计10800含清场1200/业务门9600；12真实根、PG最多9成功slot/12create尝试/32start，必要preview2、API/Vite各8、Browser6、Windows12、build6，新增费用/真实provider/公网0。全部新用量当前0，上限不是已用。普通修复可卡内连续，未知资格/同因两次仍失败或额度门停依赖部分、保留事实，不换窗清账。

固定新source及target01—08 namespace/卷/PG17本地image/端口55461—55469、API18114/Vite15114、独立control/source/backup/restore根与必要preview已给精确profile及并发最多2容器。主控只读metadata核镜像可读、新名称/端口无占、旧111 PG stopped；内存当前偏低，运行时复核，先源码/离线可推进。观察不恢复旧运行权或证明新资源已建，真实identity由接收者创建后绑定，禁止占碰旧资源。

G11关闭/DEF031—033/旧unknown25/R60/count1/历史626.566/13元和全部失败资源账保留。旧充分证据按对象与变化继承，只补新增实际影响。永久只读本切片不签完整NFR005、STEP018—020、M1/项目或发布，真实用户库/资料/密钥/迁移/删除/覆盖/切换/费用均不许可；原始/最终需求/公共库不改。

主控本轮仅读取/hashes/现有镜像metadata/正式文档维护，产品执行0。采用及新许可见TASK-113-work-decision.md、TASK-114-work-decision.md；输入/资源/窗口/预算/完整卡及保存证据在DocuN/evidence/TASK-114/orchestration-20261012，成果预期TASK-114-result.md尚未产生。唯一共享状态仍本文件。CHG1299—1308，下一1309。

## 以下为v2.46及更早历史

'''
state.write_bytes(state_prefix.replace('\n', '\r\n').encode('utf-8') + old[state])

context_paths = [ROOT / 'AGENTS.md', ROOT / 'DocuS/原始需求文档.MD', ROOT / 'DocuS/最终需求文档.MD', arch, state, parent_work, work_path, ROOT / 'DocuN/results/TASK-113-result.md', ROOT / 'DocuN/evidence/TASK-113/design/revision-01/current-contract.md', ROOT / 'DocuN/evidence/TASK-113/design/revision-01/b5-permissions.md', ROOT / 'DocuN/evidence/TASK-113/design/revision-01/format-example.json', ROOT / 'DocuN/evidence/TASK-113/design/revision-01/control-format-example.json', ROOT / 'DocuN/evidence/TASK-113/design/revision-01/relationships.mmd', ROOT / 'DocuN/evidence/TASK-113/orchestration-receipt-02/design-acceptance.md', ROOT / 'DocuN/evidence/TASK-113/orchestration-receipt-02/received.json']
json_save('input-manifest.json', {'at': at, 'TASK': 'TASK-114', 'R': 'R-108', 'snapshot_is_current_worktree_not_HEAD': True, 'git_HEAD': head, 'context': [{'path': str(path), **info(path)} for path in context_paths], 'product_before': product_baseline, 'rules': load(RULES), 'private_local_configuration_read': False, 'source_configuration_migrations_modified_by_main': 0})
json_save('window-assignment.json', {'TASK': 'TASK-114', 'R': 'R-108', 'execution': 'A+', 'recipient': '原TASK113修正轮01设计工程窗口', 'reported_client': 'Codex desktop', 'reported_model': 'GPT-6，精确子型号与窗口ID不可核', 'fallback': '原窗口确实不可用才同等胜任A+新窗最小恢复', 'route_reason': '高风险事务/ACL/原件竞态/全应用fence/恢复和控制权威', 'manual_transfer': True, 'dispatch_confirmed': False, 'acceptance_confirmed': False, 'subagent': False, 'independent_audit': '稳定后隔离A+另卡，未实际派发或占号'})

entries = [
    (1299, 'DocuN/results/TASK-113-work-decision.md', '用户确认采用STEP017-P1，当前adopted及合成实施终点，保历史原字节。'),
    (1300, 'DocuN/results/TASK-114-work-decision.md', 'TASK114/R108完整增强实施许可、精确新资源/预算/权限/审计门。'),
    (1301, 'DocuN/evidence/TASK-114/orchestration-20261012/effective-contract.md', '完整可转交成果合同：实现/定向验证/普通修复连续、29方法与停止边界。'),
    (1302, 'DocuN/tasks/TASK-114.md', '先唯一账占号后保存复读，待人工转交，不冒实际派发。'),
    (1303, 'DocuS/架构动态文档.MD', 'v1.25方案采用但产品未实现；只读范围不代完整NFR005。'),
    (1304, 'DocuS/执行动态文档.MD', 'v2.47唯一状态和新号/授权/待转交；旧预算/失败/UNKNOWN保留。'),
    (1305, 'DocuN/evidence/TASK-114/orchestration-20261012/resource-allocation.json', '实际本地image、有限独立PG/preview/端口/根/生命周期和预算；只读观察关联。'),
    (1306, 'DocuN/evidence/TASK-114/orchestration-20261012/input-manifest.json', '当前上下文/生产文件身份与长期Git差异保护，无私配/产品运行。'),
    (1307, 'DocuN/evidence/TASK-114/orchestration-20261012/window-assignment.json', '原113 A+窗口完整成果，人工闭环，独审保持隔离。'),
    (1308, 'DocuN/evidence/TASK-114/orchestration-20261012/delivery-proof.json', '一次完整卡/授权/参数/输入/原历史与源保护/CHG连续核对。'),
]
addition = ''.join(f'\r\n- CHG-{number}，{at}，Codex编排Agent，{relative}。{description}\r\n' for number, relative, description in entries)
changes.write_bytes(old[changes] + addition.encode('utf-8'))

for path in (parent_work, arch, state):
    assert path.read_bytes().endswith(old[path]), str(path)
assert changes.read_bytes().startswith(old[changes])
for row in product_baseline:
    assert info(Path(row['path'])) == {'bytes': row['bytes'], 'sha256': row['sha256']}, row['path']
assert info(ROOT / 'DocuN/results/TASK-113-result.md') == received113['result_identity']
contract = task_path.read_text(encoding='utf-8-sig')
required = ('## 目标与交付', '## 项目、规则与接收安排', '## 背景与最小充分上下文', '## 必须形成的完整产品成果', '## 允许文件和独占范围', '## 精确新资源与凭据', '## 预算、连续批次和异常处理', '## 验证、证据与审计关系', '## 精确清场、停止与回传')
assert all(section in contract for section in required)
assert not re.search(r'<[^>]+>|〈[^〉]+〉', contract), '不得遗留模板占位'
assert '*' not in contract and '|' not in contract, '本卡不使用星号或表格'
assert allocation['limits']['real_hold_seconds'] == allocation['limits']['real_business_hold_seconds'] + allocation['limits']['cleanup_reserved_seconds']
assert len(allocation['pg_slots']) == 9 and len(set(slot['port'] for slot in allocation['pg_slots'])) == 9
assert task_path.read_bytes() == root_contract.read_bytes()
for number, _, _ in entries:
    assert changes.read_text(encoding='utf-8-sig').count(f'CHG-{number}，') == 1
assert not (ROOT / 'DocuN/tasks/TASK-115.md').exists()

json_save('delivery-proof.json', {'at': at, 'TASK': 'TASK-114', 'R': 'R-108', 'status': '完整卡已保存复读、待人工转交；非已派发', 'adoption': 'STEP017-P1 adopted', 'task': {'path': str(task_path), **info(task_path)}, 'context_count': len(context_paths), 'product_baseline_count': len(product_baseline), 'rules': 7, 'histories_byte_exact': True, 'products_and_prior_result_unchanged': True, 'resources_started': 0, 'product_runs': 0, 'matrix': '113当前A—D的V01—V29及其子分支，未运行', 'CHG_range': [1299, 1308], 'next_CHG': 1309, 'required_sections': list(required), 'placeholder_and_format_check': True, 'final_docs': [{'path': str(path), **info(path)} for path in (parent_work, work_path, arch, state, changes)], 'note': '本文档一致性检查不是产品compile/test/audit。新的实际资源身份、内存与端口由执行者首操作复核。'})
print(json.dumps({'task_saved': str(task_path), **info(task_path), 'adoption': 'adopted', 'status': '待人工转交', 'product_baseline_count': len(product_baseline), 'architecture': 'v1.25', 'execution': 'v2.47', 'CHG': [1299, 1308], 'product_runs': 0, 'resources_started': 0, 'history_preserved': True}, ensure_ascii=False))
