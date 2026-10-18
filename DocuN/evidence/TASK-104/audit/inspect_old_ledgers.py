from metadata import *
nav=load(ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/raw-evidence-navigation.json')
paths=nav['old_run_and_version_records']+nav['accounting_and_resources']
summaries=[]
for p in paths:
    value=load(p)
    if isinstance(value,dict):
        shape={k:({'kind':'list','count':len(v),'first':v[0] if v and k in ('runs','entries','records','executions') else None} if isinstance(v,list) else {'kind':'dict','keys':list(v)[:16]} if isinstance(v,dict) else v) for k,v in value.items()}
    elif isinstance(value,list):
        shape={'kind':'list','count':len(value),'first':value[0] if value else None}
    else:shape={'value_type':type(value).__name__}
    summaries.append({'path':p,'sha256':sha(p),'shape':shape})
save('old-ledger-shapes.json',summaries)
for x in summaries:print(json.dumps(x,ensure_ascii=False))
finish('raw-ledger-schema-navigation',{'files':len(paths),'no_author_result_read':True})
