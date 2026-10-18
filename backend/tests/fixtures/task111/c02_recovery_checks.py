"""新增早期未create恢复的有限控制流检查；替身不冒PG或真实止树证明。"""
import asyncio,json,shutil
from pathlib import Path
from unittest.mock import patch
from .control import ROOT,EVIDENCE,CONTINUE_ROOT,batch,atomic,source_snapshot,PERMIT
from .resources import DOCKER
from app.preview.host_policy import HostPolicy
from app.preview.production_supervisor import PreviewController
from app.runtime import psycopg_compatible_loop_factory


class Ledger:
    def __init__(self):self.writes=[]
    async def read_html_preview(self,*_):return {"state":"cleanup_unconfirmed","reserve_seconds":60}
    async def update_html_preview(self,pid,key,state,**fields):self.writes.append({"preview_id":pid,"state":state,"fields":fields})


def main():
    folder=CONTINUE_ROOT/"recovery-functional-01";folder.mkdir(exist_ok=False)
    original=EVIDENCE/"synthetic/http-control/4f846728-ce59-4e64-932f-53cf8286bf6c"
    built=json.loads((EVIDENCE/"real-01/production-build.json").read_text(encoding="utf-8"));result=[]
    with batch("offline","c02-precreate-recovery-functional-control",maximum=30):
        source_snapshot(folder)
        for mode in ("known_precreate","unknown_reason","create_marker_without_receipt"):
            root=folder/mode;target=root/original.name;target.mkdir(parents=True)
            for name in ("registry.json","failure.json","reaper-ready.json"):shutil.copy2(original/name,target/name)
            row=json.loads((target/"registry.json").read_text(encoding="utf-8"))
            if mode=="create_marker_without_receipt":row["create_requested_ns"]=row["deadline_ns"]-1;atomic(target/"registry.json",row)
            if mode=="unknown_reason":atomic(target/"failure.json",{"type":"OwnershipUnknown","code":"unknown_reason"})
            atomic(root/"current.json",{"preview_id":row["preview_id"],"folder":str(target)})
            policy=HostPolicy(image_id=built["image"]["id"],load_manifest_sha256=built["load_manifest_sha256"],renderer_sha256=built["renderer_sha256"],
                kernel_release="6.6.114.1-microsoft-standard-WSL2",docker=DOCKER,registry_dir=root.resolve(),authorization=PERMIT,owner_name="Global\\RetroLumePreviewV2Task111")
            ledger=Ledger();controller=PreviewController(ledger,policy)
            async def run():
                try:
                    with patch("app.preview.production_supervisor.find_intent",return_value=None),patch("app.preview.production_supervisor.birth",return_value={"state":"exited"}),patch("app.preview.production_supervisor.terminate_owned",return_value=True):await controller.recover()
                finally:await controller.close()
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(run())
            if mode=="known_precreate":
                if controller.blocked or len(ledger.writes)!=1 or ledger.writes[0]["state"]!="failed_unstarted" or ledger.writes[0]["fields"]["elapsed"]!=60:raise RuntimeError("known no-create full reserve branch")
            elif not controller.blocked or ledger.writes:raise RuntimeError("unknown branch accepted")
            result.append({"mode":mode,"blocked":controller.blocked,"fake_ledger_updates":ledger.writes})
        atomic(folder/"result.json",{"status":"PASS_BRANCH_ONLY_WITH_DOUBLES","cases":result,"doubles":["PG ledger","process birth","exact object lookup","owned process end"],"no_live_recovery_or_refund_claim":True})
    print("precreate recovery control branches checked; no live PG settlement")


if __name__=="__main__":main()
