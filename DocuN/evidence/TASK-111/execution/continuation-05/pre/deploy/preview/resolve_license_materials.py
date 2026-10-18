"""新的定界许可方法：继承普通文本、逻辑链接定位及主Chrome PAK版权文字。"""
from __future__ import annotations
import hashlib,json,posixpath,shutil,subprocess,tarfile
from pathlib import Path,PurePosixPath

FORMAL=Path(__file__).resolve().parent
BASE="c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac"
OPENSSL_SHA="7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a"


def safe_name(name):
    name=name.removeprefix("./");value=PurePosixPath(name)
    if value.is_absolute() or ".." in value.parts:raise ValueError("unsafe_logical_image_name")
    return value.as_posix()


def collect_resolved(base_oci,output,openssl_text):
    base_oci=Path(base_oci).resolve();output=Path(output).resolve()
    if output.parent!=FORMAL/"licenses" or output.exists():raise ValueError("new_formal_directory_required")
    manifest_raw=(base_oci/"blobs/sha256"/BASE).read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest()!=BASE:raise ValueError("fixed_manifest")
    manifest=json.loads(manifest_raw);previous=json.loads((FORMAL/"licenses/base-c091b21d-v2-final/inventory.json").read_text(encoding="utf-8"))
    if previous["base_manifest"]!="sha256:"+BASE:raise ValueError("prior_material_identity")
    output.mkdir();rows=[];total=0
    def copy(name,data,origin):
        nonlocal total
        name=safe_name(name)
        if any(":" in part for part in PurePosixPath(name).parts):raise ValueError("unsafe_host_license_name")
        data.decode("utf-8")
        total+=len(data)
        if len(data)>32*1024*1024 or total>64*1024*1024:raise ValueError("license_text_bound")
        path=output/"files"/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        rows.append({"path":path.relative_to(output).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"origin":origin})
    for row in previous["notices"]:
        if row["status"]!="copied":continue
        source=FORMAL/row["path"];raw=source.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row["sha256"]:raise ValueError("prior_notice_changed")
        copy(row["image_path"].lstrip("/"),raw,{"kind":"original_layer_regular_text","image_path":row["image_path"],"layer":row["layer"]})
    logical={};pak=None;pak_layer=None
    for layer in manifest["layers"]:
        blob=base_oci/"blobs/sha256"/layer["digest"].removeprefix("sha256:")
        if blob.stat().st_size!=layer["size"]:raise ValueError("layer_size")
        with blob.open("rb") as stream:
            if hashlib.file_digest(stream,"sha256").hexdigest()!=layer["digest"].removeprefix("sha256:"):raise ValueError("layer_sha")
        with tarfile.open(blob,"r|gz") as archive:
            for member in archive:
                name=safe_name(member.name);p=PurePosixPath(name)
                if p.name==".wh..wh..opq":
                    logical={k:v for k,v in logical.items() if not k.startswith(str(p.parent)+"/")};continue
                if p.name.startswith(".wh."):
                    target=str(p.with_name(p.name[4:]));logical={k:v for k,v in logical.items() if k!=target and not k.startswith(target+"/")};continue
                select=(name.startswith(("usr/share/common-licenses/","usr/share/doc/libssl3/","usr/share/doc/libssl3t64/","usr/share/doc/openssl/"))
                    or name=="ms-playwright/chromium-1234/chrome-linux64/resources.pak")
                # 目录链接另入逻辑表，不在宿主建立symlink或junction。
                if member.issym() and name.startswith("usr/share/doc/"):
                    target=member.linkname.lstrip("/") if member.linkname.startswith("/") else posixpath.normpath(posixpath.join(str(p.parent),member.linkname))
                    logical[name]={"link":safe_name(target),"layer":layer["digest"]}
                if not select:continue
                if member.isfile():
                    if member.size>32*1024*1024:raise ValueError("selected_member_size")
                    raw=archive.extractfile(member).read();logical[name]={"data":raw,"layer":layer["digest"]}
                    if name.endswith("chrome-linux64/resources.pak"):pak=raw;pak_layer=layer["digest"]
                elif member.islnk():logical[name]={"link":safe_name(member.linkname.lstrip("/")),"layer":layer["digest"]}
    def resolve(name):
        visited=[]
        for _ in range(16):
            if name in visited:return None,visited
            visited.append(name);value=logical.get(name)
            if value is not None and "data" in value:return value,visited
            if value is not None and "link" in value:name=value["link"];continue
            parents=[key for key,value in logical.items() if "link" in value and name.startswith(key+"/")]
            if not parents:return None,visited
            key=max(parents,key=len);name=logical[key]["link"]+name[len(key):]
        return None,visited
    original_link="usr/share/doc/openssl/copyright";openssl,chain=resolve(original_link)
    for name in sorted(logical):
        if not name.startswith("usr/share/common-licenses/"):continue
        resolved,_=resolve(name)
        if resolved is not None:copy(name,resolved["data"],{"kind":"logical_image_regular_text","layer":resolved["layer"]})
    official=Path(openssl_text).read_bytes()
    if hashlib.sha256(official).hexdigest()!=OPENSSL_SHA:raise ValueError("official_openssl_text_sha")
    copy("upstream/openssl-3.0.13-LICENSE.txt",official,{"kind":"official_fixed_version_text","url":"https://raw.githubusercontent.com/openssl/openssl/openssl-3.0.13/LICENSE.txt","version":"3.0.13"})
    if pak is None:raise ValueError("main_chrome_pak_missing")
    main=output/"files/main-chrome-151.0.7922.34-CREDITS.txt";main.parent.mkdir(exist_ok=True)
    process=subprocess.run([shutil.which("node"),str(FORMAL/"license_resources.cjs"),str(main)],input=pak,capture_output=True,timeout=30)
    if process.returncode:raise ValueError("main_chrome_credits_extraction_failed")
    extracted=json.loads(process.stdout);total+=extracted["bytes"]
    if total>64*1024*1024:raise ValueError("license_total_limit")
    rows.append({"path":main.relative_to(output).as_posix(),"bytes":extracted["bytes"],"sha256":extracted["sha256"],"origin":{"kind":"main_chrome_generated_credits","image_path":"/ms-playwright/chromium-1234/chrome-linux64/resources.pak","layer":pak_layer,**extracted}})
    result={"schema":"retrolume.preview.license_materials.v3","method":"logical_target_and_main_chrome_pak_credits.v1","base_manifest":"sha256:"+BASE,
      "files":rows,"total_text_bytes":total,"openssl_original_link":{"chain":chain,"resolved_in_image":openssl is not None,"status":"dangling_original_link" if openssl is None else "resolved"},
      "coverage":{"main_chrome_actual_credits":True,"openssl_package_notice":"usr/share/doc/libssl3t64/copyright","openssl_official_license_3_0_13":True,"common_license_texts_included":True},
      "claims":"可核的实际版权原文和出处；保留原dangling事实，不裁定所有分发义务或许可兼容性"}
    (output/"inventory.json").write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2),encoding="utf-8")
    return result
