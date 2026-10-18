"""只定位Windows离线事件循环构造停点，不调用产品或外部服务。"""
import asyncio
import faulthandler
faulthandler.dump_traceback_later(2,repeat=False)
print('准备构造Selector事件循环',flush=True)
loop=asyncio.SelectorEventLoop()
print('Selector事件循环构造完成',flush=True)
loop.close()
