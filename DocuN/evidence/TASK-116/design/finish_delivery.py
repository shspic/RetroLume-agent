"""Preserve initial document check; recheck only corrected method names and save/read back artifacts."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

DESIGN=Path(__file__).resolve().parent
ROOT=DESIGN.parents[3]
RESULT=ROOT/'DocuN/results/TASK-116-result.md'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    original=(DESIGN/'consistency.json').read_bytes()
    first_path=DESIGN/'consistency-first.json'
    if first_path.exists():raise ValueError('first check already preserved; do not overwrite')
    first_path.write_bytes(original)
    report=json.loads(original.decode('utf-8'))
    failures=[x for x in report['checks'] if not x['conforming']]
    if len(failures)!=1 or failures[0]['name']!='actual named carriers':raise ValueError('unexpected broader conflict')
    relative='backend/app/interview/service.py'
    raw=(ROOT/relative).read_bytes()
    tree=ast.parse(raw.decode('utf-8-sig'))
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='InterviewService')
    functions={x.name for x in cls.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))}
    if not {'submit_command','read_citation','_frozen'}<=functions:raise ValueError('corrected methods absent')
    identities_path=DESIGN/'source-identities.json'
    identities=json.loads(identities_path.read_text(encoding='utf-8'))
    identity=next(x for x in identities['records'] if x['path']==relative)
    if identity['sha256']!=sha(raw):raise ValueError('source changed; cannot reuse 12 prior checks')
    read_records=[json.loads(x) for x in (DESIGN/'reads.jsonl').read_text(encoding='utf-8').splitlines()]
    late=read_records[-1]
    if late['path']!=relative or late['sha256']!=sha(raw):raise ValueError('targeted actual read missing')
    identity['reads'].append({key:late.get(key) for key in ('utc','mono_ns','mode','match','ranges','purpose')})
    repo_relative='backend/app/activities/interview_repository.py'
    repo_raw=(ROOT/repo_relative).read_bytes()
    repo_identity=next(x for x in identities['records'] if x['path']==repo_relative)
    if repo_identity['sha256']!=sha(repo_raw):raise ValueError('interview repository changed')
    repo_tree=ast.parse(repo_raw.decode('utf-8-sig'))
    repo_cls=next(x for x in repo_tree.body if isinstance(x,ast.ClassDef) and x.name=='InterviewLedgerMethods')
    if not any(isinstance(x,ast.AsyncFunctionDef) and x.name=='_write_interview_outcome' for x in repo_cls.body):
        raise ValueError('actual interview atomic hook absent')
    repo_identity['supplementary_scope'] = repo_identity.get('supplementary_scope','')+'; 定稿rg定义名定向核对并纠正_write_interview_outcome，不运行产品'
    identities_path.write_text(json.dumps(identities,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for x in report['checks']:
        if x['name']=='actual named carriers':
            x.update({'conforming':True,'detail':{'missing':[],'corrected':['InterviewService.submit_command','InterviewService.read_citation','InterviewLedgerMethods._write_interview_outcome'],
                      'method':'one targeted static AST/source readback; 12 unaffected earlier results reused'}})
    report.update({'status':'CONFORMING','full_consistency_runs':1,'targeted_corrections':1,
                   'initial_report_path':first_path.relative_to(ROOT).as_posix(),'initial_report_sha256':sha(original),
                   'correction_utc':datetime.now(timezone.utc).isoformat(),'correction_mono_ns':time.monotonic_ns()})
    # Snapshot changed documents and one metadata appendix, not all product sources.
    for entry in report['artifacts']:
        path=ROOT/entry['path']; saved=path.read_bytes()
        entry.update({'bytes':len(saved),'sha256':sha(saved)})
    (DESIGN/'consistency.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    receipt_path=DESIGN/'receipt.json'
    receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
    ended_utc=datetime.now(timezone.utc);ended_mono=time.monotonic_ns()
    elapsed=(ended_mono-receipt['received_mono_ns_conservative'])/1e9
    if elapsed>=receipt['active_limit_seconds']:raise ValueError('activity limit reached; cannot declare completed')
    receipt.update({'status':'design_completed','saved_utc':ended_utc.isoformat(),'saved_mono_ns':ended_mono,
                    'conservative_active_seconds':elapsed,'remaining_active_seconds':receipt['active_limit_seconds']-elapsed,
                    'full_document_consistency_runs':1,'targeted_document_correction_checks':1,
                    'document_failure_observations':1,'product_runtime_failure_observations':0,
                    'result_sha256':sha(RESULT.read_bytes()),'new_runtime_resources':0})
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    saved=[]
    for path in [RESULT, DESIGN/'integration-contract.md',DESIGN/'acceptance-contract.md',DESIGN/'implementation-card-draft.md',
                 DESIGN/'adoption-package.md',DESIGN/'sample-inputs.json',DESIGN/'sample-identities.json',
                 DESIGN/'actual-call-map.json',identities_path,DESIGN/'consistency.json',first_path,receipt_path]:
        data=path.read_bytes();data.decode('utf-8')
        saved.append({'path':path.relative_to(ROOT).as_posix(),'bytes':len(data),'sha256':sha(data),'readable':True})
    proof={'schema':'TASK116.delivery-readback.v1','utc':datetime.now(timezone.utc).isoformat(),'mono_ns':time.monotonic_ns(),
           'artifacts':saved,'full_consistency_runs':1,'targeted_corrections':1,
           'new_product_runtime_tests_services_network_fees_git_writes':0,'result':'saved_and_readable_design_only'}
    (DESIGN/'delivery.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'result_path':str(RESULT),'result_sha256':sha(RESULT.read_bytes()),'conservative_active_seconds':elapsed,
                      'readable_artifacts':len(saved),'document_consistency':'CONFORMING',
                      'initial_failure_preserved':True,'full_consistency_runs':1,'targeted_corrections':1,
                      'product_runtime':0},ensure_ascii=False))


if __name__=='__main__':main()
