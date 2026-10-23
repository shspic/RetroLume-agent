"""准确资料墓碑与清理；原记忆撤销和 M3 清理继续由既有实现负责。"""
import asyncio
import math
import time
from uuid import uuid4
from .codec import plain
from .contracts import DataError, DataJobCommand, Limits, canonical, digest, uuid
from .operations import Operation, acknowledge_unstarted, joined_thread


class _CleanupAttempt(Operation):
    """Fresh, bounded cleanup only; never restores the original execution ticket.

    The source tombstone must be read back from PG before any cleanup or success.
    The original execution/admission remains immutable journal history. This
    attempt cannot admit a tombstone, launch work, or extend a Q approval.
    """
    def __init__(self, hub, job_id, seconds):
        from .operations import CLOCK_DOMAIN
        if not math.isfinite(seconds) or seconds <= 0:
            raise DataError('operation_timeout',504)
        self.hub,self.job_id,self.actor=hub,job_id,str(uuid4())
        now=time.monotonic_ns()
        self.deadline_ns=now+int(seconds*1e9)
        self.admission=None
        self.tombstone=None
        self.clock_domain=CLOCK_DOMAIN
        def begin(job):
            execution=job.get('execution') or {}
            if (job['kind']!='source_delete' or job.get('execution_protocol')!=2
                or job.get('completion_protocol')!=1
                or (execution.get('admission') or {}).get('phase')!='source_tombstone_commit'
                or not (execution.get('admission') or {}).get('ticket')):
                raise DataError('operation_authority_unknown')
            if job['state'] not in ('deleted_pending','deletion_unconfirmed'):
                raise DataError('request_conflict')
            self.original_execution=canonical(execution)
            return {'stage':'cleanup_retry','cleanup_execution':{
                'clock_domain':self.clock_domain,'actor_id':self.actor,
                'started_ns':now,'deadline_ns':self.deadline_ns},'cleanup_confirmation':None}
        self.revision=hub.change_job(job_id,begin)['revision']

    def _validate(self,job,*,deadline=True):
        from .operations import CLOCK_DOMAIN
        attempt=job.get('cleanup_execution') or {}
        if (CLOCK_DOMAIN!=self.clock_domain or attempt.get('clock_domain')!=self.clock_domain
            or attempt.get('actor_id')!=self.actor or attempt.get('deadline_ns')!=self.deadline_ns
            or canonical(job.get('execution'))!=self.original_execution):
            raise DataError('operation_authority_unknown')
        if job['kind']!='source_delete' or job['state'] not in ('deleted_pending','deletion_unconfirmed','deleted'):
            raise DataError('request_conflict')
        if job['revision']!=self.revision:raise DataError('request_conflict')
        if deadline:self.remaining()

    def admit(self,phase):
        raise DataError('operation_authority_unknown')

    def confirm_tombstone(self,tomb):
        self.check()
        job=self.hub.execution_job(self.job_id);scope=job['scope']
        if (tomb.get('entity_kind')!='source' or str(tomb.get('entity_id'))!=scope['source_id']
            or tomb.get('business_id_observed')!=job['business_key']
            or tomb.get('manifest_sha256')!=scope['impact_sha256']
            or tomb.get('effective_revision')!=scope['expected_revision']+1):
            raise DataError('deletion_unconfirmed',503)
        self.tombstone=str(tomb['tombstone_id'])

    def finish(self,state,stage=None,**changes):
        if self.tombstone is None or state not in ('deleted','deleted_pending'):
            raise DataError('operation_authority_unknown')
        def finish(job):
            self._validate(job)
            if job['state'] not in ('deleted_pending','deletion_unconfirmed') or job.get('cleanup_confirmation'):
                raise DataError('request_conflict')
            return {**changes,'state':state,'stage':stage or state,'cleanup_confirmation':None}
        self.revision=self.hub.change_job(self.job_id,finish)['revision']
        confirmed_ns=time.monotonic_ns()
        def confirm(job):
            self._validate(job)
            return {'cleanup_confirmation':{'actor_id':self.actor,'clock_domain':self.clock_domain,
                'confirmed_ns':confirmed_ns,'tombstone_id':self.tombstone}}
        receipt=self.hub.change_job(self.job_id,confirm)
        self.revision=receipt['revision']
        return receipt

    def fail(self,error,*,cleanup_complete,state='deletion_unconfirmed',**facts):
        def fail(job):
            self._validate(job,deadline=False)
            return {**facts,'state':'deletion_unconfirmed','stage':'deletion_unconfirmed',
                'cleanup_confirmation':None,
                'error_code':error.code if isinstance(error,DataError) else 'storage_unavailable'}
        return self.hub.change_job(self.job_id,fail)


