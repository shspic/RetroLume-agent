"""受限连接修复的实际只读核验；保留预检错误，绝不进入apply。"""
import importlib.util,json,os,threading
from pathlib import Path
E=Path(__file__).absolute().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=load('task128_controller_verify',E/'run-six.py');I=load('task128_install_verify',M.ROOT/'deploy/initialize_normal.py');O=load('task128_error_verify',E/'install-observer.py')
c=M.Controller('entry05 最小连接修复后真实只读核验及空库门；不调用apply')
t=threading.Thread(target=c.memory_watch,daemon=True);t.start()
try:
    c.start_pg('source')
    cfg=json.loads((M.PRIVATE/'source/config/install.json').read_bytes());secret=c.secrets_for('source')
    with I.connect(cfg,secret) as conn:
        identity=conn.execute(I.IDENTITY_QUERY).fetchone()
        c.evidence('fixed-formal-connection.json',{'connected':True,'identity':identity,'service_environment_absent':not any(k in os.environ for k in ('PGSERVICE','PGSERVICEFILE'))})
        try:
            observed=I.preflight(conn,cfg)
            c.evidence('real-preflight.json',{'passed':True,'observed':observed})
        except I.InstallError as error:
            c.evidence('real-preflight.json',{'passed':False,'reason':error.args[0],**O.safe_diagnostic(error,list(secret.values()))})
        conn.execute('BEGIN READ ONLY')
        try:
            empty=conn.execute(I.EMPTY_QUERY).fetchone()
            c.evidence('actual-empty-facts.json',{'readonly':True,'empty_query':empty,'all_false':not any(empty.values())})
        finally:conn.execute('ROLLBACK')
finally:
    c.done.set()
    for slot in c.state['slots']:
        if c.state['slots'][slot].get('holding'):c.stop_pg(slot)
    t.join(4);c.state['last_entry']['status']='connection_verification_returned';c.save()
