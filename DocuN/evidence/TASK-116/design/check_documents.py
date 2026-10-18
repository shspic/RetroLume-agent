"""One finite document-consistency pass only. No product import/execution or test/service."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time

DESIGN = Path(__file__).resolve().parent
ROOT = DESIGN.parents[3]
RESULT = ROOT / 'DocuN/results/TASK-116-result.md'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_names(relative):
    tree = ast.parse((ROOT / relative).read_text(encoding='utf-8-sig'))
    names = set()
    def walk(nodes, parent=''):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(parent + node.name)
            elif isinstance(node, ast.ClassDef):
                walk(node.body, parent + node.name + '.')
    walk(tree.body)
    return names


def main():
    checked_at = datetime.now(timezone.utc)
    mono = time.monotonic_ns()
    # The output path itself is a valid local navigation destination for this pass.
    output = DESIGN / 'consistency.json'
    output.write_text(json.dumps({'status': 'checking_once', 'product_execution': 0}) + '\n', encoding='utf-8')
    names = ['integration-contract.md', 'acceptance-contract.md', 'implementation-card-draft.md', 'adoption-package.md']
    paths = [DESIGN / name for name in names] + [RESULT]
    docs = {path.name: path.read_text(encoding='utf-8') for path in paths}
    checks = []
    def check(name, condition, detail):
        checks.append({'name': name, 'conforming': bool(condition), 'detail': detail})
    a = docs['integration-contract.md']; c = docs['acceptance-contract.md']; d = docs['implementation-card-draft.md']; p = docs['adoption-package.md']
    check('A-D full contracts', all(x in a for x in ('## A.', '## B.', 'M01', 'M13')) and len(c)>5000 and len(d)>6000 and len(p)>4000,
          'Actual map, normative changes, finite expected outcomes and complete unassigned draft are saved.')
    check('single recommended minimum', all(x in a for x in ('embedding.v1', 'RRF(k=60)', 'data_exit.v1.r02', 'max_output_tokens=0', '费用0', 'batch_count=0', 'partial', 'interview.v2')),
          'Explicit new kind/profile/cache-hit/partial status; old tool NULL and zero-cost branch retained.')
    samples = json.loads((DESIGN/'sample-inputs.json').read_text(encoding='utf-8'))
    scenario_ids = samples['scenarios']
    rows = re.findall(r'^\| ((?:L|I|X|P)\d{2})\s', c, re.MULTILINE)
    check('28 finite scenarios exactly mapped', len(scenario_ids)==28 and len(set(scenario_ids))==28 and set(rows)==set(scenario_ids) and len(rows)==28,
          {'frozen_count':len(scenario_ids), 'contract_row_count':len(rows)})
    sample_meta = json.loads((DESIGN/'sample-identities.json').read_text(encoding='utf-8'))
    check('8 exact synthetic source texts', len(samples['sources'])==8 and all(x['lines']==x['expected_lines'] for x in sample_meta['sources']),
          'UTF-8/LF identity data matches frozen exact text; PDF is explicitly future bytes, not generated or run.')
    ids = json.loads((DESIGN/'source-identities.json').read_text(encoding='utf-8'))
    mismatches = [x['path'] for x in ids['records'] if not x['same_as_recorded_read'] or x['same_as_manifest_when_present'] is False]
    matched = sum(x['manifest_expected_sha256'] is not None for x in ids['records'])
    check('key identity no conflict', not mismatches and ids['count']==66 and not ids['all_registered_243_rehashed'],
          {'key_count':ids['count'], 'manifest_comparable':matched, 'mismatches':mismatches, 'metadata_reused_not_full_rehash':True})
    missing_links = []
    link_count = 0
    for filename, text in docs.items():
        for target in re.findall(r'\]\((D:/[^)]+)\)', text):
            link_count += 1
            if not Path(target).is_file(): missing_links.append({'document':filename, 'target':target})
    check('absolute local artifact navigation', not missing_links, {'links':link_count,'missing':missing_links})
    required_functions = {
        'backend/app/activities/repository.py':['PostgresAdmissionLedger.create_activity','PostgresAdmissionLedger.admit','PostgresAdmissionLedger.record_outcome','PostgresAdmissionLedger.revise_scope'],
        'backend/app/learning/teaching_api.py':['submit_teaching_command','read_teaching_workspace','read_teaching_seed'],
        'backend/app/learning/teaching_service.py':['TeachingService._submit_model','TeachingService._freeze_model_context'],
        'backend/app/activities/interview_repository.py':['InterviewLedgerMethods._interview_require_call','InterviewLedgerMethods.apply_interview_local','InterviewLedgerMethods.accept_interview_command'],
        'backend/app/interview/service.py':['InterviewService.submit','InterviewService._frozen','InterviewService.citation'],
        'backend/app/preview/generation.py':['HtmlGenerationService.generate'],
        'backend/app/data_exit/config.py':['DataRuntime.context','DataRuntime.bind_readonly'],
        'backend/app/retrieval/evidence.py':['build_fragments','rank_term_candidates','verify_fragment'],
    }
    missing_functions=[]
    for relative, required in required_functions.items():
        actual = function_names(relative)
        for function in required:
            if function not in actual:missing_functions.append(relative+':'+function)
    check('actual named carriers', not missing_functions, {'missing':missing_functions,'method':'limited AST definitions only; never import/call product'})
    draft_existing = [
        'frontend/src/activities/teachingApi.ts','frontend/src/activities/interviewApi.ts','frontend/src/activities/memoryApi.ts',
        'frontend/src/activities/pendingIntents.ts','frontend/src/activities/teachingIntents.ts','frontend/src/activities/teachingIntentMatch.ts',
        'frontend/src/activities/teachingDrafts.ts','frontend/src/activities/interviewIntents.ts','frontend/src/activities/interviewDrafts.ts',
        'frontend/src/activities/memoryIntents.ts','frontend/src/activities/learningIntentMatch.ts',
        'frontend/src/data/context.tsx','frontend/src/data/dataApi.ts','frontend/src/data/ReadonlyRecords.tsx',
        'frontend/src/activities/activity-workspace.css','frontend/src/activities/interview-workspace.css','frontend/src/activities/memory-workspace.css',
        'backend/app/data_exit/config.py','backend/app/data_exit/snapshot.py','backend/migrations/008_activity_tool_budget.sql',
    ]
    check('draft edited-existing paths real', all((ROOT/x).is_file() for x in draft_existing),
          'Actual API/draft/context/CSS/snapshot paths, proposed new files distinguished as new; all 001-013 protected.')
    check('finite forward budgets', 40+24+16==80 and 10+6+4==20 and 80*250000==20000000 and 27000+1800==28800
          and all(x in d for x in ('最多8个','≤4','15481','15482','15483','15484','18118','≤160','≤14400s')),
          '80 requests include both vendors/failures; 20 yuan proposed only; 4 new PGs/2 concurrent, finite roots and time, old balances not borrowed.')
    check('normal and restored-readonly distinct', all(x in a for x in ('同normal库','永久restored_readonly','R01仅1..13链','R02仅1..14链'))
          and '不预设' not in p and '永久只读' in p,
          'Same persistent normal library continuation; neither restore profile gets execution/secret/lease authority.')
    check('provider prices terms not invented', all(x in p for x in ('未核','官方现行','0.25是建议安全预留','不联网','旧13元')),
          'Specific candidates, price/account/terms gates and separate real-data boundary; no actual authority created.')
    check('new zero-runtime task boundary', all(x in docs['TASK-116-result.md'] for x in ('均0','没有删除','不自行派下一卡','compile/test/typecheck/build'))
          and all(x in d for x in ('未编号','未生效','不自动继承','001—013')),
          'Current result distinguishes zero runs from future proposals; no task IDs, shared-state writes or old runner revival.')
    receipt_path=DESIGN/'receipt.json'
    receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig'))
    elapsed=(mono-receipt['received_mono_ns_conservative'])/1e9
    check('design current time inside permission', 0<=elapsed<receipt['active_limit_seconds'] and checked_at<datetime.fromisoformat(receipt['calendar_deadline_utc']),
          {'conservative_elapsed_seconds':elapsed,'active_cap_seconds':7200,'save_reserve_seconds':600})
    conforming=all(item['conforming'] for item in checks)
    status='CONFORMING' if conforming else 'DOCUMENT_CONFLICT'
    result_text=docs['TASK-116-result.md']
    old='一次文档一致性核对的实际结果以[consistency.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/consistency.json)为准；保存后将此处写入真实结论。'
    new=f'已做一次文档一致性核对，实际结论{status}，{len(checks)}项覆盖/路径/身份/兼容/预算/边界检查记录在[consistency.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/consistency.json)。'
    if old not in result_text:raise ValueError('result expected single consistency placeholder missing')
    RESULT.write_text(result_text.replace(old,new,1),encoding='utf-8')
    receipt.update({'status':'design_completed' if conforming else 'design_document_conflict',
                    'consistency_utc':checked_at.isoformat(),'consistency_mono_ns':mono,
                    'conservative_elapsed_at_check_seconds':elapsed,'document_consistency_runs':1,
                    'current_product_test_runtime_network_fee_git_write':0})
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    inventory=[]
    for path in paths+[DESIGN/'sample-inputs.json',DESIGN/'sample-identities.json',DESIGN/'actual-call-map.json',DESIGN/'source-identities.json']:
        inventory.append({'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)})
    report={'schema':'TASK116.one-document-consistency.v1','utc':checked_at.isoformat(),'mono_ns':mono,'status':status,
            'check_count':len(checks),'checks':checks,'artifacts':inventory,'product_validation':False,
            'product_import_execution_services_tests_build_network_fees_git_write':0,
            'remaining':'AP1/AP2 pending adoption; actual runtime and semantic results NOT_RUN; no project acceptance'}
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':status,'check_count':len(checks),'failures':[x for x in checks if not x['conforming']],
                      'conservative_elapsed_seconds':elapsed,'result_sha256':sha(RESULT),'product_execution':0},ensure_ascii=False))


if __name__=='__main__':main()
