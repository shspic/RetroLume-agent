"""Finite offline validation of new controller gates, plans and JS syntax."""
from pathlib import Path
import json,py_compile,subprocess,sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from tests.fixtures.task120.queued import read_plan
class Gates(unittest.TestCase):
    def test_prospective_browser_512_one_actual_sample(self):
        for available,allowed in [(512*1024**2,True),(512*1024**2-1,False)]:
            with self.subTest(available=available),patch.object(r,'state',return_value={'current_permit_id':'TASK-120-Q-PREP-VALIDATION-04-20261019'}),patch.object(r,'event'),patch.object(r,'available_memory',return_value=available) as sample,patch.object(r.time,'sleep') as sleep:
                if allowed:r.settled_memory_gate('browser')
                else:
                    with self.assertRaisesRegex(RuntimeError,'task120_low_memory_browser'):r.settled_memory_gate('browser')
                sample.assert_called_once();sleep.assert_not_called()
    def test_old_browser_gate_not_retroactively_lowered(self):
        with patch.object(r,'state',return_value={'current_permit_id':'TASK-120-Q-PREP-REPAIR-03-20261019'}),patch.object(r,'event'),patch.object(r,'available_memory',return_value=512*1024**2):
            with self.assertRaises(RuntimeError):r.memory_gate('browser')
    def test_exact_new_finite_plan(self):
        p=read_plan(Path(__file__).with_name('root-24-plan.json'))
        self.assertEqual(p['root_id'],24);self.assertTrue(all(x['phase'].startswith('v04_') for x in p['stages']))
        self.assertLessEqual(sum(x['seconds'] for x in p['stages']),1680)
suite=unittest.defaultTestLoader.loadTestsFromTestCase(Gates);result=unittest.TextTestRunner(verbosity=2).run(suite)
for file in [ROOT/'backend/app/activities/teaching_repository.py',*(ROOT/'backend/tests/fixtures/task120').glob('*.py'),Path(__file__).with_name('runtime_control.py')]:py_compile.compile(str(file),doraise=True)
node=subprocess.run(['node','--check',str(ROOT/'frontend/tests/task120-ui-continuation.mjs')],timeout=15)
proof={'utc':r.utc(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful() and node.returncode==0,'JS_syntax_exit':node.returncode,'PG_API_Browser_started':0,'prior_11_checks_reused':True}
Path(__file__).with_name('preflight-result.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
raise SystemExit(0 if proof['successful'] else 1)
