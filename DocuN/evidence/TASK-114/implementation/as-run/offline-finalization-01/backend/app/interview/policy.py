"""Domain transitions and low-trust suggestion normalization, no scoring."""
from .contracts import (InterviewContext, InterviewProfile, InterviewRefusal, QuestionOutput,
    ProbeOutput, FeedbackOutput, MAX_VALUE, canonical, load_json, sha, profile_for)
from .prompt import messages


def transition(action, head, body):
    phase = head['phase'] if head else None
    if action == 'start':
        if head is not None: raise InterviewRefusal('interview_domain_conflict')
        return
    if head is None: raise InterviewRefusal('interview_phase_conflict', '请先开始面试场次')
    if phase == 'ended': raise InterviewRefusal('interview_phase_conflict', '本场次已结束，只读历史')
    if head.get('pending_key') and action not in ('goal','correct_answer','bind_scope','abandon'):
        raise InterviewRefusal('interview_pending','先核对原提交或显式放弃，不会自动重发')
    if action == 'ask':
        wanted='ready' if body['mode']=='first' else 'feedback_ready'
        if phase!=wanted or (body['mode']=='next' and str(head.get('current_feedback_id') or '')!=body['parent_feedback_id']):
            raise InterviewRefusal('interview_phase_conflict')
    if action=='answer' and (phase!='question_ready' or str(head.get('current_question_id') or '')!=body['question_record_id']):
        raise InterviewRefusal('interview_parent_invalid')
    if action=='review' and (phase!='answer_ready' or str(head.get('current_question_id') or '')!=body['question_record_id'] or str(head.get('current_answer_id') or '')!=body['answer_record_id']):
        raise InterviewRefusal('interview_parent_invalid')
    if action=='abandon' and str(head.get('pending_key') or '')!=body['pending_key']:
        raise InterviewRefusal('interview_parent_invalid')


def normalize_output(raw, frozen: InterviewContext):
    data = load_json(raw)
    if frozen.action=='ask':
        output=QuestionOutput.model_validate(data)
    elif isinstance(data,dict) and data.get('type')=='probe':
        if frozen.probe_depth>=frozen.limits.max_followups_per_round: raise ValueError('invalid_interview_output')
        output=ProbeOutput.model_validate(data)
    else:
        output=FeedbackOutput.model_validate(data)
    value=output.model_dump()
    catalog={c.citation_id:c for c in frozen.catalog}
    answers={r.record_id:r.body['value']['text'] for r in frozen.parent_record_refs if r.kind=='answer'}
    roles={r.source_id:r.role for r in frozen.material_roles}
    def references(ids):
        if len(set(ids))!=len(ids) or any(i not in catalog for i in ids): raise ValueError('invalid_interview_output')
    references(value.get('reference_ids',[]))
    for item in value.get('recognitions',[]):
        references(item['reference_ids']); text=answers.get(item['answer_record_id'])
        if text is None or not 0<=item['start_offset']<item['end_offset']<=len(text) or text[item['start_offset']:item['end_offset']]!=item['answer_excerpt']:
            raise ValueError('invalid_interview_output')
        supported=(item['semantic_support']=='supports' and bool(item['reference_ids']) and all(roles[catalog[i].source_id]=='reference' for i in item['reference_ids']))
        item['position_verified']=bool(item['reference_ids'])
        item['verification_kind']='source_interpretation' if supported else 'user_statement'
        if not supported:
            item['explanation']=f"你已说明：{item['answer_excerpt']}；尚未独立核实"
    for item in value.get('gaps',[]):
        if item['answer_record_id'] not in answers: raise ValueError('invalid_interview_output')
        references(item['reference_ids'])
    for item in value.get('conflicts',[]): references(item['reference_ids'])
    if len(canonical(value).encode('utf-8'))>MAX_VALUE: raise ValueError('invalid_interview_output')
    return value


def stored_result(raw, profile: InterviewProfile, request_messages):
    frozen=InterviewContext.model_validate(load_json(request_messages[1].content))
    expected=profile_for(frozen)
    if expected!=profile or [m.model_dump(mode='json',exclude_none=True) for m in request_messages]!=messages(frozen):
        raise ValueError('interview_binding_invalid')
    return dict(profile='interview.v1',activity_id=frozen.activity_id,business_key=frozen.business_key,
        action=frozen.action,goal_version=frozen.expected_goal_version,head_revision=frozen.expected_head_revision,
        scope_revision=frozen.expected_scope_revision,prompt_version=frozen.prompt_version,
        request_sha256=frozen.request_sha256,context_sha256=sha(canonical(frozen.model_dump())),
        source_refs=[s.model_dump() for s in frozen.sources],catalog=[c.model_dump() for c in frozen.catalog],
        value=normalize_output(raw,frozen))


async def validate_request(context,request,ledger):
    from .contracts import operation_id
    profile=request.interview_profile
    if profile is None or context.activity_id!=profile.activity_id or context.operation_id!=operation_id(profile.business_key) or context.scope_revision!=profile.scope_revision:
        return 'interview_binding_invalid'
    if request.allowed_tools or request.input_result is not None or len(request.messages)!=2:
        return 'interview_binding_invalid'
    try:
        frozen=InterviewContext.model_validate(load_json(request.messages[1].content))
        if profile_for(frozen)!=profile or [m.model_dump(mode='json',exclude_none=True) for m in request.messages]!=messages(frozen): return 'interview_binding_invalid'
        if request.max_output_tokens!=frozen.limits.max_output_tokens: return 'interview_binding_invalid'
        validator=getattr(ledger,'validate_interview_request',None)
        if validator is None: return 'interview_profile_required'
        await validator(context,profile,frozen)
        return None
    except (ValueError,TypeError,KeyError,RecursionError): return 'interview_binding_invalid'
