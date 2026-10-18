"""原TASK117有限批运行适配：资源启动前登记同一截止控制器。"""
from pathlib import Path
import sys,os,json,time,subprocess,secrets,hmac,hashlib
C01=Path(__file__).resolve().parent;EXEC=C01.parent;ROOT=EXEC.parents[3]
sys.path[:0]=[str(EXEC),str(ROOT/'backend'),str(ROOT/'backend/tests/fixtures/step018')]
import control as c
import runtime_control as rc
from lifecycle import BoundedResources
from app.preview.description import canonical
from app.preview.process import birth

PREVIEW_IMAGE='sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789'

def preflight(label,*,preview=False):
    rc.docker(['image','inspect',rc.PG_IMAGE]);rc.memory_gate(label+'-Docker-awake',stage='base')
    resources=[rc.metadata(r['cid']) for r in c.state()['resources'] if r.get('cid') and r.get('kind')=='pg']
    if any(r['running'] or r['pid']!=0 for r in resources):raise RuntimeError('own_pg_still_running')
    for port in (*range(15481,15488),18118):rc.port_gate(port)
    info=json.loads(rc.docker(['info','--format','{{json .}}']))
    if info['KernelVersion']!='6.6.114.1-microsoft-standard-WSL2':raise RuntimeError('adopted_kernel_changed')
    if preview:
        image=json.loads(rc.docker(['image','inspect',PREVIEW_IMAGE]))[0]
        if (image['Id'],image['Os'],image['Architecture'])!=(PREVIEW_IMAGE,'linux','amd64'):raise RuntimeError('preview_cached_identity')
    receipt={'sample':c.sample(),'pg':resources,'kernel':info['KernelVersion'],'preview_checked':preview}
    c.write(C01/(label+'-preflight-'+str(time.time_ns())+'.json'),receipt)
    return receipt


