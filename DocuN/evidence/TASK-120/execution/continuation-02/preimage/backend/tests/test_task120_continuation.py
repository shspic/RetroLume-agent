import copy,json,unittest
from pathlib import Path
from tests.fixtures.task120.queued import read_plan,runnable,PERMIT

class FinitePlanTests(unittest.TestCase):
    def setUp(self):
        from tests.fixtures.task120 import resources as r
        self.path=r.PRIVATE/'finite-plan-offline.json'
        self.plan={'schema':'task120.finite-plan.v1','permit_id':PERMIT,'root_id':9,'stages':[
            {'id':'observe','phase':'observe','seconds':30,'depends_on':[]},
            {'id':'teaching','phase':'teaching','seconds':240,'depends_on':['observe']},
            {'id':'budget','phase':'budget','seconds':280,'depends_on':['observe']}]}
    def test_failed_business_does_not_skip_independent_budget(self):
        self.path.write_text(json.dumps(self.plan),encoding='utf-8')
        plan=read_plan(self.path)
        outcomes={'observe':'PASS','teaching':'FAIL'}
        self.assertTrue(runnable(plan['stages'][2],outcomes))
        self.assertFalse(runnable(plan['stages'][1],{'observe':'FAIL'}))
    def test_closed_plan_rejects_external_argv_forward_dependencies_and_deadline_extension(self):
        invalid=[]
        v=copy.deepcopy(self.plan);v['stages'][1]['argv']=['arbitrary'];invalid.append(v)
        v=copy.deepcopy(self.plan);v['stages'][1]['depends_on']=['budget'];invalid.append(v)
        v=copy.deepcopy(self.plan);v['stages'][1]['seconds']=301;invalid.append(v)
        v=copy.deepcopy(self.plan);v['root_id']=8;invalid.append(v)
        v=copy.deepcopy(self.plan);v['stages']=[{'id':'s'+str(x),'phase':'budget','seconds':300,'depends_on':[]} for x in range(6)];invalid.append(v)
        for value in invalid:
            self.path.write_text(json.dumps(value),encoding='utf-8')
            with self.assertRaises(ValueError):read_plan(self.path)

class StartupCleanupTests(unittest.TestCase):
    def test_pressure_cleanup_waits_for_inflight_start_before_stopping(self):
        import importlib.util,threading,time
        from unittest.mock import patch
        path=Path(__file__).resolve().parents[2]/'DocuN/evidence/TASK-120/execution/continuation-01/runtime_control.py'
        spec=importlib.util.spec_from_file_location('task120_continuation_control',path)
        control=importlib.util.module_from_spec(spec);spec.loader.exec_module(control)
        entered=threading.Event();release=threading.Event();stopped=threading.Event();order=[]
        def start(*args,**kwargs):
            entered.set();self.assertTrue(release.wait(2));order.append('start_returned')
        def stop():order.append('stop_after_start');stopped.set();return {'stopped':True}
        with patch.object(control.r,'state',return_value={'pg_registry':{'Id':'own'},'no_new_container_or_volume_create':True}),patch.object(control.r,'container'),patch.object(control.r,'owned',return_value={'state':{'Running':False}}),patch.object(control.r,'memory_gate'),patch.object(control.r,'count'),patch.object(control.r,'update'),patch.object(control.r,'event'),patch.object(control.r,'docker',side_effect=start),patch.object(control.r,'stop_pg',side_effect=stop):
            starting=threading.Thread(target=control.start_existing_pg);starting.start();self.assertTrue(entered.wait(1))
            cleanup=threading.Thread(target=control.stop_existing_pg);cleanup.start()
            self.assertFalse(stopped.wait(.05));release.set();starting.join(2);cleanup.join(2)
            self.assertFalse(starting.is_alive() or cleanup.is_alive())
        self.assertEqual(order,['start_returned','stop_after_start'])

class NativeControllerImportTests(unittest.TestCase):
    def test_unchanged_job_bytes_and_real_kernel_cleanup_without_worker_exports(self):
        import hashlib,sys,time
        from uuid import uuid4
        from tests.fixtures.task120 import control_job,resources
        self.assertNotIn('app.worker',sys.modules)
        self.assertEqual(control_job.SOURCE_SHA256,hashlib.sha256(control_job.SOURCE.read_bytes()).hexdigest())
        self.assertEqual(Path(control_job.NamedJob.create.__code__.co_filename),control_job.SOURCE)
        with resources.root_job(str(uuid4())) as job:
            job.spawn_suspended([sys._base_executable,'-c','pass'],cwd=str(resources.ROOT))
            self.assertEqual(job.active_processes(),1)
            self.assertGreater(job.process_creation_time_100ns(),0)
            job.resume()
            self.assertTrue(job.wait_empty_until(time.monotonic_ns()+2_000_000_000))
            self.assertEqual(job.primary_exit_code(),0)

class MetadataSharingTests(unittest.TestCase):
    def test_actual_windows_reader_sharing_releases_without_new_bytes_or_reset(self):
        import threading,time
        from tests.fixtures.task120 import resources as r
        path=r.PRIVATE/'metadata-contention-probe.json'
        r.write(path,{'old':True})
        reader=path.open('r',encoding='utf-8')
        entered=threading.Event();outcome=[]
        def writer():
            entered.set()
            try:r.write(path,{'new':True});outcome.append('written')
            except BaseException as exc:outcome.append(type(exc).__name__)
        thread=threading.Thread(target=writer);thread.start();self.assertTrue(entered.wait(1))
        time.sleep(.05);reader.close();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertEqual(outcome,['written'])
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')),{'new':True})
