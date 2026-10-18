"""只补损坏/保存失败的客户端写前关闭，0SUP/模型；余下浏览器额度一次。"""
import json,os,subprocess,time,traceback
from pathlib import Path
from control import E,PY,write,launch_guard
from tests.fixtures.task097 import continuation_run as b
from tests.fixtures.task097.persistent_fixture import retained_learning
from tests.fixtures.task097.processes import identity,cleanup
from tests.test_learning_config import config
import httpx

def main():
    app=None;code=1
    try:
        reuse=retained_learning(b.fixture,b.OUT)
        sources=json.loads((E/'integration-07-browser/fixture-identities.json').read_text(encoding='utf-8'))['sources']
        source=next(s for s in sources if s['format']=='md')
        empty=b.execute(b.fixture.activity([source]))
        write(b.OUT/'empty-activity.json',{'activity':empty,'source':source,'model_results_seeded':False})
        setting=config();cfg=b.OUT/'synthetic-config.json';cfg.write_text(json.dumps(setting),encoding='utf-8')
        env={**os.environ,'RETROLUME_DATA_DIR':str(b.runtime/'data'),'RETROLUME_BACKUP_DIR':str(b.runtime/'backup'),'RETROLUME_DATABASE_URL':b.DSN,'RETROLUME_ACTIVITY_CONFIG':str(cfg),'RETROLUME_TEST097_KEY':'synthetic-097-only','PYTHONIOENCODING':'utf-8'}
        app=subprocess.Popen([str(PY),'-B',str(Path(__file__).with_name('bootstrap.py')),'app'],env=env,cwd=b.ROOT,stdout=(b.OUT/'app.stdout.bin').open('wb'),stderr=(b.OUT/'app.stderr.bin').open('wb'))
        owned=[identity(app.pid)|{'kind':'app'}];write(b.OUT/'owned-processes.json',owned)
        b.client=httpx.Client(base_url='http://127.0.0.1:18097',trust_env=False);until=time.monotonic()+15
        while True:
            assert app.poll() is None
            try:
                r=b.client.get('/api/session',timeout=2)
                if r.status_code==200:break
            except httpx.TransportError:pass
            assert time.monotonic()<until;time.sleep(.1)
        b.client.headers['X-RetroLume-Session']=r.json()['token']
        driver=launch_guard('driver');launch_guard('browser')
        write(b.OUT/'browser-launch.json',{'permit':'continuation-01','at':time.time(),'attempt_number':driver,'script':'frontend/tests/task097-continuation.mjs','ui_only':True})
        browserenv={k:v for k,v in os.environ.items() if k not in {'RETROLUME_TASK097_DSN','RETROLUME_DATABASE_URL','RETROLUME_TEST097_KEY'}}
        browserenv.update(RETROLUME_TASK097_REUSE=json.dumps(reuse),RETROLUME_TASK097_CASES='corrupt_picked_material_no_post,storage_failure_before_learning_post')
        node=subprocess.Popen(['node',str(b.ROOT/'frontend/tests/task097-continuation.mjs')],env=browserenv,cwd=b.ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        owned.append(identity(node.pid)|{'kind':'browser-runner'});write(b.OUT/'owned-processes.json',owned)
        stdout,stderr=node.communicate(timeout=90);(b.OUT/'browser.stdout.bin').write_bytes(stdout);(b.OUT/'browser.stderr.bin').write_bytes(stderr);print(stdout.decode('utf-8','replace'));print(stderr.decode('utf-8','replace'))
        report=json.loads((b.OUT/'browser-report.json').read_text(encoding='utf-8'))
        assert not list(b.OUT.glob('sup-launch-*.json')) and b.sends()==0
        fact=b.facts(empty);assert fact['requests_reserved']==0 and fact['cost_reserved_microunits']==0
        write(b.OUT/'ui-zero-call-facts.json',{'empty_activity':fact,'sup_attempts':0,'transport_sends':0,'old07_preserved':True})
        retained_learning(b.fixture,b.OUT);code=0 if node.returncode==0 and report['ok'] else 1
    except Exception:traceback.print_exc()
    finally:
        if b.client:b.client.close()
        ok=cleanup(b.OUT)
        if app:
            try:app.wait(timeout=10)
            except subprocess.TimeoutExpired:ok=False
        b.fixture.cleanup();write(b.OUT/'ui-summary.json',{'exit_code':code,'cleanup_ok':ok,'sup_launches':0,'model_sends':b.sends()})
    return code if ok else 2
