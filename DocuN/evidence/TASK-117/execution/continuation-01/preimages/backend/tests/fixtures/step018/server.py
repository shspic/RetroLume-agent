"""真实API与正常配置loader；只安装本轮最低传输替身。"""
import json,os
from pathlib import Path
from runtime_fixture import install

def create_app():
    if not install():raise RuntimeError('synthetic_permit_missing')
    from app.main import create_app as product
    app=product()
    config=app.state.activity_config
    proof={'api_pid':os.getpid(),'preview_config_exists':Path(os.environ['RETROLUME_PREVIEW_CONFIG']).is_file(),'preview_key_present':bool(os.environ.get('RETROLUME_TASK117_PREVIEW_REVIEW_KEY')),'normal_loader_accepted':app.state.preview_policy is not None,'authorization':app.state.preview_policy.authorization if app.state.preview_policy else None,'integration_available':app.state.integration_config.available,'data_exit_error':app.state.data_exit_error,'layers':{k:getattr(config,k).available for k in ('create_layer','continue_layer','teaching_layer','interview_model_layer','html_generation_layer')}}
    path=Path(os.environ['RETROLUME_TASK117_API_PROOF']);path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    if not all(proof['layers'].values()) or not proof['normal_loader_accepted'] or proof['data_exit_error'] is not None:raise RuntimeError('normal_deployment_not_ready')
    return app
