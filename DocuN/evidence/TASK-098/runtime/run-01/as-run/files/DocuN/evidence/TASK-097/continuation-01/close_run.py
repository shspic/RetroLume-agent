"""最终收尾原始stdout/stderr与计时，不启动业务资源。"""
from pathlib import Path
import subprocess,sys,time,json
C=Path(__file__).resolve().parent
out=C/'finalization-attempt-02';out.mkdir()
t=time.monotonic()
cmd=[sys.executable,'-B',str(C/'finalize.py')]
r=subprocess.run(cmd,capture_output=True,timeout=60)
(out/'stdout.bin').write_bytes(r.stdout);(out/'stderr.bin').write_bytes(r.stderr)
(out/'run.json').write_text(json.dumps({'command':cmd,'exit_code':r.returncode,'measured_seconds':time.monotonic()-t,'business_resources_started':0},ensure_ascii=False,indent=2),encoding='utf-8')
sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr)
raise SystemExit(r.returncode)
