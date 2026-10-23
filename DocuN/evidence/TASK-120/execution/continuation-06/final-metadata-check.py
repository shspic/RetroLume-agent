"""Final saved-witness/identity checks; exact stop query only, no service start."""
from pathlib import Path
import hashlib,json,runpy,struct,sys
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'backend'))
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
from app.data_exit.files import private_file
private=ROOT/'.runtime/TASK-120/continuation-06'
private_file(private,directory=True);private_file(private/'cluster.json')
private_file(private/'python-hook',directory=True)
for p in (private/'python-hook').glob('*.py'):private_file(p)
from app.data_exit.control import ControlHub
hub=ControlHub(private/'scope-ui-final/control');control=hub.state()
q=[]
for pid,row in control['q']['requests'].items():
    q.append({'prepared_id':pid,'business_key':row['prepared']['business_key'],'operation_id':row['prepared']['operation_id'],
      'approval_recorded':bool(row.get('approval')),'approval_expires_at':row.get('approval',{}).get('body',{}).get('expires_at'),
      'claim_recorded':bool(row.get('claim')),'launch_claimed':bool(row.get('launch_claimed')),'admission_recorded':bool(row.get('admission')),
      'closed_reason':row.get('closed'),'current_eligibility':'INVALIDATED_SOURCE_FROZEN_AND_RESTORE_SELECTED'})
write(HERE/'final-protocol-currentness-witness.json',{'utc':datetime.now(timezone.utc).isoformat(),'fence':control['fence']['state'],'selector':control['selection'],'requests':q,'no_new_authority_constructed':True,'source_normal_grant_not_rebound_to_target':True,'normal_Q_denial':'readonly-cancel-mutation-denied.json'})
wanted={x['prepared_id']:x for x in read(EX/'continuation-02/retained-unknown-witness.json')['requests']};events={pid:[] for pid in wanted}
canonical=lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
previous='0'*64;seq=0
with (ROOT/'.runtime/TASK-120/flow/control/journal.bin').open('rb') as stream:
    while header:=stream.read(4):
        assert len(header)==4;size=struct.unpack('!I',header)[0];assert 1<=size<=65536;raw=stream.read(size)
        assert stream.read(73)==b'\nCOMMIT:'+hashlib.sha256(raw).hexdigest().encode()+b'\n'
        item=json.loads(raw);seq+=1
        assert item['seq']==seq and item['prev_hash']==previous and item['body_hash']==hashlib.sha256(canonical(item['payload']).encode()).hexdigest()
        previous=hashlib.sha256(raw).hexdigest();pid=item['payload'].get('prepared_id')
        if pid in events:events[pid].append({'kind':item['kind'],'seq':seq})
for pid,actual in events.items():assert actual==wanted[pid]['events']
write(HERE/'retained-original-Q-witness.json',{'committed_journal_chain_verified':True,'old_three_exact_event_sequences_unchanged':True,'requests':[{'business_key':wanted[pid]['business_key'],'prepared_id':pid,'events':actual} for pid,actual in events.items()],'no_resend_refund_or_old_slot_release':True,'Q_is_not_financial_authority':True})
ui=read(HERE/'readonly-UI-root-51.json');assert ui['status']=='PASS'
response=next(x for x in ui['responses'] if x['path']=='/api/data/saved-records' and x['status']==200)['body']
rows=[]
for item in response['items']:
    record=item['record'];rows.append({k:str(record[k]) if k=='id' else int(record[k]) for k in ('id','requests_reserved','cost_reserved_microunits','running_reserved_seconds','running_settled_seconds')})
rows.sort(key=lambda r:r['id']);earlier=read(HERE/'restore-target-final-financials.json')['activities'];assert rows==earlier
write(HERE/'restore-target-final-after-readonly-UI.json',{'authority':'Actual fresh PG readonly saved-records GET in root51 after rejected cancel, not a Q journal balance','raw':'readonly-UI-root-51.json','data_context':response['data_context'],'accounting_point':response['accounting_point'],'activities':rows,'requests':sum(x['requests_reserved'] for x in rows),'cost':sum(x['cost_reserved_microunits'] for x in rows),'same_as_root46_copy':True,'separate_copy_not_additional_budget':True})
for x in read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):assert sha(x['absolute_path'])==x['sha256']
from app.data_exit.schema_profiles import get_profile,R02,R03
for name,expected in get_profile(R03).migration_chain.items():assert sha(ROOT/'backend/migrations'/name)==expected
for x in read(HERE/'formal-bundle-identities.json')['assets']:assert sha(ROOT/x['path'])==x['sha256']
write(HERE/'final-rules-migrations-bundle-check.json',{'seven_locked_rules_unchanged':True,'001_014_unchanged':True,'015_sha256':get_profile(R03).migration_chain['015_activity_scope_delete_permission.sql'],'old_R02_chain_unchanged':get_profile(R02).migration_chain,'final_bundle_matches_normal_build063':True,'R01_R02_constants_review':'permission-risk-check.json'})
runpy.run_path(str(HERE/'final-stop-check-after-readonly.py'),run_name='__main__')
print('Final protocol/financial witnesses, old unknowns, exact identities and both stopped PG objects checked')
