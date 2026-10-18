"""只在本许可进程内提供最低原始传输及透明原生见证。"""
import json
import os
import sys
import threading
from uuid import uuid4
from .common import event, require_runtime, reserve

SERIAL = "串行执行的最终数值为110。"
TRACE = "两个操作均先读取100，再分别写120和90，可覆盖一次写回；按给定顺序最后写90就留下90。"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def original_sentences(catalog):
    found = []
    for sentence in (SERIAL, TRACE):
        candidates = [x for x in catalog if sentence in x["text"]]
        if not candidates:
            raise ValueError("107冻结支持原句不在真实catalog；不得假造引用")
        found.append(candidates[0]["citation_id"])
    return list(dict.fromkeys(found))


async def send(self, *, endpoint, api_key, payload, timeout_seconds, max_response_bytes):
    require_runtime()
    from app.capabilities.transport import TransportResponse
    reserve("transport_send", dict(synthetic=True, model=payload["model"]))
    message = next(m["content"] for m in reversed(payload["messages"]) if m["role"] == "user")
    frozen = json.loads(message)
    if frozen.get("schema") != "interview.context.v1":
        raise ValueError("107只允许声明的面试原始传输，无旧profile/外网fallback")
    citations = original_sentences(frozen["catalog"])
    if frozen["action"] == "ask":
        value = dict(type="question", purpose="interview", reason="topic",
                     text="请仅针对给定合成余额算法，解释串行110与两个先读100后写120、90的覆盖风险。",
                     reference_ids=citations)
    else:
        answers = [x for x in frozen["parent_record_refs"] if x["kind"] == "answer"]
        answer = answers[-1]; text = answer["body"]["value"]["text"]
        if not 1 <= len(text) <= 512:
            raise ValueError("107声明回答片段超过支持fixture上限")
        recognition = dict(answer_record_id=answer["record_id"], start_offset=0, end_offset=len(text),
                           answer_excerpt=text, reference_ids=citations, semantic_support="supports",
                           explanation="仅对照这两条明确合成原句；不代表真实数据库或现实能力证明。")
        value = dict(type="feedback", summary="本轮原文对照建议已保留；现实能力与真实数据库表现仍未知。",
                     recognitions=[recognition], gaps=[], conflicts=[], next_steps=["是否继续由用户显式决定。"])
    event("lowest-raw-response", dict(context=frozen, value=value, synthetic=True,
                                     usage=dict(prompt_tokens=128, completion_tokens=64, total_tokens=192)))
    response = dict(id="task107-synthetic-" + uuid4().hex, model=payload["model"],
                    choices=[dict(index=0, message=dict(role="assistant", content=canonical(value)), finish_reason="stop")],
                    usage=dict(prompt_tokens=128, completion_tokens=64, total_tokens=192))
    data = canonical(response).encode("utf-8")
    if len(data) > max_response_bytes:
        raise ValueError("107原始response超过声明通道")
    return TransportResponse(200, data, len(data))


def profile(frame, event_name, value):
    filename = frame.f_code.co_filename.replace("\\", "/")
    if event_name == "return" and frame.f_code.co_name == "run_one_call" and "/app/worker/one_call.py" in filename and value is not None:
        event("native-session", {k: getattr(value, k, None) for k in (
            "state", "activity_id", "generation", "job_name", "pid", "active_processes_at_end",
            "settled_seconds", "reserved_seconds", "cleanup_incomplete")})
    elif event_name == "return" and frame.f_code.co_qualname == "_SuspendedSupervisor.create" and "/app/worker/launcher.py" in filename and value is not None:
        event("native-supervisor", dict(pid=value.pid, created_100ns=value.creation_time_100ns()))


def install():
    require_runtime()
    from app.capabilities.transport import HttpxModelTransport
    HttpxModelTransport.send = send
    sys.setprofile(profile); threading.setprofile(profile)
