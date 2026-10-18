"""097真实PG支撑的HTTP前置拒绝与只读兼容，不启动Windows调用。"""
import asyncio
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import create_app
from tests.fixtures.task097.support import DSN, Fixture, ROOT
from tests.fixtures.task097.samples import ENGLISH
from tests.test_learning_config import config
from app.runtime import psycopg_compatible_loop_factory

if sys.platform=="win32":asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class LearningAPITests(unittest.TestCase):
    def setUp(self):
        if not DSN:self.skipTest("097专用合成DSN未注入")
        self.root=ROOT/"DocuN/evidence/TASK-097/runtime/http-fixture"
        data=self.root/"data";backup=self.root/"backup"
        data.mkdir(parents=True,exist_ok=True);backup.mkdir(parents=True,exist_ok=True)
        originals=data/"originals";originals.mkdir(exist_ok=True)
        self.configpath=self.root/"synthetic-config.json"
        self.configpath.write_text(json.dumps(config()),encoding="utf-8")
        self.env=patch.dict(os.environ,{"RETROLUME_DATA_DIR":str(data),"RETROLUME_BACKUP_DIR":str(backup),
            "RETROLUME_DATABASE_URL":DSN,"RETROLUME_ACTIVITY_CONFIG":str(self.configpath),"RETROLUME_TEST097_KEY":"synthetic"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.app=create_app();self.client=TestClient(self.app)
        self.addCleanup(self.client.close)
        self.headers={"X-RetroLume-Session":self.app.state.session_token}
        self.fixture=Fixture(DSN,originals)
        self.addCleanup(self.fixture.cleanup)
        self.source=self.fixture.text(ENGLISH)
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as r:
            self.activity=r.run(self.fixture.activity([self.source]))
    def post(self,body):
        return self.client.post(f"/api/activities/{self.activity}/learning/first",json=body,headers=self.headers)
    def test_request_scope_authority_and_confirmation_refused_before_launcher(self):
        body={"business_key":str(uuid4()),"goal":"Explain atomicity","confirmed":True}
        with patch("app.learning.service.run_one_call",side_effect=AssertionError("不应启动")):
            for patch_value in [{"confirmed":False},{"goal":""},{"goal":"x"*1025},{"sources":[self.source["id"]]},
                {"scope_revision":1},{"profile":"learning.v1"},{"ready":True},{"system":"run tools"},
                {"budget":100},{"path":"C:/private.txt"}]:
                response=self.post(body|patch_value)
                self.assertIn(response.status_code,{400,413,422})
            self.assertEqual(self.post(body|{"goal":"outside_not_present"}).json()["precheck"]["kind"],"no_evidence")
        self.assertEqual(self.fixture.rows("SELECT requests_reserved FROM activities WHERE id=%s",(self.activity,))[0]["requests_reserved"],0)
        self.assertEqual(self.fixture.rows("SELECT count(*) AS n FROM activity_operations WHERE activity_id=%s",(self.activity,))[0]["n"],0)
    def test_layers_l0_l1_l2_and_budget_preflight(self):
        from dataclasses import replace
        from app.service_config import LayerState
        caps=self.client.get("/api/activities/capabilities",headers=self.headers).json()
        self.assertTrue(caps["learning"]["available"])
        for reason in ["learning_not_configured","learning_config_invalid","provider_key_not_configured"]:
            before=self.app.state.activity_config
            self.app.state.activity_config=replace(before,learning_layer=LayerState(False,reason),learning_output_tokens=None)
            response=self.post({"business_key":str(uuid4()),"goal":"atomicity","confirmed":True})
            self.assertEqual(response.status_code,503)
            self.assertEqual(self.client.get(f"/api/activities/{self.activity}",headers=self.headers).status_code,200)
            self.app.state.activity_config=before
        self.fixture.rows("UPDATE activities SET max_request_bytes=1024 WHERE id=%s",(self.activity,))
        response=self.post({"business_key":str(uuid4()),"goal":"atomicity","confirmed":True})
        self.assertEqual(response.status_code,413)
        self.assertEqual(response.json()["detail"]["code"],"learning_context_limit")
        self.assertEqual(self.fixture.rows("SELECT requests_reserved FROM activities WHERE id=%s",(self.activity,))[0]["requests_reserved"],0)
        self.assertEqual(self.client.post(f"/api/activities/{self.activity}/cancel",headers=self.headers).status_code,200)
        self.assertEqual(self.client.get(f"/api/activities/{self.activity}",headers=self.headers).json()["activity"]["status"],"cancelled")
    def test_read_missing_intent_and_single_origin_write_rules(self):
        key=str(uuid4())
        path=f"/api/activities/{self.activity}/learning/intents/{key}?action=first"
        self.assertEqual(self.client.get(path,headers=self.headers).json(),{"operation":None})
        response=self.client.post(f"/api/activities/{self.activity}/learning/first",headers=self.headers|{"Origin":"https://outside.invalid"},
            json={"business_key":key,"goal":"atomicity","confirmed":True})
        self.assertEqual(response.status_code,403)
        created=str(uuid4())
        self.fixture.activities.append(created)
        response=self.client.post("/api/activities",headers=self.headers,
            json={"activity_id":created,"source_ids":[self.source["id"]]})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["activity"]["activity_id"],created)
        self.assertEqual(self.fixture.rows("SELECT requests_reserved,cost_reserved_microunits FROM activities WHERE id=%s",(created,))[0],
            {"requests_reserved":0,"cost_reserved_microunits":0})
