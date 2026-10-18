"""真实专库独立权限反例和当前教学闭包原件；反例事务只回滚。"""
import json
from pathlib import Path
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import CONTINUE_ROOT,atomic
from app.preview.repository import plain


def verify(resource,folder):
    progress=json.loads((CONTINUE_ROOT/"native-progress.json").read_text(encoding="utf-8"))
    with psycopg.connect(resource["app"],row_factory=dict_row) as conn:
        records=[]
        for item in progress.values():
            records.extend(conn.execute("""SELECT r.record_id,r.kind,r.activity_id,r.body,r.body_sha256,r.source_refs,
              r.goal_record_id,r.parent_record_id,r.exercise_record_id,r.answer_record_id,r.operation_id,
              o.payload_sha256,o.payload_format,
              CASE WHEN o.payload IS NULL THEN NULL ELSE (o.payload::jsonb->'value'->>'activity_id') END AS payload_activity_id
              FROM teaching_records r LEFT JOIN activity_operation_results o ON o.activity_id=r.activity_id AND o.operation_id=r.operation_id
              WHERE r.activity_id=%s ORDER BY r.seq""",(item["activity_id"],)).fetchall())
        atomic(folder/"teaching-closure-rows.json",plain(records))
    negative=[]
    for role in ("app","denied"):
        with psycopg.connect(resource[role],row_factory=dict_row) as conn:
            for table in ("html_commands","html_artifacts","html_preview_budgets","html_preview_sessions"):
                for action in ("DELETE","UPDATE"):
                    query=sql.SQL("DELETE FROM public.{} WHERE false").format(sql.Identifier(table)) if action=="DELETE" else sql.SQL("UPDATE public.{} SET activity_id=activity_id WHERE false").format(sql.Identifier(table))
                    try:
                        with conn.transaction():
                            conn.execute(query);raise RuntimeError("direct DML unexpectedly accepted")
                    except psycopg.errors.InsufficientPrivilege:negative.append({"role":role,"table":table,"action":action,"sqlstate":"42501","rollback":True})
    atomic(folder/"sql-negative.json",negative)
    atomic(folder/"pg-result.json",{"status":"PASS_DIRECT_DML_REFUSAL_ONLY","negative_count":len(negative),"hook_rollback_upgrade_not_covered":True})
