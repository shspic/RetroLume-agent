"""仅冻结本执行者的文件/原件/报告索引；不连接业务或改共享文档。"""
import difflib
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task100.control import EVIDENCE,Ledger,atomic_json,hash_files,effective_limits,utc
from tests.fixtures.task100.runner import source_paths

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

ledger=Ledger().checkpoint_active()
for name in ('final-file-identity.json','verification-index.json','evidence-inventory.json'):
    backup=EVIDENCE/(Path(name).stem+'-before-final-20261005.json')
    if not backup.exists():backup.write_bytes((EVIDENCE/name).read_bytes())
previous=read(EVIDENCE/'final-file-identity-before-final-20261005.json')
prep=read(EVIDENCE/'preparation.json')
files=hash_files(source_paths())
offline='2026-10-05T042236.572512-0000-offline'
assert read(EVIDENCE/offline/'summary.json')['tests']==58
assert read(EVIDENCE/offline/'summary.json')['status']=='pass'
assert files==read(EVIDENCE/offline/'as-run-files.json')
build=[e['detail'] for e in ledger['events'] if e.get('event')=='frontend_build_pass'][-1]
assert all(files.get(p)==h for p,h in build['files'].items() if p.startswith('frontend/src/') or p=='frontend/package.json')
dist=hash_files(list((ROOT/'frontend/dist').rglob('*')))
assert dist==build['dist']
archive=ROOT/'DocuN/evidence/root-archive-20261005'
external={r['path']:r for r in read(archive/'changes.json')}
rule_checks=[]
for item in prep['rule_checks']:
    fact={'path':item['path'],'expected_sha256':item['expected'],'final_sha256':sha(item['path'])}
    assert fact['expected_sha256']==fact['final_sha256'];rule_checks.append(fact)

changes=[];patch=[];pre_paths={r['path'] for r in prep['pre_files']}
post=EVIDENCE/'final-post-20261005'
for path,digest in files.items():
    old=EVIDENCE/'pre'/path
    before=old.read_bytes() if old.is_file() else None
    current=(ROOT/path).read_bytes()
    own=current
    if path=='README.md':own=(archive/'before/README.md').read_bytes()
    kind='modified' if before is not None and before!=own else 'added' if before is None and path not in previous['existing_files_without_pre_copy'] else None
    if kind:
        record={'path':path,'kind':kind,'before_sha256':hashlib.sha256(before).hexdigest() if before is not None else None,
            'own_after_sha256':hashlib.sha256(own).hexdigest(),'final_sha256':digest}
        if path=='README.md':record['external_increment']='root-archive-20261005/diffs/README.md.diff'
        changes.append(record)
        target=post/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(current)
        patch.extend(difflib.unified_diff((before or b'').decode('utf-8').splitlines(True),own.decode('utf-8').splitlines(True),
            fromfile='pre/'+path,tofile='final-own/'+path))
(EVIDENCE/'diff-from-pre-final-20261005.patch').write_text(''.join(patch),encoding='utf-8')

protected=[]
for prior in previous['protected_checks']:
    path=prior['path'];target=ROOT/path;resolved=target
    if not target.exists() and path.split('/')[0] in ('Ndocu','docu','evidence','spikes'):
        resolved=ROOT/'DocuN/archives/legacy-roots-20261005'/path
    current=sha(resolved) if resolved.is_file() else None
    kind='unchanged' if current==prior['before_sha256'] else 'own_result_prefix' if path=='DocuN/results/TASK-100-result.md' else (
        'external_authorized_archive' if path in external and external[path]['after_sha256']==current else 'changed_requires_attribution')
    protected.append({'path':path,'resolved_path':str(resolved),'before_sha256':prior['before_sha256'],'final_sha256':current,'classification':kind})

