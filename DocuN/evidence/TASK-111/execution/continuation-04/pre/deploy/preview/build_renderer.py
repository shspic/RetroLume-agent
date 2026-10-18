"""仅用明确的本地OCI和项目正式资源构建；不安装或联网取依赖。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
PREVIEW=Path(__file__).resolve().parent
BASE_MANIFEST="c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac"
BROWSER_SHA="0b20b130e7edd9dd51873be867761295fe0cfad490c2b9a64f95bd3cfc08fa71"


def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(data):return hashlib.sha256(data).hexdigest()


def prepare(context_dir,*,base_oci):
    context_dir=Path(context_dir).resolve();base_oci=Path(base_oci).resolve()
    if ROOT not in context_dir.parents or context_dir.exists():raise ValueError("new_build_context_required")
    index=json.loads((base_oci/"index.json").read_text(encoding="utf-8"))
    if len(index["manifests"])!=1 or index["manifests"][0]["digest"]!="sha256:"+BASE_MANIFEST:raise ValueError("base_oci_identity")
    manifest_bytes=(base_oci/"blobs/sha256"/BASE_MANIFEST).read_bytes()
    if sha(manifest_bytes)!=BASE_MANIFEST:raise ValueError("base_manifest_bytes")
    context_dir.mkdir(parents=True)
    source_files=("runtime.cjs","runtime.css","runtime.html","descriptor.schema.json","renderer-host.cjs","renderer-bootstrap.cjs","renderer-assembly.cjs","renderer-protocol.cjs")
    for name in source_files:shutil.copy2(PREVIEW/name,context_dir/name)
    shutil.copytree(PREVIEW/"vendor/playwright-core",context_dir/"vendor/playwright-core")
    license_root=PREVIEW/"licenses/base-c091b21d-c02-resolved-02"
    license_inventory=json.loads((license_root/"inventory.json").read_text(encoding="utf-8"))
    if license_inventory["base_manifest"]!="sha256:"+BASE_MANIFEST or not license_inventory["coverage"]["main_chrome_actual_credits"]:
        raise ValueError("formal_license_materials_required")
    for item in license_inventory["files"]:
        path=license_root/item["path"]
        if path.resolve().is_relative_to(license_root.resolve()) is not True or sha(path.read_bytes())!=item["sha256"]:raise ValueError("formal_license_byte_identity")
    shutil.copytree(license_root,context_dir/"licenses")
    files={name:sha((context_dir/name).read_bytes()) for name in source_files}
    vendor_files={str(path.relative_to(context_dir)).replace("\\","/"):sha(path.read_bytes()) for path in (context_dir/"vendor/playwright-core").rglob("*") if path.is_file()}
    files.update(vendor_files)
    files.update({"licenses/"+path.relative_to(context_dir/"licenses").as_posix():sha(path.read_bytes()) for path in (context_dir/"licenses").rglob("*") if path.is_file()})
    renderer={name:files[name] for name in ("runtime.cjs","runtime.css","runtime.html","descriptor.schema.json")}
    load={"schema":"retrolume.preview.load.v2","policy":"retrolume.renderer.v2","renderer_sha256":sha(canonical(renderer).encode("utf-8")),
      "files":files,"browser_sha256":BROWSER_SHA,"playwright":"1.62.1","node":"v24.18.1","base_manifest":"sha256:"+BASE_MANIFEST}
    (context_dir/"load-manifest.json").write_text(canonical(load),encoding="utf-8")
    # named OCI context只由构建调用提供；正式运行不依赖历史cache目录。
    dockerfile=(PREVIEW/"Dockerfile.production").read_text(encoding="utf-8")
    (context_dir/"Dockerfile").write_text(dockerfile,encoding="utf-8")
    (context_dir/".dockerignore").write_text(".git\n",encoding="utf-8")
    return {"context":str(context_dir),"base_manifest":"sha256:"+BASE_MANIFEST,"base_config":json.loads(manifest_bytes)["config"],
      "load_manifest_sha256":sha((context_dir/"load-manifest.json").read_bytes()),"renderer_sha256":load["renderer_sha256"],
      "vendor_files":len(vendor_files),"source_files":files,"base_oci":str(base_oci)}


def build_args(context_dir,base_oci,tag,metadata):
    uri="oci-layout://"+Path(base_oci).resolve().as_posix()+"@sha256:"+BASE_MANIFEST
    return ["buildx","build","--platform","linux/amd64","--network","none","--pull=false","--load","--progress","plain",
      "--build-context","cached_base="+uri,"--build-arg","BASE_IMAGE=cached_base","--file",str(Path(context_dir)/"Dockerfile"),
      "--metadata-file",str(metadata),"--tag",tag,str(context_dir)]
