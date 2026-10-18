"""容器外生产控制链：单会话、固定截止、独立救援与持久预算。"""
from __future__ import annotations
import asyncio
from datetime import datetime,timedelta,timezone
import hashlib
import json
import math
import os
import re
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
from collections import deque
from uuid import uuid4
from .business_contracts import HtmlRefusal
from .compiler import runtime_identity
from .description import canonical,digest,control_value
from .docker_control import call,clean_env,creation_args,find_intent,inspect_owned,stop_owned,local_create_rejection,DockerUnknown
from .host_policy import policy_config_sha256
from .pipe import send_packet,read_packet
from .process import atomic_json,birth,GlobalOwner,OwnershipUnknown,protect_control_key,unprotect_control_key,terminate_owned

BACKEND=Path(__file__).resolve().parents[2]
PREVIEW_ROOT=BACKEND.parent/"deploy"/"preview"


class PreviewController:
    def __init__(self,ledger,policy,*,name_supplier=None,event_sink=None):
        self.ledger,self.policy=ledger,policy;self.boot_id=str(uuid4());self.current=None;self.blocked=False
        self.config_sha256=policy_config_sha256(policy);self.available=True
        self._name_supplier=name_supplier;self._event_sink=event_sink;self._lock=threading.RLock();self._writer=threading.Lock()
        self._open_lock=asyncio.Lock()
        self._owner=GlobalOwner(policy.owner_name)
        acquired=self._owner.acquire()
        if acquired=="busy":self.available=False;self.blocked=True
        self.root=policy.registry_dir;self.root.mkdir(parents=True,exist_ok=True)
        self.current_file=self.root/"current.json"
        if acquired=="abandoned" or self.current_file.exists():
            # 重启必须先救援和核对，不靠旧monotonic时间或租约直接抢占。
            self.blocked=True
        self._closed=False

    async def recover(self):
        if not self.available or not self._owner.held:return
        if not self.current_file.exists():return
        try:
            pointer=json.loads(self.current_file.read_text(encoding="utf-8"));folder=Path(pointer["folder"]).resolve()
            if folder.parent!=self.root.resolve():raise OwnershipUnknown("recovery_path")
            registry=json.loads((folder/"registry.json").read_text(encoding="utf-8"));intent=registry["intent"]
            if intent["labels"].get("retrolume.domain")!="preview.v2" or registry["preview_id"]!=pointer["preview_id"]:raise OwnershipUnknown("recovery_identity")
            old_parent=birth(registry["parent"]["pid"])
            if old_parent["state"]=="unknown" or (old_parent["state"]=="running" and old_parent["birth"]==registry["parent"]["birth"]):
                raise OwnershipUnknown("recovery_parent_not_ended")
            cid=registry.get("cid") or find_intent(self.policy.docker,intent)
            facts=json.loads((folder/"kernel-premises.json").read_text(encoding="utf-8")) if (folder/"kernel-premises.json").is_file() else None
            state=None;created=None
            if cid is None:
                created=json.loads((folder/"create.json").read_text(encoding="utf-8"))
                if (registry.get("start_requested_ns") or registry.get("attach_pid") or not local_create_rejection(created,intent,PREVIEW_ROOT/"seccomp.json")
                    or created["start_ns"]<registry["create_requested_ns"] or created["end_ns"]>registry["deadline_ns"]
                    or find_intent(self.policy.docker,intent) is not None):
                    raise OwnershipUnknown("recovery_create_unknown")
            else:
                state=inspect_owned(self.policy.docker,cid,intent)
                if state["state"]["Running"] and call(self.policy.docker,["kill",cid])["code"]:
                    raise OwnershipUnknown("recovery_kill_unconfirmed")
            attach_ended=True
            if registry.get("attach_pid"):
                attach_ended=terminate_owned(registry["attach_pid"],registry["attach_birth"])
            ready_file=folder/"reaper-ready.json"
            if ready_file.is_file():
                reaper=json.loads(ready_file.read_text(encoding="utf-8"));terminate_owned(reaper["pid"],reaper["birth"])
            else:raise OwnershipUnknown("recovery_reaper_identity_missing")
            if cid is None:
                proof={"tree_confirmation":"never_started","cid":None,"image_id":intent["image_id"],"nonce":intent["nonce"],
                    "name":intent["name"],"recovery":True,"cause":"exact_cli_pid_parse_rejection","create_receipt_sha256":digest(created),
                    "lookup":"exact_name_and_nonce_absent","parent_lifetime_ended":True,"owned_reaper_ended":True,"attach_never_started":True}
            else:
                proof=stop_owned(self.policy.docker,cid,intent,facts,attach_ended=attach_ended)
                if state["state"]["Status"]=="created" and not state["state"]["Running"] and state["state"]["Pid"]==0 and not registry.get("start_requested_ns"):
                    proof={"tree_confirmation":"never_started","cid":cid,"inspect":state,"recovery":True}
                proof["owned_reaper_ended"]=True;proof["parent_lifetime_ended"]=True
            if proof["tree_confirmation"] not in ("private_pid_init_terminated","never_started"):raise OwnershipUnknown("recovery_tree_unknown")
            row=await self.ledger.read_html_preview(registry["activity_id"],registry["preview_id"])
            if row["state"] not in ("stopped","failed_unstarted"):
                key=unprotect_control_key(registry["control_key_blob"])
                if row["state"]!="cleanup_unconfirmed":
                    await self.ledger.update_html_preview(registry["preview_id"],key,"cleanup_unconfirmed",first_receipt={"tree_confirmation":"unconfirmed","reason":"restart_recovery"})
                await self.ledger.update_html_preview(registry["preview_id"],key,"failed_unstarted" if proof["tree_confirmation"]=="never_started" else "stopped",
                    confirmation=proof,elapsed=row["reserve_seconds"])
            registry["complete"]=True;atomic_json(folder/"registry.json",registry);atomic_json(folder/"recovery-proof.json",proof)
            atomic_json(self.current_file,{"folder":str(folder),"preview_id":registry["preview_id"],"complete":True});self.blocked=False
        except Exception:self.blocked=True

    def _event(self,kind,value):
        if self._event_sink:self._event_sink(kind,value)

    def has_unconfirmed(self,aid=None):return self.blocked

    def _db(self,awaitable):
        from app.runtime import psycopg_compatible_loop_factory
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(awaitable)

    async def open(self,aid,artifact_id,command):
        async with self._open_lock:
            return await self._open_serial(aid,artifact_id,command)

    async def _open_serial(self,aid,artifact_id,command):
        if not self.available or self.blocked:raise HtmlRefusal("cleanup_unconfirmed",status=503)
        artifact=await self.ledger.read_html_artifact(aid,artifact_id)
        if artifact["artifact_sha256"]!=command.expected_artifact_sha256:raise HtmlRefusal("html_integrity_error")
        with self._lock:
            if self.current is not None:
                if self.current["aid"]==aid and self.current["start_key"]==command.start_key:
                    preview_id=self.current["preview_id"]
                else:raise HtmlRefusal("html_preview_busy")
            else:preview_id=None
        if preview_id:
            row=await self.ledger.read_html_preview(aid,preview_id)
            expected=hashlib.sha256(bytes.fromhex(command.input_owner_key)).hexdigest()
            if row["owner_key_sha256"]!=expected or row["artifact_id"]!=artifact_id or row["artifact_sha256"]!=command.expected_artifact_sha256:
                raise HtmlRefusal("html_start_key_conflict")
            return await self.status(aid,preview_id,command.input_owner_key)
        budget=await self.ledger.html_preview_budget(aid)
        reserve=min(60,180-budget["settled_seconds"]-budget["reserved_seconds"])
        if reserve<30 or budget["starts_used"]>=3:raise HtmlRefusal("html_preview_budget_exhausted")
        now=time.monotonic_ns();pid=str(uuid4());control_key=secrets.token_hex(32)
        identity={"preview_id":pid,"owner_id":str(uuid4()),"boot_id":self.boot_id,"nonce":secrets.token_hex(32),
          "control_key":control_key,"image_id":self.policy.image_id,"config_sha256":self.config_sha256,"t0_ns":now,
          "deadline_at":datetime.now(timezone.utc)+timedelta(seconds=reserve)}
        row,created=await self.ledger.reserve_html_preview(aid,artifact_id,command,identity,reserve)
        if not created:return await self.status(aid,row["preview_id"])
        name=self._name_supplier(pid,row["generation"]) if self._name_supplier else "retrolume-preview-v2-"+pid.replace("-","")
        parent=birth(os.getpid())
        if parent["state"]!="running":raise OwnershipUnknown("parent_birth_unknown")
        folder=self.root/pid;folder.mkdir(mode=0o700)
        current={"aid":aid,"preview_id":pid,"artifact_id":artifact_id,"artifact_sha256":artifact["artifact_sha256"],
           "generation":row["generation"],"owner_id":row["owner_id"],"start_key":command.start_key,
           "control_key":control_key,"channel_nonce":identity["nonce"],"nonce":identity["nonce"],"t0_ns":now,
           "deadline_ns":now+reserve*1000000000,"reserve_seconds":reserve,"description":artifact["description"],
           "folder":folder,"stop":threading.Event(),"ready":threading.Event(),"ack":threading.Event(),"frame":None,
           "frame_seq":0,"input_seq":0,"last_ack":None,"last_payload_sha256":None,"state":"reserved","cid":None,
           "identity":identity,"name":name,"attach":None,"reader":None,"stderr_reader":None,"reaper":None,
           "kernel_ready":None,"received_ready":None,"pipe_eof":False,"error_code":None,"last_contact_ns":now}
        current["input_times"]=deque();current["rate_exceeded_since"]=None
        current["intent"]={"name":name,"image_id":self.policy.image_id,"nonce":identity["nonce"],"docker":self.policy.docker,
          "kernel_release":self.policy.kernel_release,"created_unix":str(int(time.time())-1),
          "seccomp_sha256":digest(json.loads((PREVIEW_ROOT/"seccomp.json").read_text(encoding="utf-8"))),
          "labels":{"retrolume.domain":"preview.v2","retrolume.boot":self.boot_id,"retrolume.preview":pid,
                    "retrolume.nonce":identity["nonce"],"retrolume.authorization":self.policy.authorization}}
        registry={"deadline_ns":current["deadline_ns"],"parent":{"pid":os.getpid(),"birth":parent["birth"]},
                  "intent":current["intent"],"cid":None,"complete":False,"control_key_blob":protect_control_key(control_key),
                  "activity_id":aid,"preview_id":pid,"generation":row["generation"],"attach_pid":None,"attach_birth":None}
        current["registry"]=registry;atomic_json(folder/"registry.json",registry);atomic_json(self.current_file,{"folder":str(folder),"preview_id":pid})
        with self._lock:
            if self.current is not None:raise OwnershipUnknown("physical_owner_conflict")
            self.current=current
        thread=threading.Thread(target=self._run,args=(current,),name="preview-supervisor-"+pid,daemon=False)
        current["thread"]=thread;thread.start()
        return await self.status(aid,pid,command.input_owner_key)

    def _registry(self,c):atomic_json(c["folder"]/"registry.json",c["registry"])

    def _transition(self,c,state,**fields):
        self._db(self.ledger.update_html_preview(c["preview_id"],c["control_key"],state,**fields));c["state"]=state
        self._event("state",{"preview_id":c["preview_id"],"state":state,"at_ns":time.monotonic_ns()})

    def _read(self,c):
        try:
            while True:
                head,body=read_packet(c["attach"].stdout,c)
                kind=head["type"]
                if kind=="ready":
                    if head["seq"]!=0 or c["received_ready"] is not None or body.get("load_manifest_sha256")!=self.policy.load_manifest_sha256 or body.get("renderer_sha256")!=self.policy.renderer_sha256:
                        raise ValueError("ready_identity")
                    c["received_ready"]=body;c["kernel_ready"]=body;atomic_json(c["folder"]/"ready.json",body);atomic_json(c["folder"]/"ready-packet.json",{"header":head,"body":body});atomic_json(c["folder"]/"kernel-premises.json",body);c["ready"].set()
                elif kind=="frame":
                    if head["seq"]<=c["frame_seq"]:raise ValueError("frame_order")
                    c["frame_seq"]=head["seq"];c["frame"]=(head,body)
                elif kind=="input_ack":
                    if head["seq"]!=c["input_seq"]:raise ValueError("ack_order")
                    c["last_ack"]=body;c["ack"].set();self._event("ack",{"preview_id":c["preview_id"],"seq":head["seq"],"body":body})
                else:
                    if body.get("reason_code")=="bootstrap_identity":
                        c["kernel_ready"]=body;atomic_json(c["folder"]/"kernel-premises.json",body)
                    elif body.get("state")=="stopping":c["error_code"]=body.get("reason_code");c["stop"].set()
                self._event("packet",{"preview_id":c["preview_id"],"type":kind,"seq":head["seq"],"body_bytes":head["body_bytes"],"body_sha256":head["body_sha256"]})
        except EOFError:c["pipe_eof"]=True;c["stop"].set()
        except Exception:c["error_code"]="protocol_unconfirmed";c["stop"].set()

    def _stderr(self,c):
        data=bytearray()
        while True:
            chunk=c["attach"].stderr.read(1024)
            if not chunk:break
            if len(data)+len(chunk)>8192:c["error_code"]="stderr_limit";c["stop"].set();break
            data.extend(chunk)
        (c["folder"]/"container-stderr.bin").write_bytes(data)

    def _run(self,c):
        proof=None;started=False;registry=c["folder"]/"registry.json"
        try:
            reaper=subprocess.Popen([str(BACKEND/".venv"/"Scripts"/"python.exe"),"-B","-m","app.preview.production_reaper",str(registry)],
                cwd=BACKEND,env=clean_env(),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
            c["reaper"]=reaper
            while not (c["folder"]/"reaper-ready.json").exists():
                if reaper.poll() is not None or time.monotonic_ns()>c["t0_ns"]+1000000000:raise OwnershipUnknown("reaper_not_ready")
                time.sleep(.02)
            c["registry"]["create_requested_ns"]=time.monotonic_ns();self._registry(c)
            existing=find_intent(self.policy.docker,c["intent"])
            if existing is not None:raise OwnershipUnknown("name_conflict")
            self._event("create_attempt",{"name":c["name"],"preview_id":c["preview_id"]})
            try:
                result=call(self.policy.docker,creation_args(c["intent"],PREVIEW_ROOT/"seccomp.json"),timeout=2)
                atomic_json(c["folder"]/"create.json",result)
                if result["code"]:raise DockerUnknown("create_failed")
                cid=result["stdout"].strip();inspect_owned(self.policy.docker,cid,c["intent"])
            except DockerUnknown:
                cid=find_intent(self.policy.docker,c["intent"])
                if cid is None:raise
            c["cid"]=cid;c["registry"]["cid"]=cid;self._registry(c);self._transition(c,"registered",cid=cid)
            while not (c["folder"]/"reaper-bound.json").exists():
                if reaper.poll() is not None or time.monotonic_ns()>c["t0_ns"]+3000000000:raise OwnershipUnknown("reaper_bind_unconfirmed")
                time.sleep(.02)
            bound=json.loads((c["folder"]/"reaper-bound.json").read_text(encoding="utf-8"))
            if bound["cid"]!=cid or bound["deadline_ns"]!=c["deadline_ns"]:raise OwnershipUnknown("reaper_bind_identity")
            self._transition(c,"start_requested");c["registry"]["start_requested_ns"]=time.monotonic_ns();self._registry(c)
            self._event("start_attempt",{"preview_id":c["preview_id"],"cid":cid})
            attach=subprocess.Popen([self.policy.docker,"start","-a","-i",cid],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                env=clean_env(),creationflags=subprocess.CREATE_NO_WINDOW)
            c["attach"]=attach;started=True
            born=birth(attach.pid)
            if born["state"]!="running":raise OwnershipUnknown("attach_birth_unconfirmed")
            c["registry"]["attach_pid"]=attach.pid;c["registry"]["attach_birth"]=born["birth"];self._registry(c)
            c["reader"]=threading.Thread(target=self._read,args=(c,),daemon=False);c["reader"].start()
            c["stderr_reader"]=threading.Thread(target=self._stderr,args=(c,),daemon=False);c["stderr_reader"].start()
            with self._writer:send_packet(attach.stdin,c,"init",0,{"schema":"retrolume.preview.init.v2","description":c["description"],
              "description_sha256":digest(c["description"]),"renderer_sha256":self.policy.renderer_sha256,"viewport":{"width":640,"height":480}})
            ready_deadline=min(c["t0_ns"]+8000000000,c["deadline_ns"]-10000000000)
            while not c["ready"].wait(.02):
                if c["stop"].is_set() or time.monotonic_ns()>=ready_deadline:raise OwnershipUnknown("ready_unconfirmed")
            self._transition(c,"ready")
            while not c["stop"].wait(.05):
                now=time.monotonic_ns()
                if now>=c["deadline_ns"]-10000000000 or now-c["last_contact_ns"]>2000000000:
                    c["error_code"]="deadline" if now>=c["deadline_ns"]-10000000000 else "control_lost";break
                if reaper.poll() is not None:c["error_code"]="reaper_lost";break
                row=self._db(self.ledger.read_html_preview(c["aid"],c["preview_id"]))
                if not row["eligible"]:c["error_code"]="source_invalid";break
        except Exception:
            c["error_code"]=c["error_code"] or "supervision_unconfirmed"
        finally:
            c["stop"].set();diagnostic=c["deadline_ns"]+15000000000
            try:
                if started:
                    try:self._transition(c,"stopping")
                    except Exception:pass
                    if c["attach"] and c["attach"].poll() is None:
                        try:
                            with self._writer:send_packet(c["attach"].stdin,c,"stop",0,{"reason":"stop"})
                            c["attach"].wait(timeout=2)
                        except (OSError,ValueError,subprocess.TimeoutExpired):pass
                    if c["cid"]:
                        initial=stop_owned(self.policy.docker,c["cid"],c["intent"],c["kernel_ready"],attach_ended=False,diagnostic_deadline_ns=diagnostic)
                        if c["attach"]:
                            try:c["attach"].wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                c["attach"].kill();c["attach"].wait(timeout=2)
                        if c["reader"]:c["reader"].join(timeout=2)
                        if c["stderr_reader"]:c["stderr_reader"].join(timeout=2)
                        proof=stop_owned(self.policy.docker,c["cid"],c["intent"],c["kernel_ready"],
                            attach_ended=c["pipe_eof"] and c["attach"].poll() is not None and not c["reader"].is_alive() and not c["stderr_reader"].is_alive(),
                            diagnostic_deadline_ns=diagnostic)
                        proof["first_stop_observation"]=initial
                elif c["cid"]:
                    state=inspect_owned(self.policy.docker,c["cid"],c["intent"])
                    if state["state"]["Status"]=="created" and not state["state"]["Running"] and state["state"]["Pid"]==0:
                        proof={"tree_confirmation":"never_started","cid":c["cid"],"image_id":self.policy.image_id,"nonce":c["nonce"],"inspect":state,"end_ns":time.monotonic_ns()}
            except Exception:proof=None
            if proof is not None and proof["tree_confirmation"] in ("private_pid_init_terminated","never_started"):
                try:
                    # 已确认工作对象结束后，结束拥有的救援进程，再允许结算。
                    if c["reaper"] and c["reaper"].poll() is None:
                        c["reaper"].terminate();c["reaper"].wait(timeout=2)
                    proof["owned_reaper_ended"]=c["reaper"] is not None and c["reaper"].poll() is not None
                    if not proof["owned_reaper_ended"]:proof["tree_confirmation"]="unconfirmed"
                except (OSError,subprocess.TimeoutExpired):proof["tree_confirmation"]="unconfirmed"
            confirmed=proof is not None and proof["tree_confirmation"] in ("private_pid_init_terminated","never_started") and time.monotonic_ns()<=c["deadline_ns"]
            if confirmed:
                elapsed=min(c["reserve_seconds"],math.ceil((time.monotonic_ns()-c["t0_ns"])/1e9))
                try:
                    self._transition(c,"stopped" if started else "failed_unstarted",first_receipt=proof,confirmation=proof,elapsed=elapsed)
                except Exception:confirmed=False
            if not confirmed:
                self.blocked=True
                try:self._transition(c,"cleanup_unconfirmed",first_receipt=proof or {"tree_confirmation":"unconfirmed","error_code":c["error_code"]})
                except Exception:pass
            c["registry"]["complete"]=confirmed;self._registry(c)
            if c["reaper"]:
                try:c["reaper"].wait(timeout=2)
                except subprocess.TimeoutExpired:c["reaper"].terminate();c["reaper"].wait(timeout=2)
            atomic_json(c["folder"]/"supervisor-result.json",{"preview_id":c["preview_id"],"state":c["state"],"confirmed":confirmed,
                         "error_code":c["error_code"],"proof":proof,"at_ns":time.monotonic_ns()})
            self._event("finished",{"preview_id":c["preview_id"],"state":c["state"],"confirmed":confirmed,"error_code":c["error_code"]})
            if confirmed:
                atomic_json(self.current_file,{"folder":str(c["folder"]),"preview_id":c["preview_id"],"complete":True})
                with self._lock:
                    if self.current is c:self.current=None

    async def status(self,aid,pid,owner_key=None):
        row=await self.ledger.read_html_preview(aid,pid)
        c=self.current
        if c and c["aid"]==aid and c["preview_id"]==pid and row["generation"]==c["generation"] and type(owner_key) is str and re.fullmatch(r"[0-9a-f]{64}",owner_key):
            try:owner_hash=hashlib.sha256(bytes.fromhex(owner_key)).hexdigest()
            except (TypeError,ValueError):owner_hash=None
            if owner_hash is not None and secrets.compare_digest(owner_hash,row["owner_key_sha256"]):
                c["last_contact_ns"]=time.monotonic_ns()
        # 无owner的刷新仍能只读核对，但不能续活已失联控制者。
        row.pop("owner_key_sha256",None)
        return row

    async def _owner_row(self,aid,pid,generation,owner_key):
        row=await self.ledger.read_html_preview(aid,pid)
        if type(owner_key) is not str or not re.fullmatch(r"[0-9a-f]{64}",owner_key):raise HtmlRefusal("html_input_owner_invalid",status=403)
        try:owner_hash=hashlib.sha256(bytes.fromhex(owner_key)).hexdigest()
        except (ValueError,TypeError):raise HtmlRefusal("html_input_owner_invalid",status=403) from None
        if not secrets.compare_digest(owner_hash,row["owner_key_sha256"]) or row["generation"]!=generation:raise HtmlRefusal("html_input_owner_invalid",status=403)
        if not row["eligible"] or row["state"] not in ("ready","running"):raise HtmlRefusal("source_invalid")
        c=self.current
        if c is None or c["preview_id"]!=pid or c["generation"]!=generation:raise HtmlRefusal("cleanup_unconfirmed")
        c["last_contact_ns"]=time.monotonic_ns();return c

    async def input(self,aid,pid,command,owner_key):
        c=await self._owner_row(aid,pid,command.preview_generation,owner_key)
        event=command.event.model_dump();event_hash=digest(event)
        if event_hash!=command.payload_sha256:raise HtmlRefusal("html_input_hash")
        if event["type"]=="set_number":
            control=next((x for x in c["description"]["inputs"] if x["id"]==event["control_id"]),None)
            if control is None:raise HtmlRefusal("invalid_input",status=422)
            control_value(control,event["value"])
        elif not any(action["id"]==event["action_id"] for action in c["description"]["actions"]):
            raise HtmlRefusal("invalid_input",status=422)
        if command.seq==c["input_seq"]:
            if event_hash!=c["last_payload_sha256"]:raise HtmlRefusal("html_input_seq_conflict")
            return {"seq":command.seq,"preview_id":pid,"generation":c["generation"],"artifact_sha256":c["artifact_sha256"],**c["last_ack"]} if c["ack"].is_set() else {"state":"unconfirmed","seq":command.seq}
        now=time.monotonic_ns()
        while c["input_times"] and now-c["input_times"][0]>=1000000000:c["input_times"].popleft()
        if len(c["input_times"])>=20:
            c["rate_exceeded_since"]=c["rate_exceeded_since"] or now
            if now-c["rate_exceeded_since"]>=1000000000:c["stop"].set()
            raise HtmlRefusal("html_input_rate",status=429)
        c["rate_exceeded_since"]=None;c["input_times"].append(now)
        if command.seq!=c["input_seq"]+1 or time.monotonic_ns()>=c["deadline_ns"]-10000000000:raise HtmlRefusal("html_input_window_closed")
        if c["input_seq"] and not c["ack"].is_set():raise HtmlRefusal("html_input_pending")
        c["input_seq"]=command.seq;c["last_payload_sha256"]=event_hash;c["ack"].clear()
        try:
            with self._writer:send_packet(c["attach"].stdin,c,"input",command.seq,event)
            accepted=await asyncio.to_thread(c["ack"].wait,2)
            if not accepted:c["stop"].set();raise HtmlRefusal("html_input_unconfirmed")
            if c["state"]=="ready" and c["last_ack"].get("accepted") is True:
                await self.ledger.update_html_preview(pid,c["control_key"],"running");c["state"]="running"
            return {"seq":command.seq,"preview_id":pid,"generation":c["generation"],"artifact_sha256":c["artifact_sha256"],**c["last_ack"]}
        except (OSError,ValueError):c["stop"].set();raise HtmlRefusal("html_input_unconfirmed") from None

    async def frame(self,aid,pid,generation,after_seq,owner_key):
        c=self.current
        if c is None or c["preview_id"]!=pid:return None
        candidate=c["frame"]
        # 资格线性化点在候选已进入缓存之后，公开序列化之前。
        await self._owner_row(aid,pid,generation,owner_key)
        if candidate is None or candidate[0]["seq"]<=after_seq:return None
        return candidate

    async def stop(self,aid,pid,generation):
        row=await self.ledger.read_html_preview(aid,pid)
        if row["generation"]!=generation:raise HtmlRefusal("html_generation_conflict")
        c=self.current
        if c and c["preview_id"]==pid:c["stop"].set()
        return await self.status(aid,pid)

    async def close(self):
        if self._closed:return
        self._closed=True;self.available=False
        c=self.current
        if c:
            c["stop"].set();await asyncio.to_thread(c["thread"].join,15)
            if c["thread"].is_alive():self.blocked=True
        self._owner.close()
