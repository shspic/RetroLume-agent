"""本卡剩余方法制齐后的定向离线批，不启动真实资源。"""
import ast,hashlib,json
from .control import ROOT,CONTINUE_ROOT,batch,atomic,run,source_snapshot,phase

def main():
    phase("implementation_offline");folder=CONTINUE_ROOT/"prepared-offline";folder.mkdir(exist_ok=False)
    with batch("offline","C03-final-assembly-protocol-finite-limit-and-UI-build",maximum=600):
        source_snapshot(folder)
        for p in (ROOT/"backend/tests/fixtures/task111").glob("c03*.py"):ast.parse(p.read_text(encoding="utf-8"))
        from .samples import energy
        from .c03_samples import limited
        from app.preview.compiler import runtime_html,runtime_identity
        from app.preview.description import validate_description
        data={"energy":energy(),"limited":limited("lc_synthetic_energy"),"renderer":runtime_identity()["renderer_sha256"],"out":str(folder)}
        validate_description(data["limited"],["lc_synthetic_energy"]);atomic(folder/"boundary-input.json",data)
        run(["node",str(ROOT/"frontend/tests/task111/c03_assembly.cjs"),str(folder)],folder,maximum=30,name="final-assembly")
        assert (folder/"actual-production.html").read_bytes()==runtime_html().encode()
        run(["node",str(ROOT/"frontend/tests/task111/c03_boundaries.cjs"),str(folder/"boundary-input.json")],folder,maximum=30,name="host-boundaries")
        for name in ("renderer-host.cjs","renderer-assembly.cjs","renderer-protocol.cjs"):
            run(["node","--check",str(ROOT/"deploy/preview"/name)],folder,maximum=10,name="syntax-"+name)
        run(["node","--check",str(ROOT/"frontend/tests/task111/c03_ui.cjs")],folder,maximum=10,name="syntax-main-ui")
        atomic(folder/"prepare-result.json",{"status":"PASS_CHANGED_OFFLINE_BOUNDARIES","browser_pass":False,"frontend_build":"deferred to real root"})
    print("C03 preparation passed")

if __name__=="__main__":main()
