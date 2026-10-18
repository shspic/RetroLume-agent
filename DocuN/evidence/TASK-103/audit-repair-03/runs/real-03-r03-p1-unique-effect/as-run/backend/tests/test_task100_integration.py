"""真实 PG 的 G8 前置、单快照和零费边界；种子不冒充 Windows 链。"""
import json
from uuid import uuid4
from unittest.mock import patch
from tests.fixtures.task100.support import PGBase
from tests.fixtures.task100.seed_helpers import ready_answer,command,config
from app.learning.teaching_contracts import TeachingRefusal
from app.learning.teaching_service import TeachingService
from app.learning.teaching_views import public_record
from app.learning.teaching_api import _workspace_payload

class IntegrationPGTests(PGBase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.aid,self.source,self.eid,self.answer=await ready_answer(self.fixture)
        self.service=TeachingService(self.ledger,self.fixture.materials,self.fixture.originals)
    async def test_actual_frozen_context_binds_goal_path_exercise_answer(self):
        head=self.fixture.head(self.aid)
        cmd=command(head,'evaluate',{'confirmed':True,'exercise_record_id':self.eid,'answer_record_id':self.answer,'correction_record_id':None,'retry_of':None})
        frozen,identity=await self.service._freeze_model_context(self.aid,cmd,config())
        text=json.loads(frozen.messages[-1]['content'])
        self.assertIn('平均速度',text['goal']);self.assertEqual(text['task']['answer_text'],'120÷2=60m/s')
        self.assertEqual(len(frozen.reference_hashes),4)
        self.assertEqual(identity['goal_record_id'],str(head['goal_record_id']))
        receipt=await self.ledger.accept_teaching_command(self.aid,cmd,frozen)
        self.assertEqual(receipt.status,'accepted')
        self.assertTrue((await self.ledger.claim_teaching_launch(self.aid,cmd.business_key,cmd.request_sha256(self.aid)))['launch_allowed'])
    async def test_pending_closed_settled_state_is_launchable(self):
        self.fixture.rows('UPDATE activities SET dispatch_closed=true WHERE id=%s',(self.aid,))
        head=self.fixture.head(self.aid)
        cmd=command(head,'evaluate',{'confirmed':True,'exercise_record_id':self.eid,'answer_record_id':self.answer,'correction_record_id':None,'retry_of':None})
        frozen,_=await self.service._freeze_model_context(self.aid,cmd,config())
        await self.ledger.accept_teaching_command(self.aid,cmd,frozen)
        self.assertTrue((await self.ledger.claim_teaching_launch(self.aid,cmd.business_key,cmd.request_sha256(self.aid)))['launch_allowed'])
    async def test_each_public_read_uses_one_select_snapshot(self):
        import psycopg
        original=psycopg.AsyncConnection.execute;queries=[]
        async def execute(conn,query,*args,**kwargs):
            text=str(query).lstrip()
            # set_config 是原事务超时设置，不读取任何教学事实。
            if text.upper().startswith(('SELECT','WITH')) and "set_config(" not in text:queries.append(text)
            return await original(conn,query,*args,**kwargs)
        for reader in (lambda:self.ledger.read_teaching_workspace(self.aid),
            lambda:self.ledger.read_teaching_record(self.aid,self.eid),
            lambda:self.ledger.read_teaching_command(self.aid,str(self.fixture.rows('SELECT business_key FROM teaching_commands WHERE activity_id=%s ORDER BY created_at LIMIT 1',(self.aid,))[0]['business_key'])),
            lambda:self.ledger.read_teaching_history(self.aid)):
            queries.clear()
            with patch.object(psycopg.AsyncConnection,'execute',execute):await reader()
            self.assertEqual(len(queries),1);self.assertTrue(queries[0].startswith('WITH'))
    async def test_zero_fee_answer_preserved_at_exhausted_budget(self):
        self.fixture.rows('UPDATE activities SET requests_reserved=max_requests WHERE id=%s',(self.aid,))
        before=self.fixture.rows('SELECT requests_reserved,cost_reserved_microunits,tools_reserved FROM activities WHERE id=%s',(self.aid,))[0]
        head=self.fixture.head(self.aid)
        answer=command(head,'answer',{'exercise_record_id':self.eid,'kind':'revision','text':'1m/s，分钟乘60，数量级合理','supersedes_answer_record_id':self.answer})
        receipt=await self.service.submit_command(self.aid,answer,config())
        self.assertEqual(receipt.status,'committed')
        head=self.fixture.head(self.aid)
        evaluate=command(head,'evaluate',{'confirmed':True,'exercise_record_id':self.eid,'answer_record_id':receipt.record_ids[0].record_id,'correction_record_id':None,'retry_of':None})
        with self.assertRaises(TeachingRefusal) as ctx:await self.service.submit_command(self.aid,evaluate,config())
        self.assertEqual(ctx.exception.code,'budget_exhausted')
        after=self.fixture.rows('SELECT requests_reserved,cost_reserved_microunits,tools_reserved FROM activities WHERE id=%s',(self.aid,))[0]
        self.assertEqual(before,after);self.assertIsNone(head['pending_business_key'])
    async def test_reference_requires_write_exposure_and_get_does_not_write(self):
        before=len(self.fixture.records(self.aid))
        raw=await self.ledger.read_teaching_workspace(self.aid);view=_workspace_payload(self.aid,raw)
        self.assertNotIn('reference_points',view['exercise']);self.assertEqual(before,len(self.fixture.records(self.aid)))
        receipt=await self.ledger.apply_teaching_local(self.aid,command(self.fixture.head(self.aid),'expose',{'exercise_record_id':self.eid,'part':'reference'}))
        self.assertTrue(receipt.exposed_part['reference_points'])
        view=_workspace_payload(self.aid,await self.ledger.read_teaching_workspace(self.aid))
        self.assertEqual(view['exercise']['reference_points'][0]['numeric']['value_decimal'],'1')
    async def test_other_activity_cannot_read_record(self):
        other=await self.fixture.activity([self.source])
        self.assertIsNone(await self.ledger.read_teaching_record(other,self.eid))

    async def _claimed_intent(self):
        from app.capabilities.contracts import AdmissionIntent,CallContext,Provider
        from app.learning.teaching_contracts import TeachingCallBinding
        head=self.fixture.head(self.aid)
        cmd=command(head,'evaluate',{'confirmed':True,'exercise_record_id':self.eid,'answer_record_id':self.answer,'correction_record_id':None,'retry_of':None})
        frozen,_=await self.service._freeze_model_context(self.aid,cmd,config())
        await self.ledger.accept_teaching_command(self.aid,cmd,frozen)
        await self.ledger.claim_teaching_launch(self.aid,cmd.business_key,cmd.request_sha256(self.aid))
        lease=await self.fixture.lease(self.aid)
        binding=TeachingCallBinding(command_key=cmd.business_key,request_sha256=cmd.request_sha256(self.aid),context_sha256=frozen.context_sha256,
            expected_revision=head['revision'],goal_version=head['goal_version'])
        context=CallContext(activity_id=self.aid,operation_id=cmd.operation_id(self.aid),executor_id=lease.executor_id,
            execution_generation=lease.execution_generation,scope_revision=1)
        intent=AdmissionIntent(context,Provider.DEEPSEEK_CHAT_COMPLETIONS,'synthetic-model-100',2048,2048,(),teaching_binding=binding)
        return cmd,frozen,lease,intent

    async def _settle(self,lease):
        await self.ledger.begin_window_close(self.aid,lease.executor_id,lease.execution_generation)
        await self.ledger.settle_execution_window(self.aid,lease.executor_id,lease.execution_generation,window_seconds=30,elapsed_seconds=0)

    async def test_database_admit_requires_trusted_binding_before_reservation(self):
        from dataclasses import replace
        from app.capabilities.contracts import AdmissionDenied
        cmd,_,lease,intent=await self._claimed_intent()
        before=self.fixture.rows('SELECT requests_reserved,cost_reserved_microunits FROM activities WHERE id=%s',(self.aid,))[0]
        try:
            with self.assertRaises(AdmissionDenied):await self.ledger.admit(replace(intent,teaching_binding=None))
            self.assertEqual(before,self.fixture.rows('SELECT requests_reserved,cost_reserved_microunits FROM activities WHERE id=%s',(self.aid,))[0])
            self.assertEqual(self.fixture.rows('SELECT count(*) AS n FROM activity_operations WHERE activity_id=%s AND operation_id=%s',(self.aid,cmd.operation_id(self.aid)))[0]['n'],0)
        finally:await self._settle(lease)

    async def test_answer_change_after_admit_blocks_mark_before_dispatch(self):
        from app.capabilities.contracts import AdmissionDenied
        cmd,_,lease,intent=await self._claimed_intent()
        try:
            permit=await self.ledger.admit(intent)
            revision=command(self.fixture.head(self.aid),'answer',{'exercise_record_id':self.eid,'kind':'revision',
                'text':'新答案：1m/s','supersedes_answer_record_id':self.answer})
            await self.ledger.apply_teaching_local(self.aid,revision)
            with self.assertRaises(AdmissionDenied):await self.ledger.mark_dispatch_started(permit)
            row=self.fixture.rows('SELECT dispatch_started_at,state FROM activity_operations WHERE activity_id=%s AND operation_id=%s',(self.aid,cmd.operation_id(self.aid)))[0]
            self.assertIsNone(row['dispatch_started_at']);self.assertEqual(row['state'],'reserved')
        finally:await self._settle(lease)

    async def test_invalid_teaching_result_rolls_back_original_007_and_terminal(self):
        from app.capabilities.contracts import LedgerOutcome,LedgerDisposition,build_business_payload
        cmd,_,lease,intent=await self._claimed_intent()
        try:
            permit=await self.ledger.admit(intent);await self.ledger.mark_dispatch_started(permit)
            fmt,payload,digest=build_business_payload(json_object={'profile':'teaching.v1','activity_id':str(uuid4()),'result':{}})
            outcome=LedgerOutcome(LedgerDisposition.RECEIVED,returned_model='synthetic-model-100',finish_reason='stop',prompt_tokens=1,completion_tokens=1,
                response_bytes=100,payload_format=fmt,payload=payload,payload_sha256=digest)
            with self.assertRaises(TeachingRefusal):await self.ledger.record_outcome(permit,outcome)
            row=self.fixture.rows('SELECT state FROM activity_operations WHERE activity_id=%s AND operation_id=%s',(self.aid,cmd.operation_id(self.aid)))[0]
            self.assertNotEqual(row['state'],'received')
            self.assertEqual(self.fixture.rows('SELECT count(*) AS n FROM activity_operation_results WHERE activity_id=%s AND operation_id=%s',(self.aid,cmd.operation_id(self.aid)))[0]['n'],0)
            self.assertEqual(self.fixture.rows('SELECT count(*) AS n FROM teaching_records WHERE activity_id=%s AND business_key=%s',(self.aid,cmd.business_key))[0]['n'],0)
        finally:await self._settle(lease)

    async def test_real_concurrent_answer_slot_has_one_effect_and_no_fork(self):
        import asyncio
        import psycopg
        head=self.fixture.head(self.aid);before=head['last_seq']
        body={'exercise_record_id':self.eid,'kind':'revision','text':'并发同一修正版 1m/s','supersedes_answer_record_id':self.answer}
        commands=[command(head,'answer',body) for _ in range(2)]
        blocker=await psycopg.AsyncConnection.connect(self.fixture.dsn)
        tasks=[]
        try:
            await blocker.execute('SELECT id FROM activities WHERE id=%s FOR UPDATE',(self.aid,))
            tasks=[asyncio.create_task(self.ledger.apply_teaching_local(self.aid,c)) for c in commands]
            await asyncio.sleep(.05)
            await blocker.commit()
            receipts=await asyncio.gather(*tasks)
        finally:
            await blocker.close()
            if tasks:await asyncio.gather(*tasks,return_exceptions=True)
        self.assertTrue(all(r.status=='committed' for r in receipts))
        self.assertEqual(receipts[0].record_ids,receipts[1].record_ids)
        self.assertEqual(sum(r.duplicate_of is not None for r in receipts),1)
        self.assertEqual(self.fixture.head(self.aid)['last_seq'],before+1)
        head=self.fixture.head(self.aid);body['supersedes_answer_record_id']=str(head['answer_record_id'])
        pair=[command(head,'answer',body|{'text':text}) for text in ('竞争文字甲','竞争文字乙')]
        results=await asyncio.gather(*[self.ledger.apply_teaching_local(self.aid,c) for c in pair],return_exceptions=True)
        self.assertEqual(sum(isinstance(r,TeachingRefusal) for r in results),1)
        self.assertEqual(self.fixture.head(self.aid)['last_seq'],before+2)
        self.assertEqual(self.fixture.rows('SELECT count(*) AS n FROM teaching_records WHERE activity_id=%s AND supersedes_record_id=%s',(self.aid,body['supersedes_answer_record_id']))[0]['n'],1)

    async def test_teaching_already_present_replay_after_settle_is_read_only(self):
        from app.capabilities.contracts import LedgerOutcome,LedgerDisposition,build_business_payload,Message,RecordOutcome
        from app.learning.teaching_contracts import stored_teaching_result
        from tests.fixtures.task100.synthetic_content import output_for
        cmd,frozen,lease,intent=await self._claimed_intent()
        try:
            identity,_=await self.service._load_teaching_entities(self.aid,cmd)
            profile=self.service._build_profile(self.aid,cmd,frozen,identity)
            value=stored_teaching_result(profile,output_for(json.loads(frozen.messages[-1]['content'])),[Message.model_validate(m) for m in frozen.messages])
            fmt,payload,digest=build_business_payload(json_object=value)
            outcome=LedgerOutcome(LedgerDisposition.RECEIVED,returned_model='synthetic-model-100',finish_reason='stop',
                prompt_tokens=128,completion_tokens=256,response_bytes=4096,payload_format=fmt,payload=payload,payload_sha256=digest)
            permit=await self.ledger.admit(intent);await self.ledger.mark_dispatch_started(permit)
            self.assertEqual(await self.ledger.record_outcome(permit,outcome),RecordOutcome.RECORDED)
        finally:await self._settle(lease)
        def snapshot():
            return {table:self.fixture.rows('SELECT * FROM '+table+' WHERE activity_id=%s',(self.aid,))
                for table in ('activity_operations','activity_operation_results','teaching_records','teaching_commands','teaching_heads')}
        before=snapshot();budget=self.fixture.rows('SELECT requests_reserved,cost_reserved_microunits,tools_reserved FROM activities WHERE id=%s',(self.aid,))
        self.assertEqual(await self.ledger.record_outcome(permit,outcome),RecordOutcome.ALREADY_PRESENT)
        self.assertEqual(snapshot(),before)
        self.assertEqual(self.fixture.rows('SELECT requests_reserved,cost_reserved_microunits,tools_reserved FROM activities WHERE id=%s',(self.aid,)),budget)

    async def test_final009_preserves_legacy_model_tool_unknown_and_missing_body(self):
        """沿用已有m05回滚后的001—008；不建第七schema或重新跑六个反例。"""
        import hashlib
        from pathlib import Path
        from app.capabilities.contracts import build_business_payload
        from tests.fixtures.task100.pg_migration_scenarios import connect,SCHEMA_NAMES,teaching_objects,seed,fingerprints,M009
        from tests.fixtures.task100.control import atomic_json
        import os
        schema=SCHEMA_NAMES['midway']
        with connect(schema) as conn:
            self.assertEqual(teaching_objects(conn),[])
            seed(conn);aid=str(conn.execute('SELECT id FROM activities ORDER BY created_at LIMIT 1').fetchone()['id'])
            bodies=[]
            for suffix,state in (('model','received'),('unknown','unknown')):
                operation='learn-first-v1.task100-legacy-'+suffix;admission=str(uuid4())
                conn.execute("INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,execution_generation,scope_revision,provider,configured_model,request_bytes,max_output_tokens,reserved_cost_microunits,state,disposition,recorded_at) VALUES (%s,%s,%s,'legacy',1,1,'deepseek_chat_completions','synthetic-model-100',100,256,1000,%s,%s,now())",(aid,operation,admission,state,state))
                if state=='received':bodies.append((operation,admission,build_business_payload(json_object={'profile':'learning.v1','legacy_synthetic':True,'answer':'合成旧学习正文'})))
            operation='g5-tool.task100-legacy';admission=str(uuid4())
            conn.execute("INSERT INTO activity_operations(activity_id,operation_id,admission_id,executor_id,execution_generation,scope_revision,kind,tool_names,arguments_sha256,tool_call_id,reserved_cost_microunits,state,disposition,recorded_at) VALUES (%s,%s,%s,'legacy',1,1,'tool',ARRAY['finite_calculate'],%s,'task100-legacy-tool',0,'received','received',now())",(aid,operation,admission,'b'*64))
            bodies.append((operation,admission,build_business_payload(json_object={'value_decimal':'1','legacy_synthetic':True})))
            for operation,admission,(fmt,payload,digest) in bodies:
                conn.execute('INSERT INTO activity_operation_results(activity_id,operation_id,admission_id,execution_generation,scope_revision,payload_format,payload,payload_sha256) VALUES (%s,%s,%s,1,1,%s,%s,%s)',(aid,operation,admission,fmt,payload,digest))
            before=fingerprints(conn);conn.execute(M009);after=fingerprints(conn)
            self.assertEqual(before,after);self.assertEqual(len(teaching_objects(conn)),3)
            self.assertEqual(conn.execute('SELECT count(*) AS n FROM teaching_heads').fetchone()['n'],0)
            self.assertIsNone(conn.execute("SELECT payload FROM activity_operation_results WHERE activity_id=%s AND operation_id='learn-first-v1.legacy'",(aid,)).fetchone())
            atomic_json(Path(os.environ['RETROLUME_TASK100_BATCH_DIR'])/'migration-legacy-compatibility.json',{
                'status':'pass','schema':schema,'database':'retrolume_task100_g8_fault','009_executed_utf8_lf_sha256':hashlib.sha256(M009.encode()).hexdigest(),
                'legacy_before':before,'legacy_after':after,'representatives':['G7_model_body','G5_tool_body','unknown_no_body','received_no_body'],
                'no_backfill':True,'no_data_deleted':True,'not_a_legacy_provider_or_full_old_flow_test':True})

    async def test_correction_and_opposite_feedback_preserve_contested_observation(self):
        from app.capabilities.contracts import LedgerOutcome,LedgerDisposition,build_business_payload,Message
        from app.learning.teaching_contracts import stored_teaching_result
        from tests.fixtures.task100.synthetic_content import output_for
        async def commit(cmd,frozen,intent,opposite=False):
            identity,_=await self.service._load_teaching_entities(self.aid,cmd)
            profile=self.service._build_profile(self.aid,cmd,frozen,identity)
            result=output_for(json.loads(frozen.messages[-1]['content']))
            if opposite:
                result['errors']=[];result['evidence_gaps']=[];result['cause_hypotheses']=[]
                for d in result['dimension_observations']:d['observation']='met'
            value=stored_teaching_result(profile,result,[Message.model_validate(m) for m in frozen.messages])
            fmt,payload,digest=build_business_payload(json_object=value)
            permit=await self.ledger.admit(intent);await self.ledger.mark_dispatch_started(permit)
            await self.ledger.record_outcome(permit,LedgerOutcome(LedgerDisposition.RECEIVED,returned_model='synthetic-model-100',finish_reason='stop',
                prompt_tokens=128,completion_tokens=256,response_bytes=4096,payload_format=fmt,payload=payload,payload_sha256=digest))
        cmd,frozen,lease,intent=await self._claimed_intent()
        try:await commit(cmd,frozen,intent)
        finally:await self._settle(lease)
        head=self.fixture.head(self.aid);old_feedback=str(head['feedback_record_id']);old_progress=str(head['reason_record_id'])
        original=self.fixture.rows('SELECT record_id,body_sha256,applied_revision,state_after FROM teaching_records WHERE activity_id=%s ORDER BY seq',(self.aid,))
        correction=command(head,'correct',{'target_record_id':old_progress,'text':'用户认为单位解释有争议，尚未验证','disputed_dimensions':['unit']})
        fixed=await self.ledger.apply_teaching_local(self.aid,correction);head=self.fixture.head(self.aid)
        self.assertIn(self.answer,json.loads(head['projection'])['nodes']['n1']['contested'])
        next_cmd=command(head,'evaluate',{'confirmed':True,'exercise_record_id':self.eid,'answer_record_id':self.answer,
            'correction_record_id':fixed.record_ids[0].record_id,'retry_of':None})
        frozen,identity=await self.service._freeze_model_context(self.aid,next_cmd,config())
        self.assertTrue(json.loads(frozen.messages[-1]['content'])['task']['corrections'])
        await self.ledger.accept_teaching_command(self.aid,next_cmd,frozen);await self.ledger.claim_teaching_launch(self.aid,next_cmd.business_key,next_cmd.request_sha256(self.aid))
        from dataclasses import replace
        lease=await self.fixture.lease(self.aid)
        from app.learning.teaching_contracts import TeachingCallBinding
        binding=TeachingCallBinding(command_key=next_cmd.business_key,request_sha256=next_cmd.request_sha256(self.aid),context_sha256=frozen.context_sha256,
            expected_revision=head['revision'],goal_version=1)
        context=intent.context.model_copy(update={'operation_id':next_cmd.operation_id(self.aid),'execution_generation':lease.execution_generation})
        intent=replace(intent,context=context,teaching_binding=binding)
        try:await commit(next_cmd,frozen,intent,True)
        finally:await self._settle(lease)
        head=self.fixture.head(self.aid);projection=json.loads(head['projection'])['nodes']['n1']
        self.assertIn(self.answer,projection['contested']);self.assertEqual(projection['independent_answers'],[])
        self.assertNotEqual(projection['status'],'evidence_sufficient')
        after=self.fixture.rows('SELECT record_id,body_sha256,applied_revision,state_after FROM teaching_records WHERE activity_id=%s ORDER BY seq',(self.aid,))
        self.assertEqual(original,after[:len(original)])
        self.assertEqual(self.fixture.rows("SELECT count(*) AS n FROM teaching_records WHERE activity_id=%s AND kind='feedback'",(self.aid,))[0]['n'],2)
