"""一批相关离线验证：跨语言拒绝、数值/域/状态与必要旧契约回归。"""
from __future__ import annotations
import ast
import json
import os
from pathlib import Path
import sys
from .control import ROOT,EVIDENCE,batch,reserve,run,source_snapshot,atomic,event
from .samples import energy,binomial,invalid_cases


def main():
    folder=EVIDENCE/"offline-01"
    with batch("offline","v2-complete-static-and-description",maximum=1800):
        folder.mkdir(exist_ok=True);source_snapshot(folder)
        for path in (ROOT/"backend/app/preview").glob("*.py"):ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
        for relative in ("backend/app/capabilities/contracts.py","backend/app/capabilities/gateway.py","backend/app/activities/repository.py","backend/app/activities/api.py","backend/app/main.py","backend/app/service_config.py"):
            ast.parse((ROOT/relative).read_text(encoding="utf-8"),filename=relative)
        from app.preview.description import validate_description,DescriptionError,canonical,control_value
        from app.preview.compiler import compile_description,runtime_identity,runtime_html
        from app.preview.business_contracts import HtmlCommand
        from uuid import uuid4
        valid=[energy(),binomial()]
        for value in valid:validate_description(value,set(value["citations"]));compile_description(value,set(value["citations"]))
        failures=[]
        for name,value in invalid_cases():
            try:validate_description(value,{"lc_synthetic_energy"})
            except DescriptionError:continue
            failures.append(name)
        if failures:raise AssertionError("Python accepted invalid descriptions: "+','.join(failures))
        control_value(valid[1]["inputs"][2],"0.3")
        for value in ("0.30","1.1","NaN","-0"):
            try:control_value(valid[1]["inputs"][2],value)
            except DescriptionError:continue
            raise AssertionError("invalid grid accepted")
        from app.preview.description import load_json
        try:load_json('{"x":1,"x":2}')
        except DescriptionError:pass
        else:raise AssertionError("duplicate key accepted")
        command={"business_key":str(uuid4()),"parent":{"kind":"learning","operation_id":"learn-first-v1."+"a"*64,"payload_sha256":"b"*64,"segment_index":0},"focus":"x","expected_config_sha256":"c"*64,"confirmed":1}
        try:HtmlCommand.model_validate(command)
        except ValueError:pass
        else:raise AssertionError("integer confirmation accepted")
        (folder/"descriptions.json").write_text(json.dumps({"valid":valid,"invalid":invalid_cases()},ensure_ascii=True,sort_keys=True),encoding="utf-8")
        run(["node",str(ROOT/"frontend/tests/task111/offline.cjs"),str(folder/"descriptions.json")],folder,cwd=ROOT,maximum=60,name="node-contract")
        reserve("frontend_typecheck_build_batches",{"kind":"build"})
        run(["C:\\Program Files\\nodejs\\npm.cmd","run","build"],folder,cwd=ROOT/"frontend",maximum=300,name="frontend-build")
        # 原四账/Gateway/OneCall契约的实际影响，不连接用户库，也不跑提交DELETE的PG套件。
        run([sys.executable,"-B","-m","unittest","tests.test_capabilities","tests.test_worker_one_call"],folder,cwd=ROOT/"backend",maximum=120,name="legacy-contracts")
        identity=runtime_identity();html=runtime_html();atomic(folder/"runtime.json",{"identity":identity,"compiled_html_sha256":__import__('hashlib').sha256(html.encode()).hexdigest(),"compiled_html_bytes":len(html.encode()),"invalid_cases":len(invalid_cases())})
        atomic(folder/"result.json",{"status":"PASS_OFFLINE_ONLY","invalid_cases":len(invalid_cases()),"product_runtime_or_g11":False})
        event("offline_complete",{"description_cases":len(invalid_cases()),"identity":identity})


if __name__=="__main__":main()