def configuration(*,max_requests=None):
    operator=C01/'operator';operator.mkdir(exist_ok=True)
    key=secrets.token_urlsafe(48)
    ticket={'schema':'retrolume.preview.review.v2','decision':'approved','image_id':PREVIEW_IMAGE,
      'load_manifest_sha256':'8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f',
      'renderer_sha256':'6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597',
      'result_sha256':'1dab1126aa72e335288d037baed5bc13b7cfdc1e4a386b6c04553e630f871571'}
    ticket['signature']=hmac.new(key.encode(),canonical(ticket).encode(),hashlib.sha256).hexdigest()
    ticket_file=operator/'preview.review.json'
    if ticket_file.exists():
        raw=ticket_file.read_bytes();(operator/('review.previous-'+c.sha(raw)+'.json')).write_bytes(raw)
        c.event('S02_preview_normal_rekey',old_sha256=c.sha(raw),reason='原operator授权同一独审事实；仅部署认证key更换，不签新审核')
    c.write(ticket_file,ticket)
    host=json.loads((EXEC/'root04-preview-host.json').read_text())
    c.write(operator/'preview.deployment.json',{'schema':'retrolume.preview.deployment.v2','docker':host['docker'],
      'image_id':PREVIEW_IMAGE,'load_manifest_sha256':ticket['load_manifest_sha256'],'renderer_sha256':ticket['renderer_sha256'],
      'kernel_release':'6.6.114.1-microsoft-standard-WSL2','review_ticket':str(ticket_file),'review_key_env':'RETROLUME_TASK117_PREVIEW_REVIEW_KEY'})
    identity={'provider':'deepseek_chat_completions','model':'deepseek-chat'}
    activity={'model_identity':identity,'activity_defaults':{'deadline_hours':24,'max_requests':80,'max_cost_microunits':20000000,'reserve_cost_microunits':250000,'max_request_bytes':65536,'max_output_tokens':4096,'max_running_seconds':3600,'allowed_tools':['finite_calculate'],'max_tool_calls':8},
      'service':{'base_url':'https://api.deepseek.com','thinking':'disabled','timeout_seconds':10,'max_output_tokens_limit':4096,'max_request_bytes':65536,'max_response_bytes':65536},'api_key_env':'RETROLUME_MODEL_API_KEY',
      'learning':{'profile':'learning.v2','max_output_tokens':256},'teaching':{'profile':'teaching.v3','max_output_tokens':2048,'enable_calculation':True},'interview':{'profile':'interview.v2','max_output_tokens':2048,'max_followups_per_round':2},'html':{'profile':'html_explanation.v2','max_output_tokens':4096},
      'memory_context':{'selected_items':4,'max_memory_bytes':4096,'max_memory_chars':2048,'model_context_tokens':65536,'max_input_tokens_estimate':50000,'protocol_reserve_tokens':2048,'reserved_output_tokens':2048,'safety_tokens':2048,'estimate_policy':'utf8_bytes.v1','model_identity':identity}}
    if max_requests is not None:
        if max_requests!=1:raise RuntimeError('only_exact_S05_one_request_boundary_allowed')
        activity['activity_defaults']['max_requests']=1
    c.write(operator/'activity.json',activity)
    c.write(operator/'integration.json',{'schema':'retrolume.integration.v1','enabled':True,'embedding':{'provider':'zhipu_embeddings','base_url':'https://open.bigmodel.cn/api/paas/v4','model':'embedding-3','dimensions':512,'returned_models':['embedding-3'],'timeout_seconds':10,'max_request_bytes':32768,'max_response_bytes':65536},'max_index_fragments':32})
    c.write(operator/'data-exit.json',{'enabled':True,'snapshot_url_env':'RETROLUME_TASK117_SNAPSHOT','maintenance_key_env':'RETROLUME_TASK117_MAINTENANCE'})
    env=dict(os.environ)
    import sysconfig
    env.update(PYTHONPATH=os.pathsep.join([str(ROOT/'backend/tests/fixtures/step018'),str(ROOT/'backend'),sysconfig.get_paths()['purelib']]),RETROLUME_TASK117_SYNTHETIC=c.state()['active_segment'],
      RETROLUME_TASK117_TRANSPORT_LOG=str(C01/'transport.jsonl'),RETROLUME_TASK117_TRACE_PG='0',RETROLUME_DATABASE_URL=rc.dsn('source'),RETROLUME_TASK117_SNAPSHOT=rc.dsn('source','snapshot'),RETROLUME_TASK117_MAINTENANCE=rc.credentials('source')['maintenance_key'],
      RETROLUME_TASK117_LATE_GATE=str(C01/'late-transport'),
      RETROLUME_DATA_DIR=str(EXEC/'synthetic/source-data'),RETROLUME_BACKUP_DIR=str(EXEC/'synthetic/source-backup'),RETROLUME_CONTROL_ROOT=str(EXEC/'synthetic/source-control'),RETROLUME_RESTORE_ROOT=str(EXEC/'synthetic/source-restore'),
      RETROLUME_DATA_EXIT_CONFIG=str(operator/'data-exit.json'),RETROLUME_ACTIVITY_CONFIG=str(operator/'activity.json'),RETROLUME_INTEGRATION_CONFIG=str(operator/'integration.json'),RETROLUME_PREVIEW_CONFIG=str(operator/'preview.deployment.json'),
      RETROLUME_TASK117_PREVIEW_REVIEW_KEY=key,RETROLUME_MODEL_API_KEY=secrets.token_urlsafe(32),RETROLUME_EMBEDDING_API_KEY=secrets.token_urlsafe(32))
    return env


