import ast,difflib,hashlib,json
from pathlib import Path
E=Path(__file__).absolute().parent
p=E/'run-six.py';s=p.read_text(encoding='utf-8')
s=s.replace('            stage("5",self.check5)\n            if self.state["slots"]["interrupted"].get("holding"):self.stop_pg("interrupted")\n', '            require(self.state["checks"].get("5",{}).get("status")=="passed" and self.state["checks"].get("6",{}).get("status")=="passed", "backup_requires_existing_fifth_and_sixth_pass")\n')
s=s.replace('            stage("6",self.check6)\n','')
ast.parse(s);p.write_text(s,encoding='utf-8')
before=(E/'repair-before-run-six.py').read_text(encoding='utf-8')
(E/'helper-repair.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile='entry07/run-six.py',tofile='entry08/run-six.py')),encoding='utf-8')
state=json.loads((E/'checkpoint.json').read_bytes());diag=json.loads((E/'api-stop-diagnosis.json').read_bytes())
assert state['entries']==7 and state['slots']['source']['starts']==5 and state['api_starts']==1
assert all(r.get('already_absent') or not r.get('alive') or not r.get('same_birth') for r in diag['current_process_observations'])
assert not diag['port_owners']
record={'actual_entry07_failure':'api_tree_stop_unconfirmed','actual_native_parent_exit':0,'later_own_pid_birth_observations':'api-stop-diagnosis.json','root_cause':'helper checked descendant handle signals immediately after waiting for parent; subsequent read-only observation shows all original processes absent and port released','correction':'close owned input after stop line; bounded wait for child handles within native170s; save immediate/final observations before assertion; persist database facts before/after','source_product_change':False,'repeat_fifth':False,'repeat_verify':False,'new_entry':8,'source_starts_expected':[6,7],'api_starts_expected':[2,3]}
(E/'helper-repair-decision.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
