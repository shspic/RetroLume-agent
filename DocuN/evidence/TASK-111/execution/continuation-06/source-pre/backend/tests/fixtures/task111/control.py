"""本卡唯一预算和动作原件，先计数后触发，失败不返额度。"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime,timezone
import hashlib
import json
import msvcrt
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[4]
EVIDENCE=ROOT/"DocuN/evidence/TASK-111/execution"
PERMIT="TASK-111-G11-P110-20261010"
CAPS={"real_batches":6,"image_builds":3,"preview_creates":14,"preview_starts":14,"PG_containers":1,"PG_volumes":1,
 "PG_container_starts":6,"API_listener_starts":4,"main_browser_starts":3,"model_synthetic_requests":6,
 "Windows_OneCall_sessions":8,"frontend_typecheck_build_batches":3,"offline_related_batches":6,"HTTP_total":5000,
 "public_PNG_gets_subset":3000,"public_inputs_subset":300,"internal_inputs":500,"preview_reaper_validation_batches":2}
CONTINUATION="TASK-111-G11-C01-20261010"
CONTINUE_ROOT=EVIDENCE/"continuation-01"
C02_ROOT=EVIDENCE/"continuation-02"
C03_ROOT=EVIDENCE/"continuation-03"
C04_ROOT=EVIDENCE/"continuation-04"
C05_ROOT=EVIDENCE/"continuation-05"
if (C05_ROOT/"timing.json").is_file():
    CONTINUATION="TASK-111-G11-C05-20261011";CONTINUE_ROOT=C05_ROOT
    _continuation=json.loads((CONTINUE_ROOT/"timing.json").read_text(encoding="utf-8"))
    if _continuation["permit"]!=CONTINUATION:raise RuntimeError("C05 identity")
    CAPS.update(_continuation["hard_count_caps"])
    CAPS["offline_related_batches"]=None;CAPS["preview_reaper_validation_batches"]=None
elif (C04_ROOT/"timing.json").is_file():
    CONTINUATION="TASK-111-G11-C04-20261011";CONTINUE_ROOT=C04_ROOT
    _continuation=json.loads((CONTINUE_ROOT/"timing.json").read_text(encoding="utf-8"))
    if _continuation["permit"]!=CONTINUATION:raise RuntimeError("C04 identity")
    CAPS.update(_continuation["hard_count_caps"])
    CAPS["offline_related_batches"]=None;CAPS["preview_reaper_validation_batches"]=None
elif (C03_ROOT/"timing.json").is_file():
    CONTINUATION="TASK-111-G11-C03-20261011";CONTINUE_ROOT=C03_ROOT
    _continuation=json.loads((CONTINUE_ROOT/"timing.json").read_text(encoding="utf-8"))
    if _continuation["permit"]!=CONTINUATION:raise RuntimeError("C03 identity")
    CAPS.update(_continuation["hard_count_caps"])
    CAPS["offline_related_batches"]=None;CAPS["preview_reaper_validation_batches"]=None
elif (C02_ROOT/"timing.json").is_file():
    CONTINUATION="TASK-111-G11-C02-20261010";CONTINUE_ROOT=C02_ROOT
    _continuation=json.loads((CONTINUE_ROOT/"timing.json").read_text(encoding="utf-8"))
    if _continuation["permit"]!=CONTINUATION:raise RuntimeError("C02 identity")
    CAPS.update(_continuation["hard_count_caps"]);CAPS["offline_related_batches"]=None
elif (CONTINUE_ROOT/"timing.json").is_file():
    _continuation=json.loads((CONTINUE_ROOT/"timing.json").read_text(encoding="utf-8"))
    if _continuation["permit"]!=CONTINUATION or _continuation["original_deadline_ns"]!=902913370092600:raise RuntimeError("continuation identity")
    CAPS.update({key:_continuation["caps_after"][key] for key in CAPS})


def atomic(path,value):
    temporary=path.with_suffix(path.suffix+".new")
    with temporary.open("w",encoding="utf-8") as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False);stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)


@contextmanager
def locked():
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    with (EVIDENCE/"budget.lock").open("a+b") as stream:
        stream.seek(0);stream.write(b"0");stream.flush();stream.seek(0)
        until=time.monotonic()+3
        while True:
            try:msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1);break
            except OSError:
                if time.monotonic()>until:raise RuntimeError("TASK111 budget owner busy")
                time.sleep(.02)
        try:yield
        finally:stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)


def read_state():
    path=EVIDENCE/"budget.json"
    if path.is_file():value=json.loads(path.read_text(encoding="utf-8"))
    else:
        initial=json.loads((EVIDENCE/"session-start.json").read_text(encoding="utf-8-sig"))
        deadline=int(initial["deadline_tick"]*1000000000//initial["host_monotonic_frequency"])
        value={"permit":PERMIT,"deadline_ns":deadline,"counts":{key:0 for key in CAPS},"time_seconds":{"offline":0,"real":0,"cleanup":0},"active_batch":None,"events":0}
    if value["permit"]!=PERMIT:raise RuntimeError("TASK111 ledger identity")
    return value


def state():
    value=read_state()
    if time.monotonic_ns()>=value.get("business_deadline_ns",value["deadline_ns"]):raise RuntimeError("TASK111 business window ended")
    active=value.get("active_batch")
    if active and active["kind"]!="cleanup" and time.monotonic_ns()>=active["deadline_ns"]:raise RuntimeError("TASK111 root deadline")
    return value


def phase(kind):
    """续作前向段不重叠记账；PG持有段另覆盖真实租约，不重复加总。"""
    if kind not in {"metadata","implementation_offline","real","cleanup","complete"}:raise RuntimeError("invalid continuation phase")
    path=CONTINUE_ROOT/"timing.json";value=json.loads(path.read_text(encoding="utf-8"));now=time.monotonic_ns()
    previous=value["phase"];elapsed=(now-value["phase_start_ns"])/1e9
    if previous in value["used_seconds"]:value["used_seconds"][previous]+=elapsed
    with (CONTINUE_ROOT/"phase-events.jsonl").open("a",encoding="utf-8") as stream:
        stream.write(json.dumps({"phase":previous,"start_ns":value["phase_start_ns"],"end_ns":now,"seconds":elapsed,"next":kind})+"\n")
    value["phase"]=kind;value["phase_start_ns"]=now;atomic(path,value)
    if CONTINUATION.endswith(("C02-20261010","C03-20261011","C04-20261011","C05-20261011")):
        if kind not in ("cleanup","complete") and now>=value["business_deadline_ns"]:raise RuntimeError("continuation business timing exhausted")
    elif now>=value["original_deadline_ns"] or any(value["used_seconds"][key]>limit for key,limit in value["caps_seconds"].items()):raise RuntimeError("continuation timing exhausted")
    return value


def _safe(value):
    if isinstance(value,dict):return {key:("[redacted]" if key.lower() in {"password","dsn","api_key","control_key","owner_key","input_owner_key","session_token"} else _safe(item)) for key,item in value.items()}
    if isinstance(value,(tuple,list)):return [_safe(item) for item in value]
    return value


def event(kind,value,*,cleanup=False):
    with locked():
        budget=read_state() if cleanup else state();budget["events"]+=1
        row={"event":budget["events"],"kind":kind,"pid":os.getpid(),"at_ns":time.monotonic_ns(),"at_utc":datetime.now(timezone.utc).isoformat(),"data":_safe(value)}
        with (EVIDENCE/"events.jsonl").open("a",encoding="utf-8") as stream:stream.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+"\n")
        atomic(EVIDENCE/"budget.json",budget)


def reserve(kind,value=None):
    with locked():
        budget=state()
        if kind not in CAPS or (CAPS[kind] is not None and budget["counts"][kind]>=CAPS[kind]):raise RuntimeError("TASK111 count cap reached: "+kind)
        budget["counts"][kind]+=1;number=budget["counts"][kind];atomic(EVIDENCE/"budget.json",budget)
    event("reserved",{"category":kind,"number":number,"detail":value or {}});return number


def preview_name(preview_id,generation):
    """累计create计数与本卡唯一新名字分别记账，禁止回落到旧名字。"""
    number=reserve("preview_creates",{"preview_id":preview_id})
    plan=CONTINUE_ROOT/"preview-name-plan.json"
    with locked():
        if not plan.exists():raise RuntimeError("fixed preview name allocation missing")
        names=json.loads(plan.read_text(encoding="utf-8"))
        allowed=range(40,54) if CONTINUATION.endswith("C05-20261011") else range(26,45) if CONTINUATION.endswith("C04-20261011") else range(15,45) if CONTINUATION.endswith("C03-20261011") else range(2,15)
        if not names or names[0] not in [str(n).zfill(2) for n in allowed]:raise RuntimeError("fixed preview name allocation")
        chosen=names.pop(0);atomic(plan,names)
    result="retrolume-task-111-g11-preview-"+chosen
    event("preview_name_allocation",{"counter":number,"name":result,"preview_id":preview_id,"generation":generation})
    return result


def synthetic_root():
    return CONTINUE_ROOT/"synthetic" if CONTINUATION.endswith(("C03-20261011","C04-20261011","C05-20261011")) else EVIDENCE/"synthetic"


def registry_root():
    return C04_ROOT/"synthetic/control" if CONTINUATION.endswith("C05-20261011") else synthetic_root()/"control" if CONTINUATION.endswith("C04-20261011") else synthetic_root()/"http-control"


@contextmanager
def batch(kind,name,maximum=3600):
    limits={"real":14400,"offline":7200,"cleanup":1800}
    if kind not in limits:raise RuntimeError("TASK111 unknown batch category")
    if kind=="cleanup":
        # 清场独立预留，不能继承已经到期的真实验证批，也不恢复真实批计数。
        number=None
    else:
        category="real_batches" if kind=="real" else "offline_related_batches"
        number=reserve(category,{"name":name})
    start=time.monotonic_ns()
    with locked():
        budget=read_state() if kind=="cleanup" else state()
        if budget["active_batch"] is not None:raise RuntimeError("TASK111 overlapping root batch")
        remaining=float("inf") if kind=="offline" and CONTINUATION.endswith(("C02-20261010","C03-20261011","C04-20261011","C05-20261011")) else limits[kind]-budget["time_seconds"][kind]
        if kind=="real" and CONTINUATION.endswith(("C03-20261011","C04-20261011","C05-20261011")):
            remaining=min(remaining,_continuation["new_real_limit_seconds"]-(budget["time_seconds"]["real"]-_continuation["prior_time_seconds"]["real"]))
        if remaining<=0:raise RuntimeError("TASK111 category time exhausted: "+kind)
        per_root=1800 if kind=="cleanup" or (kind=="real" and CONTINUATION.endswith(("C03-20261011","C04-20261011"))) else 3500 if (CONTINUE_ROOT/"timing.json").is_file() and kind=="real" else float("inf") if kind=="offline" and CONTINUATION.endswith(("C03-20261011","C04-20261011")) else 3600
        if CONTINUATION.endswith("C05-20261011"):
            if kind=="real":per_root=1500
            elif kind=="offline":per_root=float("inf")
        maximum=min(maximum,remaining,per_root)
        limit_deadline=start+int(maximum*1000000000)
        if kind!="cleanup":limit_deadline=min(limit_deadline,budget.get("business_deadline_ns",budget["deadline_ns"]))
        budget["active_batch"]={"kind":kind,"number":number,"name":name,"start_ns":start,"deadline_ns":limit_deadline}
        atomic(EVIDENCE/"budget.json",budget)
    try:yield budget["active_batch"]
    finally:
        elapsed=(time.monotonic_ns()-start)/1e9
        with locked():
            budget=read_state();budget["time_seconds"][kind]+=elapsed;budget["active_batch"]=None;atomic(EVIDENCE/"budget.json",budget)
        event("batch_end",{"kind":kind,"number":number,"name":name,"elapsed":elapsed,"exceeded":elapsed>maximum},cleanup=True)


def run(args,folder,*,cwd=None,env=None,maximum=60,name="command"):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    budget=read_state();active=budget["active_batch"]
    if active is None:raise RuntimeError("TASK111 command outside budget batch")
    if active["kind"]!="cleanup":state()
    timeout=min(maximum,(active["deadline_ns"]-time.monotonic_ns())/1e9)
    if timeout<=0:raise RuntimeError("TASK111 batch deadline")
    started=time.monotonic_ns()
    value=subprocess.run(args,cwd=cwd,env=env,timeout=timeout,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (folder/(name+".stdout.bin")).write_bytes(value.stdout);(folder/(name+".stderr.bin")).write_bytes(value.stderr)
    atomic(folder/(name+".json"),{"args":args,"cwd":str(cwd) if cwd else None,"code":value.returncode,"start_ns":started,"end_ns":time.monotonic_ns(),
      "stdout_bytes":len(value.stdout),"stdout_sha256":hashlib.sha256(value.stdout).hexdigest(),"stderr_bytes":len(value.stderr)})
    if value.returncode:raise RuntimeError("TASK111 command failed: "+name)
    return value


def source_snapshot(folder):
    files=[]
    paths=list((ROOT/"backend/app/preview").glob("*.py"))+list((ROOT/"deploy/preview").glob("runtime.*"))+[
      ROOT/"deploy/preview/renderer-host.cjs",ROOT/"deploy/preview/renderer-bootstrap.cjs",ROOT/"deploy/preview/renderer-assembly.cjs",ROOT/"deploy/preview/renderer-protocol.cjs",ROOT/"deploy/preview/descriptor.schema.json",
      ROOT/"backend/migrations/012_html_explanations.sql",ROOT/"backend/app/preview/schema-fingerprint.json",ROOT/"backend/app/activities/repository.py",ROOT/"backend/app/capabilities/contracts.py",ROOT/"backend/app/capabilities/gateway.py"]
    paths+=list((ROOT/"frontend/src/explanations").glob("*"))
    paths+=[ROOT/"backend/tests/fixtures/task111"/name for name in (
      "control.py","resources.py","core.py","runtime.py","c01_seeds.py","c01_guardian.py","server.py","http_matrix.py",
      "c02_coordinator.py","c02_step.py","c02_normal.py","c02_pg.py","c02_lineage_check.py","c02_faults.py")]
    paths+=[ROOT/"frontend/tests/task111/browser.cjs",ROOT/"deploy/preview/build_renderer.py",ROOT/"deploy/preview/Dockerfile.production",
      ROOT/"deploy/preview/resolve_license_materials.py",ROOT/"deploy/preview/license_resources.cjs"]
    paths+=list((ROOT/"backend/tests/fixtures/task111").glob("c03*.py"))+list((ROOT/"frontend/tests/task111").glob("c03*.cjs"))
    paths+=list((ROOT/"backend/tests/fixtures/task111").glob("c03*.cjs"))
    paths+=list((ROOT/"backend/tests/fixtures/task111").glob("c04*.py"))+list((ROOT/"frontend/tests/task111").glob("c04*.cjs"))
    paths+=list((ROOT/"backend/tests/fixtures/task111").glob("c05*.py"))+list((ROOT/"frontend/tests/task111").glob("c05*.cjs"))
    for path in paths:
        if path.is_file():files.append({"path":str(path.relative_to(ROOT)).replace("\\","/"),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size})
    atomic(Path(folder)/"source-identity.json",files);return files
