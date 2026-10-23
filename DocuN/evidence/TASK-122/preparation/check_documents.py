"""本卡唯一一次文档一致性核对；不验证产品行为。"""
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
RESULT=ROOT/'DocuN/results/TASK-122-result.md'
START=datetime.now(timezone.utc)
checks=[]

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check(name, condition, detail):
    checks.append({'id':name,'passed':bool(condition),'detail':detail})

manifest_path=ROOT/'DocuN/evidence/TASK-122/orchestration-20261021/input-manifest.json'
permit=load(ROOT/'DocuN/evidence/TASK-122/orchestration-20261021/permit.json')
check('contract_identity',sha(ROOT/'DocuN/tasks/TASK-122.md')==permit['contract_sha256'],'完整卡与permit摘要')
check('manifest_identity',sha(manifest_path)==permit['input_manifest_sha256'],'锁定输入manifest与permit摘要')
identity=load(OUT/'input-identity.json')
drift=[]
for row in identity['rows']:
    if Path(row['path'])==ROOT/'README.md':continue
    if sha(row['path'])!=row['actual']:drift.append(row['path'])
check('locked_inputs_and_rules_unchanged',not drift,{'checked':len(identity['rows'])-1,'drift':drift,'README':'允许变更，另核before/after'})
read_rows=[json.loads(line) for line in (OUT/'read-ledger.jsonl').read_text(encoding='utf-8').splitlines()]
read_drift=sorted({r['path'] for r in read_rows if Path(r['path'])!=ROOT/'README.md' and sha(r['path'])!=r['sha256']})
check('additional_read_files_unchanged',not read_drift,{'read_events':len(read_rows),'unique_files':len({r['path'] for r in read_rows}),'drift':read_drift})

