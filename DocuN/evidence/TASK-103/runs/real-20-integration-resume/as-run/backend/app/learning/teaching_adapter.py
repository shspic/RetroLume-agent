"""worker 取得租约后的教学请求复核；不替代账本准入权威。"""
from __future__ import annotations

import json

from .teaching_contracts import TEACHING_PREFIX_MODEL, TeachingProfile
from .contracts import canonical,sha
from .teaching_prompt import messages_for_teaching


async def validate_teaching_request(context, request, ledger) -> str | None:
    """复核 teaching_profile：身份、消息 hash、目录、来源与当前 head。

    返回错误码或 None；与 learning adapter 同样只在受控链内调用。
    """
    try:
        from .teaching_contracts import TeachingMemoryProfile,parse_frozen_context,TeachingMemoryFrozenContext
        profile_type=TeachingMemoryProfile if request.teaching_profile.profile=='teaching.v2' else TeachingProfile
        profile = profile_type.model_validate(request.teaching_profile.model_dump())
        if request.learning_profile is not None or request.allowed_tools:
            return "invalid_teaching_profile"
        if (context.activity_id != profile.activity_id
                or context.scope_revision != profile.scope_revision
                or request.max_output_tokens != profile.max_output_tokens):
            return "invalid_teaching_profile"
        if not context.operation_id.startswith(TEACHING_PREFIX_MODEL):
            return "invalid_teaching_profile"
        # 操作键 = teach8m.<command_key>.<request_sha256>
        parts = context.operation_id.split(".")
        if len(parts) != 3 or parts[1] != profile.command_key or parts[2] != profile.request_sha256:
            return "invalid_teaching_profile"
        # 消息精确匹配（与实际 provider payload 投影一致）。
        from app.capabilities.contracts import Message
        if profile.profile=='teaching.v2':
            from app.memory.context import materialize_recipe
            from app.memory.contracts import MemoryRefusal
            view=await ledger.read_teaching_command(context.activity_id,profile.command_key)
            if view is None:return 'memory_dependency_invalid'
            frozen=parse_frozen_context(view['command']['context_body'])
            if not isinstance(frozen,TeachingMemoryFrozenContext) or frozen.context_sha256!=profile.context_sha256:
                return 'memory_profile_required'
            selection=await ledger.read_memory_selection(context.activity_id,include_bodies=True)
            if selection.get('selection_sha256')!=profile.memory_selection_sha256 or frozen.memory_refs!=profile.memory_refs:
                return 'memory_dependency_invalid'
            try: raw_expected=await materialize_recipe(ledger,frozen.recipe,frozen.catalog,selection)
            except MemoryRefusal as exc:return exc.code
            if sha(canonical([Message.model_validate(m).model_dump(mode='json',exclude_none=True) for m in raw_expected]))!=frozen.assembled_messages_sha256:
                return 'memory_dependency_invalid'
        else:
            raw_expected=messages_for_teaching(profile.action,json.loads(_last_user_content(request)))
        expected = [Message.model_validate(m).model_dump(mode="json",exclude_none=True) for m in raw_expected]
        actual = [m.model_dump(mode="json",exclude_none=True) for m in request.messages]
        if actual != expected or sha(canonical(actual)) != profile.messages_sha256:
            return "invalid_teaching_profile"
        # 目录来源身份须与活动快照一致。
        snapshot = await ledger.read_learning_snapshot(context.activity_id)
        if snapshot is None:
            return "source_invalid"
        authoritative = {s["source_id"]: s for s in snapshot["sources"]}
        if any(e.source_id not in authoritative or not authoritative[e.source_id]["valid"] or not authoritative[e.source_id]["ready"]
               or e.original_sha256 != authoritative[e.source_id]["sha256"]
               or e.title != authoritative[e.source_id]["title"]
               or e.format != authoritative[e.source_id]["format"]
               for e in profile.catalog):
            return "invalid_teaching_profile"
    except Exception:
        return "teaching_validation_unavailable"
    return None


def _last_user_content(request) -> str:
    for message in reversed(request.messages):
        if message.role == "user" and message.content:
            return message.content
    return "{}"
