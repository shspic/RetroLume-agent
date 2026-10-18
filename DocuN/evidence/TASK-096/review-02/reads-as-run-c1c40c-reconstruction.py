"""TASK-095 活动工作区读取投影：真实 PostgreSQL 定向验证。

仅在存在专用测试 DSN（RETROLUME_WORKSPACE_TEST_DATABASE_URL）时运行；
缺失即明确跳过，绝不回退任何用户 DSN。每例使用全新合成活动/来源，清理
只定向删除本例如创建的行。读取方法全部单条 SQL；绑定判定与
read_committed_result 同源。
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import unittest
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from app.activities import (
    ActivitySpec,
    PostgresAdmissionLedger,
    ResultIntegrityError,
    ResultReadStatus,
    SourceSnapshot,
)
from app.capabilities import (
    AdmissionIntent,
    CallContext,
    LedgerDisposition,
    LedgerOutcome,
    Provider,
    build_business_payload,
)
from app.runtime import psycopg_compatible_loop_factory

DSN = os.environ.get("RETROLUME_WORKSPACE_TEST_DATABASE_URL", "")
DB_NAME = "retrolume_task095_g6"
ROLE = "retrolume_task095_synth"


class CountingLedger(PostgresAdmissionLedger):
    """统计一次读取调用实际执行的 SQL 条数与真实返回列；用于单条 SQL
    快照与"列表投影不向数据库请求正文"合同的运行时观察（非 SQL 字符串断言）。"""

    count = 0
    columns: list[list[str]] = []

    async def _transaction(self, operation):
        calls: list[object] = []
        columns: list[list[str]] = []

        async def wrapped(connection):
            class _Proxy:
                def __init__(self, inner):
                    self._inner = inner

                def __getattr__(self, name):
                    return getattr(self._inner, name)

                async def execute(self, *args, **kwargs):
                    calls.append(args[0] if args else None)
                    cursor = await self._inner.execute(*args, **kwargs)
                    description = getattr(cursor, "description", None)
                    columns.append([] if description is None else [item.name for item in description])
                    return cursor

            return await operation(_Proxy(connection))

        result = await super()._transaction(wrapped)
        self.count = len(calls)
        self.columns = columns
        return result


class PGBase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self) -> None:
        self._asyncioRunner = asyncio.Runner(
            debug=True, loop_factory=psycopg_compatible_loop_factory,
        )

    async def asyncSetUp(self):
        self.activity_ids: list[str] = []
        self.sources: list[tuple[str, str]] = []
        self.ledger = PostgresAdmissionLedger(DSN)
        identity = await self.row("SELECT current_database() AS db, current_user AS role")
        self.assertEqual(identity, {"db": DB_NAME, "role": ROLE})
        self.source = await self.new_source()
        self.activity = str(uuid4())
        self.activity_ids.append(self.activity)
        await self.ledger.create_activity(ActivitySpec(
            self.activity, (self.source,),
            datetime.now(timezone.utc) + timedelta(minutes=30),
            8, 800_000, 100_000, 65536, 256, 600,
            (("deepseek_chat_completions", "synthetic-model-095"),),
        ))

    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            for activity_id in self.activity_ids:
                for table in (
                    "activity_operation_results", "activity_operations",
                    "activity_allowed_models", "activity_scope_sources",
                ):
                    await connection.execute(
                        f"DELETE FROM {table} WHERE activity_id=%s", (activity_id,),
                    )
                await connection.execute("DELETE FROM activities WHERE id=%s", (activity_id,))
            for source, _version in self.sources:
                await connection.execute(
                    "UPDATE material_sources SET current_version=NULL WHERE id=%s", (source,),
                )
                await connection.execute("DELETE FROM material_versions WHERE source_id=%s", (source,))
                await connection.execute("DELETE FROM material_sources WHERE id=%s", (source,))

    async def rows(self, sql, params=()):
        async with await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row) as connection:
            return await (await connection.execute(sql, params)).fetchall()

    async def row(self, sql, params=()):
        return (await self.rows(sql, params))[0]

    async def sql(self, sql, params=()):
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(sql, params)

    async def new_source(self) -> SourceSnapshot:
        source, version = str(uuid4()), str(uuid4())
        self.sources.append((source, version))
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "INSERT INTO material_sources(id,title,revision) VALUES (%s,'TASK095-synthetic',0)", (source,),
            )
            await connection.execute(
                "INSERT INTO material_versions(id,source_id,filename,format,sha256,size)"
                " VALUES (%s,%s,'synthetic.txt','txt',%s,1)", (version, source, "8" * 64),
            )
            await connection.execute(
                "UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (version, source),
            )
        return SourceSnapshot(source, version, 1)

    async def new_activity(self, sources=None) -> str:
        activity = str(uuid4())
        self.activity_ids.append(activity)
        await self.ledger.create_activity(ActivitySpec(
            activity, (sources or self.source,),
            datetime.now(timezone.utc) + timedelta(minutes=30),
            8, 800_000, 100_000, 65536, 256, 600,
            (("deepseek_chat_completions", "synthetic-model-095"),),
        ))
        return activity

    async def claim(self, activity_id=None):
        return await self.ledger.claim_lease(
            activity_id or self.activity, "executor095", lease_seconds=120, window_seconds=30,
        )

    def intent(self, lease, key, activity_id=None):
        return AdmissionIntent(
            CallContext(
                activity_id=activity_id or self.activity, operation_id=key,
                executor_id=lease.executor_id,
                execution_generation=lease.execution_generation,
                scope_revision=lease.scope_revision,
            ),
            Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model-095", 4096, 40, (),
        )

    async def committed_parent(self, key="P", *, activity_id=None, lease=None):
        lease = lease or await self.claim(activity_id)
        permit = await self.ledger.admit(self.intent(lease, key, activity_id))
        await self.ledger.mark_dispatch_started(permit)
        fmt, payload, sha = build_business_payload(json_object={"reply": "synthetic-parent-095"})
        await self.ledger.record_outcome(
            permit, LedgerOutcome(LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha),
        )
        return permit


@unittest.skipUnless(DSN, "仅在 TASK-095 专用合成 PostgreSQL 中运行")
class ReadProjectionTests(PGBase):
    async def test_reads_are_single_statement(self):
        await self.committed_parent()
        ledger = CountingLedger(DSN)
        await ledger.read_activity_facts(self.activity)
        self.assertEqual(ledger.count, 1, "活动详情必须恰一条 SQL")
        await ledger.list_activities(limit=10)
        self.assertEqual(ledger.count, 1, "活动列表必须恰一条 SQL")
        await ledger.list_operations(self.activity, limit=10)
        self.assertEqual(ledger.count, 1, "操作列表必须恰一条 SQL")
        self.assertNotIn("payload", ledger.columns[-1], "列表投影必须不向数据库请求正文列（真实返回列观察）")
        await ledger.read_operation(self.activity, "P")
        self.assertEqual(ledger.count, 1, "单操作必须恰一条 SQL")
        await ledger.read_committed_result(self.activity, "P")
        self.assertEqual(ledger.count, 1, "既有单结果读取必须恰一条 SQL")

    async def test_read_consistent_under_concurrent_uncommitted_write(self):
        connection = await psycopg.AsyncConnection.connect(DSN, autocommit=False)
        try:
            await connection.execute(
                "UPDATE activities SET requests_reserved=requests_reserved+1 WHERE id=%s", (self.activity,),
            )
            fact = await self.ledger.read_activity_facts(self.activity)
            self.assertEqual(fact.requests_reserved, 0, "未提交写入不得进入读取快照")
            await connection.rollback()
        finally:
            await connection.close()
        fact = await self.ledger.read_activity_facts(self.activity)
        self.assertEqual(fact.requests_reserved, 0)

    async def test_activity_facts_fields_and_source_validity(self):
        fact = await self.ledger.read_activity_facts(self.activity)
        self.assertEqual(fact.activity_id, self.activity)
        self.assertEqual(fact.status, "pending")
        self.assertEqual(fact.max_requests, 8)
        self.assertEqual(fact.requests_reserved, 0)
        self.assertEqual(fact.max_running_seconds, 600)
        self.assertIsNone(fact.max_tool_calls)
        self.assertEqual(fact.allowed_models, (("deepseek_chat_completions", "synthetic-model-095"),))
        self.assertEqual(len(fact.sources), 1)
        self.assertEqual(fact.sources[0].source_id, self.source.source_id)
        self.assertTrue(fact.sources[0].valid)
        await self.sql(
            "UPDATE material_sources SET revision=revision+1 WHERE id=%s", (self.source.source_id,),
        )
        updated = await self.ledger.read_activity_facts(self.activity)
        self.assertFalse(updated.sources[0].valid)
        self.assertIsNone(await self.ledger.read_activity_facts(str(uuid4())))

    async def test_activity_list_pagination_cursor(self):
        second = await self.new_activity()
        third = await self.new_activity()
        first_page = await self.ledger.list_activities(limit=2)
        self.assertEqual(len(first_page), 2)
        anchor = first_page[-1]
        second_page = await self.ledger.list_activities(
            limit=2, after_created_at=anchor.created_at, after_activity_id=anchor.activity_id,
        )
        seen = [item.activity_id for item in first_page] + [item.activity_id for item in second_page]
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(set(seen), {self.activity, second, third})
        keys = [
            (item.created_at, item.activity_id)
            for item in list(first_page) + list(second_page)
        ]
        self.assertEqual(keys, sorted(keys, reverse=True))
        with self.assertRaises(ValueError):
            await self.ledger.list_activities(limit=2, after_created_at=anchor.created_at)
        with self.assertRaises(ValueError):
            await self.ledger.list_activities(limit=0)
        with self.assertRaises(ValueError):
            await self.ledger.list_activities(limit=201)

    async def test_operations_projection_statuses_and_payload_boundary(self):
        lease = await self.claim()
        await self.committed_parent("P", lease=lease)
        unknown = await self.ledger.admit(self.intent(lease, "U"))
        await self.ledger.mark_dispatch_started(unknown)
        await self.sql(
            "UPDATE activity_operations SET state='unknown', disposition='unknown', recorded_at=CURRENT_TIMESTAMP"
            " WHERE activity_id=%s AND operation_id='U'", (self.activity,),
        )
        not_sent = await self.ledger.admit(self.intent(lease, "N"))
        await self.ledger.mark_dispatch_started(not_sent)
        await self.sql(
            "UPDATE activity_operations SET state='not_sent', disposition='not_sent', recorded_at=CURRENT_TIMESTAMP"
            " WHERE activity_id=%s AND operation_id='N'", (self.activity,),
        )
        tool_payload = '{"format":"text","value":"3"}'
        tool_sha = hashlib.sha256(tool_payload.encode("utf-8")).hexdigest()
        admission_id = str(uuid4())
        await self.sql(
            "INSERT INTO activity_operations(activity_id, operation_id, admission_id, executor_id,"
            " execution_generation, scope_revision, tool_names, reserved_cost_microunits, kind,"
            " arguments_sha256, tool_call_id, state, disposition, recorded_at)"
            " VALUES (%s,'T1',%s,'executor095',0,1,ARRAY['finite_calculate']::VARCHAR(64)[],0,'tool',"
            " %s,'t1','received','received',CURRENT_TIMESTAMP)",
            (self.activity, admission_id, "a" * 64),
        )
        await self.sql(
            "INSERT INTO activity_operation_results(activity_id, operation_id, admission_id,"
            " execution_generation, scope_revision, payload_format, payload, payload_sha256)"
            " VALUES (%s,'T1',%s,0,1,'text',%s,%s)",
            (self.activity, admission_id, tool_payload, tool_sha),
        )
        rows = {item.operation_id: item for item in await self.ledger.list_operations(self.activity, limit=100)}
        self.assertEqual(set(rows), {"P", "U", "N", "T1"})
        self.assertEqual(rows["P"].read_status, ResultReadStatus.COMMITTED_CURRENT)
        self.assertTrue(rows["P"].payload_available)
        self.assertIsNone(rows["P"].payload, "列表不得携带正文")
        self.assertEqual(rows["U"].read_status, ResultReadStatus.UNRESOLVED)
        self.assertFalse(rows["U"].payload_available)
        self.assertEqual(rows["N"].read_status, ResultReadStatus.TERMINAL_WITHOUT_PAYLOAD)
        self.assertEqual(rows["T1"].read_status, ResultReadStatus.COMMITTED_CURRENT)
        self.assertTrue(rows["T1"].payload_available)

        parent = await self.ledger.read_operation(self.activity, "P")
        self.assertTrue(parent.payload_available)
        self.assertEqual(json.loads(parent.payload)["format"], "json")
        listing = await self.ledger.list_committed_results(self.activity)
        by_id = {item.operation_id: item for item in listing}
        self.assertEqual(by_id["P"].read_status, parent.read_status, "列表与单读状态必须同源")

        await self.sql(
            "UPDATE activity_operation_results SET payload=%s WHERE activity_id=%s AND operation_id='T1'",
            ('{"format":"json","value":{}}', self.activity),
        )
        with self.assertRaises(ResultIntegrityError):
            await self.ledger.read_operation(self.activity, "T1")
        # 续作01（O1 修正）：正文损坏只拒绝单项读取，不得使整页元数据列表失败；
        # 列表候选资格由绑定/scope/来源投影判定，不承诺正文已通过内容完整性
        # 校验——T1 行资格仍为真而单条读取拒绝，两者并置即语义证明。
        rows_after = {item.operation_id: item for item in await self.ledger.list_operations(self.activity, limit=100)}
        self.assertEqual(set(rows_after), {"P", "U", "N", "T1"}, "正文损坏不得影响元数据列表")
        self.assertIsNone(rows_after["T1"].payload)
        self.assertTrue(rows_after["T1"].payload_available)
        self.assertIsNone(rows_after["P"].payload)
        self.assertTrue(rows_after["P"].payload_available)

    async def test_invalidated_source_suppresses_payload(self):
        await self.committed_parent("P")
        await self.sql(
            "UPDATE material_sources SET revision=revision+1 WHERE id=%s", (self.source.source_id,),
        )
        row = await self.ledger.read_operation(self.activity, "P")
        self.assertEqual(row.read_status, ResultReadStatus.INVALIDATED_SOURCE)
        self.assertFalse(row.payload_available)
        self.assertIsNone(row.payload)

    async def test_read_scope_source_versions_contract(self):
        got = await self.ledger.read_scope_source_versions([self.source.source_id])
        self.assertEqual(set(got), {self.source.source_id})
        self.assertEqual(str(got[self.source.source_id]["current_version"]), self.source.version_id)
        self.assertEqual(got[self.source.source_id]["revision"], 1)
        self.assertNotIn(str(uuid4()), got)
        with self.assertRaises(ValueError):
            await self.ledger.read_scope_source_versions([self.source.source_id, self.source.source_id])
        with self.assertRaises(ValueError):
            await self.ledger.read_scope_source_versions([])

    async def test_unknown_activity_returns_none_not_error(self):
        self.assertIsNone(await self.ledger.read_activity_facts(str(uuid4())))
        self.assertEqual(await self.ledger.list_operations(str(uuid4()), limit=10), ())
        self.assertIsNone(await self.ledger.read_operation(str(uuid4()), "P"))


if __name__ == "__main__":
    unittest.main()
