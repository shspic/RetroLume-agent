"""Correct review metadata only, preserving the first saved package verbatim."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,difflib,time,zipfile,shutil
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4];started=time.monotonic()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
b=read(EX/'budget.json');assert b['active_root'] is None and b['active_command'] is None and not b['needs_reconcile']
ident=read(HERE/'final-file-identities.json');prior={r['path']:r['sha256'] for r in read(EX/'continuation-02/adoption.json')['preimages']}
inherited=[];actual_new=[]
for row in ident['new']:
    rel=row['path']
    if rel in prior:
        assert prior[rel]==row['after_sha256']==sha(ROOT/rel)
        inherited.append({'path':rel,'sha256':row['after_sha256'],'source':'continuation-02/adoption.json preimages; unchanged since that preserved snapshot'})
    else:actual_new.append(row)
assert len(inherited)==12 and len(actual_new)==2
folder=HERE/'history/identity-reconciliation';folder.mkdir(parents=True,exist_ok=False)
report=ROOT/'DocuN/results/TASK-120-result.md'
for p in [HERE/'final-file-identities.json',HERE/'fixture.diff',HERE/'candidate-package-identity.json',HERE/'save-consistency.json',HERE/'final-review-index.json',report,EX/'budget.json',EX/'case-index.json']:
    shutil.copy2(p,folder/p.name)
old_archive=HERE/'final-review-candidate.zip';preserved=HERE/'final-review-candidate-before-identity-reconciliation.zip'
assert not preserved.exists() and old_archive.resolve().is_relative_to(ROOT.resolve()) and preserved.resolve().is_relative_to(ROOT.resolve())
first_identity=read(HERE/'candidate-package-identity.json');assert sha(old_archive)==first_identity['sha256']
old_archive.rename(preserved)
ident.update(new=actual_new,inherited_additional_files=inherited,identity_reconciliation='12 unchanged inherited fixtures were initially tagged new because repair03 input list omitted them; hashes match prior preserved C02 preimages. First package and metadata retained.')
write(HERE/'final-file-identities.json',ident)
delta=[]
for row in ident['changed']+actual_new:
    rel=row['path']
    if rel.startswith('backend/app/'):continue
    before=HERE/'preimage'/rel
    delta.extend(difflib.unified_diff(before.read_text(encoding='utf-8-sig').splitlines(True) if before.exists() else [],(ROOT/rel).read_text(encoding='utf-8-sig').splitlines(True),fromfile='before/'+rel if before.exists() else '/dev/null',tofile='after/'+rel))
(HERE/'fixture.diff').write_text(''.join(delta),encoding='utf-8')
old_wall=b['command_wall_conservative_upper_seconds'];old_failures=len(b['failures']);now=datetime.now(timezone.utc)
early=b['repair03_time_intervals'][0]['upper_seconds'];anchor=datetime.fromisoformat(b['repair03_time_intervals'][1]['start'])
active=(now-anchor).total_seconds()+60
original=read(HERE/'prior/budget.json');measured=(b['controlled_command_wall_seconds']-original['controlled_command_wall_seconds'])+(b['runtime_command_wall_seconds']-original['runtime_command_wall_seconds'])
b['repair03_unwrapped_command_wall_upper_seconds']=max(300,early+active-measured)
b['repair03_time_intervals'][1].update(end_with_save_reserve=(now+timedelta(seconds=60)).isoformat(),upper_seconds=active)
b['command_wall_conservative_upper_seconds']=sum(b.get(k,0) for k in ('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds','continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds'))
assert b['command_wall_conservative_upper_seconds']<b['command_wall_cap_seconds']
b['failures'].append({'case':'repair03-saved-review-identity-classification-corrected','classification':'metadata_only','first_package_sha256':first_identity['sha256'],'effect':'12 existing unchanged fixtures corrected from new to inherited; actual new files2. No source/runtime/test/status change. First archive retained verbatim.'})
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'kind':'repair03_review_identity_reconciled','utc':now.isoformat(),'mono_ns':time.monotonic_ns(),'inherited12_not_new':True,'actual_new_files':2,'original_archive_retained':first_identity['sha256'],'real_Q':'FROZEN'})+'\n')
case=read(EX/'case-index.json');case['repair03_failures_entries']=len(b['failures']);write(EX/'case-index.json',case)
raw=report.read_bytes();original_report=(HERE/'prior/TASK-120-result.md').read_bytes();assert raw.endswith(original_report)
prefix=raw[:-len(original_report)].decode('utf-8')
prefix=prefix.replace(f'当前 **{old_failures}条失败/诊断记录**',f'当前 **{len(b["failures"])}条失败/诊断记录**').replace(f'{old_wall:.6f}/{b["command_wall_cap_seconds"]}秒',f'{b["command_wall_conservative_upper_seconds"]:.6f}/{b["command_wall_cap_seconds"]}秒')
prefix+='保存后身份更正：12个沿用且字节未变的夹具已从“新增”归回继承；实际新增源码/测试文件2个。首版包及原身份清单完整保留，修正不改变任何运行成败。\n\n'
report.write_bytes(prefix.encode()+original_report)
preservation=read(HERE/'result-preservation.json');preservation['new_report_sha256']=sha(report);write(HERE/'result-preservation.json',preservation)
index=read(HERE/'final-review-index.json');index['identity_reconciliation']={'inherited_unchanged':12,'actual_new_files':2,'first_package_preserved':preserved.name,'first_package_sha256':first_identity['sha256']};write(HERE/'final-review-index.json',index)
write(HERE/'identity-reconciliation.json',{'inherited':inherited,'actual_new_files':[r['path'] for r in actual_new],'first_archive_sha256':sha(preserved),'source_runtime_and_test_outcomes_unchanged':True})
old_zips={ROOT/r['path']:r['sha256'] for r in index['old_packages_unchanged']}
for p,h in old_zips.items():assert sha(p)==h
pack={report,EX/'budget.json',EX/'events.jsonl',EX/'case-index.json',EX/'remaining-readiness.json',EX/'final-bundle-identities.json',*old_zips}
for row in ident['changed']+actual_new:pack.add(ROOT/row['path'])
for p in HERE.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.zip','.pyc') and p.name not in ('candidate-package-identity.json','save-consistency.json'):pack.add(p)
for number in (17,18,19,20):pack.update(p for p in EX.glob(f'root-{number:02d}*') if p.is_file())
for name in ('budget-02-creation-memory-proof.json','budget-02-selected-memory-binding.json','budget-02-bootstrap.json','budget-02-source-identities.json','budget-02-q-binding.json'):
    if (EX/name).exists():pack.add(EX/name)
with zipfile.ZipFile(old_archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for p in sorted(pack):
        if time.monotonic()-started>55:raise RuntimeError('bounded_metadata_save_limit')
        rel=p.relative_to(ROOT).as_posix();assert not rel.startswith(('.runtime/','.git/'));z.write(p,rel)
with zipfile.ZipFile(old_archive) as z:assert z.testzip() is None
identity=dict(first_identity,path=old_archive.relative_to(ROOT).as_posix(),bytes=old_archive.stat().st_size,sha256=sha(old_archive),files=len(pack),first_saved_archive_preserved_sha256=sha(preserved))
write(HERE/'candidate-package-identity.json',identity)
consistency=read(folder/'save-consistency.json');consistency.update(utc=datetime.now(timezone.utc).isoformat(),final_report_sha256=sha(report),failures_entries=len(b['failures']),command_wall_upper_seconds=b['command_wall_conservative_upper_seconds'],identity_reconciled=True,actual_new_files=2,inherited_unchanged_fixtures=12,first_archive_preserved=True,filesystem_finalize_seconds=time.monotonic()-started)
assert time.monotonic()-started<60;write(HERE/'save-consistency.json',consistency)
print(json.dumps({'final_archive':identity,'actual_new_files':2,'inherited_unchanged_fixtures':12,'failures_retained':len(b['failures']),'command_wall_upper':b['command_wall_conservative_upper_seconds'],'engineering_complete':False}))
