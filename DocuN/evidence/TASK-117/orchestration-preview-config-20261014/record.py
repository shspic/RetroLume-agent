"""补齐合成operator授权和路径交接，不生成密钥/票据或执行产品。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
OUT = Path(__file__).resolve().parent
CARD = ROOT / 'DocuN/tasks/TASK-117.md'
WORK = ROOT / 'DocuN/results/TASK-117-work-decision.md'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def save(name, value):
    p = OUT / name
    assert p.resolve().is_relative_to(ROOT) and not p.exists(), str(p)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert load(p) == value

def prefix(path, text, old):
    assert '*' not in text and not re.search(r'^\|', text, re.MULTILINE)
    path.write_bytes(text.replace('\n', '\r\n').encode('utf-8') + old)
    assert path.read_bytes().endswith(old)

assert OUT.resolve().is_relative_to(ROOT)
assert not (OUT / 'recorded.json').exists()
before = {p: p.read_bytes() for p in (CARD, WORK, STATE, CHANGES)}
assert identity(CARD)['sha256'] == '5530fb07e25a00511a0c910b7d2306e81d63e0e8e10aa35541b6b925069bf2a9'
assert '文档v2.58' in before[STATE].decode('utf-8-sig').splitlines()[2]
numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', before[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert numbers[-1] == 1404
report = ROOT / 'DocuN/results/TASK-112-result.md'
assert identity(report)['sha256'] == '1dab1126aa72e335288d037baed5bc13b7cfdc1e4a386b6c04553e630f871571'
manifest = ROOT / 'deploy/preview/load-manifest.json'
assert identity(manifest)['sha256'] == '8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f'
runtime_files = {name: identity(ROOT / 'deploy/preview' / name)['sha256']
                 for name in ('runtime.cjs', 'runtime.css', 'runtime.html', 'descriptor.schema.json')}
runtime_hash = hashlib.sha256(json.dumps(runtime_files, ensure_ascii=False, sort_keys=True,
                                        separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()
assert runtime_hash == '6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597'
accepted115 = load(ROOT / 'DocuN/evidence/TASK-115/orchestration-final-receipt-20261014/received.json')
accepted_map = {row['path']: row for row in accepted115['current']}
fixed_current = {}
for name in ('backend/app/preview/host_policy.py', 'backend/app/preview/pipe.py',
             'backend/app/preview/production_supervisor.py'):
    expected = accepted_map[name]
    actual = identity(ROOT / name)
    assert actual == {k: expected[k] for k in ('bytes', 'sha256')}, name
    fixed_current[name] = actual
assert identity(ROOT / 'deploy/preview/renderer-protocol.cjs')['sha256'] == 'd7907b8eb2414098162a03e7adc8d9f8953f026ad33a0ebbee8330a834755e24'

observed_at = datetime.now(timezone(timedelta(hours=8))).isoformat()
budget = load(ROOT / 'DocuN/evidence/TASK-117/execution/budget.json')
receipt = load(ROOT / 'DocuN/evidence/TASK-117/execution/receipt.json')
assert budget['permit'] == receipt['permit'] == 'TASK-117-STEP018-INTEGRATION-S01-20261014'
notice = (OUT / 'notice.md').read_bytes()
assert '*' not in notice.decode('utf-8')
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for p, raw in before.items():
    (backup / p.name).write_bytes(raw)

observed = {
    'observed_at': observed_at, 'task_received_basis': '用户提供执行窗口截图及当前实际receipt/budget，S01实施中',
    'receipt_status': receipt['status'],
    'start_utc_conservative': receipt['start_utc_conservative'],
    'start_mono_ns_conservative': receipt['start_mono_ns_conservative'],
    'anchor_basis': receipt['anchor_basis'],
    'counts_observed': budget['counts'], 'caps_observed': budget['caps'],
    'offline_intervals_observed': budget['offline_intervals'],
    'phase_observed': budget['phase'], 'active_root_observed': budget['active_root'],
    'not_final_acceptance_or_continuous_process_observation': True,
    'execution_records_written_by_main': False
}
save('inflight-observation.json', observed)

record = {
    'recorded_at': observed_at, 'TASK': 'TASK-117', 'R': 'R-111', 'permit': budget['permit'],
    'reason': '主控卡面把已通过独审的固定宿主误当存在可用operator票据，实际112未生成；补正常部署交接',
    'normal_operator_deployment_allowed_for_S01_synthetic_only': True,
    'audit_decision_created_by_implementation_agent': False,
    'audit_report': {'path': str(report), **identity(report)},
    'main_G11_acceptance': {'path': str(ROOT / 'DocuN/results/TASK-111-G11-final-acceptance.md'),
                           **identity(ROOT / 'DocuN/results/TASK-111-G11-final-acceptance.md')},
    'current_preview_sources_match_accepted115': fixed_current,
    'fixed_load_manifest': identity(manifest), 'fixed_renderer_sha256': runtime_hash,
    'planned_operator_config': str(ROOT / 'DocuN/evidence/TASK-117/execution/synthetic/operator/preview.deployment.json'),
    'planned_ticket': str(ROOT / 'DocuN/evidence/TASK-117/execution/synthetic/operator/preview.review.json'),
    'key_env_name_only': 'RETROLUME_TASK117_PREVIEW_REVIEW_KEY',
    'key_or_ticket_generated_by_main': False,
    'API_child_environment_already_injected': '未确认；执行者须正常注入并只核布尔/loader结果，主控不虚报已配',
    'no_runtime_signature_gate_or_schema_change': True,
    'no_Q_user_data_or_fee_activation': True, 'no_budget_or_clock_extension': True,
    'notice': {'path': str(OUT / 'notice.md'), **identity(OUT / 'notice.md')}
}
save('recorded.json', record)

CARD.write_bytes(before[CARD] + b'\r\n\r\n' + notice)
assert CARD.read_bytes().startswith(before[CARD]) and CARD.read_bytes().endswith(notice)
work_text = f'''# TASK117/R111 — 在途预览operator部署交接补充

{observed_at}。用户提供当前工程窗口截图，结合实际117 receipt/budget，调度已真实接收/S01实施中；其它接线继续，预览L10缺正常operator配置/票据。主控核112独立终审与G11最终关闭、固定load/四runtime及115当前host_policy/pipe/SUP身份，确认是部署交接漏项，不是要求用户提供密钥或重做独审。

原卡“复用已验签票”不准确，112当时未生成生产配置/票据。本次明确授权原工程窗口作为仅本轮合成实例受托operator，基于真实112 approved结果正常生成HMAC认证票据与配置；不改HostPolicy/验签器、审计报告或固定镜像，不用旧TASK111合成授权字面值绕门。具体配置/ticket绝对路径、七字段/报告hash、当前固定身份、内存随机key与仅API子进程env注入、正常loader核验见orchestration-preview-config-20261014/notice.md。主控未生成/查看密钥，未确认API子进程已注入，不虚报部署完成。

原117完整卡追加本补充、原31049字节前缀保留，原execution/receipt/budget/events/control不写，历史首点/失败/根/时间/次数均连续，无新增预算或延时。当前账观测只作在途记录，不签12方法或控制合规最终验收；真实provider/费用仍0且Q未启用。无需新TASK或用户再次授权，配置/测试在原卡连续完成，报告统一交回。

## 以下为原S01许可历史

'''
prefix(WORK, work_text, before[WORK])
state_text = f'''# 执行动态文档

文档v2.59，2026-10-14，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.34、task_model/07。以下v2.58历史原字节保留，架构方案不变。

## TASK117实际接收/实施中，预览operator交接已明确

{observed_at}。用户截图及本卡execution receipt/budget证实原A+工程窗口已接收117/R111/S01并实施，不再标未转交。实际首点2026-10-14T05:21:48.590792Z/mono1226769590214600及原5秒保守扣时说明继承；读取时root1已结束、离线1186.219秒、PG/API/Browser/Native/preview/provider等当前计数按inflight-observation.json实存。是中途观测，不冒卡内最终通过或连续进程监控，原执行账不由主控修改。

预览L10曾因配置/认证票据不存在请求主控路径。主控核112终审1dab1126aa72e335288d037baed5bc13b7cfdc1e4a386b6c04553e630f871571与G11正式关闭、固定v2-08 load/renderer及115已验源身份，确认卡面将“已独审”误当现成部署票据。原117完整卡追加正常operator交接，允许原窗仅S合成实例依据原真实独审结果签署部署认证、内存key仅本API子进程注入并正常验签，不修改审计/验签器/固定程序或伪造批准。主控未签票、未生成key或执行产品，API进程是否已注入由原窗实际核验，不要求用户提供密钥。

具体配置与票据路径、身份/hash、env名、继承链和读后继续说明在DocuN/evidence/TASK-117/orchestration-preview-config-20261014/notice.md，完整卡原前缀保留。此为原已批准合成范围内的配置交接，无新TASK/预算/真实费用或用户数据授权；原首点/所有失败/旧账/资源/次数/Q门均不重置，不自行生成新审计结论。其它实现与验证继续，未回统一结果前主控不验收工程完成。

全项目旧成果/13元/626.566/G11-25-UNKNOWN-R60/count1等及永久只读限定不改；STEP018/019/020/项目未通过。主控仅原件/固定身份/在途元数据和共享维护，产品/SQL/Docker/API/Browser/模型/费用/Git写全0。CHG1405—1411，下一1412。

## 以下为v2.58及更早历史

'''
prefix(STATE, state_text, before[STATE])
entries = [
    ('recorded.json', '112真实审核/关闭与115源身份链，补S合成operator配置，主控不签票/造key。'),
    ('notice.md', '正常票据/config路径、环境注入和loader验证，旧费用/验签/预算门保留，读后继续。'),
    ('DocuN/tasks/TASK-117.md', '同卡追加交接，原前缀保留，原窗口连续执行不另占号。'),
    ('DocuN/results/TASK-117-work-decision.md', '中途部署缺口裁定/原许可不变，主控不接管运行。'),
    ('DocuS/执行动态文档.MD', 'v2.59实际接收/实施中和中途账观测、预览配置交接与0主控运行。'),
    ('before-documents', '原卡/Work/执行/变更原字节留档，执行层账及产品不改。'),
    ('save-proof.json', '保存复读和固定原件保护、CHG连续，无秘密或票据生成。')
]
tail = ''.join(f'\r\n- CHG-{1405+i}，{observed_at}，Codex编排Agent，'
               f'{name if "/" in name else "DocuN/evidence/TASK-117/orchestration-preview-config-20261014/"+name}。{detail}\r\n'
               for i, (name, detail) in enumerate(entries))
CHANGES.write_bytes(before[CHANGES] + tail.encode('utf-8'))
assert CHANGES.read_bytes().startswith(before[CHANGES])
assert identity(report)['sha256'] == record['audit_report']['sha256']
for name, expected in fixed_current.items():
    assert identity(ROOT / name) == expected
save('save-proof.json', {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'files': [{'path': str(p), **identity(p)} for p in (CARD, WORK, STATE, CHANGES, OUT / 'notice.md', OUT / 'recorded.json')],
    'original_card_prefix_preserved': True, 'old_histories_preserved': True,
    'execution_budget_or_receipt_edited': False, 'key_or_ticket_generated': False,
    'product_execution': 0, 'new_permission_or_budget_above_original_S_scope': False,
    'CHG': list(range(1405, 1412))
})
print(json.dumps({'status': 'SAVED_AND_READABLE', 'notice': str(OUT / 'notice.md'),
                  'card': str(CARD), 'execution': 'v2.59', 'last_CHG': 1411,
                  'key_ticket_product_execution': 0}, ensure_ascii=False))
