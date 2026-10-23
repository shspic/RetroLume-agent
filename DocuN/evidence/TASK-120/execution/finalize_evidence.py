"""Read-only product inventory and exact review copies. No runtime or Git."""
from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=raw:raise RuntimeError('existing_final_evidence_differs_'+path.name)
    else:path.write_bytes(raw)
def jsave(path,value):save(path,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

baseline=read(OUT.parent/'orchestration-20261018/product-baseline.json')
original={x['relative_path'].replace('\\','/'):x for x in baseline['files']}
first=read(OUT/'baseline-check.json')
if first['mismatches']:raise RuntimeError('initial_baseline_drift')
rows=[];changed=[];unexpected=[];patch=[];post=[]
for name,old in original.items():
    current=ROOT/name;raw=current.read_bytes() if current.is_file() else None
    actual=sha(raw) if raw is not None else None
    pre=OUT/'preimage'/name
    if pre.is_file() and sha(pre.read_bytes())!=old.get('sha256'):raise RuntimeError('preimage_integrity_'+name)
    row={'path':name,'before_sha256':old.get('sha256'),'after_sha256':actual,'changed':actual!=old.get('sha256'),
         'preimage':pre.relative_to(OUT).as_posix() if pre.is_file() else None}
    rows.append(row)
    if not row['changed']:continue
    changed.append(row)
    if not pre.is_file() and not name.startswith('frontend/dist/'):unexpected.append(name)
    if raw is not None:post.append((name,raw))
    if pre.is_file() and raw is not None:
        patch.extend(difflib.unified_diff(pre.read_text(encoding='utf-8-sig').splitlines(True),raw.decode('utf-8-sig').splitlines(True),fromfile='before/'+name,tofile='after/'+name))

new=[]
candidates=[]
for folder,glob in (('backend/app/capabilities','q_*.py'),('backend/app/data_exit','q_*.py'),('backend/app/operator','*.py'),
    ('backend/tests/fixtures/task120','*.py'),('backend/tests','test_task120_*.py'),('frontend/tests','task120-*.mjs')):
    candidates.extend((ROOT/folder).glob(glob))
candidates.extend((ROOT/'config/q-approval.example.json',ROOT/'deploy/q-approval.md'))
candidates.extend(p for p in (ROOT/'frontend/dist').rglob('*') if p.is_file())
for path in sorted(set(candidates)):
    name=path.relative_to(ROOT).as_posix()
    if name in original:continue
    raw=path.read_bytes();new.append({'path':name,'before_sha256':None,'after_sha256':sha(raw),'bytes':len(raw)})
    post.append((name,raw))
    if not name.startswith('frontend/dist/'):
        patch.extend(difflib.unified_diff([],raw.decode('utf-8-sig').splitlines(True),fromfile='/dev/null',tofile='after/'+name))
if unexpected:raise RuntimeError('unexplained_baseline_drift_'+repr(unexpected))
for name,raw in post:save(OUT/'postimage'/name,raw)
jsave(OUT/'final-file-identities.json',{'baseline_count':len(rows),'initial_preimage_count':sum(x['preimage'] for x in first['files']),
    'existing_files':rows,'changed_existing':changed,'new_files':new,'unexplained_drift':unexpected,
    'old_dist_content_captured':False,'old_dist_limit':'Old build has baseline hashes only; original editable source preimages are byte-exact.',
    'runtime_verification_status':'PARTIAL; final source and build identities do not imply final browser or PG matrix PASS'})
save(OUT/'source.diff',''.join(patch).encode('utf-8'))

rules=[]
for item in read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    path=Path(item['absolute_path']);actual=sha(path.read_bytes())
    rules.append({'path':str(path),'expected_sha256':item['sha256'],'actual_sha256':actual,'matches':actual==item['sha256']})
jsave(OUT/'final-rules-check.json',{'rules':rules,'all_match':all(x['matches'] for x in rules)})
assets=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted((ROOT/'frontend/dist').rglob('*')) if p.is_file()]
jsave(OUT/'final-bundle-identities.json',{'build_receipt':'command-027.receipt.json','assets':assets,'browser_starts':0,
    'actual_JS_CSS_HTTP_response_hash_verified':False,'status':'FORMAL_BUILD_PASS_BROWSER_NOT_RUN'})
progress=read(ROOT/'.runtime/TASK-120/flow/flow-progress.json')
receipts={k:v for k,v in progress.items() if k.endswith('.done')}
jsave(OUT/'flow-committed-receipts.json',{'source':'retained original HTTP/Windows receipts','receipts':receipts,
    'fresh_final_PG_SUM_read':False,'financial_totals_not_reconstructed_as_authority':True})
planned=ROOT/'.runtime/TASK-120/root-08/batch-03.json'
jsave(OUT/'root08-unexecuted-next-batch.json',{'planned':read(planned),'executed':False,'reason':'Written after the merged manager 60-second request window; root already stopped.',
    'stop_proof':'root-08-stop.json','no_root09_authority':True})

archive=OUT/'final-review-files.zip'
if archive.exists():raise RuntimeError('final_archive_already_exists')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as output:
    names=set()
    for name,raw in sorted(post):output.writestr('postimage/'+name,raw);names.add(name)
    # Include the entire actual final dist, including unchanged cached assets.
    for path in sorted((ROOT/'frontend/dist').rglob('*')):
        if path.is_file():
            name=path.relative_to(ROOT).as_posix()
            if name not in names:output.writestr('postimage/'+name,path.read_bytes())
    for path in sorted((OUT/'preimage').rglob('*')):
        if path.is_file():output.writestr(path.relative_to(OUT).as_posix(),path.read_bytes())
    output.writestr('source.diff',(OUT/'source.diff').read_bytes())
jsave(OUT/'final-review-files-identity.json',{'path':archive.name,'sha256':sha(archive.read_bytes()),'bytes':archive.stat().st_size,
    'includes_private_configuration':False,'includes_usable_Q_authority':False})
print(json.dumps({'baseline_checked':len(rows),'changed_existing':len(changed),'new_files':len(new),'unexplained_drift':unexpected,
    'rules_match':all(x['matches'] for x in rules),'review_zip_sha256':sha(archive.read_bytes())}))
