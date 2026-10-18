from metadata import *
base=ROOT/'DocuN/evidence/TASK-103'
for rel in ('continuation-01/core-result.json','continuation-01/remaining-result.json','continuation-01/gaps-result.json','continuation-01/cleanup-gaps-result.json'):
    v=load(base/rel)
    for i,case in enumerate(v.get('cases',[])):
        if i<4 or 'SQL' in case.get('name','') or '清理' in case.get('name','') or 'absent' in case.get('name',''):
            print(json.dumps({'file':rel,'index':i,'case':case},ensure_ascii=False))
current=load(ROOT/'DocuN/evidence/TASK-104/read-only-03/business-before.json')
records={x['record_id']:x for x in current['teaching_records']}; discrepancies=[]
for row in current['learning_memory_bodies']:
    body=json.loads(row['body']); observation=body.get('observation')
    if not isinstance(observation,dict):continue
    origin=records.get(observation.get('progress_record_id'))
    if origin and origin['body']:
        actual=json.loads(origin['body']).get('observations',{}).get('independent_answers',[])
        recorded=observation.get('independent_answer_ids',[])
        if set(actual)!=set(recorded):discrepancies.append({'memory_id':row['memory_id'],'version':row['version'],'origin_progress':origin['record_id'],'origin_independent_answers':actual,'memory_claimed_ids':recorded,'origin_current_answer':origin['answer_record_id'],'origin_status':json.loads(origin['body']).get('observations',{}).get('status'),'uncertainty':observation.get('uncertainty')})
save('R104-O01-observation-count-live-comparison.json',{'at':stamp(),'live_source':'read-only-03/business-before.json','mismatches':discrepancies,'new_test_execution':False})
print(json.dumps({'observed_memory_independent_id_mismatches':discrepancies},ensure_ascii=False))
finish('case-actual-values-and-observation-projection',{'live_mismatch_count':len(discrepancies),'new_business_operations':0})
