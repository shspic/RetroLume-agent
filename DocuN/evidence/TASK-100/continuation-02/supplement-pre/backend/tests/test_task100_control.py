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
        self.assertIn('min(1800,remaining)',text)

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
