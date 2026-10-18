"""Ordinary repository/service/native harness, shared C01 originals namespace."""
import io,json,secrets
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from pydantic import SecretStr
from .control import EVIDENCE,atomic_json
from .samples import SAMPLES,HASHES
from app.storage.originals import OriginalStore
from app.materials.repository import PostgresMaterials
from app.activities import PostgresAdmissionLedger,ActivitySpec,SourceSnapshot
from app.capabilities.contracts import ModelServiceConfig
from app.service_config import ActivityConfig,LayerState
from app.worker.session import SessionConfig
from app.interview.service import InterviewService
from app.interview.contracts import InterviewCommandInput

MODEL='task106-c01-synthetic'
DATA=EVIDENCE/'synthetic/data'
class Harness:
    def __init__(self,admin,dsn,out):
        self.admin,self.dsn,self.out=admin,dsn,out;self.saved={};self.effects=[]
        self.ledger=PostgresAdmissionLedger(dsn,statement_timeout_ms=10000,lock_timeout_ms=5000)
        self.materials=PostgresMaterials(dsn);(DATA/'originals').mkdir(parents=True,exist_ok=True);self.originals=OriginalStore(DATA/'originals')
        self.session=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
        model=ModelServiceConfig(provider='deepseek_chat_completions',base_url='https://api.deepseek.com',model=MODEL,api_key=SecretStr(secrets.token_urlsafe(24)),
            timeout_seconds=1,max_request_bytes=65536,max_response_bytes=65536,max_output_tokens_limit=1024)
        self.config=ActivityConfig(provider='deepseek_chat_completions',model=MODEL,quota_preview=None,model_service=model,create_layer=LayerState(True),continue_layer=LayerState(True),
            interview_model_layer=LayerState(True),interview_output_tokens=512,interview_followups=2,learning_layer=LayerState(True),learning_output_tokens=256,teaching_layer=LayerState(True),teaching_output_tokens=512)
        self.service=InterviewService(self.ledger,self.materials,self.originals,session_config=self.session)
    def material(self,name,text=None):
        raw=(SAMPLES[name] if text is None else text).encode('utf-8');original=self.originals.put(io.BytesIO(raw),max_bytes=5242880)
        row=self.materials.save(source_id=None,expected_version=None,filename=name,format='md',sha256=original.sha256,size=original.size);self.saved[name]=row;return row
    async def activity(self,names,**extra):
        aid=str(uuid4());data=dict(activity_id=aid,sources=tuple(SourceSnapshot(self.saved[n]['id'],self.saved[n]['version_id'],self.saved[n]['revision']) for n in names),
            deadline_at=datetime.now(timezone.utc)+timedelta(hours=3),max_requests=24,max_cost_microunits=100000,reserve_cost_microunits=100,max_request_bytes=65536,max_output_tokens=1024,
            max_running_seconds=3600,allowed_models=(('deepseek_chat_completions',MODEL),),max_tool_calls=0)
        data.update(extra);await self.ledger.create_activity(ActivitySpec(**data));return aid
    async def make(self,aid,action,body,key=None):
        v=await self.ledger.read_interview_workspace(aid);head=v['head'] or {};scope=(await self.ledger.inspect_scope(aid)).scope_revision
        return InterviewCommandInput.model_validate(dict(schema='interview.command.v1',business_key=key or str(uuid4()),action=action,expected_head_revision=head.get('revision',0),
            expected_goal_version=head.get('goal_version',0),expected_scope_revision=scope,body=body))
    async def command(self,aid,action,body,key=None):
        command=await self.make(aid,action,body,key);receipt=await self.service.submit_command(aid,command,self.config,run_tag='c01-'+secrets.token_hex(10))
        self.effects.append(dict(activity=aid,command=command.model_dump(),receipt=receipt));atomic_json(self.out/'effects.json',self.effects);return receipt,command
    async def start(self,names,target,roles=None):
        aid=await self.activity(names);roles=roles or {n:'reference' for n in names}
        await self.command(aid,'start',{'goal':{'target':target,'material_roles':[dict(source_id=self.saved[n]['id'],role=roles[n]) for n in names]}});return aid
    def snapshot(self,aid):
        with psycopg.connect(self.dsn,row_factory=dict_row) as conn:
            return dict(activity=dict(conn.execute('SELECT id::text,status,execution_generation,scope_revision,dispatch_closed,requests_reserved,cost_reserved_microunits,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s',(aid,)).fetchone()),
                head=dict(conn.execute('SELECT revision,goal_version,scope_revision,phase,last_seq,round_index,probe_depth,current_question_id::text,current_answer_id::text,current_feedback_id::text,pending_key::text FROM interview_heads WHERE activity_id=%s',(aid,)).fetchone() or {}),
                commands=[dict(x) for x in conn.execute('SELECT business_key::text,action,status,obsolete,launch_claimed,effect_applied,operation_id,request_sha256 FROM interview_commands WHERE activity_id=%s ORDER BY business_key',(aid,))],
                records=[dict(x) for x in conn.execute('SELECT record_id::text,seq,kind,answer_version,question_record_id::text,body_sha256,operation_id FROM interview_records WHERE activity_id=%s ORDER BY seq',(aid,))],
                operations=[dict(x) for x in conn.execute('SELECT operation_id,state,disposition,error_code,scope_revision FROM activity_operations WHERE activity_id=%s ORDER BY operation_id',(aid,))],
                results=[dict(x) for x in conn.execute('SELECT operation_id,payload_sha256 FROM activity_operation_results WHERE activity_id=%s ORDER BY operation_id',(aid,))])
