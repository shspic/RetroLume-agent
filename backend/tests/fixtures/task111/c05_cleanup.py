"""已结束真实根之后，只恢复本轮未创建对象与精确清场，禁止新业务。"""
import asyncio,json,time
from .control import CONTINUE_ROOT,EVIDENCE,ROOT,atomic,batch,phase,read_state,locked,event,source_snapshot
from .resources import pg_resume
from .c03_resources import cleanup
from .core import Harness
from .c05_step import data
from app.runtime import psycopg_compatible_loop_factory

async def recover_only(resource,built,out):
    h=Harness(resource,built,out)
    try:
        await h.controller.recover();assert not h.controller.blocked,'未创建对象持久恢复仍未知'
        pointer=json.loads(h.controller.current_file.read_text(encoding='utf-8'));folder=__import__('pathlib').Path(pointer['folder']);reg=json.loads((folder/'registry.json').read_text(encoding='utf-8'))
        row=await h.ledger.read_html_preview(reg['activity_id'],reg['preview_id']);assert row['state']=='failed_unstarted' and row['elapsed_seconds']==row['reserve_seconds'] and row['reserved_seconds']==0
        atomic(out/'never-created-full-R-recovery.json',dict(pointer=pointer,row=row,proof=json.loads((folder/'recovery-proof.json').read_text(encoding='utf-8')),no_preview_create_or_start=True))
    finally:await h.controller.close()

def main():
    out=CONTINUE_ROOT/'cleanup-only';out.mkdir();start=time.monotonic_ns();resource=None;phase('cleanup')
    try:
        with batch('cleanup','C05 unfinished uncreated row persistent recovery only',maximum=150):
            resource=pg_resume(out);built=json.loads((CONTINUE_ROOT/'active-build.json').read_text(encoding='utf-8'));source_snapshot(out)
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(recover_only(resource,built,out))
            data(resource,out)
    finally:
        cleanup(out)
        # 本独立清场的PG恢复/持有整段仍计真实资源时间，不形成新业务根或延原deadline。
        elapsed=(time.monotonic_ns()-start)/1e9
        with locked():
            b=read_state();b['time_seconds']['real']+=elapsed;atomic(EVIDENCE/'budget.json',b)
        event('C05_cleanup_only_PG_hold_real_accounted',dict(seconds=elapsed,new_business_roots=0,new_preview_creates=0,new_preview_starts=0),cleanup=True);phase('implementation_offline')

if __name__=='__main__':main()
