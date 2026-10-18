"""最后同卡组合root的有限步骤入口；外层固定截止不因修正后移。"""
from __future__ import annotations
import asyncio
import importlib
import json
import os
from pathlib import Path
import time
import traceback
from .control import EVIDENCE,batch,atomic,event,source_snapshot,state
from .core import install_environment
from . import resources


def main():
    install_environment();folder=EVIDENCE/"real-06";folder.mkdir(exist_ok=False);resource=None
    with batch("real","v2-final-combined-known-permission-repair",3600):
        source_snapshot(folder)
        try:
            resource=resources.pg_resume(folder);built=json.loads((EVIDENCE/"real-01/production-build.json").read_text(encoding="utf-8"))
            from app.runtime import psycopg_compatible_loop_factory
            step=0
            atomic(folder/"loop-ready.json",{"pid":os.getpid(),"deadline_ns":state()["active_batch"]["deadline_ns"],"allowed":["native","http","stop"]})
            while time.monotonic_ns()<state()["active_batch"]["deadline_ns"]:
                path=folder/("step-"+str(step+1).zfill(2)+".json")
                if not path.exists():time.sleep(.1);continue
                command=json.loads(path.read_text(encoding="utf-8"));step+=1
                if command.get("action")=="stop":break
                out=folder/("attempt-"+str(step).zfill(2));out.mkdir(exist_ok=False);source_snapshot(out)
                try:
                    if command["action"]=="native":
                        module=importlib.import_module("tests.fixtures.task111.native_matrix")
                        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(module.verify(resource,built,out))
                    elif command["action"]=="http":
                        module=importlib.import_module("tests.fixtures.task111.complete_matrix")
                        module.verify(resource,built,out,command["native_results"])
                    else:raise ValueError("unsupported bounded step")
                    atomic(out/"step-result.json",{"status":"PASS_STEP_ONLY","action":command["action"],"at_ns":time.monotonic_ns()})
                except Exception:
                    (out/"failure.txt").write_text(traceback.format_exc(),encoding="utf-8")
                    atomic(out/"step-result.json",{"status":"FAIL","action":command["action"],"at_ns":time.monotonic_ns()})
                    event("step_failure",{"action":command["action"],"step":step,"raw":str(out/"failure.txt")})
                # 同批下个步骤须新原件和相关修改；不得重置任何子计数。
        finally:
            if resource is not None:resources.stop_pg(folder)


if __name__=="__main__":main()
