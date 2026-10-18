"""Owned compatibility host, normal product configuration, reader credentials only."""
import os,sys,json,threading,asyncio
from pathlib import Path
import uvicorn
from app.main import create_app
from app.runtime import psycopg_compatible_loop_factory

app=create_app();data=app.state.data_exit
assert app.state.data_exit_error is None and data is not None
assert data.context().mode=='restored_readonly' and data.source is None and data.factory is None
assert data.maintenance is None and data.maintenance_key is None and data.snapshot_dsn is None
assert app.state.preview_controller is None and app.state.preview_policy is None
for name in ('RETROLUME_TASK117_SYNTHETIC','RETROLUME_TASK117_MAINTENANCE','RETROLUME_TASK117_SNAPSHOT',
             'RETROLUME_MODEL_API_KEY','RETROLUME_EMBEDDING_API_KEY','RETROLUME_PREVIEW_CONFIG'):
    assert name not in os.environ
proof={'pid':os.getpid(),'normal_product_constructor':True,'context':data.context().public(),'caps':data.caps(),
       'source_write_loader_maintenance_credentials':False,'provider_execution_configuration':False,
       'selector':data.hub.state()['selection'],'fence':data.hub.state()['fence']}
Path(os.environ['RETROLUME_READER_PROOF']).write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=18118,timeout_graceful_shutdown=30,log_level='warning'))
def commands():sys.stdin.readline();server.should_exit=True
threading.Thread(target=commands,daemon=True).start()
with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(server.serve())