class SourceDeletionService:
    def __init__(self, hub, repository, references, gate, *, stop_affected=None, limits=None):
        self.hub, self.repository, self.references, self.gate = hub, repository, references, gate
        self.stop_affected = stop_affected
        self.limits = limits or Limits()

    @staticmethod
    def _memories(connection,source_id):
        return plain(connection.execute("""WITH RECURSIVE affected AS(
          SELECT memory_id FROM public.learning_memory_dependencies WHERE source_id=%s
          UNION SELECT d.memory_id FROM public.learning_memory_dependencies d JOIN affected a ON d.upstream_memory_id=a.memory_id
        ) SELECT r.memory_id,r.version FROM public.learning_memory_revisions r
          WHERE memory_id IN(SELECT memory_id FROM affected) ORDER BY memory_id,version""",(source_id,)).fetchall())

    @staticmethod
    def _activities(connection,source_id):
        # 历史正文和记忆传递依赖同样属于影响范围，不能只看当前 scope。
        return plain(connection.execute("""WITH RECURSIVE memories AS(
          SELECT memory_id FROM public.learning_memory_dependencies WHERE source_id=%(sid)s
          UNION SELECT d.memory_id FROM public.learning_memory_dependencies d JOIN memories m ON d.upstream_memory_id=m.memory_id
        ), affected AS(
          SELECT activity_id FROM public.activity_scope_sources WHERE source_id=%(sid)s
          UNION SELECT activity_id FROM public.activity_memory_choices WHERE memory_id IN(SELECT memory_id FROM memories)
          UNION SELECT activity_id FROM public.teaching_records WHERE jsonb_path_exists(source_refs::jsonb,'$.** ? (@.source_id == $sid)',jsonb_build_object('sid',%(sid)s::text))
          UNION SELECT activity_id FROM public.interview_records WHERE jsonb_path_exists(source_refs::jsonb,'$.** ? (@.source_id == $sid)',jsonb_build_object('sid',%(sid)s::text))
          UNION SELECT activity_id FROM public.html_commands WHERE jsonb_path_exists(context_body::jsonb,'$.** ? (@.source_id == $sid)',jsonb_build_object('sid',%(sid)s::text))
          UNION SELECT activity_id FROM public.activity_operation_results WHERE jsonb_path_exists(payload::jsonb,'$.** ? (@.source_id == $sid)',jsonb_build_object('sid',%(sid)s::text))
        ) SELECT DISTINCT activity_id FROM affected ORDER BY activity_id""",{'sid':source_id}).fetchall())

    def _impact(self, connection, source_id, expected_revision, *, lock=False):
        source = connection.execute("SELECT id,title,current_version,revision FROM public.material_sources WHERE id=%s" + (" FOR UPDATE" if lock else ""), (source_id,)).fetchone()
        if source is None: raise DataError("not_found", 404)
        if connection.execute("SELECT 1 FROM public.data_tombstones WHERE entity_kind='source' AND entity_id=%s", (source_id,)).fetchone():
            raise DataError("source_deleted")
        if source["revision"] != expected_revision: raise DataError("snapshot_changed")
        versions = plain(connection.execute("SELECT id,filename,format,sha256,size FROM public.material_versions WHERE source_id=%s ORDER BY id", (source_id,)).fetchall())
        if len(versions) > 50000: raise DataError("capacity_exceeded", 413)
        activities = self._activities(connection,source_id)
        memories = self._memories(connection,source_id)
        candidates = plain(connection.execute("SELECT id,version_id,status FROM public.pdf_review_candidates WHERE source_id=%s ORDER BY id", (source_id,)).fetchall())
        activity_ids = [r["activity_id"] for r in activities]
        previews = plain(connection.execute("SELECT preview_id,activity_id,state,reserve_seconds,elapsed_seconds FROM public.html_preview_sessions WHERE activity_id=ANY(%s::uuid[]) ORDER BY preview_id", (activity_ids,)).fetchall())
        targets = []
        for version in versions:
            item = {"sha256": version["sha256"], "size": str(version["size"])}
            if item not in targets: targets.append(item)
        targets.sort(key=lambda v: (v["sha256"], v["size"]))
        sharing = []
        for item in targets:
            count = connection.execute("""SELECT count(*) AS count FROM public.material_versions v WHERE v.sha256=%s AND v.source_id<>%s
                AND NOT EXISTS(SELECT 1 FROM public.data_tombstones t WHERE t.entity_kind='source' AND t.entity_id=v.source_id)""",
                                       (item["sha256"], source_id)).fetchone()["count"]
            sharing.append({"sha256": item["sha256"], "retained_versions_elsewhere": count})
        result = {"source_id": source_id, "expected_revision": expected_revision, "title": source["title"], "versions": versions,
                  "activities": activities, "memories": memories, "pdf_candidates": candidates, "previews": previews,
                  "hash_size_targets": targets, "shared_originals": sharing,
                  "scope": "删除本条资料全部版本的回查内容；保留历史关系和旧备份"}
        return {**result, "impact_sha256": digest(canonical(result))}

    def preview(self, source_id, expected_revision):
        source_id = uuid(source_id)
        if type(expected_revision) is not int or expected_revision < 0: raise DataError("invalid_input", 400)
        with self.repository.connection(readonly=True, repeatable=True) as connection:
            return self._impact(connection, source_id, expected_revision)

    async def confirm(self, source_id, expected_revision, impact_sha, business_key):
        if 'q' in self.hub.state():
            from .q_store import QAuthority
            async with QAuthority(self.hub).async_policy():
                with self.hub.operation_lock.acquire(True,timeout=1):
                    return await self._confirm(source_id,expected_revision,impact_sha,business_key)
        with self.hub.operation_lock.acquire(True,timeout=1):
            return await self._confirm(source_id,expected_revision,impact_sha,business_key)

    async def retry_cleanup(self,job_id):
        job=self.hub.state()['jobs'].get(uuid(job_id))
        if job is None or job['kind']!='source_delete':raise DataError('not_found',404)
        if job['state'] not in ('deleted_pending','deletion_unconfirmed'):raise DataError('operation_already_published')
        scope=job['scope']
        return await self.confirm(scope['source_id'],scope['expected_revision'],scope['impact_sha256'],job['business_key'])

    async def _confirm(self, source_id, expected_revision, impact_sha, business_key):
        source_id = uuid(source_id)
        command = DataJobCommand("source_delete", business_key, {"source_id": source_id, "expected_revision": expected_revision, "impact_sha256": impact_sha})
        job = self.hub.create_or_get_job(command, self.gate.context())
        if job['state'] == 'cancel_requested': return acknowledge_unstarted(self.hub, job['job_id'])
        if job['state'] not in ('prepared','deleted_pending','deletion_unconfirmed'):return self.hub.reconcile(job['job_id'])
        retry=job['state']!='prepared'
        operation = None
        def tombstone():
            from psycopg.types.json import Jsonb
            with self.gate.acquire(operation=operation):
                with self.references.lease.acquire(True, timeout=operation.remaining(30)):
                    with self.repository.connection(operation=operation) as connection:
                        connection.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,113))", (self.references.root_id,))
                        if retry:
                            tomb=connection.execute("SELECT * FROM public.data_export_tombstones_v1 WHERE entity_kind='source' AND entity_id=%s AND business_id_observed=%s AND manifest_sha256=%s",
                                (source_id,business_key,impact_sha)).fetchone()
                            if tomb is None:raise DataError('deletion_unconfirmed',503)
                            if tomb['effective_revision']!=expected_revision+1:raise DataError('request_conflict')
                            return {'hash_size_targets':tomb['hash_size_targets'],'activities':self._activities(connection,source_id),
                                    'memories':self._memories(connection,source_id)},plain(tomb)
                        impact = self._impact(connection, source_id, expected_revision, lock=True)
                        if impact["impact_sha256"] != impact_sha: raise DataError("snapshot_changed")
                        connection.execute('SELECT memory_id FROM public.learning_memories WHERE memory_id=ANY(%s::uuid[]) ORDER BY memory_id FOR UPDATE',
                            ([r['memory_id'] for r in impact['memories']],)).fetchall()
                        connection.execute('SELECT id FROM public.activities WHERE id=ANY(%s::uuid[]) ORDER BY id FOR UPDATE',
                            ([r['activity_id'] for r in impact['activities']],)).fetchall()
                        operation.admit('source_tombstone_commit')
                        value = connection.execute("SELECT public.data_source_delete(%s,%s,%s,%s,%s,%s) AS value",
                            (source_id, expected_revision, business_key, impact_sha, Jsonb(impact["hash_size_targets"]), self.references.maintenance_key)).fetchone()["value"]
                    # 这里只表示墓碑 COMMIT 已确认，物理结果和预览停止各自记录。
                    return impact, value
        tombstone_confirmed=False
        try:
            operation = _CleanupAttempt(self.hub,job['job_id'],self.limits.operation_seconds) if retry else Operation(self.hub, job['job_id'], self.limits.operation_seconds, 'checking_deletion')
            impact, tomb = await joined_thread(tombstone)
            if retry:operation.confirm_tombstone(tomb)
            tombstone_confirmed=True
            self.hub.commit("deletion.observe", plain(tomb))
            operation.check()
            stop_state = "not_owned"
            if self.stop_affected is not None:
                stop_state = await asyncio.wait_for(self.stop_affected([r["activity_id"] for r in impact["activities"]]), operation.remaining())
            operation.check()
            from .q_cleanup import cleanup
            q_outcomes=await joined_thread(cleanup,self.hub,source_ids=[source_id],
                memory_ids=[row['memory_id'] for row in impact['memories']])
            operation.check()
            outcomes = await joined_thread(self.references.exclusive_cleanup, impact["hash_size_targets"], operation=operation)
            def observe():
                from psycopg.types.json import Jsonb
                with self.gate.acquire(operation=operation):
                    with self.repository.connection(operation=operation) as connection:
                        connection.execute('SELECT public.data_cleanup_observe(%s,%s,%s,%s)',
                            (tomb['tombstone_id'],impact_sha,Jsonb(outcomes),self.references.maintenance_key))
            try:await joined_thread(observe)
            except DataError:pass
            uncertain = any(r["state"] == "physical_result_unknown" for r in outcomes+q_outcomes) or stop_state=='unconfirmed'
            receipt = {"source_id": source_id, "tombstone_id": tomb["tombstone_id"], "effective_revision": tomb["effective_revision"],
                       "cleanup": outcomes,"q_cleanup":q_outcomes, "preview_stop": stop_state, "history_and_old_backups_retained": True}
            from uuid import uuid4
            receipt_id=str(uuid4())
            receipt_sha=self.hub.save_artifact("receipts", receipt_id, canonical(receipt).encode("utf-8"), operation.check)
            return operation.finish('deleted_pending' if uncertain else 'deleted',
                                      stage="cleanup_unconfirmed" if uncertain else "deleted",
                                      receipt_id=receipt_id,receipt_sha256=receipt_sha,
                                      counts={"originals": len(outcomes), "unconfirmed": sum(r["state"] == "physical_result_unknown" for r in outcomes+q_outcomes)})
        except BaseException as error:
            try:
                rejected=(not tombstone_confirmed and isinstance(error,DataError)
                          and error.code in ('snapshot_changed','request_conflict','not_found','source_deleted'))
                state='failed' if rejected else 'deletion_unconfirmed'
                if operation is not None:
                    operation.fail(error, cleanup_complete=operation.admission is None, state=state)
                elif isinstance(error, DataError) and error.code == 'operation_cancelled':
                    acknowledge_unstarted(self.hub, job['job_id'])
            except (DataError, OSError): pass
            if isinstance(error, Exception) and not isinstance(error, DataError):
                raise DataError('storage_unavailable', 503) from None
            raise
