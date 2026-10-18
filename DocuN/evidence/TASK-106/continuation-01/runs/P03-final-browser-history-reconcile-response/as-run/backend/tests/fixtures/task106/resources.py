"""Only the three named new clusters. Secrets are RAM/Env, never argv/artifacts."""
from __future__ import annotations
import json,os,secrets,subprocess,time
from pathlib import Path
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import ROOT,EVIDENCE,PERMIT,reserve,locked,atomic_json,event

IMAGE='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
BOOT='retrolume_task106_bootstrap'
APP='retrolume_task106_app'
DENIED='retrolume_task106_denied'
SPECS={1:('retrolume_task106_main',55446),2:('retrolume_task106_upgrade',55447),3:('retrolume_task106_fault',55448)}


def cli(args,env=None):
    result=subprocess.run(['docker',*args],env=env,capture_output=True,text=True,encoding='utf-8',timeout=30,
        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode:raise RuntimeError('owned Docker operation failed: '+result.stderr[:800])
    return result.stdout.strip()


def inspect(cid):
    return json.loads(cli(['inspect',cid]))[0]


def freeze(obj,number):
    name=f'retrolume-task-106-g10-pg{number}';volume=name+'-data';db,port=SPECS[number]
    labels=obj['Config'].get('Labels',{})
    assert obj['Name']=='/'+name and obj['Image']==IMAGE
    assert labels.get('retrolume.task')=='TASK-106' and labels.get('retrolume.permit')==PERMIT and labels.get('retrolume.synthetic')=='true'
    h=obj['HostConfig'];assert h['Memory']==536870912 and h['NanoCpus']==1000000000 and h['PidsLimit']==128
    assert not h['Privileged'] and not h.get('CapAdd') and h['RestartPolicy']['Name']=='no'
    mounts=obj['Mounts'];assert len(mounts)==1 and mounts[0]['Type']=='volume' and mounts[0]['Name']==volume and mounts[0]['Destination']=='/var/lib/postgresql/data'
    binding=h['PortBindings']['5432/tcp'];assert binding==[{'HostIp':'127.0.0.1','HostPort':str(port)}]
    return dict(number=number,cid=obj['Id'],name=name,volume=volume,database=db,port=port,image=obj['Image'],labels=labels,
        mounts=mounts,quota=dict(memory=h['Memory'],nano_cpus=h['NanoCpus'],pids=h['PidsLimit'],restart=h['RestartPolicy'],cap_add=h.get('CapAdd'),privileged=h['Privileged']),
        binding=binding,created=obj['Created'],state={k:obj['State'][k] for k in ('Running','Pid','Status','StartedAt','FinishedAt')})


def resource(number):
    with locked() as state:value=state['resources'].get(f'pg{number}')
    return value


def create(number):
    if resource(number):return resource(number)
    name=f'retrolume-task-106-g10-pg{number}';volume=name+'-data';db,port=SPECS[number]
    assert not cli(['container','ls','-a','--filter','name=^/'+name+'$','--format','{{.ID}}'])
    assert not cli(['volume','ls','--filter','name=^'+volume+'$','--format','{{.Name}}'])
    labels=['--label','retrolume.task=TASK-106','--label','retrolume.permit='+PERMIT,'--label','retrolume.synthetic=true']
    reserve('volume_create',{'name':volume});cli(['volume','create',*labels,volume])
    env=os.environ.copy();env['POSTGRES_PASSWORD']=secrets.token_urlsafe(32)
    reserve('container_create',{'name':name})
    cid=cli(['create','--pull=never','--name',name,*labels,'--cpus','1','--memory','512m','--pids-limit','128','--restart','no',
        '-p',f'127.0.0.1:{port}:5432','--mount',f'type=volume,source={volume},target=/var/lib/postgresql/data',
        '-e','POSTGRES_PASSWORD','-e','POSTGRES_USER='+BOOT,'-e','POSTGRES_DB='+db,IMAGE],env)
    env.pop('POSTGRES_PASSWORD',None)
    owned=freeze(inspect(cid),number)
    with locked() as state:state['resources'][f'pg{number}']=owned
    atomic_json(EVIDENCE/'resources'/f'pg{number}-created.json',owned)
    return owned


def bootstrap_dsn(number):
    owned=resource(number);assert owned
    obj=inspect(owned['cid']);freeze(obj,number)
    # Explicit card authorization: only own exact-CID Env password item in RAM.
    entry=next(x for x in obj['Config']['Env'] if x.startswith('POSTGRES_PASSWORD='))
    password=entry.split('=',1)[1]
    return psycopg.conninfo.make_conninfo(host='127.0.0.1',port=owned['port'],dbname=owned['database'],user=BOOT,password=password,connect_timeout=3)


def stop(number):
    owned=resource(number)
    if not owned:return
    before=freeze(inspect(owned['cid']),number)
    if before['state']['Running']:cli(['stop','--time','10',owned['cid']])
    after=freeze(inspect(owned['cid']),number)
    assert not after['state']['Running'] and after['state']['Pid']==0
    atomic_json(EVIDENCE/'resources'/f'pg{number}-stopped-{time.time_ns()}.json',after)
    with locked() as state:state['resources'][f'pg{number}']=after


def start(number):
    owned=create(number)
    for other in SPECS:
        if other==number:continue
        previous=resource(other)
        if previous:
            obj=freeze(inspect(previous['cid']),other)
            assert not obj['state']['Running'],'one PG at a time'
    obj=freeze(inspect(owned['cid']),number)
    if obj['state']['Running']:return bootstrap_dsn(number)
    reserve('container_start',{'number':number,'cid':owned['cid']});cli(['start',owned['cid']])
    dsn=bootstrap_dsn(number)
    last=None
    for _ in range(25):
        try:
            with psycopg.connect(dsn,autocommit=True) as conn:conn.execute('SELECT 1').fetchone()
            break
        except psycopg.Error:last=True;time.sleep(.4)
    else:raise RuntimeError('owned PostgreSQL startup timeout')
    ready=freeze(inspect(owned['cid']),number);atomic_json(EVIDENCE/'resources'/f'pg{number}-running-{time.time_ns()}.json',ready)
    with locked() as state:state['resources'][f'pg{number}']=ready
    return dsn


def runtime(dsn):
    passwords={APP:secrets.token_urlsafe(32),DENIED:secrets.token_urlsafe(32)}
    with psycopg.connect(dsn,autocommit=True,row_factory=dict_row) as conn:
        for user,pw in passwords.items():
            exists=conn.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(user,)).fetchone()
            statement=sql.SQL('ALTER ROLE {} WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}') if exists else sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}')
            conn.execute(statement.format(sql.Identifier(user),sql.Literal(pw)))
        conn.execute(sql.SQL('GRANT USAGE ON SCHEMA public TO {}').format(sql.Identifier(APP)))
        privileges={
            'material_sources':'SELECT,INSERT,UPDATE','material_versions':'SELECT,INSERT',
            'activities':'SELECT,INSERT,UPDATE','activity_scope_sources':'SELECT,INSERT,DELETE','activity_allowed_models':'SELECT,INSERT',
            'activity_operations':'SELECT,INSERT,UPDATE','activity_operation_results':'SELECT,INSERT',
            'teaching_heads':'SELECT,INSERT,UPDATE','teaching_commands':'SELECT,INSERT,UPDATE','teaching_records':'SELECT,INSERT',
            'pdf_review_candidates':'SELECT,INSERT,UPDATE','pdf_review_pages':'SELECT,INSERT,UPDATE',
            'pdf_extracted_pages':'SELECT,INSERT','pdf_user_supplements':'SELECT,INSERT',
        }
        existing={r['tablename'] for r in conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'").fetchall()}
        for table,allowed in privileges.items():
            if table in existing:
                conn.execute(sql.SQL('GRANT '+allowed+' ON public.{} TO {}').format(sql.Identifier(table),sql.Identifier(APP)))
        # The old approved capability role supplies only its existing selection/
        # eligibility rights. No blanket EXECUTE and no owner/purger membership.
        conn.execute(sql.SQL('GRANT retrolume_memory_app TO {}').format(sql.Identifier(APP)))
        interview=conn.execute("SELECT 1 FROM pg_roles WHERE rolname='retrolume_interview_app'").fetchone() is not None
        if interview:conn.execute(sql.SQL('GRANT retrolume_interview_app TO {}').format(sql.Identifier(APP)))
        rows=conn.execute("SELECT rolname,rolsuper,rolcreatedb,rolcreaterole,rolbypassrls,rolcanlogin FROM pg_roles WHERE rolname=ANY(%s) ORDER BY rolname",([APP,DENIED,'retrolume_interview_owner','retrolume_interview_app'],)).fetchall()
        membership=conn.execute("SELECT CASE WHEN EXISTS(SELECT 1 FROM pg_roles WHERE rolname='retrolume_interview_owner') THEN pg_has_role(%s,'retrolume_interview_owner','MEMBER') ELSE false END AS owner,pg_has_role(%s,'retrolume_memory_purger','MEMBER') AS purger",(APP,APP)).fetchone()
        assert not membership['owner'] and not membership['purger'] and all(not r['rolsuper'] and not r['rolcreatedb'] and not r['rolcreaterole'] and not r['rolbypassrls'] for r in rows)
        atomic_json(EVIDENCE/'resources'/'runtime-attributes.json',dict(rows=rows,memberships=membership))
    values=psycopg.conninfo.conninfo_to_dict(dsn)
    app=psycopg.conninfo.make_conninfo(**{**values,'user':APP,'password':passwords[APP]})
    denied=psycopg.conninfo.make_conninfo(**{**values,'user':DENIED,'password':passwords[DENIED]})
    return app,denied
