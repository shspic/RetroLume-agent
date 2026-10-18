"""Preserve passed P05 windows; finish native diagnostic and remaining chain."""
import asyncio,json,sys
from .control import EVIDENCE,batch,atomic_json
from .resources import start,stop,runtime
from .core import Harness
from .windows import verify


async def resume(h):
    previous=json.loads((EVIDENCE/'runs/P05-exact-windows-atomic-unknown-safe-retry/marked_before_result.json').read_text(encoding='utf-8'))
    aid=previous['aid'];key=previous['receipt']['business_key'];before=h.snapshot(aid)
    receipt=await h.ledger.finish_interview_supervision(aid,key,{'state':'settled','definitely_not_admitted':False})
    after=h.snapshot(aid)
    atomic_json(h.out/'original-dispatched-native-unknown-reconciliation.json',dict(before=before,after=after,receipt=receipt,
        stop_basis='P05 actual native-session settled/active_processes_at_end0/reserved_seconds0 and retained stopped pg1; no new stop identity or refund'))
    assert after['operations'][0]['state']=='unknown' and not after['results'] and after['activity']['requests_reserved']==before['activity']['requests_reserved']==1,after
    # New precise third window proves the actual corrected lifecycle, not only old diagnostic repair.
    await verify(h,stages=('marked_before_result','committed_before_repair'))


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with batch('P06-resume-late-diagnostic-atomic-and-retry') as out:
        try:
            admin=start(1);app,denied=runtime(admin);h=Harness(admin,app,out)
            asyncio.run(resume(h))
        finally:stop(1)


if __name__=='__main__':main()
