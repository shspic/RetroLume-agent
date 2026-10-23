"""Recover already-written successful facts; no DB, application or runtime start."""
from pathlib import Path
import hashlib,json,struct,unittest,ast
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];EX=HERE.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return sha(canonical(v).encode())
def write(name,v):
    target=HERE/name
    assert not target.exists(),name
    target.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
events=[json.loads(line) for line in (EX/'events.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
def journal(slot):
    rows={};seq=0;previous='0'*64
    with (ROOT/'.runtime/TASK-120'/slot/'control/journal.bin').open('rb') as stream:
        while header:=stream.read(4):
            assert len(header)==4;size=struct.unpack('!I',header)[0];assert 1<=size<=65536
            raw=stream.read(size);assert stream.read(73)==b'\nCOMMIT:'+sha(raw).encode()+b'\n'
            event=json.loads(raw);seq+=1;assert event['seq']==seq and event['prev_hash']==previous and event['body_hash']==digest(event['payload']);previous=sha(raw)
            payload=event['payload'];kind=event['kind'];pid=payload.get('prepared_id') if isinstance(payload,dict) else None
            if kind=='q.prepared':rows[pid]=dict(payload,events=[])
            if pid in rows:
                rows[pid]['events'].append({'kind':kind,'seq':seq})
                for event_kind,field in [('q.claim','claim'),('q.admission_observed','admission')]:
                    if kind==event_kind:rows[pid][field]=payload['claim' if field=='claim' else 'fact']
    return rows
all_rows={slot:journal(slot) for slot in ('flow','budget-02')}
recovered=[]
for slot,prefix in [('flow','i'),('budget-02','i2')]:
    base=ROOT/'.runtime/TASK-120'/slot;progress=read(base/'r03-progress.json')
    fact=progress[prefix+'-ask.007'];receipt=progress[prefix+'-ask.done'];command=progress[prefix+'-ask']
    assert receipt['status']=='committed' and receipt['operation_id']==fact['operation_id'] and fact['read_status']=='committed_current'
    observed=[e for e in events if e.get('kind')=='actual_native_supervision_outcome' and e.get('root')==20 and (e.get('outcome',{}).get('model_receipt') or {}).get('context',{}).get('operation_id')==fact['operation_id']]
    assert len(observed)==1;outcome=observed[0]['outcome'];model=outcome['model_receipt']
    assert outcome['active_processes_at_end']==0 and not outcome['cleanup_incomplete'] and model['business_commit']=='committed' and model['result']['status']=='succeeded' and model['result']['payload_sha256']==fact['payload_sha256']
    row=next(x for x in all_rows[slot].values() if x['prepared']['operation_id']==fact['operation_id'])
    raw=(base/'control'/('q-prepared-'+row['prepared_id']+'.bin')).read_bytes();assert sha(raw)==row['artifact_sha256']
    artifact=json.loads(raw);p=row['prepared'];assert digest(artifact['prepared'])==row['prepared_sha256']
    assert digest(artifact['request'])==p['typed_request_sha256'] and digest(artifact['payload'])==p['payload_object_sha256'] and sha(canonical(artifact['payload']).encode())==p['payload_bytes_sha256'] and digest(artifact['provenance'])==p['provenance_sha256']
    value={'status':'PASS_FOR_RECORDED_ROOT20_MODEL_AND_007','recovered_after_fixture_KeyError':True,'no_new_PG_or_send':True,'slot':slot,'model':fact,'business_key':command['business_key'],
        'query_business_key':progress[prefix+'-query']['business_key'],'query_result_sha256':progress[prefix+'-query.done']['retrieval_ref']['result_sha256'],
        'prepared_id':row['prepared_id'],'full_request_sha256':p['typed_request_sha256'],'actual_supervision_event_utc':observed[0]['utc'],'007_currentness':'at original root20 PG read; no new live PG claim'}
    if slot=='budget-02':
        sample=read(ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json');selected=read(base/'creation-memory.json');binding=read(EX/'budget-02-selected-memory-binding.json')
        message=json.loads(artifact['request']['messages'][1]['content']);background=message['learning_background']
        assert len(background)==1 and background[0]['text']==sample['inputs']['memory_body'] and background[0]['memory_id']==selected['memory_id']==binding['entry']['memory_id']
        profile=artifact['request']['interview_profile'];assert profile['memory_selection_sha256']==binding['selection_sha256'] and profile['memory_dependency_sha256']==binding['dependency_sha256']
        value.update(frozen_memory_in_actual_full_request=True,memory_id=selected['memory_id'],frozen_text_sha256=sha(background[0]['text'].encode()),selection_sha256=binding['selection_sha256'],dependency_sha256=binding['dependency_sha256'])
    write(slot+'-interview-reconciled-positive.json',value);recovered.append(value)
progress=read(ROOT/'.runtime/TASK-120/flow/r03-progress.json')
write('teaching-plan-reconciled-positive.json',{'status':'PASS_PLAN_ONLY','007':progress['t-plan.007'],'exercise':'PREPARE_REJECTED_RATIONALE_FIELD; final fix offline only','new_PG_or_send':False})
old_keys={'1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e','430a4e36-08e1-411f-a73e-097506a6278b','3b561488-07b7-4d6d-8b98-05e793c96749'}
old=read(EX/'continuation-02/retained-unknown-witness.json');retained=[]
for row in all_rows['flow'].values():
    if row['prepared']['business_key'] not in old_keys:continue
    prior=next(x for x in old['requests'] if x['prepared_id']==row['prepared_id'])
    assert row['events']==prior['events']
    retained.append({'business_key':row['prepared']['business_key'],'operation_id':row['prepared']['operation_id'],'prepared_id':row['prepared_id'],'Q_event_sequence_exactly_unchanged_from_continuation02':True,'claim':row.get('claim'),'admission':row.get('admission'),'new_send':False})
assert len(retained)==3
write('retained-original-Q-witness.json',{'committed_frame_chains_verified':True,'original_requests':retained,'journal_is_not_financial_authority':True})
write('post-root20-reconciliation.json',{'recovered_models':recovered,'root20_original_FAIL_receipts_unchanged':True,'new_runtime':False,'new_claim':False,'new_approval':False})
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('tests.test_task120_repair03'))
write('repair-tests-049.json',{'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'new_PG':False})
for p in (ROOT/'backend/tests/fixtures/task120').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
if not result.wasSuccessful():raise SystemExit(1)
print(json.dumps({'original_PG_models_reconciled':len(recovered),'tests':result.testsRun,'Q_original_event_sequences_unchanged':True,'no_runtime':True}))
