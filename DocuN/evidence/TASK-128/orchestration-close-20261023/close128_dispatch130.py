"""只核文件和发布主控裁定、文档及人工任务卡，不导入产品或操作运行资源。"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
PUBLIC = Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
OUT = ROOT / 'DocuN/evidence/TASK-128/orchestration-close-20261023'
NEW = ROOT / 'DocuN/evidence/TASK-130/orchestration-20261023'
EX = ROOT / 'DocuN/evidence/TASK-128/execution/continuation-02'
OLD = ROOT / 'DocuN/evidence/TASK-128/orchestration-continuation02-20261023'
STATE = ROOT / 'DocuS/执行动态文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'
DECISION = ROOT / 'DocuN/results/TASK-128-work-decision.md'
CARD128 = ROOT / 'DocuN/tasks/TASK-128.md'
CARD130 = ROOT / 'DocuN/tasks/TASK-130.md'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def info(path):
    raw = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(raw), 'sha256': sha(raw)}


def js(path):
    return json.loads(path.read_bytes())


def lines(path):
    return [json.loads(line) for line in path.read_bytes().splitlines() if line.strip()]


def save_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as f:
        f.write(raw)
    assert path.read_bytes() == raw


def bounded_output(path):
    assert path.is_relative_to(ROOT), path
    for parent in [path, *path.parents]:
        if parent.exists():
            st = parent.lstat()
            assert not parent.is_symlink() and not getattr(st, 'st_file_attributes', 0) & 0x400, parent
        if parent == ROOT:
            return
    raise RuntimeError('输出越界')


def main():
    for p in [OUT, NEW, STATE, ARCH, CHANGES, DECISION, CARD128, CARD130]:
        bounded_output(p)
    assert not CARD130.exists() and not (OUT / 'acceptance-check.json').exists(), '已存在发布结果，先核断点'
    old = {p: p.read_bytes() for p in [STATE, ARCH, CHANGES, DECISION, CARD128]}
    assert '文档v3.02' in old[STATE].decode('utf-8-sig').splitlines()[2]
    assert '文档v1.74' in old[ARCH].decode('utf-8-sig').splitlines()[2]
    assert 'CHG-1683' in old[CHANGES].decode('utf-8-sig')[-1900:]
    assert 'CHG-1684' not in old[CHANGES].decode('utf-8-sig')
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp = now.isoformat()
    verified = []

    def verify(path, expected, size=None, category='输入身份'):
        path = Path(path)
        row = info(path)
        assert row['sha256'] == expected, path
        if size is not None:
            assert row['bytes'] == size, path
        verified.append({**row, 'category': category, 'match': True})

    permit = js(OLD / 'permit.json')
    manifest = js(OLD / 'input-manifest.json')
    for key in ['task_card', 'input_manifest', 'scope']:
        row = permit[key]
        verify(row['path'], row['sha256'], row.get('bytes'), '续作许可绑定')
    post = js(EX / 'post-snapshot.json')
    post_by_path = {Path(row['path']).as_posix().lower(): row for row in post['inputs']}
    doc_paths = [ROOT / 'README.md', ROOT / 'deploy/normal-install.md']
    for row in manifest['products']:
        p = Path(row['path'])
        if p in doc_paths:
            expected = post_by_path[p.as_posix().lower()]['sha256']
            assert info(EX / 'pre' / p.relative_to(ROOT))['sha256'] == row['sha256']
            verify(p, expected, category='允许的说明更新')
            verify(EX / 'post' / p.relative_to(ROOT), expected, category='说明最终快照')
        else:
            verify(p, row['sha256'], row.get('bytes'), '产品最终冻结')
    for row in js(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
        verify(PUBLIC / row['relative_path'].replace('\\', '/'), row['sha256'], category='实际公共路径与锁定规则')
    verify(ROOT / 'AGENTS.md', manifest['root_entry']['sha256'], category='项目入口')
    for key in ['audit_result', 'audit_closure']:
        row = manifest[key]
        verify(row['path'], row['sha256'], row.get('bytes'), '已验独审直接继承')
    result = info(ROOT / 'DocuN/results/TASK-128-result.md')
    readback = js(EX / 'result-readback.json')
    assert result['sha256'] == readback['sha256'] == 'f845e8d08fa1bf62bfdfb72136fcf5e2eb0e314487ba0d32335b3f9335732b97'
    assert result['bytes'] == readback['bytes'] == 39223
    result_raw = (ROOT / 'DocuN/results/TASK-128-result.md').read_bytes()
    assert sha(result_raw[-25623:]) == manifest['result128']['sha256'] == '472882152a5283bf0ff36d72ff1b73b7a9822e1cfff4dda5c0afa942950efc55'
    verify(ROOT / 'DocuN/evidence/TASK-128/execution/continuation-01/entry-06/source-success-receipt.jsonl',
           'a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06', category='成功原收据不变')
    for entry in ['entry-07', 'entry-08']:
        as_run = js(EX / entry / 'as-run.json')
        assert all(row['match'] for row in as_run['inputs'])
        for row in as_run['helpers']:
            p = EX / entry / Path(row['path']).name
            verify(p, row['sha256'], row['bytes'], entry + '实际辅助脚本')
            if entry == 'entry-08':
                verify(Path(row['path']), row['sha256'], row['bytes'], '辅助脚本最终身份')
    checkpoint = js(EX / 'checkpoint.json')
    assert all(checkpoint['checks'][str(i)]['status'] == 'passed' for i in range(1, 7))
    assert checkpoint['checks']['4']['actual_pg_stop_and_restart'] is True
    assert checkpoint['entries'] == 8 and checkpoint['api_starts'] == 3
    assert checkpoint['slots']['source']['starts'] == 7 and checkpoint['slots']['interrupted']['starts'] == 2

    # 第五项从真实提交轨迹、局部收据和独立读取得到，不以总结布尔量替代。
    trace5 = lines(EX / 'entry-07/interrupted-expected-unknown-trace.jsonl')
    submitted = [r['stage'] for r in trace5 if r['kind'] == 'original_migration_submitted']
    consumed = [r for r in trace5 if r['kind'] == 'all_real_migration_results_consumed']
    hidden = [r for r in trace5 if r['kind'] == 'planned_confirmation_hidden_after_real_commit']
    assert submitted == ['001', '002'] and len(consumed) == 2
    assert all(r['commit_observed'] and r['final_status'] == 'COMMIT' and r['transaction_status'] == 0 for r in consumed)
    assert len(hidden) == 1 and hidden[0]['stage'] == '002'
    assert trace5[-1]['connections'] == 1 and trace5[-1]['write_requests'] == 2
    partial = EX / 'entry-07/interrupted-expected-unknown-receipt.jsonl'
    verify(partial, 'f9a30db481b0849c352c759350e86fd71c6c4ded41b65d2cd76e2a76bd9d0e17', category='部分收据')
    part_rows = lines(partial)
    assert len(part_rows) == 6
    assert part_rows[-1] == {'confirmed_stages': ['001'], 'event': 'stopped', 'reason': 'commit_unknown', 'unknown_stage': '002'}
    assert [r['stage'] for r in part_rows if r['event'] == 'submitted'] == ['001', '002']
    fifth = js(EX / 'entry-07/check5.json')
    assert all(value == 0 for value in fifth['real_database_facts']['counts_excluding_control'].values())
    assert {r['relname'] for r in fifth['real_database_facts']['tables']} == {
        'activities', 'activity_allowed_models', 'activity_operations', 'activity_scope_sources', 'material_sources', 'material_versions'}
    for name in ['interrupted-same-partial-apply-trace.jsonl', 'interrupted-same-partial-verify-trace.jsonl']:
        t = lines(EX / 'entry-07' / name)
        assert t[-1]['connections'] == 0 and t[-1]['write_requests'] == 0
    fresh = lines(EX / 'entry-07/interrupted-new-receipt-partial-trace.jsonl')
    assert fresh[-1]['connections'] == 1 and fresh[-1]['write_requests'] == 0
    # 第六项实际只读边界及错误绑定的零连接。
    trace6 = lines(EX / 'entry-07/source-readonly-verify-trace.jsonl')
    assert trace6[0]['action'] == 'verify' and trace6[-1]['write_requests'] == 0
    assert any(r.get('read_only_begin') is True for r in trace6)
    assert trace6[-1]['connections'] == 1
    wrong = lines(EX / 'entry-07/source-wrong-binding-trace.jsonl')
    assert wrong[-1]['connections'] == 0 and wrong[-1]['write_requests'] == 0
    sixth = js(EX / 'entry-07/check6.json')
    assert sixth['output']['status'] == 'readonly_rechecked' and sixth['output']['runtime_closed']
    assert sixth['wrong_binding']['reason'] == 'receipt_mismatch'
    assert sixth['receipt_sha256_unchanged'] == checkpoint['slots']['source']['successful_receipt_sha256']
    verify(EX / 'entry-07/source-readonly-verify-receipt.jsonl', sixth['receipt_sha256_unchanged'], category='verify没有改成功收据')

    # 第四项绑定原生启动器、同一控制对象、业务登录、真实PG停开及前后数据。
    api_facts = []
    previous_database = None
    for i in [1, 2]:
        observation = js(EX / f'entry-08/api-{i}-observations.json')
        output = js(EX / f'entry-08/api-{i}-output.json')
        before = js(EX / f'entry-08/api-{i}-database-before.json')
        after = js(EX / f'entry-08/api-{i}-database-after.json')
        assert before == after and (previous_database is None or previous_database == before)
        previous_database = after
        assert observation['capabilities']['storage_ready'] is True
        assert observation['capabilities']['q_approval']['real_outbound_authorized'] is False
        assert observation['data']['current_mode'] == 'normal' and observation['data']['read_only'] is False
        assert observation['data']['binding_kind'] == 'original_control_hub'
        assert observation['data']['restore_executor_configured'] is False
        assert observation['control_id'] == checkpoint['slots']['source']['control_id']
        assert observation['source']['dataset_id'] == checkpoint['slots']['source']['identities']['dataset_id']
        assert observation['source']['instance_id'] == checkpoint['slots']['source']['identities']['instance_id']
        assert observation['source']['originals_root_id'] == checkpoint['slots']['source']['identities']['originals_root_id']
        assert observation['admin_environment_inherited'] is False
        assert observation['actual_pg_stat_activity'] and all(r['usename'] == 'retrolume_normal_app' for r in observation['actual_pg_stat_activity'])
        assert output['interval']['exit_code'] == 0 and output['listener_after'] == []
        assert output['stop_proof'] and all(r['exited'] for r in output['stop_proof'])
        assert output['interval']['args'][2].endswith('/deploy/start_local.py') or output['interval']['args'][2].endswith('\\deploy\\start_local.py')
        api_facts.append({'cycle': i, 'control_id': observation['control_id'], 'database_equal': True,
                          'native_exit': output['interval']['exit_code'], 'tree_and_port_stopped': True,
                          'seconds': output['interval']['seconds'], 'descendant_wait_seconds': output['descendant_wait_seconds']})
    stopped_between = js(EX / 'entry-08/source-stop-observation-9.json')['state']
    next_running = js(EX / 'entry-08/source-running-identity-7.json')['container']['state']
    assert stopped_between['Running'] is False and stopped_between['Pid'] == 0
    assert datetime.fromisoformat(stopped_between['FinishedAt']) < datetime.fromisoformat(next_running['StartedAt'])
    assert all(row['already_absent'] for row in js(EX / 'final-api-process-check.json'))
    assert len(js(EX / 'final-api-process-check.json')) == 18
    assert post['no_listeners'] and post['ports'] == []
    assert all(not obj['state']['Running'] and obj['state']['Pid'] == 0 for obj in post['objects'].values())
    assert post['objects']['source']['cid'] == checkpoint['slots']['source']['cid']
    assert post['objects']['interrupted']['cid'] == checkpoint['slots']['interrupted']['cid']
    pg_total = sum(r['seconds'] for r in checkpoint['pg_intervals'])
    api_total = sum(r['seconds'] for r in checkpoint['api_intervals'])
    assert abs(pg_total - post['pg_holding_cumulative_seconds']) < .00001 and pg_total < 1800
    assert abs(api_total - post['api_holding_seconds']) < .00001 and api_total < 900
    assert post['Q'] == 'FROZEN' and post['T0'] is None and post['provider'] == post['fees_cny'] == 0
    assert post['source_apply_replayed'] is False
    assert datetime.fromisoformat(checkpoint['api_intervals'][-1]['stopped']) < datetime.fromisoformat(permit['valid_until'])

    OUT.mkdir(parents=True, exist_ok=True)
    before_dir = OUT / 'before'
    before_dir.mkdir()
    for p, raw in old.items():
        (before_dir / p.name).write_bytes(raw)
    raw_evidence = [info(p) for p in sorted(EX.rglob('*')) if p.is_file()]
    acceptance = {'checked_at': stamp, 'TASK': 'TASK-128', 'R': 'R-122', 'result': result,
                  'reference_checks': verified, 'reference_count': len(verified), 'mismatches': 0,
                  'prior_report_suffix_bytes': 25623, 'prior_report_suffix_preserved': True,
                  'checks_1_2_3': '继承已验收TASK129独审，不重跑', 'checks_4_5_6': '主控按新增原始轨迹和实际文件核证通过',
                  'api_cycles': api_facts, 'unknown_commit_once': True, 'verify_readonly': True,
                  'runtime_stopped_basis': '原件post时点两CID/Pid及18个PID出生标识、端口记录；不是主控现场探针',
                  'product_code_unchanged': True, 'documentation_only_changes': [p.as_posix() for p in doc_paths],
                  'P3': '暂缓非阻断', 'control': {'tool_exact_seconds': None, 'tool_conservative_seconds': 9900,
                    'tool_cap': 10800, 'unused_seconds_sealed': 900, 'entries': 8, 'entry_cap': 8,
                    'source_starts': 7, 'source_cap': 7, 'interrupted_starts': 2, 'interrupted_cap': 3,
                    'api_starts': 3, 'api_cap': 3, 'pg_holding_seconds': pg_total, 'pg_cap': 1800,
                    'api_holding_conservative_seconds': api_total, 'api_cap_seconds': 900,
                    'history_and_exact_unknown': '保留旧失败和unknown，不签全部历史控制通过'},
                  'orchestrator_runtime': 0, 'orchestrator_product_test': 0,
                  'Q': 'FROZEN', 'T0': None, 'provider': 0, 'fees_cny': 0}
    save_json(OUT / 'acceptance-check.json', acceptance)
    save_json(OUT / 'raw-evidence-index.json', {'sources': raw_evidence, 'scope': '只核当前结果与有限原件，未重做产品测试或独审'})

    decision = f'''# TASK-128 / R-122 主控最终验收通过并关闭

{stamp}，Asia/Shanghai。续作02真实已接收、执行并返回。主控核结果39223字节、SHA256 {result['sha256']}，原25623字节后缀完整；本轮{len(verified)}条直接身份核对零漂移。当前代码、三定向方法及规则不变，只README和正常安装说明按真实事实更新。核证见 DocuN/evidence/TASK-128/orchestration-close-20261023/acceptance-check.json 与 raw-evidence-index.json。

## 验收范围

批准的关闭出站正常首次安装六项工程成果通过，任务128/R122验收关闭。前三项正确预检及四类拒绝、完整001—015安装与真实角色权限直接继承已验收TASK129原件和独审结论，不重新运行或审查。后三项新增真实证据已核收。

第四项通过。entry08两次原生start_local/--shutdown-stdin生命周期之间，源PG实际停止后同CID重开；两次storage_ready、normal/R03、原ControlHub和三UUID一致，均以retrolume_normal_app业务登录，无管理员环境继承。每次表OID/行数前后及两次间一致，原生exit0、树退出、端口释放。此项是关闭出站存储/控制面的运行证据，模型配置未加载、create因config_invalid不可用，不能扩张为真实业务或Q已就绪。

第五项通过。独立interrupted槽位原001与002均真实提交且读尽结果至COMMIT/IDLE，002确认仅一次被观察层隐藏。六行部分收据只确认001，002为submitted/unknown，无003、complete、自动重放或退款。独立读取确认002六表存在、业务行数0；同收据apply/verify在连接前拒绝，新收据也在只读预检拒绝非空局部目标，零后续写。保留局部库、卷与原收据，不能把已知真实提交改写为回滚或安装成功。

第六项通过。正式verify只引用管理员秘密，实走BEGIN READ ONLY及原身份、schema、role核验，写请求0；错误绑定在连接前拒绝，37行成功收据hash a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06保持。成功源禁止再次apply或重建。

## 失败、控制与资源

entry07首API原生父exit0但辅助层即时后代信号断言失败，原件及缺失stdout事实保留。随后按PID与出生标识只读确认原六进程消失、端口释放；只在新辅助脚本增加原生170秒边界内的后代自然等待与先保存观察，产品未改。entry08两次完整证据首次分别约0.063/0.047秒自然退出，不能把首失败改写为成功，也不以该失败要求重测前三项/中断/verify。

连续入口8/8、source启动7/7、interrupted2/3（唯一注入已消费）、API3/3；PG持有{pg_total}/1800秒，API按树终止确认保守{api_total}/900秒，首轮精确后代退出时刻unknown留账。连续工具保守9900/10800、完整精确unknown，未用900秒和各余槽全部封存；旧127/128失败、125/126及117/120历史控制不通过或unknown均不撤销。安装功能验收通过不等于全部历史控制追认通过。

post原时点两精确CID均Running=false/Pid=0、18个自有PID出生标识均已消失、PG/API监听释放，根/卷/网络/完整与部分数据保留。主控本轮只核文件，没有现场Docker/PG/API/内存探针或产品运行，不能声称当下又重新停止过。旧128运行许可随验收关闭，路径可读不恢复启动权。

## 已完成与下一步

TASK129的功能/安全两函数代码门直接继承；没有新安全产品变化，不再独审当前代码。F129-01两处英文注释P3按用户要求暂缓，不修、不测、不新派卡。

正常安装子成果已完成。Q仍FROZEN、T0/72h空、真实provider/费用0，100次/25元及48/28/24分额、28Must/89动作不变。当前API原件也明确模型和integration未载入，不能凭安装成功宣称外部分词/完整模板/Embedding逐项及整批容量或账号适用性已核齐。实际Q核心链仍待这些具体外部事实与后续精确启用，不另派同样的供应商搜索/协议设计卡，不反复要求用户释放内存。

直接推进不依赖Q的已授权交付工作。TASK130/R124交A-新常规Git交付窗口，完成README/正常安装说明当前事实收口和用户指定GitHub仓库同步；不使用129独审窗口，也不让已关闭128继续真实运行。STEP018仅正常安装子项通过，018整体/019/020/M1/项目/发布均未签通过。下方为此前裁定原字节历史。

'''.encode('utf-8')
    DECISION.write_bytes(decision + old[DECISION])
    notice = f'''# TASK-128 / R-122 已验收关闭，旧合同仅供取证

{stamp}，Asia/Shanghai。用户已带回续作02；主控核六项原始证据及TASK129有效独审，批准的关闭出站正常安装子成果验收通过，128已结束。完整裁定 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-work-decision.md。

旧许可、剩余工具/启动槽及全部runner均封存，不得继续启动源库、中断库、API或重放安装。完整库与部分库、收据、失败和unknown原样保留。Q/真实模型/费用继续关闭；P3暂缓。以下为验收前完整旧卡原字节，不能据其文字恢复执行权。

'''.encode('utf-8')
    CARD128.write_bytes(notice + old[CARD128])
    arch = f'''# 架构动态文档

文档v1.75，2026-10-23，Asia/Shanghai。需求v1.4、执行动态v3.03、task_model/07。以下v1.74原字节保留。

## 正常首次安装六项已验收，关闭出站存储与控制面可用

{stamp}。128续作02后三项已核收，与129已验收代码及前三项共同闭合AP-125-NORMAL-INSTALL-01有限成果。完整001—015、业务/快照权限、原生API跨实际PG停开、独立002提交未知及拒绝重放、成功收据只读verify都有适用原件；未变代码不重审、不重测。安装器hash7cd62b4f3526510c6f38de2a033a01d6ae36bcd661e90dbaca6b551db8141ba8、测试2357a7031d2da858224d75b56ee0173a3166b0ca68c6905994009b7e64e6b3c3保持。

成功source固定原CID/systemid/三UUID与原ControlHub；两个真实API周期以业务登录启动，R03/normal/storage_ready，同表OID/行数保持、树零退出。当前模型/integration尚未载入、create配置无效，真实业务能力不能由此推断就绪。独立interrupted部分库只到002真实提交，未知收据保留并禁止重放；成功库同样不重装。两库已停止的结论仅来自执行者post原时点原件，不是主控现场探针。

本轮产品零变更，README/deploy说明更新；辅助停止检查竞态有界修正及首失败保留，未改启动器/SQL/角色/权限模型。F129-01 P3暂缓。Q冻结、T0空、费用0及计量/模板/Embedding/账号外部门仍在。下一已授权非Q工作是130的安装使用说明事实收口和GitHub同步，不新增平台/功能；STEP/项目最终验收未签。

## 以下为v1.74及更早历史

'''.encode('utf-8')
    ARCH.write_bytes(arch + old[ARCH])
    NEW.mkdir(parents=True)
    (NEW / 'TASK-130-contract-status.txt').write_text('已在唯一执行动态登记TASK130/R124；完整卡将在本批保存并核读后转为待人工转交。\n', encoding='utf-8')

    def state_prefix(dispatch):
        return f'''# 执行动态文档

文档v3.03，2026-10-23，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.75、task_model/07。以下v3.02原字节保留。

## 128正常安装六项验收关闭，130文档及GitHub同步{dispatch}

{stamp}。用户带回128续作02，调度实际已返回且停止；结果39223字节/hash{result['sha256']}、旧25623后缀完整，主控核{len(verified)}条直接身份零漂移，具体原件见128/orchestration-close-20261023。六项正常首次安装有限成果验收通过并关闭，129已验收独审/前三项直接继承，4/5/6新增动态已核收，不再重复原代码审查或旧安装验证。

正常源原生API两完整周期跨真实PG停开保持原身份/ControlHub/表OID与行数，业务角色、storage_ready与关闭出站成立；模型/integration未载入且create配置无效，不能称真实业务已启用。002只一次真实提交后隐藏确认，六行未知收据与局部库保留、后续拒绝重放；成功37行收据未变且只读verify通过。首API辅助即时检查失败及后代精确时刻unknown保留，只改辅助有界等待，后两周期自然树退出证明有效。P3暂缓，不修不测不加卡。

连续预算入口8/8、source7/7、interrupted2/3、API3/3，PG{pg_total}/1800秒、API保守{api_total}/900秒，工具保守9900/10800/精确unknown，余900及启动槽全部封存，原截止及旧失败不重置。两个CID在执行者post原时点均Running=false/Pid=0、18个自有PID出生标识退出、监听释放；资源和完整/部分数据保留，主控没有现场探针。TASK128旧合同置顶关闭通知，不再生效；原127失败及129交付关闭照留，全部历史控制不通过/unknown仍在。

按用户早前明确授权使用https://github.com/shspic/RetroLume-agent及除.gitignore外可纳管同步，登记TASK130/R124，状态{dispatch}。A-新常规Git交付窗口，原080窗口已不可用且本成果是低风险确定版本交付，不占129独审窗或让128恢复运行。完整卡D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-130.md；只有核读后方为待转交，未据保存宣称真实派发/接收/开始。目标一个完整非Q成果：两份安装说明当前验收事实收口、必要普通Review、保护所有未忽略改动及历史、真实提交推送指定仓库并核远端commit与tree。无并行执行。

130独立交付预算工具/文件/Git/传输合计5400秒含600保存，24h；产品import/compile/tests/build/PG/Docker/API/browser/provider/付费全0。它不恢复128/129/125/126或旧117/120余量，不变.gitignore，不强推/清理/改产品。平台审批仍适用。低风险文档和Git交付用普通Review及Git对象证据，不设新独审门。主控这轮仅文件核证、只读Git元数据和文档维护，无产品执行。

当前核心下一步仍为STEP018真实模型完整学习/面试及28Must；供应商当前分词/完整模板/Embedding单项整批容量及账号非敏感适用事实缺失，只阻Q启用，不再派同样搜索/协议设计或反复要求释放内存。130可先完成已授权版本交付，不能以Git同步替代这些功能门。Q FROZEN、T0/72h空、provider/费用0，100/25及48/28/24分额、28Must/89动作不变；STEP018整体部分验证，019/020/M1/项目/发布未通过。CHG1684—1689，下一1690。

## 以下为v3.02及更早历史

'''.encode('utf-8')

    STATE.write_bytes(state_prefix('已登记、卡面待保存') + old[STATE])
    save_json(NEW / 'registration.json', {'registered_at': stamp, 'TASK': 'TASK-130', 'R': 'R-124',
                                        'state_registered_before_card': info(STATE), 'card_not_yet_saved': not CARD130.exists()})
    contract = '''# TASK-130 / R-124 正常安装说明收口与已验版本GitHub同步

## 目标与交付

你是本卡常规交付执行者。在已验收的关闭出站正常安装基线上，一次完成面向用户的安装说明事实收口、当前未忽略项目文件的本地版本提交和指定GitHub仓库同步，留可核对的提交/远端证据；不承担产品实现、重新测试或项目最终验收。

完整成果包括两份说明更新、现有改动与.gitignore边界核对、一次普通Review、真实提交推送、远端commit/tree与本地事实核对、结果报告。卡内自行连续处理普通Git步骤，完成后统一回传，不按stage/commit/push分别转卡。上传成功仅是版本交付，不是项目功能完成或发布。

## 项目、规则与接收安排

项目根 D:/shspic/project_NO3_RetroLume-agent；根入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。唯一task_model/07，采用V4.0、公共AGENTS CHG-0003，锁定实际指纹 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用后来规则。

公共AGENTS为 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4/DocuS/AGENTS.MD；WORK在同目录WORK.MD，本卡只需task_model角色边界、文档状态、完整合同、证据/停止/交付对应章节。公共库只读。需求v1.4、架构v1.75、执行动态v3.03。任务类型是文档与版本交付，关联TASK125—129、STEP018正常安装子成果与STEP020既有交付准备，涉及原GitHub同步授权，不签父STEP通过。

接收A-，新建常规Git交付窗口。原080工程窗已不可用，确定性文档/Git工作不要求最强实现窗，禁止占用129独审窗口。真实客户端和模型如实记录，A-标签不是模型ID；不委派、不并行。

授权来自用户此前明确要求使用 https://github.com/shspic/RetroLume-agent 并同步本项目，且明确“.gitignore中的文件不跟踪/上传/同步，其余均可”。已核本机origin为 https://github.com/shspic/RetroLume-agent.git、HEAD为main；这只是当前文件读取事实，不代表已连远端或本次已推送。实际远端和差异须在正常Git操作前核对。

本卡新独立交付单元实际尝试初始为0，不能把旧任务失败和投入写成0。原128工具保守9900/10800/精确unknown及余900已封存，入口8/8、source7/7、interrupted2/3、API3/3，PG66.82600331306458/1800、API保守99.34058094024658/900原样保留；129保守900/2400及余1500封存，全部旧控制不通过/unknown不改变。本卡不借它们运行或追认。

## 背景与最小充分上下文

按顺序读取根入口、锁定公共AGENTS/上述WORK章节、本卡、D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD顶部当前段、D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-work-decision.md顶部最终裁定、D:/shspic/project_NO3_RetroLume-agent/README.md及D:/shspic/project_NO3_RetroLume-agent/deploy/normal-install.md、.gitignore、本卡同目录证据的input-manifest.json与permit.json。不要重读全部历史状态、重演旧runner或重新研究供应商。

源安装001—015、实际业务/快照权限、原生API跨PG重开、独立002提交未知及拒绝重放、成功收据只读verify均已核证，TASK128通过关闭，129独审有效。产品安装器/测试未变；报告完整39223字节/hash f845e8d08fa1bf62bfdfb72136fcf5e2eb0e314487ba0d32335b3f9335732b97，成功收据37行/hash a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06。具体核证 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/orchestration-close-20261023/acceptance-check.json 与raw-evidence-index.json。充分证据直接引用，不复制原始运行文件。

当前README/正常安装说明仍用“六项证据齐全、待主控核验”，本卡只把这些陈旧事实更正为“批准的关闭出站正常安装有限成果已验收”。正常API的storage_ready/normal/R03不证明模型/integration加载；create仍因配置无效不可用，Q冻结、T0/72h空、真实调用/费用0。真实模型完整学习/面试及Must、供应商计量/账号/完整模板/Embedding容量与启用前置尚未闭合。不要把“能安装”写成“全部功能可用”，不要处理F129-01两条P3英文注释，不加入Linux/Nginx/增强项。

## 执行边界与资源

允许读取项目版本元数据、已纳管与未忽略候选文件、.gitignore、上述最小输入和必要证据。当前四个旧根目录已归档，历史路径依根入口映射，只引用不改归档。读取候选中若发现凭据只记录安全路径/类别，不打印值、片段或完整内容，不读取.runtime/私人环境配置、浏览器profile、密钥、DSN或账号后台。

内容修改仅允许 D:/shspic/project_NO3_RetroLume-agent/README.md 与 D:/shspic/project_NO3_RetroLume-agent/deploy/normal-install.md 的当前安装验收事实和直接必要使用说明。先存这两份pre及hash；修正事实准确即可，不全面改写或格式化手册，不改变原命令含义。允许新增 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-130/ 下本卡证据，以及 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-130-result.md；普通证据保持单份，不复制整仓生成第二份public-tree。

允许为用户已授权同步进行正常Git索引/提交/推送操作，目标仅上述指定仓库。先保存分支、工作树、现有暂存及HEAD/远端状态，保护全部既有文件内容。不得改产品、测试、迁移、配置、依赖锁、公共库、原始需求、正式DocuS、任务卡、历史结果/证据、.gitignore。git层暂存既有授权文件不等于获准修改其工作树内容。

所有未忽略文件均属于授权候选，不因历史、临时、文件多或报告多擅自排除；按Git实际ignore规则核，不按扩展名另创规则。必须检查已追踪但命中ignore的对象，必要时只对精确确认路径解除索引跟踪并保留原文件，用清单留证；禁止重置整个索引或删除磁盘文件。不得强制add被忽略内容、上传私有配置/密钥/连接凭据、把原件“脱敏覆盖”或无授权追加忽略。发现明确秘密只阻对应上传，先隔离其暂存，保留本地原件并交最小决定；不据此丢弃其它可同步成果。合成占位/公开hash不自动当凭据，不能仅凭模糊关键字无限排除证据。

可自主选择现有Git/正常GitHub认证方式、普通提交粒度与GitHub标准网络操作，均不得输出令牌或要求用户在聊天发凭据。网络限GitHub指定仓库和既有认证流程，不安装依赖、不抓供应商网页、不调用付费服务。若创建分支使用codex/前缀；已有main可在远端未产生冲突变化时正常更新，不强推。fetch发现他人未整合产品变化，不自动覆盖、rebase或合并改变已验产品；保留本地提交，停止冲突部分并说明最小差异。无依据的push重试禁止。

禁止reset --hard、clean、checkout覆盖用户改动、stash藏改动、history重写/过滤、force push、删除分支/标签、改远端到其它仓库，以及任何文件/目录/卷批量删除。单文件达到GitHub平台限制时保存精确清单，不默默截断、不擅自换LFS/改ignore/删证据；先同步可独立安全部分并交实际硬缺口。平台审批服务继续适用，不能通过改shell/通道/命令规避。需正常审批即说明具体动作已有用户授权；自动审批拒绝或账号失权，保留原错误并报告，不冒充网络成功。

本卡独占两份说明与本地Git索引/该仓库同步，没有已知并行工程或审计写入者；先核有无新在途事实，不覆盖他人增量。产品进程/PG/Docker/API/browser/Windows Job及端口均不分配，不得启动或探测它们；不读取私有凭据，也没有旧128的运行权限。

## 验证、证据与投入

完整通过标准为说明与128主控裁定一致、产品/测试/规则等非许可内容零改写、ignore边界正确、实际选定快照已提交并推送用户指定仓库、真实远端引用指向预期commit且Git tree身份可核。结果逐项区分本地提交、已推送、未推送及原因，不能只凭git exit0或口头声称同步。push被拦时保存本地成果，不把本地commit说成远端已更新。

先给当前差异和纳管候选做一次与风险相称的普通Review，核两份说明、坏路径/凭据/平台大文件、ignore与候选清单；不写实现镜像测试。复用128/129全部有效功能与审计证据，不跑compile、unittest、build、应用、浏览器、PG或真实模型。仅文档、版本对象和发布到用户指定库的低风险交付，不另设独立审计门，不签STEP019安全验收。

证据保存在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-130/。需有pre/post与必要有限diff、候选/ignore核对、受检树/commit的身份、真实Git命令与退出码/脱敏stdout、push结果和远端ref核对、时间/失败/预算。Git输出量大时落文件并只汇报摘要，不遍历无关node_modules/venv/运行资料。不把.gitignore排除的内容复制到证据再上传。

工具/文件/Git/传输总预算5400秒，含最后600秒保存回传，日历自permit签发起24小时；单批检查通常≤60秒，大传输可单独有界等待并≤60秒更新进度。正常准备/提交/推送不按每条命令另设一次性根上限。实际网络瞬时错误有证据时可最多两次恢复，沿真实失败账，不盲重跑。未测精确项记unknown并保守留时，不写0。产品运行、provider、token计量调用、费用、下载/安装预算均0，Q始终关闭。

保存结果主体和主要证据后提交同步；文件不能记载包含自身内容的commit/hash，不为这种自指无限追加提交。若需提交真实首push回执，允许一次普通收尾提交；最终远端tip可在回返消息给出，并可由主控从Git对象核对，不再为记录这个tip循环提交。明确报告的被同步快照和自然收尾事实，不把控制记录例外扩张为其它未忽略文件漏传。

## 停止、回传与人工

完成以上完整成果即停。关键权限/认证缺失、明确敏感上传、新产品变化或远端冲突、平台大文件硬限、两次有据修正仍失败、预算或日历到限时停止受影响操作，先完成无关可交付部分。原失败和全部历史投入不清零；不能以换窗口、新任务或目录可读恢复旧许可。

完整结果 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-130-result.md，按本卡R124及后续轮次保留原文。先给一句结论与实际差异/证据导航，再列接收身份、实际commit/branch/remote/tree、纳管与ignore范围、命令/失败/时间、未同步/未验证、偏差、风险、必要人工与待主控文档变化。除两份许可说明外产品和共享状态原字节保持；不自签STEP018/019/020、Q、M1、项目或发布完成。

同边界未验收补证沿原TASK130/R124和结果，稳定后主控文件核证，不预设另一审计卡。只能用户处理的GitHub登录或平台关键决定若实际出现，给最少步骤与非敏感成功标志，不索取密钥/账单/截图。没有实际阻塞不额外请求确认。公共源或必要材料不可读先利用同版完整材料并登记，只暂停依赖部分，不假称已加载。

结果保存成功且可读后，回复一句事实结论、最终可核GitHub分支/commit链接与上述结果文件绝对路径，供用户带回主控。需主控同步唯一状态及CHG，不自行改DocuS。不会新增独立状态账，也不为本卡轻微文案整理登记新P3门槛。
'''
    with CARD130.open('xb') as f:
        f.write(contract.encode('utf-8'))
    saved_card = CARD130.read_text(encoding='utf-8')
    assert saved_card == contract and '*' not in contract
    for text in ['## 目标与交付', '## 项目、规则与接收安排', '## 执行边界与资源', '## 停止、回传与人工', 'TASK-130-result.md', '5400', 'R-124']:
        assert text in saved_card
    save_json(NEW / 'input-manifest.json', {'TASK': 'TASK-130', 'R': 'R-124', 'created_at': stamp,
                                          'files': [info(p) for p in doc_paths + [ROOT / '.gitignore', ROOT / 'AGENTS.md', DECISION,
                                              ROOT / 'DocuN/results/TASK-129-work-decision.md', OUT / 'acceptance-check.json']],
                                          'rules': js(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'),
                                          'product_manifest_to_reuse': info(OLD / 'input-manifest.json')})
    save_json(NEW / 'permit.json', {'TASK': 'TASK-130', 'R': 'R-124', 'issued_at': stamp,
                                  'valid_until': (now + timedelta(hours=24)).isoformat(),
                                  'status': '待人工转交', 'actual_dispatch': False, 'receiver': 'A-新常规Git交付窗口',
                                  'task_card': info(CARD130), 'input_manifest': info(NEW / 'input-manifest.json'),
                                  'authority': '用户明确GitHub同步及除.gitignore外允许纳管；主控直接推进不依赖Q的交付',
                                  'repository': 'https://github.com/shspic/RetroLume-agent', 'tool_seconds': 5400,
                                  'save_reserve_seconds': 600, 'product_runtime': 0, 'provider': 0, 'fees_cny': 0,
                                  'old_budgets_restored': False, 'Q': 'FROZEN'})
    STATE.write_bytes(state_prefix('待人工转交') + old[STATE])
    changes = [
        (1684, 'DocuN/results/TASK-128-work-decision.md', '最终核收六项正常安装有限成果并验收关闭，保留未知提交/首API失败和全部历史控制，Q仍冻结。'),
        (1685, 'DocuN/tasks/TASK-128.md', '置顶关闭和旧许可封存通知，完整旧卡原字节保留，不恢复任何运行权。'),
        (1686, 'DocuS/架构动态文档.MD', 'v1.75登记正常安装存储/控制面真实证据和局部未知保留，业务配置/外部门未闭，不新增架构。'),
        (1687, 'DocuS/执行动态文档.MD', 'v3.03登记128实际返回/通过结束和130先占号后保存待转交，所有旧预算/控制/未完成阶段保留。'),
        (1688, 'DocuN/tasks/TASK-130.md', '按既有用户授权保存完整文档/GitHub同步合同，A-新常规窗，前置满足且无产品运行，不另设审计。'),
        (1689, 'DocuN/evidence/TASK-128/orchestration-close-20261023/ 与 DocuN/evidence/TASK-130/orchestration-20261023/', '保存原件身份核证/旧共享、有限验收及卡面登记/许可/复读，未重测产品或启用Q。'),
    ]
    suffix = ''.join(f'\n- CHG-{n:04d}，{stamp}，Codex编排Agent，{path}。{reason}\n' for n, path, reason in changes).encode('utf-8')
    CHANGES.write_bytes(old[CHANGES] + suffix)
    for p in [STATE, ARCH, DECISION, CARD128]:
        assert p.read_bytes().endswith(old[p]), p
        p.read_text(encoding='utf-8-sig')
    assert CHANGES.read_bytes().startswith(old[CHANGES])
    (NEW / 'TASK-130-contract-status.txt').write_text('完整卡已保存并核读；待用户人工转交A-新常规Git交付窗口，尚无真实派发/接收/启动。\n', encoding='utf-8')
    save_json(OUT / 'save-proof.json', {'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
                                     'shared': [info(p) for p in [DECISION, CARD128, ARCH, STATE, CHANGES]],
                                     'old_suffixes_preserved': True, 'raw_result_unchanged': info(ROOT / 'DocuN/results/TASK-128-result.md') == result,
                                     'new_card': info(CARD130), 'TASK128': '验收通过并结束', 'TASK130': '待人工转交',
                                     'runtime': 0, 'Q': 'FROZEN', 'next_CHG': 1690})
    save_json(NEW / 'dispatch-readback.json', {'saved_at': stamp, 'card': info(CARD130),
                                           'permit': info(NEW / 'permit.json'), 'state': info(STATE),
                                           'registration_before_save': True, 'utf8_readable': True,
                                           'status': '待人工转交', 'actual_dispatch': False})
    print(json.dumps({'TASK128': '验收通过并关闭', 'references': len(verified), 'TASK130': '待人工转交',
                      'card': CARD130.as_posix(), 'state': 'v3.03', 'architecture': 'v1.75', 'next_CHG': 1690}, ensure_ascii=False))


if __name__ == '__main__':
    main()
