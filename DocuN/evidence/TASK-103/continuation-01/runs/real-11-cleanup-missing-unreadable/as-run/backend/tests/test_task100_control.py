"""有限运行器已见控制故障的离线反例，不签真实 PG/进程行为。"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
from tests.fixtures.task100.control import *

class RunnerControlTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='task100-control-')
        self.addCleanup(self.temp.cleanup)
        self.ledger=Ledger(Path(self.temp.name)/'ledger.json')
        self.preparation={'active_started_at':utc()}
    def fresh(self): self.ledger.initialize(self.preparation);return self.ledger.load()
    def test_missing_and_corrupt_ledger_never_reset(self):
        with self.assertRaises(ControlRefusal): self.ledger.load()
        self.ledger.path.write_text('{invalid',encoding='utf-8')
        with self.assertRaises(ControlRefusal): self.ledger.load()
        self.assertEqual(self.ledger.path.read_text(),'{invalid')
        with self.assertRaises(ControlRefusal): self.ledger.initialize(self.preparation)
    def test_negative_boolean_and_nonfinite_rejected(self):
        self.fresh()
        for domain,key,bad in [('counts','real_entries',-1),('counts','real_entries',True),('seconds','real',False),('seconds','real',-1)]:
            value=self.ledger.load();value[domain][key]=bad;atomic_json(self.ledger.path,value)
            with self.assertRaises(ControlRefusal):self.ledger.load()
            value[domain][key]=0;atomic_json(self.ledger.path,value)
    def test_actions_count_before_failure_and_limit_prevents_next_action(self):
        self.fresh();actions=[]
        for _ in range(3):
            self.ledger.consume('container_starts'); actions.append('start_attempt_failed')
        with self.assertRaises(ControlRefusal):self.ledger.consume('container_starts');actions.append('illegal_start')
        self.assertEqual(len(actions),3);self.assertEqual(self.ledger.load()['counts']['container_starts'],3)
    def test_dsn_url_and_keywords_preserve_password(self):
        from psycopg.conninfo import conninfo_to_dict
        examples=["host=127.0.0.1 port=55442 dbname=postgres user=test password='sp ace:x'",
            'postgresql://test@127.0.0.1:55442/postgres?password=sp%20ace%3Ax']
        for text in examples:
            for db in (MAIN_DB,FAULT_DB):
                result=conninfo_to_dict(switched_dsn(text,db))
                self.assertEqual(result['dbname'],db);self.assertEqual(result['password'],'sp ace:x')
        with self.assertRaises(ControlRefusal):switched_dsn(examples[0],'user_database')
    def test_deadline_is_cumulative_monotonic_and_stage_minimum(self):
        now=[100.0];d=Deadline(30,lambda:now[0]);self.assertEqual(d.timeout(50),30)
        now[0]+=23;self.assertEqual(d.timeout(10),7)
        now[0]+=7
        with self.assertRaises(ControlRefusal):d.timeout(1)
    def test_blocked_skip_and_not_run_cannot_aggregate_pass(self):
        for state in ('blocked','skip','not_run','timeout','started_failed','fail'):
            self.assertEqual(aggregate([{'status':'pass'},{'status':state}]),'fail')
        self.assertEqual(aggregate([]),'fail')
    def test_dependency_failure_does_not_call_downstream(self):
        from tests.fixtures.task100.runner import Batch
        with patch('tests.fixtures.task100.runner.EVIDENCE',Path(self.temp.name)):
            batch=Batch('offline-control',Deadline(10));called=[]
            batch.stage('upstream',lambda:{'status':'blocked'})
            result=batch.stage('downstream',lambda:called.append(True),('upstream',))
            self.assertEqual(result['status'],'not_run');self.assertEqual(called,[])
    def test_timeout_and_logging_exception_still_close_created_process(self):
        process=MagicMock(); process.poll.return_value=None;process.pid=0
        process.communicate.side_effect=subprocess.TimeoutExpired('fixture',1)
        process.returncode=1
        with patch('tests.fixtures.task100.control.subprocess.Popen',return_value=process),patch('tests.fixtures.task100.control.subprocess.run'):
            result=run_process(['fixture'],Deadline(2),1,Path(self.temp.name)/'run')
        self.assertEqual(result['status'],'timeout');self.assertTrue(process.kill.called);self.assertTrue(process.wait.called)
    def test_execution_entries_names_loop_factory_and_build_are_real(self):
        from tests.fixtures.task100 import runner
        from tests.fixtures.task100.support import PGBase
        import inspect
        self.assertIn('loop_factory=psycopg_compatible_loop_factory',inspect.getsource(PGBase))
        text=inspect.getsource(runner)
        self.assertIn("'npm','run','build'",text)
        self.assertLess(text.index("ledger.consume('real_entries'"),text.index("batch.stage('container'"))
        self.assertIn('/api/session',text);self.assertIn('RETROLUME_DATABASE_URL',text)
    def test_rejects_wrong_resource_identity(self):
        fact={'Id':'other','Name':NAME,'Image':IMAGE,'HostConfig':{},'Mounts':[]}
        with self.assertRaises(ControlRefusal):validate_container(fact)
    def test_cleanup_is_finally_even_when_real_stage_raises(self):
        from tests.fixtures.task100 import runner
        import inspect
        text=inspect.getsource(runner.actual_main)
        self.assertIn('finally: batch.cleanup()',text)
        self.assertIn('min(1800,remaining,active_remaining(value))',text)

    def granted(self):
        value=self.fresh()
        value['counts'].update(real_entries=3,container_starts=3,app_starts=1,frontend_build=1)
        value['seconds']['active']=1000
        grant={'id':SUPPLEMENT_ID,'approval':SUPPLEMENT_APPROVAL,'additional_counts':{'real_entries':2,'container_starts':2},
            'active_seconds':10800,'active_started_at':utc(),'initial_read_upper_seconds':0,'all_other_limits_unchanged':True,
            'baseline_counts':dict(value['counts']),'baseline_seconds':dict(value['seconds'])}
        value['supplementary_permit']=grant;atomic_json(self.ledger.path,value)
        return grant

    def test_supplement_adds_only_two_attempts_without_resetting_or_extra_build(self):
        grant=self.granted()
        self.assertEqual(self.ledger.load()['counts']['real_entries'],3)
        for _ in range(2):self.ledger.consume('real_entries');self.ledger.consume('container_starts')
        for name in ('real_entries','container_starts','frontend_build'):
            with self.assertRaises(ControlRefusal):self.ledger.consume(name)
        self.assertEqual(self.ledger.load()['counts']['real_entries'],5)
        value=self.ledger.load();value['supplementary_permit']['additional_counts']['sup_creates']=1
        atomic_json(self.ledger.path,value)
        with self.assertRaises(ControlRefusal):self.ledger.load()

    def test_supplement_uses_bounded_new_active_segment_preserving_old_seconds(self):
        from datetime import datetime,timedelta
        grant=self.granted();start=datetime.fromisoformat(grant['active_started_at'])
        value=self.ledger.checkpoint_active(start+timedelta(seconds=30))
        self.assertEqual(value['seconds']['active'],1030)
        self.assertEqual(self.ledger.checkpoint_active(start+timedelta(seconds=5))['seconds']['active'],1030)
        with self.assertRaises(ControlRefusal):self.ledger.checkpoint_active(start+timedelta(seconds=10801))

    def test_browser_extra_attempt_requires_separate_explicit_permit_and_preserves_other_limits(self):
        self.granted();value=self.ledger.load()
        value['counts'].update(real_entries=4,container_starts=4,app_starts=2,sup_creates=21,browser=2,driver=2)
        atomic_json(self.ledger.path,value)
        with self.assertRaises(ControlRefusal):self.ledger.consume('browser')
        value['browser_supplementary_permit']={'id':BROWSER_SUPPLEMENT_ID,'approval':'offline synthetic approval only',
            'additional_counts':{'browser':1},'all_other_limits_unchanged':True,'baseline_counts':dict(value['counts'])}
        atomic_json(self.ledger.path,value)
        self.ledger.consume('browser')
        with self.assertRaises(ControlRefusal):self.ledger.consume('browser')
        self.assertEqual(effective_limits(self.ledger.load()),LIMITS|{'real_entries':5,'container_starts':5,'browser':3})
        value=self.ledger.load();value['browser_supplementary_permit']['additional_counts']['driver']=1
        atomic_json(self.ledger.path,value)
        with self.assertRaises(ControlRefusal):self.ledger.load()

    def test_windows_inheritance_requires_original_pass_cleanup_and_matching_product(self):
        from tests.fixtures.task100.runner import inherit_windows,WINDOWS_INHERIT_BATCH
        directory=Path(self.temp.name)/WINDOWS_INHERIT_BATCH
        current={'backend/app/learning/teaching_service.py':'synthetic product digest'}
        outcome={'active_processes_at_end':0,'cleanup_incomplete':False,'manager_pid':1,'manager_created_100ns':2,
            'worker_created_100ns':3,'job_name':'offline synthetic job'}
        saved={'summary.json':{'segments':[{'name':'windows','status':'pass'},{'name':'browser','status':'fail'}]},
            'cleanup.json':{'status':'pass'},'as-run-files.json':current,
            'windows-facts.json':{'cases':[{'status':'pass'}]*8,'session_outcomes':[outcome]*17,'provider_real':False,'user_program_executed':False},
            'browser-input.json':{'activity_id':'offline synthetic activity','title':'offline fixture'},'browser-main/facts.json':{'status':'pass'}}
        for name,value in saved.items():atomic_json(directory/name,value)
        self.assertEqual(inherit_windows(WINDOWS_INHERIT_BATCH,current,Path(self.temp.name))['session_outcomes'],17)
        with self.assertRaises(ControlRefusal):inherit_windows('../unrelated',current,Path(self.temp.name))
        with self.assertRaises(ControlRefusal):inherit_windows(WINDOWS_INHERIT_BATCH,{next(iter(current)):'changed'},Path(self.temp.name))
        atomic_json(directory/'cleanup.json',{'status':'unconfirmed'})
        with self.assertRaises(ControlRefusal):inherit_windows(WINDOWS_INHERIT_BATCH,current,Path(self.temp.name))

    def test_documentation_only_archive_change_does_not_relax_runtime_or_offline_identity(self):
        from tests.fixtures.task100.runner import verify_run_files
        before={'README.md':'before archive navigation','backend/app/main.py':'same runtime'}
        after=before|{'README.md':'after archive navigation'}
        events=[{'event':'offline_batch_pass','detail':{'files':before}}]
        self.assertEqual(verify_run_files(after,before,events)[0]['as_run_sha256'],'after archive navigation')
        with self.assertRaises(ControlRefusal):verify_run_files(after|{'backend/app/main.py':'runtime drift'},before,events)
        with self.assertRaises(ControlRefusal):verify_run_files(after,before,[])

    def test_counted_preflight_needs_separate_entry_permit_without_reset_or_extra_resource(self):
        self.granted();value=self.ledger.load()
        value['counts'].update(real_entries=5,container_starts=4,app_starts=2,sup_creates=21,browser=2,driver=2)
        baseline=dict(value['counts'])
        value['browser_supplementary_permit']={'id':BROWSER_SUPPLEMENT_ID,'approval':'offline synthetic only',
            'additional_counts':{'browser':1},'all_other_limits_unchanged':True,'baseline_counts':baseline|{'real_entries':4}}
        atomic_json(self.ledger.path,value)
        with self.assertRaises(ControlRefusal):self.ledger.consume('real_entries')
        value['preflight_supplementary_permit']={'id':PREFLIGHT_SUPPLEMENT_ID,'approval':'offline synthetic only',
            'additional_counts':{'real_entries':1},'all_other_limits_unchanged':True,'baseline_counts':baseline}
        atomic_json(self.ledger.path,value)
        self.ledger.consume('real_entries')
        with self.assertRaises(ControlRefusal):self.ledger.consume('real_entries')
        self.assertEqual(effective_limits(self.ledger.load()),LIMITS|{'real_entries':6,'container_starts':5,'browser':3})

    def test_existing_roles_and_database_are_verified_before_changes(self):
        from tests.fixtures.task100 import pg_setup
        conn=MagicMock();conn.__enter__.return_value=conn
        conn.execute.return_value.fetchone.side_effect=[{'rolsuper':True},*sum(([dict(rolsuper=False,rolcreatedb=False,rolcreaterole=False,rolreplication=False,rolbypassrls=False),{'n':0}] for _ in ROLES),[])]
        with patch.object(pg_setup,'connection',return_value=conn):pg_setup.create_roles('offline synthetic connection',{role:'offline synthetic password' for role in ROLES})
        self.assertEqual(conn.execute.call_count,10)
        conn=MagicMock();conn.__enter__.return_value=conn;conn.execute.return_value.fetchone.return_value={'owner':ROLES[0]}
        with patch.object(pg_setup,'connection',return_value=conn):pg_setup.create_database('offline',MAIN_DB)
        self.assertEqual(conn.execute.call_count,1)
        conn.execute.return_value.fetchone.return_value={'owner':'other_owner'}
        with patch.object(pg_setup,'connection',return_value=conn),self.assertRaises(ControlRefusal):pg_setup.create_database('offline',MAIN_DB)

    def test_rollback_after_failed_transaction_does_not_set_config(self):
        from tests.fixtures.task100 import pg_setup
        conn=MagicMock()
        with patch.object(pg_setup,'DEADLINE',Deadline(10)):
            pg_setup.BoundedConnection(conn).execute('ROLLBACK')
        conn.execute.assert_called_once_with('ROLLBACK')

    def test_cleanup_ledger_failure_cannot_skip_container_or_ports(self):
        from tests.fixtures.task100 import runner
        # 控制替身仅模拟 Docker/端口，不接触引擎或业务数据库。
        with patch.object(runner,'EVIDENCE',Path(self.temp.name)):
            batch=runner.Batch('cleanup-control',Deadline(10));batch.started_container=True
            docker=MagicMock();docker.returncode=0;docker.stdout=json.dumps([{}])
            sock=MagicMock();sock.__enter__.return_value=sock;sock.connect_ex.return_value=1
            with patch.object(runner.subprocess,'run',return_value=docker),patch.object(runner,'validate_container'),patch.object(runner.socket,'socket',return_value=sock),patch.object(runner,'Ledger') as ledger:
                ledger.return_value.charge.side_effect=OSError('offline evidence failure')
                batch.cleanup()
            saved=json.loads((batch.directory/'cleanup.json').read_text(encoding='utf-8'))
            self.assertEqual(saved['status'],'fail')
            self.assertTrue(any(f['action']=='exact_container_stop' for f in saved['facts']))
            self.assertEqual(sum(f.get('action')=='port_check' for f in saved['facts']),2)
            self.assertTrue(any(f.get('action')=='cleanup_ledger' for f in saved['facts']))
