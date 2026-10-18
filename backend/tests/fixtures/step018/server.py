"""真实API与正常配置loader；只安装本轮最低传输替身。"""
import json,os,sys
from pathlib import Path
from runtime_fixture import install

def create_app():
    if not install():raise RuntimeError('synthetic_permit_missing')
    from app.main import create_app as product
    app=product()
    config=app.state.activity_config
    proof={'api_pid':os.getpid(),'preview_config_exists':Path(os.environ['RETROLUME_PREVIEW_CONFIG']).is_file(),'preview_key_present':bool(os.environ.get('RETROLUME_TASK117_PREVIEW_REVIEW_KEY')),'normal_loader_accepted':app.state.preview_policy is not None,'authorization':app.state.preview_policy.authorization if app.state.preview_policy else None,'integration_available':app.state.integration_config.available,'data_exit_error':app.state.data_exit_error,'layers':{k:getattr(config,k).available for k in ('create_layer','continue_layer','teaching_layer','interview_model_layer','html_generation_layer')}}
    proof['python']={'executable':sys.executable,'base_executable':sys._base_executable,'prefix':sys.prefix}
    path=Path(os.environ['RETROLUME_TASK117_API_PROOF']);path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    if not all(proof['layers'].values()) or not proof['normal_loader_accepted'] or proof['data_exit_error'] is not None:raise RuntimeError('normal_deployment_not_ready')
    return app


def main():
    """精确stdin关闭句柄触发uvicorn原正常退出；无管理HTTP后门。"""
    import asyncio,threading,sys
    import uvicorn
    from app.runtime import psycopg_compatible_loop_factory
    app=create_app()
    marker=Path(os.environ['RETROLUME_TASK117_ACCEPTING'])
    @app.middleware('http')
    async def bounded_admission(request,call_next):
        if request.method not in ('GET','HEAD','OPTIONS') and not marker.exists() and not request.url.path.endswith('/stop'):
            from fastapi.responses import JSONResponse
            return JSONResponse({'detail':{'code':'controller_stopping','message':'本轮已停止接收新动作，请只读核对'}},status_code=503)
        return await call_next(request)
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=18118,timeout_graceful_shutdown=150,log_level='warning'))
    def commands():
        # EOF也关闭，不把API从父控制器断开后留存。
        sys.stdin.readline();server.should_exit=True
    threading.Thread(target=commands,name='task117-api-owned-shutdown',daemon=True).start()
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(server.serve())

if __name__=='__main__':main()
