"""真实新API/最终dist/PG/浏览器根入口，记录自己的PID和出生身份。"""
from __future__ import annotations
import io,json,os,secrets,subprocess,sys,time,urllib.request
from urllib.parse import quote
import psycopg
from psycopg import sql
from .control import Control,EVIDENCE,ROOT,SECRET_VALUES,atomic_json,redact
from .resources import OwnedDocker,port_available
from .processes import process_state,stop_owned
from .windows_normal import config,MATERIAL


def run():
 control=Control();control.reserve("entry",{"name":"browser-workspace"})
 start=time.monotonic();docker=OwnedDocker(control);resource=control.load()["resources"][0]
 attempt=os.environ.get("RETROLUME_TASK103_BROWSER_ATTEMPT","01")
 server=None;witness=None;report={"status":"FAIL","executed":True}
 try:
  if not port_available(18103):raise RuntimeError("owned API port unavailable")
  docker.start(resource);admin=docker.admin_dsn(resource)
  password=secrets.token_urlsafe(32);SECRET_VALUES.add(password)
  with psycopg.connect(admin,autocommit=True) as conn:
   conn.execute(sql.SQL("ALTER ROLE retrolume_task103_app PASSWORD {}").format(sql.Literal(password)))
  dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
  from app.storage.originals import OriginalStore
  from app.materials.repository import PostgresMaterials
  data=EVIDENCE/"workspace"/"data";backup=EVIDENCE/"workspace"/"backup";originals=data/"originals"
  data.mkdir(parents=True,exist_ok=True);backup.mkdir(parents=True,exist_ok=True);originals.mkdir(exist_ok=True)
  original=OriginalStore(originals).put(io.BytesIO(MATERIAL.encode()),max_bytes=5242880)
  material=PostgresMaterials(dsn).save(source_id=None,expected_version=None,filename="task103-browser-material.md",format="md",
    sha256=original.sha256,size=original.size)
  cfg=EVIDENCE/"workspace"/"browser-config.json";atomic_json(cfg,config())
  env=os.environ.copy()
  for k in list(env):
   if k.startswith("RETROLUME_TASK100_"):env.pop(k,None)
  key=secrets.token_urlsafe(24);SECRET_VALUES.add(key)
  env.update(RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=dsn,
    RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=key,RETROLUME_TASK103_FIXTURE="TASK-103-G9-20261006",
    PYTHONPATH=str(ROOT/"backend/tests/fixtures/task103/bootstrap")+os.pathsep+str(ROOT/"backend"))
  control.reserve("listener_start",{"module":"tests.fixtures.task103.server","port":18103})
  server=subprocess.Popen([sys.executable,"-X","utf8","-B","-m","tests.fixtures.task103.server"],
    cwd=ROOT/"backend",env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  state=process_state(server.pid)
  witness={**state,"module":"tests.fixtures.task103.server"};report["server_witness"]=witness
  deadline=time.monotonic()+20
  while True:
   if server.poll() is not None:raise RuntimeError("owned server exited")
   try:
    with urllib.request.urlopen("http://127.0.0.1:18103/health",timeout=1) as response:
     if response.status==200:break
   except Exception:
    if time.monotonic()>=deadline:raise RuntimeError("owned server readiness timeout")
    time.sleep(.1)
  control.reserve("driver",{"script":"frontend/tests/task103-browser.cjs"})
  control.reserve("browser",{"profile":"workspace/browser-profile-"+attempt})
  result=subprocess.run(["node",str(ROOT/"frontend/tests/task103-browser.cjs")],cwd=ROOT/"frontend",
    env=env,capture_output=True,timeout=min(600,control.remaining("real",600)),creationflags=subprocess.CREATE_NO_WINDOW)
  (EVIDENCE/("browser-"+attempt+"-node-stdout.txt")).write_bytes(redact(result.stdout.decode("utf-8","replace")).encode())
  (EVIDENCE/("browser-"+attempt+"-node-stderr.txt")).write_bytes(redact(result.stderr.decode("utf-8","replace")).encode())
  actual=json.loads((EVIDENCE/("browser-"+attempt+"/result.json")).read_text(encoding="utf-8"))
  report.update(browser=actual,exit_code=result.returncode)
  assert result.returncode==0 and actual["status"]=="PASS",actual.get("error","browser failed")
  report["status"]="PASS"
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)))
  (EVIDENCE/("browser-root-"+attempt+"-error.txt")).write_bytes(redact(__import__("traceback").format_exc()).encode())
 finally:
  control.charge("real",time.monotonic()-start,{"name":"browser-workspace"})
  clean=time.monotonic()
  if server and witness:
   try:
    report["server_stop"]=stop_owned(server,witness)
    stdout,stderr=server.communicate(timeout=5)
    (EVIDENCE/("browser-"+attempt+"-server-stdout.txt")).write_bytes(redact(stdout.decode("utf-8","replace")).encode())
    (EVIDENCE/("browser-"+attempt+"-server-stderr.txt")).write_bytes(redact(stderr.decode("utf-8","replace")).encode())
   except BaseException as exc:report["server_stop_unconfirmed"]=type(exc).__name__;report["status"]="FAIL"
  report["port18103_available"]=port_available(18103)
  try:report["container_stop"]=docker.stop(resource)
  except BaseException as exc:report["container_stop_unconfirmed"]=type(exc).__name__;report["status"]="FAIL"
  control.charge("cleanup",time.monotonic()-clean,{"name":"browser-workspace"})
  atomic_json(EVIDENCE/("browser-root-"+attempt+"-result.json"),report)
 print(json.dumps({"status":report["status"],"error":report.get("message"),"port_free":report.get("port18103_available")},ensure_ascii=False))
 return 0 if report["status"]=="PASS" else 1

if __name__=="__main__":sys.exit(run())

