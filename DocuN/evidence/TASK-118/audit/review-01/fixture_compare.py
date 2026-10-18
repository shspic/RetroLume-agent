"""Match finite fixture-history candidates against recorded hash, no execution."""
import ast,hashlib,json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');R=Path('D:/shspic/project_NO3_RetroLume-agent');O=R/'DocuN/evidence/TASK-118/audit/review-01';C=R/'DocuN/evidence/TASK-117/execution/continuation-07'
raw=(R/'backend/tests/test_step018_audit_repairs.py').read_bytes();text=raw.decode('utf-8');lines=text.splitlines(keepends=True);node=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name=='qualified_messages');wanted='7ab0eab1a1b9dda669a1077438cbd7b2d1f95f39b16ea65edf7ab12e9fdfb2a2';matches=[]
for extra in range(4):
 candidate=''.join(lines[:node.lineno-1]+lines[node.end_lineno+extra:])
 candidate=candidate.replace('ResponseMode,Message)','ResponseMode)')
 candidate=candidate.replace('messages=qualified_messages(action,document)','messages=messages_for_teaching(action,document)').replace("messages=qualified_messages('evaluate',value)","messages=messages_for_teaching('evaluate',value)")
 candidate=candidate.replace("self.assertEqual(transport.calls[0]['payload'],json.loads(json.dumps(payload)))","self.assertEqual(transport.calls[0]['payload'],payload)")
 if hashlib.sha256(candidate.encode()).hexdigest()==wanted:
  dest=O/'reconstructed-noio-test_step018_audit_repairs.py';dest.write_text(candidate,encoding='utf-8')
  def methods(s):return {x.name:ast.dump(x,include_attributes=False) for x in ast.walk(ast.parse(s)) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))}
  a,b=methods(candidate),methods(text)
  matches.append({'sha256':wanted,'saved':str(dest),'changed_methods':[k for k in a if a[k]!=b.get(k)],'unchanged_methods':[k for k in a if a[k]==b.get(k)],'extra_blank_lines_removed':extra})
result={'current_sha256':hashlib.sha256(raw).hexdigest(),'matches':matches,'scope':'whitespace/typed Message fixture helper/JSON list expectation only; hash equality is exact, never import or execute'}
(O/'fixture-history.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
