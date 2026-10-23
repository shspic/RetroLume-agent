"""Independent review02 metadata only. No product/test import or runtime."""
import argparse, datetime, difflib, hashlib, json, zipfile
from pathlib import Path
ROOT=Path(r'D:\shspic\project_NO3_RetroLume-agent')
OUT=ROOT/'DocuN/evidence/TASK-121/audit/review-02'
INP=ROOT/'DocuN/evidence/TASK-121/orchestration-review02-20261021'
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(raw):
    p=Path(raw)
    return p if p.is_absolute() else ROOT/p
def save(name,obj):
    p=OUT/name
    assert OUT.resolve() in p.resolve().parents
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(paths,start,end):
    for name in paths:
        p=resolve(name)
        assert not any(x in str(p).lower() for x in ('.runtime','task-120-result','task-120-work-decision','result.before.bytes','finalize.py','finalize-completed.py')),'forbidden decode'
        lines=p.read_text(encoding='utf-8-sig').splitlines()
        print(str(name)+' lines='+str(len(lines)))
        for i,s in enumerate(lines,1):
            if i>=start and (end is None or i<=end): print(str(i)+': '+s)
def identities(label):
    d=load(INP/'audit-inputs.json'); permit=load(INP/'audit-permit.json'); scope=load(INP/'scope-index.json'); rows=[]
    def check(group,e):
        p=resolve(e.get('absolute_path',e.get('path')))
        raw=p.read_bytes() if p.is_file() else None
        actual=sha(raw) if raw is not None else None
        expected=e.get('sha256'); ok=actual==expected
        size_ok='bytes' not in e or (len(raw) if raw is not None else None)==e['bytes']
        suffix=False
        if label=='closing' and p==ROOT/'DocuN/results/TASK-121-result.md':
            original=(OUT/'prior-result-original.md').read_bytes()
            suffix=raw is not None and raw.endswith(original) and sha(original)==d['prior_audit_result']['sha256']
            ok=size_ok=suffix
        rows.append(dict(group=group,path=str(p),expected_sha256=expected,actual_sha256=actual,bytes=len(raw) if raw is not None else None,expected_bytes=e.get('bytes'),match=ok and size_ok,own_result_exact_suffix_preserved=suffix))
    for k,v in d.items():
        if isinstance(v,list):
            for e in v:
                if isinstance(e,dict) and 'sha256' in e and ('path' in e or 'absolute_path' in e): check(k,e)
        elif isinstance(v,dict) and 'sha256' in v and ('path' in v or 'absolute_path' in v): check(k,v)
    for e in scope['changes']: check('scope_changes',e)
    for key,name in [('contract_sha256','contract.md'),('input_manifest_sha256','audit-inputs.json'),('scope_index_sha256','scope-index.json')]:
        check('permit_binding',dict(path=str(INP/name),sha256=permit[key]))
    for e in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'): check('original_rules',e)
    for k in ('source_diff','fixture_diff','asrun_map','evidence_index','impact_matrix','method_adoption'): check('scope_'+k,scope[k])
    if label=='opening':
        raw=(ROOT/'DocuN/results/TASK-121-result.md').read_bytes()
        assert sha(raw)==d['prior_audit_result']['sha256'] and len(raw)==55795
        p=OUT/'prior-result-original.md'
        if p.exists(): assert p.read_bytes()==raw
        else: p.write_bytes(raw)
    save('identity-'+label+'.json',dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),checked=len(rows),rows=rows,mismatches=[r for r in rows if not r['match']]))
    members=[]
    with zipfile.ZipFile(resolve(d['completed_archive']['path'])) as z:
        for e in z.infolist():
            raw=z.read(e); rel=Path(e.filename); p=ROOT/rel
            safe=not rel.is_absolute() and '..' not in rel.parts
            members.append(dict(name=e.filename,bytes=len(raw),sha256=sha(raw),current_path_equal=safe and p.is_file() and p.read_bytes()==raw))
    save('zip-members-'+label+'.json',dict(count=len(members),entries=members,content_decoded=False))
    print(json.dumps(dict(checked=len(rows),mismatches=[r for r in rows if not r['match']],zip_entries=len(members),zip_differing_current=[m['name'] for m in members if not m['current_path_equal']]),ensure_ascii=False))
def diffs():
    s=load(INP/'scope-index.json'); result=[]
    for e in s['changes']:
        p=ROOT/e['path']; pre=resolve(s['preimage_directory'])/e['path']; new=p.read_bytes()
        old=pre.read_bytes() if pre.is_file() else None
        assert sha(new)==e['sha256'],e['path']
        assert (sha(old) if old is not None else None)==e['before_sha256'],e['path']
        a=(old or b'').decode('utf-8-sig').splitlines(); b=new.decode('utf-8-sig').splitlines()
        delta=''.join(difflib.unified_diff([x+'\n' for x in a],[x+'\n' for x in b],fromfile='before/'+e['path'],tofile='after/'+e['path'],n=4))
        dst=OUT/'net-diff'/(e['path']+'.diff'); dst.parent.mkdir(parents=True,exist_ok=True); dst.write_text(delta,encoding='utf-8')
        result.append(dict(path=e['path'],before_sha256=sha(old) if old is not None else None,after_sha256=sha(new),lines=len(b),diff_bytes=len(delta.encode('utf-8')),hunks=[x for x in delta.splitlines() if x.startswith('@@')],is_product=e['path'] in s['product_paths_changed']))
    save('diff-index.json',result)
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['identities','diffs','read']); p.add_argument('paths',nargs='*'); p.add_argument('--label',default='opening'); p.add_argument('--start',type=int,default=1); p.add_argument('--end',type=int); a=p.parse_args()
    if a.action=='identities': identities(a.label)
    elif a.action=='diffs': diffs()
    else: read(a.paths,a.start,a.end)
