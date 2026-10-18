"""仅修复已发现的版权目录别名与notice分类，不重跑业务或构建。"""
from __future__ import annotations
import ast
import importlib.util
from .control import ROOT,EVIDENCE,batch,atomic,event


def main(folder_name="offline-04",output_name="base-c091b21d-v2-repair"):
    folder=EVIDENCE/folder_name;folder.mkdir(exist_ok=False)
    with batch("offline","license-alias-notice-classification-repair",maximum=180):
        source=ROOT/"deploy/preview/collect_licenses.py";ast.parse(source.read_text(encoding="utf-8"))
        spec=importlib.util.spec_from_file_location("task111_license_repair",source)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        output=ROOT/"deploy/preview/licenses"/output_name
        inventory=module.collect(ROOT/"deploy/preview/task109-c01-cache/oci",output)
        assert not any(row["image_path"].endswith(".js") for row in inventory["notices"])
        assert next(row for row in inventory["notices"] if row["image_path"]=="/usr/share/doc/openssl/copyright")["status"]=="copied"
        assert inventory["coverage"]["node_core_notice"]
        atomic(folder/"result.json",{"status":"PASS_NOTICE_COPY_ONLY","notices":len(inventory["notices"]),"coverage":inventory["coverage"],
             "runtime_starts":0,"full_license_review":False})
        atomic(ROOT/"deploy/preview/licenses/current.json",{"inventory":output_name+"/inventory.json","base_manifest":inventory["base_manifest"],
             "coverage":inventory["coverage"],"full_license_review":False})
        event("license_repair_complete",{"folder":str(folder),"coverage":inventory["coverage"]})


if __name__=="__main__":main()
