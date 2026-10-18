from pathlib import Path
import subprocess,os,sys
ROOT=Path(__file__).resolve().parents[4]
for p in (ROOT/'backend/tests/fixtures/task097').glob('*.py'):compile(p.read_bytes(),str(p),'exec')
r=subprocess.run(['node',str(ROOT/'frontend/tests/task097-continuation.mjs')],env={**os.environ,'RETROLUME_TASK097_PREFLIGHT':'1'},capture_output=True)
sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr)
raise SystemExit(r.returncode)
