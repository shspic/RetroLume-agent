"""仅传输层合成；原Windows OneCall/Job、PG、准入、提交与退款权仍真实。"""
from __future__ import annotations
import json
import os
import sys
import threading
from uuid import uuid4
from .control import PERMIT,reserve,event
from .samples import energy,binomial

INSTALLED=False


async def synthetic_send(self,*,endpoint,api_key,payload,timeout_seconds,max_response_bytes):
    from app.capabilities.transport import TransportResponse,DeliveryUnknown
    from app.preview.description import canonical
    reserve("model_synthetic_requests",{"model":payload["model"]})
    if payload["model"]!="task111-synthetic":raise RuntimeError("unexpected synthetic model")
    context=json.loads(payload["messages"][-1]["content"])
    if context.get("schema")!="html.context.v2":raise RuntimeError("unexpected synthetic profile")
    if "UNKNOWN" in context["focus"]:raise DeliveryUnknown("declared TASK111 transport uncertainty")
    citation=context["catalog"][0]["citation_id"]
    description=binomial(citation) if "二项" in context["focus"] else energy(citation)
    if "C04 机械能" in context["focus"]:description["inputs"][0]["kind"]="range"
    if any(marker in context["focus"] for marker in ("C01 边界","C03 边界")) and "二项" in context["focus"]:
        description["inputs"][0].update(min="0",max="20");description["inputs"][1].update(max="20")
        description["calculation_notes"][0]["domain"]="n整数0到20，k整数0到n，p在0到1"
    if "INVALID" in context["focus"]:description["html"]="<script>location.hash='x'</script>"
    result={"id":"task111-"+uuid4().hex,"model":payload["model"],"choices":[{"index":0,"message":{"role":"assistant","content":canonical(description)},"finish_reason":"stop"}],
      "usage":{"prompt_tokens":128,"completion_tokens":128,"total_tokens":256}}
    body=canonical(result).encode("utf-8");event("synthetic_response",{"business_key":context["business_key"],"request_sha256":context["request_sha256"],"description":description,
      "message_hash":__import__('hashlib').sha256(canonical(payload["messages"]).encode()).hexdigest(),"usage":result["usage"]})
    return TransportResponse(200,body,len(body),remote_request_id=result["id"])


def profile(frame,event_type,arg):
    if event_type=="call" and frame.f_code.co_name=="run_one_call" and "/app/worker/" in frame.f_code.co_filename.replace("\\","/"):
        reserve("Windows_OneCall_sessions",{"run_tag":frame.f_locals.get("run_tag"),"pid":os.getpid()})
    if event_type=="return" and frame.f_code.co_name=="run_one_call" and arg is not None:
        names=("state","activity_id","generation","job_name","pid","active_processes_at_end","settled_seconds","reserved_seconds","cleanup_incomplete","manager_pid","manager_created_100ns","worker_created_100ns")
        event("native_onecall",{key:getattr(arg,key,None) for key in names})


def install():
    global INSTALLED
    if INSTALLED:return
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("fixture permit")
    from app.capabilities.transport import HttpxModelTransport
    HttpxModelTransport.send=synthetic_send
    import psycopg
    original_execute=psycopg.AsyncConnection.execute
    async def observed_execute(self,query,*args,**kwargs):
        try:return await original_execute(self,query,*args,**kwargs)
        except psycopg.Error as exc:
            # 只保存带占位的SQL与主错误，不保存bound参数/DSN/失败行detail。
            event("pg_error",{"sqlstate":exc.sqlstate,"message":exc.diag.message_primary,"constraint":exc.diag.constraint_name,
              "table":exc.diag.table_name,"query":str(query)[:4000]})
            raise
    psycopg.AsyncConnection.execute=observed_execute
    sys.setprofile(profile);threading.setprofile(profile);INSTALLED=True
