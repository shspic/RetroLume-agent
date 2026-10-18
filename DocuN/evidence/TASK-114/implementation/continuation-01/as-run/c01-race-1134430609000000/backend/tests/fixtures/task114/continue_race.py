"""精确OS/PG引用窗口、两个锁序、真实client退出和旧包删除覆盖。"""
import asyncio
import io
import json
import os
import subprocess
import threading
import time
from uuid import uuid4
from budget import ROOT,EVIDENCE
from setup_source import start_source,stop_source,IMAGE
from app.data_exit.restore import TargetFactory,inspect_target
from app.data_exit.contracts import DataError,DataJobCommand,digest
from app.runtime import psycopg_compatible_loop_factory
from app.preview.process import birth
from continue_source import material

def asynchronous(work):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(work)

def thread(name,function,errors):
    def call():
        try:function()
        except BaseException as e:errors.append({'thread':name,'type':type(e).__name__,'code':getattr(e,'code',None),'sqlstate':getattr(e,'sqlstate',None)})
    result=threading.Thread(name=name,target=call);result.start();return result

def race_group(budget,evidence,source,credentials):
    from continue_run import runtime_for
    if not start_source(budget,source):raise RuntimeError('source实时内存门不足')
    try:
        TargetFactory._wait_pg(credentials['admin_dsn']);app,rt=runtime_for(credentials,budget)
        ref=rt.references;errors=[]
        previous=EVIDENCE/'batches/c01-race-1134241937000000/02-D-first-result.json'
        if previous.exists():
            manifest=json.loads((EVIDENCE/'as-run/c01-race-1134241937000000/manifest.json').read_bytes())['files']
            for entry in manifest:
                if entry['path'] in ('backend/app/data_exit/reference.py','backend/app/data_exit/deletions.py','backend/app/data_exit/files.py','backend/app/storage/originals.py') and digest((ROOT/entry['path']).read_bytes())!=entry['sha256']:raise RuntimeError('原件竞态生产字节改变，不能继承')
            evidence.observe('01-D-first-reused',{'original_path':str(previous),'sha256':digest(previous.read_bytes()),'production_files_unchanged':True})
        else:
            a=material(rt,'C01 D最后检查窗口\n','C01 D先.md');impact=rt.deletions.preview(a['id'],a['revision'])
            last=threading.Event();release=threading.Event();b_before=threading.Event();b_acquired=threading.Event();b={};d={};unlink_result={}
            old_unlink=app.state.originals.unlink_exact;old_acquire=ref.lease.acquire
            def unlink(original,*,lease):
                if original.sha256==a['sha256']:
                    last.set()
                    if not release.wait(5):raise RuntimeError('准确最后窗口有界等待超时')
                    unlink_result['state']=old_unlink(original,lease=lease);unlink_result['exists_immediately_after_unlink']=(app.state.originals.root/original.sha256).exists()
                    return unlink_result['state']
                return old_unlink(original,lease=lease)
            def acquire(exclusive=False,**kwargs):
                if threading.current_thread().name=='C01-B-after-last':
                    b_before.set();result=old_acquire(exclusive,**kwargs);b_acquired.set();return result
                return old_acquire(exclusive,**kwargs)
            app.state.originals.unlink_exact=unlink;ref.lease.acquire=acquire
            worker_d=thread('C01-D-last',lambda:d.update(asynchronous(rt.deletions.confirm(a['id'],a['revision'],impact['impact_sha256'],'c01-D-first-'+str(uuid4())))),errors)
            worker_b=None
            try:
                if not last.wait(5):raise RuntimeError('未到准确最后检查/unlink窗口')
                worker_b=thread('C01-B-after-last',lambda:b.update(material(rt,'C01 D最后检查窗口\n','C01 B重新发布.md')),errors)
                if not b_before.wait(3):raise RuntimeError('B未进入真实RootLease准入')
                time.sleep(.03)
                if b_acquired.is_set():raise RuntimeError('D排他期间B已经获得共享')
                evidence.observe('01-D-first-boundary',{'source_deleted':a['id'],'hash':a['sha256'],'B_root_acquire_attempted':True,'B_root_acquired':False,'last_check_completed_before_unlink':True})
            finally:
                release.set();worker_d.join(8)
                if worker_b:worker_b.join(8)
                app.state.originals.unlink_exact=old_unlink;ref.lease.acquire=old_acquire
            if errors or worker_d.is_alive() or worker_b.is_alive() or unlink_result.get('exists_immediately_after_unlink') is not False or not b:raise RuntimeError('D先的准确并发结果不完整')
            evidence.observe('02-D-first-result',{'D_receipt':d,'unlink_result':unlink_result,'B_committed':b,'file_republished':(app.state.originals.root/a['sha256']).exists(),'errors':errors})
        # B先真实持SH，D从墓碑提交开始等EX；B新source COMMIT之后D须保共用文件。
        content2='C01 B先共享原件 '+str(uuid4())+'\n'
        a2=material(rt,content2,'C01 B先原资料.md');impact2=rt.deletions.preview(a2['id'],a2['revision'])
        held=threading.Event();commit=threading.Event();d_before=threading.Event();d_acquired=threading.Event();b2={};d2={}
        old_acquire=ref.lease.acquire
        def acquire2(exclusive=False,**kwargs):
            if exclusive:
                d_before.set();result=old_acquire(exclusive,**kwargs);d_acquired.set();return result
            return old_acquire(exclusive,**kwargs)
        ref.lease.acquire=acquire2
        def write_b():
            raw=content2.encode('utf-8');prepared=ref.prepare_reference(digest(raw),len(raw))
            with ref.acquire_shared(prepared) as pin:
                original=app.state.originals.put(io.BytesIO(raw),max_bytes=5*1024**2,reference_pin=pin);held.set()
                if not commit.wait(5):raise RuntimeError('B等COMMIT有界超时')
                b2.update(app.state.materials.save(source_id=None,expected_version=None,filename='C01 B先新资料.md',format='md',sha256=original.sha256,size=original.size,reference_pin=pin,prepared_ids=prepared))
        wb=thread('C01-B-before-D',write_b,errors);wd=None
        try:
            if not held.wait(5):raise RuntimeError('B未真实持SH')
            wd=thread('C01-D-after-B',lambda:d2.update(asynchronous(rt.deletions.confirm(a2['id'],a2['revision'],impact2['impact_sha256'],'c01-B-first-'+str(uuid4())))),errors)
            if not d_before.wait(3):raise RuntimeError('D未尝试排他')
            time.sleep(.03)
            if d_acquired.is_set():raise RuntimeError('B持SH时D越过排他')
            evidence.observe('03-B-first-boundary',{'B_real_shared_held':True,'D_exclusive_attempted':True,'D_exclusive_acquired':False})
        finally:
            commit.set();wb.join(8)
            if wd:wd.join(8)
            ref.lease.acquire=old_acquire
        if errors or not b2 or d2.get('state')!='deleted' or not (app.state.originals.root/a2['sha256']).exists():raise RuntimeError('B先的共享保留错误')
        evidence.observe('04-B-first-result',{'B_committed':b2,'D_receipt':d2,'shared_original_kept':True})
        # 真正独立client进程释放OS句柄但PG仍在完成已flush的事务。
        sid,vid=str(uuid4()),str(uuid4());content='C01 PG迟到提交原件\n';sha=digest(content.encode('utf-8'))
        budget.reserve('windows_start')
        argv=[str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(ROOT/'backend/tests/fixtures/task114/late_commit_child.py')]
        child=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        born=birth(child.pid);identity='c01-client:'+str(child.pid)+':'+str(born['birth'])
        budget.created(identity,'windows',{'pid':child.pid,'birth':born['birth'],'purpose':'actual client exit after flushed COMMIT'});budget.begin(identity)
        try:
            stdout,stderr=child.communicate(json.dumps({'credentials':credentials,'source_id':sid,'version_id':vid,'content':content}),timeout=15)
            if child.returncode or not json.loads(stdout)['commit_message_flushed']:raise RuntimeError('实际client事务未有界flush')
            if birth(child.pid)['state']=='running':raise RuntimeError('client未确认退出')
            begin=time.monotonic();outcomes=ref.exclusive_cleanup([{'sha256':sha,'size':str(len(content.encode('utf-8')))}]);delay=time.monotonic()-begin
            with rt.source.connection(readonly=True) as conn:
                row=conn.execute('SELECT id,source_id,sha256,size FROM public.material_versions WHERE id=%s',(vid,)).fetchone()
            if row is None or outcomes[0]['state']!='shared_retained' or not (app.state.originals.root/sha).exists():raise RuntimeError('client退出时误删已提交/迟到原件')
            evidence.observe('05-client-death-PG-late',{'arguments':argv,'client_pid':child.pid,'client_birth':born['birth'],'exit_code':child.returncode,'stdout':json.loads(stdout),'stderr':stderr,
                'both_pipes_eof':True,'PG_committed_row':row,'cleanup':outcomes,'cleanup_elapsed_seconds':delay,'file_retained':True})
        finally:
            if child.poll() is None:child.terminate()
            child.wait(timeout=5);budget.end(identity,{'pid':child.pid,'birth':born['birth'],'process_ended':True,'both_pipes_eof':True,'exit_code':child.returncode})
        # 未确认取消COMMIT不能进unlink；只模拟丢确认的边界，不伪造PG取消成功。
        attempt=[];cancel=ref.cancel_old_epoch;unlink=app.state.originals.unlink_exact
        def unknown():raise DataError('reference_cancel_unconfirmed',503)
        def unexpected(original,*,lease):attempt.append(original.sha256);return unlink(original,lease=lease)
        ref.cancel_old_epoch=unknown;app.state.originals.unlink_exact=unexpected
        try:
            try:ref.exclusive_cleanup([{'sha256':sha,'size':str(len(content.encode('utf-8')))}])
            except DataError as e:
                if e.code!='reference_cancel_unconfirmed':raise
            else:raise RuntimeError('未知取消没有拒绝')
        finally:ref.cancel_old_epoch=cancel;app.state.originals.unlink_exact=unlink
        if attempt:raise RuntimeError('未知取消进入unlink')
        evidence.observe('06-unknown-cancel-keeps-file',{'injected_boundary':'cancel confirmation unknown, no claim of actual PG success','unlink_calls':attempt,'file_kept':(app.state.originals.root/sha).exists()})
        # 旧包中真正存在的source后来删除，不能只测试备份之后新增资料。
        legacy=json.loads((ROOT/'DocuN/evidence/TASK-114/implementation/control/source-012-before-013.json').read_bytes())
        old=legacy['identities']['sources'][1];current=app.state.materials.get(old['id'])
        if current is None:raise RuntimeError('旧包删除样本已处理，先核断点不重复')
        impact=rt.deletions.preview(current['id'],current['revision'])
        deleted=asynchronous(rt.deletions.confirm(current['id'],current['revision'],impact['impact_sha256'],'c01-old-package-source-delete-'+str(uuid4())))
        evidence.observe('07-old-package-source-deleted',{'old_package_source':old,'receipt':deleted,'shared_file_kept':(app.state.originals.root/old['sha256']).exists()})
        record=rt.hub.state()['plans']['271e9dd7-e982-4daa-9854-4beffac445a1'];old_plan=rt.restore.plan(record['plan_id'],record['plan_sha256'])
        respect=rt.restore.prepare(old_plan['upload_id'],'respect_current_deletions',rt.context())
        snapshot=rt.restore.prepare(old_plan['upload_id'],'snapshot_only_readonly',rt.context())
        evidence.observe('08-overlay-plans',{'respect':respect,'snapshot_explicit':snapshot})
        # 新可携文件和恢复备份使用现有全部合成事实，原包不覆盖。
        packs=[]
        for kind in ('portable_export','restore_checkpoint'):
            cmd=DataJobCommand(kind,'c01-'+kind+'-'+str(uuid4()),{'mode':'all','source_ids':[],'activity_ids':[],'allow_incomplete':False})
            job=rt.hub.create_or_get_job(cmd,rt.context());receipt=rt.packages.capture_and_publish(job['job_id'],cmd.scope)
            from app.data_exit.packages import PackageReader
            path=rt.packages.download(job['job_id'])
            with PackageReader(path) as reader:packs.append({'receipt':receipt,'file_sha256':digest(path.read_bytes()),'manifest':reader.manifest})
        evidence.observe('09-new-portable-and-backup',packs)
        return {'state':'passed','respect_plan':respect,'snapshot_plan':snapshot,'deleted_old_source_id':old['id'],'late_commit_source_id':sid}
    finally:stop_source(budget,source)
