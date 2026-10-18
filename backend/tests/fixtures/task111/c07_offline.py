"""三缺陷的实际产品入口定向反例；替身时钟与门级结算明确只算离线。"""
import copy,hashlib,io,json,os,struct,sys,threading,time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from .control import ROOT,CONTINUE_ROOT,CONTINUATION,EVIDENCE,atomic,batch,phase,read_state,run,source_snapshot,registry_root,CAPS
from .samples import energy
from app.preview import production_supervisor as ps
from app.preview.description import canonical,digest,load_json,validate_description
from app.preview.compiler import runtime_identity

class EndedThread:
    def is_alive(self):return False

class EndedAttach:
    def poll(self):return 0

def controller():
    result=ps.PreviewController.__new__(ps.PreviewController)
    result._event_sink=None;result.policy=SimpleNamespace(load_manifest_sha256='1'*64,renderer_sha256='2'*64)
    return result

def current(out):
    return dict(folder=out,t0_ns=10**12,deadline_ns=10**12+60*10**9,preview_id='00000000-0000-0000-0000-000000000007',
        generation=1,artifact_sha256='3'*64,channel_nonce='4'*64,description=energy(),received_ready=None,kernel_ready=None,
        ready_received_ns=None,ready_accepted_ns=None,ready=threading.Event(),stop=threading.Event(),error_code=None,
        pipe_eof=False,stderr_eof=False,stdout_read_error=None,stderr_read_error=None,stderr_observed_bytes=0,stderr_captured_bytes=0,
        stderr_overflow=False,frame_seq=0,frame=None,input_seq=0,reserve_seconds=60,state='start_requested')

def wire(c,body):
    raw=canonical(body).encode();head=dict(protocol='retrolume.preview.v2',type='ready',preview_id=c['preview_id'],generation=1,
        artifact_sha256=c['artifact_sha256'],channel_nonce=c['channel_nonce'],seq=0,body_bytes=len(raw),body_sha256=hashlib.sha256(raw).hexdigest())
    header=canonical(head).encode();return struct.pack('!I',len(header))+header+raw

def ready_checks(out):
    rows=[]
    scenarios=[('timely',7997000000,7998000000,False,True),('exact_boundary',8000000000,8000000000,False,False),
        ('wait_success_late',8005000000,8006000000,False,False),('wait_success_stop',7997000000,7998000000,True,False),
        ('scheduler_window_closed',7997000000,9000000000,False,False),('D_minus_10_boundary',6999000000,7000000000,False,False)]
    for name,arrival,decision,stopped,expected in scenarios:
        folder=out/name;folder.mkdir();owner=controller();c=current(folder)
        if name=='D_minus_10_boundary':c['deadline_ns']=c['t0_ns']+17*10**9
        body=dict(load_manifest_sha256='1'*64,renderer_sha256='2'*64,description_sha256=digest(c['description']),physical_fact_fixture='offline_only')
        read_fd,write_fd=os.pipe();r=os.fdopen(read_fd,'rb',buffering=0);w=os.fdopen(write_fd,'wb',buffering=0)
        c['attach']=SimpleNamespace(stdout=r);clock=[c['t0_ns']+arrival]
        with patch.object(ps.time,'monotonic_ns',side_effect=lambda:clock[0]):
            thread=threading.Thread(target=owner._read,args=(c,));thread.start();w.write(wire(c,body))
            assert c['ready'].wait(2),'完整packet未被实际reader读取'
            clock[0]=c['t0_ns']+decision
            if stopped:c['stop'].set()
            wait_return=c['ready'].is_set()
            try:owner._wait_ready(c);accepted=True
            except ps.OwnershipUnknown:accepted=False
            assert accepted==expected and c['kernel_ready']==body and c['ready_received_ns']==c['t0_ns']+arrival
            w.close();thread.join(2);r.close();assert not thread.is_alive()
        rows.append(dict(name=name,accepted=accepted,expected=expected,event_wait_success=wait_return,complete_packet_received_ns=c['ready_received_ns'],
            commit_accepted_ns=c['ready_accepted_ns'],decision_clock_ns=c['t0_ns']+decision,t0_ns=c['t0_ns'],deadline_ns=c['deadline_ns'],
            sampling='确定离线替身单调时钟；实际产品_read/_wait_ready及匿名管道；不冒实机调度'))
    atomic(out/'ready-offline-result.json',dict(status='PASS_ACTUAL_READY_SUCCESS_WAIT_GATE',rows=rows))

