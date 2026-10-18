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
