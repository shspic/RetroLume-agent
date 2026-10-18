"""真实SUP/停线/selector/HTTP/最终bundle合并根，保源和准确树证明。"""
import asyncio
from dataclasses import asdict
from datetime import datetime,timezone,timedelta
import json
import os
from pathlib import Path
import socket
import subprocess
import threading
import time
from uuid import uuid4
from budget import ROOT,EVIDENCE
from setup_source import start_source,stop_source,memory_guard,IMAGE
from app.data_exit.restore import TargetFactory,inspect_target
from app.data_exit.contracts import DataError,canonical,digest
from app.runtime import psycopg_compatible_loop_factory
from app.preview.process import birth

def run(work):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(work)

def integrate_group(budget,evidence,source,credentials):
    from continue_run import runtime_for
    from matrix_pg import environment
    from app.activities import ActivitySpec,SourceSnapshot
    from app.worker.one_tool import run_one_tool
    from app.worker.session import SessionConfig
    from app.capabilities.contracts import ToolExecutionInput,canonical_tool_arguments
    import psycopg
    selected=EVIDENCE/'batches/c01-overlay-1138863453000000/respect_plan-02-verified.json'
    verified=json.loads(selected.read_bytes())
    if not start_source(budget,source):raise RuntimeError('source内存门不足')
    api=None;api_identity=None;browser=None;browser_identity=None;chosen=None
    try:
        TargetFactory._wait_pg(credentials['admin_dsn']);app,rt=runtime_for(credentials,budget);ledger=app.state.activities_ledger
        current=json.loads((ROOT/'DocuN/evidence/TASK-114/implementation/control/source-full-fixture.json').read_bytes())['source']
        material=app.state.materials.get(current['id'])
        aid=str(uuid4())
        run(ledger.create_activity(ActivitySpec(activity_id=aid,sources=(SourceSnapshot(material['id'],material['version_id'],material['revision']),),
            deadline_at=datetime.now(timezone.utc)+timedelta(hours=1),max_requests=8,max_cost_microunits=1000,reserve_cost_microunits=1,
            max_request_bytes=65536,max_output_tokens=256,max_running_seconds=60,allowed_models=(('deepseek_chat_completions','c01-synthetic'),),allowed_tools=('finite_calculate',),max_tool_calls=4)))
        raw,sha=canonical_tool_arguments({'operation':'add','left':1,'right':2});call=ToolExecutionInput('c01-finite-tool','c01.calc','finite_calculate',raw,sha)
        cfg=SessionConfig(window_seconds=15,request_timeout_seconds=1,stop_grace_seconds=1,startup_limit_seconds=3,manager_db_timeout_seconds=3,cleanup_seconds=3,mutex_wait_seconds=1,manager_overhead_seconds=20)
        budget.reserve('windows_start');native_identity='native-c01:'+aid
        budget.created(native_identity,'windows',{'activity_id':aid,'purpose':'unchanged real SUP finite tool with new data fence'});budget.begin(native_identity)
        try:
            outcome=run_one_tool(ledger,cfg,aid,'c01-executor-'+aid,call,run_tag='c01-data-fence')
            evidence.observe('01-native-supervisor',asdict(outcome))
            if outcome.cleanup_incomplete or outcome.active_processes_at_end!=0:raise RuntimeError('原SUP停止证据未齐')
        finally:
            if 'outcome'in locals():budget.end(native_identity,{'manager_pid':outcome.manager_pid,'manager_birth':outcome.manager_created_100ns,'active_processes':outcome.active_processes_at_end,'cleanup_incomplete':outcome.cleanup_incomplete})
        # 有真实注册的有限服务仍在收尾时不能切；不拿旧历史unknown当新owner。
        with rt.gate.acquire(outgoing=True):owned=rt.gate.register_owned('domain_service',{'parent':{'pid':os.getpid(),'birth':birth(os.getpid())['birth']},'service':'c01-finite-result-close'})
        async def gate_checks():
            try:await rt.maintenance.drain_for_readonly_switch(0,time.monotonic()+.05)
            except DataError as e:
                if e.code!='maintenance_unconfirmed':raise
                evidence.observe('02-incomplete-owned-blocks-switch',{'code':e.code,'source_mode':rt.source.state()['mode'],'selector':rt.hub.state()['selection']})
            else:raise RuntimeError('已有注册收尾未结束却允许切换')
            try:
                with rt.gate.acquire(outgoing=True):pass
            except DataError as e:
                if e.code!='maintenance_unconfirmed':raise
            else:raise RuntimeError('draining仍准新出站')
            with rt.gate.close_lane(owned):await ledger.cancel_activity(aid)
            rt.gate.end_owned(owned,confirmed=True,proof_sha256=digest('finite existing result lane ended'))
        run(gate_checks())
        # selector COMMIT之后精确注入丢返回；GET同原键必须由journal给相同generation。
        key='c01-select-'+str(uuid4());update=rt.hub.update_job;lost={'raised':False}
        def lose(job_id,revision,**changes):
            if changes.get('state')=='active_readonly' and not lost['raised']:
                lost['raised']=True;raise OSError('C01 lost response after selector COMMIT')
            return update(job_id,revision,**changes)
        rt.hub.update_job=lose
        try:
            try:run(rt.restore.activate_readonly(verified['job_id'],verified['plan_sha256'],key,0))
            except OSError:
                if not lost['raised']:raise
        finally:rt.hub.update_job=update
        receipt=rt.hub.get_by_key(key)
        if receipt['state']!='active_readonly' or receipt['selection_generation']!=1:raise RuntimeError('丢回应后selector不确定')
        repeated=run(rt.restore.activate_readonly(verified['job_id'],verified['plan_sha256'],key,0))
        if repeated['selection_generation']!=1:raise RuntimeError('重复激活二增代次')
        evidence.observe('03-selector-lost-response',{'receipt':receipt,'repeated':repeated,'source_state':rt.source.state(),'selection':rt.hub.state()['selection']})
        chosen=rt.factory.target(verified['target_id'])
        # 全28表普通app逐行UPDATE在frozen拒绝，保具体permission或guard原因。
        from app.data_exit.schema import COLUMNS
        from app.data_exit.contracts import TABLES
        rejected=[]
        for table in TABLES:
            col=next(iter(COLUMNS[table]));sql='UPDATE public.'+table+' SET '+col+'='+col
            try:
                with psycopg.connect(credentials['app_dsn'],connect_timeout=3) as conn:conn.execute(sql)
            except psycopg.Error as e:rejected.append({'table':table,'sqlstate':e.sqlstate,'message_primary':e.diag.message_primary})
            else:raise RuntimeError('frozen仍可写表: '+table)
        evidence.observe('04-all-source-write-tables-rejected',rejected)
        # 真HTTP沿已提交selector绑定；认证token仅内存，不出日志。
        environment(credentials)
        with socket.socket() as s:s.bind(('127.0.0.1',18114))
        budget.reserve('api_start');budget.reserve('windows_start')
        with (evidence.path/'api.log').open('xb') as log:
            api=subprocess.Popen([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(ROOT/'backend/tests/fixtures/task114/api_boot.py')],cwd=ROOT,env=dict(os.environ),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            born=birth(api.pid);api_identity='api:'+str(api.pid)+':'+str(born['birth']);budget.created(api_identity,'api',{'pid':api.pid,'birth':born['birth'],'port':18114});budget.begin(api_identity)
            import httpx
            with httpx.Client(base_url='http://127.0.0.1:18114',timeout=5) as client:
                end=time.monotonic()+20
                while True:
                    try:
                        if client.get('/health').status_code==200:break
                    except httpx.TransportError:pass
                    if api.poll() is not None or time.monotonic()>end:raise RuntimeError('真实readonly API未就绪')
                    time.sleep(.1)
                token=client.get('/api/session').json()['token'];headers={'X-RetroLume-Session':token};caps=client.get('/api/data/capabilities',headers=headers).json()
                if caps['current_mode']!='restored_readonly':raise RuntimeError('实际HTTP未读取选中副本')
                reads=[]
                for category in ('activities','learning','teaching','interview','memories','preview_history','versions'):
                    response=client.get('/api/data/saved-records?category='+category,headers=headers)
                    if response.status_code!=200:raise RuntimeError('真实只读类别不能回查: '+category)
                    reads.append({'category':category,'count':len(response.json()['items'])})
                old='ead33e27-3e1a-4d6f-9e91-8433af5a390b';response=client.get('/api/materials/'+old+'/content',headers=headers)
                if response.status_code!=404:raise RuntimeError('当前删除覆盖正文仍可读')
                ctx={k:caps[k] for k in ('control_id','selection_generation','dataset_id','instance_id','current_mode','read_only')};post={**headers,'Origin':'http://127.0.0.1:18114','X-RetroLume-Data-Context':canonical(ctx)}
                denied=[]
                for route in ('/api/materials?filename=c01.txt','/api/activities','/api/activities/'+aid+'/cancel','/api/activities/'+aid+'/teaching/local','/api/activities/'+aid+'/interview/local'):
                    response=client.post(route,content=b'x',headers=post)
                    if response.status_code!=409 or response.json().get('code')!='data_readonly':raise RuntimeError('readonly POST没有被全局门拒绝')
                    denied.append({'path':route,'status':response.status_code,'code':response.json()['code']})
                evidence.observe('05-readonly-HTTP',{'caps':caps,'reads':reads,'source_deleted_body_status':404,'business_POST_rejected':denied})
                if not memory_guard()['ready']:raise RuntimeError('浏览器内存门不足；只读HTTP原件已保存')
                output=evidence.path/'browser';output.mkdir();profile=ROOT/'DocuN/evidence/TASK-114/synthetic/scratch'/('c01-readonly-browser-'+str(uuid4()));profile.mkdir()
                budget.reserve('browser_start');budget.reserve('windows_start')
                args=[str(Path('C:/Program Files/nodejs/node.exe')),str(ROOT/'frontend/tests/task114-c01-readonly.mjs'),str(output),str(profile)]
                browser=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
                born=birth(browser.pid);browser_identity='browser:'+str(browser.pid)+':'+str(born['birth']);budget.created(browser_identity,'browser',{'pid':browser.pid,'birth':born['birth'],'profile':str(profile)});budget.begin(browser_identity)
                stdout,stderr=browser.communicate(timeout=60);evidence.observe('06-browser',{'arguments':args,'exit_code':browser.returncode,'stdout':stdout,'stderr':stderr,'both_pipes_eof':True})
                if browser.returncode:raise RuntimeError('最终readonly浏览器失败，保原件')
        return {'state':'passed','selection_generation':1,'selected_target_id':chosen.target_id,'source_frozen':True,'provider_calls':0}
    finally:
        for child,identity in ((browser,browser_identity),(api,api_identity)):
            if child is None:continue
            if child.poll() is None:child.terminate()
            child.wait(timeout=10)
            if identity:budget.end(identity,{'pid':child.pid,'process_ended':True,'exit_code':child.returncode})
        if chosen is not None:rt.factory.stop(chosen)
        stop_source(budget,source)
