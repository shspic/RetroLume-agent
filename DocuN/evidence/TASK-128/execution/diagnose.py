"""唯一source诊断启动：真实控制与正式连接对照，只读，不运行apply。"""
import importlib.util,json,sys
from pathlib import Path
E=Path(__file__).absolute().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
M=load('task128_controller',E/'run-six.py')
O=load('task128_observer',E/'install-observer.py')
I=load('task128_installer',M.ROOT/'deploy/initialize_normal.py')
import os,threading
values=['synthetic-'+str(i)+'-noncredential-0000' for i in range(4)]
synthetic=O.safe_diagnostic(ValueError(' '.join(values)+' postgresql://test:example@127.0.0.1/db'),values)
assert all(v not in json.dumps(synthetic) for v in values)
assert 'postgresql://' not in json.dumps(synthetic)
if (E/'diagnostic-safety.json').exists():assert json.loads((E/'diagnostic-safety.json').read_bytes())=={'synthetic':synthetic,'passed':True}
else:
    with (E/'diagnostic-safety.json').open('x',encoding='utf-8') as out:json.dump({'synthetic':synthetic,'passed':True},out)
c=M.Controller('entry04 同身份只读连接对照诊断，无apply或DDL')
t=threading.Thread(target=c.memory_watch,daemon=True);t.start()
try:
    for slot in c.state['slots']:
        c.configure_slot(slot)
        assert not c.inspect(slot)['state']['Running']
        assert [M.WIN.file_identity(Path(r['path'])) for r in c.state['slots'][slot]['roots']]==c.state['slots'][slot]['roots']
    c.start_pg('source')
    cfg=json.loads((M.PRIVATE/'source/config/install.json').read_bytes())
    secrets=c.secrets_for('source')
    for key,value in secrets.items():os.environ[cfg['credential_env'][key]]=value
    formal=I.read_credentials(cfg)
    c.evidence('credentials-equal.json',{'all_four_byte_equal':all(formal[k].encode()==v.encode() for k,v in secrets.items()),'same_environment':True,'psycopg_version':M.psycopg.__version__})
    results=[]
    for name,fn in [('control',lambda:M.psycopg.connect(**c.pg_kwargs('source'))),('formal',lambda:I.connect(cfg,formal))]:
        try:
            with fn() as conn:
                identity=conn.execute(I.IDENTITY_QUERY).fetchone()
                results.append({'case':name,'connected':True,'identity':identity})
        except BaseException as error:
            results.append({'case':name,'connected':False,**O.safe_diagnostic(error,list(secrets.values()))})
    c.evidence('connection-comparison.json',results)
    print(json.dumps(results,ensure_ascii=True))
finally:
    c.done.set()
    for slot in c.state['slots']:
        if c.state['slots'][slot].get('holding'):c.stop_pg(slot)
    t.join(4);c.state['last_entry']['status']='diagnostic_returned';c.save()
