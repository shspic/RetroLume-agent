"""固定截止的生产救援进程；只停止预登记的精确自有对象。"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import time
from .process import atomic_json,birth
from .docker_control import find_intent,inspect_owned,stop_owned,DockerUnknown
from .host_job import HostJob,scope,job_name


def main():
    if len(sys.argv)!=2:return 2
    path=Path(sys.argv[1]).resolve();value=json.loads(path.read_text(encoding="utf-8"))
    with HostJob(job_name(value["preview_id"],value["intent"]["nonce"],"REAP")) as job:
        with scope(job):return run(job)


def run(job):
    if len(sys.argv)!=2:return 2
    registry=Path(sys.argv[1]).resolve();initial=json.loads(registry.read_text(encoding="utf-8"))
    deadline=initial["deadline_ns"];parent=initial["parent"];fixed=initial["intent"]
    ready=registry.with_name("reaper-ready.json");bound=registry.with_name("reaper-bound.json");receipt_path=registry.with_name("reaper-receipt.json")
    own=birth(os.getpid())
    if own["state"]!="running":return 2
    atomic_json(ready,{"pid":os.getpid(),"birth":own["birth"],"deadline_ns":deadline,"job_name":job.name})
    cid=None;last=initial
    while time.monotonic_ns()<deadline+15000000000:
        try:
            current=json.loads(registry.read_text(encoding="utf-8"))
            if current["intent"]!=fixed or current["deadline_ns"]!=deadline or current["parent"]!=parent:
                atomic_json(receipt_path,{"tree_confirmation":"unconfirmed","error_code":"registry_identity_changed"});return 1
            last=current
        except (OSError,ValueError,KeyError):pass
        if last.get("complete"):
            atomic_json(receipt_path,{"state":"parent_confirmed_complete","pid":os.getpid(),"at_ns":time.monotonic_ns()});return 0
        proposed=last.get("cid")
        if proposed and cid is None:
            try:inspect_owned(fixed["docker"],proposed,fixed)
            except (DockerUnknown,ValueError):
                atomic_json(receipt_path,{"tree_confirmation":"unconfirmed","error_code":"cid_bind_unknown"});return 1
            cid=proposed;atomic_json(bound,{"cid":cid,"image_id":fixed["image_id"],"nonce":fixed["nonce"],"deadline_ns":deadline})
        current_parent=birth(parent["pid"])
        lost=current_parent["state"]=="exited" or (current_parent["state"]=="running" and current_parent["birth"]!=parent["birth"])
        parent_unknown=current_parent["state"]=="unknown"
        expired=time.monotonic_ns()>=deadline-10000000000
        if lost or parent_unknown or expired:
            try:
                cid=cid or find_intent(fixed["docker"],fixed)
                if cid:
                    kernel_path=registry.with_name("kernel-premises.json")
                    facts=json.loads(kernel_path.read_text(encoding="utf-8")) if kernel_path.is_file() else None
                    proof=stop_owned(fixed["docker"],cid,fixed,facts,attach_ended=False,diagnostic_deadline_ns=deadline+15000000000)
                    # attach/控制者终结由存活父或重启救援补核，救援不伪称它已知道EOF。
                    proof["reason"]="deadline" if expired else "parent_unknown" if parent_unknown else "parent_lost"
                    atomic_json(receipt_path,proof);return 0
                atomic_json(receipt_path,{"tree_confirmation":"unconfirmed","error_code":"create_intent_unresolved",
                                          "name":fixed["name"],"at_ns":time.monotonic_ns()});return 1
            except (DockerUnknown,OSError,ValueError):
                atomic_json(receipt_path,{"tree_confirmation":"unconfirmed","error_code":"cleanup_unconfirmed"});return 1
        time.sleep(.1)
    atomic_json(receipt_path,{"tree_confirmation":"unconfirmed","error_code":"reaper_deadline"});return 1


if __name__=="__main__":raise SystemExit(main())
