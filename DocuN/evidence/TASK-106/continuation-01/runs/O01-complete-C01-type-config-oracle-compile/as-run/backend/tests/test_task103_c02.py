"""本轮独立许可字段及新薄fixture静态前置，不冒PG/浏览器证据。"""
import ast,copy,unittest
from tests.fixtures.task103.c02.control import Control,ROOT,COUNTS,LIMITS,BudgetDenied
class C02Preflight(unittest.TestCase):
 def test_fixed_receipt_and_conditional_budget(self):
  c=Control();data=c.load();self.assertEqual(data['deadline_ns']-data['start_ns'],7200*10**9)
  self.assertEqual(COUNTS['entry'],3);self.assertEqual(COUNTS['sup'],2);self.assertFalse(data['allow_sup_preparation'])
  self.assertEqual(LIMITS['cleanup'],300)
  for field,value in [('permit','TASK-103-G9-C01-20261006'),('deadline_ns',data['deadline_ns']+1)]:
   with self.assertRaises(BudgetDenied):c.validate({**data,field:value})
 def test_all_new_python_syntax(self):
  for path in (ROOT/'backend/tests/fixtures/task103/c02').rglob('*.py'):ast.parse(path.read_text('utf-8'),filename=str(path))
