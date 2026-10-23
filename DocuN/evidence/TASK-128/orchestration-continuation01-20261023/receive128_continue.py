"""主控核收128有限成果并续写同卡；仅文件/原文核证，不执行产品。"""
import ast
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
PUBLIC = Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
OUT = ROOT / 'DocuN/evidence/TASK-128/orchestration-continuation01-20261023'
E = ROOT / 'DocuN/evidence/TASK-128/execution'
PRIOR = ROOT / 'DocuN/evidence/TASK-128/orchestration-20261023'
CARD = ROOT / 'DocuN/tasks/TASK-128.md'
DECISION = ROOT / 'DocuN/results/TASK-128-work-decision.md'
STATE = ROOT / 'DocuS/执行动态文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def obj(path):
    raw = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(raw), 'sha256': sha(raw)}


def js(path):
    return json.loads(path.read_bytes())


def save_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as stream:
        stream.write(data)
    assert path.read_bytes() == data


def functions(raw):
    module = ast.parse(raw.decode('utf-8-sig'))
    return {node.name: ast.dump(node, include_attributes=False)
            for node in module.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def main():
    for path in (OUT, CARD, DECISION, STATE, ARCH, CHANGE):
        for parent in [path, *path.parents]:
            if parent.exists():
                stat = parent.lstat()
                assert not parent.is_symlink() and not getattr(stat, 'st_file_attributes', 0) & 0x400, str(parent)
            if parent == ROOT:
                break
        else:
            raise RuntimeError('输出越出项目')
    assert not DECISION.exists() and not (OUT / 'permit.json').exists(), '已有接续登记，应核断点'
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp = now.isoformat()
    old_permit = js(PRIOR / 'permit.json')
    deadline = old_permit['valid_until']
    assert now < datetime.fromisoformat(deadline), '原日历到期，不得自行延长'
    card_old, state_old, arch_old, change_old = CARD.read_bytes(), STATE.read_bytes(), ARCH.read_bytes(), CHANGE.read_bytes()
    assert sha(card_old) == old_permit['task_card']['sha256']
    assert '文档v2.99' in state_old.decode('utf-8-sig').splitlines()[2]
    assert '文档v1.71' in arch_old.decode('utf-8-sig').splitlines()[2]
    assert 'CHG-1667' in change_old.decode('utf-8-sig')[-1700:] and 'CHG-1668' not in change_old.decode('utf-8-sig')
    old_input = js(PRIOR / 'input-manifest.json')
    assert sha((PRIOR / 'input-manifest.json').read_bytes()) == old_permit['input_manifest']['sha256']
    pre, post = js(E / 'pre-snapshot.json'), js(E / 'post-snapshot.json')
    report = obj(ROOT / 'DocuN/results/TASK-128-result.md')
    readback = js(E / 'result-readback.json')
    assert report['sha256'] == readback['sha256'] == 'fd9445acbca5abe2d3b1daa8bfb8f0793d6be24ba9e70a08b7628de09b4e0558'
    assert report['bytes'] == readback['bytes'] == 13923 and readback['missing_links'] == 0
    checks = []

    def check(path, expected, size=None, category='input'):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        value = obj(path)
        assert value['sha256'] == expected, str(path)
        if size is not None:
            assert value['bytes'] == size, str(path)
        checks.append({**value, 'category': category, 'match': True})

    assert len(pre['inputs']) == len(post['inputs']) == 58
    for row in post['inputs']:
        check(row['path'], row['sha256'], category='post_input')
    changes = {row['path']: row for row in post['changes']}
    expected_changes = {
        'deploy/initialize_normal.py': '4513241f71fa3c15aa1d0ee7dc79e757a49f3583924dd5530b49ac6cc71b0ac5',
        'backend/tests/test_normal_install.py': '17bb640dce04e860d2b7343d7a034867b2088484c54578051a9741c8798a520a',
        'deploy/normal-install.md': '72dd8ff5090a25002c93a3f5e7fa9f1c783c6c9879187a3c75a4c79ff9f7f1b5',
        'README.md': '086650420ca44337fa2db9967613bf7e504673fbebcf531b4873e087bce63849',
    }
    assert set(changes) == set(expected_changes)
    current_product = []
    for row in old_input['product_baseline']:
        path = Path(row['absolute_path'])
        relative = path.relative_to(ROOT).as_posix()
        expected = expected_changes.get(relative, row['sha256'])
        check(path, expected, category='product_baseline_with_allowed_delta')
        current_product.append({**obj(path), 'relative_path': relative})
    for relative, row in changes.items():
        assert row['after_sha256'] == expected_changes[relative]
        check(E / 'pre' / relative, row['before_sha256'], category='product_pre')
        check(E / 'post' / relative, row['after_sha256'], row['bytes'], 'product_post_copy')
    rules = js(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
    for row in rules:
        check(PUBLIC / row['relative_path'].replace('\\', '/'), row['sha256'], category='locked_rule')
    old_funcs = functions((E / 'pre/deploy/initialize_normal.py').read_bytes())
    new_funcs = functions((ROOT / 'deploy/initialize_normal.py').read_bytes())
    assert old_funcs.keys() == new_funcs.keys()
    changed_functions = [name for name in old_funcs if old_funcs[name] != new_funcs[name]]
    assert changed_functions == ['connect']
    connect_source = (ROOT / 'deploy/initialize_normal.py').read_text(encoding='utf-8')
    assert 'service=""' not in connect_source and 'ambient_service_rejected' in connect_source
    assert 'ipaddress.ip_address(row["server_address"])' in connect_source
    comparison = js(E / 'entry-04/connection-comparison.json')
    assert comparison[0]['case'] == 'control' and comparison[0]['connected'] is True
    assert comparison[1]['case'] == 'formal' and comparison[1]['connected'] is False
    assert comparison[1]['exception_class'] == 'OperationalError' and comparison[1]['sqlstate'] is None
    assert 'definition of service "" not found' in comparison[1]['diagnostic']
    equals = js(E / 'entry-04/credentials-equal.json')
    assert equals['all_four_byte_equal'] is True and equals['same_environment'] is True
    fixed = js(E / 'entry-05-ready/fixed-formal-connection.json')
    assert fixed['connected'] is True and fixed['service_environment_absent'] is True
    assert comparison[0]['identity'] == fixed['identity']
    assert fixed['identity']['server_address'] == '172.19.0.2/32'
    failure = js(E / 'entry-05-ready/real-preflight.json')
    assert failure['passed'] is False and failure['reason'] == 'target_identity_mismatch'
    empty = js(E / 'entry-05-ready/actual-empty-facts.json')
    assert empty['readonly'] is True and empty['all_false'] is True and not any(empty['empty_query'].values())
    replay = js(E / 'nat-reproduction.json')
    assert replay['replay_only_no_connection'] and replay['actual_is_host_prefix']
    assert replay['ip_address_rejects_actual_text'] and not replay['product_guard_modified']
    assert all(replay['expected_fields_equal'].values())
    assert replay['original_observe_identity_rejection'] == 'target_identity_mismatch'
    tests = js(E / 'targeted-tests.json')
    assert (tests['run'], tests['failures'], tests['errors'], tests['successful']) == (2, 0, 0, True)
    assert js(E / 'diagnostic-safety.json')['passed'] is True
    for dirname in ('entry-04', 'entry-05-ready'):
        for row in js(E / dirname / 'as-run.json')['helpers']:
            copy = E / dirname / Path(row['path']).name
            check(copy, row['sha256'], row['bytes'], 'as_run_copy')
    for row in readback['extra_as_run_helpers']:
        check(row['path'], row['sha256'], category='extra_as_run_helper')
    checkpoint = js(E / 'checkpoint.json')
    assert checkpoint['entries'] == post['entries_cumulative'] == 5
    assert checkpoint['slots']['source']['starts'] == post['objects']['source']['starts'] == 3
    assert checkpoint['slots']['interrupted']['starts'] == 1
    assert post['api_starts'] == post['api_holding_seconds'] == 0
    assert abs(post['pg_holding_cumulative_seconds'] - 21.66196846961975) < .000001
    assert post['no_listeners'] is True and post['secret_matches'] == 0
    for name, cid in [('source', 'db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d'),
                      ('interrupted', '549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8')]:
        assert post['objects'][name]['cid'] == checkpoint['slots'][name]['cid'] == cid
        assert not post['objects'][name]['state']['Running'] and post['objects'][name]['state']['Pid'] == 0
    old_result127 = ROOT / 'DocuN/results/TASK-127-result.md'
    check(old_result127, 'e001d7892f3e11581db4731e53242cd007870165c97a7b186496ebb84b3dc73b', 16765, 'old127_report')
    raw_files = [
        'entry-04/connection-comparison.json', 'entry-04/credentials-equal.json',
        'entry-05-ready/fixed-formal-connection.json', 'entry-05-ready/real-preflight.json',
        'entry-05-ready/actual-empty-facts.json', 'nat-reproduction.json', 'nat-reproduction.py',
        'proposed-nat-fix.diff', 'diagnostic-safety.json', 'targeted-tests.json',
        'targeted-tests-as-run.py', 'approved-change-hashes.json', 'changes.diff',
        'failure-ledger.json', 'post-snapshot.json', 'pre-snapshot.json', 'checkpoint.json', 'result-readback.json',
    ]
    frozen_evidence = [obj(E / relative) for relative in raw_files]
    OUT.mkdir(parents=True, exist_ok=True)
    before = OUT / 'before'
    before.mkdir(exist_ok=False)
    for path, data in [(CARD, card_old), (STATE, state_old), (ARCH, arch_old), (CHANGE, change_old)]:
        (before / path.name).write_bytes(data)
    verification = {
        'checked_at': stamp, 'TASK': 'TASK-128', 'R': 'R-122', 'round': '首轮回收',
        'result': report, 'identity_reference_checks': len(checks), 'mismatches': 0, 'checks': checks,
        'allowed_product_changes': list(expected_changes), 'changed_installer_functions': changed_functions,
        'service_root_cause': 'CONFIRMED_EMPTY_SERVICE_LOOKUP',
        'service_patch': 'CANDIDATE_WITH_TWO_TARGETED_TESTS_AND_REAL_READONLY_CONNECTION',
        'new_identity_host_mask_defect': 'CONFIRMED_OPEN_P1', 'nat_patch_applied': False,
        'actual_empty_source': 'READONLY_EMPTY_QUERY_ALL_FALSE_AS_OF_ENTRY05',
        'original_six_complete_passes': 0, 'independent_audit_not_replaced': True,
        'new_budget_need': '同资源source至少再启动2次；原剩1次不足；增1次不增资源/持有/总时间',
        'orchestrator_product_runtime': 0, 'orchestrator_live_resource_probe': 0,
        'stop_evidence_as_of': post['utc'], 'current_live_stop_not_inferred': True,
        'raw_evidence': frozen_evidence,
    }
    save_json(OUT / 'return-check.json', verification)
    decision = f'''# TASK-128 / R-122 首轮主控核证与续作01裁定

{stamp}，Asia/Shanghai。已核{len(checks)}条身份引用，零缺失零漂移；报告13923字节/hash{report['sha256']}，四份允许文件变化与58输入及七规则相符。安装器函数AST差异仅connect，NAT身份guard仍未改，原127报告及失败收据保持。

## 分轴结论

调度首轮已返回并停止。有限子成果部分通过，仅确认空service根因、连接参数修复候选及两定向方法/一次真实只读认证证据；整体任务未完成，不验收关闭。连接增量尚未集中独审，不能由主控文件核对替代；原六项无完整通过。

空service不是PG不可用，真实对照在相同目标/秘密/环境得到definition of service空名未找到，移除该无效参数并在驱动前拒PGSERVICE/PGSERVICEFILE后真实认证成功，原loopback/hostaddr及options保持。现新增确定P1是原observe_identity对实际172.19.0.2/32文本误拒绝；真实预检失败与原函数回放相互支持。仅改主机地址表示形式的解析即可处理，不允许放宽其他目标身份相等或掩码语义。源只读EMPTY_QUERY全false是该时点事实，不能据此签六项或当前恒为空。

两容器在原post时点均停止、API未启动，主控本次没有现场探针。产品源码/SQL/权限/原生启动及用户私配范围不扩大；同号128/R122续作01，允许observe_identity的完整主机地址文本兼容和直接测试，保持服务选择防护及其余身份核验。

## 前向编排调整

执行层正确停在源累计3/4后，因为余一次启动不够完成原六项。主控将同一source CID的累计启动上限从4前向5，新增容器/卷/网络仍0；总10800工具秒、1800PG持有、900API持有、API3和interrupted2及原日历截止{deadline}不变。这是同资源普通一次重启余量调整，非新数据/权限/外发采用包，无须用户再批已有目标。

连续保守投入7200/10800、精确unknown，128首轮保守2400/6000；本轮仅恢复未用3600秒含900保存，原127/125/126/120/117历史失败和unknown不重置。当前入口5/6；续作主批entry06，若预算与硬资源余量仍够且仅普通夹具明确有据，前向允许一次备用entry07，累计最多7，成功即停不消耗备用。不能把备用当新启动额度或重放DDL。

采用三段一次回传路线，source第4次启动完成反例/安装/权限/首个原生API并停；interrupted第2次启动唯一002提交未知/拒绝/停；source第5次启动同库第二API重开、verify/坏绑定拒绝并停。第四项的两个API周期跨实际PG停止/重启观察，修正未运行辅助check4当前只循环API而不停止PG的流程安排，不降低原重开证明。续作先离线核完整余段再开资源。稳定后两产品修正集中独审，不逐个小步骤另审。

当前完整接续卡置顶原DocuN/tasks/TASK-128.md，旧完整卡原字节留后并明示历史；调度待人工转交原A+工程窗口，不伪造接收。Q冻结、T0空、真实provider/费用0，STEP018/019/020、M1及项目不放行。
'''
    DECISION.write_text(decision, encoding='utf-8', newline='\n')
    scope = {
        'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作01', 'issued_at': stamp, 'valid_until': deadline,
        'source_approval': 'AP-125-NORMAL-INSTALL-01，用户确认及项目普通修复/编排授权',
        'orchestrator_forward_changes': {
            'product_scope': 'connect修复保留，新增observe_identity主机格式兼容及必要测试',
            'source_pg_start_cap': {'before': 4, 'after': 5, 'same_cid_only': True},
            'combined_entry_cap': {'before': 6, 'after': 7, 'one_conditional_backup_only': True}},
        'current': {'combined_entries': 5, 'source_pg_starts': 3, 'interrupted_pg_starts': 1,
                    'api_starts': 0, 'pg_holding_seconds': 21.66196846961975, 'api_holding_seconds': 0,
                    'tool_conservative_cumulative_seconds': 7200, 'tool_exact_seconds': None},
        'caps': {'tool_cumulative_seconds': 10800, 'restored_tool_seconds': 3600,
                 'save_cleanup_reserve_seconds': 900, 'pg_holding_seconds': 1800,
                 'api_holding_seconds': 900, 'source_pg_starts': 5, 'interrupted_pg_starts': 2,
                 'api_starts': 3, 'combined_entries': 7, 'new_container_create': 0,
                 'new_volume': 0, 'new_network': 0, 'provider': 0, 'fees_cny': 0},
        'resource_identity_source': obj(E / 'checkpoint.json'), 'objects_as_of_post': post['objects'],
        'Q': 'FROZEN', 'T0': None, 'extra_user_confirmation_needed': False,
        'scope_does_not_change_sql_roles_or_data_model': True,
    }
    save_json(OUT / 'continuation-scope.json', scope)
    manifest = {
        'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作01', 'issued_at': stamp,
        'root_entry': obj(ROOT / 'AGENTS.md'), 'result': report,
        'current_product_baseline': current_product,
        'rules': [{'path': row['absolute_path'], 'sha256': row['sha256']} for row in rules],
        'old_contract': obj(before / CARD.name), 'old_permit': obj(PRIOR / 'permit.json'),
        'return_check': obj(OUT / 'return-check.json'), 'scope': obj(OUT / 'continuation-scope.json'),
        'decision': obj(DECISION), 'evidence': frozen_evidence,
    }
    save_json(OUT / 'input-manifest.json', manifest)
    contract = '''# TASK-128 / R-122 续作01 NAT主机地址格式修复及剩余六项完整验证

本段为当前唯一有效合同。下方旧卡只保留历史，不叠加其旧产品范围、已封存余量或4次source启动上限。仍用同TASK/R、同一工程窗口、统一结果和全部原证据。

## 目标、接收与交付

接收A+增强执行，继续刚完成128首轮的原125/127工程窗口；理由为正式身份核验、事务提交与权限/生命周期组合风险。实际客户端/型号如实登记，不以档位冒充身份。没有并行写入/独审，不交原126独审执行。

一次连续完成已实证的NAT主机地址格式修复、直接定向验证、原六项真实安装与精确停止，不为每个正常步骤回传。结果置顶续写D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-result.md，13923字节首轮原文必须为完整后缀保留；原失败/停止记录不覆盖。新辅助与原始证据写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/，首轮execution原件不改。稳定后产品两处增量及受影响证据统一交集中独审，不自签最终验收或Q。

完成标准是地址修复保持原身份安全目标、六项分别有真实行为原件、两API周期及真实PG重开可核、成功/未知收据真实且互不混淆、预算与失败完整和自有资源停止。原连接子成果可复用，六项不存在旧PASS可继承。整体未达标如实部分交回，不保证未运行必过。

## 项目规则、依据与最小上下文

项目根D:/shspic/project_NO3_RetroLume-agent，入口为该根AGENTS.md。task_model V4.0、公共AGENTS CHG-0003锁定，公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。读其DocuS/AGENTS.MD与WORK.MD执行合同/权限/停止/记录有关条款；同窗同版已读内容复用，只补变化。指纹源为本项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，公共只读。

需求v1.4、架构v1.72、执行动态v3.00，关联TASK128/R122、127/R121、125/R119及126/R120，STEP018/019/020、NFR-004/CON-002/DR-002与既有隔离约束。主控已核@CHECKS@条身份引用与四文件实际差异，接收有限连接子成果；整卡未关闭，NAT格式为开放P1，连接修复待集中独立增量审计。

用户已确认AP-125-NORMAL-INSTALL-01；本卡普通修复与编排沿用项目既有授权。主控现明确增加observe_identity主机表示格式修复权，并将同一source累计启动4前向5，入口累计6前向7且第7仅条件备用。没有新增资源/数据/角色/外发权限或总时间、持有/费用，执行者不得再自行扩大。

当前scope、输入清单、原文核证和许可在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/orchestration-continuation01-20261023/。签发@STAMP@；截止保持@DEADLINE@，Asia/Shanghai，不新开24h。文件保存只是待人工转交，不凭此宣称已接收/执行。

先读本卡全文、上述scope/permit/input-manifest、TASK128-work-decision和共享顶部；再读128首轮结果、connection-comparison/credentials-equal、fixed-formal-connection/real-preflight/actual-empty-facts、nat-reproduction及proposed-nat-fix.diff、当前产品实际diff和未变原接口。源文件/旧六项必要正文已包含本合同；同窗已读规则、固定001—015、start_local/Compose、data_exit根绑定/ControlHub/q_roles等只补实际缺失，不全仓重复研究。原127全部证据/检查点/报告只读，旧18/9方法与未变126审计按范围复用，不重跑。

## 已确定事实及冻结快照

127的空服务名真实根因已由相同目标/秘密/环境对照确认；当前connect不传service空串，并在驱动前拒PGSERVICE/PGSERVICEFILE存在，包括空值，环境不变。显式host/hostaddr=127.0.0.1、精确端口/库/用户/密码、SSL及options仍在。两定向方法通过和修后一次真实只读认证是有限证据，不是完整apply/ACL验证，不再真实复现旧坏连接。

当前正式只读连接成功，原preflight却因inet_server_addr()::text返回172.19.0.2/32被ip_address拒绝。其余DB/OID/systemid/login/PG17/UTF8/superuser均符合；真实EMPTY_QUERY所有字段false。回放原函数与实际预检共同定位格式缺陷，但回放不是另一次真实认证。未应用diff只给参考，不得称已修；本轮先实际实现与定向验证。

当前安装器29663字节/hash4513241f71fa3c15aa1d0ee7dc79e757a49f3583924dd5530b49ac6cc71b0ac5；测试33779字节/hash17bb640dce04e860d2b7343d7a034867b2088484c54578051a9741c8798a520a。其余当前41产品与允许四文件差异在新input-manifest逐项冻结；原首轮58输入/七规则和raw原件hash已核。源当前空态只对应entry05时点，启动后仍需只读核身份/空态和无submitted未知，不猜库恒为空。

## 允许改动与修复标准

允许deploy/initialize_normal.py仅在observe_identity的server_address格式解析作最小兼容，保留已经完成的connect安全修复；为保持同一语义的直接小帮助可以实现。不得改IDENTITY_QUERY、preflight对目标身份/排他性/权限的要求、SQL或原事务；不可用SQL host()重投影、修改驱动行/模拟器来掩盖产品缺陷。

兼容原裸IPv4/IPv6以及只表示完整主机的IPv4 /32、IPv6 /128。可按所提ip_interface思路解析并核prefixlen等于该地址max_prefixlen；不能把任意网段/短前缀当主机。保留原返回原始server_address/server_port值供收据/verify比较，不擅改序列化或隐藏真实NAT。所有原database/OID/system_identifier/installer/session login、superuser、PG17、UTF8和端口等式/类型限制不动；不是把server_address强改为客户端127.0.0.1，服务端NAT仍合法。

测试只在backend/tests/test_normal_install.py新增直接格式正/反例，原bare地址行为保留；至少覆盖实际172.19.0.2/32、原bare IPv4、IPv6完整主机表示、非法地址/非主机前缀拒绝；同一合法地址下错误OID/systemid/login等仍拒绝，拒绝不能因第一道格式错误而虚假通过。数据来自原真实行时标回放，无网络假装实测。测试文件新增后可将受影响19/22两方法与新增格式方法放一次集中小批，真实导入产品且运行前后绑定实际hash，记录器不冒PG/ACL。已有两方法历史证据不删，不重跑全部18/9。

README.md与deploy/normal-install.md仅按最终实际结果最小更新说明；新增代码注释简体中文，避免无关重排。新辅助仅写continuation-01，包括按新scope修复预算/身份/as-run/阶段调度和安全诊断；不得原地覆盖首轮helper或旧许可。保存产品pre/post副本、hash、完整diff和实际as-run。

其余产品、001—015、manifest、角色/profile/权限模型、业务/app、Q/Grant、原配置schema、start_local、正式Compose、依赖锁一律冻结。不得放宽hostaddr、目标身份、防8.3路径、秘密隔离、全局service拒绝、提交未知不重放或验证函数。其他需要改变这些目标或主要模型的风险仍停相应部分交回；同一已确定主机格式根因的直接兼容修正可在本卡合并完成，不为一个相关断言再逐项转卡。

## 两个现有对象、保留与凭据

source仅CID db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d，名称retrolume-q-first-normal，卷retrolume-q-first-normal-data，Compose项目retrolume-first-install-source，bridge Id2f79fb05977e79f3fa89791f4a97553334be384ba6df89ecd0dc650c2018adb2；127.0.0.1:55482，库retrolume_q_first_normal，OID16384，systemid7699647093882925094，bootstrap retrolume_source_bootstrap。

interrupted仅CID549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8，名称retrolume-install-interrupted，卷retrolume-install-interrupted-data，Compose项目retrolume-first-install-interrupted，bridge Idc333276027ca367edf8086eec15763185fe2800f66c820792e7ad96cb842d610；127.0.0.1:55483，库retrolume_install_interrupted，OID16384，systemid7699647123872251942，bootstrap retrolume_interrupted_bootstrap。

PG17/vector0.8.6，缓存镜像Id sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，CPU1/512MiB/pids128/restart=no/loopback映射/无host bind。最多一PG活跃，无新create/volume/network/换名/换端口/镜像拉取构建。先inspect全部真实身份/创建时刻/挂载/限制与root实体，不能只凭名字或两库相同OID授权；主控引用原post停止，不替代当前实际检查。

只复用.runtime/normal-first-install/source及interrupted原四根和originals、dataset/instance/originals_root三个UUID；完整SID/device/file-id/网络/卷创建身份在原checkpoint及本轮scope，不再生成或搬动根。不读取别的runtime/scratch私配。当前用户DPAPI内存解密既有秘密复用，不重新随机、重置密码或ALTER既有角色，禁止明文/密文/DSN/Env/完整Compose写证据或argv。业务/快照登录仍各自retrolume_normal_app、retrolume_normal_snapshot与retrolume_interrupt_app、retrolume_interrupt_snapshot，十三NOLOGIN职责组按原SQL创建，无旧库操作；应用不能拿安装管理员DSN。

API仍0次、尚未选定；只从18122/18124/18126顺序核可用后一次固定，不轮换。现存根/对象已是本卡资源，所以不能因原草案“根须不存在”去重建；本轮按实体身份复用。全部成功/失败库卷/网络和收据保留，停止只按精确CID/自有API PID+birth/句柄/树；无prune、down-v、DROP DATABASE、递归删除或旧scratch清理。

## 先离线完备，再一次执行三段

本轮不再独占一次source启动只试格式。先离线完成格式修复/必要集中测试、正常/异常分支与旧guard差异检查，准备完整余段控制器、身份/预算/安全日志和保存。检查其配置路径、env引用、规则/产物hash、序列/唯一收据、helper是否还读旧permit、输入allowlist是否仅四文件实际变化。新runner输入清单须绑定本轮最终产品，不能把全部冻结对象改成无约束的“当前即基线”。

首次真实连接成功后即在同次source启动连续做所有source前半段，避免每个查询停开。原未运行helper的check4目前只for循环两API而不在两次之间停PG；本轮必须按A/C拆分，实际记录两API跨PG停/开的事实。只改验证调度，不改产品入口或弱化旧重开断言。

三段正常顺序如下，原六项标准全部保留。

A段，source累计第4次启动。修后原只读preflight在正确配置下通过并核同一实际空库。然后分别错误OID/system_identifier、非空表与职责组碰撞四类真实拒绝，必须命中相应错误/零安装器写，关闭旁观连接避免other_clients冒充。临时对象仍仅public.retrolume_install_probe_nonempty与retrolume_data_app NOLOGIN组，先证不存在并记创建OID，只在正式安装前按同身份精确撤销，禁止清别的对象或误DROP后来的正式职责组。原失败收据不复用覆盖，用本轮新收据。

同一source使用正式apply执行原001—015原事务/guard，不重新初始化001、不Recorder替代驱动。实际核013后normal/R01、014/R02、015/R03、schema_checks/q_roles，17阶段及37行完整成功收据。原server_address带完整主机掩码事实应原样进入观察/收据，不擅改为裸串。成功安装只一次；若非预期submitted未知，立即停相应安装，不补签、不从DB状态推断可以重放。

分别真实登录业务/快照，核原ROLE_CAPABILITIES/MEMBERSHIPS及实际只读控制行；快照不能业务写/读维护秘密/SET业务或owner，业务无管理/owner/传递SET/INHERIT/ADMIN能力。少量真实权限查询/有界回滚拒绝即可，不造持久业务账或全项目安全重测。按正常data_exit源配置/四根/ControlHub绑定，model/integration/Q/preview保持原生关闭；启动原deploy/start_local.py --container retrolume-q-first-normal --port 固定API --shutdown-stdin，核真实capabilities/readiness及业务login。预期Q因外部门未齐关闭要与本地schema/正常源失败区分；不读一个200或503就标全过。第1个原生API周期正常关闭、树/端口结束，再停source并记身份/数据/控制行/收据对照。

B段，只启动interrupted累计第2次。固定002原SQL真实COMMIT且耗尽结果后唯一隐藏一次确认，留001 confirmed、002 submitted/unknown、无003/complete/自动重放，另只读核实际已提交。原失败127收据并非此情形，本轮只许一次实际注入。原收据重复apply与verify须本地拒绝，新收据对已部分库预检零写拒绝；保留部分库/卷，不继续003/补签/退款/清空。此一次预定未知可按场景观察和收尾，其他非预期未知不享豁免。停止interrupted，确认后才进入C。

C段，source累计第5次启动。同一CID/DB OID/systemid/UUID/根/ControlHub/原记录原生重开第2个API周期，核无自动迁移/新身份/重置、活动/次数/费用账无业务变化，再正常关闭API。期间仅使用新业务凭据，不把source管理员交应用；正常根绑定/选择不退回旧目标或TESTONLY。

source仍活跃时完成正式verify CLI，仅提供管理员密码环境引用，不提供其他三秘密及业务/快照DSN，实际READ ONLY/schema/roles/目标身份和完整成功收据原字节不变，无DDL/DCL/业务写。坏收据绑定输入在连接前0调用拒绝，正常verify必须真实认证。最后停止source，核两CID Running=false/Pid=0、自有API树无活跃、端口释放；保留全部持久数据。

第四项的API两周期分布A/C，B插入两者之间不改变正常源；第六项仍在B后回同一source。这样所有原检查不减，只需原基础上再给source一个start。本轮只按缺口执行，既有坏service根因、真实连接对照和离线已适用证据不反复实际复现。

## 连续投入与条件备用

原127保守4800秒/精确unknown，128首轮保守2400秒/精确unknown，累计保守7200/10800。本次仅恢复余3600工具秒，其中900保存/自有清场；未增加总工具时间。原截止@DEADLINE@保持，不能跨时窗偷偷恢复。125/126/120/117全部旧失败/unknown原样保留。

本次主批entry06；若仅明确普通夹具缺陷、原始失败/修正依据齐全、同根因未达两次失败且剩余时间与物理启动/持有硬上限仍足，主控前向允许一次定向备用entry07，只恢复失败/未完成段；成功即止不用备用。准备/只读核文件不假算真实启动，也不得将另起真实控制器伪称同一次入口。离线自检要有界，测试卡死收证后只结束确属本卡的进程，不等到吃光余量。

累计source当前3，前向上限5，余2；interrupted当前1/2余1；API当前0/3。PG持有当前21.66196846961975/1800秒、API0/900秒；累计容器/卷/网络仍原2/2/2且新增0。不把entry07理解为额外启动权。实际计时覆盖start请求到stop确认和普通筹备/修码，父子重叠分层不双算；精确unknown如实保留加保守占用。

Docker暖机后启动PG/API前可用物理内存>=512MiB，运行约2秒采样，连续两次<256MiB停止新动作并精确关闭自有API/PG。最多一个PG、一个API，无浏览器/renderer；不反复要求用户释放内存或恢复2GiB门。提前留原生start_local优雅停150秒和父等待已有上界、保存储备。离线修码不挂着PG空等耗持有；停PG前先确认余下阶段仍能在累计start内完成。

产品核心策略/权限或SQL需改、新高风险/主要模型、非预期未知提交、同根因两次有据修正仍失败、任一实际预算/日历/压力到门，停受影响段并完成不受阻项后一次交回。新证据只能触发相应有限修正，不能通过弱化正确断言/改目标身份/跳过检查造绿。

## 原始证据、审计与回传

新增证据绑定最终实际安装器/测试/辅助as-run、精确资源和原生配置结构，逐项六检查到原始命令/退出/时间/DB错误/阶段收据/生命周期/停止，保留普通夹具所有失败与修正diff、选择范围和继承依据。诊断异常限长且先脱敏后保存，不能再丢成一个通用错误，也不能原样保存str(error)、完整stderr或kwargs泄露秘密。Docker完整JSON只在内存取脱敏白名单，禁止输出Env/展开Compose。平台审批仍适用，未执行拦截如实记，不拆命令/换工具绕过。

两产品变化稳定和卡内相关验证结束后，主控集中独立审计connect服务隔离与observe_identity主机格式解析及实际影响/真实原件。原126未变SQL/角色/目录保护与旧18/9证据按范围继承，不逐条另卡审；本窗口只自查，不能签独审或主控最终关闭。README/说明只写实际通过范围，未跑保持未验证。

Q继续FROZEN，T0/72h为空，provider/Embedding/计量/真实付费、索引/查询/生成、三固定活动、grant/QAuthority.bind/InstanceBinding、浏览器/预览/业务Job和Git写全0；100/25及分额、账号/token/模板/容量外部门不变。本卡不放行STEP018/019/020、M1、项目或发布。

结果置顶续作01并保首轮完整后缀，先一句结论/实际变化和六项逐项状态/原件导航，再列真实客户端/模型、TASK/R/STEP、身份/环境、验证/复用/失败/未跑、连续工具/入口/持有/启动/压力账、偏差/停止/保留资源、风险与待同步文档。验收和共享编号/DocuS由主控维护。当前唯一人工是把本卡交原窗口，完成带回路径，不要求用户密钥/手工建库/清理/释放内存。保存复读后仅回一句真实结论与D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-result.md的可点击绝对路径。

## 以下为128首轮原完整合同历史，不再作为新增执行许可

'''.replace('@STAMP@', stamp).replace('@DEADLINE@', deadline).replace('@CHECKS@', str(len(checks)))
    assert '*' not in contract and '\n|' not in contract
    for token in ['observe_identity', 'entry06', 'entry07', '3600', '7200', '10800', '/32', '/128', '37行', 'source累计第5次', 'FROZEN']:
        assert token in contract
    # 同号续作登记后更新完整卡，核读后才记待转交。
    registered = f'# 执行动态文档\n\n文档v3.00，2026-10-23，Asia/Shanghai。需求v1.4、架构v1.72。\n\n{stamp}。128首轮已返回未关闭，续作01同号登记，完整新卡保存核读中。\n\n'.encode('utf-8')
    STATE.write_bytes(registered + state_old)
    CARD.write_bytes(contract.encode('utf-8') + card_old)
    assert CARD.read_bytes().endswith(card_old) and CARD.read_text(encoding='utf-8').startswith(contract)
    permit = {
        'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作01', 'issued_at': stamp, 'valid_until': deadline,
        'status': '待人工转交', 'actual_dispatch': False, 'acceptance': None,
        'receiver': 'A+，刚执行128的原125/127工程窗口', 'task_card': obj(CARD),
        'input_manifest': obj(OUT / 'input-manifest.json'), 'scope': obj(OUT / 'continuation-scope.json'),
        'restored_tool_seconds': 3600, 'cumulative_tool_cap_seconds': 10800,
        'source_starts_current': 3, 'source_starts_cap': 5,
        'interrupted_starts_current': 1, 'interrupted_starts_cap': 2,
        'api_starts_current': 0, 'api_starts_cap': 3, 'entries_current': 5, 'entries_cap': 7,
        'new_resources': 0, 'Q': 'FROZEN', 'T0': None, 'real_provider': 0, 'fees_cny': 0,
        'no_budget_or_failure_reset': True, 'old_permits_not_reactivated': True,
    }
    save_json(OUT / 'permit.json', permit)
    arch_prefix = f'''# 架构动态文档

文档v1.72，2026-10-23，Asia/Shanghai。需求v1.4、执行动态v3.00、task_model/07。以下v1.71原字节保留。

## 连接候选实证及NAT主机地址表示缺陷，原六项续作01

{stamp}。128首轮已确认libpq把空service当实际服务名的根因，connect不再传空串且在驱动前拒环境PGSERVICE/PGSERVICEFILE；两定向方法与一次真实只读认证支持有限候选，稳定后集中独审尚待。未变hostaddr/loopback、原SQL/角色与目录保护沿用旧有效范围。

真实preflight另被172.19.0.2/32主机文本误拒绝，原observe_identity只用ip_address；其余身份相符、源EMPTY_QUERY全false与回放定位该确定P1，但原六项尚无完整通过。续作允许完整主机表示解析兼容，拒短前缀/非法地址，所有其他身份等式及收据原值保持，未修改SQL/profile或降低正确断言。

同号128续作01一次连续完成格式修复和原六项。两原CID/卷/网络/根复用，source启动上限4前向5仅补同资源一次重启，原总工具/持有与日历不增加；A源安装/首API、B独立002未知、C同源重开API/verify完整覆盖。原执行辅助的双API循环须改为真实跨PG停/开，不把计划代码当运行证据。无新平台或数据模型。

Q冻结、T0空、真实provider/费用0，外部账号/计量/token/模板/容量与首次启用门保持。当前事实仍为有限候选及部分验证，不签完整安装、STEP或项目完成；本轮主控仅核文件原件，没有产品或现场资源操作。

## 以下为v1.71及更早历史

'''.encode('utf-8')
    ARCH.write_bytes(arch_prefix + arch_old)
    state_prefix = f'''# 执行动态文档

文档v3.00，2026-10-23，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.72、task_model/07。以下v2.99原字节保留。

## 128首轮有限连接成果已回收，NAT格式与六项续作01同号待转交

{stamp}。用户带回128结果，主控核{len(checks)}条身份引用无缺失漂移，报告13923字节/hashfd9445acbca5abe2d3b1daa8bfb8f0793d6be24ba9e70a08b7628de09b4e0558，58输入/七规则及允许四文件差异相符，安装器AST仅connect改变。首轮调度已返回/停止；有限连接子成果部分通过，整体未完成、P1开放，不能验收关闭或签六项通过。首轮报告原字节与127失败原件保持。

实际同目标/秘密/环境对照确认空service导致OperationalError，修复后在PG170011/vector0.8.6以相同身份只读连接成功；19/22两方法JSON通过及其直接有限范围采纳，未重跑18/9。connect服务隔离修复候选仍待最终集中独审。实际preflight另因server_address=172.19.0.2/32误拒绝，原函数回放与真实空态支持确定格式缺陷；未应用diff仍只是参考，不冒已修。六项均无完整PASS，未执行apply/DDL或触发002注入。

两CID/root/卷/network不变，原post时点均Running=false/Pid=0/API未启动、端口无监听；主控不作当前现场推断。累计入口5/6，source3/4、interrupted1/2、API0/3，PG持有21.66196846961975/1800秒/API0/900。原127保守4800与128首轮保守2400，连续保守7200/10800、精确unknown及所有失败留账，未用3600封存后现仅明确恢复给续作01，含900保存，原截止{deadline}不延。

主控为完成同一已授权六项，source同CID启动上限4前向5，仅多一次普通重启，资源/总工具/持有/费用不增；入口6前向7，entry06合并主验、entry07仅有据普通夹具且余量足的备用，通过即止。没有换卡清零，新TASK/R未占号。旧125/126/120/117全部历史unknown和失败预算保持。原128许可不因文件可读而自动复活，以当前新permit/scope为准。

原TASK128/R122完整卡置顶续作01且首轮原合同保为完整后缀，核读后调度待人工转交A+刚执行128的原工程窗口；没有真实派发/接收或在途证据。新产品权仅observe_identity完整主机地址表示兼容/直接测试与必要说明，connect修复保留，SQL/角色/profile/权限模型/业务/启动器/Compose/依赖锁不改。先离线准备全余段，一次A源第4开安装/权限/首API后停、B中断第2开唯一提交未知后停、C源第5开实际同库重开API及verify后停，第四项双周期跨真实PG停/开，不再仅循环两API。产品两处稳定后集中增量审计，不逐小步骤审旧代码。

核证/当前work-decision/新卡输入与许可在TASK128/orchestration-continuation01-20261023。主控本轮产品导入/测试/PG/Docker/API/现场探针均0。Q FROZEN、T0/72h空、provider/费用0、100/25与分额/28Must/89动作不变，外部计量/账号/token/模板/Embedding容量门不齐。STEP018进行中/部分验证，019/020/M1/项目/发布不放行。CHG1668—1672，下一1673。

## 以下为v2.99及更早历史

'''.encode('utf-8')
    STATE.write_bytes(state_prefix + state_old)
    changes_text = f'''
- CHG-1668，{stamp}，Codex编排Agent，DocuN/results/TASK-128-work-decision.md。核回有限连接根因/修复与真实空态，采纳主机格式P1，整体未关闭；集中裁定同号续作范围和前向一次source重启预算，不重置失败。

- CHG-1669，{stamp}，Codex编排Agent，DocuN/tasks/TASK-128.md。置顶续作01完整合同并保首轮原字节，合并格式修复/必要检查和六项三段真实验证，原A+工程窗口待人工转交。

- CHG-1670，{stamp}，Codex编排Agent，DocuS/架构动态文档.MD。v1.72登记连接候选、NAT完整主机表示缺陷和待修边界，原模型/SQL/权限/Q不变，未冒验证完成。

- CHG-1671，{stamp}，Codex编排Agent，DocuS/执行动态文档.MD。v3.00登记首轮实际返回及部分成果/剩余P1、连续预算/固定资源和续作01待转交，旧v2.99原字节保留。

- CHG-1672，{stamp}，Codex编排Agent，DocuN/evidence/TASK-128/orchestration-continuation01-20261023/。保存有限身份/实际差异/原件核证、旧共享与旧卡、新scope/输入/许可及保存复读；主控产品运行0。
'''.encode('utf-8')
    CHANGE.write_bytes(change_old + changes_text)
    assert STATE.read_bytes().endswith(state_old) and ARCH.read_bytes().endswith(arch_old)
    assert CHANGE.read_bytes().startswith(change_old) and CARD.read_bytes().endswith(card_old)
    assert obj(ROOT / 'DocuN/results/TASK-128-result.md') == report
    for row in current_product:
        assert obj(Path(row['path']))['sha256'] == row['sha256']
    proof = {
        'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作01',
        'files': [obj(path) for path in [CARD, DECISION, STATE, ARCH, CHANGE, OUT / 'return-check.json', OUT / 'input-manifest.json', OUT / 'continuation-scope.json', OUT / 'permit.json']],
        'status': '待人工转交', 'actual_dispatch': False, 'acceptance': None,
        'identity_reference_checks': len(checks), 'mismatches': 0,
        'old_card_and_shared_bytes_preserved': True, 'executor_report_unchanged': True,
        'product_runtime': 0, 'product_import': 0, 'tests': 0, 'live_resource_probes': 0,
        'new_runtime_resources': 0, 'new_task_allocated': False, 'next_CHG': 1673,
    }
    for row in proof['files']:
        Path(row['path']).read_text(encoding='utf-8')
    save_json(OUT / 'save-proof.json', proof)
    print(json.dumps({'saved': True, 'TASK': 'TASK-128', 'round': 'continuation-01',
                      'checks': len(checks), 'mismatches': 0, 'card_bytes': CARD.stat().st_size,
                      'restored_seconds': 3600, 'source_start_cap': 5, 'new_resources': 0,
                      'valid_until': deadline, 'product_runtime': 0}, ensure_ascii=True))


if __name__ == '__main__':
    main()
