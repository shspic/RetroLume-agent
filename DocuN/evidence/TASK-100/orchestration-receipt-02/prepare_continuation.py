"""Orchestration-only document maintenance; no product imports or test execution."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
PUBLIC = Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
OUT = ROOT / 'DocuN/evidence/TASK-100/orchestration-receipt-02'
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path, label: str) -> dict:
    data = path.read_bytes()
    return {'path': label, 'absolute_path': path.as_posix(),
            'sha256': digest(data), 'bytes': len(data)}


def save_json(path: Path, value: dict) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path.write_bytes(data)
    assert path.read_bytes() == data


task_path = ROOT / 'DocuN/tasks/TASK-100.md'
state_path = ROOT / 'DocuS/执行动态文档.MD'
arch_path = ROOT / 'DocuS/架构动态文档.MD'
decision_path = ROOT / 'DocuN/results/TASK-100-work-decision.md'
change_path = ROOT / 'DocuS/文档变更记录.MD'
result_path = ROOT / 'DocuN/results/TASK-100-result.md'
original = {p: p.read_bytes() for p in (task_path, state_path, arch_path, decision_path, change_path)}
assert digest(original[task_path]) == '18fd238354e291ba9303506cb82ebc82864d4e3d8d949246120362feed941cf7'
assert b'CHG-0812' in original[change_path] and b'CHG-0813' not in original[change_path]
assert 'v2.01' in original[state_path].decode('utf-8-sig')[:200]
assert 'v0.79' in original[arch_path].decode('utf-8-sig')[:200]
assert digest(result_path.read_bytes()) == '4199daf2fcc8134b55af8bb77b20c4483587272db3b449381f74f8645720bce5'
assert digest((ROOT/'DocuN/results/TASK-099-result.md').read_bytes()) == '0f38de84d6036e48a9fa544ba8304b37a72cf89e56e29fc05bef500609cc0e67'

previous = json.loads((ROOT/'DocuN/evidence/TASK-100/orchestration-receipt-01/continuation-input.json').read_text(encoding='utf-8-sig'))
rules = []
for record in previous['rules']:
    relative = record['path'].replace('\\', '/')
    current = identity(PUBLIC/relative, relative)
    current['expected_sha256'] = record['expected_sha256']
    current['match'] = current['sha256'] == current['expected_sha256']
    assert current['match'], relative
    rules.append(current)

paths = {record['path'].replace('\\', '/') for record in previous['files']}
paths.update({
    'DocuN/results/TASK-100-result.md',
    'DocuN/evidence/TASK-100/continuation-01/attempt-ledger-continuation.json',
    'DocuN/evidence/TASK-100/continuation-01/resume-check.json',
    'backend/tests/test_teaching_api.py',
    'backend/tests/test_teaching_recovery.py',
})
paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'DocuN/evidence/TASK-100/continuation-01/runtime').glob('*') if p.is_file())
paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'frontend/dist').rglob('*') if p.is_file())
before = {relative: identity(ROOT/relative, relative) for relative in sorted(paths)}

docker = {'checked_at': NOW, 'mode': 'read_only_inspect', 'state': 'unconfirmed'}
try:
    inspection = subprocess.run(
        ['docker', 'container', 'inspect', '80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d'],
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=20)
    docker['exit_code'] = inspection.returncode
    if inspection.returncode == 0:
        container = json.loads(inspection.stdout)[0]
        host = container['HostConfig']
        docker.update(state='confirmed', id=container['Id'], name=container['Name'], image=container['Image'],
                      running=container['State']['Running'], pid=container['State']['Pid'],
                      exit_status=container['State']['ExitCode'], memory=host['Memory'],
                      nano_cpus=host.get('NanoCpus'), pids_limit=host.get('PidsLimit'),
                      restart=host['RestartPolicy']['Name'], privileged=host['Privileged'],
                      bind_count=len(host.get('Binds') or []), port_bindings=host.get('PortBindings'),
                      mounts=[{'type': item['Type'], 'name': item.get('Name'), 'destination': item['Destination']}
                              for item in container.get('Mounts', [])])
    else:
        docker['error'] = inspection.stderr.strip()
        docker['note'] = 'Engine pipe unavailable; last execution cleanup says stopped, current container state unconfirmed.'
except subprocess.TimeoutExpired:
    docker.update(exit_code=None, error='read_only_inspect_timeout')

save_json(OUT/'resource-readonly.json', {
    'docker': docker,
    'host_process_listener_check': {'at': '2026-10-04T20:37:33.7517291+08:00', 'listeners': [], 'task100_processes': []},
    'mutation_performed': False,
    'secret_policy': 'Full inspect Env/stdout not saved or printed; only nonsecret selected fields.'})

for path, data in original.items():
    if path in (task_path, decision_path):
        target = OUT / ('TASK-100-pre-continuation-02.md' if path == task_path else 'TASK-100-work-decision-pre-continuation-02.md')
        assert not target.exists(), target
        target.write_bytes(data)
        assert target.read_bytes() == data

new_limits = {'active_seconds': 21600, 'offline_seconds': 1800, 'business_seconds': 3600,
              'cleanup_seconds': 480, 'real_entries': 3, 'container_start_attempts': 3,
              'application_start_attempts': 3, 'supervisor_function_entry_attempts': 24,
              'browser_launches': 2, 'browser_driver_launches': 3, 'frontend_build_attempts': 1}

state_prefix = '''# 执行动态文档

文档 v2.02，2026-10-04，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.80，task_model/阶段07。顶部当前；下方v2.01及全部历史原文保留。

## TASK100续作01已返回 部分通过 续作02完整接续

用户实际回传100/R094续作01，调度已返回，验收部分通过。接受当前修正候选及两次构建的限定证据；不接受“DEF-003—007全闭合”或完整实现/验证通过。009不可变恢复及失败收据final_status修正方向有效，仍待真实路径证明；DEF-004/005/006明确未关闭。原20项纯策略/合同及未变G3/G4/D3/G5/G6/G7有效结论继续复用，不重开旧成果。

四个入口未到教学主链：两次exit0汇总实际roles-prepare BLOCKED；末次009迁移阻断，下游仓储/恢复/故障/HTTP失败。当前runner没有Windows/浏览器子段；两项HTTP只覆盖未知活动/坏DTO。新的41项离线通过无原始unittest日志，不能作为A级证据。build成功是当时字节，最终源码—dist绑定尚待建立。原PASS/FAIL与旧错误全部保留，核证另列更正，不改执行者原件。

当前函数残留：T-launch在head.pending为空时可能放行且settle后dispatch_closed与后续教学资格冲突；admit/mark新教学分支没有完整head/版本/父实体/pending屏障；T-result缺command仍静默返回；workspace用TEXT body的JSON操作符及对默认解码jsonb再次json.loads；部分读取多SQL；故障DSN调用re却未导入；汇总漏BLOCKED、依赖失败还执行下游、直接builtin没有真正批截止及完整收尾。这是编排必要普通核证，不是全面独立审计；全部归原DEF-003—007、原100修复，不拆成新循环。

续作01许可结束，账载entry4/4、start1/3、app1/3、SUP0、browser0、driver0、build2/2，离线14.880/真实17.910/收尾0.890秒仅为该账口径；未计阅读/其他离线未知保留。初轮至少9入口、仓储计时57.170与原账51.230差5.940、至少一次start与原账0的差异继续保留，不把初轮总量写成精确9。换窗口、新许可不追认旧超限或清零失败。

2026-10-04编排只读Docker inspect引擎管道不可连接，当前容器状态未确认；上一cleanup原件记录Running=false/Pid=0。20:37:33本机18100/55442无监听，未发现task100执行进程。两库/角色准备PASS声明来自末批原件，Docker就绪后首用再核归属、结构与权限。编排没有启停服务/容器/应用，没有运行产品/compile/测试/build/PG/Job/浏览器/模型。

100/R094续作02正在保存，独占原边界，A+增强/用户最强可用新业务实施窗口。新窗口原因是两轮未进入主链且实现与控制合同仍残缺，不能继承“全部关闭”自评；不以完成任务的品牌重审。实际身份由执行者补登，不占用审计窗口，不自动子Agent。目标为修残留产品合同、补完整Windows/浏览器夹具及有限runner，再一主批集中执行，卡内普通修复后统一交回；不是只跑当前main-combo。

续作02新增许可主动21600/离线1800/业务3600/收尾480秒；入口3、精确start3、app3、SUP进入尝试24、browser2/driver3/build1，当前新增使用0。独立新账引用旧账，入口前计数，BLOCKED也占额。先完整离线控制验证与具体执行计划，真实运行等Docker引擎就绪。只用精确100容器/唯一卷/固定镜像、g8_main/g8_fault及六固定故障schema；保留数据、凭据仅内存安全注入，无用户库/外网/付费/删除清理/Git/新依赖。

STEP009进行中/部分验证，010—012候选行为仍未完整验证。只有稳定完整成果后一次隔离集中审计，下一101/R095只留计划、不占号、不提前出卡。Compose/Linux/Nginx/Git与项目剩余Must保持；G8、M-1、全部STEP及项目没有通过。编排统一维护共享状态，执行者仅回事实。

本批CHG0813—0819，下一CHG0820。完整卡DocuN/tasks/TASK-100.md及本轮裁定/身份索引已保存后核可读，待人工转交；没有已转交、接收或开始事实。结果仍DocuN/results/TASK-100-result.md，历史不改。

## 以下为v2.01及更早历史

'''

decision_prefix = '''# TASK-100 / R-094 续作01编排核证与续作02裁定（当前）

2026-10-04，Asia/Shanghai，Codex编排Agent。调度已返回，验收部分通过；候选修正与限定构建子证据采纳，完整G8与“DEF-003—007全闭合”不采纳。保持原TASK/R与授权，不追加产品模型批准，不接管执行。以下是少量关键函数/原件的普通核证，不是独立审计。

## 输入、实际证据与失败裁定

返回结果4199daf2fcc8134b55af8bb77b20c4483587272db3b449381f74f8645720bce5，原文保持。前轮当前代码/夹具身份、七锁定规则和原件导航见本轮continuation-input.json/receipt.json；旧卡完整原字节18fd2383保存TASK-100-pre-continuation-02.md。旧索引是过去基线，不要求当前修正与它相同，变化按实际用途登记。

续作01四入口：第一DSN前检阻断、两次roles阻断却汇总PASS/exit0、最后009缺password及其依赖失败。修码后的migrate DSN/恢复类名/fault DSN/token没有真实复验。不存在Windows/浏览器子段，HTTP仅未知活动404及坏DTO；不能认“下一步直接main-combo即可全链打通”。两次真实build日志可采当时构建；没有最终dist绑定。41项离线无原始运行日志，仅为执行者声明，不签全部实际运行或零skip。

DEF-003 current009恢复全列不可变、仓储预计算INSERT方向符合，DEF-007 final_status方向符合；保持候选，最终最小权限真实命令/恢复证据not_run。DEF-004/005/006未关闭：_locked_teaching_binding缺完整当前屏障，T-launch pending空放行与下一窗dispatch_closed问题，T-result缺command静默返回；workspace TEXT body JSON操作符及jsonb重复解码、其他端点多SQL；fault re缺导入，runner漏blocked/缺真正deadline/依赖隔离/finally/缺两类子段。定位以当前源码与本轮卡为准，不自修，不对未读模块给无缺陷结论。

原001—008、停止/账本旧权威及未变G3/G4/D3/G5/G6/G7保持；099批准的模型、表与接口不推翻，以上是同合同落实。DEF-001/002仍开放，097旧注入器禁用。没有以观察替代权限/停止证明、以SQL文本或mock替代PG真实结果。

## 投入、资源和接续

续作01账载入口4/start1/app1/SUP0/browser0/driver0/build2，14.880离线、17.910真实、0.890收尾；许可结束。初轮至少9入口及旧超限/漏时/未知保留，两次BLOCKED汇总PASS单列纠正而不覆盖原件。没有凭“预检失败”退还额度。

Docker只读inspect当前管道不可连接，容器实时状态未确认；前轮cleanup停容器原件有效于当时。20:37:33的18100/55442与task100进程检查无残留。先离线修完整控制/夹具，运行需引擎就绪、精确归属/限额/两库前置核对。不开共享服务，不重建资源，不问真实密码；只需引擎仍不可连接时用户启动Docker Desktop。

续作02由新的胜任A+最强可用业务实施窗口完整承接，原因是两轮未到主链、修正结论与实际事实矛盾，非模型品牌重审。仍原100/R094独占实施，新增主动6h/离线1800/业务3600/收尾480、入口3/start3/app3/SUP24/browser2/driver3/build1独立记账，旧投入不重置；第一完整主批，余两个仅有据修正/未测部分，不计划跑满。先实际完整fixtures与离线控制、冻结产品，再集中剩余PG/HTTP/Windows/bundle浏览器，一次回传。

更新状态v2.02、架构v0.80，需求v1.1不变。卡保存并回读后待转交，不称已派发。稳定后一次集中隔离审计，101/R095仍只留计划。编排产品/测试/编译/构建/PG/Job/浏览器/资源修改均0；本轮只写卡、裁定、必要原件索引和共享文档。

## 以下为2026-10-03初轮核证与续作01历史（原文保留）

'''

arch_prefix = '''# 架构动态文档

文档 v0.80，2026-10-04，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.02。G8候选修正继续，完整批准合同尚未落实；下面v0.79及全部历史保留。

## G8续作01候选与本轮实现边界

DATA当前009恢复teaching_records全列UPDATE/DELETE拒绝、仓储转向同事务预计算最终事实INSERT；这是符合099的修正方向，尚无最终最小权限真实命令证明。007仍唯一模型/工具正文，与教学facts/exposure/progress/head/command同短事务，缺教学链必须拒绝/回滚，不允许正文独自提交。没有新增表或持久列授权。

FLOW当前目标/答案/引用装配有候选增量，但数据库T-launch/admit/mark的head/revision/父实体/pending屏障仍欠缺。合法settle后的pending/dispatch_closed与下一次教学启动需要按原仓储权威协调；不改原关门/恢复/退款或SUP停止主体。T-result允许合法历史分类，不能以当前资格全拒历史代替批准语义。DEF-004仍开放。

MOD/API workspace的新单SQL候选有TEXT body JSON操作符与默认jsonb解码不匹配；其他读面也需原合同单快照、007正文、来源和暴露规则实际成立。只读GET零副作用。DEF-005仍开放。失败收据final_status修正为静态候选，真实恢复待证。

验证层runner尚缺真实Windows/浏览器、HTTP教学主链，blocked汇总/依赖/时限/保留式收尾仍不足，DEF-006开放。100续作02完成原边界产品修正、完整项目内fixtures与控制后集中验证，产品不得依赖公共库/DocuN临时实现。固定100资源/保留数据，强实现新窗口并非审计。

未变G3/G4/D3/G5/G6/G7证据与限定验收保持，097旧注入器禁用。完整稳定后一次隔离集中审计；真实provider、G8最终、完整STEP/M-1/项目及部署没有通过。Compose/Linux/Nginx/Git和其他Must安排不变。

## 以下为v0.79及更早历史

'''

# Register before publishing the card; both transitions are recorded by CHG-0819.
state_path.write_bytes(state_prefix.encode('utf-8') + original[state_path])
decision_path.write_bytes(decision_prefix.encode('utf-8') + original[decision_path])
prefix = (OUT/'continuation-02-prefix.md').read_bytes()
card = prefix + b'\n' + original[task_path]
task_path.write_bytes(card)
assert task_path.read_bytes() == card and card.endswith(original[task_path])
arch_path.write_bytes(arch_prefix.encode('utf-8') + original[arch_path])
state_prefix = state_prefix.replace('100/R094续作02正在保存', '100/R094续作02已保存并核可读，调度待转交')
state_path.write_bytes(state_prefix.encode('utf-8') + original[state_path])

after = {relative: identity(ROOT/relative, relative) for relative in sorted(paths)}
allowed_doc_changes = {p.relative_to(ROOT).as_posix() for p in (task_path, state_path, arch_path, decision_path, change_path)}
assert all(before[p]['sha256'] == after[p]['sha256'] for p in paths if p not in allowed_doc_changes)
assert result_path.read_bytes() and digest(result_path.read_bytes()) == '4199daf2fcc8134b55af8bb77b20c4483587272db3b449381f74f8645720bce5'

input_data = {'schema': 'task100.continuation-input.v2', 'at': NOW, 'root': ROOT.as_posix(),
              'task': 'TASK-100', 'r': 'R-094', 'continuation': '02', 'files': list(after.values()),
              'rules': rules, 'document_snapshot_note': 'Current navigation only, not a pass certificate. Public version locked. Product pre-edit baseline; shared DocuS remains dynamic.'}
save_json(OUT/'continuation-input.json', input_data)
receipt = {'schema': 'task100.orchestration-receipt.v2', 'at': NOW, 'task': 'TASK-100', 'r': 'R-094',
           'returned_round': 'continuation-01', 'dispatch': 'returned', 'acceptance': 'partial',
           'continuation_02_dispatch': 'saved_readable_pending_manual_transfer', 'new_limits': new_limits,
           'new_used': {key: 0 for key in new_limits},
           'returned_result': identity(result_path, result_path.relative_to(ROOT).as_posix()),
           'previous_card': identity(OUT/'TASK-100-pre-continuation-02.md', 'orchestration-receipt-02/TASK-100-pre-continuation-02.md'),
           'current_card': identity(task_path, task_path.relative_to(ROOT).as_posix()),
           'prior_permits': {'initial': 'ended; at least 9 entries, total other diagnostics unknown, preserved',
                             'continuation_01': 'ended; counts 4/1/1/0/0/0/2, times 14.880/17.910/0.890 per returned ledger'},
           'findings': [{'def': 'DEF-003', 'status': 'candidate_fix_dynamic_missing'},
                        {'def': 'DEF-004', 'status': 'open', 'functions': ['claim_teaching_launch', '_locked_teaching_binding', '_write_teaching_outcome']},
                        {'def': 'DEF-005', 'status': 'open', 'facts': ['TEXT body->> SQL type mismatch', 'native jsonb decoded twice', 'other reads multiple statements']},
                        {'def': 'DEF-006', 'status': 'open', 'facts': ['re missing import', 'blocked ignored in summary', 'missing windows/browser stage', 'deadline/finally incomplete']},
                        {'def': 'DEF-007', 'status': 'candidate_fix_dynamic_missing'}],
           'resource': docker, 'indexed_objects': len(after), 'rules_matches': len(rules),
           'card_history_byte_exact': True, 'current_result_unchanged': True,
           'product_mutations': 0, 'product_execution': 0, 'resource_mutations': 0,
           'next_audit': '101/R095 plan only, not allocated/issued'}
save_json(OUT/'receipt.json', receipt)

changes = [
    ('0813', 'DocuN/results/TASK-100-result.md', '续作01真实返回核证，原文不改；部分通过，不采全部DEF关闭和完整G8自评。'),
    ('0814', 'DocuN/evidence/TASK-100/orchestration-receipt-02/', '保存当前必要身份/七规则、旧卡与裁定原字节、只读资源与真实失败核证；无产品或资源运行。'),
    ('0815', 'DocuN/results/TASK-100-work-decision.md', '置顶续作01核证/续作02裁定，当前合同残留与控制阻断、旧预算未知保留，历史原字节保留。'),
    ('0816', 'DocuN/tasks/TASK-100.md', '同100/R094完整续作02，A+最强可用新业务窗口；残留修正/完整控制夹具/集中PG-HTTP-Windows-browser卡内完成，旧两许可结束，新许可独立。'),
    ('0817', 'DocuS/架构动态文档.MD', 'v0.80记录候选不可变修正、当前资格/原子结果/读取和实际验证缺口，不改099批准模型及旧停止权威。'),
    ('0818', 'DocuN/evidence/TASK-100/orchestration-receipt-02/continuation-input.json', '保存卡与产品/夹具/dist当前导航及原件身份；索引非通过证明，首改核实际字节。'),
    ('0819', 'DocuS/执行动态文档.MD', 'v2.02先登记续作02，保存全文核可读后改待转交；旧投入/未知/失败保留，新增0，Docker实时状态未确认，101仅计划，下一0820。'),
]
addition = '\n' + '\n'.join(f'- CHG-{number}，{NOW}，Codex编排Agent，{path}。{message}' for number, path, message in changes) + '\n'
change_path.write_bytes(original[change_path] + addition.encode('utf-8'))

# Document consistency and protected-byte verification only.
assert state_path.read_bytes().endswith(original[state_path])
assert arch_path.read_bytes().endswith(original[arch_path])
assert decision_path.read_bytes().endswith(original[decision_path])
assert change_path.read_bytes().startswith(original[change_path])
assert '待转交' in state_path.read_text(encoding='utf-8')[:4500]
for relative in paths:
    if relative not in allowed_doc_changes:
        assert identity(ROOT/relative, relative)['sha256'] == before[relative]['sha256'], relative
for path in (task_path, state_path, arch_path, decision_path, change_path):
    assert path.read_bytes().decode('utf-8-sig')
verification = {'at': NOW, 'scope': 'document consistency only', 'result': 'PASS',
                'indexed_files': len(after), 'public_rules_matches': len(rules),
                'product_and_result_hashes_unchanged': True, 'histories_byte_exact': True,
                'card': identity(task_path, 'DocuN/tasks/TASK-100.md'),
                'formal_versions': {'requirements': '1.1', 'architecture': '0.80', 'execution': '2.02'},
                'changes': ['CHG-'+item[0] for item in changes], 'next_chg': 'CHG-0820'}
save_json(OUT/'document-verification.json', verification)
print(json.dumps({'saved_card': task_path.as_posix(), 'card_bytes': len(card),
                  'indexed_files': len(after), 'rules_matches': len(rules), 'verification': 'PASS',
                  'dispatch': 'pending_manual_transfer', 'docker': docker['state'],
                  'product_resource_execution': 0}, ensure_ascii=False))
