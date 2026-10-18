"""权限边界停止后只核已有数据、ROLLBACK拒绝和未知预扣，不再生成或启动。"""
import asyncio,json,time
from uuid import uuid4
import psycopg
from .control import CONTINUE_ROOT,atomic
from .core import Harness
from .c03_matrix import plan,aid_for
from app.runtime import psycopg_compatible_loop_factory

async def checks(resource,built,out):
    from app.memory.service import MemoryService
    from app.memory.contracts import MemoryCommandInput
    h=Harness(resource,built,out,registry_dir=(CONTINUE_ROOT/'synthetic/read-only-final-control').resolve())
    try:
        mid=plan()['objects']['race_memory']['memory_id'];view=await h.ledger.read_memory_snapshot(mid)
        selection_before=await h.ledger.read_memory_selection(aid_for('race_memory'))
        head=await h.ledger.read_teaching_head(aid_for('race_memory'));assert head['exercise_record_id']
        if selection_before['eligible']:
            impact=await h.ledger.preview_memory_change(mid,view['revision'],'revise')
            await MemoryService(h.ledger).submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=view['revision'],action='revise',body={'kind':'self_report','title':'C03 保留旧版的合成修订','text':'仅核背景失效的持久事实，不宣帧竞态通过','base_body_sha256':view['body_sha256'],'impact_token':impact['impact_token']}))
        else:assert view['version']>=2
        after=await h.ledger.read_memory_selection(aid_for('race_memory'));assert not after['eligible']
        with psycopg.connect(resource['app']) as conn:
            retained=conn.execute('SELECT count(*) FROM learning_memory_bodies WHERE memory_id=%s',(mid,)).fetchone()[0]
        assert retained>=2
        head=json.loads(json.dumps(head,default=str))
        atomic(out/'memory-v2-parent-and-change-limited.json',{'status':'PASS_MEMORY_SELECTED_PARENT_AND_COMMITTED_CHANGE_ONLY','activity_id':aid_for('race_memory'),'head':head,
          'before_selection':selection_before,'after_selection':after,'old_memory_bodies_retained':retained,'prior_commit_reused':not selection_before['eligible'],
          'frame_or_HTML_artifact_qualification':'NOT_RUN_42501_HTML_OWNER_PDF_READ_BOUNDARY','no_new_privileges':True})
    finally:await h.controller.close()

def run(resource,built,out):
    effects=[];artifact=json.loads((CONTINUE_ROOT/'root-10/step-08-probe/phase-a-result.json').read_text(encoding='utf-8'))['item']['receipt']['artifact_id']
    for role in ('app','denied'):
        with psycopg.connect(resource[role]) as conn:
            for operation,query in (('update',"UPDATE html_artifacts SET artifact_sha256=repeat('0',64) WHERE artifact_id=%s"),('delete','DELETE FROM html_artifacts WHERE artifact_id=%s')):
                try:conn.execute(query,(artifact,))
                except psycopg.Error as error:effects.append({'role':role,'operation':operation,'sqlstate':error.sqlstate});assert error.sqlstate=='42501'
                else:raise AssertionError('artifact direct DML unexpectedly allowed')
                finally:conn.rollback()
    with psycopg.connect(resource['app']) as conn:
        unknown=conn.execute("SELECT state,reserve_seconds,elapsed_seconds FROM html_preview_sessions WHERE preview_id=%s",('542b0750-6e02-418a-b216-5dfbd3b93047',)).fetchone()
        budget=conn.execute('SELECT starts_used,reserved_seconds,settled_seconds FROM html_preview_budgets WHERE activity_id=%s',(plan()['objects']['fault_node_busy']['activity_id'],)).fetchone()
    assert unknown==('cleanup_unconfirmed',60,None) and budget[0]==1 and budget[1]==60
    atomic(out/'permissions-and-unknown-final.json',{'status':'PASS_PERMISSION_REJECTIONS_AND_UNKNOWN_FULL_RESERVE','effects':effects,'unknown_session':unknown,'unknown_budget':budget,
      'commit_delete':False,'renderer_starts_added':0,'HTML_owner_permissions_expanded':False})
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(checks(resource,built,out))
