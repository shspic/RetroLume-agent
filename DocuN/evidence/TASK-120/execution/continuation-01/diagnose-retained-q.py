"""Original private denial witnesses only; no execution or PG connection."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.control import ControlHub
from app.data_exit.q_store import QAuthority
from tests.fixtures.task120 import resources as r
a=QAuthority(ControlHub(r.PRIVATE/'flow/control'))
rows=[]
for row in a.hub.state()['q']['requests'].values():
    if row['prepared']['domain']!='interview':continue
    rows.append({k:row.get(k) for k in ('prepared_id','claim','admission_intent','admission_owner','admission','closed','revoked','launch_claimed')})
r.write(Path(__file__).resolve().parent/'retained-interview-q-witness.json',{'no_runtime':True,'rows':rows})
print(json.dumps({'no_runtime':True,'rows':rows}))
