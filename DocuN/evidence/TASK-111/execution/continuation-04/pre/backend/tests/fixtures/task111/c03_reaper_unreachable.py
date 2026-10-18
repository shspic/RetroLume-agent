"""专用控制路径失联夹具，执行真实Reaper但在绑定后拒绝其限定Docker调用。"""
import json,sys
from pathlib import Path

def main():
    from .control import CONTINUE_ROOT
    from app.preview import docker_control,production_reaper
    registry=Path(sys.argv[1]).resolve()
    if not registry.is_relative_to((CONTINUE_ROOT/"synthetic/fault-control").resolve()) or registry.name!="registry.json":raise RuntimeError("fixed test reaper scope")
    original=docker_control.call
    def unavailable(docker,args,timeout=2):
        if registry.with_name("control-unreachable.flag").exists():raise docker_control.DockerUnknown("fixed_test_control_path_unavailable")
        return original(docker,args,timeout)
    docker_control.call=unavailable
    return production_reaper.main()

if __name__=="__main__":raise SystemExit(main())
