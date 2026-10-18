"""正常链必需功能检查：真实互斥、挂起入Job和过期后的独立清场。"""
import ctypes,json,os,secrets,subprocess,sys,time
from ctypes import wintypes
from pathlib import Path
from uuid import uuid4
from . import control
from .resources import shell_env
from app.preview.process import GlobalOwner,birth
from app.preview.host_job import HostJob,JobChild,job_name


def main():
    if len(sys.argv)>1:
        if sys.argv[1]=="mutex":
            owner=GlobalOwner(sys.argv[2])
            try:print(json.dumps({"acquire":owner.acquire(),"identity":owner.identity(),"pid":os.getpid()}))
            finally:owner.close()
        else:
            api=ctypes.WinDLL("kernel32",use_last_error=True);api.IsProcessInJob.argtypes=(wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL));api.IsProcessInJob.restype=wintypes.BOOL
            included=wintypes.BOOL();assert api.IsProcessInJob(wintypes.HANDLE(-1),None,ctypes.byref(included))
            api.OpenJobObjectW.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.LPCWSTR);api.OpenJobObjectW.restype=wintypes.HANDLE
            api.CloseHandle.argtypes=(wintypes.HANDLE,)
            exact=api.OpenJobObjectW(4,False,sys.argv[2]);specific=wintypes.BOOL()
            try:assert exact and api.IsProcessInJob(wintypes.HANDLE(-1),exact,ctypes.byref(specific))
            finally:
                if exact:api.CloseHandle(exact)
            print(json.dumps({"pid":os.getpid(),"in_job":bool(included.value),"specific_job":bool(specific.value)}))
        return
    control.phase("implementation_offline");number=1+len(list(control.CONTINUE_ROOT.glob("control-check-*")))
    folder=control.CONTINUE_ROOT/("control-check-"+str(number).zfill(2));folder.mkdir(exist_ok=False)
    with control.batch("offline","c02-normal-control-functional",maximum=120):
        control.source_snapshot(folder)
        owner=GlobalOwner("Global\\RetroLumePreviewV2Task111Probe"+uuid4().hex)
        try:
            assert owner.acquire()=="acquired";actual=owner.identity()
            with HostJob(job_name(str(uuid4()),secrets.token_hex(32),"CALL")) as job:
                child=JobChild([sys.executable,"-B","-m","tests.fixtures.task111.c02_checks","mutex",owner.name],job,env=shell_env(),cwd=str(control.ROOT/"backend"))
                try:
                    out,err=child.communicate(timeout=5);assert child.poll()==0,(out,err)
                    competing=json.loads(out)
                    control.atomic(folder/"global-owner.json",{"held_identity":actual,"other_process":competing,"scope":"actual Global kernel object, two local user processes; no login/session manipulation"})
                    assert competing["acquire"]=="busy" and competing["identity"]["kernel_object_path"]==actual["kernel_object_path"]
                finally:child.close()
                control.atomic(folder/"mutex-child-job-end.json",job.finish())
        finally:owner.close()
        with HostJob(job_name(str(uuid4()),secrets.token_hex(32),"CALL")) as job:
            child=JobChild([sys.executable,"-B","-m","tests.fixtures.task111.c02_checks","job",job.name],job,env=shell_env(),cwd=str(control.ROOT/"backend"))
            try:
                started=child.birth;out,err=child.communicate(timeout=5);assert child.poll()==0,(out,err)
                body=json.loads(out)
                control.atomic(folder/"job-child.json",{"primary_pid":child.pid,"birth":started,"child":body,"stdin_closed":child.stdin.closed,"stdout_eof":child.stdout.read()==b"","ended":birth(child.pid),"job":job.finish()})
                assert body["in_job"] and body["specific_job"] and body["pid"]>0
            finally:child.close()
        # 同一真实函数切到纯合成账目录，旧业务截止必须拒绝、cleanup必须能执行。
        original=control.EVIDENCE;sandbox=folder/"expired-budget";sandbox.mkdir()
        fake=control.read_state();fake["deadline_ns"]=time.monotonic_ns()-1;fake["business_deadline_ns"]=fake["deadline_ns"];fake["active_batch"]=None
        control.atomic(sandbox/"budget.json",fake)
        try:
            control.EVIDENCE=sandbox
            try:control.state();raise AssertionError("expired business accepted")
            except RuntimeError:pass
            with control.batch("cleanup","functional-expired-cleanup",maximum=10):
                result=control.run([sys.executable,"-B","-c","print('cleanup-after-expiry')"],sandbox,env=shell_env(),maximum=5,name="expired-cleanup")
                assert result.stdout.strip()==b"cleanup-after-expiry"
        finally:control.EVIDENCE=original
        control.atomic(folder/"result.json",{"status":"PASS_FUNCTIONAL_LOCAL","global_kernel_scope":True,"suspended_assigned_child":True,"expired_business_refused_cleanup_executed":True,"no_PG_or_renderer_start":True})
        print("C02 normal control functional checks passed")


if __name__=="__main__":main()
