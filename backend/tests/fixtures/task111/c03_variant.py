"""一个冻结专用variant承载有限忙死夹具，独立于最终生产image/load。"""
import importlib.util,json,shutil
from .control import ROOT,CONTINUE_ROOT,reserve,atomic,run
from .resources import DOCKER

def build(folder):
    spec=importlib.util.spec_from_file_location("task111_c03_variant_builder",ROOT/"deploy/preview/build_renderer.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    number=reserve("image_builds",{"purpose":"C03 one frozen fault variant"});tag="retrolume-task-111-g11-renderer:v2-"+str(number).zfill(2)
    context=ROOT/"deploy/preview/build-contexts"/("v2-"+str(number).zfill(2))
    prepared=module.prepare(context,base_oci=ROOT/"deploy/preview/task109-c01-cache/oci")
    host=context/"renderer-host.cjs";text=host.read_text(encoding="utf-8")
    text=text.replace("const fs=require('node:fs'),", "const fault=require('./task111-fault.cjs');\nconst fs=require('node:fs'),",1)
    text=text.replace("async function input(body,seq){", "async function input(body,seq){\n await fault.beforeInput({frame});",1)
    host.write_text(text,encoding="utf-8");shutil.copyfile(ROOT/"backend/tests/fixtures/task111/c03_fault_runtime.cjs",context/"task111-fault.cjs")
    load=json.loads((context/"load-manifest.json").read_text(encoding="utf-8"));load["files"]["renderer-host.cjs"]=module.sha(host.read_bytes());load["files"]["task111-fault.cjs"]=module.sha((context/"task111-fault.cjs").read_bytes())
    (context/"load-manifest.json").write_text(module.canonical(load),encoding="utf-8")
    (context/"Dockerfile").write_text((context/"Dockerfile").read_text(encoding="utf-8").replace("load-manifest.json ./","load-manifest.json task111-fault.cjs ./"),encoding="utf-8")
    prepared.update(load_manifest_sha256=module.sha((context/"load-manifest.json").read_bytes()),source_files=load["files"],fault_variant=True)
    atomic(folder/"fault-build-input.json",prepared)
    run([DOCKER,*module.build_args(context,prepared["base_oci"],tag,folder/"build-metadata.json")],folder,cwd=ROOT,maximum=600,name="fault-variant-build")
    result=run([DOCKER,"image","inspect","--format",'{"id":{{json .Id}},"descriptor":{{json .Descriptor}}}',tag],folder,maximum=10,name="fault-image")
    prepared.update(image=json.loads(result.stdout),tag=tag);atomic(folder/"fault-production-build.json",prepared);atomic(CONTINUE_ROOT/"fault-build.json",prepared)
    return prepared
