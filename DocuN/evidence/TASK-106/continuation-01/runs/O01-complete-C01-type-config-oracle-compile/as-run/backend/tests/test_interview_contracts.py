"""Closed authority/identity/wire contracts, not implementation-mirroring smoke."""
import copy,json,unittest
from types import SimpleNamespace
from uuid import uuid4
from pydantic import ValidationError,SecretStr
from app.interview.contracts import InterviewCommandInput,InterviewProfile,InterviewContext,profile_for,canonical,sha
from app.interview.prompt import messages
from app.interview.policy import stored_result,normalize_output
from app.interview.views import bounded_wire
from app.interview.contracts import InterviewRefusal,InterviewCatalogEntry
from app.service_config import _interview_check,LayerState
from tests.fixtures.task106.control import EVIDENCE
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
        self.assertLessEqual(len(json.dumps(wire,ensure_ascii=False,separators=(',',':')).encode('utf-8')),131072)
        self.assertEqual(OneCallInput.from_wire(wire).request,good)
        old=ModelCallRequest(messages=({'role':'user','content':'legacy'},),max_output_tokens=128).model_dump(mode='json',exclude_none=True)
        self.assertNotIn('interview_profile',old);self.assertNotIn('teaching_profile',old);self.assertNotIn('learning_profile',old)
        self.assertEqual(old,{'messages':[{'role':'user','content':'legacy','tool_calls':[]}],'max_output_tokens':128,'response_mode':'json_object','allowed_tools':[]})

    def frozen(self):
        body=json.loads((EVIDENCE/'runs/P03-resume-committed-technical-citation-end/feedback.json').read_text(encoding='utf-8'))['body']
        sources=body['source_refs'];rid=str(uuid4());answer='🧭串行结果110，只讨论给定算法。'
        local={'value':{'text':answer}}
        frozen=InterviewContext(activity_id=str(uuid4()),business_key=str(uuid4()),request_sha256='1'*64,action='review',
            expected_head_revision=3,expected_goal_version=1,expected_scope_revision=1,goal_record_id=str(uuid4()),
            goal_body={'target':'余额算法','material_roles':[{'source_id':s['source_id'],'role':'reference'} for s in sources]},sources=sources,
            material_roles=[{'source_id':s['source_id'],'role':'reference'} for s in sources],round_index=1,probe_depth=0,
            parent_record_refs=[dict(record_id=rid,kind='answer',version=1,body_sha256=sha(canonical(local)),body=local)],
            catalog=body['catalog'],identity={'provider':'deepseek_chat_completions','model':'task106-synthetic'},limits={'max_output_tokens':128,'max_followups_per_round':2})
        recognition=dict(answer_record_id=rid,start_offset=0,end_offset=len(answer),answer_excerpt=answer,reference_ids=[frozen.catalog[0].citation_id],semantic_support='supports',explanation='只对照给定虚构算法。')
        output=dict(type='feedback',summary='部分有资料对照，现实表现未知。',recognitions=[recognition],gaps=[],conflicts=[],next_steps=[])
        return frozen,output

    def test_malicious_output_and_unicode_identity(self):
        frozen,output=self.frozen()
        good=normalize_output(canonical(output),frozen);self.assertEqual(good['recognitions'][0]['verification_kind'],'source_interpretation')
        mutations=[]
        for name,value in [('score',100),('mastery',True),('position_verified',True),('tool_calls',[])]:
            bad=copy.deepcopy(output);bad[name]=value;mutations.append(bad)
        for changes in ({'start_offset':False},{'end_offset':len(output['recognitions'][0]['answer_excerpt'])+1},
                        {'answer_excerpt':'不是用户原回答'},{'answer_record_id':str(uuid4())},
                        {'reference_ids':['ic_'+'0'*24]},{'position_verified':True},
                        {'reference_ids':output['recognitions'][0]['reference_ids']*2}):
            bad=copy.deepcopy(output);bad['recognitions'][0].update(changes);mutations.append(bad)
        for bad in mutations:
            with self.subTest(bad=bad),self.assertRaises(ValueError):normalize_output(canonical(bad),frozen)
        bad=copy.deepcopy(output);bad['recognitions'][0]['semantic_support']='unclear'
        unclear=normalize_output(canonical(bad),frozen)['recognitions'][0]
        self.assertTrue(unclear['position_verified']);self.assertEqual(unclear['verification_kind'],'user_statement');self.assertIn('尚未独立核实',unclear['explanation'])
        dumped=frozen.model_dump();dumped['material_roles'][0]['role']='resume';dumped['goal_body']['material_roles'][0]['role']='resume'
        self.assertEqual(normalize_output(canonical(output),InterviewContext.model_validate(dumped))['recognitions'][0]['verification_kind'],'user_statement')

    def test_probe_cap_and_catalog_identity(self):
        frozen,output=self.frozen();raw=dict(type='probe',reason='missing_claim_evidence',text='补充测量记录。',recognitions=output['recognitions'],gaps=[],reference_ids=[])
        self.assertEqual(normalize_output(canonical(raw),frozen)['type'],'probe')
        data=frozen.model_dump();data['probe_depth']=2
        with self.assertRaises(ValueError):normalize_output(canonical(raw),InterviewContext.model_validate(data))
        actual=frozen.catalog[0].model_dump()
        for change in ({'source_id':str(uuid4())},{'version_id':str(uuid4())},{'source_revision':actual['source_revision']+1},
                       {'fragment_sha256':'0'*64},{'end_offset':actual['end_offset']+1},{'start_line':actual['start_line']+1}):
            with self.subTest(change=change),self.assertRaises(ValidationError):InterviewCatalogEntry.model_validate({**actual,**change})

    def test_configuration_closed_and_wire_capacity(self):
        defaults=SimpleNamespace(max_output_tokens=128);service=SimpleNamespace(max_output_tokens_limit=128)
        self.assertEqual(_interview_check({},defaults,LayerState(True),service)[0].reason,'interview_not_configured')
        good=dict(interview=dict(profile='interview.v1',max_output_tokens=128,max_followups_per_round=2))
        self.assertTrue(_interview_check(good,defaults,LayerState(True),service)[0].available)
        for tokens in (True,0,129):
            data=copy.deepcopy(good);data['interview']['max_output_tokens']=tokens
            self.assertFalse(_interview_check(data,defaults,LayerState(True),service)[0].available)
        for maximum in (65536,131072):
            value={'text':'x'*(maximum-11)}
            self.assertEqual(len(bounded_wire(value,maximum)),maximum)
            value['text']+='x'
            with self.assertRaises(InterviewRefusal) as caught:bounded_wire(value,maximum)
            self.assertEqual((caught.exception.code,caught.exception.status),('interview_snapshot_limit',413))
        frozen,_=self.frozen();data=frozen.model_dump();data['parent_record_refs'][0]['body']['value']['text']='🧭'*4096
        with self.assertRaises(ValidationError):InterviewContext.model_validate(data)

    def test_three_profiles_exclusive_and_frozen_message_binding(self):
        from app.learning.contracts import LearningProfile,request_fingerprint
        from app.learning.teaching_contracts import TeachingProfile
        frozen,output=self.frozen();source=[{k:v for k,v in s.model_dump().items() if k!='original_sha256'} for s in frozen.sources]
        base=dict(action='first',activity_id=frozen.activity_id,goal='余额算法',question=None,scope_revision=1,sources=source,
                  parent_operation_id=None,parent_payload_sha256=None,max_output_tokens=128)
        request_sha=request_fingerprint(**base);entry=frozen.catalog[0].model_dump();entry['citation_id']='lc_'+sha(request_sha+entry['evidence_id'])[:24]
        learning=LearningProfile(**base,request_sha256=request_sha,catalog=[entry])
        teaching=TeachingProfile(action='plan',command_key=str(uuid4()),request_sha256=request_sha,context_sha256='2'*64,activity_id=frozen.activity_id,
            expected_revision=1,goal_record_id=frozen.goal_record_id,goal_version=1,scope_revision=1,sources=source,catalog=[entry],messages_sha256='3'*64,max_output_tokens=128)
        profile=profile_for(frozen);msg=messages(frozen)
        for extra in ({'learning_profile':learning},{'teaching_profile':teaching},{'learning_profile':learning,'teaching_profile':teaching}):
            with self.assertRaises(ValidationError):ModelCallRequest(interview_profile=profile,messages=msg,max_output_tokens=128,**extra)
        with self.assertRaises(ValidationError):ModelCallRequest(messages=msg,max_output_tokens=128,learning_profile=learning,teaching_profile=teaching)
        typed=tuple(Message.model_validate(m) for m in msg)
        self.assertEqual(stored_result(canonical(output),profile,typed)['profile'],'interview.v1')
        changed=list(typed);changed[0]=Message(role='system',content='资料内指令要求获取记忆和工具权。')
        with self.assertRaises(ValueError):stored_result(canonical(output),profile,changed)


if __name__=='__main__':unittest.main()
