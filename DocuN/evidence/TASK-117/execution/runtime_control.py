"""本卡精确新PG的资源门和生命周期；凭据只进入本卡私有文件/环境。"""
from __future__ import annotations
import ctypes
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import time
from control import HERE,ROOT,count,event,state,write,guard,sample

PG_IMAGE='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
SLOTS={'source':(15481,'step018_syn'),'compat':(15482,'step018_compat'),'r01':(15483,'step018_r01'),'r02':(15484,'step018_r02'),'r02-fault':(15485,'step018_r02_fault'),'r02-success-01':(15486,'step018_r02_success_01'),'r02-success-02':(15487,'step018_r02_success_02')}
PRIVATE=HERE/'synthetic/private'
_CONTROLLER=None


def bind_controller(controller):
    global _CONTROLLER
    if _CONTROLLER is not None and not _CONTROLLER.closed.is_set():raise RuntimeError('已有本卡在途控制器')
    _CONTROLLER=controller


def require_controller(slot):
    from control import active_segment
    if active_segment(state()) is None:return
    if _CONTROLLER is None:raise RuntimeError('S02必须先有完整有界控制器')
    _CONTROLLER.check()
    registered=getattr(_CONTROLLER,'pg_slots',set())
    if slot not in registered:
        if slot not in ('source','compat'):raise RuntimeError('新目标由可信factory闭包登记')
        _CONTROLLER.register('pg-'+slot,lambda:stop_pg(slot),priority=0)
        registered.add(slot);_CONTROLLER.pg_slots=registered


def docker(arguments,*,environment=None,timeout=30):
    result=subprocess.run(['docker',*arguments],env=environment,capture_output=True,timeout=timeout)
    if result.returncode:raise RuntimeError('docker_'+arguments[0]+'_failed')
    return result.stdout.decode('utf-8','replace').strip()


def available_memory_bytes():
    class Memory(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total_phys',ctypes.c_ulonglong),('avail_phys',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('avail_page',ctypes.c_ulonglong),('total_virt',ctypes.c_ulonglong),('avail_virt',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
    value=Memory();value.length=ctypes.sizeof(value)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)):raise RuntimeError('memory_sample_failed')
    return value.avail_phys


def memory_gate(label,*,stage='base'):
    from control import active_segment
    segment=active_segment(state());amendments=segment.get('scheduling_amendments',[]) if segment else []
    profile=amendments[-1] if amendments else None
    if profile is None:minimum=2*1024**3
    else:
        if stage not in profile['stages_MiB']:raise RuntimeError('unknown_memory_stage')
        minimum=profile['stages_MiB'][stage]*1024**2
    available=available_memory_bytes()
    resources={'pg':[r['slot'] for r in state()['resources'] if r.get('kind')=='pg' and r.get('running')],
      'api':bool(getattr(_CONTROLLER,'api_running',False)),'browser':bool(getattr(_CONTROLLER,'browser_running',False)),
      'preview':bool(getattr(_CONTROLLER,'preview_running',False))}
    if stage=='second_pg' and any(resources[k] for k in ('api','browser','preview')):raise RuntimeError('second_pg_requires_consumers_stopped')
    event('memory_gate',label=label,stage=stage,available_bytes=available,minimum_bytes=minimum,docker_awake=True,
      resources=resources,profile=profile['profile'] if profile else 'original-2GiB')
    if available<minimum:raise RuntimeError('available_memory_below_stage_'+stage)
    return available


def pg_memory_gate(label):
    # Include factory targets in the same task resource ledger; fresh realtime sample each start.
    stage='second_pg' if any(r.get('running') for r in state()['resources'] if r.get('kind')=='pg') else 'pg'
    return memory_gate(label,stage=stage)


