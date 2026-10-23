"""Metadata-only working sets for the exact owned runtime Job, at each sample."""
import ctypes,json,time
from ctypes import wintypes
from . import resources as r
from .control_job import NamedJob,JobOpenError
from .merged import members
class Counters(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
kernel.CloseHandle.argtypes=[wintypes.HANDLE]
psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
def probe(identity,root):
    available=r.available_memory();values=[]
    try:job=NamedJob.open_existing(identity,1)
    except JobOpenError as exc:
        values=[{'job_not_created_or_closed':True,'Windows_error':exc.code}]
    else:
        try:rows=members(job)
        except (OSError,RuntimeError) as exc:values=[{'exiting_job_snapshot_unknown':type(exc).__name__}]
        else:
            for row in rows:
                handle=kernel.OpenProcess(0x0410,False,row['pid'])
                if not handle:values.append({**row,'query_unavailable':ctypes.get_last_error()});continue
                try:
                    counter=Counters();counter.cb=ctypes.sizeof(counter)
                    ok=psapi.GetProcessMemoryInfo(handle,ctypes.byref(counter),counter.cb)
                    values.append({**row,'working_set_bytes':counter.WorkingSetSize if ok else None})
                finally:kernel.CloseHandle(handle)
        finally:job.close()
    folder='audit-repair-08' if r.state().get('current_permit_id')=='TASK-120-Q-PREP-TARGETED-REPAIR-08-20261021' else 'audit-repair-07' if r.state().get('current_permit_id')=='TASK-120-Q-PREP-AUDIT-REPAIR-07-20261021' else 'continuation-06' if r.state().get('current_permit_id')=='TASK-120-Q-PREP-CONTINUATION-06-20261020' else 'finalization-05' if r.state().get('current_permit_id')=='TASK-120-Q-PREP-FINALIZATION-05-20261019' else 'validation-04'
    path=(r.EXECUTION/folder/f'root-{root:02d}-memory-samples.jsonl') if folder=='audit-repair-07' else (r.EVIDENCE/folder/f'root-{root:02d}-memory-samples.jsonl')
    with path.open('a',encoding='utf-8') as stream:stream.write(json.dumps({'utc':r.utc(),'mono_ns':time.monotonic_ns(),'available_bytes':available,'owned_processes':values})+'\n')
    return available
