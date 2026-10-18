"""M6 unreliable representative on preserved own fault cluster, restores name."""
import asyncio,json,os,sys
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from uuid import uuid4
from datetime import datetime,timedelta,timezone
from .harness import Harness
from .samples import T_NAME
from .control import atomic_json
from .core import reject
from .harness import MODEL
from app.memory.contracts import MemoryCommandInput,MemorySelectionInput
from app.activities import ActivitySpec,SourceSnapshot

async def run(h):
    source=h.material(T_NAME);mid=str(uuid4())
    save=MemoryCommandInput.model_validate(dict(schema='memory.command.v1',business_key=str(uuid4()),memory_id=mid,expected_revision=0,action='save',body=dict(title='C01不可靠资格样本',text='明确虚构的文字偏好',kind='preference',capture=None)))
    await h.ledger.apply_memory_command(save)
    with psycopg.connect(h.dsn,row_factory=dict_row) as conn:
        m=conn.execute('SELECT h.revision,h.current_version,r.body_sha256 FROM learning_memories h JOIN learning_memory_revisions r ON r.memory_id=h.memory_id AND r.version=h.current_version WHERE h.memory_id=%s',(mid,)).fetchone()
    selection=MemorySelectionInput.model_validate(dict(confirmed=True,entries=[dict(memory_id=mid,version=m['current_version'],revision=m['revision'],body_sha256=m['body_sha256'])]))
    aid=str(uuid4())
    await h.ledger.create_activity(ActivitySpec(activity_id=aid,sources=(SourceSnapshot(source['id'],source['version_id'],source['revision']),),deadline_at=datetime.now(timezone.utc)+timedelta(hours=2),max_requests=10,max_cost_microunits=10000,reserve_cost_microunits=100,max_request_bytes=65536,max_output_tokens=1024,max_running_seconds=3600,allowed_models=(('deepseek_chat_completions',MODEL),),max_tool_calls=0),memory_selection=selection)
    before=h.snapshot(aid);before_view=await h.ledger.read_interview_workspace(aid);assert before_view['memory']['selected'] and before_view['memory']['eligible']
    with psycopg.connect(h.admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.learning_memories RENAME TO c01_preserved_learning_memories')
    try:
        state=await h.ledger._transaction(h.ledger._memory_schema_info);assert state not in ('ready','legacy'),state
        view=await h.ledger.read_interview_workspace(aid);assert not view['memory']['eligible']
        code=await reject(lambda:h.command(aid,'start',{'goal':None}),{'interview_memory_dependency_invalid'})
        assert h.snapshot(aid)==before
        atomic_json(h.out/'M6-unreliable-new-domain-refusal.json',dict(activity=aid,memory=mid,selection=selection.model_dump(),state=state,ordinary_role=True,before_view=before_view,view=view,code=code,before=before,after=h.snapshot(aid),no_SUP_or_memory_fallback=True))
    finally:
        with psycopg.connect(h.admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.c01_preserved_learning_memories RENAME TO learning_memories')
    assert await h.ledger._transaction(h.ledger._memory_schema_info)=='ready'
    assert await h.ledger._transaction(h.ledger._interview_schema_info)=='ready'
    atomic_json(h.out/'M6-S1-restored.json',dict(M6='ready',S1='ready',no_DDL_source_or_ACL_change=True,no_drop_delete=True))

if __name__=='__main__':
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    out=Path(os.environ['C01_OUT']);asyncio.run(run(Harness(os.environ['C01_ADMIN_DSN'],os.environ['C01_APP_DSN'],out)))
