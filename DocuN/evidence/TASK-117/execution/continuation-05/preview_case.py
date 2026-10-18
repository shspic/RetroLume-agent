"""L10固定宿主分时实证；沿正常API、ACK/PNG及原StopProof，无新渲染权限。"""
from batch_runtime import *
from uuid import uuid4
from app.preview.description import digest

def run_preview(batch,flow,aid,artifact_id):
    if batch.browser is not None:batch.close_browser()
    rc.docker(['image','inspect',PREVIEW_IMAGE]);rc.memory_gate('L10-fixed-preview',stage='preview')
    artifact=flow.call('GET',f'/api/activities/{aid}/html/artifacts/{artifact_id}')
    holder={};folder=C01/'L10';folder.mkdir(exist_ok=True)
    def proof():
        pid=holder.get('preview_id')
        if not pid:raise RuntimeError('preview_open_receipt_missing')
        origin=EXEC/'synthetic/source-data/preview-control'/pid
        source=origin/'supervisor-result.json'
        if not source.exists():raise RuntimeError('preview_StopProof_not_published')
        value=json.loads(source.read_text());p=value.get('proof') or {}
        assert value['confirmed'] is True and p['tree_confirmation'] in ('private_pid_init_terminated','never_started')
        assert p['owned_reaper_ended']
        if p['tree_confirmation']=='private_pid_init_terminated':assert p['pipe_observation']['stdout_eof'] and p['pipe_observation']['stderr_eof']
        for f in origin.glob('*.json'):
            if f.name in ('registry.json','current.json'):continue
            if f.name.startswith(('supervisor-result','supervisor-job-final','reaper-job-final','ready','kernel-premises','engine-observation')):
                (folder/f.name).write_bytes(f.read_bytes())
        batch.run.preview_running=False
        return {'preview_id':pid,'StopProof_sha256':c.sha(source.read_bytes()),'cid':p['cid'],'confirmed':True}
    # API lifespan owns the original preview controller; it stops it even on pressure/deadline.
    batch.run.register('preview-owned-api-lifespan',batch.close_api,priority=50)
    batch.run.register('preview-original-stop-proof',proof,priority=49)
    owner=secrets.token_hex(32);flow.client.headers['X-RetroLume-Preview-Owner']=owner
    c.count('preview_creates');c.count('preview_starts');batch.run.preview_running=True
    opened=flow.call('POST',f'/api/activities/{aid}/html/artifacts/{artifact_id}/previews',{'start_key':str(uuid4()),'expected_artifact_sha256':artifact['artifact_sha256'],'input_owner_key':owner,'confirmed':True})
    pid=opened['preview_id'];holder['preview_id']=pid;generation=opened['generation'];base=f'/api/activities/{aid}/html/previews/{pid}'
    observations=[]
    try:
        deadline=min(time.monotonic()+32,batch.run.deadline)
        while True:
            status=flow.call('GET',base)
            if status['state'] in ('ready','running'):break
            if status['state'] in ('stopped','failed_unstarted','cleanup_unconfirmed') or time.monotonic()>=deadline:raise RuntimeError('preview_not_ready:'+status['state'])
            time.sleep(.15)
        def send(seq,event,expected=200):
            result=flow.call('POST',base+'/inputs',{'preview_generation':generation,'seq':seq,'payload_sha256':digest(event),'event':event},expected=expected)
            observations.append({'seq':seq,'event':event,'http':expected,'ack':result});return result
        def speed(ack,value):
            assert ack['accepted'] is True and next(r['value'] for r in ack['readouts'] if r['id']=='hout_speed')==value,ack
        speed(send(1,{'type':'set_number','control_id':'hctl_time','value':'120'}),'1')
        speed(send(2,{'type':'set_number','control_id':'hctl_time','value':'240'}),'0.5')
        send(3,{'type':'set_number','control_id':'hctl_time','value':'0'},422)
        send(3,{'type':'set_number','control_id':'hctl_undefined','value':'1'},422)
        speed(send(3,{'type':'activate','action_id':'hact_reset'}),'1')
        c.count('http');frame=flow.client.get(base+'/frames',params={'generation':generation,'after_seq':0})
        assert frame.status_code==200 and frame.content.startswith(b'\x89PNG\r\n\x1a\n')
        assert c.sha(frame.content)==frame.headers['X-Frame-Sha256']
        (folder/'actual-frame.png').write_bytes(frame.content)
        c.write(folder/'input-acks.json',{'activity_id':aid,'artifact_id':artifact_id,'artifact_sha256':artifact['artifact_sha256'],'parent':artifact['parent'],'observations':observations,'PNG_sha256':c.sha(frame.content),'sample':c.sample()})
    finally:
        try:
            flow.call('POST',base+'/stop',{'generation':generation,'stop_key':str(uuid4()),'reason':'user'})
            deadline=min(time.monotonic()+25,batch.run.deadline)
            while time.monotonic()<deadline:
                status=flow.call('GET',base)
                if status['state']=='stopped':break
                if status['state']=='cleanup_unconfirmed':raise RuntimeError('preview_cleanup_unconfirmed')
                time.sleep(.15)
            else:raise RuntimeError('preview_stop_unconfirmed')
            proof()
        finally:flow.client.headers.pop('X-RetroLume-Preview-Owner',None)

