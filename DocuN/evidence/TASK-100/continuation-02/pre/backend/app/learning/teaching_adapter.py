"""worker 取得租约后的教学请求复核；不替代账本准入权威。"""
from __future__ import annotations

import json

from .teaching_contracts import TEACHING_PREFIX_MODEL, TeachingProfile
from .teaching_prompt import messages_for_teaching


async def validate_teaching_request(context, request, ledger) -> str | None:
    """复核 teaching_profile：身份、消息 hash、目录、来源与当前 head。

    返回错误码或 None；与 learning adapter 同样只在受控链内调用。
    """
    try:
        profile = TeachingProfile.model_validate(request.teaching_profile.model_dump())
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
        expected = messages_for_teaching(profile.action, json.loads(_last_user_content(request)))
        if [m.model_dump(exclude_none=True, exclude={"tool_calls"}) for m in request.messages] != expected:
            return "invalid_teaching_profile"
        # 目录来源身份须与活动快照一致。
        snapshot = await ledger.read_learning_snapshot(context.activity_id)
        authoritative = {s["source_id"]: s for s in snapshot["sources"]}
        if any(e.original_sha256 != authoritative[e.source_id]["sha256"]
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
