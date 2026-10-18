"""097唯一受控资源入口，预检abort计账，finally保留库卷并停止精确资源。"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/"DocuN/evidence/TASK-097"))
from artifacts import E,PY,freeze,append_event,write,digest

CID="e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4"
NAME="retrolume-task-088-g3-w1"
IMAGE="sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
VOLUME="retrolume-task-088-g3-w1-data"
ADMIN="retrolume_task088_synth"
DB="retrolume_task097_g7"
ROLE="retrolume_task097_synth"


def docker(*args,timeout=30,input=None):
    return subprocess.run(["docker",*args],input=input,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)


def inspect_guard():
    result=docker("inspect",CID)
    if result.returncode:raise ValueError("精确容器inspect失败")
    data=json.loads(result.stdout)[0]
    host=data["HostConfig"]
    assert data["Id"]==CID and data["Name"]=="/"+NAME and data["Image"]==IMAGE and data["Config"]["Image"]==IMAGE
    assert host["Memory"]==536870912 and host["NanoCpus"]==1000000000 and host["PidsLimit"]==128
    assert not host["Privileged"] and host["NetworkMode"] not in {"host","none"} and host.get("PidMode")!="host"
    assert host.get("RestartPolicy",{}).get("Name") in {"no",""}
    assert not host.get("Devices") and not host.get("CapAdd")
    ports=host.get("PortBindings",{})
    assert set(ports)=={"5432/tcp"} and ports["5432/tcp"]==[{"HostIp":"127.0.0.1","HostPort":"55441"}]
    mounts=data["Mounts"]
    assert len(mounts)==1 and mounts[0]["Type"]=="volume" and mounts[0]["Name"]==VOLUME
    assert mounts[0]["Destination"]=="/var/lib/postgresql/data" and mounts[0]["RW"] is True
    assert all(b.split(":")[0]==VOLUME for b in host.get("Binds") or [])
    return {"id":data["Id"],"name":data["Name"],"image":data["Image"],"volume":VOLUME,
        "running":data["State"]["Running"],"pid":data["State"]["Pid"],"ports":ports,
        "memory":host["Memory"],"cpu":host["NanoCpus"],"pids_limit":host["PidsLimit"],
        "env_inspected_in_memory_only":True,"env_logged":False}


def free(port):
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        probe.bind(("127.0.0.1",port))


def psql(sql,database,*,secret=False,label=None,out=None):
    r=docker("exec","-i","-e","PGOPTIONS=-c statement_timeout=10000 -c lock_timeout=2000",CID,
        "psql","-X","-q","-A","-t","-v","ON_ERROR_STOP=1","-U",ADMIN,"-d",database,input=sql)
    if out and label:
        (out/(label+".stdout.txt")).write_text("凭据SQL不记录正文\n" if secret else r.stdout,encoding="utf-8")
        (out/(label+".stderr.txt")).write_text("凭据SQL仅记录退出码\n" if secret else r.stderr,encoding="utf-8")
        write(out/(label+".run.json"),{"exit_code":r.returncode,"database":database,"role":ADMIN,"secret_sql":secret})
    if r.returncode:raise ValueError("097数据库准备失败，详情见非敏感阶段输出")
    return r.stdout.strip()


def provision(out):
    state=E/"resource-ownership.json"
    owns=json.loads(state.read_text(encoding="utf-8")) if state.exists() else {}
    facts=json.loads(psql("SELECT json_build_object('db_owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='"+DB+"'),"
        "'role_exists',EXISTS(SELECT 1 FROM pg_roles WHERE rolname='"+ROLE+"'),'role_sessions',(SELECT count(*) FROM pg_stat_activity WHERE usename='"+ROLE+"'));", "postgres"))
    if facts["db_owner"] or facts["role_exists"]:
        if owns.get("created_db")!=DB or owns.get("created_role")!=ROLE or facts["db_owner"]!=ADMIN or not facts["role_exists"]:
            raise ValueError("097同名对象归属不明，拒绝覆盖")
        if facts["role_sessions"]!=0:raise ValueError("097角色被其他会话使用")
    else:
        psql("CREATE DATABASE "+DB+" OWNER "+ADMIN+";", "postgres",label="create-db",out=out)
        owns={"task":"TASK-097","container":CID,"created_db":DB,"created_role":None,"created_at":datetime.now(timezone.utc).isoformat()}
        write(state,owns)
    password=secrets.token_urlsafe(32)
    sql=("ALTER ROLE " if facts["role_exists"] else "CREATE ROLE ")+ROLE+" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD '"+password+"';"
    psql(sql,"postgres",secret=True,label="role-password-stdin",out=out)
    owns["created_role"]=ROLE;write(state,owns)
    tables=psql("SELECT count(*) FROM pg_tables WHERE schemaname='public';",DB)
    if int(tables)==0:
        for file in sorted((ROOT/"backend/migrations").glob("00[1-8]_*.sql")):
            psql(file.read_text(encoding="utf-8"),DB,label=file.stem,out=out)
    elif not owns.get("schema_initialized"):
        raise ValueError("097初始化未完成，必须查明已执行迁移，不能覆盖重建")
    psql("REVOKE CONNECT ON DATABASE "+DB+" FROM PUBLIC; GRANT CONNECT ON DATABASE "+DB+" TO "+ROLE+";"
        "REVOKE CREATE ON SCHEMA public FROM PUBLIC; GRANT USAGE ON SCHEMA public TO "+ROLE+";"
        "GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO "+ROLE+";",DB,label="limited-grants",out=out)
    owns["schema_initialized"]=True;write(state,owns)
    permissions=psql("SELECT json_build_object('db',current_database(),'super',rolsuper,'create_db',rolcreatedb,'create_role',rolcreaterole,"
        "'replication',rolreplication,'bypass_rls',rolbypassrls,'member_count',(SELECT count(*) FROM pg_auth_members WHERE member=r.oid)) "
        "FROM pg_roles r WHERE rolname='"+ROLE+"';",DB)
    write(out/"role-permissions.json",json.loads(permissions))
    assert all(not json.loads(permissions)[k] for k in ["super","create_db","create_role","replication","bypass_rls","member_count"])
    return f"host=127.0.0.1 port=55441 dbname={DB} user={ROLE} password={password} connect_timeout=3"


def main():
    mode=sys.argv[1]
    attempts=json.loads((E/"attempt-ledger.json").read_text(encoding="utf-8")) if (E/"attempt-ledger.json").exists() else []
    entries=sum(1 for x in attempts if x.get("category")=="integration_entry")
    if entries>=8:raise ValueError("097入口额度已用尽")
    label=f"integration-{entries+1:02d}-{mode}"
    out=E/label;out.mkdir()
    start=time.monotonic();started_container=False;cleanup_start=None;resultcode=1;error=None
    append_event({"category":"integration_entry","label":label,"entry_number":entries+1,"started_at":datetime.now(timezone.utc).isoformat()})
    freeze(label,[str(PY),"-B",str(Path(__file__).resolve()),mode],"专用PG/HTTP以及按模式受控Windows/浏览器；最多900业务秒+120清理秒")
    try:
        facts=inspect_guard();write(out/"container-pre.json",facts)
        if facts["running"] or facts["pid"]!=0:raise ValueError("精确容器已运行或被其他任务使用")
        for port in [18097,15197,55441]:free(port)
        starts=sum(1 for x in attempts if x.get("category")=="container_start")
        if starts>=8:raise ValueError("097容器start额度已用尽")
        append_event({"category":"container_start","label":label,"container":CID})
        result=docker("start",CID)
        if result.returncode:raise ValueError("精确容器启动失败")
        started_container=True
        deadline=time.monotonic()+20
        while True:
            ready=docker("exec",CID,"pg_isready","-U",ADMIN,"-d","postgres",timeout=5)
            if ready.returncode==0:break
            if time.monotonic()>deadline:raise ValueError("专用PG未在期限就绪")
            time.sleep(.2)
        dsn=provision(out)
        env={**os.environ,"RETROLUME_TASK097_DSN":dsn,"RETROLUME_TASK097_OUT":str(out),"PYTHONIOENCODING":"utf-8"}
        if mode=="pg":
            cmd=[str(PY),"-B",str(ROOT/"backend/tests/fixtures/task097/pg_run.py")]
        elif mode=="business":
            cmd=[str(PY),"-B",str(ROOT/"backend/tests/fixtures/task097/business_run.py")]
        else:raise ValueError("未授权的runner模式")
        remaining=min(900-(time.monotonic()-start),3600-sum(x.get("business_seconds",0) for x in attempts if x.get("category")=="integration_end"))
        result=subprocess.run(cmd,cwd=ROOT,capture_output=True,env=env,timeout=remaining)
        (out/"stdout.bin").write_bytes(result.stdout);(out/"stderr.bin").write_bytes(result.stderr)
        resultcode=result.returncode
        print(result.stdout.decode("utf-8","replace"));print(result.stderr.decode("utf-8","replace"))
    except BaseException as exc:
        error=type(exc).__name__+": "+str(exc)[:200]
        print(error)
    finally:
        cleanup_start=time.monotonic();business=cleanup_start-start
        cleanup_ok=True
        if started_container:
            r=docker("stop","--time","5",CID,timeout=30)
            facts=inspect_guard();write(out/"container-post.json",facts)
            cleanup_ok=r.returncode==0 and not facts["running"] and facts["pid"]==0
        for port in [18097,15197]:
            try:free(port)
            except OSError:cleanup_ok=False
        cleanup=time.monotonic()-cleanup_start
        state={"exit_code":resultcode,"error":error,"business_seconds":business,"cleanup_seconds":cleanup,
            "total_seconds":time.monotonic()-start,"container_started":started_container,"cleanup_ok":cleanup_ok}
        write(out/"run.json",state)
        append_event({"category":"integration_end","label":label,**state})
        write(out/"post-hashes.json",{p.relative_to(ROOT).as_posix():digest(p) for p in __import__("artifacts").files()})
    if not cleanup_ok:return 2
    return resultcode


if __name__=="__main__":raise SystemExit(main())
