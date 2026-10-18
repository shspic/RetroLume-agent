"""Read logs and reconstruct exact as-run test bytes from bounded fixture-only edits."""
import ast,datetime as dt,hashlib,itertools,json,re,sys,time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');R=Path('D:/shspic/project_NO3_RetroLume-agent');C=R/'DocuN/evidence/TASK-117/execution/continuation-07';O=R/'DocuN/evidence/TASK-118/audit/review-01';T=time.perf_counter();access=[]
def raw(p):
 b=p.read_bytes();access.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
records={n:load(C/n) for n in ['targeted-as-run.json','targeted-no-io-as-run.json','model-v2-as-run.json','as-run-final.json']}
result={'bindings':[],'logs':{},'reconstruction':[]}
for n,v in records.items():
 for row in v.get('files',[]):
  p=R/row['path'];b=raw(p);result['bindings'].append({'record':n,'path':row['path'],'expected':row['sha256'],'current':sha(b),'match':sha(b)==row['sha256']})
for name in ['backend-targeted.log','backend-targeted-v2.log','backend-no-io.log','model-scope-v2.log','approved-model-final.log']:
 text=raw(C/name).decode('utf-8-sig');events=re.findall(r'^(test_\w+) \(([^)]+)\) \.\.\. (ok|FAIL|ERROR)\s*$',text,re.M)
 result['logs'][name]={'completed_methods':[{'name':fq,'status':status} for short,fq,status in events],'summary':re.findall(r'^Ran .*$|^OK$|^FAILED .*$',text,re.M)}
for rel in ['backend/tests/test_step018_control_snapshot.py','backend/tests/test_step018_audit_repairs.py']:
 cur=raw(R/rel);wanted={x['expected'] for x in result['bindings'] if x['path']==rel and not x['match']};text=cur.decode('utf-8-sig')
 variants=[('remove_tempdir_evidence_location_only',text.replace(",dir=os.environ.get('S08_EVIDENCE')",'')),
  ('pre_tuple_list_assert_only',text.replace("self.assertEqual(transport.calls[0]['payload'],json.loads(json.dumps(payload)))","self.assertEqual(transport.calls[0]['payload'],payload)"))]
 for basis,value in variants:
  b=value.encode('utf-8');h=sha(b)
  if h in wanted:
   dest=O/('reconstructed-'+Path(rel).name);dest.write_bytes(b)
   current_ast=ast.parse(text);old_ast=ast.parse(value)
   def methods(tree):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
   a,bm=methods(current_ast),methods(old_ast)
   result['reconstruction'].append({'path':rel,'matched_asrun_sha256':h,'basis':basis,'saved':str(dest),'methods_changed':[k for k in a if a[k]!=bm.get(k)],'methods_unchanged':[k for k in a if a[k]==bm.get(k)]})
oks={}
for log,v in result['logs'].items():
 for row in v['completed_methods']:
  if row['status']=='ok':oks.setdefault(row['name'],[]).append(log)
result['unique_methods_completed_ok']=len(oks);result['unique_ok_methods']=oks
result['at']=dt.datetime.now(dt.timezone.utc).isoformat();result['accesses']=access;result['elapsed_seconds']=time.perf_counter()-T
(O/'method-bindings.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'binding_mismatches':[x for x in result['bindings'] if not x['match']],'reconstruction':result['reconstruction'],'unique_completed_ok':len(oks),'ok_by_log':{k:len([x for x in v['completed_methods'] if x['status']=='ok']) for k,v in result['logs'].items()},'seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
