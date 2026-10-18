from audit_io import *
import re
raw=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
s=read(raw/'batch-01/stderr.txt')
found=[f'{m[2]}.{m[1]}' for m in re.finditer(r'^(test_[\w]+) \(([^)]+)\) \.\.\. ok$',s,re.M)]
r=load(raw/'batch-01/unittest-result.json')
finish('pairing-parser-diagnosis',{'our_regex_matches':len(found),'observed_methods':len(r['methods']),'method_mismatch':list(set(r['methods'])-set(found)),'suffix_repr':repr(s[-100:]),'original_failed_script':'pair_runtime.py','exit_code':1,'shell_seconds':0.369566,'product_not_run':True})
