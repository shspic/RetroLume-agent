"""Read-only preimage-chain and AST method comparison; never import test/product."""
import ast,datetime as dt,difflib,hashlib,json,sys,time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
R=Path('D:/shspic/project_NO3_RetroLume-agent');O=R/'DocuN/evidence/TASK-118/audit/review-01';C=R/'DocuN/evidence/TASK-117/execution/continuation-07';T=time.perf_counter();access=[]
def raw(p):
    b=p.read_bytes();access.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
prior=load(R/'DocuN/evidence/TASK-118/audit/raw-bindings.json')['result']['checks'];prior={str((Path(x['path']) if Path(x['path']).is_absolute() else R/x['path']).resolve()):x['actual_sha256'] for x in prior}
rows=load(C/'post-source-manifest.json')['files'];facts=[];backups=[];errors=[]
for row in rows:
    p=R/row['path'];now=raw(p);base=None;before={}
    for key in ('TASK118_pre','S08_pre'):
        rec=row[key];bp=R/rec['backup'] if rec.get('backup') else None;b=raw(bp) if bp else None
        check={'path':row['path'],'stage':key,'backup':str(bp) if bp else None,'expected':rec.get('sha256'),'actual':hashlib.sha256(b).hexdigest() if b is not None else None,'match':(hashlib.sha256(b).hexdigest() if b is not None else None)==rec.get('sha256')}
        backups.append(check);before[key]=b
        if key=='TASK118_pre':base=b
    rel=row['path'].replace('/','__');dpath=O/'diffs'/(rel+'.diff');dpath.parent.mkdir(exist_ok=True)
    old='' if base is None else base.decode('utf-8-sig');new=now.decode('utf-8-sig')
    diff=''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='first-audit/'+row['path'],tofile='current/'+row['path']))
    dpath.write_text(diff,encoding='utf-8')
    facts.append({'path':row['path'],'D':row['D'],'current_sha256':hashlib.sha256(now).hexdigest(),'audited_baseline_matches_own_prior':None if str(p.resolve()) not in prior else (hashlib.sha256(base).hexdigest() if base else None)==prior[str(p.resolve())],
        'changed_from_first_available':base!=now,'changed_from_S08':before['S08_pre']!=now,'diff':str(dpath),'diff_lines':len(diff.splitlines()),'new_file':base is None})
    if p.suffix=='.py':
        try:ast.parse(new)
        except SyntaxError as ex:errors.append({'path':str(p),'error':str(ex)})
result={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'files':facts,'backup_checks':backups,'backup_mismatches':[x for x in backups if not x['match']],'AST_errors':errors,'accesses':access,'elapsed_seconds':time.perf_counter()-T}
(O/'scope-chain.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':[{k:v for k,v in x.items() if k not in ('current_sha256','diff')} for x in facts],'backup_mismatches':result['backup_mismatches'],'AST_errors':errors,'seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
