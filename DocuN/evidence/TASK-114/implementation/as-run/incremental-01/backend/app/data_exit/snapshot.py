"""一个专用只读连接的同 T 31 安全域，以及保原字节的文件复制。"""
from dataclasses import dataclass
import os
from pathlib import Path
import time
from uuid import uuid4
from .codec import encode_row, plain, TRANSFORMS
from .contracts import DataError, Limits, PROFILE, TABLES, VIEWS, canonical, digest, uuid
from .files import safe_root, regular
from .repository import DataRepository
from .schema import COLUMNS, MIGRATIONS
from .spool import SpoolRows, FilteredRows
from app.storage.originals import Original


@dataclass
class SnapshotResult:
    root: Path
    point: dict
    source_control: dict
    entries: list
    availability: list
    rows: dict
    scope: dict


def validate_scope(scope, kind):
    if not isinstance(scope, dict) or set(scope) - {"mode", "source_ids", "activity_ids", "allow_incomplete",'expected_closure_sha256'}:
        raise DataError("invalid_input", 400)
    if scope.get("mode", "all") not in ("all", "selected"):
        raise DataError("invalid_input", 400)
    for field in ("source_ids", "activity_ids"):
        values = scope.get(field, [])
        if not isinstance(values, list) or len(values) > 128 or len(set(values)) != len(values):
            raise DataError("invalid_input", 400)
        for value in values: uuid(value)
    if scope.get("mode", "all") == "selected" and not (scope.get("source_ids") or scope.get("activity_ids")):
        raise DataError("invalid_input", 400)
    if type(scope.get("allow_incomplete", False)) is not bool:
        raise DataError("invalid_input", 400)
    if kind == "restore_checkpoint" and (scope.get("mode", "all") != "all" or scope.get("allow_incomplete")):
        raise DataError("restore_not_supported")
    result={"mode": scope.get("mode", "all"), "source_ids": scope.get("source_ids", []),
            "activity_ids": scope.get("activity_ids", []), "allow_incomplete": scope.get("allow_incomplete", False)}
    if 'expected_closure_sha256' in scope:result['expected_closure_sha256']=scope['expected_closure_sha256']
    return result


