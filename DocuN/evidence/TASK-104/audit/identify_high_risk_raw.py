from metadata import *
base=ROOT/'DocuN/evidence/TASK-103'
for name in ('migration-upgrade-resume-result.json','migration-fault-result.json','memory-boundaries-result.json','integration-resume-result.json','integration-remaining-result.json','content-oracle-final.json'):
    p=base/name;v=load(p)
    out={}
    for k,x in v.items():
        if k in ('cases','observations') and isinstance(x,list):
            out[k]=[{field:y.get(field) for field in ('name','status','executed','sqlstate','reason','properties','before_sha','after_sha','received','new_result_count','budgets') if field in y} if isinstance(y,dict) else y for y in x]
        elif isinstance(x,dict):out[k]={'keys':list(x)}
        elif isinstance(x,list):out[k]={'count':len(x)}
        else:out[k]=x
    print(json.dumps({'file':name,'sha256':sha(p),'raw_fields':out},ensure_ascii=False))
print(json.dumps({'fixture_assertion_names':[]},ensure_ascii=False))
finish('original-high-risk-case-identification',{'original_runs_not_reexecuted':True})
