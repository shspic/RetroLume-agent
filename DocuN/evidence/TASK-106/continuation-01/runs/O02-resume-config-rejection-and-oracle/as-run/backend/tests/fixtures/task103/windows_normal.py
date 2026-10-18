"""新合成PG+真实HTTP入口函数+原Windows监督链的正常v2组合。"""
from __future__ import annotations
import io,json,os,secrets,sys,time
from uuid import uuid4
import psycopg
from psycopg import sql
from .control import Control,ROOT,EVIDENCE,atomic_json,SECRET_VALUES,redact
from .resources import OwnedDocker

MATERIAL="平均速度等于路程除以时间，先统一米和秒。120米除以120秒是1米每秒。180米除以180秒也是1米每秒。单次正确不能证明长期掌握。\n"


def config():
 return {"model_identity":{"provider":"deepseek_chat_completions","model":"deepseek-v4-flash"},
  "activity_defaults":{"deadline_hours":1,"max_requests":24,"max_cost_microunits":1000000,
   "reserve_cost_microunits":1000,"max_request_bytes":65536,"max_output_tokens":2048,"max_running_seconds":240,
   "allowed_tools":["finite_calculate"],"max_tool_calls":4},
  "service":{"base_url":"https://api.deepseek.com","thinking":"disabled","timeout_seconds":2.0,
   "max_output_tokens_limit":2048,"max_request_bytes":65536,"max_response_bytes":65536},
  "api_key_env":"RETROLUME_TASK103_SYNTHETIC_KEY",
  "learning":{"profile":"learning.v1","max_output_tokens":256},
  "teaching":{"profile":"teaching.v1","max_output_tokens":2048,"enable_calculation":True},
  "memory_context":{"selected_items":4,"max_memory_bytes":4096,"max_memory_chars":2048,
   "model_context_tokens":32768,"max_input_tokens_estimate":24576,"protocol_reserve_tokens":1024,
   "reserved_output_tokens":2048,"safety_tokens":2048,"estimate_policy":"utf8_bytes.v1",
   "model_identity":{"provider":"deepseek_chat_completions","model":"deepseek-v4-flash"}}}


