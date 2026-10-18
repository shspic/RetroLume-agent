"""同卡固定HTTP正常/故障入口，真实远端ACK与精确停止，不替代主UI证据。"""
import json,secrets,time,hashlib
from pathlib import Path
from uuid import uuid4
from .control import CONTINUE_ROOT,EVIDENCE,atomic
from app.preview.description import digest


def normal_http(matrix,folder,item,kind):
    aid=item["activity_id"];base=f"/api/activities/{aid}/html"
    artifact=matrix.request("GET",base+"/artifacts/"+item["receipt"]["artifact_id"])
    owner=secrets.token_hex(32);headers={"X-RetroLume-Preview-Owner":owner}
    opened=matrix.request("POST",base+"/artifacts/"+artifact["artifact_id"]+"/previews",{
      "start_key":str(uuid4()),"expected_artifact_sha256":artifact["artifact_sha256"],"input_owner_key":owner,"confirmed":True})
    pid=opened["preview_id"];until=time.monotonic()+8;last=opened
    while time.monotonic()<until:
        last=matrix.request("GET",base+"/previews/"+pid,headers=headers)
        if last["state"]=="ready":break
        if last["state"] in ("cleanup_unconfirmed","failed_unstarted","stopped"):raise RuntimeError("normal ready failed: "+last["state"])
        time.sleep(.05)
    if last["state"]!="ready":raise RuntimeError("normal ready timeout")
    events=[("h","3",58.8),("h","0",0),("m","0",0)] if kind=="energy" else [("p","0.5",.375),("k","0",.125),("p","0",1),("n","0",1),("n","20",1),("k","20",0)]
    acks=[];frames=[]
    for seq,(control,value,expected) in enumerate(events,1):
        action={"type":"set_number","control_id":"hctl_"+control,"value":value}
        body=matrix.request("POST",base+"/previews/"+pid+"/inputs",{"preview_generation":last["generation"],"seq":seq,"payload_sha256":digest(action),"event":action},headers=headers)
        acks.append({"expected":expected,"ack":body});atomic(folder/("normal-acks-"+kind+".json"),acks)
        if body.get("accepted") is not True or abs(float(body["readouts"][0]["value"])-expected)>1e-9:raise RuntimeError("remote mathematical oracle")
        response=matrix.client.get(base+"/previews/"+pid+"/frames",params={"generation":last["generation"],"after_seq":0},headers=headers)
        if response.status_code==200:
            name="remote-"+kind+"-"+str(seq)+".png";(folder/name).write_bytes(response.content)
            frames.append({"path":name,"bytes":len(response.content),"sha256":hashlib.sha256(response.content).hexdigest()})
        time.sleep(.5)
    matrix.request("POST",base+"/previews/"+pid+"/stop",{"generation":last["generation"],"stop_key":str(uuid4()),"reason":"user"})
    until=time.monotonic()+15
    while time.monotonic()<until:
        last=matrix.request("GET",base+"/previews/"+pid,headers=headers)
        if last["state"] in ("stopped","cleanup_unconfirmed"):break
        time.sleep(.1)
    atomic(folder/("normal-http-"+kind+".json"),{"preview_id":pid,"acks":acks,"frames":frames,"final":last,"main_UI_pass":False})
    if last["state"]!="stopped" or not frames:raise RuntimeError("normal full stop or actual PNG missing")


def verify(resource,built,folder,matrix,command):
    if command.get("mode")=="normal_http":
        progress=json.loads((CONTINUE_ROOT/"native-progress.json").read_text(encoding="utf-8"));kind=command["kind"]
        normal_http(matrix,folder,progress[kind],kind);return
    raise RuntimeError("complete fault scenarios not yet prepared")
