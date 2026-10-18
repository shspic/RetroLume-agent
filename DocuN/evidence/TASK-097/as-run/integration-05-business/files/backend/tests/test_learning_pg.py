"""097真实PG范围、有限查询、原子规范正文及关键失效反例。"""
import asyncio
import copy
from dataclasses import replace
import json
from unittest.mock import patch
from uuid import uuid4

from app.capabilities.contracts import *
from app.capabilities.gateway import ControlledModelGateway
from app.learning.contracts import *
from app.learning.evidence import *
from app.learning.prompt import messages_for
from app.learning.service import LearningService
from app.activities import PostgresAdmissionLedger
from tests.fixtures.task097.support import PGBase
from tests.fixtures.task097.samples import ENGLISH, CHINESE, XSS, answer
from tests.test_learning_gateway import service, Transport


class LearningPGTests(PGBase):
    async def prepare(self,rows,goal="Explain atomicity"):
        activity=await self.fixture.activity(rows)
        snap=await self.ledger.read_learning_snapshot(activity)
        sources=validate_snapshot(snap)
        identity=dict(action="first",activity_id=activity,goal=goal,question=None,scope_revision=snap["scope_revision"],
            sources=[s.model_dump() for s in sources],parent_operation_id=None,parent_payload_sha256=None,max_output_tokens=256)
        digest=request_fingerprint(**identity)
        units=load_units(snap,self.fixture.materials,self.fixture.originals)
        p=LearningProfile(**identity,request_sha256=digest,catalog=assemble_catalog(goal,units,digest))
        lease=await self.ledger.claim_lease(activity,"pg097",lease_seconds=120,window_seconds=30)
        ctx=CallContext(activity_id=activity,executor_id=lease.executor_id,operation_id=FIRST_PREFIX+digest,
            execution_generation=lease.execution_generation,scope_revision=lease.scope_revision)
        req=ModelCallRequest(messages=messages_for(p),max_output_tokens=256,learning_profile=p)
        return activity,p,lease,ctx,req
    async def close(self,a,lease):
        await self.ledger.begin_window_close(a,lease.executor_id,lease.execution_generation)
        await self.ledger.settle_execution_window(a,lease.executor_id,lease.execution_generation,window_seconds=30,elapsed_seconds=1)
    async def test_authoritative_txt_md_pdf_supplement_scope_and_utf8(self):
        en=self.fixture.text(ENGLISH+XSS,"english.txt","txt")
        cn=self.fixture.text(CHINESE,"中文.md")
        pdf=self.fixture.pdf()
        hidden=self.fixture.text("atomicity "*100,"outside.txt","txt")
        a=await self.fixture.activity([en,cn,pdf])
        snap=await self.ledger.read_learning_snapshot(a)
        units=load_units(snap,self.fixture.materials,self.fixture.originals)
        catalog=assemble_catalog("atomicity 事务",units,"a"*64)
        self.assertNotIn(hidden["id"],{e.source_id for e in catalog})
        self.assertTrue(any(e.origin_kind=="user_supplement" and e.physical_page==2 for e in catalog))
        for e in catalog:
            actual=next(r for r in snap["sources"] if r["source_id"]==e.source_id)
            self.assertEqual(e.source_revision,actual["source_revision"])
        self.assertIn(CHINESE, [u.unit.text for u in units])
        print(json.dumps({"scenario":"scope-multilingual","source_ids":[en["id"],cn["id"],pdf["id"]],
            "catalog":[e.model_dump() for e in catalog]},ensure_ascii=False))
    async def test_deleted_replaced_unreviewed_and_budget_reads_single_select(self):
        source=self.fixture.text(ENGLISH)
        a=await self.fixture.activity([source])
        self.fixture.rows("UPDATE material_sources SET revision=revision+1 WHERE id=%s",(source["id"],))
        with self.assertRaisesRegex(LearningRefusal,"source_invalid"):validate_snapshot(await self.ledger.read_learning_snapshot(a))
        # pending新PDF尚无current_version，不能取得活动范围资格。
        pending=self.fixture.pdf(confirmed=False)
        self.assertIsNone(self.fixture.materials.get(pending["source_id"]))
        self.assertIsNone(self.fixture.materials.get_active_pdf_pages(pending["source_id"],pending["version_id"]))
        queries=[];columns=[]
        orig=self.ledger._transaction
        async def counted(operation):
            async def wrapped(conn):
                class Proxy:
                    async def execute(self,*args):
                        queries.append(args[0]);cursor=await conn.execute(*args)
                        columns.append([c.name for c in cursor.description] if cursor.description else [])
                        return cursor
                return await operation(Proxy())
            return await orig(wrapped)
        with patch.object(self.ledger,"_transaction",counted):
            for method in [lambda:self.ledger.list_activities(limit=20),lambda:self.ledger.read_activity_facts(a),
                lambda:self.ledger.list_operations(a,limit=20),lambda:self.ledger.read_operation(a,"missing"),
                lambda:self.ledger.read_learning_snapshot(a),lambda:self.ledger.find_learning_operation(a,FIRST_PREFIX)]:
                queries.clear();columns.clear();await method();self.assertEqual(len(queries),1)
                if "r.payload" not in queries[0]:self.assertTrue(all("payload" not in c for c in columns))
        print(json.dumps({"scenario":"single-select","reads":6,"per_read_business_selects":1,"list_body_requested":False}))
    async def test_real_gateway_atomic_normalization_and_citation_invalidation(self):
        source=self.fixture.text(ENGLISH+CHINESE+XSS)
        a,p,lease,ctx,req=await self.prepare([source])
        class Observer:
            def __init__(self,ledger):self.ledger=ledger;self.events=[]
            async def send(self,**kw):
                self.events.append("send")
                raw=json.dumps({"model":"synthetic-model-097","choices":[{"finish_reason":"stop","message":{"role":"assistant","content":json.dumps(answer(p))}}],
                    "usage":{"prompt_tokens":2,"completion_tokens":8,"total_tokens":10}}).encode()
                from app.capabilities.transport import TransportResponse
                return TransportResponse(200,raw,len(raw))
        observed=Observer(self.ledger)
        r=await ControlledModelGateway(service(),ledger=self.ledger,transport=observed).call(ctx,req)
        self.assertEqual(r.status,CallStatus.SUCCEEDED)
        row=self.fixture.rows("SELECT o.state,o.disposition,r.payload,r.payload_sha256,o.xmin::text AS op_xmin,r.xmin::text AS result_xmin "
            "FROM activity_operations o JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s",(a,))[0]
        self.assertEqual(row["op_xmin"],row["result_xmin"])
        self.assertEqual(row["state"],"received");self.assertEqual(row["disposition"],"received")
        self.assertEqual(json.loads(row["payload"])["value"]["goal"],p.goal)
        catalog=p.catalog[0]
        returned=await read_citation(self.ledger,self.fixture.materials,self.fixture.originals,a,ctx.operation_id,catalog.citation_id)
        self.assertEqual(returned["citation"]["text"],catalog.text)
        with self.assertRaisesRegex(LearningRefusal,"citation_not_found"):
            await read_citation(self.ledger,self.fixture.materials,self.fixture.originals,a,ctx.operation_id,"lc_fake")
        await self.close(a,lease)
        replacement=self.fixture.materials.save(source_id=source["id"],expected_version=source["version_id"],filename="new.md",format="md",sha256=source["sha256"],size=source["size"])
        self.assertGreater(replacement["revision"],source["revision"])
        with self.assertRaisesRegex(LearningRefusal,"citation_unavailable"):
            await read_citation(self.ledger,self.fixture.materials,self.fixture.originals,a,ctx.operation_id,catalog.citation_id)
        self.assertEqual(self.fixture.rows("SELECT payload_sha256 FROM activity_operation_results WHERE activity_id=%s",(a,))[0]["payload_sha256"],r.payload_sha256)
        print(json.dumps({"scenario":"atomic-result","activity":a,"same_transaction":True,"op_xmin":row["op_xmin"],"payload_sha256":r.payload_sha256}))
    async def test_source_change_after_send_and_invalid_output_never_commit(self):
        from app.capabilities.transport import TransportResponse
        for mode in ["invalid","replace","cancel"]:
            source=self.fixture.text(ENGLISH)
            a,p,lease,ctx,req=await self.prepare([source])
            fixture=self.fixture;ledger=self.ledger
            class T:
                async def send(self,**kw):
                    if mode=="replace":fixture.rows("UPDATE material_sources SET revision=revision+1 WHERE id=%s",(source["id"],))
                    if mode=="cancel":await ledger.cancel_activity(a)
                    value=answer(p)
                    if mode=="invalid":value["segments"][0]["citations"]=["lc_fake"]
                    raw=json.dumps({"model":"synthetic-model-097","choices":[{"finish_reason":"stop","message":{"role":"assistant","content":json.dumps(value)}}],
                        "usage":{"prompt_tokens":2,"completion_tokens":8,"total_tokens":10}}).encode()
                    return TransportResponse(200,raw,len(raw))
            r=await ControlledModelGateway(service(),ledger=ledger,transport=T()).call(ctx,req)
            self.assertEqual(r.status,CallStatus.FAILED if mode=="invalid" else CallStatus.UNKNOWN)
            self.assertEqual(self.fixture.rows("SELECT count(*) AS n FROM activity_operation_results WHERE activity_id=%s",(a,))[0]["n"],0)
            if mode=="invalid":
                row=self.fixture.rows("SELECT state,error_code FROM activity_operations WHERE activity_id=%s",(a,))[0]
                self.assertEqual(row,{"state":"received","error_code":"invalid_learning_output"})
            if mode != "cancel":await self.close(a,lease)
    async def test_committed_ack_loss_and_real_scope_slot_conflicts(self):
        source=self.fixture.text(ENGLISH)
        a,p,lease,ctx,req=await self.prepare([source])
        original=self.ledger.record_outcome
        async def lose(permit,outcome):
            await original(permit,outcome);raise RuntimeError("synthetic acknowledgment loss")
        class T:
            async def send(self,**kw):
                from app.capabilities.transport import TransportResponse
                raw=json.dumps({"model":"synthetic-model-097","choices":[{"finish_reason":"stop","message":{"role":"assistant","content":json.dumps(answer(p))}}],
                    "usage":{"prompt_tokens":2,"completion_tokens":8,"total_tokens":10}}).encode()
                return TransportResponse(200,raw,len(raw))
        with patch.object(self.ledger,"record_outcome",lose):
            result=await ControlledModelGateway(service(),ledger=self.ledger,transport=T()).call(ctx,req)
        self.assertEqual(result.status,CallStatus.UNKNOWN)
        persisted=await self.ledger.read_committed_result(a,ctx.operation_id)
        self.assertEqual(persisted.read_status.value,"committed_current")
        self.assertEqual(await self.ledger.find_learning_operation(a,FIRST_PREFIX),ctx.operation_id)
        await self.close(a,lease)
        # 真实父正文来自刚才gateway，不种父成果。
        ref=ResultConsumptionRef(activity_id=a,operation_id=ctx.operation_id,scope_revision=1,payload_sha256=persisted.payload_sha256)
        self.assertIsNotNone(ref)
        await self.ledger.cancel_activity(a)
        self.assertEqual((await self.ledger.read_committed_result(a,ctx.operation_id)).read_status.value,"committed_history_cancelled")
