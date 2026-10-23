"""Read retained artifacts and normal codecs only. No PG or launch."""
import json,os,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r,setup
from app.data_exit.control import ControlHub
from app.data_exit.q_store import QAuthority
from app.service_config import load_activity_config
from app.capabilities.contracts import ModelCallRequest
from app.worker.one_call import OneCallInput
setup.environment('flow',include_admin=False)
authority=QAuthority(ControlHub(r.PRIVATE/'flow/control'))
config=load_activity_config(r.PRIVATE/'flow/activity.json').model_service
result={'no_pg':True,'no_launch':True,'rows':[]}
for row in authority.hub.state()['q']['requests'].values():
    if row['prepared']['domain']!='interview':continue
    stage='artifact'
    item={'prepared_id':row['prepared_id'],'claimed':bool(row.get('claim')),'launch_claimed':bool(row.get('launch_claimed'))}
    try:
        artifact=authority.artifact(row)
        request=ModelCallRequest.model_validate_json(json.dumps(artifact['request']))
        service=config.model_copy(update={'outbound_authorization':authority.reference(row)})
        stage='encode';wire=OneCallInput(row['prepared']['operation_id'],request,service).to_wire()
        stage='decode';decoded=OneCallInput.from_wire(wire)
        item.update(codec_pass=True,identical=decoded.to_wire()==wire)
    except BaseException as exc:
        item.update(stage=stage,error_type=type(exc).__name__,safe_code=str(exc) if type(exc) is ValueError else None,frames=[{'file':str(x.filename).replace(str(ROOT),'PROJECT'),'line':x.lineno,'function':x.name} for x in traceback.extract_tb(exc.__traceback__)])
    result['rows'].append(item)
r.write(Path(__file__).resolve().parent/'wire-readonly-diagnosis.json',result)
print(json.dumps(result))
