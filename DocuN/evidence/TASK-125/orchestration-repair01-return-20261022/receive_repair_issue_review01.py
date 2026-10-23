"""主控仅核文件/已有证据，回收修复并签发原独审增量卡。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import ast
import hashlib
import json
import re
import sys

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
RETURN = 'DocuN/evidence/TASK-125/orchestration-repair01-return-20261022/'
REVIEW = 'DocuN/evidence/TASK-126/orchestration-review01-20261022/'
REPAIR = 'DocuN/evidence/TASK-125/execution/repair-01/'
TZ = timezone(timedelta(hours=8))


def p(relative):
    dest = (ROOT / relative).resolve()
    dest.relative_to(ROOT)
    return dest


def read(relative):
    return p(relative).read_bytes()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(relative):
    return json.loads(read(relative).decode('utf-8-sig'))


def put(relative, raw):
    dest = p(relative)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw.encode('utf-8') if isinstance(raw, str) else raw)
    return dest


def dump(relative, value):
    return put(relative, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


CONTRACT = r'''# TASK-126 / R-120 review-01 双缺陷修正独立增量复核 当前有效

## 唯一目标与四个问题

你继续原TASK126独审责任，只对稳定修复增量完成一次独立复核。不重新做首轮安装器完整审查，不运行任何产品、测试或服务，不引入新的计量/账号研究。

本轮回答四问。

1. F126-01 P1是否消除。真实产品connect是否显式固定host和hostaddr为原配置允许的127.0.0.1，apply/verify是否共享这一路径；原真实数据库身份和合法容器NAT语义是否保留，是否不靠全局环境修改或预检后的身份查询掩盖认证目的地。
2. F126-02 P2是否消除。原拼写的reparse/junction拒绝是否在物理长路径身份归一之前；实际父目录与项目根归一及归一失败关闭能否封闭已证8.3别名路径，并覆盖new_output、plan输出、Journal/apply收据，保留正常输出、排他创建和完整收据verify仅读。
3. 原始batch03的9方法及三文件最终字节、明确选例/继承和控制记录是否真实对应修正；未变12方法、旧18方法/首轮其它结论在哪些范围能继承。不能以参数记录器、零字段或本地文件元数据称真实TCP/认证/PG/ACL通过。
4. 根据上述事实更新当前代码门/证据轴/控制轴结论，给两项发现逐项关闭或保留理由；首轮最小真实验证清单仅列因本次变化而确有必要的差异，没有差异即明确沿用。不新写一份同样部署设计。

交付仍为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-126-result.md，在review-01置顶追加完整增量结论，原33379字节首轮全文及失败结论完整保留。新增原始核证只进D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/review-01/，不改首轮audit文件。

## 身份、规则与基线

项目根D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。模式task_model，V4.0/公共AGENTS CHG-0003，来源D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。锁定规则沿DocuN/evidence/v4-migration-20260930/rules-snapshot.json，当前需求v1.4、架构v1.68、执行动态v2.96。已读且指纹不变规则和首轮上下文直接复用，只补新增合同与实际差异。

接收A+，继续刚完成TASK126首轮的原独审窗口，须未参与TASK125修复实施或测试设计，不得让125工程窗口自审。若原独立窗口确不可用，才用新隔离独审窗口接续同号，先披露独立性并读取原结论/必要证据，仍不重审未变完整业务。真实客户端/模型按实际登记，不因标签变化自动作废已有工作。

本轮仍TASK126/R120，父TASK125/R119，STEP-018/020及未来019适用安全证据。不占新TASK或R。工程修复01已返回并冻结，没有并行写入；本卡待人工转交，未声称接收/启动。旧首轮审计交付已结束，本卡才给明确的有限增量许可。

当前三个变化对象的冻结hash如下。

- deploy/initialize_normal.py，29403字节，68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09。
- backend/tests/test_normal_install.py，32786字节，93dabd4887760641884fc7ca5d5c83e520522563ea2d44be4dc2e72db320c3b7。
- deploy/normal-install.md，10845字节，fb553199dafb11be8608a3608ff2f18778f07acbff265badb2994855c0fd6ddb。

未变README、固定清单、安装示例、001—015和原业务/profile/角色检查保持首轮身份与结论。原F126-01/F126-02在主控账仍开放，工程自评不能替代本轮独立判断。原报告hash为b1f52e0284e37b5e67f28ef1a1c2dee7d1c7d255a3e090d1478bc5747d72b1d3，原首轮代码门不通过历史不得追改。

## 最小充分独立输入

1. 根入口、当前有效卡及主控DocuN/evidence/TASK-126/orchestration-review01-20261022/input-manifest.json、raw-evidence-index.json和permit.json，核本轮真实范围和冻结身份。
2. 原TASK125审计修复01合同的范围与验收部分，以及你自己的TASK126首轮F126-01/F126-02及其原始依据。原合同已读内容不重读；不读TASK125统一结果或result-prefix.md，不读工程聊天/思考/自评。偶然接触如实披露，不伪称从未接触。
3. execution/repair-01/changes.patch、pre/中的三产品原件、当前三个完整文件及post副本。先以原始缺陷和合同形成判断，再检查已有测试对实际风险的证明边界。完整源码可读，但审查归属限定本次变化及其传导。
4. 现有psycopg3.3.5的必要驱动源码、当前Python标准库pathlib.py/ntpath.py相关严格resolve/realpath实现。主控清单给出当前实际绝对路径/hash，不猜安装目录。只读源码，不import或执行产品、驱动、安装器CLI。对当前Windows实现判断，Linux并非本轮新增交付平台。
5. repair-01的batch-03-selection、tested-before-batch-03、batch-03-start/command/output/summary、harness/runner、post/pre-snapshot、junction-before、command-ledger及必要旧batch02原件。不要执行它们，也不只信作者的match布尔或硬编码计数。

本轮主控身份元数据用于找到原件，不提供产品优劣预结论。不得把实现报告放进独立输入。原首轮已核的SQL顺序、角色分工、未知提交/不重放等未变主体直接继承；若本次helper修改传导到Journal或apply/verify，则只追对应调用影响。

## 对新增证据的具体核点

F126-01检查test19实际替换驱动入口之前后顺序、局部合成PGHOSTADDR/PGHOST、真实产品connect的direct/apply/verify三用途kwargs和当前驱动显式参数优先关系。保留客户端127.0.0.1映射端口与服务端172.18.0.2:5432不同的语义。不得为了证明修复尝试向非loopback连接或运行真实认证。

F126-02检查test20是否取本机真实GetShortPathNameW/GetLongPathNameW和samefile，backend/deploy/config三类实际别名是否命中同一保护；写入探针是否只阻断写、没有把危险路径先改为安全路径或伪造lstat/物理身份。test21的归一失败分支与原test07正常/冲突、08真实junction及11/12/13收据路径和17脱敏要与实际代码对上。

主控未新增NTFS探针或重建夹具，原junction由已有元数据和原证据引用。本轮若需确认当前fixture，只读lstat/readlink即可，不跟随递归或新建/删除。受信目录下的对手并发替换仍是原条件风险，不将未获证实的任意理论竞态自动升级为新P1；也不能用它掩盖确定的本次别名回归。

batch03原日志9/9、fail/error/skip0及exit0是已有待你核证的客观输入，不要求重跑。测试正文共原18方法加新19/20/21；原18 AST正文相符并不单独证明12未跑方法仍有效，须结合两处产品diff与调用影响判断继承。不得宣称最终21项全跑或把旧18和新9简单相加为不同方法数量。

工程本轮600秒和累计4200/10800是保守账，精确总工具wall仍unknown；实际进程1.7951588000287302秒、harness0.6536168999737129秒和工具外层2.6215342秒不同层级不相加。累计3/4批，batch04未用。保持原批1失败、原中间版未完整存档、平台原批准回执缺失等边界，不能从日历包络直接签精确控制合规。

读取文件名时曾一次误枚举旧scratch的范围偏差已留在本轮账，未声明读旧正文或改删旧对象。按实际证据定级，不补造原始命令或将unknown转成已违规。新增11个测试目录和junction未变记录可以在原summary/post中核对，禁止借审计整理或删除。

## 预算、权限及停止

本轮从原TASK126已封存余量中明确恢复最多1200秒工具，含240秒保存；原保守1800/3600、精确unknown照留，总cap3600不变。原截止2026-10-23T09:56:00.006928+08:00不重置，工具或日历先到门停止；单命令通常60秒，不为用满预算扩审。完成四问即可统一回传。

只允许PowerShell/标准库的有界文件读取、hash、JSON、diff和AST分析，以及保存指定报告/新证据。产品/测试/SQL/配置/README/DocuS/公共库、原审计/工程证据及主控orchestration不可改。不能访问实际local/private配置、.runtime、用户资料/库、凭据或账号后台。

产品导入、CLI/help/plan/apply、compile/unittest、PG/Docker/Compose、端口/服务、浏览器/Job/预览、provider/Embedding/网络、安装依赖/Git写入/费用/委派全部0。不通过执行新harness来确认旧日志，不创建短别名/junction或系统设置。

冻结对象漂移则只停止对应复核，带具体path/hash和影响交回。新确定风险直接由增量引出时定位并说明，不借机扩审整仓；必要缺口保存事实，不能直接修复或虚签关闭。无新增产品变化和直接风险就不得要求再全审或无理由重跑18/9项。

## 回传与验收边界

review-01置顶写独立性、精确范围/读取hash、两项逐一关闭或保留的代码事实、当前三轴结论、9方法字节绑定/继承依据/未验证项、本轮实际命令/时间/失败/unknown和原账累计、最小真实清单差异。原首轮全文及报告hash链完整保留，新增原始输出只存audit/review-01。

报告结论限定为当前代码门可通过/仍不通过及已有证据范围，不签真实PG/认证/ACL/正常安装/正常启动或Q启用。最终TASK125关闭和后续真实资源许可由主控另行裁定；Q继续冻结，T0为空，STEP018/019/020、M1/项目不宣告通过。

无须用户提供key、开服务、释放内存或删文件。保存并复读原结果D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-126-result.md，只回复一句话结论和可点击完整绝对路径，供用户带回。

## 以下为原TASK126完整审计卡 原字节保留

'''


def main():
    now = datetime.now(TZ)
    timestamp = now.isoformat()
    state_rel = 'DocuS/执行动态文档.MD'
    arch_rel = 'DocuS/架构动态文档.MD'
    changes_rel = 'DocuS/文档变更记录.MD'
    task_rel = 'DocuN/tasks/TASK-126.md'
    decision125 = 'DocuN/results/TASK-125-work-decision.md'
    decision126 = 'DocuN/results/TASK-126-work-decision.md'
    before = {name: read(name) for name in (state_rel, arch_rel, changes_rel, task_rel, decision125, decision126)}
    assert '文档v2.95' in before[state_rel].decode('utf-8-sig')[:120]
    assert '文档v1.67' in before[arch_rel].decode('utf-8-sig')[:120]
    assert max(map(int, re.findall(r'CHG-(\d+)', before[changes_rel].decode('utf-8-sig')))) == 1644
    assert sha(before[task_rel]) == 'e456d9c73b04fd8a9c631fc5bf755f741c19d8d45a6d9d1193cba13b889618fc'
    assert not p('DocuN/tasks/TASK-127.md').exists()
    original_audit_permit = load('DocuN/evidence/TASK-126/orchestration-20261022/permit.json')
    assert now < datetime.fromisoformat(original_audit_permit['deadline'])
    closure = load(REPAIR + 'closing-receipt.json')
    tested = load(REPAIR + 'tested-before-batch-03.json')
    post = load(REPAIR + 'post-snapshot.json')
    initial = load('DocuN/evidence/TASK-125/orchestration-repair01-20261022/input-manifest.json')
    original_products = load('DocuN/evidence/TASK-125/execution/post-snapshot.json')['products']
    final_by_path = {item['path']: item for item in tested}
    allowed = set(initial['allowed_product_writes'])
    rows = []

    def verify(source, expected, group, byte_count=None, relative=None):
        raw = Path(source).read_bytes()
        actual = sha(raw)
        assert actual == expected, (str(source), expected, actual)
        assert byte_count is None or len(raw) == byte_count, str(source)
        rows.append({'path': relative or str(source), 'absolute_path': str(source), 'bytes': len(raw),
                     'sha256': actual, 'group': group, 'match': True})

    for item in tested:
        verify(p(item['path']), item['sha256'], 'batch03_tested', item['bytes'], item['path'])
    for item in initial['sources']:
        expected = final_by_path[item['path']]['sha256'] if item['path'] in allowed else item['sha256']
        verify(item['absolute_path'], expected, 'repair_input_preservation', relative=item['path'])
    for item in original_products:
        if item['path'] in allowed:
            verify(p(REPAIR + 'pre/' + item['path']), item['sha256'], 'repair_pre_product', item['bytes'])
            final = final_by_path[item['path']]
            verify(p(REPAIR + 'post/' + item['path']), final['sha256'], 'repair_post_product', final['bytes'])
        else:
            verify(p(item['path']), item['sha256'], 'unchanged_original_product', item['bytes'], item['path'])
        verify(p('DocuN/evidence/TASK-125/execution/post/' + item['path']), item['sha256'], 'immutable_old_post', item['bytes'])
    for item in load('DocuN/evidence/TASK-125/execution/closing-receipt.json')['artifacts']:
        verify(p(item['path']), item['sha256'], 'immutable_original_artifact', item['bytes'], item['path'])
    report_rel = 'DocuN/results/TASK-125-result.md'
    verify(p(report_rel), closure['result']['sha256'], 'returned_report', closure['result']['bytes'], report_rel)
    report = read(report_rel)
    suffix_length = closure['result']['original_suffix_bytes']
    assert sha(report[-suffix_length:]) == closure['result']['original_suffix_sha256']
    assert report[:-suffix_length] == read(REPAIR + 'result-prefix.md')
    for row in post['tested_and_final_bytes']:
        assert row['sha256'] == final_by_path[row['path']]['sha256'] == row['actual_post_sha256']
    summary = load(REPAIR + 'batch-03-summary.json')
    command = load(REPAIR + 'batch-03-command.json')
    selection = load(REPAIR + 'batch-03-selection.json')
    raw_output = read(REPAIR + 'batch-03-output.txt').decode('utf-8')
    assert (summary['tests_run'], summary['failures'], summary['errors'], summary['skipped'], command['exit_code']) == (9, 0, 0, 0, 0)
    assert summary['selected_methods'] == selection['selected_methods']
    assert len(summary['records']) == 9 and raw_output.count(' ... ok') == 9
    assert 'Ran 9 tests' in raw_output and raw_output.rstrip().endswith('OK')
    assert not summary['denied_effect_attempts']
    observed = summary['observations']
    assert [r['purpose'] for r in observed['F126-01']['driver_kwargs']] == ['direct', 'apply', 'verify']
    assert all(r['host'] == r['hostaddr'] == '127.0.0.1' for r in observed['F126-01']['driver_kwargs'])
    assert not observed['F126-02']['blocked_write_probe_calls']
    assert len(observed['F126-02']['directories']) == 3
    old_test_tree = ast.parse(read(REPAIR + 'pre/backend/tests/test_normal_install.py').decode('utf-8-sig'))
    current_test_tree = ast.parse(read('backend/tests/test_normal_install.py').decode('utf-8-sig'))

    def methods(tree):
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'NormalInstallTests')
        return {n.name: ast.dump(n, include_attributes=False) for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}

    old_methods, current_methods = methods(old_test_tree), methods(current_test_tree)
    assert len(old_methods) == 18 and len(current_methods) == 21
    assert all(current_methods[name] == body for name, body in old_methods.items())
    old_code_tree = ast.parse(read(REPAIR + 'pre/deploy/initialize_normal.py').decode('utf-8-sig'))
    new_code_tree = ast.parse(read('deploy/initialize_normal.py').decode('utf-8-sig'))
    old_functions = {n.name: ast.dump(n, include_attributes=False) for n in old_code_tree.body if isinstance(n, ast.FunctionDef)}
    new_functions = {n.name: ast.dump(n, include_attributes=False) for n in new_code_tree.body if isinstance(n, ast.FunctionDef)}
    assert old_functions.keys() == new_functions.keys()
    changed_functions = [name for name in old_functions if old_functions[name] != new_functions[name]]
    assert set(changed_functions) == {'new_output', 'connect'}
    ledger = load(REPAIR + 'command-ledger.json')
    assert ledger['budget']['cumulative_conservative_seconds'] == 4200
    assert ledger['budget']['continuation_conservative_seconds'] == 600
    assert ledger['precise_total_tool_seconds'] is None
    assert ledger['tests']['cumulative_used'] == 3 and not ledger['tests']['batch04_run']
    assert '*' not in CONTRACT and '〈' not in CONTRACT and '| ---' not in CONTRACT
    for relative, old in before.items():
        put(RETURN + 'before/' + Path(relative).name, old)
    dump(RETURN + 'return-check.json', {
        'TASK': 'TASK-125', 'R': 'R-119', 'continuation': 'audit-repair-01', 'checked_at': timestamp,
        'identity_reference_checks': len(rows), 'mismatches': 0, 'rows': rows,
        'changed_product_functions_ast': changed_functions, 'original_18_methods_ast_unchanged': True,
        'selected_methods': summary['selected_methods'], 'actual_method_counts': {'old': 18, 'current': 21, 'batch03': 9},
        'report_suffix_preserved': True, 'original_artifacts_preserved': True,
        'process_seconds': command['elapsed_seconds'], 'harness_seconds': summary['elapsed_seconds'],
        'scope': '文件身份/差异边界与原始离线结果核证，非独审或真实PG验证',
        'product_runtime': 0, 'new_test_runs': 0,
    })
    decision_prefix = f'''# TASK125审计修复01候选已返回，待原126 review-01

{timestamp}，Asia/Shanghai。主控读取修复实际diff与原始9方法，核{len(rows)}条身份引用无漂移。新安装器/测试/说明三文件及本批名单/harness/runner六份受测字节当前相符，pre/post与原26证据/旧post保持；原报告15686字节后缀完整，当前统一报告26676字节/hash{closure['result']['sha256']}。

安装器AST变化仅connect和new_output，测试原18方法正文AST不变、新增19/20/21；主控仅据此确认范围，不把AST相同当动态继承全证明。原batch03选6旧/3新共9方法，原文9/0失败/error/skip及exit0成立，父1.7951588000287302秒、harness0.6536168999737129秒和外层2.6215342秒不同层级不相加。原12未跑方法不称新字节已重跑；真实TCP/认证/PG/ACL未验证。

F126-01/F126-02仍为待独立确认，125当前尚未最终验收，不由主控有限文件核证替代原必需独审。原126同号review-01完整卡已保存待转交，仅核两项及直接影响和9方法绑定，旧未变结论直接继承，运行0。

工程新增600秒/累计4200/10800为保守列支，精确unknown和原失败保持。累计3/4批、batch04未用与当前余量封存，不再自动启动。误枚举旧scratch文件名偏差按原记录保留，不追改为已获批准，也不补造原调用。主控未导入产品、重测或探服务资源。

Q继续冻结、T0为空。真实安装和账号/token/模板/Embedding容量/正常绑定等后继门保持。下方为旧主控裁定原字节，历史失败结论保留。

'''
    put(decision125, decision_prefix.encode('utf-8') + before[decision125])
    audit_prefix = f'''# TASK126 review-01有限增量复核待转交

{timestamp}，Asia/Shanghai。125修复01实际候选及9方法已回收冻结，完整增量合同置顶TASK126卡，交原独审窗口核F126-01/F126-02、当前三文件及直接影响、受测身份/证据与四问结论。尚未转交、接收或启动；原首轮不通过报告与两发现保持开放，不预判关闭。

仅明确恢复原126封存余量中的最多1200工具秒含240保存，原保守1800/3600、精确unknown、原截止2026-10-23T09:56:00.006928+08:00不重置；所有产品/测试/PG/运行/联网额度0。原SQL/角色/其它首轮结论继承，不重新完整审查或重跑9/18方法。修复自评不进入独立输入。

主控本次核{len(rows)}条身份引用与实际diff/原日志，无产品运行，证据只表示原始有限离线事实。下方为原首轮主控裁定原字节，不回写历史失败。

'''
    put(decision126, audit_prefix.encode('utf-8') + before[decision126])
    put(task_rel, CONTRACT.encode('utf-8') + before[task_rel])
    state_prefix = f'''# 执行动态文档

文档v2.96，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.68、task_model/07。以下v2.95原字节保留。

## 125审计修复01候选已返回冻结，原126 review-01待人工转交

{timestamp}。用户带回双缺陷修复候选，主控核{len(rows)}条身份引用无漂移，三产品与batch03六份实际受测输入相符、原26证据/旧post不变、原报告15686字节后缀保留，当前报告26676字节/hash{closure['result']['sha256']}。只改connect/new_output及三新测试和相关说明，SQL/角色/业务与README/固定清单/示例不变。125当前调度已返回冻结，最终缺陷/任务验收仍待独立增量结论。

已有batch03原文9方法/0失败error skip/exit0，父1.7951588/harness0.6536169/外层2.6215342秒分层不相加；原18方法正文AST不变，9方法含6旧3新，未跑12项仅按不受影响范围继承，不称最终21全跑。原失败/unknown及本轮误枚举旧scratch文件名偏差保留。工具精确总unknown，新增保守600/累计4200/10800，3/4批/batch04未用和剩余预算随交回封存不自动恢复。

原TASK126/R120同号review-01完整卡已置顶DocuN/tasks/TASK-126.md，待人工转交刚完成首轮的独立A+窗口，须未参与125修复；不是新占号。只核F126-01/P1、F126-02/P2修正及hash/直接影响/9方法证据，旧未变结论继承。当前两项仍开放待复核，不预写关闭。没有转交/接收/启动事实。

明确恢复126原余量最多1200工具秒含240保存，原保守1800/3600/精确unknown及原24h截止不变；运行/compile/测试/PG/Docker/联网/费用全0，不追审未变整仓。主控本轮无产品导入、测试或服务探针，只作文件/原始证据核对。

Q冻结、T0/72h空，真实PG安装/ACL/正常启动和外部计量/账号/模板/Embedding容量/normal绑定仍未验证或未齐。100/25及固定分额、Must/89动作/24片6索引不变；STEP018进行中/部分验证，019/020/M1/项目不放行。回收证据在TASK125/orchestration-repair01-return-20261022，独审输入/许可在TASK126/orchestration-review01-20261022。CHG1645—1650，下一1651。

## 以下为v2.95及更早历史

'''
    put(state_rel, state_prefix.encode('utf-8') + before[state_rel])
    arch_prefix = f'''# 架构动态文档

文档v1.68，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.96、task_model/07。以下v1.67原字节保留。

## 连接地址和输出物理目录修正已为候选，原独审增量待回收

{timestamp}。125修复01返回connect显式host/hostaddr，以及先逐级拒绝原拼写reparse再对现存父/root严格resolve的输出保护；本机真实短别名和归一失败已有9项定向离线证据，属于候选/待原126独立确认，不预签缺陷关闭或真实PG通过。

变化只在原安装器两函数、测试/说明，固定SQL/角色/业务/配置schema/原启动链不变。合法容器NAT、排他新建、提交未知与完整收据verify语义保留在待核候选；受信目录的对手竞态及真实TCP/认证/PG/ACL仍未验证。原128范围以原记录为准，不新增平台。正常资源和Q启用前置仍保持关闭，阶段整体未完成。

## 以下为v1.67及更早历史

'''.replace('原128范围以原记录为准，', '原首轮范围以原记录为准，')
    put(arch_rel, arch_prefix.encode('utf-8') + before[arch_rel])
    descriptions = [
        (1645, decision125, '置顶修复候选回收/9方法原件及范围核证，缺陷和最终验收待原独审，旧历史保留。'),
        (1646, decision126, '登记原126四问增量待转交及从原余量恢复的有限只读许可，不预判关闭。'),
        (1647, task_rel, '置顶完整review-01合同，仅复核两缺陷/直接影响/实际字节，原完整卡原字节留后。'),
        (1648, arch_rel, 'v1.68登记两处候选加强和9方法证据边界，未变模型/SQL/角色/Q。'),
        (1649, state_rel, 'v2.96登记125修复已返回冻结、126增量待转交、封存工程账及保留前置。'),
        (1650, 'DocuN/evidence/TASK-125/orchestration-repair01-return-20261022及TASK-126/orchestration-review01-20261022', '保存有限身份/原件/AST范围核证、旧共享与增量卡输入/许可/读回；产品运行0。'),
    ]
    additions = '\n\n' + '\n\n'.join(f'- CHG-{n}，{timestamp}，Codex编排Agent，{name}。{text}' for n, name, text in descriptions) + '\n'
    put(changes_rel, before[changes_rel] + additions.encode('utf-8'))
    raw_names = (
        'changes.patch', 'pre-snapshot.json', 'post-snapshot.json', 'tested-before-batch-03.json',
        'batch-03-selection.json', 'batch-03-start.json', 'batch-03-command.json', 'batch-03-output.txt',
        'batch-03-summary.json', 'offline-harness-03.py', 'run-offline-batch-03.py', 'junction-before.json',
        'command-ledger.json',
    )
    audit_sources = [item['path'] for item in tested[:3]]
    audit_sources += [REPAIR + name for name in raw_names]
    audit_sources += [REPAIR + 'pre/' + item['path'] for item in tested[:3]]
    audit_sources += [REPAIR + 'post/' + item['path'] for item in tested[:3]]
    audit_sources += [
        'AGENTS.md', 'DocuN/tasks/TASK-125.md', state_rel, arch_rel,
        'DocuN/results/TASK-126-result.md', 'DocuN/evidence/TASK-126/audit/closure.json',
        'DocuN/evidence/TASK-126/audit/static-analysis-02.json',
        'DocuN/evidence/TASK-125/orchestration-repair01-20261022/permit.json',
        'DocuN/evidence/TASK-125/execution/batch-02-summary.json',
        'DocuN/evidence/TASK-125/execution/tested-before-batch-02.json',
        'DocuN/evidence/TASK-125/execution/post-snapshot.json',
        'deploy/normal_install_manifest.json', 'config/normal-install.example.json', 'README.md',
        'DocuN/evidence/v4-migration-20260930/rules-snapshot.json',
    ]
    identities = []
    for relative in dict.fromkeys(audit_sources):
        raw = read(relative)
        identities.append({'path': relative, 'absolute_path': str(p(relative)), 'bytes': len(raw), 'sha256': sha(raw)})
    stdlib_root = Path(sys.base_prefix) / 'Lib'
    for source in (stdlib_root / 'pathlib.py', stdlib_root / 'ntpath.py'):
        raw = source.read_bytes()
        identities.append({'path': str(source), 'absolute_path': str(source), 'bytes': len(raw),
                           'sha256': sha(raw), 'kind': 'installed_stdlib_readonly'})
    for source in (ROOT / 'backend/.venv/Lib/site-packages/psycopg' / name for name in
                   ('connection.py', '_connection_base.py', '_conninfo_utils.py', '_conninfo_attempts.py')):
        raw = source.read_bytes()
        identities.append({'path': str(source), 'absolute_path': str(source), 'bytes': len(raw),
                           'sha256': sha(raw), 'kind': 'installed_driver_readonly'})
    for item in load('DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
        raw = Path(item['absolute_path']).read_bytes()
        assert sha(raw) == item['sha256']
        identities.append({'path': item['relative_path'], 'absolute_path': item['absolute_path'], 'bytes': len(raw),
                           'sha256': sha(raw), 'public_readonly': True})
    manifest = dump(REVIEW + 'input-manifest.json', {
        'TASK': 'TASK-126', 'R': 'R-120', 'continuation': 'review-01', 'issued_at': timestamp,
        'source_count': len(identities), 'sources': identities,
        'current_changed_products': tested[:3], 'excluded': ['DocuN/results/TASK-125-result.md',
            REPAIR + 'result-prefix.md', '工程聊天/思考/自评', '私有配置/.runtime/用户库/凭据'],
    })
    index = dump(REVIEW + 'raw-evidence-index.json', {
        'TASK': 'TASK-126', 'R': 'R-120', 'continuation': 'review-01',
        'upstream_contract': 'DocuN/tasks/TASK-125.md', 'diff': REPAIR + 'changes.patch',
        'pre_root': REPAIR + 'pre/', 'post_root': REPAIR + 'post/',
        'raw_artifacts': [REPAIR + name for name in raw_names],
        'batch03_selected_methods': selection['selected_methods'],
        'inheritance_candidates': selection['inherited_without_rerun'],
        'original_audit_report': 'DocuN/results/TASK-126-result.md',
        'original_audit_report_sha256': sha(read('DocuN/results/TASK-126-result.md')),
        'current_findings_status': {'F126-01': 'OPEN pending independent review', 'F126-02': 'OPEN pending independent review'},
        'proof_limit': '原始离线参数/文件元数据/控制流，不是TCP/认证/真实PG或控制全量精确证明',
    })
    permit = dump(REVIEW + 'permit.json', {
        'schema': 'retrolume.task-scope.v1', 'TASK': 'TASK-126', 'R': 'R-120', 'continuation': 'review-01',
        'issued_at': timestamp, 'deadline': original_audit_permit['deadline'],
        'full_current_card_sha256': sha(read(task_rel)), 'effective_contract_prefix_sha256': sha(CONTRACT.encode('utf-8')),
        'historical_full_card_sha256': sha(before[task_rel]), 'input_manifest_sha256': sha(manifest.read_bytes()),
        'raw_evidence_index_sha256': sha(index.read_bytes()), 'dispatch_status': '待人工转交', 'acceptance': None,
        'recipient': 'A+原TASK126独审窗口，未参与125修复',
        'historical_conservative_tool_seconds': 1800, 'historical_exact_tool_seconds': None,
        'historical_tool_cap_seconds': 3600, 'unsealed_tool_extra_cap_seconds': 1200,
        'reserved_close_seconds': 240, 'per_command_seconds': 60,
        'allowed_writes': ['DocuN/evidence/TASK-126/audit/review-01/', 'DocuN/results/TASK-126-result.md'],
        'caps': {name: 0 for name in ('product_import', 'installer_cli', 'compile', 'test', 'pg', 'docker', 'service',
            'browser', 'job', 'preview', 'provider', 'embedding', 'network', 'dependency_install', 'git_write', 'fee_cny', 'delegation')},
        'Q': 'FROZEN', 'T0': None,
    })
    for row in identities:
        assert sha(Path(row['absolute_path']).read_bytes()) == row['sha256'], row['path']
    for relative, old in before.items():
        if relative == changes_rel:
            assert read(relative).startswith(old)
        else:
            assert read(relative).endswith(old)
    assert sha(read(report_rel)) == closure['result']['sha256']
    assert sha(read('DocuN/results/TASK-126-result.md')) == 'b1f52e0284e37b5e67f28ef1a1c2dee7d1c7d255a3e090d1478bc5747d72b1d3'
    proof = {
        'TASK': 'TASK-126', 'R': 'R-120', 'continuation': 'review-01', 'issued_at': timestamp,
        'checked_at': datetime.now(TZ).isoformat(), 'status': '待人工转交',
        'engineering_return_identity_checks': len(rows), 'audit_input_identities': len(identities), 'mismatches': 0,
        'effective_contract_bytes': len(CONTRACT.encode('utf-8')), 'full_current_card_bytes': len(read(task_rel)),
        'full_current_card_sha256': sha(read(task_rel)), 'permit_sha256': sha(permit.read_bytes()),
        'source_manifest_sha256': sha(manifest.read_bytes()), 'shared_state_version': '2.96',
        'architecture_version': '1.68', 'next_CHG': 1651,
        'original_reports_unchanged': True, 'historical_shared_and_card_bytes_preserved': True,
        'F126-01': 'OPEN pending review', 'F126-02': 'OPEN pending review', 'new_test_runs': 0,
        'product_runtime': 0, 'Q': 'FROZEN', 'T0': None,
    }
    dump(REVIEW + 'save-proof.json', proof)
    dump(RETURN + 'return-receipt.json', {
        'TASK': 'TASK-125', 'R': 'R-119', 'continuation': 'audit-repair-01', 'checked_at': timestamp,
        'dispatch': '已返回', 'candidate_received': True, 'acceptance': '待独立增量确认，原失败未改',
        'report_sha256': closure['result']['sha256'], 'verification_sha256': sha(read(RETURN + 'return-check.json')),
        'budget_sealed': True, 'cumulative_conservative_seconds': 4200, 'exact_total_seconds': None,
        'cumulative_batches': 3, 'batch04_run': False, 'next': 'TASK126/R120 review-01待人工转交',
        'new_product_runs': 0, 'Q': 'FROZEN',
    })
    print(json.dumps({key: proof[key] for key in ('TASK', 'R', 'continuation', 'status',
        'engineering_return_identity_checks', 'audit_input_identities', 'mismatches',
        'full_current_card_bytes', 'next_CHG', 'new_test_runs', 'Q')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
