"""断点修正后的定向离线复核与许可材料；不重复前端构建或启动真实资源。"""
from __future__ import annotations
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from .control import ROOT,EVIDENCE,batch,atomic,run,source_snapshot,event
from .samples import energy,binomial,const,op


def main():
    folder=EVIDENCE/"offline-02";folder.mkdir(exist_ok=False)
    with batch("offline","resume-host-deployment-limit-license-repair",maximum=600):
        source_snapshot(folder)
        for name in ("backend/app/preview/docker_control.py","backend/app/preview/process.py","backend/app/preview/production_supervisor.py",
                     "backend/tests/fixtures/task111/control.py","backend/tests/fixtures/task111/cleanup.py","deploy/start_local.py","deploy/preview/collect_licenses.py"):
            ast.parse((ROOT/name).read_text(encoding="utf-8"),filename=name)
        from app.preview.docker_control import creation_args,local_create_rejection
        control=EVIDENCE/"synthetic/http-control/2672ce7f-c64f-4605-8395-109a47310d06"
        registry=json.loads((control/"registry.json").read_text(encoding="utf-8"));intent=registry["intent"]
        saved=json.loads((control/"create.json").read_text(encoding="utf-8"));seccomp=ROOT/"deploy/preview/seccomp.json"
        assert "--pid" not in creation_args(intent,seccomp)
        assert local_create_rejection(saved,intent,seccomp)
        variants=[]
        for key,value in (("code",1),("code",0),("stdout","a"*64),("stderr","connection lost"),("start_ns",0),("end_ns",0),("end_ns","1")):
            bad=deepcopy(saved);bad[key]=value;assert not local_create_rejection(bad,intent,seccomp);variants.append(key)
        changed=deepcopy(intent);changed["nonce"]="b"*64;changed["labels"]["retrolume.nonce"]="b"*64
        assert not local_create_rejection(saved,changed,seccomp)
        from app.preview.host_policy import load_host_policy
        assert load_host_policy(ROOT/"config/preview.example.json",folder/"unused-control") is None
        from app.preview.description import validate_description
        p=binomial();p["inputs"][0].update(min="0",max="20");p["inputs"][1].update(max="20")
        upper=energy();branches=[op("binomial_pmf",const("20"),const("20"),const("0.5")) for _ in range(16)]
        while len(branches)>1:branches=[op("add",branches[i],branches[i+1]) for i in range(0,len(branches),2)]
        upper["views"]=[upper["views"][0],{"id":"hview_limit","kind":"curve","label":"有限步数上界", "source":{"min":"0","max":"1","samples":128,"expression":branches[0]}}]
        for description in (p,upper):validate_description(description,set(description["citations"]))
        atomic(folder/"limits.json",{"binomial":p,"upper":upper})
        run(["node",str(ROOT/"frontend/tests/task111/limits.cjs"),str(folder/"limits.json")],folder,cwd=ROOT,maximum=30,name="node-limits")
        spec=importlib.util.spec_from_file_location("task111_collect_licenses",ROOT/"deploy/preview/collect_licenses.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        licenses=module.collect(ROOT/"deploy/preview/task109-c01-cache/oci",ROOT/"deploy/preview/licenses/base-c091b21d-v2")
        atomic(folder/"license-coverage.json",{"notices":len(licenses["notices"]),"vendor_notices":len(licenses["vendor_notices"]),"coverage":licenses["coverage"]})
        atomic(folder/"result.json",{"status":"PASS_OFFLINE_CHECKS_ONLY","syntax_files":7,"narrow_rejection_negative_variants":len(variants)+1,
              "runtime_resource_starts":0,"production_review":False,"license_coverage":licenses["coverage"]})
        event("resume_offline_complete",{"scope":"host/deployment repair and numeric upper bound; no runtime verdict","folder":str(folder)})


if __name__=="__main__":main()
