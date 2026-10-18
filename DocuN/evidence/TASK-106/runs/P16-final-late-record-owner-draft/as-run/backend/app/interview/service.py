"""Explicit commands only. Native SUP owns stops and budget reconciliation."""
from __future__ import annotations
import asyncio

from app.capabilities.contracts import ModelCallRequest,Message
from app.worker.one_call import OneCallInput,run_one_call
from app.worker.session import SessionConfig
from .contracts import (InterviewContext,InterviewLimits,GoalBody,SourceBinding,SourceRole,RecordRef,
    InterviewRefusal,profile_for,operation_id,canonical,load_json,sha)
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
        available=bool(layer and layer.available and view['qualification']=='current' and view['domain']=='interview')
        view['capabilities'].update(model=available,model_reason=None if available else view['suppression_reason'] or (layer.reason if layer else 'interview_not_configured'))
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
        catalog=assemble_catalog(g.target+' '+(g.focus or '')+' '+' '.join(g.clarifications),units,command.request_hash(aid))
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
        frozen=InterviewContext(activity_id=aid,business_key=command.business_key,request_sha256=command.request_hash(aid),action=command.action,
            expected_head_revision=command.expected_head_revision,expected_goal_version=command.expected_goal_version,expected_scope_revision=command.expected_scope_revision,
            goal_record_id=h['goal_record_id'],goal_body=g,sources=[SourceBinding.model_validate({k:s[k] for k in ('source_id','version_id','source_revision','original_sha256')}) for s in view['sources']],
            material_roles=g.material_roles,round_index=h['round_index'],probe_depth=h['probe_depth'],parent_record_refs=refs,catalog=catalog,
            identity=identity,limits=limits)
        return frozen

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
        request=ModelCallRequest(interview_profile=profile_for(frozen),messages=tuple(Message.model_validate(m) for m in messages(frozen)),
            max_output_tokens=frozen.limits.max_output_tokens,allowed_tools=frozenset())
        service=config.model_service;session=self.session_config or SessionConfig()
        if service.timeout_seconds>session.request_timeout_seconds:raise InterviewRefusal('interview_config_invalid','模型超时超过监督窗口',503)
        try:OneCallInput(operation_id(command.business_key),request,service).to_wire()
        except (ValueError,TypeError):raise InterviewRefusal('interview_context_too_large','完整受控请求超过通道上限',422) from None
        receipt=await self.ledger.accept_interview_command(aid,command,frozen) if stored is None else await self.ledger.read_interview_command(aid,command.business_key)
        if receipt['status']!='accepted' or receipt['duplicate_of']:return receipt
        claim=await self.ledger.claim_interview_launch(aid,command.business_key,command.request_hash(aid))
        if not claim['launch_allowed']:return await self.ledger.read_interview_command(aid,command.business_key)
        task=asyncio.create_task(asyncio.to_thread(run_one_call,self.ledger,session,aid,'local-ui',claim['operation_id'],request,service,run_tag=run_tag))
        cancelled=False;supervision=None
        while True:
            try:
                supervision=await asyncio.shield(task);break
            except asyncio.CancelledError:
                cancelled=True
                if task.done():supervision=task.result();break
            except Exception:break
        if cancelled:raise asyncio.CancelledError
        state=getattr(supervision,'state','') or ''
        receipt_present=bool(getattr(supervision,'model_receipt',None)) or bool(getattr(supervision,'tool_receipt',None))
        facts=dict(state=state,definitely_not_admitted=not receipt_present and state in ('not_started','budget_exhausted','startup_deadline','partial_window_too_small'))
        return await self.ledger.finish_interview_supervision(aid,command.business_key,facts)

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
