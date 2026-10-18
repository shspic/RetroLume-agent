from control import ROOT,HERE,state,pre,count,event,write,sha,failure,end_root
import os,subprocess,json,shutil
if state()['active_root']!=3:raise RuntimeError('root_identity')
env=dict(os.environ);env['PYTHONPATH']=str(ROOT/'backend')
r=subprocess.run([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8','-m','unittest','discover','-s','backend/tests','-p','test_step018_flows.py','-v'],cwd=ROOT,env=env,capture_output=True,timeout=30)
(HERE/'root03-flow-contracts.txt').write_bytes(r.stdout+r.stderr)
if r.returncode:raise RuntimeError('flow_contracts_failed')
for path in (ROOT/'frontend/dist').rglob('*'):
    if path.is_file():pre(path.relative_to(ROOT).as_posix())
count('frontend_builds')
r=subprocess.run([shutil.which('npm.cmd'),'run','build'],cwd=ROOT/'frontend',capture_output=True,timeout=120)
(HERE/'root03-build.txt').write_bytes(r.stdout+r.stderr)
if r.returncode:failure('ROOT03-build',r.stdout.decode('utf-8','replace')[-700:]);raise RuntimeError('build_failed')
manifest={str(p.relative_to(ROOT)):{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()}
write(HERE/'root03-bundle.json',manifest)
write(HERE/'root03-check.json',{'typescript_and_bundle_build':'passed','flow_contract_methods':4,'first_flow_fixture_error_preserved':'request_body method name corrected to canonical_request_body; expected old omission unchanged','bundle_files':len(manifest)})
event('root03_bundle_ready',files=len(manifest),tests=4)
end_root(result='Final TypeScript/build + 4 new profile/canonical/restore-owner assertions passed; original fixture failures retained')
print('Final bundle built; four new contract assertions passed; ROOT03 stopped')
