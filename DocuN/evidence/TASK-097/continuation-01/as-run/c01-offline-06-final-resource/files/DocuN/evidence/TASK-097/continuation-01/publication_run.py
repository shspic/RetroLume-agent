from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'backend'))
suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_learning_observer_publication')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
