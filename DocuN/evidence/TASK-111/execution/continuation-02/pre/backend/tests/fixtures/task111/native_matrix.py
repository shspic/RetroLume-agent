"""同卡夹具修正后复用现镜像/专库，核真实四次原生受控提交。"""
from __future__ import annotations
import asyncio
import json
from .control import EVIDENCE,batch,atomic,event,source_snapshot
from .core import Harness,install_environment
from . import resources


async def verify(resource,built,folder):
    h=Harness(resource,built,folder)
    try:
        aid,parent=await h.parent("energy");energy,command=await h.generate(aid,parent,"机械能计算与柱形图")
        assert energy["terminal_disposition"]=="succeeded",energy
        aid2,parent2=await h.parent("binomial");probability,command2=await h.generate(aid2,parent2,"二项概率与分布图")
        assert probability["terminal_disposition"]=="succeeded",probability
        invalid,_=await h.generate(aid,parent,"INVALID 机械能输出含非法HTML")
        assert invalid["terminal_disposition"]=="invalid_output" and invalid["artifact_id"] is None,invalid
        unknown,_=await h.generate(aid2,parent2,"UNKNOWN 二项概率传输失联")
        assert unknown["terminal_disposition"]=="unknown" and unknown["artifact_id"] is None,unknown
        value={"energy":{"activity_id":aid,"parent":parent,"receipt":energy,"command":command.model_dump()},
               "binomial":{"activity_id":aid2,"parent":parent2,"receipt":probability,"command":command2.model_dump()},
               "invalid":invalid,"unknown":unknown,"classification":"real native SUP/OneCall/PG with synthetic transport; no renderer or provider quality verdict"}
        atomic(folder/"native-results.json",value);event("native_matrix_pass",value)
    finally:await h.controller.close()


def main():
    install_environment()
    from .control import state
    folder=EVIDENCE/("real-"+str(state()["counts"]["real_batches"]+1).zfill(2));folder.mkdir(exist_ok=False);resource=None
    with batch("real","short-query-repair-native-commit",3600):
        source_snapshot(folder)
        try:
            resource=resources.pg_resume(folder);resources.restore_fixture_acl(resource,folder);built=json.loads((EVIDENCE/"real-01/production-build.json").read_text(encoding="utf-8"))
            from app.runtime import psycopg_compatible_loop_factory
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(verify(resource,built,folder))
        finally:
            if resource is not None:resources.stop_pg(folder)


if __name__=="__main__":main()
