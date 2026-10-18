"""定界新方法：只定位旧未解链接与主Chrome版权资源，不重跑旧collector。"""
import hashlib,json,posixpath,tarfile,time
from pathlib import Path
from .control import ROOT,CONTINUE_ROOT,atomic,batch,phase


def main():
    phase("implementation_offline");folder=CONTINUE_ROOT/"license-logical-probe";folder.mkdir(exist_ok=False)
    inventory=json.loads((ROOT/"deploy/preview/licenses/base-c091b21d-v2-final/inventory.json").read_text(encoding="utf-8"))
    targets={r["layer"] for r in inventory["notices"] if "openssl/" in r["image_path"] or "libssl3t64/" in r["image_path"] or "/chrome-linux64/" in r["image_path"]}
    oci=ROOT/"deploy/preview/task109-c01-cache/oci";manifest=json.loads((oci/"blobs/sha256/c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac").read_bytes());rows=[];texts={}
    with batch("offline","c02-qualified-logical-link-license-probe",maximum=300):
        for layer in manifest["layers"]:
            if layer["digest"] not in targets:continue
            blob=oci/"blobs/sha256"/layer["digest"].split(":")[1]
            with blob.open("rb") as stream:
                if hashlib.file_digest(stream,"sha256").hexdigest()!=layer["digest"].split(":")[1]:raise RuntimeError("OCI fixed layer changed")
            with tarfile.open(blob,"r|gz") as archive:
                for member in archive:
                    name=member.name.lstrip("./");lower=name.lower()
                    selected=(lower.startswith(("usr/share/doc/openssl","usr/share/doc/libssl3t64")) or
                       ("/chrome-linux64/" in lower and (any(term in lower for term in ("license","notice","credits","about")) or lower.endswith("resources.pak"))))
                    if not selected:continue
                    rows.append({"name":name,"raw_name":member.name,"type":member.type.decode("ascii"),"link":member.linkname,"bytes":member.size,"layer":layer["digest"]})
                    if member.isfile() and member.size<=32*1024*1024 and ("/usr/share/doc/" in "/"+lower or lower.endswith("resources.pak") or "credits" in lower or "license" in lower):
                        raw=archive.extractfile(member).read();destination=folder/"selected"/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
                        texts[name]={"path":str(destination),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
        atomic(folder/"logical-members.json",rows);atomic(folder/"selected-files.json",texts)
        print(json.dumps({"members":rows,"selected_files":texts},ensure_ascii=True))


if __name__=="__main__":main()