def methods(raw):
    text=raw.read_text(encoding='utf-8')
    matches=list(re.finditer(r'^test_\w+ \((tests\.[^)]+)\)',text,re.M))
    result=[]
    for i,m in enumerate(matches):
        block=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
        status=re.search(r'\.\.\. (ok|FAIL|ERROR|skipped[^\n]*)',block)
        if status:result.append({'method':m.group(1),'status':status[1],'batch':raw.parents[1].name,
            'raw':str(raw.relative_to(EVIDENCE)).replace('\\','/')})
    return result

pg={};http={};failures=[];batches=[]
for batch in sorted(EVIDENCE.glob('*main-combo')):
    summary=read(batch/'summary.json');assert summary['status']=='fail'
    batches.append({'id':batch.name,'status':summary['status'],'raw':batch.name+'/summary.json','segments':summary['segments']})
    for category,destination in (('repository-raw',pg),('http-raw',http)):
        raw=batch/category/'stderr.txt'
        if raw.exists():
            for item in methods(raw):
                if item['status']=='ok':destination[item['method']]=item
                else:failures.append(item)
refusal=read(EVIDENCE/'fifth-entry-evidence-location.json')['directory']
batches.append({'id':refusal,'status':'fail','reason':'README concurrent archive navigation preflight','raw':refusal+'/result.json','resources_started':False})
batches.sort(key=lambda b:b['id'])
assert len(pg)==29 and len(http)==4 and len(batches)==6
wbatch=EVIDENCE/'2026-10-05T033911.225278-0000-main-combo'
w=read(wbatch/'windows-facts.json')
outcomes=[read(p)['value'] for p in (wbatch/'observations').glob('*session_outcome.json')]
assert len(outcomes)==21 and all(o['active_processes_at_end']==0 and o['cleanup_incomplete'] is False for o in outcomes)
observation_counts=Counter(read(p)['kind'] for p in (wbatch/'observations').glob('*.json'))
atomic_json(EVIDENCE/'process-observation-binding.json',{'at':utc(),'windows_matrix_outcomes':17,'all_actual_outcomes':21,
    'observation_counts':dict(observation_counts),'session_outcomes':outcomes,'per_process_module_content_hash':'not_captured',
    'as_run_binding':wbatch.name+'/as-run-files.json','final_products_match_as_run':all(files[p]==h for p,h in read(wbatch/'as-run-files.json').items() if p.startswith('backend/app/'))})
browser=read(EVIDENCE/'browser-final-artifact-verification.json')
assert browser['status']=='pass' and len(browser['actual_controls_passed'])==10
last='2026-10-05T041623.670843-0000-main-combo'
legacy=read(EVIDENCE/last/'migration-legacy-compatibility.json');assert legacy['status']=='pass'
last_files=read(EVIDENCE/last/'as-run-files.json')
since_last=[p for p in set(files)|set(last_files) if files.get(p)!=last_files.get(p)]
assert set(since_last)=={'frontend/tests/task100-browser.cjs','backend/tests/fixtures/task100/runner.py','backend/tests/fixtures/task100/browser_artifacts.py'}
identity={'at':utc(),'source_files':files,'changes':changes,'protected_checks':protected,'rule_checks':rule_checks,
    'last_real_batch':last,'since_last_real_changed':sorted(since_last),'products_changed_since_last_real':False,
    'final_offline_batch':offline,'final_offline_exact_files_match':True,'frontend_build_batch':previous['frontend_build_batch'],
    'frontend_source_exact_build_match':True,'frontend_dist_exact_build_match':True,'dist':dist,
    '009_raw_sha256':files['backend/migrations/009_teaching.sql'],'009_executed_utf8_lf_sha256':legacy['009_executed_utf8_lf_sha256'],
    'full_chain_status':'bounded_functional_evidence_available; raw_batches_fail; limits_explicit','windows':'17-window pass plus 4 real reopened windows',
    'browser':'main pass; 10 required controls pass; zero-fee correction and saved DOM verified; final script rerun not_run',
    'provider_real':'not_run','independent_audit':'not_run','per_process_as_loaded_hash':'not_captured',
    'existing_files_without_pre_copy':previous['existing_files_without_pre_copy'],
    'diff_scope_note':'Only own code/fixture changes and own teaching README text; concurrent authorized archive delta separately attributed.',
    'result_history_identity':'result-history-identity-final-20261005.json',
    'final_resource_check':'final-read-only-resource-check-20261005.json'}
