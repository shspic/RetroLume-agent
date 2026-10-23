"""TASK-121 只读文件身份和记录对照，不导入项目模块。"""
import argparse
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(r'D:\shspic\project_NO3_RetroLume-agent')
OUT = ROOT / 'DocuN/evidence/TASK-121/audit'
INPUT = ROOT / 'DocuN/evidence/TASK-121/orchestration-20261021'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save(name, data):
    destination = OUT / name
    if destination.parent.resolve() != OUT.resolve():
        raise ValueError('输出越界')
    destination.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def identities():
    inputs, scope = load(INPUT/'audit-inputs.json'), load(INPUT/'scope-index.json')
    rows = []
    def check(group, entry, hash_key='sha256'):
        rawpath = entry.get('absolute_path',entry.get('path'))
        path = Path(rawpath)
        if not path.is_absolute():
            path = ROOT / path
        exists = path.is_file()
        raw = path.read_bytes() if exists else b''
        actual = digest(raw) if exists else None
        expected = entry.get(hash_key)
        row = dict(group=group,path=str(path),expected=expected,actual=actual,exists=exists,
                   bytes=len(raw) if exists else None,match=(not exists if expected is None else exists and expected==actual))
        if 'bytes' in entry:
            row['expected_bytes']=entry['bytes']
            row['match'] = row['match'] and row['bytes']==entry['bytes']
        rows.append(row)
    for group in ('rules','current_frozen_files','formal_dist','raw_evidence_identity_entries','engineering_ledger'):
        for entry in inputs[group]:
            check(group,entry)
    for group in ('opaque_engineering_report','candidate_archive'):
        check(group, inputs[group])
    for entry in scope['net_product_changes_relative_to_initial_manifest']:
        check('net_product_changes',entry,'final_sha256')
    for entry in scope['diff_chain']:
        check('diff_chain',entry)
    for entry in scope['as_run_index']:
        check('as_run_index',entry)
    for entry in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
        check('original_rule_locks',entry)
    save('identity-check.json',dict(observed_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
         rows=rows,checked=len(rows),mismatches=[r for r in rows if not r['match']]))
    archive=ROOT/inputs['candidate_archive']['path']
    members=[]
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            raw=z.read(item)
            name=item.filename
            path=ROOT/name
            same=path.is_file() and digest(path.read_bytes())==digest(raw) if not name.startswith(('/', '\\')) and '..' not in Path(name).parts else None
            members.append(dict(name=name,bytes=len(raw),sha256=digest(raw),current_path_exists=path.is_file(),same_current_bytes=same))
    save('candidate-zip-members.json',dict(count=len(members),entries=members,content_decoded=False))
    print(json.dumps(dict(checked=len(rows),mismatches=[r for r in rows if not r['match']],zip_entries=len(members)),ensure_ascii=False))

def read(paths, start, end):
    for path in paths:
        p=ROOT/path
        banned={'task-120-result.md','task-120-work-decision.md'}
        if p.name.lower() in banned:
            raise ValueError('禁止解码工程报告')
        lines=p.read_text(encoding='utf-8-sig',errors='replace').splitlines()
        print(str(path)+' total_lines='+str(len(lines)))
        for i,line in enumerate(lines,start=1):
            if i>=start and (end is None or i<=end):
                print(str(i)+': '+line)

def netdiff():
    scope=load(INPUT/'scope-index.json')
    summary=[]
    for entry in scope['net_product_changes_relative_to_initial_manifest']:
        name=entry['path']
        current=ROOT/name
        pre=ROOT/scope['baseline_preimages']/name
        old=pre.read_bytes() if pre.is_file() else None
        provenance=str(pre.relative_to(ROOT)) if old is not None else None
        if old is None and entry['initial_sha256'] is not None:
            for increment in scope['later_preimages']:
                candidate=ROOT/'DocuN/evidence/TASK-120/execution'/increment/name
                if candidate.is_file() and digest(candidate.read_bytes())==entry['initial_sha256']:
                    old=candidate.read_bytes();provenance=str(candidate.relative_to(ROOT));break
        new=current.read_bytes()
        expected=entry['initial_sha256']
        if old is not None and digest(old)!=expected:
            raise ValueError('preimage mismatch '+name)
        old_lines=[x+'\n' for x in (old or b'').decode('utf-8-sig').splitlines()]
        new_lines=[x+'\n' for x in new.decode('utf-8-sig').splitlines()]
        delta=list(difflib.unified_diff(old_lines,new_lines,fromfile='initial/'+name,tofile='final/'+name,n=5))
        output=OUT/'net-diff'/(name+'.diff')
        if OUT.resolve() not in output.resolve().parents:
            raise ValueError('输出越界')
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(''.join(delta),encoding='utf-8',newline='\n')
        summary.append(dict(path=name,initial_manifest_present=entry['initial_manifest_entry_present'],
          preimage_available=old is not None,preimage_path=provenance,preimage_sha256=digest(old) if old is not None else None,
          final_sha256=digest(new),final_lines=len(new.splitlines()),diff_lines=len(delta),
          hunks=[x.strip() for x in delta if x.startswith('@@')]))
    save('net-diff-index.json',summary)
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('identities','read','netdiff'))
    parser.add_argument('paths',nargs='*')
    parser.add_argument('--start',type=int,default=1)
    parser.add_argument('--end',type=int)
    args=parser.parse_args()
    if args.action=='identities': identities()
    elif args.action=='netdiff': netdiff()
    else: read(args.paths,args.start,args.end)
