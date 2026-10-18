"""C02精确API入口，环境只由本轮父runner给，不下载/启动任何预览。"""
import asyncio
import sys
from budget import ROOT,Budget,FactoryHooks
sys.path.insert(0,str(ROOT/'backend'))
from app.main import create_app
from app.runtime import psycopg_compatible_loop_factory
import uvicorn
app=create_app()
if app.state.data_exit is None:raise RuntimeError('C02 API入口未配置')
app.state.data_exit.factory.hooks=FactoryHooks(Budget())
config=uvicorn.Config(app,host='127.0.0.1',port=18114,log_level='error',access_log=False,loop='asyncio')
with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(uvicorn.Server(config).serve())
