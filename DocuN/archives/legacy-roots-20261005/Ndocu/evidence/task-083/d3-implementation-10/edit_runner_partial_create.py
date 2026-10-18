from pathlib import Path
p=Path("Ndocu/evidence/task-083/d3-implementation-10/runner_replacement.py")
s=p.read_text(encoding="utf-8")
def rep(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError((s.count(a),a[:90]))
 s=s.replace(a,b,1)
rep('cid=None\nstate=', 'cid=None\nrun_attempted=False\nstate=')
rep('    r=docker(["run","-d","--name",NAME,', '    run_attempted=True\n    r=docker(["run","-d","--name",NAME,')
rep('finally:\n    if active_proc is not None', '''finally:
    if run_attempted and cid is None:
        # Docker may create the named container before reporting a run error.
        try:
            r=docker(["inspect",NAME],30,cleanup=True)
            if r.returncode==0:
                candidate=json.loads(r.stdout)[0]
                labels=candidate["Config"]["Labels"] or {}
                if (candidate["Name"]=="/"+NAME and candidate["Image"]==IMAGE
                    and labels.get("retrolume-task")=="083"
                    and labels.get("phase")=="d3-10" and labels.get("run")==TAG):
                    cid=candidate["Id"]
                    state["container_id"]=cid
                    log(f"partial run resource found id={cid}")
                else:
                    state["cleanup_incomplete"]=True
                    state["partial_run_owner"]="mismatch"
        except BaseException as exc:
            state["cleanup_incomplete"]=True
            state["partial_run_owner"]=f"{type(exc).__name__}: {exc}"
    if active_proc is not None''')
p.write_text(s,encoding="utf-8")
