"""只核新许可／harness前置；竞态必须由真实浏览器断言。"""
import ast,unittest
from tests.fixtures.task103.r03.control import Control,ROOT,COUNTS,BudgetDenied
class R03Preflight(unittest.TestCase):
 def test_scope_and_fixed_deadline(self):
  c=Control();s=c.load();self.assertEqual(s['deadline_ns']-s['start_ns'],10800*10**9)
  self.assertEqual(COUNTS['memory_post'],12);self.assertEqual(COUNTS['sup'],0)
  with self.assertRaises(BudgetDenied):c.validate({**s,'permit':'TASK-103-G9-C02-20261007'})
  self.assertEqual(ROOT.name,'project_NO3_RetroLume-agent')
 def test_current_harness_compile(self):
  for p in (ROOT/'backend/tests/fixtures/task103/r03').rglob('*.py'):ast.parse(p.read_text('utf-8'),filename=str(p))
