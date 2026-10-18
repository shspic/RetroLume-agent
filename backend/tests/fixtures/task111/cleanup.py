"""仅收尾已经登记的本卡对象；独立清场预留不增加运行许可。"""
from __future__ import annotations
import json
from pathlib import Path
from .control import EVIDENCE,PERMIT,batch,run,atomic,event
from .resources import DOCKER,PG,PG_IMAGE
from app.preview.process import birth,terminate_owned


def main():
    folder=EVIDENCE/"cleanup-resume-20261010"
    folder.mkdir(exist_ok=False)
    proof={"permit":PERMIT,"errors":[],"scope":"recorded TASK111 resources only; no budget settlement or new start"}
    with batch("cleanup","interrupted-root6-resource-cleanup",maximum=180):
        try:
            expected=json.loads((EVIDENCE/"real-01/pg-final.stdout.bin").read_text(encoding="utf-8"))
            fmt='{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"running":{{json .State.Running}},"pid":{{json .State.Pid}}}'
            before=json.loads(run([DOCKER,"inspect","--format",fmt,expected["id"]],folder,maximum=10,name="pg-before").stdout)
            if (before["id"]!=expected["id"] or before["image"]!=PG_IMAGE.split("@",1)[1] or before["name"]!="/"+PG):
                raise RuntimeError("PG ownership mismatch; not stopped")
            if before["running"]:run([DOCKER,"stop","--time","5",before["id"]],folder,maximum=15,name="pg-stop")
            after=json.loads(run([DOCKER,"inspect","--format",fmt,before["id"]],folder,maximum=10,name="pg-after").stdout)
            proof["pg"]={"before":before,"after":after,"stopped":after["id"]==before["id"] and not after["running"] and after["pid"]==0}
        except Exception as error:proof["errors"].append({"part":"pg","type":type(error).__name__,"reason":str(error)})
        root=EVIDENCE/"synthetic/http-control"
        for registry_file in root.glob("*/registry.json"):
            registry=json.loads(registry_file.read_text(encoding="utf-8"));intent=registry["intent"]
            if intent["labels"].get("retrolume.authorization")!=PERMIT:raise RuntimeError("preview permit mismatch")
            response=run([DOCKER,"ps","-a","--no-trunc","--filter","name=^/"+intent["name"]+"$","--format","{{.ID}}"],folder,maximum=10,name="preview-"+registry["preview_id"])
            ids=response.stdout.decode().split()
            row={"preview_id":registry["preview_id"],"name":intent["name"],"objects":ids,"start_requested":bool(registry.get("start_requested_ns"))}
            ready=registry_file.parent/"reaper-ready.json"
            if ready.is_file():
                recorded=json.loads(ready.read_text(encoding="utf-8"));snapshot=birth(recorded["pid"])
                if snapshot["state"]=="running" and snapshot.get("birth")==recorded["birth"]:
                    row["owned_reaper_terminated"]=terminate_owned(recorded["pid"],recorded["birth"])
                    snapshot=birth(recorded["pid"])
                row["reaper_birth_check"]=snapshot
            created_file=registry_file.parent/"create.json"
            created=json.loads(created_file.read_text(encoding="utf-8")) if created_file.is_file() else {}
            row["known_create_rejection_no_object"]=(not ids and not row["start_requested"] and created.get("code")==125
                and "--pid: invalid PID mode" in created.get("stderr","") and row.get("reaper_birth_check",{}).get("state")=="exited")
            proof.setdefault("previews",[]).append(row)
            if ids:proof["errors"].append({"part":"preview","reason":"unexpected recorded object requires exact rescue; no new start"})
        loop=json.loads((EVIDENCE/"real-06/loop-ready.json").read_text(encoding="utf-8"))
        proof["root6_process"]=birth(loop["pid"])
        # 只核本卡两个独占端口，不枚举或停止其他用户进程。
        command="$rows=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in 18111,55451 } | Select-Object LocalAddress,LocalPort,OwningProcess); ConvertTo-Json -InputObject $rows -Compress"
        listeners=json.loads(run(["powershell","-NoProfile","-Command",command],folder,maximum=15,name="ports-after").stdout.decode("utf-8-sig"))
        proof["listeners"]=listeners
        proof["physical_cleanup_confirmed"]=(not proof["errors"] and proof.get("pg",{}).get("stopped") is True
            and not listeners and proof["root6_process"]["state"]=="exited"
            and all(row["known_create_rejection_no_object"] for row in proof.get("previews",[])))
        atomic(folder/"cleanup-receipt.json",proof)
        event("cleanup_completed",{"confirmed":proof["physical_cleanup_confirmed"],"receipt":str(folder/"cleanup-receipt.json")})
    print(json.dumps({"cleanup_confirmed":proof["physical_cleanup_confirmed"],"receipt":str(folder/"cleanup-receipt.json")}))


if __name__=="__main__":main()