class SnapshotCoordinator:
    def __init__(self, snapshot_dsn, store, root_lease, backup_root, limits=None):
        self.repository = DataRepository(snapshot_dsn)
        self.store, self.lease, self.backup_root = store, root_lease, safe_root(backup_root)
        self.limits = limits or Limits()

    def preview_scope(self,scope):
        scope=validate_scope(scope,'portable_export')
        rows={table:[] for table in TABLES}
        graph=('material_sources','material_versions','activities','activity_scope_sources','activity_memory_choices','learning_memory_dependencies')
        with self.repository.connection(readonly=True,repeatable=True) as connection:
            for table in graph:
                columns=','.join(COLUMNS[table])
                rows[table]=[encode_row(table,row) for row in connection.execute('SELECT '+columns+' FROM public.'+table).fetchall()]
        selected,closure=self._closure(rows,scope)
        return {**closure,'closure_sha256':self.closure_digest(selected,closure),
                'materials':[{'id':r['id'],'title':r['title'],'revision':r['revision']} for r in selected['material_sources']],
                'activity_count':len(selected['activities'])}

    @staticmethod
    def closure_digest(rows,closure):
        import hashlib
        values={'closure':closure,'materials':rows['material_sources'],
                'versions':rows['material_versions'],'activity_scope_sources':rows['activity_scope_sources'],
                'activity_memory_choices':rows['activity_memory_choices'],'learning_memory_dependencies':rows['learning_memory_dependencies']}
        result=hashlib.sha256();result.update(b'{')
        for index,(key,value) in enumerate(sorted(values.items())):
            if index:result.update(b',')
            result.update((canonical(key)+':').encode('utf-8'))
            if key=='closure':result.update(canonical(value).encode('utf-8'))
            else:
                result.update(b'[')
                for position,row in enumerate(value):
                    if position:result.update(b',')
                    result.update(canonical(row).encode('utf-8'))
                result.update(b']')
        result.update(b'}')
        return result.hexdigest()

    def capture(self, job_id, kind, scope, *, check_cancel=lambda: None, on_stage=lambda _: None):
        scope = validate_scope(scope, kind)
        spool_parent = self.backup_root / ".spool"
        if not spool_parent.exists(): spool_parent.mkdir()
        safe_root(spool_parent)
        root = spool_parent / uuid(job_id)
        root.mkdir()
        start = time.monotonic()
        entries, rows, availability = [], {}, []
        total_bytes, row_count = 0, 0
        def bounded():
            check_cancel()
            if time.monotonic() - start > self.limits.operation_seconds:
                raise DataError("operation_timeout", 504)
        def write_entry(name, content, entry_kind="relation_records"):
            import hashlib
            nonlocal total_bytes
            if len(entries) >= self.limits.members:
                raise DataError("capacity_exceeded", 413)
            path = root / name
            if not path.parent.exists(): path.parent.mkdir()
            safe_root(path.parent)
            count=0;checksum=hashlib.sha256()
            with path.open("xb") as stream:
                chunks=(content,) if isinstance(content,bytes) else content
                for raw in chunks:
                    bounded();count+=len(raw);total_bytes+=len(raw)
                    if total_bytes>self.limits.package_bytes or count>self.limits.chunk_bytes:
                        raise DataError('capacity_exceeded',413)
                    stream.write(raw);checksum.update(raw)
                stream.flush(); os.fsync(stream.fileno())
            entries.append({"path": name, "kind": entry_kind, "availability": "present",
                            "bytes": str(count), "sha256": checksum.hexdigest()})
        def json_lines(values):
            for value in values:yield canonical(value).encode('utf-8')+b'\n'
        raw_root=root/'.raw';raw_root.mkdir()
        raw_bytes=0
        def spool(connection,name,query,encoder):
            nonlocal row_count,raw_bytes
            table_bytes,count=0,0;path=raw_root/(name+'.jsonl')
            with path.open('xb') as stream,connection.cursor(name='data_'+name) as cursor:
                cursor.execute(query)
                while chunk:=cursor.fetchmany(128):
                    bounded()
                    if time.monotonic()-start>self.limits.snapshot_seconds:raise DataError('operation_timeout',504)
                    for row in chunk:
                        raw=canonical(encoder(row)).encode('utf-8')+b'\n'
                        table_bytes+=len(raw);raw_bytes+=len(raw);row_count+=1;count+=1
                        if (len(raw)>self.limits.json_line_bytes or table_bytes>self.limits.chunk_bytes
                            or raw_bytes>self.limits.package_bytes or row_count>self.limits.rows):
                            raise DataError('capacity_exceeded',413)
                        stream.write(raw)
                stream.flush();os.fsync(stream.fileno())
            return SpoolRows(path,count,self.limits)
        on_stage("reading")
        with self.lease.acquire():
            with self.repository.connection(readonly=True, repeatable=True) as connection:
                role = connection.execute("SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolbypassrls FROM pg_roles WHERE rolname=SESSION_USER").fetchone()
                if role is None or any(role[k] for k in ("rolsuper", "rolcreatedb", "rolcreaterole", "rolbypassrls")):
                    raise DataError("snapshot_role_unsafe", 503)
                point = plain(connection.execute("SELECT CURRENT_TIMESTAMP AS logical_time_utc,pg_current_snapshot()::text AS database_snapshot").fetchone())
                for table in TABLES:
                    bounded()
                    columns = COLUMNS[table]
                    selected = ",".join('"' + column + '"' for column in columns)
                    where = ""
                    if table == "learning_memory_bodies":
                        where = " WHERE memory_id IN(SELECT memory_id FROM public.learning_memories WHERE state='active')"
                    query = f"SELECT {selected} FROM public.{table}{where} ORDER BY " + ",".join(list(columns)[:2])
                    rows[table] = spool(connection,table,query,lambda row:encode_row(table,row))
                    if time.monotonic() - start > self.limits.snapshot_seconds:
                        raise DataError("operation_timeout", 504)
                control = plain(connection.execute("SELECT * FROM public.data_export_control_v1").fetchone())
                history = spool(connection,'operation_history',"SELECT * FROM public.data_export_job_history_v1 ORDER BY origin_source_row_id",plain)
                tombstones = spool(connection,'tombstones',"SELECT * FROM public.data_export_tombstones_v1 ORDER BY entity_kind,entity_id,effective_revision",plain)
                if control is None or control["schema_profile"] != PROFILE:
                    raise DataError("schema_profile_mismatch", 503)
                if time.monotonic() - start > self.limits.snapshot_seconds:
                    raise DataError("operation_timeout", 504)
            # 数据库事务已经结束，仍持同一 RootLease，避免复制中原件被准确清理。
            selected_rows, closure = self._closure(rows, scope)
            rows = selected_rows
            if scope['mode']=='selected' and scope.get('expected_closure_sha256')!=self.closure_digest(rows,closure):
                raise DataError('snapshot_changed')
            for table, table_rows in rows.items():
                write_entry("records/" + table + ".jsonl", json_lines(table_rows))
                if kind == "restore_checkpoint":
                    write_entry("checkpoint/" + table + ".jsonl", json_lines(table_rows), "normalized_checkpoint")
            write_entry("metadata/source_control.json", canonical(control).encode("utf-8"), "source_observation")
            write_entry("metadata/operation_history.jsonl", json_lines(history), "history_observation")
            write_entry("metadata/tombstones.jsonl", json_lines(tombstones), "deletion_observation")
            tomb_source = {r["entity_id"] for r in tombstones if r["entity_kind"] == "source"}
            copied = {}
            on_stage("copying")
            for version in rows["material_versions"]:
                bounded()
                original = Original(version["sha256"], int(version["size"]))
                item = {"source_id": version["source_id"], "version_id": version["id"], "original_filename": version["filename"],
                        "sha256": original.sha256, "size": str(original.size), "availability": "present", "reason": None}
                if version["source_id"] in tomb_source:
                    item.update(availability="deleted", reason="explicit_source_tombstone")
                elif original.sha256 not in copied:
                    try:
                        content = self.store.read(original, max_bytes=self.limits.original_bytes)
                    except (OSError, ValueError):
                        item.update(availability="missing_required", reason="original_unavailable_or_corrupt")
                    else:
                        write_entry("originals/" + original.sha256, content, "original_bytes")
                        if version["format"] in ("txt", "md"):
                            try: content.decode("utf-8-sig")
                            except UnicodeError: raise DataError("integrity_failed", 422) from None
                            write_entry("texts/" + original.sha256 + ".txt", content, "independent_text")
                        copied[original.sha256]=original.size
                elif copied[original.sha256]!=original.size:
                    item.update(availability='missing_required',reason='retained_version_size_mismatch')
                availability.append(item)
            present = {(r["memory_id"], r["version"]) for r in rows["learning_memory_bodies"]}
            heads = {r["memory_id"]: r for r in rows["learning_memories"]}
            for revision in rows["learning_memory_revisions"]:
                state = "revoked" if heads[revision["memory_id"]]["state"] == "revoked" else (
                    "present" if (revision["memory_id"], revision["version"]) in present else "missing_required")
                availability.append({"memory_id": revision["memory_id"], "version": revision["version"], "availability": state,
                                     "sha256": revision["body_sha256"], "reason": "revoked_body_excluded" if state == "revoked" else None})
            for operation in rows["activity_operations"]:
                if operation["state"] != "received": continue
                if not any(r["activity_id"] == operation["activity_id"] and r["operation_id"] == operation["operation_id"] for r in rows["activity_operation_results"]):
                    availability.append({"activity_id": operation["activity_id"], "operation_id": operation["operation_id"],
                                         "availability": "legacy_without_payload", "reason": "legacy_received_without_payload"})
            edges = self._edges(rows, availability)
            write_entry("references/reference_edges.jsonl", json_lines(edges), "references")
            for activity in rows["activities"]:
                def summary():
                    yield ('已保存活动 '+activity['id']+'\n\n以下额度为备份时点记录，执行已冻结。\n\n'+canonical(activity)).encode('utf-8')
                    for table in ('activity_operation_results','teaching_records','interview_records','html_artifacts'):
                        for row in rows[table]:
                            if row['activity_id']==activity['id']:yield ('\n\n'+table+'\n'+canonical(row)).encode('utf-8')
                write_entry("summaries/" + activity["id"] + ".txt", summary(), "independent_summary")
        missing = [r for r in availability if r["availability"] == "missing_required"]
        if missing and (kind != "portable_export" or not scope["allow_incomplete"]):
            raise DataError("package_incomplete")
        write_entry("codec_description.json", canonical({"profile": PROFILE, "columns": COLUMNS, "transformations": TRANSFORMS,
                    "bigint_encoding": "decimal_string", "text_encoding": "UTF-8 原字符串", "migration_sha256": MIGRATIONS}).encode("utf-8"), "codec_description")
        readme = ("RetroLume 已保存资料包\n\n这是 ZIP_STORED 普通文件。先核对 manifest.json 的成员长度和 SHA-256。"
                  "哈希只证明字节一致，不证明作者或执行权。texts 为原文本，records 为逐列 JSONL，summaries 为活动文本，"
                  "references 为来源关系。原 PDF 位于 originals，逐页提取与用户补充分别存放。\n"
                  "浏览器未提交草稿不在服务器备份。已撤销记忆正文排除；历史模型正文及旧备份不会随之后删除消失。"
                  "metadata 三文件与业务记录来自同一数据库时点，之后的删除和账只能作为独立旁证。\n"
                  "checkpoint 仅用于受信工厂建立永久只读的隔离副本。控制秘密、旧窗口、执行身份、预览控制和真实单调时钟均未迁入。"
                  "预算与未知预留保留原快照事实，不能认领、退款或继续调用。\n")
        write_entry("README.txt", readme.encode("utf-8"), "instructions")
        return SnapshotResult(root, point, control, entries, availability, rows, closure)

    @staticmethod
    def _closure(rows, scope):
        if scope["mode"] == "all": return rows, {"mode": "all", "automatically_added": {"source_ids": [], "activity_ids": []}}
        sources, activities, memories = set(scope["source_ids"]), set(scope["activity_ids"]), set()
        if not sources.issubset({r["id"] for r in rows["material_sources"]}) or not activities.issubset({r["id"] for r in rows["activities"]}):
            raise DataError("not_found", 404)
        changed = True
        while changed:
            old = (len(sources), len(activities), len(memories))
            for r in rows["activity_scope_sources"]:
                if r["activity_id"] in activities: sources.add(r["source_id"])
            for r in rows["activity_memory_choices"]:
                if r["activity_id"] in activities: memories.add(r["memory_id"])
            for r in rows["learning_memory_dependencies"]:
                if r["memory_id"] in memories:
                    if r["source_id"]: sources.add(r["source_id"])
                    if r["origin_activity_id"]: activities.add(r["origin_activity_id"])
                    if r["upstream_memory_id"]: memories.add(r["upstream_memory_id"])
            changed = old != (len(sources), len(activities), len(memories))
        versions = {r["id"] for r in rows["material_versions"] if r["source_id"] in sources}
        candidates = {r["id"] for r in rows["pdf_review_candidates"] if r["source_id"] in sources}
        selected = {}
        for table, values in rows.items():
            if table == "material_sources": predicate=lambda r:r['id'] in sources
            elif table == "material_versions": predicate=lambda r:r['source_id'] in sources
            elif table == "activities": predicate=lambda r:r['id'] in activities
            elif table == "pdf_review_candidates": predicate=lambda r:r['id'] in candidates
            elif table.startswith("pdf_"): predicate=lambda r:r['version_id'] in versions
            elif table.startswith("learning_memory") or table == "learning_memories": predicate=lambda r:r['memory_id'] in memories
            else: predicate=lambda r:r['activity_id'] in activities
            selected[table] = FilteredRows(values,predicate)
        return selected, {"mode": "selected", "source_ids": sorted(sources), "activity_ids": sorted(activities),
                          "memory_ids": sorted(memories), "automatically_added": {"source_ids": sorted(sources - set(scope["source_ids"])),
                          "activity_ids": sorted(activities - set(scope["activity_ids"]))}}

    @staticmethod
    def _edges(rows, availability):
        import json
        active = {r["id"]: r for r in rows["material_sources"]}
        versions = {r["id"]: r for r in rows["material_versions"]}
        unavailable = {r["version_id"]: r["availability"] for r in availability if "version_id" in r}
        def walk(value, location):
            if isinstance(value, dict):
                if value.get("source_id") and (value.get("version_id") or value.get("source_version_id")):
                    sid, vid = value["source_id"], value.get("version_id", value.get("source_version_id"))
                    source, version = active.get(sid), versions.get(vid)
                    status = unavailable.get(vid, "missing_required" if version is None else "present")
                    qualification = "current" if source and source["current_version"] == vid and status == "present" else status if status != "present" else "historical"
                    yield {"location": location, "reference": value, "qualification_at_snapshot": qualification,
                           "available_for_current_use": qualification == "current"}
                for key, child in value.items(): yield from walk(child, location + "/" + key)
            elif isinstance(value, list):
                for index, child in enumerate(value): yield from walk(child, location + "/" + str(index))
        for table, values in rows.items():
            for index, row in enumerate(values):
                yield from walk(row, f"{table}/{index}")
                for key in ("payload", "source_refs", "context_body", "body", "local_body"):
                    if isinstance(row.get(key), str):
                        try: value = json.loads(row[key])
                        except ValueError: continue
                        yield from walk(value, f"{table}/{index}/{key}")
