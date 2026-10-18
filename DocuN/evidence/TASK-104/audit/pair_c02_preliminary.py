from metadata import *
base=ROOT/'DocuN/evidence/TASK-103/continuation-02'
no=load(base/'no-evidence-http.json');assert no['response_status']==409 and no['response']['detail']['code']=='no_evidence'
assert no['before']==no['after'] and no['budgets_before']==no['budgets_after'] and no['provider_sends']==no['sup']==0
browser=load(base/'browser/result.json');late=load(base/'browser/late-edit-controller.json');switch=load(base/'browser-02/late-switch-controller.json');pg=load(base/'tail/pg-before.json');persistent=load(base/'final/persistent-proof.json')
summary={'no_evidence':{'http_status':409,'code':'no_evidence','six_tables_deep_equal':True,'budgets_deep_equal':True,'provider_SUP':0},'browser_cases':[{k:x.get(k) for k in ('name','memory_id','business_key','stale_key','response_status','response','before','during','after','preserved','new_identity','receipt')} for x in browser['cases']], 'late_edit_controller':{k:v for k,v in late.items() if k not in ('response','network')},'late_switch_controller':{k:v for k,v in switch.items() if k not in ('response','network')},'pg_before':{'kind':type(pg).__name__,'keys':list(pg) if isinstance(pg,dict) else None},'persistent_proof':persistent}
save('c02-evidence-pairing-preliminary.json',summary)
for key,value in summary.items():
    if key=='persistent_proof': print(json.dumps({'persistent_proof_keys':list(value),'top_fields':{k:v for k,v in value.items() if not isinstance(v,(dict,list))}},ensure_ascii=False))
    else:print(json.dumps({key:value},ensure_ascii=False))
finish('c02-primary-case-fields-and-side-effects',{'no_evidence_verified':True,'old_total_browser_status':browser['status'],'runtime_writes_new':0})
