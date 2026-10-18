"""已制齐运行方法的语法、身份和只读精确资源预检，不占真实根。"""
import ast,hashlib,json,subprocess,time
from .control import ROOT,CONTINUE_ROOT,EVIDENCE,CONTINUATION,atomic,batch,phase,read_state,source_snapshot,registry_root,CAPS
from .resources import DOCKER,shell_env
from app.preview.process import GlobalOwner

def main():
    out=CONTINUE_ROOT/'prepared';out.mkdir(exist_ok=False);phase('implementation_offline')
    with batch('offline','C07 frozen real harness identity and exact resource preflight',maximum=(read_state()['business_deadline_ns']-time.monotonic_ns())/1e9):
        assert CONTINUATION=='TASK-111-G11-C07-20261012'
        prior=json.loads((EVIDENCE/'continuation-06/final/source-identity.json').read_text(encoding='utf-8'))
        allowed={'backend/app/preview/production_supervisor.py','backend/app/preview/pipe.py','deploy/preview/renderer-protocol.cjs','backend/tests/fixtures/task111/control.py','backend/tests/fixtures/task111/core.py'}
        changes=[]
        for row in prior:
            actual=hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()
            if actual!=row['sha256']:assert row['path'] in allowed;changes.append(dict(path=row['path'],before=row['sha256'],after=actual))
        assert len(changes)==5
        for p in (ROOT/'backend/tests/fixtures/task111').glob('c07*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
        for name in ('renderer-protocol.cjs','renderer-host.cjs'):
            r=subprocess.run(['node','--check',str(ROOT/'deploy/preview'/name)],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
            assert r.returncode==0
        previous=json.loads((EVIDENCE/'continuation-06/final/exact-resources-final.json').read_text(encoding='utf-8'))
        fmt='{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"restart_count":{{json .RestartCount}}}'
        r=subprocess.run([DOCKER,'inspect','--format',fmt,*[x['id'] for x in previous['objects']]],capture_output=True,timeout=15,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        (out/'preflight-inspect.stdout.bin').write_bytes(r.stdout);(out/'preflight-inspect.stderr.bin').write_bytes(r.stderr);assert r.returncode==0
        objects=[json.loads(line) for line in r.stdout.splitlines()];assert objects==previous['objects'] and len(objects)==40
        mutex=GlobalOwner('Global\\RetroLumePreviewV2Task111')
        try:assert mutex.acquire()=='acquired';global_identity=mutex.identity()
        finally:mutex.close()
        atomic(out/'source-delta-from-C06.json',dict(old_count=len(prior),changes=changes,unmodified_count=len(prior)-len(changes),forbidden_files_unchanged=True))
        atomic(out/'preflight.json',dict(status='PASS_C07_FROZEN_HARNESS_AND_STOPPED_40_OBJECTS',objects=objects,global_exclusive=global_identity,
            registry=str(registry_root()),counts=read_state()['counts'],hard_caps=CAPS,real_starts=0))
        source_snapshot(out)
    print('PASS_C07_FROZEN_REAL_HARNESS_PREFLIGHT')

if __name__=='__main__':main()
