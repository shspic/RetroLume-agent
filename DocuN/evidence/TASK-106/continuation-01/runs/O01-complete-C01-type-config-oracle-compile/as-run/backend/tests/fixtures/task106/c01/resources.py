"""Reuse exact initial106 CIDs. No create/bootstrap/grants; two app PW resets max."""
import hashlib,json,os,secrets,subprocess,time
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import EVIDENCE,INPUT,PERMIT,atomic_json,event,reserve

IMAGE='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
APP='retrolume_task106_app';BOOT='retrolume_task106_bootstrap'

def cli(args):
    r=subprocess.run(['docker',*args],capture_output=True,text=True,encoding='utf-8',timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    if r.returncode:raise RuntimeError('C01 exact Docker operation failed')
    return r.stdout

def spec(n):return json.loads(INPUT.read_text(encoding='utf-8'))['resources_now']['containers'][n-1]

def inspect(n):
    expected=spec(n);obj=json.loads(cli(['inspect',expected['cid']]))[0];h=obj['HostConfig'];labels=obj['Config']['Labels']
    assert obj['Id']==expected['cid'] and obj['Name']=='/'+expected['name'] and obj['Image']==IMAGE
    assert labels==expected['labels'] and labels['retrolume.permit']=='TASK-106-G10-20261008'
    assert h['Memory']==536870912 and h['NanoCpus']==1000000000 and h['PidsLimit']==128 and not h['Privileged'] and not h.get('CapAdd') and h['RestartPolicy']['Name']=='no'
    mounts=obj['Mounts'];assert len(mounts)==1 and mounts[0]['Type']=='volume' and mounts[0]['Name']==expected['name']+'-data' and mounts[0]['Destination']=='/var/lib/postgresql/data'
    assert h['PortBindings']==expected['ports']
    return obj

def public(obj):
    return dict(cid=obj['Id'],name=obj['Name'],image=obj['Image'],labels=obj['Config']['Labels'],mounts=obj['Mounts'],
                state={k:obj['State'][k] for k in ('Running','Pid','Status','StartedAt','FinishedAt')},action_permit=PERMIT,original_labels_unchanged=True)

def bootstrap(n):
    obj=inspect(n);pw=next(x.split('=',1)[1] for x in obj['Config']['Env'] if x.startswith('POSTGRES_PASSWORD='));s=spec(n)
    return psycopg.conninfo.make_conninfo(host='127.0.0.1',port=s['port'],dbname=s['database'],user=BOOT,password=pw,connect_timeout=3)

def start(n):
    for other in (1,2,3):
        obj=inspect(other)
        assert not obj['State']['Running'],'C01 start requires all reused PG stopped'
    reserve('container_start',dict(n=n,cid=spec(n)['cid']));cli(['start',spec(n)['cid']]);dsn=bootstrap(n)
    until=time.perf_counter()+20
    while True:
        try:
            with psycopg.connect(dsn,autocommit=True) as conn:conn.execute('SELECT 1')
            break
        except psycopg.Error:
            if time.perf_counter()>until:raise RuntimeError('C01 owned PG readiness failed') from None
            time.sleep(.2)
    event('pg-start',public(inspect(n)));return dsn

def stop(n):
    obj=inspect(n)
    if obj['State']['Running']:cli(['stop','--time','10',obj['Id']])
    obj=inspect(n);assert not obj['State']['Running'] and obj['State']['Pid']==0;event('pg-stop',public(obj))

def role_shape(conn):
    role=conn.execute("SELECT to_jsonb(r)-'rolpassword' AS role FROM pg_roles r WHERE rolname=%s",(APP,)).fetchone()['role']
    memberships=[dict(x) for x in conn.execute("SELECT roleid::regrole::text AS role,member::regrole::text AS member,admin_option,inherit_option,set_option FROM pg_auth_members WHERE member=%s::regrole ORDER BY roleid::regrole::text",(APP,)).fetchall()]
    acls=[dict(x) for x in conn.execute("SELECT relname,relacl::text AS acl FROM pg_class WHERE relnamespace='public'::regnamespace AND relkind IN ('r','v') ORDER BY relname").fetchall()]
    return dict(role=role,membership=memberships,acl=acls)

def runtime(dsn,n):
    pw=secrets.token_urlsafe(32)
    with psycopg.connect(dsn,autocommit=True,row_factory=dict_row) as conn:
        before=role_shape(conn);r=before['role'];assert r['rolcanlogin'] and not any(r[k] for k in ('rolsuper','rolcreatedb','rolcreaterole','rolbypassrls'))
        assert not any(x['role'] in ('retrolume_interview_owner','retrolume_memory_owner','retrolume_memory_purger') for x in before['membership'])
        reserve('password_reset',dict(role=APP,cid=spec(n)['cid'],only_password=True))
        conn.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(APP),sql.Literal(pw)))
        after=role_shape(conn);assert before==after
    atomic_json(EVIDENCE/'resources'/f'pg{n}-ordinary-role-before-after.json',dict(before=before,after=after,equal=True,no_grants=True,password_not_saved=True))
    values=psycopg.conninfo.conninfo_to_dict(dsn);app=psycopg.conninfo.make_conninfo(**{**values,'user':APP,'password':pw})
    with psycopg.connect(app,row_factory=dict_row) as conn:
        row=conn.execute('SELECT current_user AS role').fetchone();assert row['role']==APP
    return app
