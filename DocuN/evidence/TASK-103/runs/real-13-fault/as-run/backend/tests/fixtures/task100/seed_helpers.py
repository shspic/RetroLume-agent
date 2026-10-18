"""定向数据库前提种子；不冒充 SUP 或 provider 动态证据。正常 H1 另走全链。"""
from __future__ import annotations
import json
import os
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
from app.learning.contracts import canonical,sha
from app.learning.teaching_contracts import TeachingCommandInput,stored_teaching_result
from app.learning.teaching_service import TeachingService
from app.activities.teaching_repository import _state_after
from app.capabilities.contracts import build_business_payload
from app.service_config import load_activity_config
from .synthetic_content import MATERIAL,GOAL,output_for

def config():
    os.environ['RETROLUME_TASK100_SYNTHETIC_KEY']='task100-synthetic-not-a-real-key'
    return load_activity_config(Path(__file__).with_name('activity.synthetic.json'))

def command(head,action,body,key=None):
    return TeachingCommandInput(business_key=key or str(uuid4()),expected_revision=0 if head is None else head['revision'],
        expected_goal_version=0 if head is None else head['goal_version'],expected_scope_revision=1,action=action,body=body)

async def seed_model(fixture,aid,action,body):
    """明示插入已提交合成前提；未创建进程、未声称 transport 实际发送。"""
    ledger=fixture.ledger; head=fixture.head(aid); cmd=command(head,action,body)
    service=TeachingService(ledger,fixture.materials,fixture.originals)
    frozen,identity=await service._freeze_model_context(aid,cmd,config())
    profile=service._build_profile(aid,cmd,frozen,identity)
    doc=json.loads(frozen.messages[-1]['content']); result=output_for(doc)
    from app.capabilities.contracts import Message
    value=stored_teaching_result(profile,result,[Message.model_validate(m) for m in frozen.messages])
    fmt,payload,payload_sha=build_business_payload(json_object=value)
    receipt=await ledger.accept_teaching_command(aid,cmd,frozen)
    assert receipt.status=='accepted'
    rid,admission=str(uuid4()),str(uuid4());seq=head['last_seq']+1;revision=head['revision']+1
    kind='path_proposal' if action=='plan' else 'exercise'
    projection=json.loads(head['projection']); projection['pending_proposal_record_id']=rid if action=='plan' else None
    final=dict(head,revision=revision,phase='path_review' if action=='plan' else 'exercise_ready',reason_record_id=rid,pending_business_key=None,projection=projection)
    if action=='exercise': final.update(exercise_record_id=rid,answer_record_id=None,feedback_record_id=None)
    record_state=_state_after(revision,final)
    with __import__('psycopg').connect(fixture.dsn) as conn:
        conn.execute("INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,execution_generation,scope_revision,provider,configured_model,request_bytes,max_output_tokens,reserved_cost_microunits,state,disposition,recorded_at) VALUES (%s,%s,%s,'task100_fixture_seed',0,1,'deepseek_chat_completions','synthetic-model-100',100,2048,100000,'received','received',now())",(aid,cmd.operation_id(aid),admission))
        conn.execute('INSERT INTO activity_operation_results(activity_id,operation_id,admission_id,execution_generation,scope_revision,payload_format,payload,payload_sha256) VALUES (%s,%s,%s,0,1,%s,%s,%s)',(aid,cmd.operation_id(aid),admission,fmt,payload,payload_sha))
        conn.execute('INSERT INTO teaching_records(activity_id,record_id,seq,kind,business_key,ordinal,goal_version,scope_revision,goal_record_id,operation_id,body_sha256,source_refs,applied_revision,state_after) VALUES (%s,%s,%s,%s,%s,1,1,1,%s,%s,%s,%s,%s,%s)',
            (aid,rid,seq,kind,cmd.business_key,head['goal_record_id'],cmd.operation_id(aid),payload_sha,canonical([e.model_dump(include={'source_id','version_id','source_revision','original_sha256'}) for e in frozen.catalog]),revision,record_state))
        conn.execute('UPDATE teaching_heads SET revision=%s,last_seq=%s,phase=%s,reason_record_id=%s,pending_business_key=NULL,projection=%s,exercise_record_id=%s,answer_record_id=NULL,feedback_record_id=NULL WHERE activity_id=%s',
            (revision,seq,final['phase'],rid,canonical(projection),final['exercise_record_id'],aid))
        conn.execute("UPDATE teaching_commands SET status='committed',result_record_id=%s WHERE activity_id=%s AND business_key=%s",(rid,aid,cmd.business_key))
        conn.execute('UPDATE activities SET requests_reserved=requests_reserved+1,cost_reserved_microunits=cost_reserved_microunits+100000 WHERE id=%s',(aid,))
    return rid

async def ready_answer(fixture,source=None):
    source=source or fixture.text(MATERIAL,'task100-combined.md')
    aid=await fixture.activity([source],allowed_tools=('finite_calculate',),max_tool_calls=2)
    goal=command(None,'goal',{'goal':GOAL,'self_report':'经常混用分钟和秒','domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
    await fixture.ledger.apply_teaching_local(aid,goal)
    proposal=await seed_model(fixture,aid,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None})
    await fixture.ledger.apply_teaching_local(aid,command(fixture.head(aid),'accept_path',{'proposal_record_id':proposal}))
    head=fixture.head(aid)
    eid=await seed_model(fixture,aid,'exercise',{'confirmed':True,'path_record_id':str(head['path_record_id']),'node_id':'n1','purpose':'initial','parent_feedback_record_id':None,'retry_of':None})
    receipt=await fixture.ledger.apply_teaching_local(aid,command(fixture.head(aid),'answer',{'exercise_record_id':eid,'kind':'initial','text':'120÷2=60m/s','supersedes_answer_record_id':None}))
    return aid,source,eid,receipt.record_ids[0].record_id
