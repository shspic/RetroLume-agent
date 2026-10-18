"""最终纯边界与原字节兼容；不替代末尾SQL/HTTP实测。"""
import asyncio,importlib.util,json,sys,unittest
from pathlib import Path
from pydantic import ValidationError
from app.learning.contracts import canonical,sha
from app.learning.teaching_contracts import TeachingFrozenContext,TeachingCommandInput,frozen_context_digest
from app.memory.contracts import read_bounded_json,MemoryRefusal
from app.memory.context import check_capacity
from app.capabilities.contracts import ModelServiceConfig,ModelCallRequest
from app.worker.one_call import OneCallInput
from tests.fixtures.task103.control import EVIDENCE,ROOT
from tests.fixtures.task103.windows_normal import config

class FinalPureTests(unittest.TestCase):
 def test_v1_canonical_bytes_match_preserved_pre_module(self):
  name='app.learning._task103_pre_contracts';path=EVIDENCE/'pre/backend/app/learning/teaching_contracts.py'
  spec=importlib.util.spec_from_file_location(name,path);old=importlib.util.module_from_spec(spec);sys.modules[name]=old;spec.loader.exec_module(old)
  command={'business_key':'11111111-1111-4111-8111-111111111111','expected_revision':0,'expected_goal_version':0,'expected_scope_revision':1,'action':'goal',
   'body':{'goal':'平均速度','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None}}
  activity='22222222-2222-4222-8222-222222222222'
  before=old.TeachingCommandInput.model_validate(command);after=TeachingCommandInput.model_validate(command)
  self.assertEqual(canonical(before.canonical_request_body(activity)).encode(),canonical(after.canonical_request_body(activity)).encode())
  self.assertEqual(before.request_sha256(activity),after.request_sha256(activity))
  for kind in ['model','tool']:
   value={'kind':kind,'reference_hashes':[],'operation_id':'teach8.sample','context_sha256':'0'*64}
   if kind=='model':value.update(profile_version='teaching.v1',prompt_version='teaching-prompt-v1',max_output_tokens=256,messages=[{'role':'user','content':'旧规范'}],catalog=[])
   else:value.update(call={'call_id':'c1','name':'finite_calculate','arguments_json':'{}','arguments_sha256':'a'*64})
   left=old.TeachingFrozenContext.model_validate(value);right=TeachingFrozenContext.model_validate(value)
   self.assertEqual(canonical(left.model_dump(by_alias=True)).encode(),canonical(right.model_dump(by_alias=True)).encode())
   self.assertEqual(old.frozen_context_digest(left),frozen_context_digest(right))

 def test_internal_one_call_roundtrip_and_real_byte_limit(self):
  service=ModelServiceConfig(provider='deepseek_chat_completions',base_url='https://api.deepseek.com',model='deepseek-v4-flash',api_key='pure-no-provider',
   timeout_seconds=2,max_request_bytes=65536,max_response_bytes=65536,max_output_tokens_limit=2048)
  call=OneCallInput('task103.pure',ModelCallRequest(messages=[{'role':'user','content':'有限请求'}],max_output_tokens=128),service)
  self.assertEqual(call.to_wire(),OneCallInput.from_wire(call.to_wire()).to_wire())
  with self.assertRaises(ValueError):OneCallInput('task103.limit',ModelCallRequest(messages=[{'role':'user','content':'界'*30000}],max_output_tokens=128),service).to_wire()

 def test_strict_nested_json_depth_and_utf8_without_http_or_pg(self):
  class Input:
   def __init__(self,raw):self.raw=raw
   async def stream(self):yield self.raw
  for raw in [b'{"body":{"a":1,"a":2}}',b'{"x":NaN}',b'{"x":"\xff"}',('{"x":'+('[0,'*13)+'0'+(']'*13)+'}').encode()]:
   with self.subTest(raw=raw[:40]),self.assertRaises(MemoryRefusal):asyncio.run(read_bounded_json(Input(raw)))
  self.assertEqual(asyncio.run(read_bounded_json(Input('{"x":"正常😀"}'.encode()))),{'x':'正常😀'})

 def test_capacity_checks_actual_messages_and_selected_bodies(self):
  from types import SimpleNamespace
  cfg=config()['memory_context'];snapshot={'max_output_tokens':2048};service=SimpleNamespace(provider='deepseek_chat_completions',model='deepseek-v4-flash',max_output_tokens_limit=2048)
  selection={'entries':[{'body':{'title':'我仍需练习','text':'低信任','kind':'self_report','uncertainty':'self_reported'}}]}
  messages=[{'role':'user','content':'当前输入'}]
  check_capacity(messages,selection,cfg,snapshot,service)
  for bad_cfg,bad_messages,bad_selection in [(None,messages,selection),({**cfg,'model_identity':{'provider':'deepseek_chat_completions','model':'different'}},messages,selection),
    (cfg,[{'role':'user','content':'x'*24577}],selection),(cfg,messages,{'entries':[{'body':{'text':'界'*2048}}]})]:
   with self.assertRaises(MemoryRefusal):check_capacity(bad_messages,bad_selection,bad_cfg,snapshot,service)

 def test_final_python_sources_compile_without_user_configuration(self):
  files=list((ROOT/'backend/app').rglob('*.py'))+list((ROOT/'backend/tests/fixtures/task103').rglob('*.py'))
  for path in files:compile(path.read_text(encoding='utf-8-sig'),str(path),'exec')
