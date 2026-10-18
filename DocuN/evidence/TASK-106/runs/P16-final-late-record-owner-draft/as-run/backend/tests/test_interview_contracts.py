"""Closed authority/identity/wire contracts, not implementation-mirroring smoke."""
import json,unittest
from uuid import uuid4
from pydantic import ValidationError,SecretStr
from app.interview.contracts import InterviewCommandInput,InterviewProfile,InterviewContext,profile_for,canonical,sha
from app.interview.prompt import messages
from app.interview.policy import stored_result
from app.capabilities.contracts import ModelCallRequest,Message,ModelServiceConfig
from app.worker.one_call import OneCallInput
from app.service_config import _InterviewInput


class InterviewContracts(unittest.TestCase):
    def command(self,**override):
        data=dict(schema='interview.command.v1',business_key=str(uuid4()),action='start',expected_head_revision=0,
            expected_goal_version=0,expected_scope_revision=1,body={'goal':{'target':'  “🧭余额算法”\r\n保持原文  '}})
        data.update(override);return data

    def test_keys_hash_and_original_text(self):
        aid=str(uuid4());a=InterviewCommandInput.model_validate(self.command());b=InterviewCommandInput.model_validate({**a.model_dump(),'business_key':str(uuid4())})
        self.assertEqual(a.request_hash(aid),b.request_hash(aid));self.assertEqual(a.body['goal']['target'],'  “🧭余额算法”\r\n保持原文  ')
        changed=InterviewCommandInput.model_validate({**a.model_dump(),'body':{'goal':{'target':'别的目标'}}})
        self.assertNotEqual(a.request_hash(aid),changed.request_hash(aid))

    def test_closed_actions_boolean_and_extra_authority(self):
        for data in [self.command(action='score'),self.command(expected_head_revision=False),self.command(body={'goal':None,'budget':0}),self.command(authority=True)]:
            with self.assertRaises(ValidationError):InterviewCommandInput.model_validate(data)
        for v in (0,True,2049):
            with self.assertRaises(ValidationError):_InterviewInput.model_validate(dict(profile='interview.v1',max_output_tokens=v,max_followups_per_round=2))

    def profile(self):
        return InterviewProfile(activity_id=str(uuid4()),business_key=str(uuid4()),action='ask',request_sha256='1'*64,context_sha256='2'*64,
            expected_head_revision=1,goal_version=1,scope_revision=1,round_index=0,probe_depth=0,goal_record_id=str(uuid4()))

    def test_carrier_closed_no_tool_parent_and_wire_alias(self):
        p=self.profile();m=({'role':'system','content':'fixed'},{'role':'user','content':'data'})
        good=ModelCallRequest(interview_profile=p,messages=m,max_output_tokens=128)
        dump=good.model_dump(mode='json',exclude_none=True)
        self.assertEqual(dump['interview_profile']['schema'],'interview.v1');self.assertNotIn('schema_id',dump['interview_profile'])
        self.assertEqual(ModelCallRequest.model_validate(dump),good)
        for kwargs in ({'allowed_tools':{'finite_calculate'}},{'messages':m[:1]},{'response_mode':'text'}):
            with self.assertRaises(ValidationError):ModelCallRequest(interview_profile=p,messages=kwargs.pop('messages',m),max_output_tokens=128,**kwargs)
        service=ModelServiceConfig(provider='deepseek_chat_completions',base_url='https://api.deepseek.com',model='task106-synthetic',api_key=SecretStr('SYNTHETIC-NOT-AN-ACCOUNT'),max_request_bytes=65536,max_response_bytes=65536,timeout_seconds=1.0)
        wire=OneCallInput('int10m.'+p.business_key.replace('-',''),good,service).to_wire()
        self.assertLessEqual(len(wire),131072)
        old=ModelCallRequest(messages=({'role':'user','content':'legacy'},),max_output_tokens=128).model_dump(mode='json',exclude_none=True)
        self.assertNotIn('interview_profile',old);self.assertNotIn('teaching_profile',old);self.assertNotIn('learning_profile',old)
        self.assertEqual(old,{'messages':[{'role':'user','content':'legacy','tool_calls':[]}],'max_output_tokens':128,'response_mode':'json_object','allowed_tools':[]})


if __name__=='__main__':unittest.main()
