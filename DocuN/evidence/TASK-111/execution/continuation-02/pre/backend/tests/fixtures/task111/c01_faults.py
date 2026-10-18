"""冻结故障计划。只作用精确自有CID/namespace和本卡测试进程，不加公开fault接口。"""
from pathlib import Path
import hashlib,json,secrets,time
from uuid import uuid4
from .control import CONTINUE_ROOT,atomic,event,reserve
from app.preview.description import digest

PLAN=("qualification_cache_barrier","cancel_refresh_budget","renderer_busy","browser_busy","supervisor_death","reaper_death","create_reply_lost","control_lost","pipe_corrupt","hard_deadline")


def verify_faults(resource,built,folder,diagnostic,matrix):
    # 计划与运行方法ID显式分离，缺独立触发/原件不把计划签成通过。
    result=[]
    for number,name in enumerate(PLAN):
        item=diagnostic[number//3];aid=item["activity_id"];artifact=matrix.request("GET",f"/api/activities/{aid}/html/artifacts/"+item["receipt"]["artifact_id"])
        owner=secrets.token_hex(32)
        opened=matrix.request("POST",f"/api/activities/{aid}/html/artifacts/{artifact['artifact_id']}/previews",{"start_key":str(uuid4()),"expected_artifact_sha256":artifact["artifact_sha256"],"input_owner_key":owner,"confirmed":True})
        pid=opened["preview_id"];root=CONTINUE_ROOT/"fault-"+name;root.mkdir(exist_ok=False)
        # 仅已冻结有限名字通过继承匿名控制管道交本卡API夹具执行；没有URL、代码或任意命令。
        command={"scenario":name,"activity_id":aid,"preview_id":pid,"generation":opened["generation"]}
        matrix.fixture_command(command)
        until=time.monotonic()+65;last=None
        while time.monotonic()<until:
            headers={"X-RetroLume-Preview-Owner":owner} if name not in ("control_lost","supervisor_death","hard_deadline") else {}
            last=matrix.request("GET",f"/api/activities/{aid}/html/previews/"+pid,headers=headers)
            if last["state"] in ("stopped","failed_unstarted","cleanup_unconfirmed"):break
            time.sleep(.15)
        receipt={"scenario":name,"preview_id":pid,"last":last,"classification":"fault request sent; requires independent scenario evidence"}
        atomic(root/"receipt.json",receipt);result.append(receipt)
        if last is None or last["state"]=="cleanup_unconfirmed":
            raise RuntimeError("fault stop unconfirmed: "+name)
    atomic(folder/"fault-results.json",result)
