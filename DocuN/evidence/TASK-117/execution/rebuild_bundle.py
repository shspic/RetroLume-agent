from control import *
import subprocess,shutil
guard();count('frontend_builds');attempt=state()['counts']['frontend_builds']
for path in (ROOT/'frontend/dist').rglob('*'):
    if path.is_file():
        backup=HERE/f'bundle-before-build-{attempt}'/path.relative_to(ROOT/'frontend/dist');backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(path.read_bytes())
r=subprocess.run([shutil.which('npm.cmd'),'run','build'],cwd=ROOT/'frontend',capture_output=True,timeout=120)
(HERE/f'build-{attempt}.txt').write_bytes(r.stdout+r.stderr)
if r.returncode:failure('final-bundle-build',r.stdout.decode('utf-8','replace')[-600:]);raise SystemExit(1)
write(HERE/f'bundle-{attempt}.json',{p.relative_to(ROOT).as_posix():{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()})
event('final_bundle_built',attempt=attempt);print('Final bundle '+str(attempt)+' built')
