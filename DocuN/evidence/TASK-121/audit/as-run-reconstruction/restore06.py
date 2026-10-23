"""Exact factory observation/cleanup for the single approved06 restore target."""
import json,re,socket
from dataclasses import asdict
from . import resources as r
NAME='retrolume-task120-scopeui-ro1';VOLUME=NAME+'-data'
IMAGE='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'

def preflight():
    saved=r.state().get('continuation06_target_port')
    if saved:return saved
    assert not r.docker(['ps','-aq','--filter','name=^/'+NAME+'$'])
    assert VOLUME not in r.docker(['volume','ls','-q']).splitlines()
    results=[];chosen=None
    for port in (55481,55482):
        with socket.socket() as s:
            try:s.bind(('127.0.0.1',port))
            except OSError as e:results.append({'port':port,'bindable':False,'Windows_error':getattr(e,'winerror',None)})
            else:
                results.append({'port':port,'bindable':True})
                if chosen is None:chosen=port
    r.write(r.EVIDENCE/'continuation-06/factory-preflight.json',{'ports':results,'chosen_first_bindable':chosen,'container_and_volume_names_absent':True,'factory_only':True})
    if chosen is None:raise RuntimeError('both_approved_restore_ports_unavailable')
    r.update(lambda v:v.update(continuation06_target_port=chosen));return chosen

def identity(value):
    # Full inspect stays in memory; only whitelisted identity/state is returned.
    full=json.loads(r.docker(['container','inspect',value['cid']]))[0]
    host=full['HostConfig'];labels=full['Config'].get('Labels',{});mount=full['Mounts']
    assert full['Id']==value['cid'] and full['Name']=='/'+NAME and full['Image']==IMAGE
    assert labels.get('retrolume.data.job')==value['job_id'] and labels.get('retrolume.data.profile')==value['profile_id'] and labels.get('retrolume.data.target')==value['target_id'] and labels.get('retrolume.data.purpose')=='restore-readonly'
    assert host['Memory']==536870912 and host['NanoCpus']==10**9 and host['PidsLimit']==128 and host['RestartPolicy']['Name']=='no' and not host['Privileged']
    assert len(mount)==1 and mount[0]['Type']=='volume' and mount[0]['Name']==VOLUME and mount[0]['Destination']=='/var/lib/postgresql/data'
    assert host['PortBindings']=={'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':str(value['port'])}]}
    return {'cid':full['Id'],'name':full['Name'],'image_id':full['Image'],'labels':labels,'volume':VOLUME,'port':value['port'],'running':full['State']['Running'],'Pid':full['State']['Pid'],'status':full['State']['Status'],'limits':{'Memory':host['Memory'],'NanoCpus':host['NanoCpus'],'PidsLimit':host['PidsLimit'],'restart':host['RestartPolicy']['Name']}}

def stop_targets():
    value=r.state().get('continuation06_restore_target')
    if value is None:return {'created':False}
    actual=identity(value)
    if actual['running']:r.docker(['container','stop','--time','5',value['cid']],timeout=15)
    actual=identity(value);assert not actual['running'] and actual['Pid']==0
    r.update(lambda v:v.update(continuation06_restore_target_last_stop=actual));return actual

def install(factory):
    from app.data_exit import restore
    original=restore.docker_call
    def observed(arguments,**kwargs):
        value=original(arguments,**kwargs)
        if arguments[0]=='create':
            assert re.fullmatch('[0-9a-f]{64}',value)
            labels={arguments[n+1].split('=',1)[0]:arguments[n+1].split('=',1)[1] for n,x in enumerate(arguments) if x=='--label'}
            record={'cid':value,'name':NAME,'volume':VOLUME,'port':r.state()['continuation06_target_port'],'job_id':labels['retrolume.data.job'],'profile_id':labels['retrolume.data.profile'],'target_id':labels['retrolume.data.target'],'actual_CID_registered_before_return_to_factory':True}
            def registered(v):
                assert v.get('continuation06_restore_target') is None
                v['continuation06_restore_target']=record;v['counts']['pg_objects']+=1;v['counts']['volumes']+=1;v['ports']['restore_pg']=record['port']
            r.update(registered);r.event('continuation06_factory_actual_CID_returned',target=record)
        return value
    restore.docker_call=observed
    class Hooks:
        def before_create(self,slot):
            assert slot['name']==NAME and slot['volume']==VOLUME and slot['port']==r.state()['continuation06_target_port']
            r.memory_gate('pg')
            def reserve(v):
                for name in ('pg_create_attempts','volume_create_attempts'):assert v['counts'][name]<v['caps'][name]
                assert v.get('continuation06_restore_target') is None
                v['counts']['pg_create_attempts']+=1;v['counts']['volume_create_attempts']+=1
            r.update(reserve);r.event('continuation06_factory_before_create_counted',slot=slot)
        def created(self,target,actual):
            value={k:str(v) if k=='data_root' else v for k,v in asdict(target).items()}
            assert r.state()['continuation06_restore_target']['cid']==target.cid
            r.update(lambda v:v.update(continuation06_restore_target=value))
            r.write(r.EVIDENCE/'continuation-06/actual-restore-target-created.json',{'target':value,'actual':identity(value)})
        def before_start(self,target):r.memory_gate('pg');r.count('pg_starts');r.event('continuation06_factory_before_start_counted',cid=target.cid)
        def started(self,target,actual):r.event('continuation06_factory_started',cid=target.cid,actual=actual)
        def stopped(self,target,actual):r.event('continuation06_factory_stopped',cid=target.cid,actual=actual)
    factory.hooks=Hooks()
    return lambda:setattr(restore,'docker_call',original)
