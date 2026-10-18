"""定向离线批；每命令60秒，保存退出码/实际耗时/当前指纹。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[4]
BACKEND=ROOT/"backend"
EVID=ROOT/"Ndocu/evidence/task-085"

def hashes():
    paths=list((BACKEND/"app").rglob("*.py"))+list((BACKEND/"migrations").glob("*.sql"))
    paths+=list((BACKEND/"tests/fixtures/task085").glob("*.py"))
    paths += [BACKEND/"tests/test_worker_one_call.py",BACKEND/"tests/test_worker_session.py",BACKEND/"tests/test_capabilities.py"]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

if __name__=="__main__":
    tag=sys.argv[1]
    command=[sys.executable,"-B","-m","unittest","-v"]+sys.argv[2:]
    started=time.monotonic()
    before=hashes()
    env=os.environ.copy();env["PYTHONDONTWRITEBYTECODE"]="1"
    result=subprocess.run(command,cwd=BACKEND,env=env,capture_output=True,timeout=55)
    elapsed=time.monotonic()-started
    for label,raw in (("stdout",result.stdout),("stderr",result.stderr)):
        data=raw.decode("utf-8",errors="replace")
        for value in ("synthetic-secret-085","synthetic-body-085","synthetic-answer-085","synthetic-dsn"):
            data=data.replace(value,"[redacted-synthetic]")
        (EVID/f"{tag}-{label}.log").write_text(data,encoding="utf-8")
    (EVID/f"{tag}-meta.json").write_text(json.dumps(dict(command=command,exit=result.returncode,
        seconds=elapsed,utc=datetime.now(timezone.utc).isoformat(),as_run=before,post=hashes()),indent=2),encoding="utf-8")
    print(json.dumps(dict(tag=tag,exit=result.returncode,seconds=elapsed)))
    print((EVID/f"{tag}-stderr.log").read_text(encoding="utf-8")[-2500:])
    sys.exit(result.returncode)