class Batch:
    def __init__(self,number,label):
        if c.state()['active_root'] is None:
            if c.state()['counts']['roots']==number:
                proof=max(C01.glob('root'+str(number).zfill(2)+'-stop-*.json'),key=lambda p:p.stat().st_mtime_ns)
                c.resume_root(number,stop_evidence=proof)
            elif c.state()['counts']['roots']+1==number:c.begin_root(label,'runtime')
            else:raise RuntimeError('next_root_identity')
        if c.state()['active_root']!=number:raise RuntimeError('root_identity')
        root=next(r for r in c.state()['roots'] if r['id']==number)
        self.number,self.label=number,'root'+str(number).zfill(2)
        self.id=str(time.time_ns());self.api=None;self.api_log=None;self.browser=None;self.browser_log=None
        self.marker=C01/(self.label+'-accepting')
        self.run=BoundedResources(deadline=root['business_deadline_mono_ns']/1e9,on_close=lambda p:c.write(C01/(self.label+'-cleanup-'+self.id+'.json'),{**p,'sample':c.sample()}))
        self.run.monitor_memory(rc.available_memory_bytes)
        rc.bind_controller(self.run)
    def __enter__(self):
        self.run.__enter__();self.run.register('reject-new-mutations',self.reject,priority=100)
        return self
    def reject(self):
        self.marker.unlink(missing_ok=True);return {'accepting':False}
    def fresh_api_handle(self):
        # Separate immutable owner object per launch; all stages share this original deadline.
        child=object.__new__(Batch)
        child.number,child.label,child.id=self.number,self.label,self.id+'-stage-'+str(time.time_ns())
        child.run,child.marker=self.run,self.marker
        child.api=child.api_log=child.browser=child.browser_log=None
        return child
    def start_api(self,*,launcher=False,read_only_factory=False,source_slot='source',max_requests=None):
        self.run.check();rc.port_gate(18118)
        rc.docker(['image','inspect',rc.PG_IMAGE]);rc.memory_gate('API-start',stage='api')
        if self.api is not None:raise RuntimeError('one_api_per_launch_handle')
        self.run.register('api-normal-lifespan-and-preview',self.close_api,priority=30)
        env=configuration(max_requests=max_requests);self.marker.write_text('accepting',encoding='ascii')
        if read_only_factory:
            from profiles_batch import factory_profile
            path=C01/'operator/data-exit-readonly-view.json'
            c.write(path,{'enabled':True,'snapshot_url_env':'RETROLUME_TASK117_SNAPSHOT','maintenance_key_env':'RETROLUME_TASK117_MAINTENANCE','factory':factory_profile()})
            env['RETROLUME_DATA_EXIT_CONFIG']=str(path)
        if source_slot!='source':
            if source_slot!='compat' or launcher or read_only_factory:raise RuntimeError('only_exact_normal_compat_fixture_allowed')
            restore=EXEC/'synthetic/compat-restore';restore.mkdir(exist_ok=True)
            env.update(RETROLUME_DATABASE_URL=rc.dsn('compat'),RETROLUME_TASK117_SNAPSHOT=rc.dsn('compat','snapshot'),RETROLUME_TASK117_MAINTENANCE=rc.credentials('compat')['maintenance_key'],
              RETROLUME_DATA_DIR=str(EXEC/'synthetic/compat-data'),RETROLUME_BACKUP_DIR=str(EXEC/'synthetic/compat-backup'),RETROLUME_CONTROL_ROOT=str(EXEC/'synthetic/compat-control'),RETROLUME_RESTORE_ROOT=str(restore))
        self.env=env
        c.count('api_starts');self.api_attempt=c.state()['counts']['api_starts']
        env.update(RETROLUME_TASK117_ACCEPTING=str(self.marker),RETROLUME_TASK117_API_PROOF=str(C01/f'api-proof-{self.api_attempt}.json'))
        self.api_log=(C01/f'api-{self.api_attempt}.log').open('wb')
        c.write(C01/f'api-{self.api_attempt}-as-run.json',{'sample':c.sample(),
            'files':[{'path':str(p.relative_to(ROOT)),'sha256':c.sha(p.read_bytes())} for p in (ROOT/'backend/app').rglob('*.py')],
            'operator_config_sha256':c.sha((C01/'operator/activity.json').read_bytes()),'max_requests_override':max_requests,'source_slot':source_slot})
        command=[str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8']
        command+=([str(ROOT/'deploy/start_local.py'),'--port','18118','--container','retrolume-step018-syn-source','--shutdown-stdin'] if launcher else ['-m','server'])
        self.api=subprocess.Popen(command,cwd=ROOT/'backend',env=env,stdin=subprocess.PIPE,stdout=self.api_log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        self.api_birth=birth(self.api.pid)
        self.run.api_running=True
        c.event('S02_api_launch',attempt=self.api_attempt,pid=self.api.pid,birth=self.api_birth,normal_launcher=launcher,hidden=True,stdin_owned=True)
        import httpx
        deadline=min(time.monotonic()+35,self.run.deadline)
        while time.monotonic()<deadline:
            self.run.check()
            if self.api.poll() is not None:raise RuntimeError('api_exit_before_ready')
            c.count('http')
            try:
                r=httpx.get('http://127.0.0.1:18118/health',timeout=1,trust_env=False)
                if r.status_code==200:return
            except httpx.HTTPError:pass
            time.sleep(.3)
        raise RuntimeError('api_not_ready')
    def close_api(self):
        self.reject()
        if self.api is None:return {'not_started':True}
        graceful=True
        if self.api.poll() is None:
            try:self.api.stdin.write(b'stop\n');self.api.stdin.flush();self.api.wait(timeout=self.run.remaining_cleanup(175))
            except (OSError,ValueError,subprocess.TimeoutExpired):
                graceful=False;self.api.terminate()
                try:self.api.wait(timeout=self.run.remaining_cleanup(5))
                except subprocess.TimeoutExpired:self.api.kill();self.api.wait(timeout=3)
        self.api_log.close();self.run.api_running=False
        proof={'pid':self.api.pid,'birth_before':self.api_birth,'birth_after':birth(self.api.pid),'exit_code':self.api.returncode,'graceful':graceful,'owned_launch_handle_waited':True,'sample':c.sample()}
        c.write(C01/f'api-stop-{self.api_attempt}.json',proof);self.env.clear()
        if not graceful:raise RuntimeError('api_lifespan_unconfirmed')
        self.api=None
        return proof
    def start_reader_api(self,target,dsn):
        self.run.check();rc.port_gate(18118);rc.memory_gate('isolated-reader-API',stage='api')
        self.run.register('reader-API-owned-lifespan',self.close_api,priority=30)
        if self.api is not None:raise RuntimeError('reader_api_already_started')
        paths={}
        for name in ('backup','restore','control'):
            p=C01/('reader-r01-'+name);p.mkdir(exist_ok=True);paths[name]=p
        operator=C01/'operator';operator.mkdir(exist_ok=True);config=operator/'reader-r01.json'
        c.write(config,{'enabled':True,'reader':{'readonly_url_env':'RETROLUME_READER_DATABASE_URL','target_id':target.target_id,
            'dataset_id':target.dataset_id,'instance_id':target.instance_id,'schema_profile':target.schema_profile}})
        allowed={'PATH','PATHEXT','COMSPEC','SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','HOMEDRIVE','HOMEPATH','PROGRAMFILES','PROGRAMFILES(X86)'}
        env={k:v for k,v in os.environ.items() if k.upper() in allowed}
        env.update(PYTHONPATH=str(ROOT/'backend'),RETROLUME_DATABASE_URL=dsn,RETROLUME_READER_DATABASE_URL=dsn,
            RETROLUME_DATA_DIR=str(target.data_root),RETROLUME_BACKUP_DIR=str(paths['backup']),RETROLUME_RESTORE_ROOT=str(paths['restore']),
            RETROLUME_CONTROL_ROOT=str(paths['control']),RETROLUME_DATA_EXIT_CONFIG=str(config),
            RETROLUME_ACTIVITY_CONFIG=str(ROOT/'config/activity.example.json'),RETROLUME_READER_PROOF=str(C01/'reader-host-proof.json'))
        self.env=env;self.marker.write_text('accepting',encoding='ascii')
        c.count('api_starts');self.api_attempt=c.state()['counts']['api_starts']
        sources=[{'path':str(p.relative_to(ROOT)),'sha256':c.sha(p.read_bytes())} for p in (ROOT/'backend/app').rglob('*.py')]
        c.write(C01/f'api-{self.api_attempt}-as-run.json',{'sample':c.sample(),'files':sources,'config_sha256':c.sha(config.read_bytes()),'execution_credentials':False,'target_id':target.target_id})
        self.api_log=(C01/f'api-{self.api_attempt}.log').open('wb')
        self.api=subprocess.Popen([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(C01/'reader_server.py')],cwd=ROOT/'backend',env=env,
            stdin=subprocess.PIPE,stdout=self.api_log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        self.api_birth=birth(self.api.pid);self.run.api_running=True
        c.event('S05_reader_api_launch',attempt=self.api_attempt,pid=self.api.pid,birth=self.api_birth,source_writer_credentials=False)
        import httpx
        end=min(time.monotonic()+35,self.run.deadline)
        while time.monotonic()<end:
            self.run.check()
            if self.api.poll() is not None:raise RuntimeError('reader_api_exit_before_ready')
            c.count('http')
            try:
                if httpx.get('http://127.0.0.1:18118/health',timeout=1,trust_env=False).status_code==200:return
            except httpx.HTTPError:pass
            time.sleep(.3)
        raise RuntimeError('reader_api_not_ready')
    def start_browser(self,phase,*,resume=None):
        self.run.check();rc.docker(['image','inspect',PREVIEW_IMAGE]);rc.memory_gate('browser-'+phase,stage='browser')
        if self.browser is not None:raise RuntimeError('one_browser_per_handle')
        self.run.register('browser-owned-handle',self.close_browser,priority=60)
        c.count('browser_starts');self.browser_attempt=c.state()['counts']['browser_starts']
        allowed={'PATH','PATHEXT','COMSPEC','SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','HOMEDRIVE','HOMEPATH','PROGRAMFILES','PROGRAMFILES(X86)','PLAYWRIGHT_BROWSERS_PATH'}
        env={k:v for k,v in os.environ.items() if k.upper() in allowed}
        env.update(RETROLUME_TASK117_EVIDENCE=str(C01),RETROLUME_TASK117_CONTROL=str(EXEC),RETROLUME_TASK117_BROWSER_ATTEMPT=str(self.browser_attempt),RETROLUME_TASK117_BROWSER_PHASE=phase)
        if resume:env['RETROLUME_TASK117_RESUME_PROOF']=str(resume)
        self.browser_log=(C01/f'browser-{self.browser_attempt}.log').open('wb')
        browser_script='step018-s05-reader.mjs' if phase=='reader' else 'step018-s05-budget.mjs' if phase=='budget' else 'step018-s05.mjs'
        self.browser=subprocess.Popen(['node',str(ROOT/'frontend/tests'/browser_script)],cwd=ROOT/'frontend',env=env,stdin=subprocess.PIPE,stdout=self.browser_log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        self.browser_birth=birth(self.browser.pid)
        self.run.browser_running=True
        c.event('S02_browser_launch',attempt=self.browser_attempt,pid=self.browser.pid,birth=self.browser_birth,phase=phase,hidden=True,no_service_secrets=True)
        try:self.browser.wait(timeout=min(540,max(1,self.run.deadline-time.monotonic())))
        except subprocess.TimeoutExpired:raise RuntimeError('browser_batch_timeout') from None
        proof_path=C01/f'browser-{self.browser_attempt}/proof.json'
        if self.browser.returncode!=0:raise RuntimeError('browser_failed_read_exact_log')
        proof=json.loads(proof_path.read_text())
        if proof.get('status')!='passed' or proof.get('browser_closed') is not True:raise RuntimeError('browser_proof_incomplete')
        return proof
    def close_browser(self):
        if self.browser is None:return {'not_started':True}
        graceful=True
        if self.browser.poll() is None:
            try:self.browser.stdin.write(b'stop\n');self.browser.stdin.flush();self.browser.wait(timeout=self.run.remaining_cleanup(35))
            except (OSError,ValueError,subprocess.TimeoutExpired):
                graceful=False;self.browser.terminate()
                try:self.browser.wait(timeout=5)
                except subprocess.TimeoutExpired:self.browser.kill();self.browser.wait(timeout=3)
        self.browser_log.close();self.run.browser_running=False
        path=C01/f'browser-{self.browser_attempt}/proof.json';body=json.loads(path.read_text()) if path.exists() else {}
        proof={'pid':self.browser.pid,'birth_before':self.browser_birth,'birth_after':birth(self.browser.pid),'exit_code':self.browser.returncode,'owned_handle_waited':True,'browser_close_observed':body.get('browser_closed') is True,'graceful':graceful,'sample':c.sample()}
        c.write(C01/f'browser-stop-{self.browser_attempt}.json',proof)
        if not graceful or body.get('browser_closed') is not True:raise RuntimeError('browser_stop_unconfirmed')
        self.browser=None
        return proof
    def __exit__(self,kind,value,tb):
        self.run.__exit__(kind,value,tb)
        rows=[]
        for r in c.state()['resources']:
            if r.get('kind')=='pg' and r.get('cid'):rows.append(rc.metadata(r['cid']))
        from profiles_batch import listeners
        fixed=listeners();stopped=bool(self.run.report and self.run.report['all_confirmed']) and all(not r['running'] and r['pid']==0 for r in rows) and not fixed
        c.write(C01/(self.label+'-stop-'+self.id+'.json'),{'sample':c.sample(),'pg':rows,'listeners':fixed,'cleanup':self.run.report,'all_stopped':stopped})
        if stopped:c.end_root(result=self.label+(' failed, cleaned' if kind else ' completed, cleaned'))
        else:raise RuntimeError('batch_stop_unconfirmed')
        return False
