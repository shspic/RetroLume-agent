"""005 空/非空事务回滚的专用PG脚本准备；本轮 not_run。"""

from __future__ import annotations

import os
from pathlib import Path
import unittest
from uuid import uuid4

import psycopg
from psycopg import sql


BACKEND = Path(__file__).resolve().parents[3]
DSN = os.environ.get("RETROLUME_TASK_083_DATABASE_URL", "")
MIGRATIONS = [
    BACKEND / "migrations" / name for name in (
        "001_materials.sql", "002_activities.sql", "003_pdf_review.sql",
        "004_activities_time_budget.sql", "005_activities_dispatch_closed.sql",
    )
]


@unittest.skipUnless(DSN, "仅在TASK-083专用合成PG运行；不回退应用/用户DSN")
class PGMigrationTests(unittest.TestCase):
    def isolated_schema(self, action):
        schema = "task083_" + uuid4().hex
        with psycopg.connect(DSN, autocommit=True) as conn:
            conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
            try:
                conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
                for path in MIGRATIONS[:4]:
                    conn.execute(path.read_text(encoding="utf-8"))
                action(conn, schema)
            finally:
                conn.execute("ROLLBACK")  # 非空005异常后清除失败事务；空闲时无副作用。
                conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))

    def test_pg_migration_01_empty_table_adds_only_closed_column(self):
        def check(conn, schema):
            before = {row[0] for row in conn.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name='activities'", (schema,)
            )}
            conn.execute(MIGRATIONS[4].read_text(encoding="utf-8"))
            after = list(conn.execute(
                "SELECT column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema=%s AND table_name='activities'",
                (schema,),
            ))
            added = [row for row in after if row[0] not in before]
            self.assertEqual(added, [("dispatch_closed", "boolean", "NO", "false")])
        self.isolated_schema(check)

    def test_pg_migration_02_nonempty_table_rolls_back_whole_005(self):
        def check(conn, schema):
            activity_id = str(uuid4())
            conn.execute(
                """INSERT INTO activities(id,status,scope_revision,deadline_at,max_requests,
                   max_cost_microunits,reserve_cost_microunits,max_request_bytes,max_output_tokens,
                   max_running_seconds) VALUES (%s,'pending',1,CURRENT_TIMESTAMP + interval '1 hour',1,1,1,1,1,1)""",
                (activity_id,),
            )
            with self.assertRaises(psycopg.Error):
                conn.execute(MIGRATIONS[4].read_text(encoding="utf-8"))
            conn.execute("ROLLBACK")
            self.assertEqual(conn.execute("SELECT count(*) FROM activities WHERE id=%s", (activity_id,)).fetchone()[0], 1)
            self.assertEqual(conn.execute(
                "SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='activities' AND column_name='dispatch_closed'",
                (schema,),
            ).fetchone()[0], 0)
        self.isolated_schema(check)


if __name__ == "__main__":
    unittest.main(verbosity=2)
