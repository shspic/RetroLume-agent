"""真实PG/HTTP合并边界；不mock仓储、事务、准入或结果。"""
from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io,json,os,secrets,sys,time
from uuid import uuid4
from urllib.parse import quote
import psycopg
from psycopg import sql
from .control import Control,ROOT,EVIDENCE,atomic_json,SECRET_VALUES,redact
from .resources import OwnedDocker
from .windows_normal import config,MATERIAL


def run():
 control=Control();control.reserve("entry",{"name":"memory-boundaries"})
 start=time.monotonic();docker=OwnedDocker(control);resource=control.load()["resources"][0]
 report={"status":"FAIL","executed":True,"cases":[]};cases=report["cases"]
 def passed(name,**values):
  cases.append({"case":name,"status":"PASS","executed":True,**values})
  atomic_json(EVIDENCE/"memory-boundaries-checkpoint.json",report)
 try:
  docker.start(resource);admin=docker.admin_dsn(resource)
  password=secrets.token_urlsafe(32);denied_password=secrets.token_urlsafe(32);SECRET_VALUES.update([password,denied_password])
  with psycopg.connect(admin,autocommit=True) as conn:
   conn.execute(sql.SQL("ALTER ROLE retrolume_task103_app PASSWORD {}").format(sql.Literal(password)))
   conn.execute(sql.SQL("ALTER ROLE retrolume_task103_denied PASSWORD {}").format(sql.Literal(denied_password)))
  app_dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
  denied_dsn=f"postgresql://retrolume_task103_denied:{quote(denied_password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
  data=EVIDENCE/"workspace"/"data";backup=EVIDENCE/"workspace"/"backup"
  data.mkdir(parents=True,exist_ok=True);backup.mkdir(parents=True,exist_ok=True)
  cfg=EVIDENCE/"workspace"/"boundary-config.json";atomic_json(cfg,config())
  os.environ.update(RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=app_dsn,
    RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=secrets.token_urlsafe(24))
  SECRET_VALUES.add(os.environ["RETROLUME_TASK103_SYNTHETIC_KEY"])
  from app.main import create_app
  from app.runtime import psycopg_compatible_loop_factory
  from app.worker.session import SessionConfig
  from app.memory.contracts import MemoryCommandInput,MemoryRefusal
  from app.learning.teaching_contracts import TeachingCommandInput
  from app.learning.teaching_service import TeachingService
  from app.materials.repository import PostgresMaterials
  from fastapi.testclient import TestClient
  app=create_app();app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
  SECRET_VALUES.add(app.state.session_token)
  def async_run(value):
   with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(value)
  with TestClient(app,backend_options={"loop_factory":psycopg_compatible_loop_factory}) as client:
   headers={"x-retrolume-session":app.state.session_token,"origin":"http://testserver"}
   def req(path,body=None,status=200):
    response=client.get(path,headers=headers) if body is None else client.post(path,json=body,headers=headers)
    assert response.status_code==status,(path,response.status_code,response.json())
    return response.json()
   def save(text="合成自报",title="合成记忆"):
    mid=str(uuid4());key=str(uuid4())
    receipt=req("/api/memories/commands",{"business_key":key,"memory_id":mid,"expected_revision":0,"action":"save",
     "body":{"kind":"self_report","title":title,"text":text}})
    return mid,key,receipt
   def detail(mid):return req("/api/memories/"+mid)
   def impact(mid,revision,action):return req(f"/api/memories/{mid}/impact?expected_revision={revision}&action={action}")
   mid,key,receipt=save()
   original=detail(mid)
   with psycopg.connect(app_dsn) as conn:before=conn.execute("SELECT count(*) FROM learning_memory_commands").fetchone()[0]
   endpoint="/api/memories/commands"
   bad_payloads=[b'{"business_key":"x","business_key":"x"}',b'{"body":{"x":1,"x":2}}',b'{"body":"\xff"}']
   for raw in bad_payloads:
    response=client.post(endpoint,content=raw,headers={**headers,"content-type":"application/json"});assert response.status_code==400
   response=client.post(endpoint,content=b"x"*32769,headers=headers);assert response.status_code==413
   assert client.get("/api/memories",headers={}).status_code==403
   assert client.get("/api/memories",headers={**headers,"origin":"https://other.example","sec-fetch-site":"cross-site"}).status_code==403
   with psycopg.connect(app_dsn) as conn:assert conn.execute("SELECT count(*) FROM learning_memory_commands").fetchone()[0]==before
   passed("V12 strict UTF8/duplicate/bytes/auth zero write",commands_before=before,commands_after=before)
   changed={"business_key":key,"memory_id":mid,"expected_revision":0,"action":"save","body":{"kind":"self_report","title":"异文","text":"异文"}}
   req(endpoint,changed,409);assert detail(mid)["revision"]==1
   received=req("/api/memories/commands/"+key);assert "合成自报" not in json.dumps(received,ensure_ascii=False)
   passed("V10 same key different body rejected, receipt no content",memory_id=mid)
   imp=impact(mid,1,"revise")
   def compete(text):
    return client.post(endpoint,json={"business_key":str(uuid4()),"memory_id":mid,"expected_revision":1,"action":"revise",
     "body":{"kind":"self_report","title":"竞争","text":text,"base_body_sha256":original["body_sha256"],"impact_token":imp["impact_token"]}},headers=headers)
   with ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(compete,["左侧修订","右侧修订"]))
   assert sorted(r.status_code for r in results)==[200,409],[r.json() for r in results]
   assert detail(mid)["revision"]==2
   passed("V11 actual concurrent CAS one effect",statuses=[r.status_code for r in results],revision=2)
   for i in range(50):save(title=("😀界"*40),text="列表合成"+str(i))
   response=client.get("/api/memories?limit=50",headers=headers)
   assert response.status_code==200 and len(response.content)<=65536 and len(response.json()["items"])==50
   assert all("body" not in item and "dependencies" not in item for item in response.json()["items"])
   passed("V09/V21 50 unicode list metadata only",wire_bytes=len(response.content),items=50)
   with psycopg.connect(app_dsn) as conn:
    for statement in ("UPDATE learning_memory_bodies SET body=body WHERE memory_id=%s","DELETE FROM learning_memory_bodies WHERE memory_id=%s",
                      "UPDATE learning_memory_revisions SET uncertainty=uncertainty WHERE memory_id=%s"):
     try:
      with conn.transaction():conn.execute(statement,(mid,))
      raise AssertionError("unauthorized mutation accepted")
     except psycopg.Error:pass
   with psycopg.connect(denied_dsn) as conn:
    try:
     with conn.transaction():conn.execute("SELECT public.purge_learning_memory(%s,%s,%s,%s)",(str(uuid4()),"a"*64,str(uuid4()),"b"*64))
     raise AssertionError("denied function executed")
    except psycopg.errors.InsufficientPrivilege:pass
   passed("V12/V16 real app direct mutation and denied execution rejected")
   pending,_,_=save(text="待清理故障保留")
   imp=impact(pending,1,"revoke")
   revoke=MemoryCommandInput(business_key=str(uuid4()),memory_id=pending,expected_revision=1,action="revoke",
     body={"impact_token":imp["impact_token"],"confirm_revoke":True,"purge_memory_content":True})
   revoked=async_run(app.state.activities_ledger.apply_memory_command(revoke))
   assert revoked["purge_state_now"]=="pending" and detail(pending)["body"] is None
   with psycopg.connect(app_dsn) as conn:
    try:
     with conn.transaction():conn.execute("SELECT public.purge_learning_memory(%s,%s,%s,%s)",(revoke.business_key,"a"*64,str(uuid4()),"b"*64))
     raise AssertionError("wrong manifest accepted")
    except psycopg.Error:pass
    assert conn.execute("SELECT count(*) FROM learning_memory_bodies WHERE memory_id=%s",(pending,)).fetchone()[0]==1
   done=req(endpoint,{"business_key":str(uuid4()),"memory_id":pending,"expected_revision":2,"action":"purge",
      "body":{"revocation_key":revoke.business_key,"manifest_sha256":revoked["manifest_sha256"],"confirm_memory_cleanup":True}})
   assert done["purge_state_now"]=="done"
   passed("V18/V19 separate revoke, wrong manifest retains body, explicit original cleanup",memory_id=pending)

   original_file=app.state.originals.put(io.BytesIO(MATERIAL.encode()),max_bytes=5242880)
   materials=PostgresMaterials(app_dsn)
   source=materials.save(source_id=None,expected_version=None,filename="task103-boundary.md",format="md",sha256=original_file.sha256,size=original_file.size)
   def new_activity(memory=None):
    aid=str(uuid4());body={"activity_id":aid,"source_ids":[source["id"]]}
    if memory:
     view=detail(memory);body["memory_selection"]={"confirmed":True,"entries":[{"memory_id":memory,"version":view["version"],"revision":view["revision"],"body_sha256":view["body_sha256"]}]}
    req("/api/activities",body);return aid
   def workspace(aid):return req(f"/api/activities/{aid}/teaching/workspace")
   def command(aid,action,body):
    view=workspace(aid)
    return {"business_key":str(uuid4()),"expected_revision":view["head"]["revision"],"expected_goal_version":view["head"]["goal_version"],
      "expected_scope_revision":1,"action":action,"body":body}
   def submit(aid,action,body):return req(f"/api/activities/{aid}/teaching/commands",command(aid,action,body))
   def goal(aid):submit(aid,"goal",{"goal":"平均速度和秒的换算","self_report":None,"domain":None,"seed_operation_id":None,"seed_payload_sha256":None})

   bg,_,_=save();aid=new_activity(bg);goal(aid)
   cfg=app.state.activity_config
   teach=TeachingService(app.state.activities_ledger,app.state.materials,app.state.originals,session_config=app.state.teaching_session_config)
   plan_command=TeachingCommandInput.model_validate(command(aid,"plan",{"confirmed":True,"correction_record_id":None,"retry_of":None}))
   frozen,_=async_run(teach._freeze_model_context(aid,plan_command,cfg))
   accepted=async_run(app.state.activities_ledger.accept_teaching_command(aid,plan_command,frozen))
   assert accepted.status=="accepted";sup_before=control.load()["counts"]["sup"]
   current=detail(bg);imp=impact(bg,1,"revise")
   req(endpoint,{"business_key":str(uuid4()),"memory_id":bg,"expected_revision":1,"action":"revise",
     "body":{"kind":"self_report","title":"失效","text":"新背景","base_body_sha256":current["body_sha256"],"impact_token":imp["impact_token"]}})
   old=req(f"/api/activities/{aid}/teaching/commands/{plan_command.business_key}")
   assert old["retry_policy"]=="read_only" and old["qualification"]=="memory_invalid",old
   req(f"/api/activities/{aid}/teaching/commands",plan_command.model_dump(),409)
   assert control.load()["counts"]["sup"]==sup_before
   passed("V13 accept-unclaimed invalid memory zero launch",activity_id=aid,sup_delta=0)

   plain=new_activity();goal(plain)
   proposed=submit(plain,"plan",{"confirmed":True,"correction_record_id":None,"retry_of":None});assert proposed["status"]=="committed"
   view=workspace(plain);submit(plain,"accept_path",{"proposal_record_id":view["proposal"]["record_id"]})
   view=workspace(plain)
   ex=submit(plain,"exercise",{"confirmed":True,"path_record_id":view["head"]["path_record_id"],"node_id":"n1","purpose":"initial","parent_feedback_record_id":None,"retry_of":None})
   assert ex["status"]=="committed"
   eid=workspace(plain)["head"]["exercise_record_id"]
   answer=submit(plain,"answer",{"exercise_record_id":eid,"kind":"initial","text":"1m/s","supersedes_answer_record_id":None})
   evaluation=submit(plain,"evaluate",{"confirmed":True,"exercise_record_id":eid,"answer_record_id":answer["record_ids"][0]["record_id"],"correction_record_id":None,"retry_of":None})
   assert evaluation["status"]=="committed";view=workspace(plain);pid=view["head"]["reason_record_id"]
   preview=req(f"/api/activities/{plain}/teaching/records/{pid}/memory-preview")
   observed=str(uuid4())
   req(endpoint,{"business_key":str(uuid4()),"memory_id":observed,"expected_revision":0,"action":"save",
     "body":{"kind":"learning_observation","title":"有限源观察","text":"","capture":preview["capture"]}})
   assert detail(observed)["qualification"]=="current"
   target=new_activity(observed);goal(target)
   submit(plain,"correct",{"target_record_id":pid,"text":"这是我的争议注记","disputed_dimensions":["value"]})
   assert detail(observed)["body"] is None
   assert workspace(target)["memory_invalid"]
   req(f"/api/activities/{plain}/teaching/records/{pid}/memory-preview",status=409)
   passed("V07/V17 original correction invalidates saved observation, preview suppressed",memory_id=observed,target_activity=target)
   with psycopg.connect(app_dsn) as conn:
    fact=conn.execute("SELECT body,body_sha256 FROM teaching_records WHERE activity_id=%s AND record_id=%s",(plain,pid)).fetchone()
    try:
     with conn.transaction():conn.execute("UPDATE teaching_records SET body=body WHERE activity_id=%s AND record_id=%s",(plain,pid))
     raise AssertionError("old fact editable")
    except psycopg.Error:pass
    assert conn.execute("SELECT body,body_sha256 FROM teaching_records WHERE activity_id=%s AND record_id=%s",(plain,pid)).fetchone()==fact
   passed("V16 immutable original progress unchanged")
   source_bg,_,_=save();source_target=new_activity(source_bg)
   replacement=app.state.originals.put(io.BytesIO((MATERIAL+"这是新版本。").encode()),max_bytes=5242880)
   materials.save(source_id=source["id"],expected_version=source["version_id"],filename="task103-boundary-new.md",format="md",sha256=replacement.sha256,size=replacement.size)
   selected=async_run(app.state.activities_ledger.read_memory_selection(source_target));assert not selected["eligible"]
   passed("V05 source replacement invalidates target scope even self-report selection",activity_id=source_target)
  report["status"]="PASS"
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)))
  (EVIDENCE/"memory-boundaries-error.txt").write_bytes(redact(__import__("traceback").format_exc()).encode())
 finally:
  control.charge("real",time.monotonic()-start,{"name":"memory-boundaries"})
  clean=time.monotonic()
  try:report["cleanup"]=docker.stop(resource)
  except BaseException as exc:report["cleanup_unconfirmed"]=type(exc).__name__;report["status"]="FAIL"
  control.charge("cleanup",time.monotonic()-clean,{"name":"memory-boundaries"})
  atomic_json(EVIDENCE/"memory-boundaries-result.json",report)
 print(json.dumps({"status":report["status"],"cases":len(cases),"error_type":report.get("error_type"),"message":report.get("message")},ensure_ascii=False))
 return 0 if report["status"]=="PASS" else 1

if __name__=="__main__":sys.exit(run())

