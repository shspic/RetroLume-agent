from pathlib import Path
src=Path("Ndocu/evidence/task-083/d3-implementation-10/runner.py")
dst=src.with_name("runner_replacement.py")
s=src.read_text(encoding="utf-8")
def rep(a,b):
 global s
 count=s.count(a)
 if count!=1: raise RuntimeError((count,a[:100]))
 s=s.replace(a,b,1)
rep("from datetime import datetime\n", "from datetime import datetime, timezone, timedelta\nimport hashlib\n")
rep('NAME=f"retrolume-task-083-d3-{TAG}"\n', '''NAME=f"retrolume-task-083-d3-{TAG}"
RUN_EVID=EVID/f"replacement-{TAG}"
RUN_EVID.mkdir(exist_ok=False)
''')
s=s.replace('(EVID/', '(RUN_EVID/')
rep('attempt=EVID/f"attempt-{number:02d}"','attempt=RUN_EVID/f"attempt-{number:02d}"')
rep('go=EVID/f"attempt-{number:02d}.go"','go=RUN_EVID/f"attempt-{number:02d}.go"')
rep('state={"tag":TAG,"name":NAME,"attempts":[],"container_id":None,"cleanup_incomplete":False}\n', '''state={"tag":TAG,"name":NAME,"attempts":[],"container_id":None,"cleanup_incomplete":False}
active_proc=None
active_created=None
runner_bytes=Path(__file__).read_bytes()
(RUN_EVID/"runner-as-run.py").write_bytes(runner_bytes)
(RUN_EVID/"runner-as-run.sha256").write_text(hashlib.sha256(runner_bytes).hexdigest()+"  runner_replacement.py\\n",encoding="utf-8")
''')
rep('def docker(args, timeout=30):\n    r=subprocess.run(["docker",*args],capture_output=True,text=True,timeout=min(timeout,max(1,left()-60)))\n    return r\n', '''def docker(args, timeout=30, *, cleanup=False):
    reserve=0 if cleanup else 60
    r=subprocess.run(["docker",*args],capture_output=True,text=True,
                     timeout=min(timeout,max(1,left()-reserve)))
    return r
''')
rep('def select_inspect(container):\n    r=docker(["inspect",container],30)', 'def select_inspect(container, *, cleanup=False):\n    r=docker(["inspect",container],30,cleanup=cleanup)')
rep('"port_bindings":hc["PortBindings"],"binds":hc["Binds"],"mounts":obj["Mounts"],', '"port_bindings":hc["PortBindings"],"binds":hc["Binds"],\n        "configured_mounts":hc.get("Mounts"),"mounts":obj["Mounts"],')
start=s.index("def owner_ok(obj):")
end=s.index("\ndef process_created",start)
s=s[:start]+'''def identity_ok(obj):
    labels=obj["labels"] or {}
    return (obj["id"]==cid and obj["name"]=="/"+NAME and obj["image"]==IMAGE
            and labels.get("retrolume-task")=="083"
            and labels.get("phase")=="d3-10" and labels.get("run")==TAG)

def config_ok(obj):
    binding=(obj["port_bindings"] or {}).get("5432/tcp") or []
    mounts=obj["mounts"] or []
    return (obj["nano_cpus"]==1000000000 and obj["memory"]==536870912
            and obj["pids_limit"]==128 and obj["restart"]=="no"
            and obj["network"]=="bridge" and obj["binds"] is None
            and obj["configured_mounts"] in (None,[])
            and len(mounts)==1 and mounts[0]["Type"]=="volume"
            and mounts[0]["Destination"]=="/var/lib/postgresql/data"
            and binding==[{"HostIp":"127.0.0.1","HostPort":str(PORT)}])
''' + s[end:]
rep('def batch(parts,number,dsn):\n    attempt=', 'def batch(parts,number,dsn):\n    global active_proc,active_created\n    attempt=')
rep('    created=process_created(proc._handle)\n    killed=False', '    active_proc=proc\n    created=process_created(proc._handle)\n    active_created=created\n    killed=False')
rep('    state["attempts"].append(meta);save()\n    ok=', '    state["attempts"].append(meta);save()\n    active_proc=None\n    active_created=None\n    ok=')
rep('    if r.returncode!=0 or r.stdout.strip()!=IMAGE: raise RuntimeError("fixed local image unavailable")\n', '''    if r.returncode!=0 or r.stdout.strip()!=IMAGE: raise RuntimeError("fixed local image unavailable")
    r=docker(["image","inspect",IMAGE,"--format","{{json .Config.Volumes}}"],30)
    image_volumes=json.loads(r.stdout) if r.returncode==0 else None
    state["precheck_image_volumes"]=image_volumes
    if image_volumes!={"/var/lib/postgresql/data":{}}:
        raise RuntimeError("image-declared anonymous PG volume differs")
''')
rep('    r=docker(["run","-d","--name",NAME,', '    run_started=datetime.now(timezone.utc)\n    r=docker(["run","-d","--name",NAME,')
rep('    if not owner_ok(obj) or not obj["running"]: raise RuntimeError("created resource identity/config mismatch")\n', '''    if not identity_ok(obj): raise RuntimeError("created container identity mismatch")
    if not config_ok(obj) or not obj["running"]:
        raise RuntimeError("created resource config mismatch")
    volume_name=obj["mounts"][0]["Name"]
    r=docker(["volume","inspect",volume_name],30)
    if r.returncode!=0: raise RuntimeError("anonymous volume inspect failed")
    volume=json.loads(r.stdout)[0]
    created_at=datetime.fromisoformat(volume["CreatedAt"].replace("Z","+00:00"))
    volume_ok=(volume["Name"]==volume_name and volume["Scope"]=="local"
               and volume["Mountpoint"]==obj["mounts"][0]["Source"]
               and run_started-timedelta(minutes=2)<=created_at<=datetime.now(timezone.utc)+timedelta(minutes=2))
    state["anonymous_volume"]={"name":volume_name,"created_at":str(created_at),
                               "new_this_run":volume_ok}
    save()
    if not volume_ok: raise RuntimeError("volume origin not confirmed new")
''')
rep('finally:\n    if cid is not None:\n', '''finally:
    if active_proc is not None and active_proc.poll() is None:
        try:
            if active_created is not None and process_created(active_proc._handle)==active_created:
                r=subprocess.run(["taskkill","/PID",str(active_proc.pid),"/T","/F"],
                                 capture_output=True,text=True,timeout=min(15,max(1,left()-30)))
                state["batch_final_kill"]={"pid":active_proc.pid,"created_100ns":active_created,
                                           "exit":r.returncode,"stdout":r.stdout,"stderr":r.stderr}
                active_proc.wait(timeout=min(10,max(1,left()-20)))
            else:
                # Exact Popen handle, but descendant ownership is unconfirmed.
                active_proc.kill()
                active_proc.wait(timeout=min(10,max(1,left()-20)))
                state["cleanup_incomplete"]=True
                state["batch_cleanup_error"]="creation time unavailable"
        except BaseException as exc:
            state["cleanup_incomplete"]=True
            state["batch_cleanup_error"]=f"{type(exc).__name__}: {exc}"
    if cid is not None:
''')
rep('            obj=select_inspect(cid)\n            if not owner_ok(obj): raise RuntimeError("cleanup owner mismatch")\n', '            obj=select_inspect(cid,cleanup=True)\n            if not identity_ok(obj): raise RuntimeError("cleanup owner mismatch")\n')
rep('            r=docker(["stop","--timeout","10",cid],20)', '            r=docker(["stop","--timeout","10",cid],20,cleanup=True)')
rep('                r=docker(["kill",cid],15)', '                r=docker(["kill",cid],15,cleanup=True)')
rep('            final=select_inspect(cid)\n', '            final=select_inspect(cid,cleanup=True)\n')
rep('            if not owner_ok(final) or final["running"]:', '            if not identity_ok(final) or final["running"]:')
dst.write_text(s,encoding="utf-8")
print("source_hash",hashlib.sha256(src.read_bytes()).hexdigest())
print("replacement_hash",hashlib.sha256(dst.read_bytes()).hexdigest())
