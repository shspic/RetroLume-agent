"""续作第一个固定关联离线批；一个进程登记，后续定向子检查不另开批。"""
import ast,json,sys,time,traceback
from pathlib import Path
from .control import ROOT,CONTINUE_ROOT,batch,atomic,source_snapshot,run,phase


def main():
    folder=CONTINUE_ROOT/"offline-07";folder.mkdir(exist_ok=False)
    with batch("offline","c01-final-control-fixture-static",maximum=1200):
        source_snapshot(folder)
        try:
            paths=list((ROOT/"backend/app/preview").glob("*.py"))+list((ROOT/"backend/tests/fixtures/task111").glob("c01*.py"))
            for path in paths:ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
            from app.preview.docker_control import namespace_premises
            base={"processes":{"kernel":"6.6.114.1-microsoft-standard-WSL2","own_uid":10001,"own_gid":10001,"own_pid":2,"own_namespace":"pid:[1234]","init_namespace":"pid:[1234]","errors":[],"rows":[
                {"pid":1,"NSpid":"1","birth_ticks":"11","pid_namespace":"pid:[1234]"},{"pid":2,"NSpid":"2","birth_ticks":"12","pid_namespace":"pid:[1234]","NoNewPrivs":"1","CapEff":"0000000000000000"}]}}
            intent={"kernel_release":"6.6.114.1-microsoft-standard-WSL2"};assert namespace_premises(base,intent)
            from copy import deepcopy
            missing=deepcopy(base);missing["processes"].pop("own_namespace");missing["processes"].pop("init_namespace");assert not namespace_premises(missing,intent)
            for value in (None,"","pid:[]","pid:[x]"):
                wrong=deepcopy(base);wrong["processes"]["own_namespace"]=wrong["processes"]["init_namespace"]=value;assert not namespace_premises(wrong,intent)
            run(["node","--check",str(ROOT/"frontend/tests/task111/browser.cjs")],folder,maximum=10,name="browser-fixture-syntax")
            atomic(folder/"result.json",{"status":"PASS_STATIC_ONLY","syntax_files":len(paths),"missing_namespace_rejected":True,"no_runtime_start":True})
        except Exception:
            (folder/"failure.txt").write_text(traceback.format_exc(),encoding="utf-8");raise


if __name__=="__main__":main()
