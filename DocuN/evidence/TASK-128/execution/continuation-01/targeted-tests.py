import ast,faulthandler,hashlib,importlib.util,json,os,sys,time,unittest
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[4]
sys.path[:0]=[str(R/'backend'),str(R/'backend/.venv/Lib/site-packages')]
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
(E/'offline').mkdir(exist_ok=True);os.environ['RETROLUME_NORMAL_TEST_SCRATCH']=str(E/'offline')
faulthandler.dump_traceback_later(15,exit=True)
paths=[R/'deploy/initialize_normal.py',R/'backend/tests/test_normal_install.py']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
s=importlib.util.spec_from_file_location('continuation01_tests',paths[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
names=['test_19_connect_pins_driver_address_for_direct_apply_and_verify','test_22_ambient_service_is_rejected_before_driver_without_environment_changes','test_23_identity_accepts_only_host_addresses_and_preserves_other_checks']
started=time.perf_counter();result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(m.NormalInstallTests(n) for n in names))
assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
faulthandler.cancel_dump_traceback_later()
with (E/'targeted-tests.json').open('x',encoding='utf-8') as out:json.dump({'names':names,'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'seconds':time.perf_counter()-started,'before_after_identical':before},out,indent=2)
raise SystemExit(0 if result.wasSuccessful() else 1)
