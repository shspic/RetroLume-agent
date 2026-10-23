"""Explicit commands only. Native SUP owns stops and budget reconciliation."""
from __future__ import annotations
from app.data_exit.maintenance import owned_service
import asyncio
from datetime import datetime,timezone
from anyio import CancelScope

from app.capabilities.contracts import ModelCallRequest,Message
from app.worker.one_call import OneCallInput,run_one_call
from app.worker.session import SessionConfig
from .contracts import (InterviewContext,InterviewLimits,GoalBody,SourceBinding,SourceRole,RecordRef,
    InterviewRefusal,profile_for,operation_id,canonical,load_json,sha,InterviewHybridContext,InterviewCatalogEntry)
from .prompt import messages
from .policy import transition
from .evidence import load_units,assemble_catalog,verify_citation


class InterviewService:
    def __init__(self,ledger,materials,originals, *, session_config=None):
        self.ledger,self.materials,self.originals=ledger,materials,originals
        self.session_config=session_config

    async def read_workspace(self,aid,config):
        view=await self.ledger.read_interview_workspace(aid)
        layer=getattr(config,'interview_model_layer',None)
        budget=view['budget'];head=view['head']
        live=budget['status'] in ('pending','running') and datetime.fromisoformat(budget['deadline_at'])>datetime.now(timezone.utc)
        remaining=budget['requests_reserved']<budget['max_requests'] and budget['cost_reserved_microunits']+budget['reserve_cost_microunits']<=budget['max_cost_microunits']
        available=bool(layer and layer.available and live and remaining and not view['pending'] and head and head['phase']!='ended' and view['qualification']=='current' and view['domain']=='interview')
        reason=view['suppression_reason'] or ('cancelled' if budget['status']=='cancelled' else 'activity_expired' if not live else 'interview_budget_exhausted' if not remaining else 'interview_pending' if view['pending'] else 'interview_ended' if head and head['phase']=='ended' else (layer.reason if layer else 'interview_not_configured'))
        view['capabilities'].update(model=available,model_reason=None if available else reason)
        view['capabilities']['max_followups_per_round']=getattr(config,'interview_followups',None)
        view['capabilities']['max_output_tokens']=getattr(config,'interview_output_tokens',None)
        return view

    async def _frozen(self,aid,command,config):
        view=await self.ledger.read_interview_workspace(aid);h=view['head']
        if h is None:raise InterviewRefusal('interview_phase_conflict')
        transition(command.action,h,command.body)
        goal=await self.ledger.read_interview_record(aid,h['goal_record_id'],view['view_token'])
        if goal['body'] is None:raise InterviewRefusal('interview_parent_invalid')
        g=GoalBody.model_validate(goal['body']['value']['goal'])
        snapshot=await self.ledger.read_learning_snapshot(aid)
        units=await asyncio.to_thread(load_units,snapshot,self.materials,self.originals)
        hybrid=command.schema_id=='interview.command.v2'
        if hybrid:
            from app.retrieval.service import RetrievalService
            from app.retrieval.contracts import RetrievalRefusal
            try:entries=await RetrievalService(self.ledger,self.materials,self.originals).catalog(aid,command.retrieval_ref,command.request_hash(aid),top_k=4,max_chars=4000,max_bytes=8000)
            except RetrievalRefusal as exc:raise InterviewRefusal(exc.code,'本轮检索已失效') from None
            catalog=[InterviewCatalogEntry.model_validate({**e.model_dump(),'citation_id':'ic_'+sha(command.request_hash(aid)+e.evidence_id)[:24]}) for e in entries]
        else:catalog=assemble_catalog(g.target+' '+(g.focus or '')+' '+' '.join(g.clarifications),units,command.request_hash(aid))
        refs=[]
        if command.action=='review':
            # Only this round's question/answer chain. No unbounded prior history.
            needed={h['root_question_id'],h['current_question_id'],h['current_answer_id']}
            round_rows=await self.ledger.read_interview_round_refs(aid,view['view_token'])
            needed.update(r['record_id'] for r in round_rows)
        else:needed={command.body.get('parent_feedback_id')} if command.body.get('parent_feedback_id') else set()
        if len(needed)>12:raise InterviewRefusal('interview_context_too_large',status=422)
        for rid in sorted(x for x in needed if x):
            detail=await self.ledger.read_interview_record(aid,rid,view['view_token'])
            if detail['body'] is None or not detail['record']['eligible']:raise InterviewRefusal('interview_parent_invalid')
            r=detail['record'];refs.append(RecordRef(record_id=rid,kind=r['kind'],version=r['answer_version'],body_sha256=r['body_sha256'],
                body=self.ledger._interview_ref_body(r,detail['body'],command.action),operation_id=r['operation_id'],payload_sha256=r['payload_sha256']))
        # Sorting by durable seq, not UUID, identifies latest answer/probe reliably.
        order={r['record_id']:r['seq'] for r in view['records']}
        if command.action=='review':order.update({r['record_id']:r['seq'] for r in round_rows})
        refs.sort(key=lambda r:order.get(r.record_id,0))
        limits=InterviewLimits(max_output_tokens=getattr(config,'interview_output_tokens',0) or 1,
            max_followups_per_round=getattr(config,'interview_followups',0) or 1)
        identity={'provider':config.provider,'model':config.model} if config.provider and config.model else await self.ledger.read_interview_identity(aid)
        extra={}
        if hybrid:
            selection=await self.ledger.read_memory_selection(aid,include_bodies=True)
            if not selection.get('eligible'):raise InterviewRefusal('interview_memory_dependency_invalid')
            memory_refs=[{k:x[k] for k in ('memory_id','version','revision','body_sha256')} for x in selection['entries']]
            extra=dict(retrieval_ref=command.retrieval_ref,memory_recipe={'policy':'interview.memory.recipe.v1','activity_id':aid,'refs':memory_refs} if memory_refs else None,
                memory_refs=memory_refs,memory_selection_sha256=selection['selection_sha256'],memory_dependency_sha256=selection.get('dependency_sha256'))
        frozen=(InterviewHybridContext if hybrid else InterviewContext)(activity_id=aid,business_key=command.business_key,request_sha256=command.request_hash(aid),action=command.action,
            expected_head_revision=command.expected_head_revision,expected_goal_version=command.expected_goal_version,expected_scope_revision=command.expected_scope_revision,
            goal_record_id=h['goal_record_id'],goal_body=g,sources=[SourceBinding.model_validate({k:s[k] for k in ('source_id','version_id','source_revision','original_sha256')}) for s in view['sources']],
            material_roles=g.material_roles,round_index=h['round_index'],probe_depth=h['probe_depth'],parent_record_refs=refs,catalog=catalog,
            identity=identity,limits=limits,**extra)
        return frozen

    @owned_service
    async def submit_command(self,aid,command,config, *, run_tag):
        if command.action not in ('ask','review'):
            return await self.ledger.apply_interview_local(aid,command)
        stored=await self.ledger.read_interview_frozen_command(aid,command.business_key,command.request_body(aid))
        if stored is False:return await self.ledger.read_interview_command(aid,command.business_key)
        if stored is None:
            replay=await self.ledger.lookup_interview_replay(aid,command)
            if replay is not None:return replay
        frozen=stored or await self._frozen(aid,command,config)
        if not frozen.catalog:
            if command.action=='ask':
                value=dict(type='question',purpose='clarification',reason='missing_material',
                    text=f'目前资料没有可定位的相关片段。针对“{frozen.goal_body.target}”，请说明具体范围或补充包含依据的资料。',reference_ids=[])
            else:
                value=dict(type='feedback',summary='已保存你的说明；目前缺少可定位的资料，不能确认内容或业绩。',recognitions=[],
                    gaps=[dict(answer_record_id=command.body['answer_record_id'],text='请补充具体概念、基线、测量口径、样本、环境及可核查记录；或修正目标和资料范围。',reference_ids=[])],conflicts=[],next_steps=['补充资料并明确确认范围后再继续。'])
            return await self.ledger.apply_interview_local(aid,command,application_value=value)
        layer=getattr(config,'interview_model_layer',None)
        if not layer or not layer.available or config.model_service is None:raise InterviewRefusal(layer.reason if layer else 'interview_not_configured','面试模型配置未就绪',503)
        background=None
        if isinstance(frozen,InterviewHybridContext):
            from app.memory.context import interview_background,check_capacity
            from app.memory.contracts import MemoryRefusal
            try:
                selection=await self.ledger.read_memory_selection(aid,include_bodies=True)
                background=interview_background(selection,frozen)
                if selection.get('selected'):check_capacity(messages(frozen,background),selection,config.memory_context,await self.ledger.read_learning_snapshot(aid),config.model_service)
            except MemoryRefusal as exc:raise InterviewRefusal(exc.code,exc.message) from None
        request=ModelCallRequest(interview_profile=profile_for(frozen),messages=tuple(Message.model_validate(m) for m in messages(frozen,background)),
            max_output_tokens=frozen.limits.max_output_tokens,allowed_tools=frozenset(),retrieval_ref=frozen.retrieval_ref if isinstance(frozen,InterviewHybridContext) else None)
        service=config.model_service;session=self.session_config or SessionConfig()
        if service.timeout_seconds>session.request_timeout_seconds:raise InterviewRefusal('interview_config_invalid','模型超时超过监督窗口',503)
        try:OneCallInput(operation_id(command.business_key,command.schema_id),request,service).to_wire()
        except (ValueError,TypeError):raise InterviewRefusal('interview_context_too_large','完整受控请求超过通道上限',422) from None
        receipt=await self.ledger.accept_interview_command(aid,command,frozen) if stored is None else await self.ledger.read_interview_command(aid,command.business_key)
        if receipt['status']!='accepted' or receipt['duplicate_of']:return receipt
        from app.capabilities.q_gateway import is_v2
        if is_v2(service):
            from app.capabilities.q_context import prepare
            from app.capabilities.gateway import ControlledModelGateway
            projection,service=await prepare(self.ledger,aid,command.business_key,operation_id(command.business_key,command.schema_id),
                request,service,ControlledModelGateway(service)._build_payload(request),domain='interview',action=command.action)
            if not projection['can_continue']:return {**receipt,'outbound_approval':projection,'model_called':False}
        from app.capabilities.q_context import claim_approved
        claim=await claim_approved(self.ledger,service,lambda:self.ledger.claim_interview_launch(aid,command.business_key,command.request_hash(aid)))
        if not claim['launch_allowed']:return await self.ledger.read_interview_command(aid,command.business_key)
        task=asyncio.create_task(asyncio.to_thread(run_one_call,self.ledger,session,aid,'local-ui',claim['operation_id'],request,service,run_tag=run_tag))
        cancelled=False;supervision=None
        # The existing ASGI middleware also uses AnyIO level cancellation.
        # Shield its scope while retaining explicit asyncio caller cancellation.
        with CancelScope(shield=True):
            while True:
                try:
                    supervision=await asyncio.shield(task);break
                except asyncio.CancelledError:
                    cancelled=True
                    if task.done():
                        if not task.cancelled():
                            try:supervision=task.result()
                            except Exception:pass
                        break
                except Exception:break
            state=getattr(supervision,'state','') or ''
            receipt_present=bool(getattr(supervision,'model_receipt',None)) or bool(getattr(supervision,'tool_receipt',None))
            facts=dict(state=state,definitely_not_admitted=not receipt_present and state in ('not_started','budget_exhausted','startup_deadline','partial_window_too_small'))
            # Repeated caller cancellation cannot skip/restart bounded cleanup.
            finishing=asyncio.create_task(asyncio.wait_for(
                self.ledger.finish_interview_supervision(aid,command.business_key,facts),timeout=15.0))
            while True:
                try:
                    receipt=await asyncio.shield(finishing);break
                except asyncio.CancelledError:
                    cancelled=True
                    if finishing.done():
                        try:receipt=finishing.result()
                        except BaseException:raise asyncio.CancelledError from None
                        break
                except Exception:
                    if cancelled:raise asyncio.CancelledError from None
                    raise
        if cancelled:raise asyncio.CancelledError
        return receipt

    async def read_citation(self,aid,rid,citation_id,view_token=None):
        first=await self.ledger.read_interview_record(aid,rid,view_token)
        if first['body'] is None:raise InterviewRefusal('source_invalid','该引用已失去当前资格')
        entry=next((c for c in first['body'].get('catalog',[]) if c['citation_id']==citation_id),None)
        if entry is None:raise InterviewRefusal('not_found','引用不存在',404)
        snapshot=await self.ledger.read_learning_snapshot(aid)
        selected=dict(snapshot,sources=[s for s in snapshot['sources'] if s['source_id']==entry['source_id']],source_count=1)
        units=await asyncio.to_thread(load_units,selected,self.materials,self.originals)
        if not verify_citation(entry,units):raise InterviewRefusal('source_invalid','原文位置或身份已变化')
        # Last DB qualification statement is the delivery cutoff; no network retraction promise.
        last=await self.ledger.read_interview_record(aid,rid,first['view_token'])
        if last['body'] is None or entry not in last['body'].get('catalog',[]):raise InterviewRefusal('source_invalid')
        return dict(schema='interview.citation.v1',activity_id=aid,record_id=rid,citation=entry,position_verified=True,
            semantic_verification='model_suggestion_only',view_token=last['view_token'])