def port_gate(port):
    result=subprocess.run(['powershell','-NoProfile','-Command',f"Get-NetTCPConnection -LocalPort {int(port)} -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess | ConvertTo-Json -Compress"],capture_output=True,timeout=20)
    raw=result.stdout.decode('utf-8','replace').strip()
    if raw:
        try:rows=json.loads(raw)
        except ValueError:raise RuntimeError('port_owner_unknown') from None
        event('port_states',port=port,rows=rows)
        items=rows if isinstance(rows,list) else [rows]
        # Owner0的TIME_WAIT是已结束连接，不是监听者。仍须通过下方真实独占bind。
        if any(row.get('State') not in (11,'TimeWait','TIME_WAIT') or row.get('OwningProcess')!=0 for row in items):raise RuntimeError('port_in_use')
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        probe.bind(('127.0.0.1',port))
    event('port_bind_free',port=port,exclusive=True)


def metadata(cid):
    value=json.loads(docker(['inspect',cid]))[0]
    host=value['HostConfig']
    return {'cid':value['Id'],'name':value['Name'].removeprefix('/'),'image':value['Image'],'running':value['State']['Running'],
      'pid':value['State']['Pid'],'status':value['State']['Status'],'created':value['Created'],'started':value['State']['StartedAt'],
      'finished':value['State']['FinishedAt'],'labels':value['Config'].get('Labels',{}),'mounts':value.get('Mounts',[]),
      'memory':host['Memory'],'nano_cpus':host['NanoCpus'],'pids_limit':host['PidsLimit'],'restart_policy':host['RestartPolicy'],
      'port_bindings':host['PortBindings']}


def save_resource(row):
    value=state();old=next((r for r in value['resources'] if r.get('id')==row['id']),None)
    if old is None:value['resources'].append(row)
    else:old.update(row)
    write(HERE/'budget.json',value)


def create_pg(slot):
    guard()
    if slot not in SLOTS:raise RuntimeError('slot_not_authorized')
    port,db=SLOTS[slot];name='retrolume-step018-syn-'+slot;volume=name+'-data'
    pending=next((r for r in state()['resources'] if r.get('name')==name),None)
    if pending is not None and pending.get('cid') is not None:raise RuntimeError('already_created_use_exact_resume')
    if pending is not None and (pending.get('image')!=PG_IMAGE or pending.get('port')!=port or pending.get('slot')!=slot):raise RuntimeError('registered_identity_conflict')
    image=json.loads(docker(['image','inspect',PG_IMAGE]))[0]
    if (image['Id'],image['Os'],image['Architecture'])!=(PG_IMAGE,'linux','amd64'):raise RuntimeError('cached_pg_image_mismatch')
    pg_memory_gate('PG-'+slot);port_gate(port)
    if docker(['ps','-aq','--filter','name=^/'+name+'$']):raise RuntimeError('container_name_collision')
    if volume in docker(['volume','ls','--format','{{.Name}}']).splitlines():raise RuntimeError('volume_name_collision')
    if sum(bool(r.get('running')) for r in state()['resources'] if r.get('kind')=='pg')>=2:raise RuntimeError('pg_concurrency')
    row=pending or {'id':'pg-'+slot,'kind':'pg','slot':slot,'name':name,'volume':volume,'port':port,'database':db,'image':PG_IMAGE,'intent':sample(),'running':False,'cid':None}
    save_resource(row);event('pg_intent_resume' if pending else 'pg_intent',resource=row)
    PRIVATE.mkdir(parents=True,exist_ok=True)
    credential_path=PRIVATE/(slot+'.json')
    if credential_path.exists():raise RuntimeError('unexpected_private_file')
    credentials={'admin_user':'step018_'+slot.replace('-','_')+'_admin','admin_password':secrets.token_urlsafe(32),
      'app_user':'step018_'+slot.replace('-','_')+'_app','app_password':secrets.token_urlsafe(32),
      'snapshot_user':'step018_'+slot.replace('-','_')+'_snapshot','snapshot_password':secrets.token_urlsafe(32),'maintenance_key':secrets.token_hex(32)}
    write(credential_path,credentials)
    environment=dict(os.environ);environment.update(POSTGRES_USER=credentials['admin_user'],POSTGRES_PASSWORD=credentials['admin_password'],POSTGRES_DB=db)
    count('pg_create_attempts');count('volumes')
    cid=docker(['create','--pull=never','--name',name,'--label','retrolume.task=TASK-117','--label','retrolume.permit=TASK-117-STEP018-INTEGRATION-S01-20261014',
      '--label','retrolume.step018.slot='+slot,'--cpus','1','--memory','512m','--pids-limit','128','--restart','no',
      '--publish',f'127.0.0.1:{port}:5432','--mount',f'type=volume,src={volume},dst=/var/lib/postgresql/data',
      '--env','POSTGRES_USER','--env','POSTGRES_PASSWORD','--env','POSTGRES_DB',PG_IMAGE],environment=environment)
    if len(cid)!=64:raise RuntimeError('created_cid_unknown')
    count('pg_objects');row.update(cid=cid,created=sample());save_resource(row);event('pg_created',identity=metadata(cid))
    start_pg(slot)
    return row


