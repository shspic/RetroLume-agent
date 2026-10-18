"""只在原C04唯一控制根，绑定后令本对象真实Reaper控制路径失联。"""
import sys
from pathlib import Path
def main():
    from .control import registry_root
    from app.preview import docker_control,production_reaper
    registry=Path(sys.argv[1]).resolve()
    if registry.parent.parent!=registry_root().resolve() or registry.name!='registry.json':raise RuntimeError('fixed C05 reaper scope')
    original=docker_control.call
    def unavailable(docker,args,timeout=2):
        if registry.with_name('control-unreachable.flag').exists():raise docker_control.DockerUnknown('fixed_test_control_path_unavailable')
        return original(docker,args,timeout)
    docker_control.call=unavailable
    return production_reaper.main()
if __name__=='__main__':raise SystemExit(main())
