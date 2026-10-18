"""Finalize the authorized result; old result bytes and all attempts are preserved."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task100.control import EVIDENCE,Ledger,atomic_json,hash_files,utc
from tests.fixtures.task100.runner import source_paths
load=lambda p:json.loads(Path(p).read_text('utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

begun=time.monotonic()
ledger=Ledger()
prep=load(EVIDENCE/'preparation.json')
identity=load(EVIDENCE/'final-identity.json')
assert hash_files(source_paths())=={p:h for p,h in identity['as_run_runtime_scope'].items() if not p.startswith('frontend/dist/')}
for p,h in identity['post_files'].items():assert sha(ROOT/p)==h
for row in identity['baseline_input_objects']:
    actual=sha(row['path']) if Path(row['path']).is_file() else None
    assert actual==row['post']
assert load(EVIDENCE/'final-resource-read.json')['status']=='pass'
assert load(EVIDENCE/'2026-10-05T110007.993696-0000-readonly-browser-combo/summary.json')['status']=='pass'
assert ledger.load()['counts']=={'real_entries':4,'container_starts':4,'app_starts':3,'sup_creates':12,'browser':2,'driver':2,'frontend_build':2}

# Batch construction creates a temporary path before the worker adopts the
# controller's batch-dir. Annotate those existing scaffolds; do not delete them
# or miscount directory names as additional runtime entries.
for directory in EVIDENCE.iterdir():
    if directory.is_dir() and directory.name.endswith('-repair-combo') and not any(directory.iterdir()):
        atomic_json(directory/'directory-ownership-note.json',{'kind':'unused_worker_constructor_evidence_path',
            'reason':'RepairBatch constructor then adopts controller --batch-dir; resource and counter facts are in the four actual controller batches',
            'new_independent_entry':False,'business_runs_recorded_here':0})

report=ROOT/'DocuN/results/TASK-100-result.md'
old=(EVIDENCE/'TASK-100-result-before.md').read_bytes()
assert len(old)==prep['old_result_bytes']
assert hashlib.sha256(old).hexdigest()==prep['old_result_sha256']
assert report.read_bytes()==old, 'result changed since pre; do not overwrite another writer'
template=(EVIDENCE/'result-header.md').read_text('utf-8')

# Only report/index work since the last metered offline action, no resources.
ledger.charge('offline',time.monotonic()-begun,{'mode':'final_identity_readability_preparation_no_business_resources'})
frozen=ledger.checkpoint_active()
values={f'{name.upper()}_SECONDS':frozen['seconds'][name] for name in ('offline','real','cleanup','active')}
values.update(OLD_RESULT_BYTES=len(old),OLD_RESULT_SHA256=hashlib.sha256(old).hexdigest())
for key,value in values.items():
    template=template.replace('{{'+key+'}}',f'{value:.3f}' if isinstance(value,float) else str(value))
assert '{{' not in template
header=template.encode('utf-8')
content=header+old
temporary=report.with_name('TASK-100-result.audit-repair-03.tmp')
assert not temporary.exists()
temporary.write_bytes(content);temporary.replace(report)
(EVIDENCE/'result-header.md').write_bytes(header)
assert report.read_bytes()[len(header):]==old

freeze={'at':utc(),'permit':frozen['permit'],'delivery_status':'candidate_complete_independent_101_review_pending',
    'counts':frozen['counts'],'limits':frozen['limits'],'seconds_at_freeze':frozen['seconds'],'time_limits':frozen['time_limits'],
    'old_usage':frozen['old_usage'],'old_result_bytes':len(old),'old_result_sha256':values['OLD_RESULT_SHA256'],
    'old_result_exact_suffix_preserved':True,'report':str(report),'report_bytes':len(content),'report_sha256':sha(report),
    'source_dist_post_manifest_sha256':sha(EVIDENCE/'post/manifest.json'),'final_identity_sha256':sha(EVIDENCE/'final-identity.json'),
    'final_source_runtime_objects':len(identity['as_run_runtime_scope']),'complete_post_objects':len(identity['post_files']),
    'final_backend_matches_actual_PG_HTTP_windows':True,'final_dist_consumed_by_browser':True,
    'resource_read_status':'pass','resource_read_sha256':sha(EVIDENCE/'final-resource-read.json'),
    'new_resource_permission_after_delivery':False,'independent_audit_signed_here':False,'G8_STEP_M1_provider_deployment_project_pass_signed':False,
    'timing_basis':'fixed monotonic, initial conservative 120 seconds; quoted values are this exact freeze checkpoint'}
atomic_json(EVIDENCE/'final-freeze-and-usage.json',freeze)
atomic_json(EVIDENCE/'delivery-readability.json',{'status':'checking'})
checked=[]
for path in (report,EVIDENCE/'evidence-applicability.md',EVIDENCE/'method-bindings-final.md'):
    text=path.read_text('utf-8')
    # Only the new report prefix is this card's maintained navigation. Old report
    # links remain byte-exact and obey AGENTS legacy-root mapping.
    if path==report:text=text[:len(template)]
    for target in re.findall(r'\]\(([^)\n]+)\)',text):
        target=target.strip('<>')
        if re.match(r'^[A-Za-z]:/',target):
            exists=Path(target).is_file();checked.append({'document':str(path),'target':target,'readable_file':exists})
            assert exists, 'missing new delivery link: '+target
assert report.read_bytes().endswith(old)
atomic_json(EVIDENCE/'delivery-readability.json',{'at':utc(),'status':'pass','result_sha256':sha(report),
    'old_result_exact_suffix_preserved':True,'checked_new_links':checked,'old_link_policy':'original bytes; AGENTS legacy root prefix mapping',
    'post_files_hash_verified':len(identity['post_files']),'rules_and_protected_input_reverified':True})
ledger.note('permit_ended',{'reason':'candidate_delivered_and_exact_owned_resources_stopped',
    'report_sha256':sha(report),'new_resource_attempts_authorized':False,'freeze_usage':str(EVIDENCE/'final-freeze-and-usage.json')})
freeze['ledger_sha256_after_permit_end_note']=sha(EVIDENCE/'attempt-ledger.json')
atomic_json(EVIDENCE/'final-freeze-and-usage.json',freeze)
index={}
for path in EVIDENCE.rglob('*'):
    if path.is_file() and path.name not in ('evidence-file-index.json','attempt-ledger.lock'):
        index[path.relative_to(EVIDENCE).as_posix()]={'sha256':sha(path),'bytes':path.stat().st_size}
atomic_json(EVIDENCE/'evidence-file-index.json',{'at':utc(),'files':index,'self_hash_excluded':True,'lock_file_excluded':True})
print(json.dumps({'status':'pass','report':str(report),'report_bytes':len(content),'old_bytes_preserved':len(old),
    'new_links_verified':len(checked),'evidence_files_indexed':len(index),'counts':frozen['counts'],'seconds_at_freeze':frozen['seconds'],
    'artifact_pack_tail_elapsed_after_freeze_seconds':time.monotonic()-begun},ensure_ascii=True))
