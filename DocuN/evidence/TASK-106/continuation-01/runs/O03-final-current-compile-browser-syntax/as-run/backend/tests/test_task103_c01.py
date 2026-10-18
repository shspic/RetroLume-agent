"""本轮必要控制和类型口径；不访问真实库或启动资源。"""
import copy,unittest
from unittest.mock import patch
from tests.fixtures.task103.c01.control import Control,COUNTS,LIMITS,BudgetDenied,finite,aggregate,ROOT
class C01Controls(unittest.TestCase):
 def test_fixed_permit_counters_and_limits(self):
  c=Control();d=c.load()
  for field,value in [('deadline_ns',d['deadline_ns']+1),('permit','TASK-103-G9-20261006')]:
   with self.subTest(field=field),self.assertRaises(BudgetDenied):c.validate({**d,field:value})
  for value in [True,None,-1,25]:
   bad=copy.deepcopy(d);bad['counts']['sup']=value
   with self.subTest(value=value),self.assertRaises(BudgetDenied):c.validate(bad)
  for value in [True,None,float('nan'),-1]:
   with self.assertRaises(BudgetDenied):finite(value)
  self.assertEqual(COUNTS['container_create'],0);self.assertEqual(LIMITS['cleanup'],600)
 def test_new_root_reuses_resource_identity_without_creation(self):
  from tests.fixtures.task103.c01.resources import OwnedDocker
  with self.assertRaises(BudgetDenied):OwnedDocker().create(1)
  self.assertEqual(aggregate([{'status':'BLOCKED','executed':False}],0),'BLOCKED')
  self.assertEqual(aggregate([{'status':'FAIL','executed':True}],0),'FAIL')
 def test_preserved_supervision_type_manager50(self):
  from app.worker.session import SessionConfig
  cfg=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2,startup_limit_seconds=5,manager_db_timeout_seconds=5,cleanup_seconds=5,mutex_wait_seconds=3,manager_overhead_seconds=30)
  self.assertEqual(cfg.manager_total_seconds,50)
 def test_all_changed_python_sources_compile(self):
  for folder in [ROOT/'backend/app',ROOT/'backend/tests/fixtures/task103/c01']:
   for path in folder.rglob('*.py'):compile(path.read_text(encoding='utf-8-sig'),str(path),'exec')

class C01TeachingEvidenceHTTP(unittest.TestCase):
 def test_real_evidence_refusal_http_before_and_after(self):
  # 实际ASGI异常映射，只有底层service为抛错替身；不冒PG、认证或业务效果证明。
  import importlib.util,sys
  from pathlib import Path
  from unittest.mock import AsyncMock,patch
  from fastapi import FastAPI
  from fastapi.testclient import TestClient
  from app.learning.evidence import LearningRefusal
  from app.learning import teaching_api as current
  name='app.learning._task103_c01_pre_teaching_api'
  path=ROOT/'DocuN/evidence/TASK-103/continuation-01/pre/backend/app/learning/teaching_api.py'
  spec=importlib.util.spec_from_file_location(name,path);previous=importlib.util.module_from_spec(spec);sys.modules[name]=previous;spec.loader.exec_module(previous)
  def response(module):
   app=FastAPI();app.include_router(module.router)
   class Service:submit_command=AsyncMock(side_effect=LearningRefusal('no_evidence','有限词项检索没有找到相关证据；请明确目标或调整资料范围'))
   service=Service()
   command={'business_key':'11111111-1111-4111-8111-111111111111','expected_revision':1,'expected_goal_version':1,'expected_scope_revision':1,
    'action':'plan','body':{'confirmed':True,'correction_record_id':None,'retry_of':None}}
   with patch.object(module,'_guard',return_value=None),patch.object(module,'_config',return_value=None),patch.object(module,'_service',return_value=service),TestClient(app,raise_server_exceptions=False) as client:
    result=client.post('/api/activities/22222222-2222-4222-8222-222222222222/teaching/commands',json=command)
   service.submit_command.assert_awaited_once();return result
  before=response(previous);after=response(current)
  self.assertEqual(before.status_code,500);self.assertEqual(after.status_code,409)
  self.assertEqual(after.json()['detail']['code'],'no_evidence');self.assertIn('明确目标',after.json()['detail']['message'])