matrix=load(OUT/'remaining-must-matrix.json')
samples=load(ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json')
budget=load(ROOT/'DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json')
check('effective_adopted_budget',matrix['global_max_requests']==100 and matrix['global_max_cost_microunits']==25000000
      and sum(r['max_requests'] for r in matrix['roster'])==100 and sum(r['max_cost_microunits'] for r in matrix['roster'])==25000000,
      [(r['activity_id'],r['max_requests'],r['max_cost_microunits']) for r in matrix['roster']])
check('roster_exact_identity',[(r['activity_id'],r['max_requests'],r['max_cost_microunits']) for r in matrix['roster']]
      ==[(r['activity_id'],r['max_requests'],r['max_cost_microunits']) for r in budget['roster']],'固定UUID与48/28/24、12/7/6')
actions=matrix['actions_in_recommended_order']
ids=[a['id'] for a in actions]
counts=Counter(a['kind'] for a in actions)
check('action_counts',len(ids)==len(set(ids))==89 and dict(counts)=={'source_index_embedding':6,'query_embedding':41,'model':41,'html':1},dict(counts))
check('row_action_consistency',all(sum(a['row']==r['id'] for a in actions)==r['requests'] for r in matrix['rows']),
      {r['id']:r['requests'] for r in matrix['rows']})
check('reserve_and_allocation',all(r['planned_requests']*250000==r['planned_reserve_microunits'] and r['planned_requests']<=r['max_requests'] and r['planned_reserve_microunits']<=r['max_cost_microunits'] for r in matrix['roster'])
      and sum(r['planned_requests'] for r in matrix['roster'])==89 and sum(r['planned_reserve_microunits'] for r in matrix['roster'])==22250000,
      {'planned':[r['planned_requests'] for r in matrix['roster']],'remaining':[r['remaining_requests_after_normal_path'] for r in matrix['roster']]})
check('all_musts_preserved',set(x['id'] for x in matrix['must_coverage'])==set(samples['scenarios']) and len(matrix['must_coverage'])==28,
      {'count':len(matrix['must_coverage']),'L05_included':any(r['id']=='Q12' and r['requests']==4 for r in matrix['rows'])})
bad_dependencies=[]
for index,action in enumerate(actions):
    expected_previous=ids[index-1] if index else None
    if action['previous_external_action_commit_required']!=expected_previous:bad_dependencies.append(action['id'])
    for parent in action['parent_commits_required']:
        for ref in re.findall(r'Q\d{2}\.(?:\d{2}\.(?:query|model)|batch\d+|html)',parent):
            if ref not in ids or ids.index(ref)>=index:bad_dependencies.append([action['id'],ref])
check('parent_commit_order',not bad_dependencies,bad_dependencies)
check('exact_approval_and_recovery_contracts',all(a['operator_approval_required'] and a['process_contract']=='EXACT_REQUEST_V2'
      and a['failure_contract']=='ORIGINAL_KEY_STOP_AND_ACCOUNT' and a['status']=='NOT_RUN' for a in actions)
      and matrix['real_completed_requests']==0 and matrix['TESTONLY_deducted_requests']==0,'89动作均引用同一精确批准/GET/显式继续/失败留账合同，无伪造已运行')
fragments=load(OUT/'sample-fragments.json')
check('fragment_static_arithmetic',fragments['total_fragments']==24 and fragments['source_index_calls']==6
      and sum(x['statically_required_fragments'] for x in fragments['sources'])==24
      and fragments['max_item_utf8_bytes']==100 and fragments['any_four_fragment_payload_bytes_upper_bound']==446,
      '逐行规则算术24片/6批；不是产品分片实验或token证明')
cost=load(OUT/'cost-calculation.json')
check('conditional_cost_not_live_quote',cost['actual_applicable_per_request_ceiling'] is None
      and cost['matrix_totals']['conditional_shared_rate_ceiling_microunits']==16373760
      and all(x['below_reservation'] for x in cost['class_formal_comparisons'].values()),
      {'conditional_total':16373760,'live_ceiling':None,'input_tax_token_reasoning':'UNKNOWN，草案关闭'})

draft=load(OUT/'deployment-package.draft.json')
check('drafts_cannot_activate',draft['enabled'] is False and draft['loadable_by_product'] is False
      and draft['actual_grant'] is None and draft['actual_manifest'] is None and draft['actual_binding'] is None
      and draft['actual_operator_approval'] is None and draft['actual_activation_receipt'] is None and draft['T0'] is None
      and draft['price_snapshot_outline']['token_upper_bound_verified'] is False
      and load(OUT/'integration.disabled.draft.json')['enabled'] is False
      and load(OUT/'q-approval.disabled.draft.json')['enabled'] is False
      and load(OUT/'account-attestation.draft.json')['enabled'] is False,'无active grant/instance/approval/receipt/T0；原生配置均disabled')
check('unknown_prerequisites_explicit',load(OUT/'official-facts.json')['live_charge_bound'] is None
      and load(OUT/'readiness-plan.json')['current_checks']['normal_server_readiness']=='UNKNOWN_NOT_STARTED'
      and load(OUT/'decisions-and-blockers.json')['decision_package_count']==1,'官方/账号/loader缺口集中且不影响其余文档完成')

readme_change=load(OUT/'README-change.json')
check('README_before_after',sha(OUT/'README.before.bin')==readme_change['before_sha256']
      and sha(ROOT/'README.md')==readme_change['after_sha256'] and readme_change['replacement_count']==4,
      {'before':readme_change['before_sha256'],'after':readme_change['after_sha256'],'diff':'README.diff'})
all_json=[]
for path in OUT.glob('*.json'):
    load(path);all_json.append(path.name)
check('json_readable',True,all_json)

links=[]
documents=[RESULT,OUT/'operation-runbook.md']
for path in documents:
    body=path.read_text(encoding='utf-8')
    check('markdown_style_'+path.name,'*' not in body and not re.search(r'^\s*\|',body,re.M),'新增Markdown无星号/表格；保留代码/配置原名')
    for target in re.findall(r'\]\(([^)]+)\)',body):
        if target.startswith(('https://','http://')):continue
        links.append((str(path),target))
for line in (OUT/'README.diff').read_text(encoding='utf-8').splitlines():
    if line.startswith('+') and not line.startswith('+++'):
        for target in re.findall(r'\]\(([^)]+)\)',line):
            if not target.startswith(('https://','http://')):links.append((str(ROOT/'README.md'),target))
scheduled={str(OUT/'delivery.json'),str(OUT/'document-consistency.json')}
bad_links=[]
for owner,target in links:
    candidate=Path(target)
    if not candidate.is_absolute():candidate=Path(owner).parent/candidate
    if not candidate.exists() and str(candidate) not in scheduled:bad_links.append([owner,target])
check('local_links_readable',not bad_links,{'checked':len(links),'missing':bad_links,'final_two_outputs':'本命令结束前生成并复读'})

commands=load(OUT/'command-ledger.json')
web=load(OUT/'web-request-ledger.json')
known_wall=sum(Decimal(str(x.get('wall_seconds',0))) for x in commands['commands'])
known_web=sum(Decimal(str(x['wall_seconds'])) for x in web['entries'])
conservative_upper=known_wall+known_web+Decimal('1200')+Decimal('60')
check('tool_and_calendar_limits',conservative_upper<2400
      and START<datetime.fromisoformat('2026-10-22T22:37:01.283336+08:00'),
      {'known_command_wall_seconds':str(known_wall),'known_web_wall_seconds':str(known_web),
       'bootstrap_clock_patch_unmetered_reserve_seconds':1200,'final_check_and_save_reserve_seconds':60,
       'conservative_charge_seconds':str(conservative_upper),'cap_seconds':2400,
       'reserve_is_not_measured_usage':True,'calendar_deadline':'2026-10-22T22:37:01.283336+08:00'})

result={'schema':'retrolume.task122.document-consistency.v1','performed_once':True,'started_at':START.isoformat(),
    'finished_at':datetime.now(timezone.utc).isoformat(),'scope':'文档身份/覆盖/算术/依赖/路径/disabled一致性；非产品测试或独审',
    'passed':all(x['passed'] for x in checks),'checks':checks,'product_verification_performed':False}
(OUT/'document-consistency.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
delivery={'schema':'retrolume.task122.delivery.v1','task':'TASK-122','R':'R-116','prepared_at':datetime.now(timezone.utc).isoformat(),
    'document_consistency_passed':result['passed'],'result_path':str(RESULT),'result_sha256':sha(RESULT),
    'input_identity_rows':len(identity['rows']),'rules_fingerprints_verified':7,'loaded_rule_scope':'公共AGENTS全文、WORK适用task_model/授权/合同/验证段、07；其余锁定规则只核身份，未切阶段',
    'budget':{'tool_wall_cap_seconds':2400,'known_command_wall_seconds':str(known_wall),'known_web_wall_seconds':str(known_web),
        'unknown_wall': '未逐表计时的bootstrap/采钟/补丁/收尾，保守预留1200秒；不伪造实际值',
        'final_command_and_save_reserve_seconds':60,'conservative_charge_seconds':str(conservative_upper),
        'remaining_from_conservative_charge_seconds':str(Decimal(2400)-conservative_upper),
        'holding_product_resource_seconds':0,'human_model_tokens':'unknown'},
    'official_counts':web['counts'],'new_attempt':1,'metadata_lookup_failure_minimum':2,
    'unknown_subcommand_failures':'部分rg隐藏stderr/覆盖子退出；见command-ledger，不冒充全子项成功',
    'product_import_tests_compile_build_PG_Docker_API_browser_model_Git_writes':0,'provider_calls':0,'actual_paid_cost_microunits':0,
    'activation_T0':None,'Q':'FROZEN','historical_control':'FAILED_NOT_RETROACTIVELY_APPROVED',
    'history_retained':load(ROOT/'DocuN/evidence/TASK-122/orchestration-20261021/handoff-facts.json')['old_history_retained'],
    'write_scope':['DocuN/evidence/TASK-122/preparation/','DocuN/results/TASK-122-result.md','README.md four replacements and operator preparation append'],
    'shared_DocuS_and_public_rules_and_original_requirements_written':False,
    'artifacts':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ('delivery.json','command-ledger.json')],
    'mutable_closing_log':{'path':str(OUT/'command-ledger.json'),'reason':'最终核对命令的实际退出由根Agent收到工具回执后追加；不对仍在收尾的日志做自引用hash'},
    'acceptance':'只报告准备交付；TASK/STEP/Q/项目放行归主控'}
(OUT/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for path in (RESULT,OUT/'document-consistency.json',OUT/'delivery.json'):
    data=path.read_bytes()
    if not data:raise RuntimeError('保存后复读为空')
print(json.dumps({'document_consistency_passed':result['passed'],'checks':len(checks),
    'failed':[x for x in checks if not x['passed']], 'result_path':str(RESULT),'result_bytes':RESULT.stat().st_size,
    'result_sha256':sha(RESULT),'conservative_charge_seconds':str(conservative_upper),'Q':'FROZEN'},ensure_ascii=False,indent=2))
sys.exit(0 if result['passed'] else 1)
