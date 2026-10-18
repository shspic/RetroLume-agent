"""从锁定本地OCI按层覆盖关系收集发布自带的许可；不运行基础镜像。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path,PurePosixPath
import posixpath
import tarfile

BASE="c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac"


def collect(base_oci,output):
    base_oci=Path(base_oci).resolve();output=Path(output).resolve()
    formal=Path(__file__).resolve().parent
    if output.parent!=formal/"licenses" or output.exists():raise ValueError("new_formal_license_directory_required")
    manifest_bytes=(base_oci/"blobs/sha256"/BASE).read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest()!=BASE:raise ValueError("base_manifest_identity")
    manifest=json.loads(manifest_bytes);selected={};links={};scanned=[]
    for layer in manifest["layers"]:
        identifier=layer["digest"].removeprefix("sha256:");path=base_oci/"blobs/sha256"/identifier
        if path.stat().st_size!=layer["size"]:raise ValueError("base_layer_size")
        # 单个固定材料hash，不扫描旧任务的证据或源码。
        with path.open("rb") as stream:
            if hashlib.file_digest(stream,"sha256").hexdigest()!=identifier:raise ValueError("base_layer_identity")
        scanned.append({"digest":layer["digest"],"bytes":layer["size"]})
        with tarfile.open(path,mode="r|gz") as archive:
            for member in archive:
                name=member.name.removeprefix("./");p=PurePosixPath(name)
                if p.is_absolute() or ".." in p.parts:raise ValueError("unsafe_oci_member")
                if p.name==".wh..wh..opq":
                    selected={key:value for key,value in selected.items() if not key.startswith(str(p.parent)+"/")}
                    links={key:value for key,value in links.items() if not key.startswith(str(p.parent)+"/")};continue
                if p.name.startswith(".wh."):
                    target=str(p.with_name(p.name[4:]));selected={key:value for key,value in selected.items() if key!=target and not key.startswith(target+"/")}
                    links={key:value for key,value in links.items() if key!=target and not key.startswith(target+"/")};continue
                if member.issym() and name.startswith("usr/share/doc/"):
                    target=member.linkname.lstrip("/") if member.linkname.startswith("/") else posixpath.normpath(posixpath.join(str(p.parent),member.linkname))
                    if target.startswith("../"):raise ValueError("unsafe_license_link")
                    links[name]=target
                is_system=name.startswith("usr/share/doc/") and p.name=="copyright"
                basename=p.name.lower()
                is_notice=(basename in {"license","licence","copying","notice","copyright","thirdpartynotices.txt","third_party_notices.txt"}
                    or (basename.startswith(("license.","licence.","copying.","notice.")) and p.suffix.lower() not in {".js",".cjs",".mjs",".map",".h",".pak"}))
                is_runtime=is_notice and any(part in name.lower() for part in ("node","chrom","playwright","opt/"))
                if not (is_system or is_runtime):continue
                if member.isfile():
                    if member.size>32*1024*1024:raise ValueError("license_file_limit")
                    selected[name]={"data":archive.extractfile(member).read(),"layer":layer["digest"],"component":"system" if is_system else "runtime"}
                elif member.issym() or member.islnk():
                    target=member.linkname.lstrip("/") if member.islnk() or member.linkname.startswith("/") else posixpath.normpath(posixpath.join(str(p.parent),member.linkname))
                    if target.startswith("../"):raise ValueError("unsafe_license_link")
                    selected[name]={"link":posixpath.normpath(target),"layer":layer["digest"],"component":"system" if is_system else "runtime"}
                if len(selected)>1200:raise ValueError("license_count_limit")
    output.mkdir(parents=True);rows=[];total=0
    for name,item in sorted(selected.items()):
        resolved=item;visited=set()
        while "link" in resolved:
            target=resolved["link"]
            for _ in range(8):
                replacement=next((key for key in sorted(links,key=len,reverse=True) if target==key or target.startswith(key+"/")),None)
                if replacement is None:break
                target=links[replacement]+target[len(replacement):]
            if target in visited or target not in selected or len(visited)>8:resolved=None;break
            visited.add(target);resolved=selected[target]
        row={"image_path":"/"+name,"layer":item["layer"],"component":item["component"]}
        if resolved is None:row["status"]="unresolved_link"
        else:
            data=resolved["data"];total+=len(data)
            if total>64*1024*1024:raise ValueError("license_total_limit")
            destination=output/"files"/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
            row.update(status="copied",bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),path=str(destination.relative_to(formal)).replace("\\","/"))
        rows.append(row)
    vendor=formal/"vendor/playwright-core"
    notices=[]
    for name in ("LICENSE","NOTICE","ThirdPartyNotices.txt"):
        data=(vendor/name).read_bytes();notices.append({"path":"vendor/playwright-core/"+name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
    coverage={"node_core_notice":any(row["image_path"]=="/usr/share/doc/nodejs/copyright" and row["status"]=="copied" for row in rows),
        "browser_related_notice":any("chrom" in row["image_path"].lower() and row["status"]=="copied" for row in rows),
        "main_chrome_license_file":any("/chrome-linux64/" in row["image_path"] and "/WidevineCdm/" not in row["image_path"] and row["status"]=="copied" for row in rows),
        "unresolved_links":[row["image_path"] for row in rows if row["status"]!="copied"]}
    value={"schema":"retrolume.preview.license_inventory.v2","base_manifest":"sha256:"+BASE,"layers":scanned,"notices":rows,"vendor_notices":notices,
        "coverage":coverage,"claims":"发布材料自带许可的原字节清单，非许可兼容性或完整分发义务裁定"}
    (output/"inventory.json").write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2),encoding="utf-8")
    return value
