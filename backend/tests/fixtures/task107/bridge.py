"""同一107根内的精确main普通角色只读原件与计数快照。"""
import json
import os
import sys
from uuid import UUID
from .common import atomic_json, EVIDENCE, register_secret, require_runtime, serial, state


def snapshot(aid):
    if str(UUID(aid)) != aid:
        raise ValueError("107活动ID非法")
    import psycopg
    from psycopg.rows import dict_row
    dsn = os.environ["RETROLUME_DATABASE_URL"]; register_secret(dsn)
    with psycopg.connect(dsn, row_factory=dict_row) as connection:
        assert connection.execute("SELECT current_user AS name").fetchone()["name"] == "retrolume_task106_app"
        activity = connection.execute("SELECT id::text,status,deadline_at,execution_generation,scope_revision,dispatch_closed,requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds,running_settled_seconds,running_owner_session_id FROM public.activities WHERE id=%s", (aid,)).fetchone()
        tables = {}
        for name in ("interview_heads", "interview_commands", "interview_records", "activity_operations", "activity_operation_results"):
            tables[name] = list(connection.execute("SELECT * FROM public." + name + " WHERE activity_id=%s", (aid,)))
    return dict(activity=activity, tables=tables, ordinary_role=True)


def main():
    require_runtime(); request = json.load(sys.stdin)
    if request["action"] == "counts":
        value = dict(counts=state()["counts"], seconds=state()["seconds"])
    elif request["action"] == "snapshot":
        value = snapshot(request["activity_id"])
    else:
        raise ValueError("107桥只允许精确只读")
    print(json.dumps(value, ensure_ascii=False, default=serial))


if __name__ == "__main__":
    main()
