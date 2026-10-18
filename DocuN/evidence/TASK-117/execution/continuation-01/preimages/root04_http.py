"""正常operator验签、API子进程和两链；秘钥只活在控制器内存及受控子env。"""
from control import *
from runtime_control import dsn,credentials,port_gate,metadata
import os,sys,json,hmac,hashlib,secrets,subprocess,time
sys.path.insert(0,str(ROOT/'backend'))
from app.preview.description import canonical

def main():
    guard()
    if state()['active_root']!=4:raise RuntimeError('root_identity')
    operator=HERE/'synthetic/operator';operator.mkdir(parents=True,exist_ok=True)
    host=json.loads((HERE/'root04-preview-host.json').read_text())
    if host['kernel']!='6.6.114.1-microsoft-standard-WSL2':raise RuntimeError('preview_kernel_mismatch')
    ticket={'schema':'retrolume.preview.review.v2','decision':'approved','image_id':host['image'],'load_manifest_sha256':'8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f','renderer_sha256':'6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597','result_sha256':'1dab1126aa72e335288d037baed5bc13b7cfdc1e4a386b6c04553e630f871571'}
    key=secrets.token_urlsafe(48)
    ticket['signature']=hmac.new(key.encode(),canonical(ticket).encode(),hashlib.sha256).hexdigest()
    tp=operator/'preview.review.json'
    if tp.exists():
        old=tp.read_bytes();(operator/f'preview.review.previous-{sha(old)}.json').write_bytes(old);event('preview_ticket_rekey',old_sha256=sha(old),reason='本卡控制器重新启动，旧内存key不读取不复用，正常认证同一冻结审核事实')
    write(tp,ticket)
    deployment={k:host[k] for k in ('docker',)}
    deployment.update(schema='retrolume.preview.deployment.v2',image_id=ticket['image_id'],load_manifest_sha256=ticket['load_manifest_sha256'],renderer_sha256=ticket['renderer_sha256'],kernel_release=host['kernel'],review_ticket=str(tp),review_key_env='RETROLUME_TASK117_PREVIEW_REVIEW_KEY')
    write(operator/'preview.deployment.json',deployment)
    activity={'model_identity':{'provider':'deepseek_chat_completions','model':'deepseek-chat'},'activity_defaults':{'deadline_hours':24,'max_requests':80,'max_cost_microunits':20000000,'reserve_cost_microunits':250000,'max_request_bytes':65536,'max_output_tokens':4096,'max_running_seconds':3600,'allowed_tools':['finite_calculate'],'max_tool_calls':8},'service':{'base_url':'https://api.deepseek.com','thinking':'disabled','timeout_seconds':10,'max_output_tokens_limit':4096,'max_request_bytes':65536,'max_response_bytes':65536},'api_key_env':'RETROLUME_MODEL_API_KEY','learning':{'profile':'learning.v2','max_output_tokens':256},'teaching':{'profile':'teaching.v3','max_output_tokens':2048,'enable_calculation':True},'interview':{'profile':'interview.v2','max_output_tokens':2048,'max_followups_per_round':2},'html':{'profile':'html_explanation.v2','max_output_tokens':4096}}
    write(operator/'activity.json',activity)
    embedding={'provider':'zhipu_embeddings','base_url':'https://open.bigmodel.cn/api/paas/v4','model':'embedding-3','dimensions':512,'returned_models':['embedding-3'],'timeout_seconds':10,'max_request_bytes':32768,'max_response_bytes':65536}
    write(operator/'integration.json',{'schema':'retrolume.integration.v1','enabled':True,'embedding':embedding,'max_index_fragments':8})
    write(operator/'data-exit.json',{'enabled':True,'snapshot_url_env':'RETROLUME_TASK117_SNAPSHOT','maintenance_key_env':'RETROLUME_TASK117_MAINTENANCE'})
    env=dict(os.environ);fixture=ROOT/'backend/tests/fixtures/step018'
    env.update(PYTHONPATH=str(fixture)+os.pathsep+str(ROOT/'backend'),RETROLUME_TASK117_SYNTHETIC=PERMIT,RETROLUME_TASK117_TRANSPORT_LOG=str(HERE/'root04-transport.jsonl'),RETROLUME_TASK117_TRACE_PG='1',RETROLUME_DATABASE_URL=dsn('source'),RETROLUME_TASK117_SNAPSHOT=dsn('source','snapshot'),RETROLUME_TASK117_MAINTENANCE=credentials('source')['maintenance_key'],RETROLUME_DATA_DIR=str(HERE/'synthetic/source-data'),RETROLUME_BACKUP_DIR=str(HERE/'synthetic/source-backup'),RETROLUME_CONTROL_ROOT=str(HERE/'synthetic/source-control'),RETROLUME_RESTORE_ROOT=str(HERE/'synthetic/source-restore'),RETROLUME_DATA_EXIT_CONFIG=str(operator/'data-exit.json'),RETROLUME_ACTIVITY_CONFIG=str(operator/'activity.json'),RETROLUME_INTEGRATION_CONFIG=str(operator/'integration.json'),RETROLUME_PREVIEW_CONFIG=str(operator/'preview.deployment.json'),RETROLUME_TASK117_PREVIEW_REVIEW_KEY=key,RETROLUME_MODEL_API_KEY=secrets.token_urlsafe(32),RETROLUME_EMBEDDING_API_KEY=secrets.token_urlsafe(32),RETROLUME_TASK117_API_PROOF=str(operator/'api-proof.json'))
    port_gate(18118);count('api_starts');attempt=state()['counts']['api_starts']
    proof=operator/'api-proof.json'
    if proof.exists():(operator/f'api-proof-before-attempt-{attempt}.json').write_bytes(proof.read_bytes())
    log=(HERE/f'root04-api-{attempt}.txt').open('wb')
    proc=subprocess.Popen([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8','-m','uvicorn','server:create_app','--factory','--loop','app.runtime:psycopg_compatible_loop_factory','--host','127.0.0.1','--port','18118'],cwd=ROOT/'backend',env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP)
    event('api_started',pid=proc.pid,attempt=attempt,hidden=True,exact_launch_handle=True)
    try:
        import httpx
        end=time.monotonic()+25
        while True:
            if proc.poll() is not None:raise RuntimeError('api_start_failed')
            count('http')
            try:
                r=httpx.get('http://127.0.0.1:18118/health',timeout=1,trust_env=False)
                if r.status_code==200:break
            except httpx.HTTPError:pass
            if time.monotonic()>end:raise RuntimeError('api_readiness_timeout')
            time.sleep(.2)
        if '--serve' in sys.argv:
            import importlib
            request_path=HERE/'root04-command.json';seen=None
            if request_path.exists():seen=json.loads(request_path.read_text())['key']
            print('TASK117 own API ready; bounded controller active',flush=True)
            deadline=time.monotonic()+2400
            while time.monotonic()<deadline:
                guard()
                if request_path.exists():
                    work=json.loads(request_path.read_text())
                    if work['key']!=seen:
                        seen=work['key'];command=work['command']
                        if command=='stop':break
                        try:
                            if command=='flow':
                                import http_flows;importlib.reload(http_flows)
                                flow=http_flows.Flow()
                                try:ids=flow.run()
                                finally:flow.client.close()
                                event('two_http_chains_passed',ids=ids)
                            elif command=='browser':
                                from runtime_control import docker,memory_gate
                                docker(['image','inspect',host['image']]);memory_gate('browser');count('browser_starts')
                                result=subprocess.run(['node',str(ROOT/'frontend/tests/step018-flow.mjs')],cwd=ROOT/'frontend',env={**env,'RETROLUME_TASK117_EVIDENCE':str(HERE)},capture_output=True,timeout=180)
                                (HERE/f'root04-browser-{seen}.txt').write_bytes(result.stdout+result.stderr)
                                if result.returncode:raise RuntimeError('browser_flow_failed')
                            else:raise RuntimeError('unknown_controller_command')
                            write(HERE/f'root04-command-result-{seen}.json',{'command':command,'status':'passed',**sample()})
                            print(command+' passed',flush=True)
                        except Exception as error:
                            failure('ROOT04-'+command,type(error).__name__+':'+str(error)[:650])
                            write(HERE/f'root04-command-result-{seen}.json',{'command':command,'status':'failed','reason':str(error)[:700],**sample()})
                            print(command+' failed: '+str(error)[:500],flush=True)
                time.sleep(.5)
        else:
            from http_flows import Flow
            flow=Flow();ids=flow.run();flow.client.close()
            event('two_http_chains_passed',ids=ids)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:proc.wait(timeout=20)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
        log.close();event('api_stopped',pid=proc.pid,exit_code=proc.returncode,launch_handle_wait_confirmed=True)
        key=None;env.clear()

if __name__=='__main__':
    try:main()
    except Exception as e:failure('ROOT04-http',type(e).__name__+':'+str(e)[:650],effect='保留原键/命令/UNKNOWN与预算；只修有据根因，不删除数据库');raise