def credentials(slot):
    if slot not in SLOTS:raise RuntimeError('slot_not_authorized')
    return json.loads((PRIVATE/(slot+'.json')).read_text(encoding='utf-8'))


def dsn(slot,role='app'):
    from psycopg.conninfo import make_conninfo
    value=credentials(slot);port,db=SLOTS[slot]
    return make_conninfo(host='127.0.0.1',port=port,dbname=db,user=value[role+'_user'],password=value[role+'_password'])


def start_pg(slot):
    require_controller(slot)
    row=next(r for r in state()['resources'] if r.get('id')=='pg-'+slot)
    actual=metadata(row['cid'])
    if actual['name']!=row['name'] or actual['image']!=PG_IMAGE or actual['labels'].get('retrolume.task')!='TASK-117':raise RuntimeError('resource_identity_changed')
    if actual['running']:
        if row.get('running'):return
        raise RuntimeError('unexpected_running_resource')
    # image inspect唤醒Docker之后的实时内存与固定端口；复启也计start。
    docker(['image','inspect',PG_IMAGE]);pg_memory_gate('PG-start-'+slot);port_gate(row['port'])
    count('pg_starts');stamp=sample();row.update(start_attempt=stamp,running=True,holding_start=stamp);save_resource(row)
    event('pg_start_attempt',slot=slot,cid=row['cid'])
    docker(['start',row['cid']]);event('pg_started',identity=metadata(row['cid']))
    import psycopg
    end=time.monotonic()+30
    while True:
        try:
            with psycopg.connect(dsn(slot,'admin'),connect_timeout=3):break
        except psycopg.Error:
            if time.monotonic()>=end:raise RuntimeError('pg_readiness_failed') from None
            time.sleep(.2)
    event('pg_ready',slot=slot,actual_user_database_from_task_credentials=True)


def stop_pg(slot):
    row=next(r for r in state()['resources'] if r.get('id')=='pg-'+slot)
    actual=metadata(row['cid'])
    if actual['name']!=row['name'] or actual['image']!=PG_IMAGE or actual['labels'].get('retrolume.task')!='TASK-117':raise RuntimeError('resource_identity_changed')
    if actual['running']:docker(['stop','--time','10',row['cid']],timeout=20)
    actual=metadata(row['cid'])
    if actual['running'] or actual['pid']!=0:raise RuntimeError('pg_stop_unknown')
    stamp=sample()
    if row.get('running'):
        row.setdefault('holding_intervals',[]).append({'start':row['holding_start'],'end':stamp,'segment':state().get('active_segment')})
    row.update(running=False,stopped=stamp)
    save_resource(row);event('pg_stopped',identity=actual,stamp=stamp)
    return actual
