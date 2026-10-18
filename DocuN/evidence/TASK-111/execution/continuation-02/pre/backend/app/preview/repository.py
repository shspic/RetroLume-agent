"""交互域短事务与同快照资格；复用来源/记忆/活动/操作的既有锁序。"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid4
from .business_contracts import HtmlRefusal, HtmlCommand, HtmlProfile, HtmlCallBinding, operation_id
from .compiler import verify_package, runtime_identity
from .description import canonical, digest, load_json

TABLES = ("html_commands", "html_artifacts", "html_preview_budgets", "html_preview_sessions")
SCHEMA_FILE = Path(__file__).with_name("schema-fingerprint.json")


def plain(value):
    if isinstance(value, dict): return {k: plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return [plain(v) for v in value]
    if isinstance(value, (UUID, datetime)): return str(value)
    return value


class HtmlLedgerMethods:
    async def html_schema_shape(self, connection):
        queries = {
          "columns": """SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod) AS type,a.attnotnull,
            pg_get_expr(d.adbin,d.adrelid) AS default,r.rolname AS owner,c.relacl::text AS acl
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner
            JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped
            LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
            WHERE n.nspname='public' AND c.relname=ANY(%s) ORDER BY c.relname,a.attnum""",
          "constraints": """SELECT c.relname,k.conname,k.contype,k.convalidated,pg_get_constraintdef(k.oid) AS definition
            FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND c.relname=ANY(%s) ORDER BY c.relname,k.conname""",
          "indexes": "SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' AND tablename=ANY(%s) ORDER BY tablename,indexname",
          "triggers": """SELECT c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid) AS definition FROM pg_trigger t
            JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND c.relname=ANY(%s) AND NOT t.tgisinternal ORDER BY c.relname,t.tgname"""}
        shape = {}
        for key, sql in queries.items():
            cursor = await connection.execute(sql, (list(TABLES),)); shape[key] = plain(await cursor.fetchall())
        cursor = await connection.execute("""SELECT p.proname,pg_get_function_identity_arguments(p.oid) AS arguments,
          p.prosrc,p.prosecdef,p.provolatile,p.proconfig,p.proacl::text AS acl,r.rolname AS owner
          FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner
          WHERE n.nspname='public' AND p.proname LIKE 'html_%%' ORDER BY p.proname,arguments""")
        shape["functions"] = plain(await cursor.fetchall())
        cursor = await connection.execute("""SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls
          FROM pg_roles WHERE rolname IN ('retrolume_html_owner','retrolume_html_app') ORDER BY rolname""")
        shape["roles"] = plain(await cursor.fetchall())
        return shape

    async def _html_assert_schema(self, connection):
        try:
            expected = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))["sha256"]
            if len(expected) != 64 or digest(await self.html_schema_shape(connection)) != expected:
                raise HtmlRefusal("html_schema_not_ready", status=503)
        except (OSError, ValueError, KeyError):
            raise HtmlRefusal("html_schema_not_ready", status=503) from None

    async def _html_sources(self, connection, activity_id):
        cursor = await connection.execute("""SELECT s.source_id::text,s.version_id::text,s.source_revision,
         v.sha256 AS original_sha256,COALESCE(m.current_version=s.version_id AND m.revision=s.source_revision,false) AS valid
         FROM public.activity_scope_sources s JOIN public.material_versions v ON v.id=s.version_id AND v.source_id=s.source_id
          JOIN public.material_sources m ON m.id=s.source_id WHERE s.activity_id=%s ORDER BY s.source_id""", (activity_id,))
        sources = list(await cursor.fetchall())
        if not 1 <= len(sources) <= 10 or any(not s["valid"] for s in sources):
            raise HtmlRefusal("source_invalid")
        return [{k: v for k, v in s.items() if k != "valid"} for s in sources]

    async def _html_parent_locked(self, connection, activity, parent):
        from app.capabilities.contracts import validate_business_payload
        from app.learning.contracts import read_document
        aid = str(activity["id"])
        sources = await self._html_sources(connection, aid)
        dependencies = []
        if parent["kind"] == "learning":
            if not parent["operation_id"].startswith(("learn-first-v1.", "learn-next-v1.")):
                raise HtmlRefusal("html_parent_forbidden")
            cursor = await connection.execute("""SELECT r.*,o.state,o.kind FROM public.activity_operation_results r
              JOIN public.activity_operations o ON o.activity_id=r.activity_id AND o.operation_id=r.operation_id
              WHERE r.activity_id=%s AND r.operation_id=%s""", (aid, parent["operation_id"]))
            row = await cursor.fetchone()
            if row is None or row["state"] != "received" or row["kind"] != "model" or row["scope_revision"] != activity["scope_revision"] or row["payload_sha256"] != parent["payload_sha256"]:
                raise HtmlRefusal("result_invalidated")
            validate_business_payload(row["payload"], row["payload_format"], row["payload_sha256"])
            document = json.loads(row["payload"])["value"]
            _, output = read_document(document, activity_id=aid, operation_id=parent["operation_id"])
            if output.kind != "answer" or not 0 <= parent["segment_index"] < len(output.segments):
                raise HtmlRefusal("html_parent_forbidden")
            segment = output.segments[parent["segment_index"]]
            summary = segment.text
            catalog = [item for item in document["catalog"] if item["citation_id"] in segment.citations]
            goal_version = 0
        else:
            await self._teaching_lock_operations(connection, aid)
            cursor = await connection.execute("SELECT * FROM public.teaching_heads WHERE activity_id=%s FOR UPDATE", (aid,))
            head = await cursor.fetchone()
            cursor = await connection.execute("SELECT business_key FROM public.teaching_commands WHERE activity_id=%s ORDER BY business_key FOR UPDATE", (aid,))
            await cursor.fetchall()
            cursor = await connection.execute("""WITH RECURSIVE d AS (
             SELECT r.*,ARRAY[r.record_id] AS path FROM public.teaching_records r WHERE r.activity_id=%s AND r.record_id=%s
             UNION ALL SELECT r.*,d.path||r.record_id FROM d JOIN public.teaching_records r ON r.activity_id=d.activity_id
               AND r.record_id IN (d.parent_record_id,d.goal_record_id,d.exercise_record_id,d.answer_record_id)
               WHERE NOT r.record_id=ANY(d.path) AND cardinality(d.path)<13)
             SELECT DISTINCT ON (d.record_id) d.*,d.business_key AS command_key,p.payload,p.payload_format,p.payload_sha256 AS operation_payload_sha256
              FROM d LEFT JOIN public.activity_operation_results p ON p.activity_id=d.activity_id AND p.operation_id=d.operation_id
             ORDER BY d.record_id""", (aid, parent["record_id"]))
            rows = list(await cursor.fetchall())
            row = next((r for r in rows if str(r["record_id"]) == parent["record_id"]), None)
            if (head is None or row is None or len(rows)>12 or row["kind"] not in ("exercise", "feedback")
                or str(head[row["kind"]+"_record_id"]) != parent["record_id"] or row["body_sha256"] != parent["body_sha256"]
                or any(r["goal_version"] != head["goal_version"] or r["scope_revision"] != activity["scope_revision"] for r in rows)):
                raise HtmlRefusal("result_invalidated")
            from app.learning.teaching_views import verified_document, bound_references
            source_map = {(s["source_id"], s["version_id"]): s for s in sources}
            for dependency in rows:
                references = bound_references(dependency)
                if references is None or any((s := source_map.get((r["source_id"],r["version_id"]))) is None
                    or s["source_revision"] != r["source_revision"] or s["original_sha256"] != r["original_sha256"] for r in references):
                    raise HtmlRefusal("source_invalid")
                verified_document(dependency)
                dependencies.append({"record_id": str(dependency["record_id"]), "body_sha256": dependency["body_sha256"]})
            body = verified_document(row)
            raw = json.loads(row["payload"])["value"]
            catalog = raw["catalog"]
            if parent.get("point_id") is not None:
                points = body.get("points", [])
                if not any(p.get("id",p.get("point_id")) == parent["point_id"] for p in points if type(p) is dict):
                    raise HtmlRefusal("html_parent_forbidden")
            summary = canonical(body)
            goal_version = head["goal_version"]
        if len(summary.encode("utf-8")) > 4096 or not 1 <= len(catalog) <= 8 or sum(len(canonical(e).encode("utf-8")) for e in catalog) > 12288:
            raise HtmlRefusal("html_context_limit", status=413)
        source_map = {(s["source_id"],s["version_id"]):s for s in sources}
        for entry in catalog:
            s = source_map.get((entry["source_id"],entry["version_id"]))
            if s is None or s["source_revision"] != entry["source_revision"]:
                raise HtmlRefusal("source_invalid")
        cursor = await connection.execute("SELECT selection_sha256 FROM public.activity_memory_bindings WHERE activity_id=%s", (aid,))
        memory = await cursor.fetchone()
        return {"sources": sources, "parent": parent, "parent_summary": summary, "catalog": catalog,
                "dependencies": sorted(dependencies, key=lambda x:x["record_id"]), "goal_version": goal_version,
                "scope_revision": activity["scope_revision"], "memory_selection_sha256": None if memory is None else memory["selection_sha256"]}

    async def accept_html_command(self, activity_id, command, renderer_sha256, config_sha256):
        aid = self._uuid(activity_id, "activity_id")
        command = HtmlCommand.model_validate(command.model_dump())
        request = command.model_dump()
        request_body, request_hash = canonical(request), digest(request)
        async def transaction(connection):
            await self._html_assert_schema(connection)
            state = await self._memory_lock_prefix(connection, aid)
            activity = state["activity"]
            if activity is None or not state["eligible"] or activity["status"] == "cancelled" or activity["deadline_at"] <= datetime.now(timezone.utc):
                raise HtmlRefusal("result_invalidated")
            await self._interview_require_non_domain(connection, aid)
            await self._teaching_lock_operations(connection, aid)
            parent = await self._html_parent_locked(connection, activity, request["parent"])
            cursor = await connection.execute("SELECT * FROM public.html_commands WHERE activity_id=%s AND business_key=%s", (aid, command.business_key))
            existing = await cursor.fetchone()
            if existing is not None:
                if existing["request_sha256"] != request_hash or existing["request_body"] != request_body:
                    raise HtmlRefusal("html_key_conflict")
                return plain(existing)
            if command.expected_config_sha256 != config_sha256 or renderer_sha256 != runtime_identity()["renderer_sha256"]:
                raise HtmlRefusal("html_config_changed")
            context = {"schema":"html.context.v2", "activity_id":aid, "business_key":command.business_key,
                       "request_sha256":request_hash, "renderer_sha256":renderer_sha256, "focus":command.focus,
                       "config_sha256":config_sha256, **parent}
            context_body = canonical(context)
            if len(context_body.encode("utf-8")) > 24576: raise HtmlRefusal("html_context_limit", status=413)
            p = request["parent"]
            locator = p.get("operation_id",p.get("record_id"))
            ph = p.get("payload_sha256",p.get("body_sha256"))
            await connection.execute("SELECT public.html_accept_command(%s::uuid,%s::uuid,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
              (aid,command.business_key,operation_id(command.business_key),request_body,request_hash,context_body,digest(context),
               renderer_sha256,activity["scope_revision"],p["kind"],locator,ph))
            cursor = await connection.execute("SELECT * FROM public.html_commands WHERE activity_id=%s AND business_key=%s", (aid,command.business_key))
            return plain(await cursor.fetchone())
        return await self._transaction(transaction)

    async def claim_html_command(self, aid, key):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            await self._memory_lock_prefix(connection, aid)
            await self._teaching_lock_operations(connection, aid)
            cursor = await connection.execute("SELECT public.html_claim_command(%s::uuid,%s::uuid) AS claimed", (aid,key))
            return bool((await cursor.fetchone())["claimed"])
        return await self._transaction(transaction)

    async def _html_locked_binding(self, connection, activity, op, binding=None, *, allow_invalidated=False):
        from app.capabilities.contracts import AdmissionDenied
        if not op.startswith("html11m."): raise AdmissionDenied("html_profile_required")
        await self._html_assert_schema(connection)
        cursor = await connection.execute("SELECT * FROM public.html_commands WHERE activity_id=%s AND operation_id=%s", (activity["id"],op))
        command = await cursor.fetchone()
        if command is None or command["status"] != "launch_claimed": raise AdmissionDenied("html_command_not_claimed")
        if binding is not None:
            b = HtmlCallBinding.model_validate(binding.model_dump())
            if (b.business_key != str(command["business_key"]) or b.request_sha256 != command["request_sha256"]
                or b.context_sha256 != command["context_sha256"] or b.renderer_sha256 != command["renderer_sha256"]
                or b.memory_selection_sha256 != load_json(command["context_body"]).get("memory_selection_sha256")):
                raise AdmissionDenied("invalid_html_profile")
        cursor = await connection.execute("SELECT public.html_parent_eligible(%s::uuid,%s::jsonb) AS eligible", (activity["id"],command["context_body"]))
        if not (await cursor.fetchone())["eligible"] and not allow_invalidated: raise AdmissionDenied("result_invalidated")
        return command

    async def _html_require_call(self, connection, activity, op, binding):
        from app.capabilities.contracts import AdmissionDenied
        if activity is None or binding is None or not activity.get("_memory_eligible",True):
            raise AdmissionDenied("html_profile_required")
        # 旧锁序的operations/head先于新command；没有新profile不能绕背景资格。
        await self._teaching_lock_operations(connection,str(activity["id"]))
        await self._html_locked_binding(connection,activity,op,binding)

    async def verify_html_request(self, profile):
        async def transaction(connection):
            state = await self._memory_lock_prefix(connection,profile.activity_id)
            if state["activity"] is None: raise HtmlRefusal("result_invalidated")
            await self._teaching_lock_operations(connection,profile.activity_id)
            command = await self._html_locked_binding(connection,state["activity"],operation_id(profile.business_key),
                HtmlCallBinding(business_key=profile.business_key,request_sha256=profile.request_sha256,context_sha256=profile.context_sha256,
                  renderer_sha256=profile.renderer_sha256,memory_selection_sha256=load_json(profile.context_json).get("memory_selection_sha256")))
            if command["context_body"] != profile.context_json: raise HtmlRefusal("invalid_html_profile")
        await self._transaction(transaction)

    async def _write_html_outcome(self, connection, activity, call, outcome, payload_triple):
        from app.capabilities.contracts import LedgerDisposition, AdmissionDenied
        # RECEIVED非法结构仍写真实收据；只有完整v2正文能插入artifact。
        command = await self._html_locked_binding(connection,activity,call["operation_id"],
             allow_invalidated=outcome.disposition is LedgerDisposition.UNKNOWN and payload_triple is None)
        disposition = "unknown" if outcome.disposition is LedgerDisposition.UNKNOWN else "not_sent" if outcome.disposition is LedgerDisposition.NOT_SENT else "invalid_output"
        if payload_triple is not None:
            value = json.loads(payload_triple[1])["value"]
            if (value.get("profile") != "html_explanation.v2" or value.get("activity_id") != str(activity["id"])
                or value.get("business_key") != str(command["business_key"]) or value.get("request_sha256") != command["request_sha256"]
                or value.get("context_sha256") != command["context_sha256"]):
                raise AdmissionDenied("invalid_html_profile")
            package = value["package"]; verify_package(package)
            await connection.execute("SELECT public.html_commit_artifact(%s::uuid,%s::uuid,%s::uuid,%s,%s,%s,%s,%s,%s,%s)",
              (activity["id"],command["business_key"],str(uuid4()),call["operation_id"],canonical(package),package["artifact_sha256"],
               package["description_sha256"],package["renderer"]["renderer_sha256"],package["execution_package_sha256"],payload_triple[2]))
            disposition = "succeeded"
        await connection.execute("SELECT public.html_finish_command(%s::uuid,%s::uuid,%s,%s)",
                                 (activity["id"],command["business_key"],disposition,outcome.error_code))

    async def _html_confirm_integrity(self, connection, call, payload_triple):
        from app.capabilities.contracts import AdmissionDenied
        cursor = await connection.execute("SELECT b.* FROM public.html_artifacts b WHERE activity_id=%s AND operation_id=%s", (call["activity_id"],call["operation_id"]))
        artifact = await cursor.fetchone()
        if (payload_triple is None) != (artifact is None) or (artifact is not None and artifact["body_sha256"] != payload_triple[2]):
            raise AdmissionDenied("html_integrity_error")

    async def finish_html_supervision(self, aid, key, supervision):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            await self._memory_lock_prefix(connection,aid)
            await self._teaching_lock_operations(connection,aid)
            cursor = await connection.execute("""SELECT c.*,o.state AS operation_state FROM public.html_commands c
              LEFT JOIN public.activity_operations o ON o.activity_id=c.activity_id AND o.operation_id=c.operation_id
              WHERE c.activity_id=%s AND c.business_key=%s""", (aid,key))
            row = await cursor.fetchone()
            if row and row["status"] == "launch_claimed":
                disposition = "refused" if row["operation_state"] is None and supervision is not None and not supervision.cleanup_incomplete else "unknown"
                await connection.execute("SELECT public.html_finish_command(%s::uuid,%s::uuid,%s,%s)", (aid,key,disposition,"html_supervision_unconfirmed"))
        await self._transaction(transaction)

    async def read_html_command(self, aid, key):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            cursor = await connection.execute("""SELECT c.business_key::text,c.operation_id,c.status,c.terminal_disposition,c.error_code,
              c.request_body,c.request_sha256,b.artifact_id::text,b.artifact_sha256,
              CASE WHEN b.artifact_id IS NULL THEN false ELSE public.html_artifact_eligible(c.activity_id,b.artifact_id) END AS eligible
              FROM public.html_commands c LEFT JOIN public.html_artifacts b ON b.activity_id=c.activity_id AND b.business_key=c.business_key
              WHERE c.activity_id=%s AND c.business_key=%s""", (aid,key))
            row = await cursor.fetchone()
            if row is None: return None
            result = plain(row); result["accepted_input"] = load_json(result.pop("request_body"),8192)
            result["read_status"] = "current" if result.pop("eligible") else "unconfirmed" if result["artifact_id"] is None else "source_invalid"
            return result
        return await self._transaction(transaction)

    async def read_html_artifact(self, aid, artifact_id):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            cursor = await connection.execute("""SELECT b.artifact_id::text,b.business_key::text,b.operation_id,b.artifact_sha256,b.description_sha256,b.renderer_sha256,
             public.html_artifact_eligible(b.activity_id,b.artifact_id) AS eligible,
             CASE WHEN public.html_artifact_eligible(b.activity_id,b.artifact_id) THEN b.artifact_body ELSE NULL END AS artifact_body,
             CASE WHEN public.html_artifact_eligible(b.activity_id,b.artifact_id) THEN c.context_body ELSE NULL END AS context_body
             FROM public.html_artifacts b JOIN public.html_commands c ON c.activity_id=b.activity_id AND c.business_key=b.business_key
             WHERE b.activity_id=%s AND b.artifact_id=%s""", (aid,artifact_id))
            row = await cursor.fetchone()
            if row is None: raise HtmlRefusal("not_found",status=404)
            if not row["eligible"]: raise HtmlRefusal("source_invalid")
            result = plain(row); package = load_json(result.pop("artifact_body"),110592)
            result["description"] = verify_package(package)
            result["context"] = load_json(result.pop("context_body"))
            return result
        return await self._transaction(transaction)

    async def list_html_artifacts(self, aid, before=None):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            cursor = await connection.execute("""SELECT artifact_id::text,business_key::text,operation_id,artifact_sha256,created_at,
              public.html_artifact_eligible(activity_id,artifact_id) AS eligible FROM public.html_artifacts
              WHERE activity_id=%s AND (%s::timestamptz IS NULL OR created_at<%s::timestamptz)
              ORDER BY created_at DESC,artifact_id LIMIT 20""", (aid,before,before))
            return plain(await cursor.fetchall())
        return await self._transaction(transaction)

    async def reserve_html_preview(self, aid, artifact_id, command, identity, reserve_seconds):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            await self._memory_lock_prefix(connection,aid)
            await self._teaching_lock_operations(connection,aid)
            cursor = await connection.execute("SELECT * FROM public.html_preview_sessions WHERE activity_id=%s AND start_key=%s", (aid,command.start_key))
            existing = await cursor.fetchone()
            owner_hash = hashlib.sha256(bytes.fromhex(command.input_owner_key)).hexdigest()
            if existing is not None:
                if str(existing["artifact_id"]) != artifact_id or existing["artifact_sha256"] != command.expected_artifact_sha256 or existing["owner_key_sha256"] != owner_hash:
                    raise HtmlRefusal("html_start_key_conflict")
                return plain(existing), False
            cursor = await connection.execute("SELECT artifact_sha256 FROM public.html_artifacts WHERE activity_id=%s AND artifact_id=%s", (aid,artifact_id))
            artifact = await cursor.fetchone()
            if artifact is None or artifact["artifact_sha256"] != command.expected_artifact_sha256: raise HtmlRefusal("html_integrity_error")
            await connection.execute("SELECT public.html_reserve_preview(%s::uuid,%s::uuid,%s::uuid,%s::uuid,%s,%s::uuid,%s,%s,%s::uuid,%s,%s,%s,%s,%s,%s)",
              (aid,artifact_id,identity["preview_id"],command.start_key,command.expected_artifact_sha256,identity["owner_id"],owner_hash,
               hashlib.sha256(bytes.fromhex(identity["control_key"])).hexdigest(),identity["boot_id"],identity["nonce"],identity["image_id"],
               reserve_seconds,identity["t0_ns"],identity["deadline_at"],identity["config_sha256"]))
            cursor = await connection.execute("SELECT * FROM public.html_preview_sessions WHERE preview_id=%s", (identity["preview_id"],))
            return plain(await cursor.fetchone()), True
        return await self._transaction(transaction)

    async def update_html_preview(self, pid, control_key, state, *, cid=None, first_receipt=None, confirmation=None, elapsed=None):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            cursor = await connection.execute("SELECT activity_id::text FROM public.html_preview_sessions WHERE preview_id=%s", (pid,))
            locator = await cursor.fetchone()
            if locator is None: raise HtmlRefusal("not_found",status=404)
            await self._memory_lock_prefix(connection,locator["activity_id"])
            # 旧activity行已独占；新域DML/行锁由有限security-definer producer持有。
            await connection.execute("SELECT public.html_update_preview(%s::uuid,%s,%s,%s,%s,%s,%s)",
                (pid,control_key,state,cid,canonical(first_receipt) if first_receipt else None,canonical(confirmation) if confirmation else None,elapsed))
        await self._transaction(transaction)

    async def read_html_preview(self, aid, pid):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            cursor = await connection.execute("""SELECT s.preview_id::text,s.artifact_id::text,s.artifact_sha256,s.generation,s.owner_id::text,
              s.owner_key_sha256,s.boot_id::text,s.state,s.deadline_at,s.reserve_seconds,s.elapsed_seconds,s.revision,
              public.html_artifact_eligible(s.activity_id,s.artifact_id) AS eligible,
              b.starts_used,b.settled_seconds,b.reserved_seconds FROM public.html_preview_sessions s
              JOIN public.html_preview_budgets b ON b.activity_id=s.activity_id WHERE s.activity_id=%s AND s.preview_id=%s""", (aid,pid))
            row = await cursor.fetchone()
            if row is None: raise HtmlRefusal("not_found",status=404)
            return plain(row)
        return await self._transaction(transaction)

    async def html_preview_budget(self, aid):
        async def transaction(connection):
            await self._html_assert_schema(connection)
            cursor = await connection.execute("SELECT * FROM public.html_preview_budgets WHERE activity_id=%s", (aid,))
            row = await cursor.fetchone()
            return plain(row) if row else {"max_starts":3,"max_seconds":180,"starts_used":0,"settled_seconds":0,"reserved_seconds":0}
        return await self._transaction(transaction)
