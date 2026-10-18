"""M6 unreliable representative on preserved own fault cluster, restores name."""
import asyncio,json,os,sys
from pathlib import Path
import psycopg
from .harness import Harness
from .samples import T_NAME
from .control import atomic_json
from .core import reject

async def run(h):
    h.material(T_NAME);aid=await h.activity([T_NAME]);before=h.snapshot(aid)
    with psycopg.connect(h.admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.learning_memories RENAME TO c01_preserved_learning_memories')
    try:
        state=await h.ledger._transaction(h.ledger._memory_schema_info);assert state not in ('ready','legacy'),state
        view=await h.ledger.read_interview_workspace(aid);assert not view['memory']['eligible']
        code=await reject(lambda:h.command(aid,'start',{'goal':None}),{'interview_memory_dependency_invalid'})
        assert h.snapshot(aid)==before
        atomic_json(h.out/'M6-unreliable-new-domain-refusal.json',dict(activity=aid,state=state,ordinary_role=True,view=view,code=code,before=before,after=h.snapshot(aid),no_SUP_or_memory_fallback=True))
    finally:
        with psycopg.connect(h.admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.c01_preserved_learning_memories RENAME TO learning_memories')
    assert await h.ledger._transaction(h.ledger._memory_schema_info)=='ready'
    assert await h.ledger._transaction(h.ledger._interview_schema_info)=='ready'
    atomic_json(h.out/'M6-S1-restored.json',dict(M6='ready',S1='ready',no_DDL_source_or_ACL_change=True,no_drop_delete=True))

if __name__=='__main__':
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    out=Path(os.environ['C01_OUT']);asyncio.run(run(Harness(os.environ['C01_ADMIN_DSN'],os.environ['C01_APP_DSN'],out)))
