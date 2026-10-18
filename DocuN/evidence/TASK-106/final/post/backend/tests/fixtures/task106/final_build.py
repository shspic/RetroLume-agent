"""Third permitted build, justified by the actual saved-draft activity race."""
import hashlib,shutil,subprocess
from .control import ROOT,batch,atomic_json

def main():
    with batch('F03-final-immediate-panel-invalidation-build',category='offline_build',count='build',maximum=300) as out:
        shutil.copytree(ROOT/'frontend/dist',out/'pre-dist')
        command=['npm.cmd','run','build']
        with (out/'build-log.txt').open('w',encoding='utf-8') as stream:
            result=subprocess.run(command,cwd=ROOT/'frontend',stdout=stream,stderr=stream,timeout=290,creationflags=subprocess.CREATE_NO_WINDOW)
        assert result.returncode==0, 'Actual final build failed; output retained'
        files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()}
        atomic_json(out/'build-identity.json',dict(command=command,exit_code=result.returncode,dist=files,cause='P11 actual saved draft continuation POST before new detail arrived; invalidate at selection change'))
        print('Final build passed; source/dist identity retained')

if __name__=='__main__':main()
