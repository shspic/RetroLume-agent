from metadata import *
base=ROOT/'DocuN/evidence/TASK-103/continuation-01'
files=['core-result.json','remaining-result.json','gaps-result.json','cleanup-gaps-result.json','sql/pg1-forward-proof.json','sql/pg3-forward-proof.json','sql/pg2-final-row-summary.json']
for rel in files:
    p=base/rel;v=load(p)
    if isinstance(v,dict):
        out={k:( [{'keys':list(x),'name':x.get('name',x.get('property'))} if isinstance(x,dict) else x for x in val] if isinstance(val,list) and k=='cases' else {'keys':list(val)} if isinstance(val,dict) else {'count':len(val)} if isinstance(val,list) else val) for k,val in v.items()}
    else:out={'count':len(v)}
    print(json.dumps({'path':str(p),'sha256':sha(p),'shape':out},ensure_ascii=False))
current=load(ROOT/'DocuN/evidence/TASK-104/read-only-03/business-before.json')
key='a392c565-1731-4314-b22e-6cee9458f862'
cmd=next(x for x in current['teaching_commands'] if x['business_key']==key)
activity=next(x for x in current['activities'] if x['id']==cmd['activity_id'])
save('current-unknown-preserved.json',{'at':stamp(),'source':'104/read-only-03/business-before.json（本次真实只读PG）','command':cmd,'activity':activity})
print(json.dumps({'actual_current_unknown':{k:cmd[k] for k in ('business_key','activity_id','status','operation_id','launch_claimed_at')},'actual_budget':{k:activity[k] for k in ('requests_reserved','cost_reserved_microunits','tools_reserved','running_settled_seconds','running_reserved_seconds')}},ensure_ascii=False))
finish('raw-case-names-and-live-unknown',{'selected_old_files':len(files),'new_business_write':0})
