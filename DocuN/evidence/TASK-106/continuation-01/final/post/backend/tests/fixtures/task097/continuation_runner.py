"""显式continuation-01单一资源入口，旧模式仍受初轮8次停门。"""
import json, os, secrets, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'backend'));sys.path.insert(0,str(ROOT/'DocuN/evidence/TASK-097/continuation-01'))
from control import E,C,PY,write,files,digest,permit,ledger,added,events,event,start_guard,freeze
from tests.fixtures.task097.resource_runner import CID,ADMIN,DB,ROLE,inspect_guard,free,docker,psql

def provision(out):
    owns=json.loads((E/'resource-ownership.json').read_text(encoding='utf-8'))
    facts=json.loads(psql("SELECT json_build_object('db_owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='"+DB+"'),'role_exists',EXISTS(SELECT 1 FROM pg_roles WHERE rolname='"+ROLE+"'),'role_sessions',(SELECT count(*) FROM pg_stat_activity WHERE usename='"+ROLE+"'));",'postgres'))
    assert owns['created_db']==DB and owns['created_role']==ROLE and owns['schema_initialized'] is True
    assert owns['container']==CID and facts=={'db_owner':ADMIN,'role_exists':True,'role_sessions':0}
    assert int(psql("SELECT count(*) FROM pg_tables WHERE schemaname='public';",DB))>0
    permissions=json.loads(psql("SELECT json_build_object('db',current_database(),'super',rolsuper,'create_db',rolcreatedb,'create_role',rolcreaterole,'replication',rolreplication,'bypass_rls',rolbypassrls,'member_count',(SELECT count(*) FROM pg_auth_members WHERE member=r.oid)) FROM pg_roles r WHERE rolname='"+ROLE+"';",DB))
    assert permissions['db']==DB and all(not permissions[k] for k in ['super','create_db','create_role','replication','bypass_rls','member_count'])
    write(out/'role-permissions.json',permissions)
    password=secrets.token_urlsafe(32)
    psql("ALTER ROLE "+ROLE+" PASSWORD '"+password+"';",'postgres',secret=True,label='role-password-stdin',out=out)
    return f'host=127.0.0.1 port=55441 dbname={DB} user={ROLE} password={password} connect_timeout=3'

def main(mode):
    assert mode in {'combined','repair','ui-only'},'未许可的续作模式'
    start_guard('entry')
    number=len(events('integration_entry'))+1;label=f'integration-{number:02d}-{mode}'
    out=E/label;out.mkdir();start=time.monotonic();started=False;identity_ok=False;code=1;error=None
    event({'category':'integration_entry','label':label,'entry_number':number,'started_at_epoch':time.time()})
    freeze(label,[str(PY),'-B',str(Path(__file__).with_name('resource_runner.py')),mode,'--permit','continuation-01'],
        'S2最终真实首续/浏览器，S3不同目标竞争/来源撤销/真实SUP截止硬停；独立UI反例；业务<=600/清理<=120')
    try:
        facts=inspect_guard();write(out/'container-pre.json',facts)
        assert not facts['running'] and facts['pid']==0,'精确资源有其他使用者'
        identity_ok=True
        for port in [18097,15197,55441]:free(port)
        start_guard('start');event({'category':'container_start','label':label,'container':CID})
        result=docker('start',CID);assert result.returncode==0,'容器启动失败';started=True
        until=time.monotonic()+20
        while docker('exec',CID,'pg_isready','-U',ADMIN,'-d','postgres',timeout=5).returncode:
            assert time.monotonic()<until,'PG就绪超时'
            time.sleep(.2)
        dsn=provision(out)
        remaining=min(600-(time.monotonic()-start),1200-sum(x.get('business_seconds',0) for x in added('integration_end')),3600-sum(x.get('business_seconds',0) for x in events('integration_end')))
        env={**os.environ,'RETROLUME_TASK097_DSN':dsn,'RETROLUME_TASK097_OUT':str(out),'RETROLUME_TASK097_PERMIT':'continuation-01','PYTHONIOENCODING':'utf-8'}
        cmd=[str(PY),'-B',str(Path(__file__).with_name('continuation_run.py')),mode]
        try:
            result=subprocess.run(cmd,cwd=ROOT,capture_output=True,env=env,timeout=remaining)
            (out/'stdout.bin').write_bytes(result.stdout);(out/'stderr.bin').write_bytes(result.stderr);code=result.returncode
            print(result.stdout.decode('utf-8','replace'));print(result.stderr.decode('utf-8','replace'))
        except subprocess.TimeoutExpired as exc:
            (out/'stdout.bin').write_bytes(exc.stdout or b'');(out/'stderr.bin').write_bytes(exc.stderr or b'');raise
    except BaseException as exc:
        error=type(exc).__name__+': '+str(exc)[:200];print(error)
    finally:
        cleanup_start=time.monotonic();business=cleanup_start-start;ok=True
        from tests.fixtures.task097.processes import cleanup
        try:ok=cleanup(out)
        except Exception as exc:ok=False;write(out/'cleanup-error.json',{'error':type(exc).__name__})
        if started:
            try:
                r=docker('stop','--time','5',CID,timeout=30);facts=inspect_guard();write(out/'container-post.json',facts)
                ok=ok and r.returncode==0 and not facts['running'] and facts['pid']==0
            except Exception:ok=False
        # 未经本入口启动的其他资源绝不终止。
        if identity_ok:
            for port in [18097,15197,55441]:
                try:free(port)
                except OSError:ok=False
        elapsed=time.monotonic()-cleanup_start
        fact={'category':'integration_end','label':label,'exit_code':code,'error':error,'business_seconds':business,'cleanup_seconds':elapsed,'total_seconds':time.monotonic()-start,'container_started':started,'cleanup_ok':ok,'business_limit':600,'cleanup_limit':120}
        write(out/'run.json',fact);event(fact)
        write(out/'post-hashes.json',{p.relative_to(ROOT).as_posix():digest(p) for p in files()})
    return code if ok else 2
