"""One TASK-119 document consistency pass only. No product imports or execution."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
report_path = ROOT / 'DocuN/results/TASK-119-result.md'
read = lambda name: json.loads((OUT / name).read_text(encoding='utf-8'))
matrix, traces, protocol = read('call-matrix.json'), read('hand-traces.json'), read('protocol.json')
ledger, receipt, inputs = read('web-request-ledger.json'), read('execution-receipt.json'), read('input-identities.json')
report = report_path.read_text(encoding='utf-8')
checks = []
def check(name, ok, detail=None):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

check('sections_A_to_D', all(('## ' + letter + '.') in report for letter in 'ABCD'))
check('no_pending_authoring_placeholder', '待下节填入' not in report and '尚在编制' not in report)
check('exactly_four_unexecuted_hand_traces', traces['count'] == len(traces['traces']) == 4 and traces['executed'] is False)
rows = matrix['rows']
calls = sum(x['requests'] for x in rows)
check('row_arithmetic', all(x['requests'] == sum(x[k] for k in ('model_calls','query_calls','index_calls','html_calls')) and x['reserve_microunits'] == x['requests'] * 250000 for x in rows))
check('global_81_calls_and_preserved_caps', calls == matrix['totals']['provider_calls'] == 81 and matrix['totals']['reserve_microunits'] == 20250000 and matrix['totals']['global_request_cap'] == 80 and matrix['totals']['global_reserve_cap_microunits'] == 20000000)
check('roster_39_24_18_and_no_transfer', [sum(x['requests'] for x in rows if x['activity'] == role) for role in ('learning','interview','supplement')] == [39,24,18] and [x['max_requests'] for x in matrix['roster']] == [40,24,16] and [x['max_cost_microunits'] for x in matrix['roster']] == [10000000,6000000,4000000])
check('cost_counterfactual_only', matrix['price_gates']['live_cost_estimate'] is None and matrix['price_gates']['token_byte_upper_bound_verified'] is False and matrix['totals']['conditional_common_rate_token_cost_ceiling_microunits'] == 39 * 194560 + 215040 + 41 * 174080)
check('no_activation_or_DDL', matrix['activation_eligible'] is False and protocol['DDL'] == 0 and protocol['activation'] is None and protocol['new_financial_ledgers'] == 0)
check('network_budget', ledger['search_queries_used'] == 8 and ledger['effective_document_responses'] == 15 and ledger['effective_document_responses'] <= 16 and ledger['document_requests_attempted'] == 22)
current_inputs = []
for item in inputs['inputs']:
    if 'sha256' not in item:
        continue
    path = Path(item['path'])
    raw = path.read_bytes()
    current_inputs.append({'path': str(path), 'bytes': len(raw), 'sha256': sha256(raw).hexdigest(),
                           'matches_first_sample': len(raw) == item['bytes'] and sha256(raw).hexdigest() == item['sha256']})
check('sampled_inputs_unchanged', all(x['matches_first_sample'] for x in current_inputs), {'count': len(current_inputs)})
check('runtime_and_fee_zero', all(x == 0 for x in receipt['runtime_new_counts'].values()))
check('metadata_single_and_cumulative_wall', all(x['wall_seconds'] is not None and x['wall_seconds'] < 60 for x in receipt['commands']) and receipt['metadata_wall_seconds_observed'] + 60 <= 1200)
markdown = [report_path, OUT / 'adoption-package.md']
missing = []
for path in markdown:
    value = path.read_text(encoding='utf-8')
    check('markdown_style_' + path.name, chr(42) not in value and not re.search(r'^\s*\|', value, re.M))
    for target in re.findall(r'\]\(([^)]+)\)', value):
        if re.match(r'^[A-Za-z]:/', target):
            normalized = re.sub(r':\d+$', '', target)
            if normalized.endswith('/document-consistency.json'):
                continue
            if not Path(normalized).exists():
                missing.append(target)
check('local_report_links_exist', not missing, missing)
artifacts = []
for path in sorted(OUT.iterdir()):
    if path.is_file() and path.name not in ('document-consistency.json','execution-receipt.json'):
        raw = path.read_bytes()
        if path.suffix == '.json':
            json.loads(raw.decode('utf-8'))
        artifacts.append({'path': str(path), 'bytes': len(raw), 'sha256': sha256(raw).hexdigest()})
raw = report_path.read_bytes()
artifacts.append({'path': str(report_path), 'bytes': len(raw), 'sha256': sha256(raw).hexdigest()})
result = {'task': 'TASK-119', 'checked_utc': datetime.now(timezone.utc).isoformat(),
          'kind': 'single_document_metadata_consistency_pass_not_product_test', 'checks': checks,
          'passed': all(x['ok'] for x in checks), 'product_runtime_or_tests': 0,
          'current_input_identities': current_inputs, 'artifacts': artifacts,
          'execution_receipt_binding': 'finalized separately after this command; self hashes deliberately excluded'}
(OUT / 'document-consistency.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failed': [x for x in checks if not x['ok']],
                  'result_bytes': len(raw), 'result_sha256': sha256(raw).hexdigest()}, ensure_ascii=False))
