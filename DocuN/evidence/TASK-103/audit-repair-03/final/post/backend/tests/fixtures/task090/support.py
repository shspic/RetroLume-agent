"""TASK090专用合成库准备与定向清理；不执行迁移、不回退用户DSN。"""
import asyncio,os,unittest
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from app.activities import *
from app.capabilities.contracts import *
from app.runtime import psycopg_compatible_loop_factory
DSN=os.environ.get("RETROLUME_SCOPE_TEST_DATABASE_URL","")
class PGBase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self):
        self._asyncioRunner=asyncio.Runner(loop_factory=psycopg_compatible_loop_factory)
    async def asyncSetUp(self):
        self.ids=[];self.sources=[];self.ledger=PostgresAdmissionLedger(DSN)
        identity=await self.row("SELECT current_database() AS db,current_user AS role")
        assert identity=={"db":"retrolume_task090_scope","role":"retrolume_task090_synth"}
        self.source=await self.new_source();self.activity=str(uuid4());self.ids.append(self.activity)
        await self.ledger.create_activity(ActivitySpec(self.activity,(self.source,),datetime.now(timezone.utc)+timedelta(minutes=10),8,800,100,65536,256,300,(("deepseek_chat_completions","synthetic-model"),)))
    async def asyncTearDown(self):
        async with await psycopg.AsyncConnection.connect(DSN) as c:
            for a in self.ids:
                for table in ("activity_operation_results","activity_operations","activity_allowed_models","activity_scope_sources"):
                    await c.execute("DELETE FROM "+table+" WHERE activity_id=%s",(a,))
                await c.execute("DELETE FROM activities WHERE id=%s",(a,))
            for source,version in self.sources:
                await c.execute("UPDATE material_sources SET current_version=NULL WHERE id=%s",(source,))
                await c.execute("DELETE FROM material_versions WHERE source_id=%s",(source,))
                await c.execute("DELETE FROM material_sources WHERE id=%s",(source,))
    async def rows(self,sql,params=()):
        async with await psycopg.AsyncConnection.connect(DSN,row_factory=dict_row) as c:
            return await (await c.execute(sql,params)).fetchall()
    async def row(self,sql,params=()):return (await self.rows(sql,params))[0]
    async def sql(self,sql,params=()):
        async with await psycopg.AsyncConnection.connect(DSN) as c:await c.execute(sql,params)
    async def new_source(self):
        source,version=str(uuid4()),str(uuid4());self.sources.append((source,version))
        async with await psycopg.AsyncConnection.connect(DSN) as c:
            await c.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'TASK090-synthetic',0)",(source,))
            await c.execute("INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'synthetic.txt','txt',%s,1)",(version,source,'8'*64))
            await c.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s",(version,source))
        return SourceSnapshot(source,version,1)
    async def claim(self):
        return await self.ledger.claim_lease(self.activity,"executor090",lease_seconds=120,window_seconds=30)
    def intent(self,lease,key='P',ref=None):
        return AdmissionIntent(CallContext(activity_id=self.activity,operation_id=key,executor_id=lease.executor_id,execution_generation=lease.execution_generation,scope_revision=lease.scope_revision),Provider.DEEPSEEK_CHAT_COMPLETIONS,'synthetic-model',512,40,(),ref)
    def outcome(self):
        fmt,payload,sha=build_business_payload(json_object={"parent":"低信任历史"})
        return LedgerOutcome(LedgerDisposition.RECEIVED,payload_format=fmt,payload=payload,payload_sha256=sha)
    async def parent(self):
        lease=await self.claim();permit=await self.ledger.admit(self.intent(lease));await self.ledger.mark_dispatch_started(permit)
        await self.ledger.record_outcome(permit,self.outcome());snap=await self.ledger.read_committed_result(self.activity,'P')
        return lease,ResultConsumptionRef(activity_id=self.activity,operation_id='P',scope_revision=snap.scope_revision,payload_sha256=snap.payload_sha256)
    async def account(self):
        return await self.row("SELECT status,execution_generation,executor_id,lease_expires_at,dispatch_closed,deadline_at,max_running_seconds,running_reserved_seconds,running_settled_seconds,requests_reserved,cost_reserved_microunits FROM activities WHERE id=%s",(self.activity,))
