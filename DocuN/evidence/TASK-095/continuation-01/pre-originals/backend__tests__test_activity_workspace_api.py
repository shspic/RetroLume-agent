"""TASK-095 活动工作区 HTTP 契约：离线反例与真实 PostgreSQL 定向验证。

离线部分不访问数据库；PG 部分仅在存在专用测试 DSN
（RETROLUME_WORKSPACE_TEST_DATABASE_URL）时运行，不回退用户库。
继续动作的成功监督链由独立 Windows 批次（HTTP+替身传输）覆盖；本文件
只覆盖拒绝映射与既有事实读取，不触发真实模型传输。
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from fastapi.testclient import TestClient

from app.capabilities import build_business_payload
from app.main import create_app
from app.runtime import psycopg_compatible_loop_factory

# TestClient 的 anyio 门户在本进程创建事件循环；Windows 默认 Proactor 循环
# 与 psycopg 异步不兼容（产品运行使用 app.runtime 的 Selector 工厂），
# 因此测试进程同样固定为 Selector 策略，与产品启动口径一致。
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

DSN = os.environ.get("RETROLUME_WORKSPACE_TEST_DATABASE_URL", "")
DB_NAME = "retrolume_task095_g6"
ROLE = "retrolume_task095_synth"
APP_ROOT = Path(__file__).resolve().parents[2]


def good_config() -> dict:
    return {
        "model_identity": {"provider": "deepseek_chat_completions", "model": "synthetic-model-095"},
        "activity_defaults": {
            "deadline_hours": 24, "max_requests": 8, "max_cost_microunits": 800_000,
            "reserve_cost_microunits": 100_000, "max_request_bytes": 65536,
            "max_output_tokens": 256, "max_running_seconds": 600,
            "allowed_tools": [], "max_tool_calls": None,
        },
        "service": {
            "base_url": "https://api.deepseek.com", "thinking": "disabled",
            "timeout_seconds": 10, "max_output_tokens_limit": 8192,
            "max_request_bytes": 65536, "max_response_bytes": 65536,
        },
        "api_key_env": "RETROLUME_TEST095_KEY",
    }


class BaseApiTests(unittest.TestCase):
    with_key = False

    def setUp(self):
        self.data = tempfile.TemporaryDirectory()
        self.backup = tempfile.TemporaryDirectory()
        self.config_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.data.cleanup)
        self.addCleanup(self.backup.cleanup)
        self.addCleanup(self.config_dir.cleanup)
        config_path = Path(self.config_dir.name) / "activity.local.json"
        config_path.write_text(json.dumps(good_config(), ensure_ascii=False), encoding="utf-8")
        self.dsn = os.environ.get("RETROLUME_WORKSPACE_TEST_DATABASE_URL", "") if self.with_key else ""
        env = {
            "RETROLUME_DATA_DIR": self.data.name,
            "RETROLUME_BACKUP_DIR": self.backup.name,
            "RETROLUME_DATABASE_URL": self.dsn,
            "RETROLUME_ACTIVITY_CONFIG": str(config_path),
        }
        if self.with_key:
            env["RETROLUME_TEST095_KEY"] = "synthetic-placeholder-key"
        self.env = patch.dict(os.environ, env, clear=False)
        self.env.start()
        self.addCleanup(self.env.stop)
        if not self.with_key:
            os.environ.pop("RETROLUME_TEST095_KEY", None)
        self.client = TestClient(create_app())
        self.token = self.client.get("/api/session").json()["token"]
        self.headers = {"x-retrolume-session": self.token, "origin": "http://127.0.0.1:8000"}


class OfflineApiTests(BaseApiTests):
    def test_guard_rejections(self):
        for headers in (
            {"origin": "http://127.0.0.1:8000"},
            {**self.headers, "x-retrolume-session": "wrong"},
            {**self.headers, "origin": "https://evil.example"},
            {**self.headers, "sec-fetch-site": "cross-site"},
        ):
            self.assertEqual(self.client.get("/api/activities", headers=headers).status_code, 403)

    def test_own_origin_allowed_for_same_site_page(self):
        headers = {"x-retrolume-session": self.token, "origin": "http://testserver"}
        self.assertEqual(self.client.get("/api/activities/capabilities", headers=headers).status_code, 200)

    def test_capabilities_without_storage(self):
        body = self.client.get("/api/activities/capabilities", headers=self.headers).json()
        self.assertFalse(body["storage_ready"])
        self.assertEqual(body["storage_reason"], "database_not_configured")
        self.assertFalse(body["create"]["available"])
        self.assertFalse(body["continue"]["available"])
        self.assertEqual(body["continue"]["reason"], "provider_key_not_configured")
        self.assertEqual(body["quota_preview"]["max_requests"], 8)
        self.assertEqual(body["supervision_management_budget_seconds"], 120.0)
        self.assertEqual(body["window_seconds"], 90)
        self.assertEqual(body["followup_max_chars"], 4096)

    def test_reads_require_storage_with_distinguishable_codes(self):
        self.assertEqual(self.client.get("/api/activities", headers=self.headers).status_code, 503)
        code = self.client.get("/api/activities", headers=self.headers).json()["detail"]["code"]
        self.assertEqual(code, "database_not_configured")

    def test_input_validation_precedes_storage(self):
        bad = str(uuid4()) + "x"
        self.assertEqual(self.client.get(f"/api/activities/{bad}", headers=self.headers).status_code, 400)
        self.assertEqual(self.client.post(
            "/api/activities/not-a-uuid/cancel", headers=self.headers).status_code, 400)
        self.assertEqual(self.client.get(
            "/api/activities", params={"limit": 999}, headers=self.headers).status_code, 400)
        self.assertEqual(self.client.get(
            "/api/activities", params={"cursor": "!!!not-base64!!!"}, headers=self.headers).status_code, 400)
        self.assertEqual(self.client.post(
            "/api/activities", json={"activity_id": "nope", "source_ids": [str(uuid4())]},
            headers=self.headers).status_code, 400)
        self.assertEqual(self.client.post(
            "/api/activities", json={"activity_id": str(uuid4()), "source_ids": []},
            headers=self.headers).status_code, 422)
        self.assertEqual(self.client.post(
            "/api/activities", json={"activity_id": str(uuid4()), "source_ids": [str(uuid4())], "extra": 1},
            headers=self.headers).status_code, 422)

    def test_continue_layer_refused_without_key(self):
        response = self.client.post(
            f"/api/activities/{uuid4()}/continuations",
            json={"parent_operation_id": "P", "new_operation_id": "Q", "followup": "追问"},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"]["code"], "provider_key_not_configured")

    def test_continue_input_validation(self):
        body = {"parent_operation_id": "P", "new_operation_id": "Q", "followup": "x" * 4097}
        self.assertEqual(self.client.post(
            f"/api/activities/{uuid4()}/continuations", json=body, headers=self.headers).status_code, 400)
        body = {"parent_operation_id": "bad id!", "new_operation_id": "Q", "followup": "x"}
        self.assertEqual(self.client.post(
            f"/api/activities/{uuid4()}/continuations", json=body, headers=self.headers).status_code, 400)
        body = {"parent_operation_id": "P", "new_operation_id": "Q", "followup": "   "}
        self.assertEqual(self.client.post(
            f"/api/activities/{uuid4()}/continuations", json=body, headers=self.headers).status_code, 400)

    def test_error_bodies_do_not_leak_internals(self):
        text = self.client.get("/api/activities", headers=self.headers).text
        for needle in ("dsn", "password", "postgresql://", "Traceback"):
            self.assertNotIn(needle, text)


class PGReadLedger:
    """PG 场景下与批次测试共用的数据准备。"""


@unittest.skipUnless(DSN, "仅在 TASK-095 专用合成 PostgreSQL 中运行")
class PostgresApiTests(BaseApiTests):
    with_key = True

    def setUp(self):
        super().setUp()
        self.activity_ids = []
        self.sources = []
        self._run(self._prepare())

    def _run(self, coro):
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            return runner.run(coro)

    async def _rows(self, sql, params=()):
        async with await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row) as connection:
            return await (await connection.execute(sql, params)).fetchall()

    async def _sql(self, sql, params=()):
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(sql, params)

    async def _prepare(self):
        identity = (await self._rows("SELECT current_database() AS db, current_user AS role"))[0]
        self.assertEqual(identity, {"db": DB_NAME, "role": ROLE})
        await self._new_source()

    async def _new_source(self):
        source, version = str(uuid4()), str(uuid4())
        self.sources.append((source, version))
        await self._sql(
            "INSERT INTO material_sources(id,title,revision) VALUES (%s,'TASK095-api',0)", (source,))
        await self._sql(
            "INSERT INTO material_versions(id,source_id,filename,format,sha256,size)"
            " VALUES (%s,%s,'synthetic.md','md',%s,1)", (version, source, "8" * 64))
        await self._sql(
            "UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (version, source))
        return source, version

    def tearDown(self):
        async def cleanup():
            async with await psycopg.AsyncConnection.connect(DSN) as connection:
                for activity_id in self.activity_ids:
                    for table in ("activity_operation_results", "activity_operations",
                                  "activity_allowed_models", "activity_scope_sources"):
                        await connection.execute(
                            f"DELETE FROM {table} WHERE activity_id=%s", (activity_id,))
                    await connection.execute("DELETE FROM activities WHERE id=%s", (activity_id,))
                for source, _ in self.sources:
                    await connection.execute(
                        "UPDATE material_sources SET current_version=NULL WHERE id=%s", (source,))
                    await connection.execute(
                        "DELETE FROM material_versions WHERE source_id=%s", (source,))
                    await connection.execute("DELETE FROM material_sources WHERE id=%s", (source,))
        try:
            self._run(cleanup())
        finally:
            super().tearDown()

    def create_activity(self, sources=None):
        activity = str(uuid4())
        response = self.client.post(
            "/api/activities",
            json={"activity_id": activity, "source_ids": sources or [self.sources[0][0]]},
            headers=self.headers,
        )
        self.activity_ids.append(activity)
        return activity, response

    def seed_committed_parent(self, activity_id, key="P", extra_keys=()):
        async def seed():
            from app.activities import PostgresAdmissionLedger
            from app.capabilities import AdmissionIntent, CallContext, LedgerDisposition, LedgerOutcome, Provider
            ledger = PostgresAdmissionLedger(DSN)
            lease = await ledger.claim_lease(activity_id, "seed095", lease_seconds=120, window_seconds=30)
            for operation_key in (key, *extra_keys):
                intent = AdmissionIntent(
                    CallContext(activity_id=activity_id, operation_id=operation_key, executor_id=lease.executor_id,
                                execution_generation=lease.execution_generation,
                                scope_revision=lease.scope_revision),
                    Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model-095", 4096, 40, (),
                )
                permit = await ledger.admit(intent)
                await ledger.mark_dispatch_started(permit)
                fmt, payload, sha = build_business_payload(json_object={"reply": "synthetic-parent-095"})
                await ledger.record_outcome(permit, LedgerOutcome(
                    LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        self._run(seed())

    def test_capabilities_storage_ready(self):
        body = self.client.get("/api/activities/capabilities", headers=self.headers).json()
        self.assertTrue(body["storage_ready"])
        self.assertIsNone(body["storage_reason"])
        self.assertTrue(body["create"]["available"])
        self.assertTrue(body["continue"]["available"])

    def test_create_flow_and_idempotency(self):
        activity, response = self.create_activity()
        self.assertEqual(response.status_code, 200)
        body = response.json()["activity"]
        self.assertEqual(body["activity_id"], activity)
        self.assertEqual(body["status"], "pending")
        self.assertEqual(body["max_requests"], 8)
        self.assertEqual(body["source_count"], 1)
        self.assertTrue(body["sources"][0]["valid"])
        self.assertEqual(body["allowed_models"], [
            {"provider": "deepseek_chat_completions", "model": "synthetic-model-095"},
        ])
        again = self.client.post(
            "/api/activities",
            json={"activity_id": activity, "source_ids": [self.sources[0][0]]},
            headers=self.headers,
        )
        self.assertEqual(again.status_code, 409)
        self.assertEqual(again.json()["detail"]["code"], "activity_exists")
        not_ready_source = str(uuid4())
        self.sources.append((not_ready_source, str(uuid4())))
        self._run(self._sql(
            "INSERT INTO material_sources(id,title,revision) VALUES (%s,'pending',0)", (not_ready_source,)))
        pending = self.client.post(
            "/api/activities",
            json={"activity_id": str(uuid4()), "source_ids": [not_ready_source]},
            headers=self.headers,
        )
        self.assertEqual(pending.status_code, 409)
        self.assertEqual(pending.json()["detail"]["code"], "source_not_ready")

    def test_source_replaced_mapping(self):
        from app.activities import ActivityLedgerConflict
        ledger = self.client.app.state.activities_ledger
        with patch.object(
            ledger, "create_activity",
            side_effect=ActivityLedgerConflict("来源快照已撤销或被替换"),
        ):
            response = self.client.post(
                "/api/activities",
                json={"activity_id": str(uuid4()), "source_ids": [self.sources[0][0]]},
                headers=self.headers,
            )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"]["code"], "source_replaced")

    def test_list_detail_operations_shapes_hide_internals(self):
        activity, _ = self.create_activity()
        self.seed_committed_parent(activity)
        listing = self.client.get("/api/activities", headers=self.headers).json()
        item = next(entry for entry in listing["items"] if entry["activity_id"] == activity)
        self.assertEqual(item["status"], "running")
        self.assertEqual(item["requests_reserved"], 1)
        self.assertEqual(item["source_titles"], ["TASK095-api"])
        detail = self.client.get(f"/api/activities/{activity}", headers=self.headers).json()["activity"]
        self.assertEqual(detail["running_reserved_seconds"], 30)
        self.assertIn("last_settled_generation", detail)
        operations = self.client.get(
            f"/api/activities/{activity}/operations", headers=self.headers,
        ).json()
        row = operations["items"][0]
        self.assertEqual(row["operation_id"], "P")
        self.assertEqual(row["read_status"], "committed_current")
        self.assertTrue(row["payload_available"])
        self.assertIsNone(row["payload"], "列表不得携带正文")
        single = self.client.get(
            f"/api/activities/{activity}/operations/P", headers=self.headers,
        ).json()["operation"]
        self.assertEqual(single["payload"]["format"], "json")
        self.assertEqual(single["payload"]["value"]["reply"], "synthetic-parent-095")
        for needle in ("admission_id", "executor", "arguments_sha256", "tool_call_id",
                       "remote_request_id", "response_bytes"):
            self.assertNotIn(needle, json.dumps(detail, ensure_ascii=False))
            self.assertNotIn(needle, json.dumps(single, ensure_ascii=False))
        missing = self.client.get(
            f"/api/activities/{activity}/operations/absent", headers=self.headers)
        self.assertEqual(missing.status_code, 404)

    def test_cancel_idempotent_and_history(self):
        activity, _ = self.create_activity()
        first = self.client.post(f"/api/activities/{activity}/cancel", headers=self.headers)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["activity"]["status"], "cancelled")
        second = self.client.post(f"/api/activities/{activity}/cancel", headers=self.headers)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["activity"]["status"], "cancelled")
        missing = self.client.post(f"/api/activities/{uuid4()}/cancel", headers=self.headers)
        self.assertEqual(missing.status_code, 404)

    def test_continue_existing_key_facts_without_supervision(self):
        activity, _ = self.create_activity()
        self.seed_committed_parent(activity, "P", extra_keys=("S",))  # S 为非父的既有模型操作
        with patch("app.worker.one_call.run_one_call", side_effect=AssertionError("不得启动监督")):
            response = self.client.post(
                f"/api/activities/{activity}/continuations",
                json={"parent_operation_id": "P", "new_operation_id": "S", "followup": "同键"},
                headers=self.headers,
            )
            # 同键指向既有操作：只读返回既有事实，不进入监督。
            same_as_parent = self.client.post(
                f"/api/activities/{activity}/continuations",
                json={"parent_operation_id": "P", "new_operation_id": "P", "followup": "父键同键"},
                headers=self.headers,
            )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "committed_current")
        self.assertIsNone(response.json()["supervision"])
        self.assertEqual(same_as_parent.status_code, 400)

    def test_continue_refusals_do_not_start_supervision(self):
        activity, _ = self.create_activity()
        other = self.create_activity()[0]
        self.seed_committed_parent(other)  # 父在另一活动：本活动无此操作
        with patch("app.worker.one_call.run_one_call", side_effect=AssertionError("不得启动监督")):
            absent = self.client.post(
                f"/api/activities/{activity}/continuations",
                json={"parent_operation_id": "P", "new_operation_id": "Q1", "followup": "x"},
                headers=self.headers,
            )
            self.assertEqual(absent.status_code, 404, absent.text)
            cancelled_activity = self.create_activity()[0]
            self.seed_committed_parent(cancelled_activity)
            self.client.post(f"/api/activities/{cancelled_activity}/cancel", headers=self.headers)
            cancelled = self.client.post(
                f"/api/activities/{cancelled_activity}/continuations",
                json={"parent_operation_id": "P", "new_operation_id": "Q2", "followup": "x"},
                headers=self.headers,
            )
            self.assertEqual(cancelled.status_code, 409, cancelled.text)
            self.assertEqual(cancelled.json()["detail"]["code"], "activity_cancelled")
            # 父成果失效（来源被替换）
            self.seed_committed_parent(activity)
            self._run(self._sql(
                "UPDATE material_sources SET revision=revision+1 WHERE id=%s", (self.sources[0][0],)))
            invalid = self.client.post(
                f"/api/activities/{activity}/continuations",
                json={"parent_operation_id": "P", "new_operation_id": "Q3", "followup": "x"},
                headers=self.headers,
            )
            self.assertEqual(invalid.status_code, 409, invalid.text)
            self.assertEqual(invalid.json()["detail"]["code"], "source_invalid")
            self._run(self._sql(
                "UPDATE material_sources SET revision=revision-1 WHERE id=%s", (self.sources[0][0],)))
            # 损坏父正文 → integrity_error
            self._run(self._sql(
                "UPDATE activity_operation_results SET payload=%s WHERE activity_id=%s AND operation_id='P'",
                ('{"format":"json","value":{"tampered":true}}', activity)))
            corrupt = self.client.post(
                f"/api/activities/{activity}/continuations",
                json={"parent_operation_id": "P", "new_operation_id": "Q4", "followup": "x"},
                headers=self.headers,
            )
            self.assertEqual(corrupt.status_code, 409, corrupt.text)
            self.assertEqual(corrupt.json()["detail"]["code"], "integrity_error")

    def test_continue_input_too_large_mapping(self):
        activity, _ = self.create_activity()
        big_value = "长" * 30_000  # 多字节正文接近上限
        async def seed_big():
            from app.activities import PostgresAdmissionLedger
            from app.capabilities import AdmissionIntent, CallContext, LedgerDisposition, LedgerOutcome, Provider
            ledger = PostgresAdmissionLedger(DSN)
            lease = await ledger.claim_lease(activity, "seed095", lease_seconds=120, window_seconds=30)
            intent = AdmissionIntent(
                CallContext(activity_id=activity, operation_id="BIG", executor_id=lease.executor_id,
                            execution_generation=lease.execution_generation,
                            scope_revision=lease.scope_revision),
                Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model-095", 4096, 40, (),
            )
            permit = await ledger.admit(intent)
            await ledger.mark_dispatch_started(permit)
            fmt, payload, sha = build_business_payload(text=big_value)
            await ledger.record_outcome(permit, LedgerOutcome(
                LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        self._run(seed_big())
        with patch("app.worker.one_call.run_one_call", side_effect=AssertionError("不得启动监督")):
            response = self.client.post(
                f"/api/activities/{activity}/continuations",
                json={"parent_operation_id": "BIG", "new_operation_id": "Q5", "followup": "x"},
                headers=self.headers,
            )
        self.assertEqual(response.status_code, 413, response.text)
        self.assertEqual(response.json()["detail"]["code"], "input_too_large")

    def test_max_legal_payload_is_readable_through_http(self):
        activity, _ = self.create_activity()
        big_value = "长" * 43_000  # 约 129KB UTF-8，接近 131072 上限
        escape_value = "\\" * 60_000 + "\t\"引号\"\n"  # 转义敏感：反斜杠/引号/控制字符

        async def seed_big():
            from app.activities import PostgresAdmissionLedger
            from app.capabilities import AdmissionIntent, CallContext, LedgerDisposition, LedgerOutcome, Provider
            ledger = PostgresAdmissionLedger(DSN)
            lease = await ledger.claim_lease(activity, "seed095", lease_seconds=120, window_seconds=30)
            for key, text in (("MAX", big_value), ("MAXESC", escape_value)):
                intent = AdmissionIntent(
                    CallContext(activity_id=activity, operation_id=key, executor_id=lease.executor_id,
                                execution_generation=lease.execution_generation,
                                scope_revision=lease.scope_revision),
                    Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model-095", 4096, 40, (),
                )
                permit = await ledger.admit(intent)
                await ledger.mark_dispatch_started(permit)
                fmt, payload, sha = build_business_payload(text=text)
                await ledger.record_outcome(permit, LedgerOutcome(
                    LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        self._run(seed_big())
        for key, expected in (("MAX", big_value), ("MAXESC", escape_value)):
            response = self.client.get(
                f"/api/activities/{activity}/operations/{key}", headers=self.headers,
            )
            self.assertEqual(response.status_code, 200)
            value = response.json()["operation"]["payload"]["value"]
            self.assertEqual(value, expected, key)

    def test_bad_cursor_shapes(self):
        self.assertEqual(self.client.get(
            "/api/activities", params={"cursor": "AAAA"}, headers=self.headers).status_code, 400)
        self.assertEqual(self.client.get(
            "/api/activities", params={"cursor": "!!!not-base64!!!"}, headers=self.headers).status_code, 400)


if __name__ == "__main__":
    unittest.main()