atomic_json(EVIDENCE/'final-file-identity.json',identity)
old_index=read(EVIDENCE/'verification-index-before-final-20261005.json')
index={'at':utc(),'full_chain_status':identity['full_chain_status'],'all_raw_batch_statuses':'fail; never rewritten',
    'pg_distinct_passed_methods':sorted(pg.values(),key=lambda x:x['method']),'http_methods':sorted(http.values(),key=lambda x:x['method']),
    'failures_preserved':failures,'batches':batches,'offline':{'batch':offline,'tests':58,'skipped':0,'status':'pass'},
    'build':old_index['build'],'windows':{'status':'pass','matrix_cases':w['cases'],'matrix_outcomes':17,'all_observed_outcomes':21,
        'raw':wbatch.name+'/windows-facts.json','additional_binding':'process-observation-binding.json'},
    'browser':{'main':{'status':'pass','raw':wbatch.name+'/browser-main/facts.json'},
        'reopen_raw_status':'fail at later storage locator; preceding three-type/response-loss assertions reached',
        'reopen_raw':wbatch.name+'/browser-reopen/facts.json','controls':browser['actual_controls_passed'],
        'actual_correction':browser['actual_local_correction_receipt'],'saved_artifacts':'browser-final-artifact-verification.json',
        'corrected_script_dynamic_rerun':'not_run','window_global_probe':'not_run'},
    'migration':old_index['migration']|{'additional_legacy_compatibility':last+'/migration-legacy-compatibility.json',
        'coverage_limit':'Old model/tool bodies, unknown and received without body coexist unchanged; full old G7/plain workflows not newly run.'},
    'original_limits':ledger['limits'],'effective_limits':effective_limits(ledger),'counts':ledger['counts'],'seconds':ledger['seconds'],
    'permits':['supplementary-permit-20261005.json','browser-supplementary-permit-20261005.json','preflight-supplementary-permit-20261005.json'],
    'not_run':['real provider quality','independent audit','corrected whole browser script rerun','window-global probe'],
    'not_captured':['per-process as-loaded module content hashes','individual Chromium descendant PID creation times'],
    'final_resource_check':'final-read-only-resource-check-20261005.json'}
atomic_json(EVIDENCE/'verification-index.json',index)

report=ROOT/'DocuN/results/TASK-100-result.md'
raw=report.read_bytes();old_identity=read(EVIDENCE/'result-history-identity.json')
history=raw[-old_identity['before_bytes']:]
assert hashlib.sha256(history).hexdigest()==old_identity['before_sha256']
backup=EVIDENCE/'result-before-final-20261005.md'
if not backup.exists():backup.write_bytes(raw)
prefix=(EVIDENCE/'result-prefix-final-20261005.md').read_bytes()
report.write_bytes(prefix+history)
after=report.read_bytes();after.decode('utf-8')
assert after.endswith(history)
atomic_json(EVIDENCE/'result-history-identity-final-20261005.json',{'at':utc(),'path':str(report),'history_bytes':len(history),
    'history_sha256':hashlib.sha256(history).hexdigest(),'original_history_bytes_preserved':True,
    'previous_own_report':'result-before-final-20261005.md','final_bytes':len(after),'final_sha256':sha(report),'readable_utf8':True})
print(json.dumps({'saved_report':str(report),'source_files':len(files),'own_changes':dict(Counter(c['kind'] for c in changes)),
    'pg_distinct_passed':len(pg),'http_distinct_passed':len(http),'browser_controls_passed':10,
    'protected_classifications':dict(Counter(p['classification'] for p in protected)),
    'counts':ledger['counts'],'seconds':ledger['seconds'],'original_result_history_preserved':True}))
