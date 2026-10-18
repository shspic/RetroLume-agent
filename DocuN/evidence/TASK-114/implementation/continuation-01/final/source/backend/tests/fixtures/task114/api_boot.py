"""仅本卡 18114 的真实应用入口；环境与工厂 hooks 只由本卡父 runner 给。"""
import asyncio
import os
import sys
from budget import ROOT,Budget,FactoryHooks
sys.path.insert(0,str(ROOT/'backend'))
from app.main import create_app
from app.runtime import psycopg_compatible_loop_factory
import uvicorn

app=create_app()
if app.state.data_exit is None:raise RuntimeError('数据运行入口未就绪')
app.state.data_exit.factory.hooks=FactoryHooks(Budget())
config=uvicorn.Config(app,host='127.0.0.1',port=18114,log_level='error',access_log=False,loop='asyncio')
with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(uvicorn.Server(config).serve())
