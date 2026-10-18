"""新profile在原准入/OneCall链内的绑定与结果处理。"""
from .business_contracts import HtmlProfile, operation_id, messages_for
from .compiler import compile_description, runtime_identity
from .description import load_json


async def validate_request(context, request, ledger):
    try:
        profile = HtmlProfile.model_validate(request.html_profile.model_dump())
        if (context.activity_id != profile.activity_id or context.operation_id != operation_id(profile.business_key)
                or request.allowed_tools or request.input_result is not None or request.response_mode.value != "json_object"
                or request.max_output_tokens != profile.max_output_tokens
                or [m.model_dump(exclude_none=True, exclude={"tool_calls"}) for m in request.messages] != messages_for(profile)
                or any(m.tool_calls or m.tool_call_id is not None for m in request.messages)
                or runtime_identity()["renderer_sha256"] != profile.renderer_sha256):
            return "invalid_html_profile"
        await ledger.verify_html_request(profile)
        return None
    except Exception:
        return "invalid_html_profile"


def stored_result(content, profile):
    context = load_json(profile.context_json)
    package = compile_description(load_json(content), {item["citation_id"] for item in context["catalog"]})
    return {"profile": profile.profile, "activity_id": profile.activity_id, "business_key": profile.business_key,
            "request_sha256": profile.request_sha256, "context_sha256": profile.context_sha256,
            "package": package}
