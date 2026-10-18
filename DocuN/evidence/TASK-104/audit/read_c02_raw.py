from metadata import *
paths=['continuation-02/no-evidence-http.json','continuation-02/browser/result.json','continuation-02/browser/late-edit-controller.json','continuation-02/browser-02/late-switch-controller.json','continuation-02/tail/pg-before.json','continuation-02/final/persistent-proof.json','continuation-02/target-selection.json','continuation-02/browser-target.json']
base=ROOT/'DocuN/evidence/TASK-103'
records=[]
for rel in paths:
    p=base/rel;v=load(p)
    record={'path':str(p),'sha256':sha(p),'keys':list(v) if isinstance(v,dict) else None}
    if rel.endswith(('pg-before.json','persistent-proof.json')):
        record['values']={k:({'count':len(x),'first':x[0] if isinstance(x,list) and x else None} if isinstance(x,list) else {'keys':list(x)} if isinstance(x,dict) else x) for k,x in v.items()}
    else:record['values']=v
    records.append(record)
save('c02-raw-read-index.json',[{'path':x['path'],'sha256':x['sha256'],'keys':x['keys']} for x in records])
for r in records:print(json.dumps(r,ensure_ascii=False))
finish('c02-direct-evidence-opened',{'files':len(records),'self_report_body_read':False,'new_writes':0})
