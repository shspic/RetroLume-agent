from control import *
from runtime_control import docker,memory_gate,PG_IMAGE
import os,subprocess
guard();docker(['image','inspect',PG_IMAGE]);memory_gate('final-bundle-browser');count('browser_starts')
attempt=state()['counts']['browser_starts']
env=dict(os.environ);env.update(RETROLUME_TASK117_EVIDENCE=str(HERE),RETROLUME_TASK117_BROWSER_ATTEMPT=str(attempt))
event('browser_attempt',attempt=attempt,final_dist=True)
r=subprocess.run(['node',str(ROOT/'frontend/tests/step018-flow.mjs')],cwd=ROOT/'frontend',env=env,capture_output=True,timeout=600)
(HERE/f'browser-{attempt}-output.txt').write_bytes(r.stdout+r.stderr)
event('browser_finished',attempt=attempt,exit_code=r.returncode,child_wait_confirmed=True)
if r.returncode:failure('ROOT04-browser',r.stderr.decode('utf-8','replace')[-600:]);print(r.stderr.decode('utf-8','replace')[-800:]);raise SystemExit(1)
print('Final bundle two browser chains passed')
