"""独立只读差异及原件配对；只导入自有标准库读取辅助。"""
import ast,difflib,json,pathlib,re,sys,time
from collections import Counter
from datetime import datetime,timezone
from review_io import ROOT,OWN,read,load,sha,save
RAW=ROOT/'DocuN/evidence/TASK-100/audit-repair-03'
def diffs():
    index=load(ROOT/'DocuN/evidence/TASK-101/review-02-input.json');rows=[]
    for c in index['changes']:
        if c['path'].startswith('frontend/dist/'):continue
        pre=RAW/'pre'/c['path'];current=ROOT/c['path']
        before='\n'.join(read(pre)) if pre.exists() else ''
        after='\n'.join(read(current)) if current.exists() else ''
        delta=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='pre/'+c['path'],tofile='current/'+c['path']))
        rows.append({'path':c['path'],'pre_sha256':sha(pre) if pre.exists() else None,'current_sha256':sha(current) if current.exists() else None,'normalized_diff':delta,'diff_lines':len(delta.splitlines())})
    save('independent-normalized-diffs.json',rows)
    print([(r['path'],r['diff_lines']) for r in rows])
def show():
    for row in load(OWN/'independent-normalized-diffs.json'):
        if any(s in row['path'] for s in sys.argv[2:]):print(row['path']+'\n'+row['normalized_diff'])
def outlines():
    index=load(ROOT/'DocuN/evidence/TASK-101/review-02-input.json');rows=[]
    for c in index['changes']:
        p=ROOT/c['path']
        if not p.is_file() or p.suffix!='.py':continue
        text='\n'.join(read(p));tree=ast.parse(text)
        for cls in ast.walk(tree):
            if isinstance(cls,(ast.FunctionDef,ast.AsyncFunctionDef)):
                rows.append({'path':c['path'],'name':cls.name,'line':cls.lineno,'end':cls.end_lineno})
    save('current-function-outline.json',rows)
    print([(r['path'],r['name'],r['line'],r['end']) for r in rows if r['name'].startswith('test_') or '/fixtures/' in r['path']])
begun=time.perf_counter()
{'diffs':diffs,'show':show,'outlines':outlines}[sys.argv[1]]()
with (OWN/'helpers.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'action':sys.argv[1],'seconds':time.perf_counter()-begun})+'\n')