def run():
 control=Control();control.reserve("entry",{"name":"windows-v2-normal"})
 start=time.monotonic();resource=control.load()["resources"][0];docker=OwnedDocker(control)
 report={"status":"FAIL","executed":True};case={}
 try:
  docker.start(resource);admin=docker.admin_dsn(resource)
  assert control.load()["counts"]["listener_start"]==0
  password=secrets.token_urlsafe(32);SECRET_VALUES.add(password)
  with psycopg.connect(admin,autocommit=True) as conn:
   conn.execute(sql.SQL("ALTER ROLE retrolume_task103_app PASSWORD {}").format(sql.Literal(password)))
  from urllib.parse import quote
  dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
  data=EVIDENCE/"workspace"/"data";backup=EVIDENCE/"workspace"/"backup"
  data.mkdir(parents=True,exist_ok=True);backup.mkdir(parents=True,exist_ok=True)
  cfg=EVIDENCE/"workspace"/"activity-test.json";atomic_json(cfg,config())
  os.environ.update(RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=dsn,
   RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=secrets.token_urlsafe(24))
  SECRET_VALUES.add(os.environ["RETROLUME_TASK103_SYNTHETIC_KEY"])
  from app.main import create_app
  from app.worker.session import SessionConfig
  from app.runtime import psycopg_compatible_loop_factory
  from fastapi.testclient import TestClient
  from app.materials.repository import PostgresMaterials
  app=create_app()
  app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
  session=app.state.session_token;SECRET_VALUES.add(session)
  original=app.state.originals.put(io.BytesIO(MATERIAL.encode()),max_bytes=5242880)
  source=PostgresMaterials(dsn).save(source_id=None,expected_version=None,filename="task103-v2-synthetic.md",
     format="md",sha256=original.sha256,size=original.size)
  with TestClient(app,backend_options={"loop_factory":psycopg_compatible_loop_factory}) as client:
   headers={"x-retrolume-session":session,"origin":"http://testserver"}
   def req(path,body=None,status=200):
    response=client.get(path,headers=headers) if body is None else client.post(path,json=body,headers=headers)
    assert response.status_code==status,(path,response.status_code,response.json())
    return response.json()
   case["capabilities"]=req("/api/activities/capabilities")
   assert case["capabilities"]["teaching"]["available"] and case["capabilities"]["memory_model"]["available"],case["capabilities"]
   mid=str(uuid4());note="合成背景：我经常忘记单位，仍需复测"
   saved=req("/api/memories/commands",{"business_key":str(uuid4()),"memory_id":mid,"expected_revision":0,"action":"save",
     "body":{"kind":"self_report","title":"单位偏好","text":note}})
   detail=req("/api/memories/"+mid)
   aid=str(uuid4());case.update(memory_id=mid,activity_id=aid,source_id=source["id"])
   created=req("/api/activities",{"activity_id":aid,"source_ids":[source["id"]],"memory_selection":{"confirmed":True,
     "entries":[{"memory_id":mid,"version":1,"revision":1,"body_sha256":detail["body_sha256"]}]}})
   assert created["activity"]["memory_selection"]["eligible"],created
   def workspace():return req(f"/api/activities/{aid}/teaching/workspace")
   def command(action,body):
    view=workspace()
    return req(f"/api/activities/{aid}/teaching/commands",{"business_key":str(uuid4()),"expected_revision":view["head"]["revision"],
      "expected_goal_version":view["head"]["goal_version"],"expected_scope_revision":1,"action":action,"body":body})
   command("goal",{"goal":"理解平均速度并统一米和秒","self_report":None,"domain":None,"seed_operation_id":None,"seed_payload_sha256":None})
   sup_before=control.load()["counts"]["sup"]
   proposal=command("plan",{"confirmed":True,"correction_record_id":None,"retry_of":None})
   assert proposal["status"]=="committed",proposal
   view=workspace();pid=view["proposal"]["record_id"]
   command("accept_path",{"proposal_record_id":pid})
   view=workspace()
   exercise=command("exercise",{"confirmed":True,"path_record_id":view["head"]["path_record_id"],"node_id":view["head"]["node_id"],
     "purpose":"initial","parent_feedback_record_id":None,"retry_of":None})
   assert exercise["status"]=="committed",exercise
   eid=workspace()["head"]["exercise_record_id"]
   answer=command("answer",{"exercise_record_id":eid,"kind":"initial","text":"1m/s","supersedes_answer_record_id":None})
   answer_id=answer["record_ids"][0]["record_id"]
   evaluation=command("evaluate",{"confirmed":True,"exercise_record_id":eid,"answer_record_id":answer_id,"correction_record_id":None,"retry_of":None})
   assert evaluation["status"]=="committed",evaluation
   view=workspace();assert view["feedback"]["qualification"]=="current",view
   progress_id=view["head"]["reason_record_id"]
   preview=req(f"/api/activities/{aid}/teaching/records/{progress_id}/memory-preview")
   captured=req("/api/memories/commands",{"business_key":str(uuid4()),"memory_id":str(uuid4()),"expected_revision":0,"action":"save",
    "body":{"kind":"learning_observation","title":"本轮有限表现","text":"仍需更多复测","capture":preview["capture"]}})
   with psycopg.connect(dsn) as conn:
    stored=conn.execute("SELECT context_body FROM teaching_commands WHERE activity_id=%s AND action='plan'",(aid,)).fetchone()[0]
    frozen=json.loads(stored);assert frozen["schema"]=="teaching.context.v2" and "messages" not in frozen and note not in stored
    before=conn.execute("SELECT requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds FROM activities WHERE id=%s",(aid,)).fetchone()
   impact=req(f"/api/memories/{mid}/impact?expected_revision=1&action=revise")
   req("/api/memories/commands",{"business_key":str(uuid4()),"memory_id":mid,"expected_revision":1,"action":"revise",
    "body":{"kind":"self_report","title":"新版本背景","text":"背景已变更","base_body_sha256":detail["body_sha256"],"impact_token":impact["impact_token"]}})
   invalid=workspace();assert invalid["memory_invalid"] and not invalid["nodes"]
   record=req(f"/api/activities/{aid}/teaching/records/{evaluation['record_ids'][0]['record_id']}")
   assert record["public_body"] is None and record["qualification"]=="memory_invalid",record
   with psycopg.connect(dsn) as conn:
    after=conn.execute("SELECT requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds FROM activities WHERE id=%s",(aid,)).fetchone()
    assert before==after
   case.update(frozen_schema=frozen["schema"],context_has_messages=False,context_has_memory_text=False,
      sup_delta=control.load()["counts"]["sup"]-sup_before,budget_before=list(before),budget_after=list(after),
      captured_memory_id=captured["memory_id"],final_workspace=invalid,feedback_record=record)
   assert case["sup_delta"]==3 and before[3]==0,case
  report={"status":"PASS","executed":True,**case}
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)),case=case)
  (EVIDENCE/"windows-v2-normal-error.txt").write_bytes(redact(__import__("traceback").format_exc()).encode())
 finally:
  control.charge("real",time.monotonic()-start,{"name":"windows-v2-normal"})
  clean=time.monotonic()
  try:report["cleanup"]=docker.stop(resource)
  except BaseException as exc:report["cleanup_unconfirmed"]=type(exc).__name__;report["status"]="FAIL"
  control.charge("cleanup",time.monotonic()-clean,{"name":"windows-v2-normal"})
  atomic_json(EVIDENCE/"windows-v2-normal-result.json",report)
 print(json.dumps({"status":report["status"],"error":report.get("error_type"),"message":report.get("message"),"case_ids":case},ensure_ascii=False))
 return 0 if report["status"]=="PASS" else 1

if __name__=="__main__":sys.exit(run())