class Chunks:
    def __init__(self,chunks,error=False):self.chunks=list(chunks);self.error=error
    def read(self,size):
        if self.chunks:return self.chunks.pop(0)
        if self.error:raise OSError('fixed offline read exception')
        return b''

def stderr_checks(out):
    rows=[]
    for name,chunks,error in [('empty',[],False),('8192',[b'x'*1024]*8,False),('8193',[b'x'*1024]*8+[b'x'],False),
        ('chunked_10000',[b'x'*1000]*10,False),('read_exception',[b'x'*1024]*9,True)]:
        folder=out/name;folder.mkdir();owner=controller();c=current(folder);c['deadline_ns']=time.monotonic_ns()+60*10**9
        c['t0_ns']=time.monotonic_ns();c['attach']=EndedAttach();c['attach'].stderr=Chunks(chunks,error)
        c.update(pipe_eof=True,reader=EndedThread(),stderr_reader=EndedThread());owner._stderr(c)
        calls=[];owner._transition=lambda current,state,**kw:calls.append(dict(state=state,elapsed=kw.get('elapsed')))
        proof=dict(tree_confirmation='private_pid_init_terminated');settled=owner._settle_stop(c,proof,True)
        assert settled==(not error) and bool(calls)==(not error) and c['stderr_observed_bytes']==sum(map(len,chunks))
        assert (folder/'container-stderr.bin').stat().st_size==min(8192,sum(map(len,chunks)))
        assert c['stderr_overflow']==(sum(map(len,chunks))>8192)
        rows.append(dict(name=name,observation=owner._pipe_observation(c),settled=settled,settlement_calls=calls,
            level='实际读取及结算门离线；不冒Linux/Job证明或PG事务'))
    for name,stdout,stderr,read_error in [('thread_ended_without_stderr_eof',True,False,None),('stdout_missing',False,True,None),('read_error_even_after_eof',True,True,'OSError')]:
        folder=out/name;folder.mkdir();owner=controller();c=current(folder)
        c.update(deadline_ns=time.monotonic_ns()+60*10**9,t0_ns=time.monotonic_ns(),pipe_eof=stdout,stderr_eof=stderr,stderr_read_error=read_error,
            attach=EndedAttach(),reader=EndedThread(),stderr_reader=EndedThread())
        calls=[];owner._transition=lambda *a,**kw:calls.append(kw)
        settled=owner._settle_stop(c,dict(tree_confirmation='private_pid_init_terminated',attach_eof_confirmed=True),True)
        assert not settled and not calls
        rows.append(dict(name=name,settled=settled,settlement_calls=calls,observation=owner._pipe_observation(c)))
    # 实际Python流读取异常不会因后续排空返回空读而消除异常事实。
    owner=controller();folder=out/'stdout_read_exception';folder.mkdir();c=current(folder);c['deadline_ns']=time.monotonic_ns()+60*10**9
    class OnceError:
        def __init__(self):self.first=True
        def read(self,size):
            if self.first:self.first=False;raise OSError('fixed read failure')
            return b''
    c['attach']=SimpleNamespace(stdout=OnceError());owner._read(c)
    assert c['pipe_eof'] and c['stdout_read_error']=='PipeReadError'
    rows.append(dict(name='stdout_read_exception',observation=owner._pipe_observation(c)))
    atomic(out/'stderr-offline-result.json',dict(status='PASS_REAL_EOF_AND_NO_SETTLEMENT_GATES_OFFLINE',rows=rows))

