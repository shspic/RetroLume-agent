"""仅替代最低provider transport；用profile观察原函数，不替代任何权威。"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import threading
import time
from uuid import uuid4
from .control import Control,EVIDENCE,atomic_json
INSTALLED=False
SQL_FRAMES=set()

def race_wait(phase,activity_id=None):
    raw=os.environ.get('RETROLUME_TASK103_RACE')
    if not raw:return
    spec=json.loads(raw)
    if spec['phase']!=phase or (activity_id and spec['activity_id']!=activity_id):return
    base=Path(spec['path']).resolve()
    if not base.is_relative_to((EVIDENCE/'workspace/races').resolve()):raise RuntimeError('race path outside permit')
    atomic_json(base.with_suffix('.ready.json'),{'phase':phase,'activity_id':spec['activity_id'],'pid':os.getpid()})
    end=time.monotonic()+5
    while not base.with_suffix('.release.json').exists():
        if time.monotonic()>=end:raise RuntimeError('synthetic race actor timeout')
        time.sleep(.01)


def observation(kind,value):
    target=EVIDENCE/"observations"
    atomic_json(target/(str(time.time_ns())+"-"+str(os.getpid())+"-"+uuid4().hex+"-"+kind+".json"),
      {"kind":kind,"pid":os.getpid(),"value":value})


def profile(frame,event,arg):
    file=frame.f_code.co_filename.replace("\\","/")
    name=frame.f_code.co_name
    if event=='return' and name=='admit' and '/app/activities/repository.py' in file and hasattr(arg,'admission_id'):
        race_wait('after_admit',frame.f_locals['intent'].context.activity_id)
    tag=os.environ.get('RETROLUME_TASK103_READ_TAG')
    if tag and name=='execute' and '/psycopg/connection_async.py' in file:
        if event=='call' and id(frame) not in SQL_FRAMES:
            SQL_FRAMES.add(id(frame));query=frame.f_locals.get('query')
            if isinstance(query,str):observation('sql',{'tag':tag,'sql':query,'arguments_saved':False})
        if event=='return' and type(arg).__name__=='AsyncCursor':SQL_FRAMES.discard(id(frame))
    if event=="call" and name in ("run_one_call","run_one_tool") and "/app/worker/" in file:
        Control().reserve("sup",{"kind":name,"caller_pid":os.getpid()})
    elif event=="return" and name in ("run_one_call","run_one_tool") and "/app/worker/" in file and arg is not None:
        keys=("state","activity_id","generation","job_name","pid","active_processes_at_end","settled_seconds",
              "reserved_seconds","cleanup_incomplete","manager_pid","manager_created_100ns","worker_created_100ns")
        observation("session",{k:getattr(arg,k,None) for k in keys})
    elif event=="return" and frame.f_code.co_qualname=="_SuspendedSupervisor.create" and "/app/worker/launcher.py" in file and arg is not None:
        observation("sup",{"pid":arg.pid,"created_100ns":arg.creation_time_100ns()})


async def synthetic_send(self,*,endpoint,api_key,payload,timeout_seconds,max_response_bytes):
    from app.capabilities.transport import TransportResponse
    from app.learning.contracts import canonical,sha
    document=json.loads(next(m["content"] for m in reversed(payload["messages"]) if m["role"]=="user"))
    task=document["task"];kind=task["kind"];citations=[x["id"] for x in document["evidence"]][:1]
    if kind=="plan":
        result={"result_type":"path","message":"依据当前资料练习速度单位，背景仅作偏好。",
          "nodes":[{"title":"平均速度与单位","objective":"能用路程和时间求速度","prerequisites":[],
            "rationale":"按原文公式并独立复测，不据自报宣布掌握","citations":citations,
            "completion_dimensions":[{"dimension":"value","required_point":"统一秒与米后给出速度"}]}]}
    elif kind=="exercise":
        distance=180 if task.get("purpose")=="retest" else 120
        result={"result_type":"exercise","message":"一次有限新练习","exercise_type":"calculation","difficulty":1,
          "stem":str(distance)+"米用"+str(distance)+"秒，平均速度是多少？",
          "reference_points":[{"point_id":"p1","text":"路程除以时间得到1米每秒","citations":citations,
            "numeric":{"value_decimal":"1","unit":"m/s","operation":"divide","left":str(distance),"right":str(distance),"tolerance_decimal":None}}],
          "reference_explanation":"先统一单位，路程除以时间。","dimensions":[{"id":"value","point_ids":["p1"],"description":"速度数值与单位"}],
          "hint":"先确认米和秒","variant":{"purpose":task["purpose"],"parent_exercise_record_id":task.get("parent_exercise_record_id"),
            "parent_feedback_record_id":task.get("parent_feedback_record_id"),"instance_data":{"kind":"calculation","quantities":[
            {"name":"distance","value_decimal":str(distance),"unit":"m"},{"name":"time","value_decimal":str(distance),"unit":"s"}]}}}
    elif kind=="evaluate":
        answer=task["answer_text"]
        result={"result_type":"feedback","message":"有限评价，仅供下一步复测。","correct_parts":[{"answer_excerpt":answer[:200],
          "explanation":"对照本题资料与数值依据","point_ids":["p1"],"citations":citations}],
          "errors":[],"evidence_gaps":[],"cause_hypotheses":[{"hypothesis":"仍需要更多独立表现","evidence_for":"单次有限作答",
           "missing_evidence":"独立复测","confidence":"unknown"}],
          "dimension_observations":[{"id":"value","observation":"met","reason":"合成故意met，应用仍须实际支持检查","point_ids":["p1"]}],
          "next_focus":{"focus_dimension":"value","reason":"独立实例用于核对","suggested_mode":"retest"}}
    else:raise RuntimeError("unknown synthetic action")
    observation("provider",{"action":kind,"messages_sha256":sha(canonical(payload["messages"])),
       "background_count":len(document.get("learning_background",[])),
       "background_ids":[x["memory_id"] for x in document.get("learning_background",[])],
       "citation_ids":citations,"result":result})
    response={"id":"task103-"+uuid4().hex,"object":"chat.completion","model":payload["model"],
       "choices":[{"index":0,"message":{"role":"assistant","content":canonical(result)},"finish_reason":"stop"}],
       "usage":{"prompt_tokens":128,"completion_tokens":64,"total_tokens":192,"prompt_tokens_details":{"cached_tokens":0}}}
    body=canonical(response).encode()
    race_wait('before_result')
    return TransportResponse(200,body,len(body),remote_request_id=response["id"])


def install():
    global INSTALLED
    if INSTALLED:return
    from app.capabilities.transport import HttpxModelTransport
    HttpxModelTransport.send=synthetic_send
    sys.setprofile(profile);threading.setprofile(profile)
    INSTALLED=True
