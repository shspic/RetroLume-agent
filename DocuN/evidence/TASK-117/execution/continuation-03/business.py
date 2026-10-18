from batch_runtime import *
from uuid import uuid4
def generate(flow,aid):
    w=flow.call('GET',f'/api/activities/{aid}/teaching/workspace');h=w['head'];rid=h['feedback_record_id']
    record=flow.call('GET',f'/api/activities/{aid}/teaching/records/{rid}')
    caps=flow.call('GET',f'/api/activities/{aid}/html/capabilities');assert caps['available'],caps
    result=flow.call('POST',f'/api/activities/{aid}/html/commands',{'business_key':str(uuid4()),'parent':{'kind':'teaching','record_id':rid,'body_sha256':record['body_sha256'],'point_id':None},'focus':'分钟换秒与平均速度d/t','expected_config_sha256':caps['config_sha256'],'confirmed':True},native=1)
    assert result['artifact_id'];return result
