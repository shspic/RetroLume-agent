"""用已真实捕获的PG前后与POST核本轮授权域，不启动资源或重做效果。"""
import json,sys,hashlib
from .control import Control,EVIDENCE,atomic_json
def main():
 c=Control();state=c.load();ids=state['synthetic_memory_ids'];reports=[];all_posts=[]
 for name in ['real-01-r03-main','real-02-r03-preloaded-targets']:
  folder=EVIDENCE/'groups'/name;before=json.loads((folder/'pg-before.json').read_text('utf-8'));after=json.loads((folder/'pg-after.json').read_text('utf-8'));browser=json.loads((folder/'browser/result.json').read_text('utf-8'))
  immutable_old=[]
  for table,rows in before.items():
   for row in rows:
    if table=='learning_memories' and row['memory_id'] in ids:
     final=next(x for x in after[table] if x['memory_id']==row['memory_id'])
     assert all(final[k]==v for k,v in row.items() if k not in ['revision','current_version','updated_at'])
    else:assert row in after[table],(name,table)
   immutable_old.append(table)
  assert not any(r['memory_id'] in ids for r in after['activity_memory_choices'])
  writes=[x['payload'] for x in browser['network'] if x['event']=='request' and x['method']=='POST'];proof=[]
  for payload in writes:
   mid=payload['memory_id'];assert mid in ids and payload['action'] in ('save','revise')
   record=next(r for r in after['learning_memory_commands'] if r['business_key']==payload['business_key'])
   assert record['effect_applied']
   revision=next(r for r in after['learning_memory_revisions'] if r['memory_id']==mid and r['created_by_key']==payload['business_key'])
   assert revision['version']==record['after_version']
   proof.append({'request':payload,'receipt_row':record,'revision':revision})
  all_posts.extend(writes);reports.append({'root':name,'browser_status':browser['status'],'old_rows_except_authorized_heads_equal':True,'authorized_head_fields':['revision','current_version','updated_at'],
   'not_selected_by_old_activities':True,'writes':proof,'before_path':str(folder/'pg-before.json'),'after_path':str(folder/'pg-after.json'),
   'after_sha256':hashlib.sha256((folder/'pg-after.json').read_bytes()).hexdigest(),'root_original_status':'FAIL'})
 assert len(all_posts)==state['counts']['memory_post']==7
 assert len({r['business_key'] for r in all_posts})==7
 last=json.loads((EVIDENCE/'groups/real-02-r03-preloaded-targets/pg-after.json').read_text('utf-8'))
 for mid in ids:
  head=next(r for r in last['learning_memories'] if r['memory_id']==mid);effects=[r for r in last['learning_memory_commands'] if r['memory_id']==mid and r['effect_applied']]
  assert head['current_version']==head['revision']==len(effects)
  assert len([r for r in last['learning_memory_bodies'] if r['memory_id']==mid])==len(effects)
 atomic_json(EVIDENCE/'captured-pg-verification.json',{'status':'PASS','executed':True,'scope':'已捕获真实原件的独立有限核对，不是新PG运行','root_total_FAIL_kept':True,'total_POSTs':len(all_posts),'unique_keys':7,'no_old_effect_replay':True,'groups':reports})
 print(json.dumps({'status':'PASS','POSTs':len(all_posts),'unique_keys':7,'old_data_preserved':True}));return 0
if __name__=='__main__':sys.exit(main())
