"""One final production build with the preceding dist kept intact."""
import hashlib,shutil,subprocess
from .control import ROOT,batch,atomic_json

def main():
    with batch('F01-history-reconcile-cancel-final-build',category='offline_build',count='build',maximum=300) as out:
        shutil.copytree(ROOT/'frontend/dist',out/'pre-dist')
        with (out/'build.log').open('w',encoding='utf-8') as stream:
            result=subprocess.run(['npm.cmd','run','build'],cwd=ROOT/'frontend',stdout=stream,stderr=stream,timeout=290,creationflags=subprocess.CREATE_NO_WINDOW)
        assert result.returncode==0,'C01 actual build failed; full output saved'
        files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()}
        atomic_json(out/'build-identity.json',dict(command=['npm.cmd','run','build'],exit_code=result.returncode,dist=files,production_scope='final current interview/UI guards and read metadata'))
        print('C01 final source build passed')

if __name__=='__main__':main()
