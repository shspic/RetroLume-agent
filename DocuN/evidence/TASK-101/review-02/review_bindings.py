"""静态完整字节、原方法stderr、AST断言绑定，不执行被审代码。"""
import ast, collections, difflib, hashlib, json, re, time
from review_io import ROOT, OWN, read, load, save, sha
from review_evidence import BASE, BATCHES
def parse_log(p):
    lines=read(p);methods=[];pending=None
    for i,line in enumerate(lines,1):
        m=re.match(r'(test_\w+) \(([^)]+)\)(.*)',line)
        if m:pending={'method':m[1],'qualified':m[2],'first_line':i}
        done=re.search(r'(?:\.\.\. |^)(ok|skipped.*|FAIL|ERROR)\s*$',line)
        if pending and done:methods.append({**pending,'outcome':done[1],'last_line':i});pending=None
    return methods
def ast_method(text,qualified):
    module,cls,method=qualified.rsplit('.',2);tree=ast.parse(text)
    klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
    node=next(n for n in klass.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==method)
    return node,klass
started=time.perf_counter();result={};file_cache={}
for label,kind in [('B1','repository-raw'),('B3','repository-raw'),('B3','http-raw'),('offline','common-raw'),('offline','repair-raw')]:
    folder=BASE/BATCHES[label];methods=parse_log(folder/kind/'stderr.txt');manifest=load(folder/'as-run/manifest.json');rows=[]
    rawresult=load(folder/kind/'result.json')
    for method in methods:
        module,cls,name=method['qualified'].rsplit('.',2);rel='backend/'+module.replace('.','/')+'.py'
        snapshot=folder/'as-run'/rel;current=ROOT/rel
        for p in (snapshot,current):
            if str(p) not in file_cache:file_cache[str(p)]='\n'.join(read(p))
        old,k=ast_method(file_cache[str(snapshot)],method['qualified']);new,_=ast_method(file_cache[str(current)],method['qualified'])
        asthash=lambda n:hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()
        rows.append({**method,'source':rel,'as_run_full_sha256':sha(snapshot),'manifest_sha256':manifest[rel],'final_full_sha256':sha(current),'method_AST_sha256':asthash(old),'final_method_AST_sha256':asthash(new),'source_line':old.lineno,'source_end_line':old.end_lineno,'assert_nodes':sum(isinstance(n,(ast.Assert,ast.Call)) and (isinstance(n,ast.Assert) or isinstance(n.func,ast.Attribute) and n.func.attr.startswith('assert')) for n in ast.walk(old)),'direct_calls':sorted({n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id for n in ast.walk(old) if isinstance(n,ast.Call) and isinstance(n.func,(ast.Attribute,ast.Name))})})
    identities=[]
    for rel,digest in manifest.items():
        snap=folder/'as-run'/rel;cur=ROOT/rel
        identities.append({'path':rel,'manifest':digest,'copy_match':snap.is_file() and sha(snap)==digest,'current_match':cur.is_file() and sha(cur)==digest})
    key=label+'/'+kind
    result[key]={'methods':rows,'raw_result':rawresult,'identity_count':len(identities),'copy_mismatches':[r['path'] for r in identities if not r['copy_match']],'changed_current':[r['path'] for r in identities if not r['current_match']]}
    print(key,'methods',len(rows),'raw_count',rawresult.get('tests'),'skipped',rawresult.get('skipped'),'exit',rawresult.get('exit_code'),'all_ok',all(r['outcome']=='ok' for r in rows),'all_source_equal',all(r['as_run_full_sha256']==r['final_full_sha256']==r['manifest_sha256'] for r in rows),'bad_copies',result[key]['copy_mismatches'])
    print('changed_current',result[key]['changed_current'])
    if label=='B1':
        for row in rows:print('PG',row['qualified'],row['source_line'],'assert_nodes',row['assert_nodes'])
old_union=[]
for file,classes in [('backend/tests/test_teaching_repository.py',('TeachingLedgerPGTests',)),('backend/tests/test_teaching_recovery.py',('RecoveryPgTests',)),('backend/tests/test_task100_integration.py',('IntegrationPGTests','IntegrationHttpTests'))]:
    text=file_cache.get(str(ROOT/file)) or '\n'.join(read(file));tree=ast.parse(text)
    for klass in tree.body:
        if isinstance(klass,ast.ClassDef) and klass.name in classes:
            for node in klass.body:
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('test_'):
                    old_union.append({'file':file,'class':klass.name,'method':node.name,'line':node.lineno})
observed={(m['source'],m['qualified'].rsplit('.',2)[1],m['method']) for batch in ('B1/repository-raw','B3/http-raw') for m in result[batch]['methods']}
result['old_methods_not_newly_executed']=[r for r in old_union if (r['file'],r['class'],r['method']) not in observed]
print('old_methods_not_newly_executed',result['old_methods_not_newly_executed'])
fixture_diffs={}
for rel in ['backend/tests/fixtures/task100/synthetic_content.py','backend/tests/fixtures/task100/runner.py','backend/tests/fixtures/task100/bootstrap/sitecustomize.py']:
    old='\n'.join(read(BASE/BATCHES['B1']/'as-run'/rel));new='\n'.join(read(ROOT/rel))
    fixture_diffs[rel]='\n'.join(difflib.unified_diff(old.splitlines(),new.splitlines(),fromfile='B1/'+rel,tofile='final/'+rel,n=3))
save('independent-method-bindings-v2.json',result)
if not (OWN/'independent-B1-fixture-deltas.json').exists():save('independent-B1-fixture-deltas.json',fixture_diffs)
for rel,diff in fixture_diffs.items():print('fixture_delta',rel,diff)
with (OWN/'helpers.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'action':'method binding','seconds':time.perf_counter()-started})+'\n')
