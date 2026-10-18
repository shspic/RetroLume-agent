"""Offline execution of the actual bootstrap guard; no PG or real fixture install."""
import os
import runpy
import socket
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch

class RepairBootstrapTests(unittest.TestCase):
    def test_actual_app_settings_with_sibling_data_and_backup_and_no_connection(self):
        from tests.fixtures.task100.control import ROOT
        from app.main import create_app
        data=ROOT/'backend/tests/data/task100/audit-repair-03/data'
        backups=ROOT/'backend/tests/data/task100/audit-repair-03/backups'
        data.mkdir(parents=True,exist_ok=True);backups.mkdir(parents=True,exist_ok=True)
        values={'RETROLUME_DATA_DIR':str(data),'RETROLUME_BACKUP_DIR':str(backups),
            'RETROLUME_DATABASE_URL':'host=127.0.0.1 port=55442 dbname=retrolume_task100_g8_main user=retrolume_task100_app',
            'RETROLUME_ACTIVITY_CONFIG':str(ROOT/'backend/tests/fixtures/task100/activity.synthetic.json'),
            'RETROLUME_TASK100_SYNTHETIC_KEY':'task100-synthetic-not-a-real-key'}
        with (patch.dict(os.environ,values),patch('psycopg.connect',side_effect=AssertionError('offline may not connect')),
              patch('psycopg.AsyncConnection.connect',side_effect=AssertionError('offline may not connect'))):
            app=create_app()
            self.assertIsNotNone(app.state.activities_ledger)
            self.assertTrue(app.state.activity_config.teaching_layer.available)
            self.assertEqual(app.state.originals.root,data/'originals')
            from fastapi.testclient import TestClient
            with TestClient(app) as client:
                response=client.get('/api/session')
                self.assertEqual(response.status_code,200)
                self.assertTrue(response.json()['storage_configured']);self.assertTrue(response.json()['token'])

    def test_actual_teaching_catalog_query_for_each_synthetic_exercise_and_feedback(self):
        from uuid import uuid4
        from app.retrieval.evidence import SourceTextUnit,_terms,MAX_QUERY_TERMS
        from app.learning.evidence import Unit
        from app.learning.teaching_evidence import assemble_teaching_catalog
        from app.learning.teaching_service import TeachingService
        from tests.fixtures.task100.synthetic_content import MATERIAL,GOAL,output_for
        from tests.fixtures.task100.seed_helpers import command
        source={'source_id':str(uuid4()),'version_id':str(uuid4()),'source_revision':1,'title':'bounded-offline.md',
                'format':'md','sha256':__import__('hashlib').sha256(MATERIAL.encode()).hexdigest()}
        unit=Unit(source,SourceTextUnit(source['source_id'],source['version_id'],1,None,'original',MATERIAL,True),None)
        plan_catalog=assemble_teaching_catalog(GOAL,(unit,),'a'*64)
        plan=output_for({'evidence':[{'id':e.citation_id,'text':e.text} for e in plan_catalog],'task':{'kind':'plan'}})
        for index,node in enumerate(plan['nodes'],1):
            nid='n'+str(index);node['node_id']=nid
        for nid in ('n1','n2','n3'):
            cmd=command(None,'exercise',{'confirmed':True,'path_record_id':str(uuid4()),'node_id':nid,
                'purpose':'initial','parent_feedback_record_id':None,'retry_of':None})
            query=TeachingService._context_query(cmd,{'teaching_query':GOAL},{'path_nodes':plan['nodes']})
            self.assertLessEqual(len(_terms(query)),MAX_QUERY_TERMS)
            catalog=assemble_teaching_catalog(query,(unit,),'b'*64)
            exercise=output_for({'evidence':[{'id':e.citation_id,'text':e.text} for e in catalog],
                'task':{'kind':'exercise','node_id':nid,'purpose':'initial'}})
            self.assertEqual(exercise['result_type'],'exercise')
            evaluation=command(None,'evaluate',{'confirmed':True,'exercise_record_id':str(uuid4()),
                'answer_record_id':str(uuid4()),'correction_record_id':None,'retry_of':None})
            query=TeachingService._context_query(evaluation,{'teaching_query':GOAL},{'exercise_projection':exercise})
            self.assertLessEqual(len(_terms(query)),MAX_QUERY_TERMS)
            catalog=assemble_teaching_catalog(query,(unit,),'c'*64)
            feedback=output_for({'evidence':[{'id':e.citation_id,'text':e.text} for e in catalog],
                'task':{'kind':'evaluate','exercise':exercise,'answer_text':'给定有限答案'}})
            self.assertEqual(feedback['result_type'],'feedback')

    def test_actual_current_permit_installs_and_ended_or_mismatched_permit_fails_closed(self):
        current='TASK-100-audit-repair-03-20261005';old='TASK-100-continuation-02-20261004'
        script=Path(__file__).parent/'fixtures/task100/bootstrap/sitecustomize.py'
        for fixture,permit,allowed in ((current,current,True),(old,current,False),(current,old,False)):
            install=Mock();exit_mock=Mock(side_effect=SystemExit(86))
            with (patch.dict(os.environ,{'RETROLUME_TASK100_FIXTURE':fixture,'RETROLUME_TASK100_PERMIT':permit}),
                  patch.dict('sys.modules',{'tests.fixtures.task100.fixture_runtime':SimpleNamespace(install=install)}),
                  patch.object(socket.socket,'connect',socket.socket.connect),
                  patch.object(socket.socket,'connect_ex',socket.socket.connect_ex),patch.object(os,'_exit',exit_mock)):
                if allowed:runpy.run_path(str(script));install.assert_called_once();exit_mock.assert_not_called()
                else:
                    with self.assertRaises(SystemExit) as rejection:runpy.run_path(str(script))
                    self.assertEqual(rejection.exception.code,86);install.assert_not_called()
