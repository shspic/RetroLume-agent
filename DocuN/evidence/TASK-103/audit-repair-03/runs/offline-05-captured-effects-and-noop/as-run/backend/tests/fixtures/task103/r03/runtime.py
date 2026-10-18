"""只观察并阻止禁用的监督入口，不提供资格／模型结果替身。"""
import sys,threading
from .control import Control
def profile(frame,event,arg):
 file=frame.f_code.co_filename.replace('\\','/')
 if event=='call' and frame.f_code.co_name in ('run_one_call','run_one_tool') and '/app/worker/' in file:
  Control().reserve('sup',{'unexpected_worker_call':frame.f_code.co_name})
def install():sys.setprofile(profile);threading.setprofile(profile)
