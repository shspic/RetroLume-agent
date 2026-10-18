"""TASK-100 教学域真实 PG 支撑：身份断言、真实资料发布与每例定向 FK 清理。

沿用 TASK-097 既有受控模式（专属库 + 专属角色 + 身份硬核对），
差异：库名/角色为本卡合成库；额外准备教学三表的清理顺序，
并暴露教学账本所需的 lease/命令构造助手。

DSN 只经 RETROLUME_TASK100_PG_DSN 注入，绝不回退任何用户库。
本文件永不进入产品导入链。
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from app.activities import ActivitySpec, PostgresAdmissionLedger, SourceSnapshot
from app.materials.repository import PostgresMaterials
from app.runtime import psycopg_compatible_loop_factory
from app.storage.originals import OriginalStore

# 续作01 业务库：g8_main（001—009 完整实现与合成业务）。旧初轮库
# retrolume_task100_main 只读保留；库身份可经环境覆盖但必须显式声明。
DB = os.environ.get("RETROLUME_TASK100_EXPECTED_DB", "retrolume_task100_g8_main")
# 产品连接身份：本卡合成库的应用角色（非 admin、非 super），
# 以确保测的是真实权限下的行为，不靠超级权限旁路。
ROLE = os.environ.get("RETROLUME_TASK100_EXPECTED_ROLE", "retrolume_task100_app")
DSN = os.environ.get("RETROLUME_TASK100_PG_DSN", "")
ROOT = Path(__file__).resolve().parents[4]

# 教学三表读取顺序（子表先于父表）；本卡不执行任何删除，仅用于核对口径。


class Fixture:
    def __init__(self, dsn: str, root: Path) -> None:
        self.dsn = dsn
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.originals = OriginalStore(self.root)
        self.materials = PostgresMaterials(dsn)
        self.ledger = PostgresAdmissionLedger(dsn)
        self.activities: list[str] = []
        self.sources: list[str] = []
        fact = self.rows("SELECT current_database() AS db, current_user AS role")[0]
        if fact != {"db": DB, "role": ROLE}:
            raise ValueError(f"TASK-100 合成身份不匹配: {fact}")

    def rows(self, sql: str, params: tuple = ()) -> list[dict]:
        with psycopg.connect(self.dsn, row_factory=dict_row) as connection:
            cursor = connection.execute(sql, params)
            return cursor.fetchall() if cursor.description else []

    def text(self, text: str, title: str = "speed.md", fmt: str = "md") -> dict:
        raw = text.encode("utf-8")
        original = self.originals.put(io.BytesIO(raw), max_bytes=5242880)
        row = self.materials.save(source_id=None, expected_version=None, filename=title,
                                  format=fmt, sha256=original.sha256, size=original.size)
        self.sources.append(row["id"])
        return row

    async def activity(self, rows, **overrides) -> str:
        activity_id = str(uuid4())
        self.activities.append(activity_id)
        values = dict(
            activity_id=activity_id,
            sources=tuple(SourceSnapshot(r["id"], r["version_id"], r["revision"]) for r in rows),
            deadline_at=datetime.now(timezone.utc) + timedelta(hours=1),
            max_requests=16, max_cost_microunits=1600000, reserve_cost_microunits=100000,
            max_request_bytes=65536, max_output_tokens=2048, max_running_seconds=900,
            allowed_models=(("deepseek_chat_completions", "synthetic-model-100"),),
        )
        await self.ledger.create_activity(ActivitySpec(**(values | overrides)))
        return activity_id

    async def lease(self, activity_id: str, *, executor: str = "pg100"):
        return await self.ledger.claim_lease(activity_id, executor, lease_seconds=120,
                                             window_seconds=30)

    def head(self, activity_id: str) -> dict | None:
        rows = self.rows("SELECT * FROM teaching_heads WHERE activity_id=%s", (activity_id,))
        return rows[0] if rows else None

    def commands(self, activity_id: str) -> list[dict]:
        return self.rows(
            "SELECT business_key, action, status, request_sha256 FROM teaching_commands "
            "WHERE activity_id=%s ORDER BY created_at", (activity_id,))

    def records(self, activity_id: str) -> list[dict]:
        return self.rows(
            "SELECT kind, ordinal, goal_version, scope_revision FROM teaching_records "
            "WHERE activity_id=%s ORDER BY seq", (activity_id,))

    def identity(self) -> dict:
        """专库身份核对：库名/角色两项全等才算本卡合成库。"""
        return self.rows(
            "SELECT current_database() AS db, current_user AS role")[0]

    def retained(self) -> dict:
        """保留态事实：本卡写入的活动/资料/教学行仍留在库内。"""
        return {
            "activities_tracked": len(self.activities),
            "sources_tracked": len(self.sources),
            "teaching_heads": self.rows("SELECT count(*) AS n FROM teaching_heads")[0]["n"],
            "teaching_commands": self.rows("SELECT count(*) AS n FROM teaching_commands")[0]["n"],
            "teaching_records": self.rows("SELECT count(*) AS n FROM teaching_records")[0]["n"],
        }

    def preserve(self) -> dict:
        """保留式收尾：只核对专库身份并记录残留，绝不 DELETE。

        本卡纪律：已写入的合成数据与失败证据一律保留在专库内，供后续
        定向续验与独立审计复核；清理权归编排，不在本卡行使。
        """
        identity = self.identity()
        if identity["db"] != DB:
            raise ValueError(f"专库身份不符，拒绝按保留态处理: {identity}")
        fact = {"identity": identity, "retained": self.retained()}
        print("PRESERVED " + json.dumps(fact, ensure_ascii=False))
        return fact


class PGBase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self):
        self._asyncioRunner = asyncio.Runner(debug=False,
                                            loop_factory=psycopg_compatible_loop_factory)

    async def asyncSetUp(self):
        if not DSN:
            self.skipTest("TASK-100 专用合成 DSN 未注入")
        # 原件暂存目录放在证据目录之外：OriginalStore.put 会写 .incoming-* 临时
        # 文件再改名，落在证据目录内会与证据冻结/清理纪律冲突。
        self.fixture = Fixture(DSN, Path(os.environ.get(
            "RETROLUME_TASK100_ORIGINALS_DIR",
            str(Path(os.environ.get("TEMP", ".")) / "retrolume-task100-originals"))))
        self.ledger = self.fixture.ledger

    async def asyncTearDown(self):
        # 保留式收尾：不清理合成数据，只核对专库身份并记录残留量。
        try:
            self.fixture.preserve()
        except Exception as exc:  # noqa: BLE001 - 保留失败不掩盖用例结论
            print(f"PRESERVE_FAILED {type(exc).__name__}: {exc}")
