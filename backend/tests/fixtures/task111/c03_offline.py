"""只补实际生产组装与跨语言编译包缺口，不重跑未变的旧矩阵。"""
import ast,hashlib,json,subprocess,time
from .control import ROOT,CONTINUE_ROOT,batch,atomic,phase,source_snapshot,run

def main():
    phase("implementation_offline")
    folder=CONTINUE_ROOT/"assembly-offline";folder.mkdir(exist_ok=False)
    with batch("offline","C03-real-production-assembly",maximum=300):
        source_snapshot(folder)
        for name in ("control.py","core.py","c03_init.py","c03_offline.py"):
            ast.parse((ROOT/"backend/tests/fixtures/task111"/name).read_text(encoding="utf-8"))
        run(["node",str(ROOT/"frontend/tests/task111/c03_assembly.cjs"),str(folder)],folder,maximum=30,name="node-production-assembly")
        from app.preview.compiler import runtime_html,compile_description
        from .samples import energy
        from app.preview.description import canonical
        html=runtime_html().encode("utf-8");actual=(folder/"actual-production.html").read_bytes()
        assert actual==html,"actual Node production HTML differs from Python"
        package=compile_description(energy(),["lc_synthetic_energy"])
        assert package["compiled_html"].encode("utf-8")==actual
        atomic(folder/"assembly-result.json",{"status":"PASS_PRODUCTION_BYTES_AND_PYTHON_PACKAGE","script_bytes":(ROOT/"deploy/preview/runtime.cjs").stat().st_size,
          "html_bytes":len(actual),"html_sha256":hashlib.sha256(actual).hexdigest(),"compiled_package_sha256":hashlib.sha256(canonical(package).encode()).hexdigest(),
          "browser_execution":False,"existing_runtime_identity_unchanged":True})
    print((folder/"assembly-result.json").read_text(encoding="utf-8"))

if __name__=="__main__":main()
