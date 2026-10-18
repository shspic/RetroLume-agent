from audit_io import *
from collections import Counter
raw=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
result={}
for rel in ('batch-01/as-run-identities.json','batch-01/after-identities.json','case-results.json','pre-identities.json','final-identities.json','protected-method-byte-check.json','delivery-check.json'):
    value=load(raw/rel)
    if isinstance(value,list):
        result[rel]={'kind':'list','count':len(value),'first':value[0] if value else None}
    elif isinstance(value,dict):
        result[rel]={'kind':'dict','keys':list(value),'values':{k:({'count':len(v),'first':v[0] if v else None} if isinstance(v,list) else v if not isinstance(v,dict) else {'keys':list(v)[:16]}) for k,v in value.items()}}
structure=load(OWN/'source-structure-check.json')
result['our_structural_counts']={path:dict(Counter('protected-identical' if not x['allowed_change'] and x['identical_source_segment'] else 'changed' for x in structure['methods'] if x['path']==path)) for path in set(x['path'] for x in structure['methods'])}
result['protected_non_test_functions']=[x['name'] for x in structure['methods'] if 'test_task100_repair' in x['path'] and not x['allowed_change'] and not x['test_method']]
save('raw-schema-summary.json',result)
finish('raw-schema-and-protection-counts',result)