def node_checks(out):
    renderer=runtime_identity()['renderer_sha256'];cases=[];python_rows=[]
    variants=[('missing','MISSING',True),('empty',[],True),('null',None,False),('string','',False),('object',{},False),('number',1,False),('bool',True,False),('internal_BOM',[],True)]
    for name,value,expected in variants:
        desc=energy()
        if value=='MISSING':desc.pop('constraints',None)
        else:desc['constraints']=value
        if name=='internal_BOM':desc['title']+='\ufeff合法内部字符'
        raw=canonical(desc).encode()
        try:validate_description(load_json(raw),desc['citations']);accepted=True
        except ValueError:accepted=False
        assert accepted==expected
        body=dict(schema='retrolume.preview.init.v2',description=desc,description_sha256=digest(desc),renderer_sha256=renderer,viewport=dict(width=640,height=480))
        body_bytes=canonical(body).encode();h=dict(protocol='retrolume.preview.v2',type='init',preview_id='00000000-0000-0000-0000-000000000007',generation=1,
            artifact_sha256='3'*64,channel_nonce='4'*64,seq=0,body_bytes=len(body_bytes),body_sha256=hashlib.sha256(body_bytes).hexdigest())
        header=canonical(h).encode();case=dict(name=name,expected=expected,body_hex=body_bytes.hex(),header_hex=header.hex())
        if name=='internal_BOM':case['internal_title']=desc['title']
        cases.append(case);python_rows.append(dict(name=name,accepted=accepted,description_sha256=hashlib.sha256(raw).hexdigest()))
    for kind in ('header','body'):
        base=copy.deepcopy(cases[1]);base.update(name='BOM_'+kind,expected=False)
        raw=bytes.fromhex(base['body_hex']);h=json.loads(bytes.fromhex(base['header_hex']))
        if kind=='body':raw=b'\xef\xbb\xbf'+raw;h['body_bytes']=len(raw);h['body_sha256']=hashlib.sha256(raw).hexdigest()
        header=canonical(h).encode()
        if kind=='header':header=b'\xef\xbb\xbf'+header
        try:load_json(header if kind=='header' else raw);accepted=True
        except ValueError:accepted=False
        assert not accepted;base.update(body_hex=raw.hex(),header_hex=header.hex());cases.append(base)
        python_rows.append(dict(name=base['name'],accepted=False,raw_sha256=hashlib.sha256(header if kind=='header' else raw).hexdigest()))
    payload=dict(renderer=renderer,cases=cases,out=str(out/'node-host-result.json'));atomic(out/'node-input.json',payload)
    run(['node',str(ROOT/'backend/tests/fixtures/task111/c07_node.cjs'),str(out/'node-input.json')],out,maximum=30,name='node-actual-host-ingress')
    atomic(out/'python-domain-result.json',dict(status='PASS_ACTUAL_PYTHON_DESCRIPTION_AND_JSON_ENTRIES',rows=python_rows))

def main():
    node_only=len(sys.argv)>1 and sys.argv[1]=='node_only'
    out=CONTINUE_ROOT/('offline-02-node' if node_only else 'offline-01');out.mkdir(exist_ok=False);phase('implementation_offline')
    with batch('offline','C07 three defects actual product gates and exact resource preflight',maximum=(read_state()['business_deadline_ns']-time.monotonic_ns())/1e9):
        assert CONTINUATION=='TASK-111-G11-C07-20261012' and registry_root()==EVIDENCE/'continuation-04/synthetic/control'
        assert CAPS['real_batches']==20 and CAPS['image_builds']==9
        assert sum(x.get('issue')=='E112-01' for x in read_state()['execution_time_adjustments'])==1
        if not node_only:
            for part in ('ready','stderr','node'):(out/part).mkdir()
            ready_checks(out/'ready');stderr_checks(out/'stderr')
        else:
            (out/'node').mkdir()
            atomic(out/'retained-failure-and-inheritance.json',dict(failure='offline-01/node实际宿主VM与require跨realm的Object.prototype不一致；离线夹具改为同realm CJS wrapper',
                original_node_failure=str(CONTINUE_ROOT/'offline-01/node/node-actual-host-ingress.stderr.bin'),
                ready=str(CONTINUE_ROOT/'offline-01/ready/ready-offline-result.json'),stderr=str(CONTINUE_ROOT/'offline-01/stderr/stderr-offline-result.json'),product_changes_for_retry=False))
        node_checks(out/'node');source_snapshot(out)
        atomic(out/'result.json',dict(status='PASS_C07_TARGETED_PRODUCT_GATES_OFFLINE',real_PG_or_browser_started=False))
    print('PASS_C07_TARGETED_PRODUCT_GATES_OFFLINE')

if __name__=='__main__':main()
