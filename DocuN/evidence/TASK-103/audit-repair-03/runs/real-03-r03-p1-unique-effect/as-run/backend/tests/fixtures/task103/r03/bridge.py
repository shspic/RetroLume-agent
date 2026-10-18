"""同一主根内浏览器发出实际记忆POST之前计数；stdin仅合成身份。"""
import json,sys
from .control import Control,require_entry,atomic_json
def main():
 require_entry();data=json.load(sys.stdin);c=Control()
 assert data['action'] in ('save','revise')
 if data['action']=='save':
  assert data['expected_revision']==0
  with c.locked():
   state=c.load();ids=state.setdefault('synthetic_memory_ids',[]);assert data['memory_id'] not in ids;ids.append(data['memory_id']);atomic_json(c.path,state)
 else:assert data['memory_id'] in c.load().get('synthetic_memory_ids',[])
 number=c.reserve('memory_post',data);print(json.dumps({'count':number}))
if __name__=='__main__':main()
