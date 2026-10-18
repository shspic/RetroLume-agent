"""未知停止封新预览后，只完成不依赖新资源的事务、资格和文件边界核对。"""
import asyncio,ctypes,hashlib,json,threading,time
from ctypes import wintypes
from uuid import uuid4
import psycopg
from .control import CONTINUE_ROOT,atomic
from .core import Harness
from .c01_seeds import teaching_parent,diagnostic_artifact
from .c03_matrix import aid_for,plan
from app.preview.process import atomic_json
from app.preview.business_contracts import HtmlRefusal
from app.runtime import psycopg_compatible_loop_factory

def filesystem(out):
    api=ctypes.WinDLL('kernel32',use_last_error=True)
    api.CreateFileW.argtypes=(wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE);api.CreateFileW.restype=wintypes.HANDLE
    api.CloseHandle.argtypes=(wintypes.HANDLE,)
    target=out/'atomic-reader-boundary.json';atomic_json(target,{'version':1})
    def held():
        handle=api.CreateFileW(str(target),0x80000000,1,None,3,0,None)
        if handle==ctypes.c_void_p(-1).value:raise RuntimeError('own fixture reader handle')
        return handle
    handle=held();result={};started=time.monotonic()
    def writer():
        try:atomic_json(target,{'version':2});result['status']='published'
        except Exception as error:result['error_type']=type(error).__name__
    thread=threading.Thread(target=writer);thread.start();time.sleep(.03);api.CloseHandle(handle);thread.join(1)
    assert not thread.is_alive() and result.get('status')=='published' and json.loads(target.read_text(encoding='utf-8'))['version']==2
    transient=time.monotonic()-started;handle=held();started=time.monotonic()
    try:
        try:atomic_json(target,{'version':3})
        except PermissionError:permanent='bounded_permission_error'
        else:raise AssertionError('persistent reader sharing denial not reported')
    finally:api.CloseHandle(handle)
    elapsed=time.monotonic()-started;assert elapsed<.3 and json.loads(target.read_text(encoding='utf-8'))['version']==2
    atomic(out/'atomic-filesystem-result.json',{'status':'PASS_REAL_WINDOWS_READER_SHARING_BOUNDARY','transient_seconds':transient,'persistent_seconds':elapsed,'persistent_status':permanent,'old_target_preserved':True,'browser_or_tree_proof':False})

async def data(resource,built,out):
    from app.memory.service import MemoryService
    from app.memory.contracts import MemoryCommandInput,MemorySelectionInput
    h=Harness(resource,built,out,registry_dir=(CONTINUE_ROOT/'synthetic/independent-data-control').resolve())
    try:
        with psycopg.connect(resource['app']) as conn:
            unknown_before=conn.execute("SELECT state,reserve_seconds,elapsed_seconds FROM html_preview_sessions WHERE preview_id=%s",('542b0750-6e02-418a-b216-5dfbd3b93047',)).fetchone()
        assert unknown_before==('cleanup_unconfirmed',60,None)
        mid=plan()['objects']['race_memory']['memory_id'];service=MemoryService(h.ledger);view=await h.ledger.read_memory_snapshot(mid)
        selection=MemorySelectionInput(confirmed=True,entries=[{'memory_id':mid,'version':view['version'],'revision':view['revision'],'body_sha256':view['body_sha256']}])
        parent=await teaching_parent(h,'energy',memory_selection=selection,activity_id=aid_for('race_memory'),resume_existing=True)
        item=await diagnostic_artifact(h,'energy',parent_item=parent);artifact=await h.ledger.read_html_artifact(item['activity_id'],item['receipt']['artifact_id'])
        assert artifact['context']['memory_selection_sha256'] and artifact['context']['parent']['kind']=='teaching'
        impact=await h.ledger.preview_memory_change(mid,view['revision'],'revise')
        await service.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=view['revision'],action='revise',body={'kind':'self_report','title':'C03 新记忆版本','text':'改变后的合成背景，旧正文和版本保留','base_body_sha256':view['body_sha256'],'impact_token':impact['impact_token']}))
        invalid=await h.ledger.read_memory_selection(item['activity_id']);assert not invalid['eligible']
        try:await h.ledger.read_html_artifact(item['activity_id'],item['receipt']['artifact_id'])
        except HtmlRefusal as error:assert error.code=='source_invalid'
        else:raise AssertionError('changed selected memory left artifact eligible')
        atomic(out/'memory-v2-qualified-producer-and-revision.json',{'status':'PASS_REAL_V2_PARENT_ARTIFACT_AND_COMMITTED_MEMORY_INVALIDATION','item':item,'before_context_schema':artifact['context']['schema'],
          'memory_selection_sha256':artifact['context']['memory_selection_sha256'],'after_selection':invalid,'cached_frame_barrier':'NOT_RUN_BLOCKED_BY_UNKNOWN_STOP','transport_or_OneCall':False})
        effects=[]
        for role in ('app','denied'):
            with psycopg.connect(resource[role]) as conn:
                for operation,statement in (('update',"UPDATE html_artifacts SET artifact_sha256=repeat('0',64) WHERE artifact_id=%s"),('delete',"DELETE FROM html_artifacts WHERE artifact_id=%s")):
                    try:conn.execute(statement,(item['receipt']['artifact_id'],))
                    except psycopg.Error as error:effects.append({'role':role,'operation':operation,'sqlstate':error.sqlstate});assert error.sqlstate=='42501'
                    else:raise AssertionError('unexpected artifact direct DML privilege')
                    finally:conn.rollback()
        with psycopg.connect(resource['app']) as conn:
            unknown_after=conn.execute("SELECT state,reserve_seconds,elapsed_seconds FROM html_preview_sessions WHERE preview_id=%s",('542b0750-6e02-418a-b216-5dfbd3b93047',)).fetchone()
            bodies=conn.execute('SELECT count(*) FROM learning_memory_bodies WHERE memory_id=%s',(mid,)).fetchone()[0]
        assert unknown_before==unknown_after and bodies>=2
        atomic(out/'post-patch-permissions-and-unknown.json',{'status':'PASS_DIRECT_DML_REJECTIONS_ROLLBACK_ONLY_AND_UNKNOWN_RESERVE_RETAINED','effects':effects,'unknown_before':unknown_before,'unknown_after':unknown_after,'memory_bodies_retained':bodies,'new_preview_starts':0})
    finally:await h.controller.close()

def run(resource,built,out):
    filesystem(out)
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(data(resource,built,out))

