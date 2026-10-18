"""TASK090范围修订与真实锁屏障。"""
import asyncio,json,unittest
from dataclasses import replace
from unittest.mock import patch
from app.activities import *
from app.capabilities.contracts import AdmissionDenied
from tests.fixtures.task090.support import PGBase,DSN

class ScopeOfflineTests(unittest.TestCase):
    def test_strict_sources_and_revision_boundaries(self):
        from uuid import uuid4
        source=SourceSnapshot(str(uuid4()),str(uuid4()),1)
        for values in ((source,source),(replace(source,revision=True),),(replace(source,revision=-1),),tuple(source for _ in range(129))):
            with self.assertRaises(ValueError):PostgresAdmissionLedger._normalize_scope(values)
        self.assertEqual(PostgresAdmissionLedger._normalize_scope(()),())
        with self.assertRaises(ValueError):PostgresAdmissionLedger._normalize_scope([{'source_id':source.source_id}])

@unittest.skipUnless(DSN,'专用TASK090合成库未注入')
class ScopePostgresTests(PGBase):
    async def test_v1_replace_cas_noop_empty_budget(self):
        before=await self.account();second=await self.new_source()
        scope=await self.ledger.revise_scope(self.activity,1,(second,));self.assertEqual(scope.scope_revision,2)
        self.assertEqual(scope,await self.ledger.inspect_scope(self.activity));self.assertEqual(before,await self.account())
        row=await self.row("SELECT xmin::text AS xmin FROM activities WHERE id=%s",(self.activity,))
        self.assertEqual(scope,await self.ledger.revise_scope(self.activity,2,(second,)))
        self.assertEqual(row,await self.row("SELECT xmin::text AS xmin FROM activities WHERE id=%s",(self.activity,)))
        with self.assertRaisesRegex(ScopeConflict,'scope_conflict'):await self.ledger.revise_scope(self.activity,1,(self.source,))
        self.assertEqual((await self.ledger.revise_scope(self.activity,2,())).scope_revision,3)
        with self.assertRaises(ActivityLedgerConflict):await self.claim()
        self.assertEqual((await self.ledger.inspect_scope(self.activity)).sources,())
    async def test_v1_upper_bound_missing_and_response_loss(self):
        self.assertIsNone(await self.ledger.inspect_scope('00000000-0000-0000-0000-000000000090'))
        await self.sql("UPDATE activities SET scope_revision=2147483647 WHERE id=%s",(self.activity,))
        second=await self.new_source()
        with self.assertRaisesRegex(ActivityLedgerConflict,'scope_revision_limit'):await self.ledger.revise_scope(self.activity,2147483647,(second,))
        self.assertEqual((await self.ledger.inspect_scope(self.activity)).scope_revision,2147483647)
        await self.sql("UPDATE activities SET scope_revision=1 WHERE id=%s",(self.activity,))
        original=self.ledger._transaction
        async def lose(operation):
            await original(operation);raise RuntimeError('synthetic lost response after commit')
        with patch.object(self.ledger,'_transaction',lose):
            with self.assertRaises(RuntimeError):await self.ledger.revise_scope(self.activity,1,(second,))
        scope=await self.ledger.inspect_scope(self.activity);self.assertEqual(scope.scope_revision,2)
        with self.assertRaises(ScopeConflict):await self.ledger.revise_scope(self.activity,1,(second,))
        self.assertEqual(scope,await self.ledger.inspect_scope(self.activity))
    async def test_v2_change_commits_before_old_disjoint_hint(self):
        second=await self.new_source();hint_ready=asyncio.Event();release=asyncio.Event();original=self.ledger._source_rows;first=True
        async def pause(c,a):
            nonlocal first
            rows=await original(c,a)
            if first:
                first=False;hint_ready.set();await asyncio.wait_for(release.wait(),3)
            return rows
        with patch.object(self.ledger,'_source_rows',pause):
            old=asyncio.create_task(self.ledger.inspect_window(self.activity))
            try:
                await asyncio.wait_for(hint_ready.wait(),3)
                await PostgresAdmissionLedger(DSN).revise_scope(self.activity,1,(second,))
                release.set()
                with self.assertRaisesRegex(ScopeConflict,'scope_conflict'):await asyncio.wait_for(old,3)
            finally:
                release.set();await asyncio.gather(old,return_exceptions=True)
        self.assertEqual((await self.ledger.inspect_scope(self.activity)).sources,(second,))
    async def test_v2_old_transaction_locks_before_revision(self):
        second=await self.new_source();locked=asyncio.Event();release=asyncio.Event();pid=[];original=self.ledger._verify_scope_hint
        async def pause(c,a,h):
            await original(c,a,h);pid.append((await (await c.execute('SELECT pg_backend_pid() AS pid')).fetchone())['pid']);locked.set();await asyncio.wait_for(release.wait(),4)
        with patch.object(self.ledger,'_verify_scope_hint',pause):
            old=asyncio.create_task(self.ledger.inspect_window(self.activity));new=None
            try:
                await asyncio.wait_for(locked.wait(),3);new=asyncio.create_task(PostgresAdmissionLedger(DSN).revise_scope(self.activity,1,(second,)))
                async def barrier():
                    while True:
                        rows=await self.rows('SELECT pid FROM pg_stat_activity WHERE %s=ANY(pg_blocking_pids(pid))',(pid[0],))
                        if rows:return rows
                        await asyncio.sleep(0)
                blocked=await asyncio.wait_for(barrier(),3);print(json.dumps({'event':'pg_lock_barrier','blocker':pid[0],'blocked':blocked}),flush=True)
                self.assertFalse(new.done());release.set();self.assertTrue((await old).sources_valid);self.assertEqual((await new).scope_revision,2)
            finally:
                release.set();await asyncio.gather(*[x for x in (old,new) if x],return_exceptions=True)
    async def test_v2_source_replaced_new_scope_invalid(self):
        await self.sql('UPDATE material_sources SET revision=revision+1 WHERE id=%s',(self.source.source_id,))
        with self.assertRaisesRegex(ActivityLedgerConflict,'source_invalid'):await self.ledger.revise_scope(self.activity,1,(self.source,))
        fresh=replace(self.source,revision=2);self.assertEqual((await self.ledger.revise_scope(self.activity,1,(fresh,))).scope_revision,2)
    async def test_v2_empty_or_obsolete_sources_do_not_block_close_settle_cancel(self):
        lease=await self.claim();await self.ledger.revise_scope(self.activity,1,())
        await self.ledger.begin_window_close(self.activity,lease.executor_id,lease.execution_generation)
        self.assertEqual(await self.ledger.settle_execution_window(self.activity,lease.executor_id,lease.execution_generation,window_seconds=30,elapsed_seconds=1),SettleResult.SETTLED)
        before=await self.account();await self.ledger.cancel_activity(self.activity);self.assertEqual((await self.account())['running_settled_seconds'],before['running_settled_seconds'])
        with self.assertRaises(ActivityLedgerConflict):await self.ledger.revise_scope(self.activity,2,(self.source,))
        self.assertEqual(await self.ledger.recover_unknown(self.activity),0)
    async def test_v2_obsolete_source_cancel_folds_once(self):
        lease=await self.claim();await self.sql('UPDATE material_sources SET revision=revision+1 WHERE id=%s',(self.source.source_id,))
        g=await self.ledger.cancel_activity(self.activity);before=await self.account();self.assertEqual(before['running_settled_seconds'],30)
        self.assertEqual(await self.ledger.cancel_activity(self.activity),g)
        with self.assertRaises(ActivityLedgerConflict):await self.ledger.settle_execution_window(self.activity,lease.executor_id,lease.execution_generation,window_seconds=30,elapsed_seconds=1)
        self.assertEqual(before,await self.account())

    async def test_v2_source_version_race_uses_authority_and_lock_barrier(self):
        import psycopg
        from psycopg.rows import dict_row
        from app.materials.repository import PostgresMaterials
        # 既有同步资料权威save自身锁来源并revision+1；不改其实现。
        locked=asyncio.Event();release=asyncio.Event();pid=[];original=self.ledger._verify_scope_hint
        async def pause(c,a,h):
            await original(c,a,h);pid.append((await (await c.execute('SELECT pg_backend_pid() AS pid')).fetchone())['pid']);locked.set();await asyncio.wait_for(release.wait(),4)
        with patch.object(self.ledger,'_verify_scope_hint',pause):
            inspect=asyncio.create_task(self.ledger.inspect_window(self.activity));replace_task=None
            try:
                await asyncio.wait_for(locked.wait(),3)
                materials=PostgresMaterials(DSN)
                replace_task=asyncio.create_task(asyncio.to_thread(materials.save,source_id=self.source.source_id,expected_version=self.source.version_id,filename='new.txt',format='txt',sha256='7'*64,size=1))
                async def barrier():
                    while True:
                        blocked=await self.rows('SELECT pid FROM pg_stat_activity WHERE %s=ANY(pg_blocking_pids(pid))',(pid[0],))
                        if blocked:return blocked
                        await asyncio.sleep(0)
                observed=await asyncio.wait_for(barrier(),3);print(json.dumps({'event':'source_authority_lock_barrier','blocker':pid[0],'blocked':observed}),flush=True)
                release.set();self.assertTrue((await inspect).sources_valid);new=await replace_task
            finally:
                release.set();await asyncio.gather(*[x for x in (inspect,replace_task) if x],return_exceptions=True)
        with self.assertRaisesRegex(ActivityLedgerConflict,'source_invalid'):await self.ledger.revise_scope(self.activity,1,(self.source,))
        self.assertEqual((await self.ledger.revise_scope(self.activity,1,(SourceSnapshot(self.source.source_id,new['version_id'],new['revision']),))).scope_revision,2)
