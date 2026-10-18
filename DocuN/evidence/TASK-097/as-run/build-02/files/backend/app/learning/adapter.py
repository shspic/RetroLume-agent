"""worker取得租约后的业务复核；不替代账本准入或原子提交权威。"""
import json
from uuid import UUID

from .contracts import FIRST_PREFIX, NEXT_PREFIX, LearningProfile, canonical, read_document
from .evidence import LearningRefusal, validate_snapshot
from .prompt import messages_for


async def validate_learning_request(context, request, ledger):
    try:
        profile = LearningProfile.model_validate(request.learning_profile.model_dump())
        if (context.activity_id != profile.activity_id or context.scope_revision != profile.scope_revision
                or request.allowed_tools or request.response_mode.value != "json_object"
                or request.max_output_tokens != profile.max_output_tokens
                or [m.model_dump(exclude_none=True, exclude={"tool_calls"}) for m in request.messages] != messages_for(profile)
                or any(m.tool_calls or m.tool_call_id is not None for m in request.messages)):
            return "invalid_learning_profile"
        if profile.action == "first":
            prefix = FIRST_PREFIX
            if request.input_result is not None or context.operation_id != prefix + profile.request_sha256:
                return "invalid_learning_profile"
        else:
            prefix = context.operation_id[:-64]
            if not prefix.startswith(NEXT_PREFIX) or not prefix.endswith("."):
                return "invalid_learning_profile"
            key = prefix[len(NEXT_PREFIX):-1]
            if str(UUID(key)) != key or context.operation_id != prefix + profile.request_sha256:
                return "invalid_learning_profile"
            ref = request.input_result
            if (ref is None or ref.activity_id != context.activity_id or ref.operation_id != profile.parent_operation_id
                    or ref.payload_sha256 != profile.parent_payload_sha256 or ref.scope_revision != profile.scope_revision):
                return "invalid_learning_profile"
            parent = await ledger.read_committed_result(context.activity_id, ref.operation_id)
            if parent.read_status.value != "committed_current" or parent.kind != "model" or parent.payload_sha256 != ref.payload_sha256:
                return "result_invalidated"
            parent_profile, parent_output = read_document(json.loads(parent.payload)["value"],
                activity_id=context.activity_id, operation_id=profile.parent_operation_id)
            if parent_profile.goal != profile.goal or canonical(parent_output.model_dump()) != profile.history:
                return "invalid_learning_profile"
        snapshot = await ledger.read_learning_snapshot(context.activity_id)
        sources = validate_snapshot(snapshot)
        if (snapshot["scope_revision"] != profile.scope_revision
                or [s.model_dump() for s in sources] != [s.model_dump() for s in profile.sources]):
            return "result_invalidated"
        slot = await ledger.find_learning_operation(context.activity_id, prefix)
        if slot is not None:
            return "learning_slot_occupied" if slot == context.operation_id else "learning_input_conflict"
    except LearningRefusal as exc:
        return exc.code
    except Exception:
        return "learning_validation_unavailable"
    return None
