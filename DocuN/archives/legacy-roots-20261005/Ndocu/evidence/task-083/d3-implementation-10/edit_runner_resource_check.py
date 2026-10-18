from pathlib import Path
p=Path("Ndocu/evidence/task-083/d3-implementation-10/runner.py")
s=p.read_text(encoding="utf-8")
a='            and obj["binds"] is None and obj["mounts"]==[]\n'
b='            and obj["binds"] is None\n            and len(obj["mounts"])==1\n            and obj["mounts"][0]["Type"]=="volume"\n            and obj["mounts"][0]["Destination"]=="/var/lib/postgresql/data"\n'
if s.count(a)!=1: raise RuntimeError(s.count(a))
s=s.replace(a,b,1).replace('["stop","--time","10",cid]','["stop","--timeout","10",cid]')
p.write_text(s,encoding="utf-8")
