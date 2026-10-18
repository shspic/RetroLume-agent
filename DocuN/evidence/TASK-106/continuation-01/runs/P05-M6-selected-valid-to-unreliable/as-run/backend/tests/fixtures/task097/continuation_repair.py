"""仅09失败/未覆盖及受影响夹具：不重复首续/硬停/来源撤销已成立场景。"""
import json, os, secrets, subprocess, sys, time, traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'DocuN/evidence/TASK-097/continuation-01'))
from control import E,C,PY,write,launch_guard
from tests.fixtures.task097 import continuation_run as b
from tests.fixtures.task097.persistent_fixture import retained_learning
from tests.fixtures.task097.processes import identity,cleanup
from tests.test_learning_config import config
from tests.fixtures.task097.samples import ENGLISH
import httpx

def main():
    code=1;owned=[];app=None
    try:
        old=E/'integration-09-combined';owner=json.loads((old/'retained-fixture.json').read_text(encoding='utf-8'))
        assert owner['task']=='TASK-097' and owner['permit']=='continuation-01' and Path(owner['root'])==b.originals
        fresh=json.loads((old/'browser-report.json').read_text(encoding='utf-8'))['fresh'];hardstop=json.loads((old/'hardstop.json').read_text(encoding='utf-8'))
        assert fresh['activity'] in owner['activities']
        reuse=retained_learning(b.fixture,b.OUT)
        setting=config();setting['activity_defaults'].update(max_requests=16,max_cost_microunits=1600000,max_running_seconds=900)
        cfg=b.OUT/'synthetic-config.json';cfg.write_text(json.dumps(setting),encoding='utf-8')
        env={**os.environ,'RETROLUME_DATA_DIR':str(b.runtime/'data'),'RETROLUME_BACKUP_DIR':str(b.runtime/'backup'),
            'RETROLUME_DATABASE_URL':b.DSN,'RETROLUME_ACTIVITY_CONFIG':str(cfg),'RETROLUME_TEST097_KEY':'synthetic-097-only','PYTHONIOENCODING':'utf-8'}
        app=subprocess.Popen([str(PY),'-B',str(Path(__file__).with_name('bootstrap.py')),'app'],env=env,cwd=ROOT,
            stdout=(b.OUT/'app.stdout.bin').open('wb'),stderr=(b.OUT/'app.stderr.bin').open('wb'))
        owned.append(identity(app.pid)|{'kind':'app'});write(b.OUT/'owned-processes.json',owned)
        b.client=httpx.Client(base_url='http://127.0.0.1:18097',trust_env=False)
        until=time.monotonic()+15
        while True:
            assert app.poll() is None
            try:
                r=b.client.get('/api/session',timeout=2)
                if r.status_code==200:break
            except httpx.TransportError:pass
            assert time.monotonic()<until;time.sleep(.1)
        b.client.headers['X-RetroLume-Session']=r.json()['token']
        def recovery_declared():
            # HTTP默认未声明旧running恢复，09正确失败关闭；不改产品默认或停止参数。
            # 本卡已明确限定同主机/交互会话、旧SUP/树0、来源有效；使用既有内部SUP入口显式声明该部署前提。
            from tests.fixtures.task097.bootstrap import install_launcher
            install_launcher() # 在run_one_call绑定之前安装真实回执观察器。
            from app.worker.one_call import run_one_call
            from app.worker.session import SessionConfig
            from app.service_config import load_activity_config
            from app.learning.contracts import read_document,canonical,request_fingerprint,LearningProfile,NEXT_PREFIX
            from app.learning.evidence import validate_snapshot,load_units,assemble_catalog
            from app.learning.prompt import messages_for
            from app.capabilities.contracts import ModelCallRequest,ResultConsumptionRef
            a=fresh['activity'];parent=fresh['followup'];before=b.sends();oldfact=b.facts(a)
            assert oldfact['running_reserved_seconds']==90 and oldfact['status']=='running'
            committed=b.execute(b.fixture.ledger.read_committed_result(a,parent));p,result=read_document(json.loads(committed.payload)['value'],activity_id=a,operation_id=parent)
            snap=b.execute(b.fixture.ledger.read_learning_snapshot(a));sources=validate_snapshot(snap);question='atomicity recovery examples';key=str(uuid4())
            values=dict(action='followup',activity_id=a,goal=p.goal,question=question,scope_revision=snap['scope_revision'],sources=[s.model_dump() for s in sources],parent_operation_id=parent,parent_payload_sha256=committed.payload_sha256,max_output_tokens=256)
            digest=request_fingerprint(**values);catalog=assemble_catalog(question,load_units(snap,b.fixture.materials,b.fixture.originals),digest)
            profile=LearningProfile(**values,request_sha256=digest,catalog=catalog,history=canonical(result.model_dump()))
            request=ModelCallRequest(messages=messages_for(profile),max_output_tokens=256,allowed_tools=frozenset(),input_result=ResultConsumptionRef(activity_id=a,operation_id=parent,scope_revision=committed.scope_revision,payload_sha256=committed.payload_sha256),learning_profile=profile)
            os.environ['RETROLUME_TEST097_KEY']='synthetic-097-only';svc=load_activity_config(cfg).model_service
            op=NEXT_PREFIX+key+'.'+digest
            outcome=run_one_call(b.fixture.ledger,SessionConfig(single_host_single_session_recovery=True),a,'task097-recovery',op,request,svc,run_tag='learn-'+secrets.token_hex(12))
            assert outcome.model_receipt and outcome.model_receipt['business_commit']=='committed' and not outcome.cleanup_incomplete,outcome
            assert outcome.active_processes_at_end==0 and outcome.generation>hardstop['session']['generation']
            fact=b.facts(a);assert fact['running_reserved_seconds']==0 and fact['running_settled_seconds']>=oldfact['running_settled_seconds']+90,fact
            assert fact['requests_reserved']==oldfact['requests_reserved']+1
            once=b.follow(a,parent,question,key);assert once[0]==200 and once[1]['operation_id']==op and once[1]['business']['read_status']=='committed_current',once
            assert b.sends()-before==1 and b.facts(a)['running_settled_seconds']==fact['running_settled_seconds']
            return {'declared_existing_precondition':True,'product_http_default_recovery_enabled':False,'old_fact':oldfact,'fact':fact,'generation':outcome.generation,'old_generation':hardstop['session']['generation'],'same_key_http_read':once,'fold_old_reservation_once':90,'actual_send_delta':1,'atomic':b.atomic(a,op)}
        b.test('legal_recovery_declared_existing_sup_fold_once',recovery_declared)
        def competing_fixed():
            source=b.fixture.text(ENGLISH,title='TASK097 C01 race repair.md');a=b.execute(b.fixture.activity([source]));before=b.sends();import threading
            barrier=threading.Barrier(2);goals=['Explain atomicity basics','Explain atomicity details']
            def contender(g):barrier.wait(timeout=5);return b.first(a,g)
            with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(contender,goals))
            row=b.req('GET',f'/api/activities/{a}/learning/intents/{uuid4()}?action=first')[1]['operation'];assert row and row['read_status']=='committed_current'
            assert b.sends()-before==1,responses
            actual=row['payload']['value']['goal'];assert actual in goals
            for g,(s,v) in zip(goals,responses):
                if g!=actual:assert s==409 or (s==200 and v['business']['read_status']!='committed_current'),responses
            launches=[json.loads(p.read_text(encoding='utf-8')) for p in b.OUT.glob('sup-launch-*.json')]
            sessions=[json.loads(p.read_text(encoding='utf-8')) for p in b.OUT.glob('session-*.json') if json.loads(p.read_text(encoding='utf-8'))['activity_id']==a]
            assert len(sessions)==2 and all(s['manager_pid'] is not None and not s['cleanup_incomplete'] for s in sessions),sessions
            return {'activity':a,'responses':responses,'goals':goals,'persistent_goal':actual,'send_delta':1,'real_supervisor_outcomes':sessions,'atomic':b.atomic(a,row['operation_id'])}
        b.test('different_goal_competition_atomic_observer_repair',competing_fixed)
        def bounds_http():
            rows=json.loads((old/'fixture-identities.json').read_text(encoding='utf-8'))['sources'];before=b.sends();before_sup=len(list(b.OUT.glob('sup-launch-*.json')))
            low=b.execute(b.fixture.activity([rows[0]],max_request_bytes=1024));status,value=b.first(low,'atomicity');assert status==413,value
            output=b.execute(b.fixture.activity([rows[0]],max_output_tokens=128));s,v=b.first(output,'atomicity');assert s==409 and v['detail']['code']=='output_token_limit',v
            empty=b.first(low,'');long=b.first(low,'x'*1025);assert empty[0]==400 and long[0]==422
            forged=b.req('GET',f"/api/activities/{reuse['activity']}/learning/operations/{reuse['first']}/citations/lc_forged");assert forged[0]==404,forged
            assert b.sends()==before and len(list(b.OUT.glob('sup-launch-*.json')))==before_sup
            assert b.facts(low)['requests_reserved']==b.facts(output)['requests_reserved']==0
            return {'request_limit':{'status':status,'body':value},'output_limit':{'status':s,'body':v},'empty':empty,'long':long,'forged_citation':forged,'send_delta':0,'sup_delta':0}
        b.test('http_bounds_and_forged_citation_zero_call',bounds_http)
        launch_guard('browser');driver=launch_guard('driver');write(b.OUT/'browser-launch.json',{'permit':'continuation-01','at':time.time(),'attempt_number':driver,'script':'frontend/tests/task097-continuation.mjs','repair_only':True})
        cases='lost_response_matching_conflict,unknown_same_key_retry_abandon,poll_no_overlap_hidden_unmount,bad_and_slow_citation_switch,slow_activity_detail_switch'
        browserenv={k:v for k,v in os.environ.items() if k not in {'RETROLUME_TASK097_DSN','RETROLUME_DATABASE_URL','RETROLUME_TEST097_KEY'}}
        browserenv.update(RETROLUME_TASK097_REUSE=json.dumps(reuse),RETROLUME_TASK097_FRESH=json.dumps(fresh),RETROLUME_TASK097_CASES=cases)
        node=subprocess.Popen(['node',str(ROOT/'frontend/tests/task097-continuation.mjs')],env=browserenv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        owned.append(identity(node.pid)|{'kind':'browser-runner'});write(b.OUT/'owned-processes.json',owned)
        stdout,stderr=node.communicate(timeout=210);(b.OUT/'browser.stdout.bin').write_bytes(stdout);(b.OUT/'browser.stderr.bin').write_bytes(stderr)
        print(stdout.decode('utf-8','replace'));print(stderr.decode('utf-8','replace'))
        report=json.loads((b.OUT/'browser-report.json').read_text(encoding='utf-8'));retained_learning(b.fixture,b.OUT)
        code=0 if node.returncode==0 and report['ok'] and all(x['status']=='PASS' for x in b.checks) else 1
    except Exception:traceback.print_exc()
    finally:
        if b.client:b.client.close()
        ok=cleanup(b.OUT)
        if app:
            try:app.wait(timeout=10)
            except subprocess.TimeoutExpired:ok=False
        # 新增修复临时行定向清理；09与07真实成果均保留以支撑最终回查。
        b.fixture.cleanup()
        write(b.OUT/'repair-summary.json',{'exit_code':code,'cleanup_ok':ok,'checks':b.checks,'sup_attempts':len(list(b.OUT.glob('sup-launch-*.json'))),'actual_sends':b.sends(),'preserved':['integration-07-browser','integration-09-combined']})
    return code if ok else 2
