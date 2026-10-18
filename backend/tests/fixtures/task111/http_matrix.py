"""公开HTTP/真实浏览器和PG定向矩阵，非mock替代；原数据全部保留。"""
from __future__ import annotations
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from uuid import uuid4
import httpx
from .control import ROOT,EVIDENCE,PERMIT,reserve,event,atomic,run
from .resources import shell_env

BASE="http://127.0.0.1:18111"


class HttpMatrix:
    def __init__(self,resource,built,folder):
        self.resource,self.built,self.folder=resource,built,folder;self.token=secrets.token_urlsafe(32);self.process=None;self.actual_owner=None
        self.client=httpx.Client(base_url=BASE,timeout=120,trust_env=False,headers={"X-RetroLume-Session":self.token,"Origin":BASE})
        self.results=[]

    def start(self):
        policy={"image_id":self.built["image"]["id"],"load_manifest_sha256":self.built["load_manifest_sha256"],"renderer_sha256":self.built["renderer_sha256"],
                "kernel_release":self.resource["platform"]["kernel"],"docker":r"C:\Users\28432\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe"}
        env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_INTERACTIVE_TEST_DATABASE_URL=self.resource["app"],
           RETROLUME_TASK111_SESSION=self.token,RETROLUME_TASK111_POLICY=json.dumps(policy),PYTHONPATH=str(ROOT/"backend/tests/fixtures/task111/bootstrap")+os.pathsep+str(ROOT/"backend"))
        reserve("API_listener_starts",{"port":18111})
        self.stdout=(self.folder/"api.stdout.bin").open("wb");self.stderr=(self.folder/"api.stderr.bin").open("wb")
        self.process=subprocess.Popen([sys.executable,"-B","-m","tests.fixtures.task111.server"],cwd=ROOT/"backend",env=env,stdin=subprocess.PIPE,
                                      stdout=self.stdout,stderr=self.stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        from app.preview.process import birth
        atomic(self.folder/"api-owner.json",{"pid":self.process.pid,"birth":birth(self.process.pid),"port":18111})
        until=time.monotonic()+20
        while True:
            if self.process.poll() is not None:raise RuntimeError("TASK111 API process ended")
            try:
                if self.client.get("/health").status_code==200:break
            except httpx.HTTPError:pass
            if time.monotonic()>until:raise RuntimeError("TASK111 API ready timeout")
            time.sleep(.2)
        from .control import CONTINUE_ROOT
        from app.preview.host_job import child_lineage
        primary=birth(self.process.pid);owners=[]
        for path in CONTINUE_ROOT.glob("api-actual-*.json"):
            row=json.loads(path.read_text(encoding="utf-8"))
            if birth(row["pid"])["state"]=="exited":continue
            try:row["lineage"]=child_lineage(row["pid"],row["birth"],self.process.pid,primary["birth"]);owners.append(row)
            except RuntimeError:continue
        if len(owners)!=1:raise RuntimeError("API actual owner unconfirmed")
        self.actual_owner=owners[0];atomic(self.folder/"api-actual-bound.json",self.actual_owner)

    def fixture_command(self,value):
        if set(value)!={"scenario","activity_id","preview_id","generation"}:raise RuntimeError("fixture control fields")
        self.process.stdin.write((json.dumps(value,sort_keys=True)+"\n").encode());self.process.stdin.flush()

    def request(self,method,path,body=None,expected=200,headers=None):
        response=self.client.request(method,path,json=body,headers=headers)
        data=response.json() if response.content and response.headers.get("content-type","").startswith("application/json") else None
        entry={"method":method,"path":path,"status":response.status_code,"expected":expected,"response":data}
        self.results.append(entry);atomic(self.folder/"http-effects.json",self.results)
        assert response.status_code==expected,entry
        return data

    def generate(self,aid,parent,focus):
        base=f"/api/activities/{aid}/html";caps=self.request("GET",base+"/capabilities")
        assert caps["available"],caps
        command={"business_key":str(uuid4()),"parent":parent,"focus":focus,"expected_config_sha256":caps["config_sha256"],"confirmed":True}
        receipt=self.request("POST",base+"/commands",command)
        assert self.request("GET",base+"/commands/"+command["business_key"])["artifact_id"]==receipt["artifact_id"]
        return receipt,command

    def browser(self,cases):
        reserve("main_browser_starts",{"purpose":"real-learning-html-UI"})
        payload=self.folder/"browser-input.json";atomic(payload,{"base":BASE,"cases":cases,"out":str(self.folder)})
        env=shell_env();env["RETROLUME_TASK111_BROWSER_SESSION"]=self.token
        run(["node",str(ROOT/"frontend/tests/task111/browser.cjs"),str(payload)],self.folder,cwd=ROOT,env=env,maximum=600,name="browser-matrix")

    def close(self):
        self.client.close()
        if self.actual_owner:
            from app.preview.process import terminate_owned
            terminate_owned(self.actual_owner["pid"],self.actual_owner["birth"])
        elif self.process and self.process.poll() is None:raise RuntimeError("API actual owner unknown")
        if self.process and self.process.poll() is None:
            try:self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=5)
        self.stdout.close();self.stderr.close()
