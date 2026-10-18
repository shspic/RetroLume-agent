"""仅定位本机事件循环初始化，10秒打印阻塞栈；不调用任何业务/外部服务。"""
import faulthandler
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'backend'))
from app.runtime import psycopg_compatible_loop_factory
faulthandler.dump_traceback_later(5,repeat=False)
print('selector_factory_begin',flush=True)
loop=psycopg_compatible_loop_factory()
print('selector_factory_created',flush=True)
loop.close()
faulthandler.cancel_dump_traceback_later()
print('selector_factory_closed',flush=True)
