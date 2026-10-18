"""唯一PG托管者；准备后连续运行，原硬截止前留真实清场余量。"""
import ctypes,json,os,subprocess,sys,time,traceback
from ctypes import wintypes
from .control import ROOT,CONTINUE_ROOT,CONTINUATION,PERMIT,atomic,batch,phase,read_state,source_snapshot,event,CAPS
from .resources import pg_resume,shell_env,DOCKER
from .c03_resources import guardian,cleanup
from app.preview.process import birth,terminate_owned,GlobalOwner

def preflight(out):
    previous=json.loads((ROOT/'DocuN/evidence/TASK-111/orchestration-receipt-04/resource-recheck.json').read_text(encoding='utf-8-sig'));objects=[]
    fmt='{"id":{{json .Id}},"name":{{json .Name}},"image":{{json .Image}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"restart_count":{{json .RestartCount}}}'
    for row in previous['objects']:
        result=subprocess.run([DOCKER,'inspect','--format',fmt,row['id']],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW);assert result.returncode==0
        actual=json.loads(result.stdout);assert actual['id']==row['id'] and actual['image']==row['image'] and actual['name']==row['name'] and not actual['running'] and actual['pid']==0 and actual['restart_count']==0;objects.append(actual)
    owners=[]
    prior=json.loads((ROOT/'DocuN/evidence/TASK-111/execution/continuation-03/final-exact-resource-check.json').read_text(encoding='utf-8'))
    old_ended={(r['pid'],r['expected_birth']) for r in prior['owners'] if r['current']['state']=='exited'}
    class Entry(ctypes.Structure):
        _fields_=[('size',wintypes.DWORD),('usage',wintypes.DWORD),('pid',wintypes.DWORD),('heap',ctypes.c_size_t),('module',wintypes.DWORD),('threads',wintypes.DWORD),('parent',wintypes.DWORD),('priority',wintypes.LONG),('flags',wintypes.DWORD),('exe',wintypes.WCHAR*260)]
    api=ctypes.WinDLL('kernel32',use_last_error=True);api.CreateToolhelp32Snapshot.argtypes=(wintypes.DWORD,wintypes.DWORD);api.CreateToolhelp32Snapshot.restype=wintypes.HANDLE
    api.Process32FirstW.argtypes=(wintypes.HANDLE,ctypes.POINTER(Entry));api.Process32FirstW.restype=wintypes.BOOL;api.Process32NextW.argtypes=api.Process32FirstW.argtypes;api.Process32NextW.restype=wintypes.BOOL;api.CloseHandle.argtypes=(wintypes.HANDLE,)
    snapshot=api.CreateToolhelp32Snapshot(2,0);assert snapshot not in (None,ctypes.c_void_p(-1).value);catalog=set();entry=Entry();entry.size=ctypes.sizeof(entry)
    try:
        more=api.Process32FirstW(snapshot,ctypes.byref(entry))
        while more:catalog.add(int(entry.pid));more=api.Process32NextW(snapshot,ctypes.byref(entry))
    finally:api.CloseHandle(snapshot)
    old=ROOT/'DocuN/evidence/TASK-111/execution/continuation-03'
    for path in old.rglob('registry.json'):
        row=json.loads(path.read_text(encoding='utf-8'))
        if 'intent' not in row:continue
        for data in (row.get('parent'),row.get('reaper_owner'),row.get('reaper_launcher'),dict(pid=row.get('attach_pid'),birth=row.get('attach_birth'))):
            if not data or not data.get('pid'):continue
            actual=birth(data['pid']);inherited_exit=(data['pid'],data['birth']) in old_ended and data['pid'] not in catalog
            assert (actual['state']!='unknown' or inherited_exit) and not (actual['state']=='running' and actual['birth']==data['birth'])
            owners.append(dict(pid=data['pid'],expected_birth=data['birth'],current=actual,registered=str(path.relative_to(ROOT)),prior_exact_exit_and_current_catalog_absent=inherited_exit))
    owner=GlobalOwner('Global\\RetroLumePreviewV2Task111')
    try:assert owner.acquire()=='acquired'
    finally:owner.close()
    atomic(out/'old-objects-and-global-preflight.json',dict(objects=objects,registered_windows=owners,global_exclusive=True,old_roots_unmodified=True,old_unknown_kernel_EOF_still_missing=True))

def main():
    if os.environ.get('RETROLUME_TASK111_FIXTURE')!=PERMIT or CONTINUATION!='TASK-111-G11-C04-20261011':raise RuntimeError('C04 permit')
    timing=json.loads((CONTINUE_ROOT/'timing.json').read_text(encoding='utf-8'));current=read_state();remaining=min(3000,14400-current['time_seconds']['real'])
    hold_deadline=min(current['business_deadline_ns'],time.monotonic_ns()+int((remaining-10)*1e9));phase('real')
    lease=CONTINUE_ROOT/('integrated-holder-'+str(current['counts']['real_batches']+1));lease.mkdir();atomic(lease/'owner.json',dict(pid=os.getpid(),birth=birth(os.getpid()),deadline_ns=hold_deadline));resource=None;guard=None;step=0;stop=False
    try:
        for root_no in range(current['counts']['real_batches']+1,CAPS['real_batches']+1):
            if stop or time.monotonic_ns()>=hold_deadline-15*10**9:break
            folder=CONTINUE_ROOT/('root-'+str(root_no));folder.mkdir()
            with batch('real','C04 qualification startup Native UI remaining matrix',maximum=min(1800,(hold_deadline-time.monotonic_ns())/1e9)) as active:
                source_snapshot(folder)
                if resource is None:
                    preflight(folder);guard=guardian(lease,hold_deadline);resource=pg_resume(folder)
                atomic(CONTINUE_ROOT/'coordinator-ready.json',dict(pid=os.getpid(),birth=birth(os.getpid()),root=root_no,root_deadline_ns=active['deadline_ns'],hold_deadline_ns=hold_deadline))
                while time.monotonic_ns()<min(active['deadline_ns']-10*10**9,hold_deadline-10*10**9):
                    path=CONTINUE_ROOT/('command-'+str(step+1).zfill(2)+'.json')
                    if not path.exists():time.sleep(.05);continue
                    command=json.loads(path.read_text(encoding='utf-8'));step+=1;action=command['action']
                    if action=='stop':stop=True;break
                    if action=='next_root':break
                    out=folder/('step-'+str(step).zfill(2)+'-'+action);out.mkdir()
                    env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource),PYTHONPATH=str(ROOT/'backend/tests/fixtures/task111/bootstrap')+os.pathsep+str(ROOT/'backend'))
                    with (out/'stdout.bin').open('wb') as stdout,(out/'stderr.bin').open('wb') as stderr:
                        child=subprocess.Popen([sys.executable,'-B','-m','tests.fixtures.task111.c04_step',action,str(out)],cwd=ROOT/'backend',env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW);atomic(out/'launcher.json',dict(pid=child.pid,birth=birth(child.pid)))
                        try:child.wait(timeout=min(900,max(.1,(min(active['deadline_ns'],hold_deadline)-time.monotonic_ns())/1e9-15)))
                        except subprocess.TimeoutExpired:
                            actual=json.loads((out/'actual-step-owner.json').read_text(encoding='utf-8'));terminate_owned(actual['pid'],actual['birth']);child.wait(5)
                    atomic(CONTINUE_ROOT/'step-complete.json',dict(step=step,action=action,folder=str(out),exit=child.returncode))
    finally:
        phase('cleanup');cleanup(lease,guard);phase('implementation_offline')

if __name__=='__main__':main()
