import hashlib,importlib.util,json,sys,unittest,os,faulthandler
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[3]
(E/'offline').mkdir(exist_ok=True)
os.environ['RETROLUME_NORMAL_TEST_SCRATCH']=str(E/'offline')
faulthandler.dump_traceback_later(10)
sys.path[:0]=[str(R/'backend'),str(R/'backend/.venv/Lib/site-packages')]
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
spec=importlib.util.spec_from_file_location('task128_tests',R/'backend/tests/test_normal_install.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
names=['test_19_connect_pins_driver_address_for_direct_apply_and_verify','test_22_ambient_service_is_rejected_before_driver_without_environment_changes']
result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(m.NormalInstallTests(n) for n in names))
with (E/'targeted-tests.json').open('x',encoding='utf-8') as out:json.dump({'names':names,'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful()},out)
raise SystemExit(0 if result.wasSuccessful() else 1)
