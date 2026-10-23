"""核收安装前三项原件并登记零运行集中审计；只维护文件和共享状态。"""
import difflib
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
PUBLIC = Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
E0 = ROOT / 'DocuN/evidence/TASK-128/execution'
E1 = E0 / 'continuation-01'
RETURN = ROOT / 'DocuN/evidence/TASK-128/orchestration-return-continuation01-20261023'
OUT = ROOT / 'DocuN/evidence/TASK-129/orchestration-20261023'
CARD = ROOT / 'DocuN/tasks/TASK-129.md'
DECISION = ROOT / 'DocuN/results/TASK-128-work-decision.md'
STATE = ROOT / 'DocuS/执行动态文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def js(path):
    return json.loads(path.read_bytes())


def identity(path):
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': sha(data)}


def save_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as stream:
        stream.write(data)
    assert path.read_bytes() == data


def main():
    for path in (OUT, RETURN, CARD, DECISION, STATE, ARCH, CHANGE):
        for parent in [path, *path.parents]:
            if parent.exists():
                stat = parent.lstat()
                assert not parent.is_symlink() and not getattr(stat, 'st_file_attributes', 0) & 0x400, str(parent)
            if parent == ROOT:
                break
        else:
            raise RuntimeError('输出路径不在项目')
    assert not CARD.exists() and not (OUT / 'permit.json').exists(), '已有新卡或部分登记，先核断点'
    old_state, old_arch, old_change, old_decision = STATE.read_bytes(), ARCH.read_bytes(), CHANGE.read_bytes(), DECISION.read_bytes()
    assert '文档v3.00' in old_state.decode('utf-8-sig').splitlines()[2]
    assert '文档v1.72' in old_arch.decode('utf-8-sig').splitlines()[2]
    assert 'CHG-1672' in old_change.decode('utf-8-sig')[-1800:] and 'CHG-1673' not in old_change.decode('utf-8-sig')
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp, deadline = now.isoformat(), (now + timedelta(hours=24)).isoformat()
    report_path = ROOT / 'DocuN/results/TASK-128-result.md'
    report = identity(report_path)
    readback = js(E1 / 'result-readback.json')
    assert report['sha256'] == readback['sha256'] == '472882152a5283bf0ff36d72ff1b73b7a9822e1cfff4dda5c0afa942950efc55'
    assert report['bytes'] == readback['bytes'] == 25623 and not readback['missing_links']
    assert sha(report_path.read_bytes()[-13923:]) == 'fd9445acbca5abe2d3b1daa8bfb8f0793d6be24ba9e70a08b7628de09b4e0558'
    post = js(E1 / 'post-snapshot.json')
    checks = []
    historical_report_binding = []
    for row in post['inputs']:
        path = Path(row['path'])
        actual = identity(path)
        if path == report_path and actual['sha256'] != row['sha256']:
            assert row['sha256'] == sha(report_path.read_bytes()[-13923:])
            historical_report_binding.append({'as_run_sha256': row['sha256'], 'current': actual,
                                              'basis': '结果在运行结束后置顶追加，原13923字节后缀完整；非产品漂移'})
        else:
            assert actual['sha256'] == row['sha256'], str(path)
            checks.append({**actual, 'category': 'post_input', 'match': True})
    rules = js(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
    for row in rules:
        path = PUBLIC / row['relative_path'].replace('\\', '/')
        actual = identity(path)
        assert actual['sha256'] == row['sha256']
        checks.append({**actual, 'category': 'locked_rule', 'match': True})
    assert post['rules_unchanged'] == 7
    baseline = js(ROOT / 'DocuN/evidence/TASK-128/orchestration-continuation01-20261023/input-manifest.json')['current_product_baseline']
    allowed = {row['path']: row for row in post['changes']}
    assert set(allowed) == {'deploy/initialize_normal.py', 'backend/tests/test_normal_install.py', 'deploy/normal-install.md', 'README.md'}
    products = []
    for row in baseline:
        relative = row['relative_path']
        expected = allowed[relative]['after_sha256'] if relative in allowed else row['sha256']
        actual = identity(ROOT / relative)
        assert actual['sha256'] == expected, relative
        products.append({**actual, 'relative_path': relative})
        checks.append({**actual, 'category': 'product_with_allowed_four_changes', 'match': True})
    for relative, row in allowed.items():
        assert sha((E1 / 'pre' / relative).read_bytes()) == row['before_sha256']
        assert sha((E1 / 'post' / relative).read_bytes()) == row['after_sha256']
    tests = js(E1 / 'targeted-tests.json')
    assert (tests['run'], tests['failures'], tests['errors'], tests['passed']) == (3, 0, 0, True)
    for path, expected in tests['before_after_identical'].items():
        assert sha(Path(path).read_bytes()) == expected
    check1, check2, check3 = js(E1 / 'entry-06/check1.json'), js(E1 / 'entry-06/check2.json'), js(E1 / 'entry-06/check3.json')
    assert [row['case'] for row in check1] == ['database_oid', 'system_identifier', 'nonempty', 'role_collision']
    assert [row['output']['reason'] for row in check1] == ['target_identity_mismatch', 'target_identity_mismatch', 'target_not_empty_or_exclusive', 'global_role_collision']
    assert all(row.get('writes', 0) == 0 for row in check1)
    receipt_path = E1 / 'entry-06/source-success-receipt.jsonl'
    assert sha(receipt_path.read_bytes()) == 'a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06'
    receipt = [json.loads(line) for line in receipt_path.read_text(encoding='utf-8').splitlines()]
    stages = [f'{n:03}' for n in range(1, 14)] + ['normal_control', '014', '015', 'login_roles']
    assert len(receipt) == 37 and receipt[0]['event'] == 'intent' and receipt[1]['event'] == 'preflight'
    for index, stage in enumerate(stages):
        assert receipt[2 + 2*index] == {'event': 'submitted', 'stage': stage}
        assert receipt[3 + 2*index] == {'event': 'confirmed', 'stage': stage}
    assert receipt[-1] == {'event': 'complete', 'confirmed_stages': stages, 'schema_profile': 'data_exit.v1.r03'}
    assert check2['output']['status'] == 'installed' and check2['output']['confirmed_stages'] == stages and check2['receipt_lines'] == 37
    assert [row['purpose'] for row in check3] == ['business', 'snapshot']
    for row, login in zip(check3, ('retrolume_normal_app', 'retrolume_normal_snapshot')):
        assert row['actual_login']['current_user'] == row['actual_login']['session_user'] == login
        assert row['actual_login']['reads_maintenance'] is False
        assert row['control']['schema_profile'] == 'data_exit.v1.r03'
    role_crosscheck = js(E1 / 'receipt-role-crosscheck.json')
    assert role_crosscheck['actual_permission_refusals'] == 5
    for name in ('stage-api1-failure.json', 'stage-5-failure.json'):
        assert js(E1 / 'entry-06' / name)['reason'] == 'startup_memory_below512'
    memories = [json.loads(line)['available_mib'] for line in (E1 / 'entry-06/memory.jsonl').read_text().splitlines()]
    assert min(memories) == 105.33203125
    assert post['entries_cumulative'] == 6 and post['api_starts'] == post['api_holding_seconds'] == 0
    assert abs(post['pg_holding_cumulative_seconds'] - 34.1386296749115) < .000001
    assert post['no_listeners'] is True and post['secret_matches'] == 0
    for slot in ('source', 'interrupted'):
        assert post['objects'][slot]['state']['Running'] is False and post['objects'][slot]['state']['Pid'] == 0
    helpers = js(E1 / 'entry-06/as-run.json')['helpers']
    for row in helpers:
        copy = E1 / 'entry-06' / Path(row['path']).name
        assert sha(copy.read_bytes()) == row['sha256'] and copy.stat().st_size == row['bytes']
        checks.append({**identity(copy), 'category': 'entry06_as_run_copy', 'match': True})

    OUT.mkdir(parents=True, exist_ok=True)
    RETURN.mkdir(parents=True, exist_ok=False)
    before = RETURN / 'before'
    before.mkdir(exist_ok=False)
    for path, data in [(STATE, old_state), (ARCH, old_arch), (CHANGE, old_change), (DECISION, old_decision)]:
        (before / path.name).write_bytes(data)
    return_check = {'checked_at': stamp, 'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作01回收',
                    'result': report, 'identity_reference_checks': len(checks), 'mismatches': 0, 'checks': checks,
                    'historical_report_binding': historical_report_binding,
                    'checks_1_2_3': '原始有限运行证据核收；完整安装成果未验收关闭，集中增量审计待执行',
                    'checks_4_5_6': 'not_run_capacity_blocked', 'current_open_new_code_defect_claimed': False,
                    'memory_min_mib_in_last_batch': min(memories), 'runtime_live_probe_by_main': 0,
                    'source_success_receipt': identity(receipt_path), 'no_installation_replay': True,
                    'runtime_permission_restored': False, 'new_task': 'TASK-129/R-123'}
    save_json(RETURN / 'return-check.json', return_check)
    decision_prefix = f'''# TASK-128 / R-122 续作01主控回收裁定

{stamp}，Asia/Shanghai。核{len(checks)}条当前身份引用零漂移；运行后结果从13923追加为25623字节/hash{report['sha256']}，原13923后缀完整，此项不是产品漂移。41产品只四份允许变化、三方法before/after实际绑定与真实37行/17阶段收据相符。

## 当前验收与阻断

调度已返回并停止；前三项真实拒绝/安装/角色权限证据按范围核收，任务验收仍部分通过、未完成。连接与主机格式候选稳定，未发现本次结果声称新的代码失败；前三项的最终安装安全成果尚待TASK129集中独立增量审查，不凭主控文件核对代签。第四/五/六项仍未执行，API0，中断注入0，verify未跑。

本批可用内存采样最低105.33203125MiB，API与中断槽位均在Popen/start前被512MiB门拒绝。不是API实际启动失败或中断恢复反例失败；原post时点两精确CID已停止、无监听，主控未现场重新采样/操作。现有正常源已成功安装且收据完整，禁止重放001—015、重建或丢弃成果。

连续保守工具8400/10800秒、精确unknown，未用2400封存；入口6/7、source4/5、interrupted1/2、API0/3，PG持有34.1386296749115/1800、API0/900。entry07原仅适用于夹具条件，容量不满足不借它恢复。当前不签新PG/API许可，也不再发只为等待内存的同类试跑卡。以后最小资源条件具备再一次合并第四/五/六项，必须重新核完整生命周期所需余量，现剩一次source启动不够两个跨PG周期，不能隐增或伪重开。

## 对编排延误的收敛

局部授权/启动次数切分过细，曾使有剩余时间的普通修复也停线转卡；实际安装兼容缺陷暴露偏晚。后续围绕正常部署、完整学习/面试验收、最终自用交付三个现有收尾成果推进，复用充分证据，不加入Linux/Nginx或增强功能。内存阻断只限相关真实运行，先进行不需要产品启动的必要集中审查。

TASK129/R123完整只读卡已登记，接收A+原126独立窗口且未参与127/128；不可续则新隔离窗。一次核两函数/三定向方法、实际两轮差异、前三项原件及执行控制，不重审旧整仓，不运行产品或额外PG。剩余三项动态保持缺口，后续未变代码不再重复审；新变更/风险才增量核。本卡不是STEP019完整验收，也不签Q/STEP/项目通过。原128工程写入与运行冻结。

以下保留首轮主控裁定原字节。

'''.encode('utf-8')
    DECISION.write_bytes(decision_prefix + old_decision)

    # 独审输入只给原目标、最终差异、源码和原始证据，不给工程自评/主控裁定。
    full_diffs = []
    for relative in ('deploy/initialize_normal.py', 'backend/tests/test_normal_install.py', 'deploy/normal-install.md', 'README.md'):
        before_bytes = (E0 / 'pre' / relative).read_bytes()
        current = (ROOT / relative).read_bytes()
        full_diffs.extend(difflib.unified_diff(before_bytes.decode('utf-8-sig').splitlines(keepends=True),
                                             current.decode('utf-8-sig').splitlines(keepends=True),
                                             fromfile='TASK128-pre/' + relative, tofile='final/' + relative))
    (OUT / 'two-repairs-final.diff').write_text(''.join(full_diffs), encoding='utf-8', newline='\n')
    raw = []
    for path in sorted((E1 / 'entry-06').iterdir()):
        if path.is_file():
            raw.append(identity(path))
    for base, names in [
        (E0, ['changes.diff', 'targeted-tests.json', 'targeted-tests-as-run.py', 'diagnostic-safety.json', 'nat-reproduction.json', 'failure-ledger.json', 'post-snapshot.json']),
        (E0 / 'entry-04', ['as-run.json', 'diagnose.py', 'connection-comparison.json', 'credentials-equal.json']),
        (E0 / 'entry-05-ready', ['as-run.json', 'verify-connection.py', 'fixed-formal-connection.json', 'real-preflight.json', 'actual-empty-facts.json']),
        (E1, ['changes.diff', 'targeted-tests.json', 'targeted-tests.py', 'final-run-inputs.json', 'failure-ledger.json', 'post-snapshot.json', 'pre-snapshot.json', 'checkpoint.json', 'receipt-role-crosscheck.json'])]:
        for name in names:
            raw.append(identity(base / name))
    raw_index = {'TASK': 'TASK-129', 'R': 'R-123', 'issued_at': stamp, 'sources': raw,
                 'source_self_assessment_excluded': True, 'current_dynamic_remainder_not_run': [4, 5, 6]}
    save_json(OUT / 'raw-evidence-index.json', raw_index)
    originals = []
    for relative in ('deploy/initialize_normal.py', 'backend/tests/test_normal_install.py', 'deploy/normal-install.md', 'README.md'):
        originals.append(identity(E0 / 'pre' / relative))
        originals.append(identity(E1 / 'pre' / relative))
    manifest = {'TASK': 'TASK-129', 'R': 'R-123', 'issued_at': stamp,
                'requirements_version': '1.4', 'architecture_version': '1.73', 'state_version': '3.01',
                'products': products, 'before_sources': originals,
                'root_entry': identity(ROOT / 'AGENTS.md'),
                'original_contracts': [identity(ROOT / 'DocuN/tasks/TASK-127.md'), identity(ROOT / 'DocuN/tasks/TASK-128.md')],
                'rules': [{'path': row['absolute_path'], 'sha256': row['sha256']} for row in rules],
                'raw_evidence_index': identity(OUT / 'raw-evidence-index.json'),
                'finite_diff': identity(OUT / 'two-repairs-final.diff'),
                'exclude': ['TASK-128-result正文及实现聊天/思考', 'TASK-128-work-decision', '主控return-check及共享文档验收自评段']}
    save_json(OUT / 'input-manifest.json', manifest)
    task = '''# TASK-129 / R-123 首次安装两处修复与前三项真实证据集中独立审查

## 目标与交付

你是A+独立审计者，优先继续原TASK126独立审计窗口，必须未参与TASK127/128及其修复；窗口不可续或曾参与工程则新隔离会话。不能用原工程窗口自审。实际客户端/模型如实登记；人工转卡，不开并行子Agent。

一次集中审查当前稳定的connect服务选择隔离、observe_identity完整主机地址表示兼容、三项定向测试和前三项真实安装证据及控制。判断是否存在确定缺陷、前三项原始事实能否采纳、剩余最小动态缺口是什么。独立审计不依赖空闲内存达到PG/API门，本卡产品运行0。

结果保存D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-129-result.md；只可写该报告和D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/。不修代码、不改测试/迁移/配置/旧证据或DocuS，不签TASK128最终关闭、STEP019整体验收、Q或项目通过。

## 项目、规则及原始约束

真实项目根D:/shspic/project_NO3_RetroLume-agent；入口该根AGENTS.md。task_model V4.0/公共AGENTS CHG-0003；公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。按根入口读公共DocuS/AGENTS.MD和必要WORK合同/审计/停止章节；同窗有效材料复用，不自动采用新版本。锁定指纹在项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。

需求v1.4、架构v1.73、执行动态v3.01；关联TASK128/R122、127/R121及125/126，STEP018部署前置、STEP019适用安全证据、STEP020本机交付。当前只审两处新增边界和其真实影响；原126已审未变SQL/角色/profile/目录保护等继续按原范围使用，不重审整仓。新权限/迁移写入执行已由原用户采用包与工程卡限定，本卡自己无运行权限。

输入/原件索引/有限统一diff/新许可在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/orchestration-20261023/。签发@STAMP@，日历截止@DEADLINE@，Asia/Shanghai；工具wall最多2400秒含480保存，单次普通读取/静态分析命令<=60秒。全程PG、Docker、API、浏览器、Job、compile/测试/构建、产品import、网络/provider、安装/依赖、费用、删除及Git写均0。标准库只读hash/JSON/diff/AST分析可以，用于查原件，不能执行产品。

本卡新只读投入独立登记，原128连续保守8400/10800、精确unknown、入口6/7、source4/5/interrupted1/2/API0/3、PG持有34.1386296749115/1800和所有旧失败均封存，不恢复工程许可、不重置或消耗旧资源余额。原128产品与证据已交回冻结，没有并行工程；源码漂移则停止相关结论并带精确差异回主控。

## 独立输入和读取顺序

先读根入口/锁定公共规则、本卡全文，再核input-manifest与raw-evidence-index中当前产品、两轮pre副本、实际as-run及原始日志。只按必要原需求/约束阅读下述两目标。

- 连接必须显式限定loopback host/hostaddr和精确端口/库/登录/秘密；不能由PGSERVICE/PGSERVICEFILE或PGHOSTADDR等隐式环境把认证送去别处，不能读取用户service配置或改全局环境。连接错误公共输出脱敏，异常观察亦不能泄秘密。
- 服务端NAT地址允许区别于客户端127.0.0.1和映射端口，但database/OID/systemid/installer与session login、superuser、PG17、UTF8和端口等式/类型不得放宽。原裸IPv4/IPv6及完整主机掩码/32、/128合法，短前缀/非法值拒绝；收据保留真实观察值，正常verify不得伪造相等。
- 原首次安装只能对独立新空库/排他目标；先正确预检，再四种可区分拒绝，两个精确临时对象只按本卡创建OID撤销；001—015原SQL不改、各自事务，013后normal/R01、014/R02、015/R03；17阶段37行成功收据与真实提交相互支持。业务/快照登录权限必须实际认证，与安装管理员分离。

查看DocuN/tasks/TASK-127.md的原六项和TASK-128.md当前完整合同的范围/资源/预算/停止条款。合同历史中的事实结论不作为证明；以源码和原始证据独立判断。原独审未变结论可按适用范围参考，不能把修后新代码自动视为原审通过。

本卡不读TASK128结果正文、实现者完整聊天/思考、自评或主控work-decision/return-check/共享文档验收段。当前结果是运行结束后在旧13923字节报告前追加，所以旧as-run中该报告hash不等当前属于阶段性报告更新；它不是被审产品，不为审其自评去读正文，不把这一个可变报告项机械当源码漂移。当前版本/必要约束已经由本合同给全，无需读取完整共享历史。

必要源码为deploy/initialize_normal.py、backend/tests/test_normal_install.py、deploy/normal_install_manifest.json、README/normal-install对应说明，以及原data_exit schema_checks/schema_profiles/q_roles等直接依赖。原始两轮产品pre快照、两次变化diff和最终有限合并diff均在manifest；按原字节/hash核对，不能只看作者列的函数名。只读原SQL及角色前提到足以解释真实结果，不重新检查全部业务。

当前安装器29865字节/hash7cd62b4f3526510c6f38de2a033a01d6ae36bcd661e90dbaca6b551db8141ba8，测试35468字节/hash2357a7031d2da858224d75b56ee0173a3166b0ca68c6905994009b7e64e6b3c3；其余逐项身份以input-manifest为准。冻结不是预先通过结论。

## 一次审查的五项标准

1. connect的实际安全与兼容。

独立对照原与最终源码和当前驱动直接依赖，查移除service空串是否解决原API行为，PGSERVICE/PGSERVICEFILE非空或空值的存在都在驱动前拒绝且环境不被修改；保持host/hostaddr、精确秘密来源、超时/search_path/SSL、direct/apply/verify共用连接、合法NAT与公共脱敏。核真实同秘密对照和修后认证的对象/版本绑定，合成异常脱敏有无漏出DSN/秘密或吞掉故障；不要求再次真实认证或测试对手服务。

2. observe_identity的主机格式与身份门。

只兼容完整主机语义、拒非主机前缀和非法地址；保持其他目标身份等式、异常路径和收据观察值原样。实际172.19.0.2/32的原拒绝、回放和修后真实预检要分层，回放不能充作额外真实运行。检查测试19/22/23能区分旧坏行为、合法表示与非法/错身份，未弱化正确断言；实际受测hash与最终一致。普通格式边界若不构成缺陷只记观察，别任意扩大到新协议/平台。

3. 前三项真实事实与证据链。

核entry06 as-run、相邻真实命令/退出码/trace/收据和helper源码，真实驱动未被Recorder、改SQL/guard/核验替代。四反例分别命中预定原因，安装器零写和两临时对象精确撤销有依据，不能都被other_clients挡住。源成功收据实际37行/17个submitted+confirmed+complete及逐次COMMIT观察/R01-R03吻合，不由顶层exit0或单末行installed冒充成功。安装后原schema/role能力核验及两个实际current_user=session_user登录/权限拒绝吻合，无持久业务测试数据。

核实际目标CID/systemid/OID/卷/root与原创建身份连续，不能因两库OID一样而混淆。来源仅两个原独立槽位：source CID db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d、127.0.0.1:55482、systemid7699647093882925094；interrupted CID549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8、55483、systemid7699647123872251942，本轮中断槽位未重新连接。不得把未运行第四/五/六项补写为PASS。

4. 控制事实与容量停止。

按原许可/as-run时间分清累计5→6入口、source3→4次与受门阻止的API/中断启动。核startup512与运行连续两次<256策略实际采样、失败在Popen/start前而计数未消耗、最低105.33203125与下一样本情况；不要把启动门阻断叫产品启动失败或把一次低于256叫连续退出。核按精确CID停止/保留/端口，未新增资源/重建/换身份/角色密码重置/删卷/clear/付费；工具精确unknown/保守占用保持，不倒造精确账。原历史执行控制问题照留，不能用本次新证据追认旧不合规。

5. 范围结论与后续最小项。

代码轴、证据轴、控制轴分别给结论，缺陷写严重度/源码或证据定位/触发/影响/最小修正，区分确定缺陷、条件风险、未验证和普通观察。对前三项原始事实给可采纳范围；余第四API跨PG重开、第五002真实提交未知、第六成功收据verify继续not_run。本卡可以完成对稳定两处代码及前三证据的独审交付，即使余三动态仍未完成；不能因此给整安装/Q/STEP/项目放行，也不因余三缺失把已查代码结论一概写证据不足。

后续只需原成功源不可重装、同身份补余三项；提出确有依赖的最小缺口及已有原件标识，不默认重跑前三/19-23/旧18-9或全安全矩阵，不把既有非阻断观察变成新硬门。若无新代码/风险，后续仅凭新的真实动态证据可更新事实，无须把这两函数重新全审一遍。普通用户文案只检查未冒称未跑项目已完成。

## 边界、审计完整性与停止

仅读上述源码/合同/必要直接依赖及原件索引，不枚举无关工作区或用户配置。不读DPAPI密文/凭据/DSN或运行环境，不探Docker/端口/内存，不启动任何服务。如果确需验证成功收据副本与私有原件同字节，只可按原始命令中精确收据路径及安全父链对该单一非敏感安装收据作只读hash，不触碰其他私有配置；不是数据库查询许可。否则明确副本身份支持范围即可，不为更强证明制造运行。

审计只写新audit目录与结果；无产品修复/测试/compile/安装、联网/费用、Git和删除。冻结漂移、发现明确数据破坏/越权风险先保全原件交回；其余完成上述一次集中范围。单项疑点依据充分即定界，不重复审未变模块；两次分析方法有据修正仍不稳或预算到门，报告准确缺口并停，不改标准造绿。

记录读入范围/hash/有限diff、独立性及偶然暴露；已接触工程自评就披露内容/时点，不伪称未接触。不能确认原窗口独立则新隔离窗口，不以换模型重置本卡投入；若既有窗口不参与实现且上下文有效可直接复用。

## 保存回传与共享维护

报告先一句三轴结论/代码缺陷与可采纳范围，随后给TASK129/R123/STEP关系、对象/独立性/真实模型、逐项事实与定位、证据分级、失败/未验证/容量边界、工具投入/剩余、最小修正或后续项、文档建议和必要人工。不抄实现者聊天/自评，不填写主控最终验收。

保存D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-129-result.md并复读；需要补证同号追加保留历史，不能覆盖旧失败。DocuS/共享状态/编号由主控维护，本卡只报告实际待同步内容。当前必要人工仅用户转交和带回路径，无须提供密钥/账单/释放内存/手工建库或清理资源。最终只回一句结论与可点击结果绝对路径。
'''.replace('@STAMP@', stamp).replace('@DEADLINE@', deadline)
    assert '*' not in task and '\n|' not in task
    registered = f'# 执行动态文档\n\n文档v3.01，2026-10-23，Asia/Shanghai。需求v1.4、架构v1.73。\n\n{stamp}。128续作01已返回，129/R123只读集中审计已登记，完整卡保存核读中，未派发。\n\n'.encode('utf-8')
    STATE.write_bytes(registered + old_state)
    with CARD.open('xb') as stream:
        stream.write(task.encode('utf-8'))
    assert CARD.read_text(encoding='utf-8') == task
    permit = {'TASK': 'TASK-129', 'R': 'R-123', 'issued_at': stamp, 'valid_until': deadline,
              'status': '待人工转交', 'actual_dispatch': False, 'acceptance': None,
              'receiver': 'A+，未参与127/128的原126独审窗口；不可续则新隔离窗',
              'task_card': identity(CARD), 'input_manifest': identity(OUT / 'input-manifest.json'),
              'raw_evidence_index': identity(OUT / 'raw-evidence-index.json'),
              'tool_wall_seconds': 2400, 'save_reserve_seconds': 480, 'per_read_command_seconds': 60,
              'product_runtime': 0, 'tests_compile_build': 0, 'pg_docker_api_browser': 0,
              'network_provider_fees': 0, 'git_write': 0, 'old_engineering_budgets_not_restored': True,
              'Q': 'FROZEN', 'T0': None}
    save_json(OUT / 'permit.json', permit)
    arch_prefix = f'''# 架构动态文档

文档v1.73，2026-10-23，Asia/Shanghai。需求v1.4、执行动态v3.01、task_model/07。以下v1.72原字节保留。

## 正常源首次安装及两登录已具真实证据，运行余项受容量门阻断

{stamp}。128续作01已落地主机格式兼容候选；三定向方法绑定实际字节通过，原正确preflight/四反例、001—015及17阶段37行成功收据、实际业务/快照登录权限已有原始真实证据。normal控制行R01/R02/R03与三UUID保持，未改SQL/角色/profile或业务。源安装已成功，后续不可重放或重建。

API两周期/跨PG重开、002提交未知与独立成功verify仍未执行，因可用物理内存低于512MiB门在启动前拦截，不能当API产品失败或完整部署已过。原post两CID已停、数据保留；主控未现场操作。当前代码两处增量稳定，129仅集中独审连接/主机表示边界及前三真实原件，旧未变范围继承，运行不依赖审计重新启动产品。

没有新功能/模型/平台。收口仍为正常部署余缺、真实模型完整学习/面试及既定Must、最终安全/自用交付；Linux/Nginx与增强格式不加入Windows首版Must。Q冻结、T0空和外部计量/账号/token/模板/容量门保持，所有阶段/项目最终通过未签。

## 以下为v1.72及更早历史

'''.encode('utf-8')
    ARCH.write_bytes(arch_prefix + old_arch)
    state_prefix = f'''# 执行动态文档

文档v3.01，2026-10-23，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.73、task_model/07。以下v3.00原字节保留。

## 128前三项真实成果已核收，运行因容量停止；129集中只读审计待转交

{stamp}。用户带回128续作01并询问项目迟延，主控核{len(checks)}条当前引用无漂移；报告25623字节/hash472882152a5283bf0ff36d72ff1b73b7a9822e1cfff4dda5c0afa942950efc55、原13923后缀完整。运行时旧报告hash与当前不同是运行后追加的阶段性变化，已单列核证，不误判产品漂移。三定向方法19/22/23最终字节一致，41产品仅四允许项变化，七规则不变。

TASK128/R122续作01实际已返回/停止，验收仍部分通过、未完成。前三项四类可区分拒绝/完整001—015/两个实际登录权限已有原件，17阶段37行成功收据hasha2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06及控制行R01/R02/R03、五次42501与真实trace相互对应。先核收有限运行事实，最终安装安全仍待集中独审；已成功正常源不得重放安装/重建或丢弃。

第四API跨PG重开、第五002真实提交未知、第六成功收据verify均not_run。API Popen与interrupted start前被512MiB可用内存门挡住，内存样本最低105.33203125MiB，仅一次低于256，不能误叫连续压力退出或实际API启动失败。两CID原post时点Running=false/Pid=0、无监听、卷/数据保留；主控没有现场采样/资源操作。没有新产品缺陷的本轮声明，不能预写余三通过。

连续工具精确unknown、保守8400/10800，余2400封存；入口6/7且entry07原夹具条件不符不使用，source4/5、interrupted1/2、API0/3，PG持有34.1386296749115/1800/API0/900。当前不恢复工程写入/运行，不发只为等待同一容量门的重复试跑卡。后续具备最小运行条件才统一补余三，须完整处理两次API跨PG生命周期所需启动余量；旧有限许可不能因可读或换窗复活。全部125/126/120/117及失败/unknown保持。

TASK129/R123已登记并保存核读，待人工转交A+原126独审窗口，必须未参与127/128；否则新隔离窗。没有实际转交/接收/开始事实。范围只读核当前两函数、三方法、两轮实际差异、前三项原始动态与执行控制，工具2400秒含480保存/24h，运行/测试/compile/PG/Docker/网络/费用全0。工程候选冻结，审计不依赖PG/API内存门；未来未变代码不再全审，余三仍未验。

编排调整只收口既有工作，不加功能或阶段。迟延因素包括普通授权/启动次数过细导致多次停线转卡，以及真实安装兼容问题暴露晚；本轮另有实际容量不足。剩余总成果为STEP018正常部署/真实模型完整学习与面试和Must，STEP019适用权限/预算/一致性集中验收，STEP020本人自用/README/恢复运行交接与GitHub同步。复用已验模块和充分证据，不整仓重做，不加入Linux/Nginx或增强项。不能给无证据完工日期或把三安装检查等同全部项目余量。

Q FROZEN、T0/72h空、provider/费用0，100/25及固定分额/28Must/89动作不变，计量/账号/token/模板/Embedding容量外部门未齐。STEP018进行中/部分验证，019/020/M1/项目/发布未验。回收原件在TASK128/orchestration-return-continuation01-20261023；129独立输入/许可在orchestration-20261023，刻意不提供工程自评/主控裁定。主控仅文件核证与共享维护，无产品或资源执行。CHG1673—1677，下一1678。

## 以下为v3.00及更早历史

'''.encode('utf-8')
    STATE.write_bytes(state_prefix + old_state)
    change_text = f'''
- CHG-1673，{stamp}，Codex编排Agent，DocuN/results/TASK-128-work-decision.md。置顶续作01前三项有限核收、容量阻断/成功源不可重放、工程许可封存与集中审查安排，旧裁定原字节保留。

- CHG-1674，{stamp}，Codex编排Agent，DocuN/tasks/TASK-129.md。登记129/R123稳定两处代码和前三真实证据集中独审，A+独立原126或新隔离窗待人工转交，不启动产品或重复旧全审。

- CHG-1675，{stamp}，Codex编排Agent，DocuS/架构动态文档.MD。v1.73登记真实成功安装与权限及余三容量阻断，原模型/SQL/角色不变，完整部署与Q未验。

- CHG-1676，{stamp}，Codex编排Agent，DocuS/执行动态文档.MD。v3.01登记已回收/许可封存、129待转交及剩余三收尾成果，明确减少机械转卡、不扩首版Must。

- CHG-1677，{stamp}，Codex编排Agent，DocuN/evidence/TASK-128/orchestration-return-continuation01-20261023/与TASK-129/orchestration-20261023/。保存原件/收据结构/旧报告后缀核证、旧共享、独立输入及有限diff/新许可/保存复读；主控产品运行0。
'''.encode('utf-8')
    CHANGE.write_bytes(old_change + change_text)
    assert STATE.read_bytes().endswith(old_state) and ARCH.read_bytes().endswith(old_arch)
    assert DECISION.read_bytes().endswith(old_decision) and CHANGE.read_bytes().startswith(old_change)
    assert identity(report_path) == report
    for product in products:
        assert identity(Path(product['path'])) == {key: product[key] for key in ('path', 'bytes', 'sha256')}
    proof = {'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'TASK': 'TASK-129', 'R': 'R-123',
             'files': [identity(path) for path in [CARD, DECISION, STATE, ARCH, CHANGE, OUT / 'permit.json', OUT / 'input-manifest.json', OUT / 'raw-evidence-index.json', RETURN / 'return-check.json']],
             'identity_reference_checks': len(checks), 'mismatches': 0, 'status': '待人工转交',
             'actual_dispatch': False, 'acceptance': None, 'products_unchanged_by_main': True,
             'executor_report_unchanged': True, 'old_shared_bytes_preserved': True,
             'product_runtime': 0, 'live_resource_probes': 0, 'next_CHG': 1678}
    for row in proof['files']:
        Path(row['path']).read_text(encoding='utf-8')
    save_json(OUT / 'save-proof.json', proof)
    print(json.dumps({'saved': True, 'TASK': 'TASK-129', 'R': 'R-123', 'checks': len(checks),
                      'raw_evidence_files': len(raw), 'mismatches': 0, 'card_bytes': CARD.stat().st_size,
                      'runtime': 0, 'state': '3.01', 'architecture': '1.73'}, ensure_ascii=True))


if __name__ == '__main__':
    main()
